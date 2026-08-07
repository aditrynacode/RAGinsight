from typing import Optional

from app.database.database import SessionLocal
from app.database.models import Diagnosis, Experiment, QueryLog
from app.diagnostics.diagnostic_agent import diagnose as run_diagnosis
from app.diagnostics.fix_applier import apply_fix
from app.services.feedback_service import get_query_with_chunks
from app.services.query_service import answer_question
from app.rag.evaluator import score_answer


def diagnose_query(
    query_id: int,
    feedback_note: Optional[str] = None,
    reference_answer: Optional[str] = None,
) -> Diagnosis:
    """Run the diagnostic agent on a flagged query and persist the result."""
    query, chunks = get_query_with_chunks(query_id)
    if not query:
        raise ValueError(f"Query {query_id} not found")

    result = run_diagnosis(
        question=query.question,
        chunks=chunks,
        answer=query.answer,
        feedback_note=feedback_note,
        reference_answer=reference_answer,
    )

    db = SessionLocal()
    try:
        diagnosis = Diagnosis(
            query_id=query_id,
            failure_category=result["failure_category"],
            reasoning=result["reasoning"],
            proposed_fix=result["proposed_fix"],
            diagnosis_confidence=result["diagnosis_confidence"],
            expected_impact=result["expected_impact"],
            expected_impact_reasoning=result.get("expected_impact_reasoning", ""),
        )
        db.add(diagnosis)
        db.commit()
        db.refresh(diagnosis)
        return diagnosis
    finally:
        db.close()


def apply_and_retest(
    diagnosis_id: int,
    target_document_id: Optional[int] = None,
    reference_answer: Optional[str] = None,
) -> Experiment:
    """Score the original answer (pre_score), apply the diagnosis's proposed
    fix, re-run the original question, score the new answer (post_score), and
    log the whole thing as an Experiment row for the dashboard's
    before/after chart.
    """
    db = SessionLocal()
    try:
        diagnosis = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
        if not diagnosis:
            raise ValueError(f"Diagnosis {diagnosis_id} not found")
        original_query = db.query(QueryLog).filter(QueryLog.id == diagnosis.query_id).first()
        if not original_query:
            raise ValueError(f"Query {diagnosis.query_id} for diagnosis {diagnosis_id} not found")
        original_question = original_query.question
        original_answer = original_query.answer
    finally:
        db.close()

    _, original_chunks = get_query_with_chunks(diagnosis.query_id)
    pre_result = score_answer(original_question, original_answer, original_chunks, reference_answer)

    apply_result = apply_fix(diagnosis.proposed_fix, target_document_id=target_document_id)

    new_answer = answer_question(original_question, log=True)

    post_result = score_answer(
        original_question, new_answer["answer"], new_answer["chunks"], reference_answer
    )

    db = SessionLocal()
    try:
        experiment = Experiment(
            diagnosis_id=diagnosis_id,
            applied_fix={**diagnosis.proposed_fix, "apply_result": apply_result},
            pre_score=pre_result["overall"],
            post_score=post_result["overall"],
            new_query_id=new_answer.get("query_id"),
        )
        db.add(experiment)
        db.commit()
        db.refresh(experiment)
        return experiment
    finally:
        db.close()
