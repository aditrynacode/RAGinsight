from typing import List
from fastapi import APIRouter, HTTPException

from app.database.database import SessionLocal
from app.database.models import Diagnosis
from app.schemas import DiagnosisOut, ApplyFixRequest, ApplyFixResponse
from app.services.experiment_service import apply_and_retest

router = APIRouter(prefix="/diagnoses", tags=["diagnostics"])


@router.get("", response_model=List[DiagnosisOut])
def list_diagnoses():
    db = SessionLocal()
    try:
        return db.query(Diagnosis).order_by(Diagnosis.created_at.desc()).all()
    finally:
        db.close()


@router.get("/{diagnosis_id}", response_model=DiagnosisOut)
def get_diagnosis(diagnosis_id: int):
    db = SessionLocal()
    try:
        diagnosis = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
        if not diagnosis:
            raise HTTPException(404, "Diagnosis not found")
        return diagnosis
    finally:
        db.close()


@router.post("/{diagnosis_id}/apply-fix", response_model=ApplyFixResponse)
def apply_fix_endpoint(diagnosis_id: int, request: ApplyFixRequest):
    try:
        experiment = apply_and_retest(
            diagnosis_id,
            target_document_id=request.target_document_id,
            reference_answer=request.reference_answer,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))

    pre = experiment.pre_score or 0
    post = experiment.post_score or 0
    return ApplyFixResponse(
        experiment_id=experiment.id,
        pre_score=experiment.pre_score,
        post_score=experiment.post_score,
        improved=post > pre,
    )
