from typing import List
from fastapi import APIRouter, HTTPException

from app.database.database import SessionLocal
from app.database.models import Document, Chunk
from app.schemas import DocumentOut, ChunkOut

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=List[DocumentOut])
def list_documents():
    db = SessionLocal()
    try:
        return db.query(Document).all()
    finally:
        db.close()


@router.get("/{document_id}/chunks", response_model=List[ChunkOut])
def get_chunks(document_id: int):
    """Powers the 'chunk inspector' — see which chunks exist for a document,
    e.g. to check the effect of a rechunk_document fix.
    """
    db = SessionLocal()
    try:
        chunks = (
            db.query(Chunk)
            .filter(Chunk.document_id == document_id)
            .order_by(Chunk.chunk_index)
            .all()
        )
        if not chunks:
            raise HTTPException(404, "No chunks found for this document")
        return chunks
    finally:
        db.close()
