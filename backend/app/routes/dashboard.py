from fastapi import APIRouter
from sqlalchemy import func

from app.database.database import SessionLocal
from app.database.models import EvalScore, Diagnosis, Experiment, QueryLog

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/timeline")
def eval_timeline():
    """Average eval score over time — the upward-trending chart from the spec."""
    db = SessionLocal()
    try:
        rows = (
            db.query(EvalScore.id, EvalScore.overall, EvalScore.created_at)
            .order_by(EvalScore.created_at)
            .all()
        )
        return [{"id": r.id, "score": r.overall, "timestamp": r.created_at} for r in rows]
    finally:
        db.close()


@router.get("/failures")
def failure_breakdown():
    """Category counts for the failures-diagnosed pie chart."""
    db = SessionLocal()
    try:
        rows = (
            db.query(Diagnosis.failure_category, func.count(Diagnosis.id))
            .group_by(Diagnosis.failure_category)
            .all()
        )
        return [{"category": category, "count": count} for category, count in rows]
    finally:
        db.close()


@router.get("/summary")
def summary():
    db = SessionLocal()
    try:
        total_queries = db.query(func.count(QueryLog.id)).scalar() or 0
        total_diagnoses = db.query(func.count(Diagnosis.id)).scalar() or 0
        total_experiments = db.query(func.count(Experiment.id)).scalar() or 0
        avg_score = db.query(func.avg(EvalScore.overall)).scalar()
        improved = (
            db.query(func.count(Experiment.id))
            .filter(Experiment.post_score > Experiment.pre_score)
            .scalar()
            or 0
        )
        return {
            "total_queries": total_queries,
            "total_diagnoses": total_diagnoses,
            "total_experiments": total_experiments,
            "average_eval_score": round(avg_score, 2) if avg_score is not None else None,
            "experiments_that_improved": improved,
        }
    finally:
        db.close()
