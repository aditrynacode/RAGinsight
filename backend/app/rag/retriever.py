from typing import List, Dict, Any, Optional

from app.rag.vector_store import similarity_search_with_score
from app.services.dynamic_config_service import get_config


def expand_query(question: str) -> str:
    """Append any synonym aliases that a previously-applied RETRIEVAL_MISS fix
    registered for a term found in this question. This is the mechanism the
    diagnostic agent's "add_synonym_mapping" fix actually changes at runtime.
    """
    config = get_config()
    mappings = config.get("synonym_mappings", {})
    q_lower = question.lower()

    extra_terms: List[str] = []
    for term, aliases in mappings.items():
        if term.lower() in q_lower:
            extra_terms.extend(aliases)

    if extra_terms:
        return f"{question} {' '.join(extra_terms)}"
    return question


def retrieve(question: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
    config = get_config()
    k = top_k or config.get("top_k_overrides", {}).get("default", 4)

    expanded_question = expand_query(question)
    results = similarity_search_with_score(expanded_question, k=k)

    retrieved = []
    for doc, score in results:
        retrieved.append({
            "chunk_id": doc.metadata.get("db_chunk_id"),
            "document_id": doc.metadata.get("document_id"),
            "content": doc.page_content,
            "similarity_score": float(score),
            "source": doc.metadata.get("source"),
        })
    return retrieved
