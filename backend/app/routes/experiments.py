from typing import List
from fastapi import APIRouter

from app.database.database import SessionLocal
from app.database.models import Experiment
from app.schemas import ExperimentOut

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("", response_model=List[ExperimentOut])
def list_experiments():
    db = SessionLocal()
    try:
        return db.query(Experiment).order_by(Experiment.applied_at.desc()).all()
    finally:
        db.close()
