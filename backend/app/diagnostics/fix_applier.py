from typing import Dict, Any, Optional

from app.services import dynamic_config_service as cfg
from app.rag.ingest import rechunk_document


def apply_fix(proposed_fix: Dict[str, Any], target_document_id: Optional[int] = None) -> Dict[str, Any]:
    """Apply a diagnostic agent's proposed_fix. Reads structured values from
    proposed_fix['params'] rather than parsing the free-text description, so
    application is deterministic. Returns a small result dict that gets
    stored alongside the experiment for the dashboard.
    """
    fix_type = proposed_fix.get("fix_type")
    params = proposed_fix.get("params") or {}

    if fix_type == "add_synonym_mapping":
        term = params.get("term")
        aliases = params.get("aliases") or []
        if not term or not aliases:
            return {"applied": False, "detail": "Missing 'term'/'aliases' in proposed_fix.params"}
        cfg.add_synonym_mapping(term, aliases)
        return {"applied": True, "detail": f"Added synonyms {aliases} for query term '{term}'"}

    if fix_type == "adjust_top_k":
        new_k = params.get("new_top_k")
        if not new_k:
            return {"applied": False, "detail": "Missing 'new_top_k' in proposed_fix.params"}
        cfg.set_top_k(int(new_k))
        return {"applied": True, "detail": f"Set default retrieval top_k to {new_k}"}

    if fix_type == "rechunk_document":
        if target_document_id is None:
            return {"applied": False, "detail": "No target_document_id supplied to apply this fix"}
        chunk_size = int(params.get("chunk_size", 800))
        chunk_overlap = int(params.get("chunk_overlap", 200))
        n_chunks = rechunk_document(target_document_id, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return {
            "applied": True,
            "detail": f"Re-chunked document {target_document_id} into {n_chunks} chunks "
                      f"(chunk_size={chunk_size}, chunk_overlap={chunk_overlap})",
        }

    if fix_type == "add_clarification_prompt":
        text = params.get("prompt_addition") or proposed_fix.get("description", "")
        cfg.add_clarification_prompt_addition(text)
        return {"applied": True, "detail": "Added clarification-prompt guidance to the system prompt"}

    if fix_type == "adjust_system_prompt":
        text = params.get("prompt_addition") or proposed_fix.get("description", "")
        cfg.add_system_prompt_addition(text)
        return {"applied": True, "detail": "Added system-prompt tweak"}

    if fix_type == "no_fix_needed":
        return {"applied": False, "detail": "Diagnostic agent judged no fix was needed (e.g. NO_INFORMATION case)"}

    return {"applied": False, "detail": f"Unrecognized fix_type: {fix_type!r}"}
