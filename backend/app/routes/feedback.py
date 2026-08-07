from fastapi import APIRouter

from app.schemas import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import record_feedback
from app.services.experiment_service import diagnose_query

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackRequest):
    fb = record_feedback(request.query_id, request.rating, request.note)

    diagnosis_id = None
    if request.rating == "down":
        # Run the diagnostic agent synchronously so the UI can show the
        # diagnosis right away, matching the demo narrative in the spec.
        diagnosis = diagnose_query(request.query_id, feedback_note=request.note)
        diagnosis_id = diagnosis.id

    return FeedbackResponse(feedback_id=fb.id, diagnosis_id=diagnosis_id)
