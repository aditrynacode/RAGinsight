from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import JSON
from sqlalchemy.sql import func

from app.database.database import Base


class Document(Base):

    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    # Chunking strategy this document was last ingested with. Updated when a
    # "rechunk_document" fix is applied, so you can see lineage between a
    # document's current chunks and the fix that produced them.
    chunk_size = Column(Integer, default=500)
    chunk_overlap = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Chunk(Base):

    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)

    chunk_index = Column(Integer)
    document_id = Column(Integer, ForeignKey("documents.id"))
    page = Column(Integer)
    content = Column(Text)
    embedding_ref = Column(String)


class QueryLog(Base):

    __tablename__ = "queries"
    id = Column(Integer, primary_key=True)

    question = Column(Text)
    answer = Column(Text)
    # List of Chunk.id values that were retrieved for this query.
    retrieved_chunk_ids = Column(JSON)
    # Model self-reported confidence, 1-5.
    confidence = Column(Float, nullable=True)
    response_time = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Feedback(Base):

    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)

    query_id = Column(Integer, ForeignKey("queries.id"))
    rating = Column(String)  # "up" | "down"
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Diagnosis(Base):

    __tablename__ = "diagnoses"
    id = Column(Integer, primary_key=True)

    query_id = Column(Integer, ForeignKey("queries.id"))
    failure_category = Column(String)
    reasoning = Column(Text)
    # Full proposed_fix object from the diagnostic agent (fix_type,
    # description, target, params).
    proposed_fix = Column(JSON)
    diagnosis_confidence = Column(Float)
    expected_impact = Column(String)
    expected_impact_reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Experiment(Base):

    __tablename__ = "experiments"
    id = Column(Integer, primary_key=True)

    diagnosis_id = Column(Integer, ForeignKey("diagnoses.id"))
    applied_fix = Column(JSON)
    pre_score = Column(Float, nullable=True)
    post_score = Column(Float, nullable=True)
    # The new QueryLog row created when the original question was re-run
    # after the fix was applied.
    new_query_id = Column(Integer, ForeignKey("queries.id"), nullable=True)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())


class EvalScore(Base):

    __tablename__ = "eval_scores"
    id = Column(Integer, primary_key=True)

    query_id = Column(Integer, ForeignKey("queries.id"))
    correctness = Column(Float)
    groundedness = Column(Float)
    completeness = Column(Float)
    overall = Column(Float)
    judge_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
