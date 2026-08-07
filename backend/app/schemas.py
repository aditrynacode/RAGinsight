from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, ConfigDict


class ChunkResult(BaseModel):
    chunk_id: Optional[int] = None
    document_id: Optional[int] = None
    content: str
    similarity_score: Optional[float] = None
    source: Optional[Any] = None


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    query_id: Optional[int] = None
    answer: str
    chunks: List[ChunkResult]
    confidence: Optional[float] = None
    response_time: float


class FeedbackRequest(BaseModel):
    query_id: int
    rating: str  # "up" | "down"
    note: Optional[str] = None


class FeedbackResponse(BaseModel):
    feedback_id: int
    diagnosis_id: Optional[int] = None


class DiagnosisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    query_id: int
    failure_category: str
    reasoning: str
    proposed_fix: Dict[str, Any]
    diagnosis_confidence: float
    expected_impact: str
    expected_impact_reasoning: Optional[str] = None
    created_at: datetime


class ApplyFixRequest(BaseModel):
    target_document_id: Optional[int] = None
    reference_answer: Optional[str] = None


class ApplyFixResponse(BaseModel):
    experiment_id: int
    pre_score: Optional[float] = None
    post_score: Optional[float] = None
    improved: bool


class ExperimentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    diagnosis_id: int
    applied_fix: Dict[str, Any]
    pre_score: Optional[float] = None
    post_score: Optional[float] = None
    new_query_id: Optional[int] = None
    applied_at: datetime


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    source: str
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    created_at: datetime


class ChunkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chunk_index: Optional[int] = None
    document_id: int
    page: Optional[int] = None
    content: str
