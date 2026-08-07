from typing import List, Dict, Any, Optional

from app.database.database import SessionLocal
from app.database.models import EvalScore
from app.rag.evaluator import score_answer


def evaluate_and_log(
    query_id: int,
    question: str,
    answer: str,
    chunks: List[Dict[str, Any]],
    reference_answer: Optional[str] = None,
) -> EvalScore:
    result = score_answer(question, answer, chunks, reference_answer)

    db = SessionLocal()
    try:
        entry = EvalScore(
            query_id=query_id,
            correctness=result["correctness"],
            groundedness=result["groundedness"],
            completeness=result["completeness"],
            overall=result["overall"],
            judge_notes=result.get("notes", ""),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    finally:
        db.close()
