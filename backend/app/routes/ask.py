from fastapi import APIRouter, BackgroundTasks

from app.schemas import AskRequest, AskResponse
from app.services.query_service import answer_question
from app.services.eval_service import evaluate_and_log

router = APIRouter(prefix="/ask", tags=["ask"])


@router.post("", response_model=AskResponse)
def ask(request: AskRequest, background_tasks: BackgroundTasks):
    result = answer_question(request.question)

    # Score every query from day one (per spec), but off the request path so
    # the user doesn't wait on an extra LLM call to get their answer.
    if result.get("query_id") is not None:
        background_tasks.add_task(
            evaluate_and_log,
            result["query_id"],
            result["question"],
            result["answer"],
            result["chunks"],
        )

    return AskResponse(
        query_id=result.get("query_id"),
        answer=result["answer"],
        chunks=result["chunks"],
        confidence=result["confidence"],
        response_time=result["response_time"],
    )
