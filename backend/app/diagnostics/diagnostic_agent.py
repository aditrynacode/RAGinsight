from typing import List, Dict, Any, Optional

from app.llm.llm_client import chat_completion
from app.utils.llm_json import parse_json_response
from app.diagnostics.prompts import DIAGNOSTIC_SYSTEM_PROMPT


def diagnose(
    question: str,
    chunks: List[Dict[str, Any]],
    answer: str,
    feedback_note: Optional[str] = None,
    reference_answer: Optional[str] = None,
) -> Dict[str, Any]:
    """Classify a failed/flagged answer and propose a fix. `chunks` is the
    list of retrieved chunk dicts (must include 'content'; 'chunk_id' and
    'source' are used for readability but optional).
    """
    chunk_text = "\n\n".join(
        f"[Chunk {c.get('chunk_id', i)}, doc: {c.get('source', 'unknown')}]: {c['content']}"
        for i, c in enumerate(chunks)
    ) or "(no chunks were retrieved)"

    user_content = f"QUESTION: {question}\n\nRETRIEVED CHUNKS:\n{chunk_text}\n\nGENERATED ANSWER: {answer}"
    if feedback_note:
        user_content += f"\n\nUSER FEEDBACK: {feedback_note}"
    if reference_answer:
        user_content += f"\n\nREFERENCE ANSWER: {reference_answer}"

    raw = chat_completion(
        messages=[
            {"role": "system", "content": DIAGNOSTIC_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        json_mode=True,
        temperature=0,
    )
    return parse_json_response(raw)
