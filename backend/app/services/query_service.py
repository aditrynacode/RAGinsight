import time
from typing import Optional, Dict, Any

from app.rag.retriever import retrieve
from app.llm.llm_client import chat_completion
from app.services.dynamic_config_service import get_config
from app.database.models import QueryLog
from app.database.database import SessionLocal

BASE_SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions using ONLY the provided context. "
    "Cite the chunk id(s) you used in square brackets, e.g. [Chunk 3]. "
    "If the context does not contain the answer, say so clearly instead of guessing. "
    "At the very end, on its own line, output 'CONFIDENCE: x' where x is your confidence "
    "1-5 that the answer is correct and fully grounded in the context."
)


def build_system_prompt() -> str:
    """System prompt is assembled at request time from BASE_SYSTEM_PROMPT plus
    any GENERATION_ERROR / AMBIGUOUS_QUERY fixes the diagnostic agent has
    applied, so those fixes take effect immediately on the next question.
    """
    config = get_config()
    prompt = BASE_SYSTEM_PROMPT

    for addition in config.get("system_prompt_additions", []):
        prompt += f"\n{addition}"

    clarification_additions = config.get("clarification_prompt_additions", [])
    if clarification_additions:
        prompt += (
            "\nIf the question is ambiguous or could reasonably refer to multiple things, "
            "say so explicitly and ask a brief clarifying question instead of guessing. "
            + " ".join(clarification_additions)
        )

    return prompt


def answer_question(question: str, top_k: Optional[int] = None, log: bool = True) -> Dict[str, Any]:
    start = time.time()
    chunks = retrieve(question, top_k=top_k)

    context = "\n\n".join(f"[Chunk {c['chunk_id']}]: {c['content']}" for c in chunks) or "(no chunks retrieved)"
    user_content = f"CONTEXT:\n{context}\n\nQUESTION: {question}"

    raw = chat_completion(
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
    )

    answer = raw
    confidence = None
    if "CONFIDENCE:" in raw:
        body, _, tail = raw.rpartition("CONFIDENCE:")
        answer = body.strip()
        try:
            confidence = float(tail.strip().split()[0])
        except (ValueError, IndexError):
            confidence = None

    response_time = time.time() - start

    result: Dict[str, Any] = {
        "question": question,
        "answer": answer,
        "chunks": chunks,
        "confidence": confidence,
        "response_time": response_time,
    }

    if log:
        db = SessionLocal()
        try:
            entry = QueryLog(
                question=question,
                answer=answer,
                retrieved_chunk_ids=[c["chunk_id"] for c in chunks],
                confidence=confidence,
                response_time=response_time,
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)
            result["query_id"] = entry.id
        finally:
            db.close()

    return result
