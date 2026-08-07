from typing import Optional, List, Dict, Any, Tuple

from app.database.database import SessionLocal
from app.database.models import Feedback, QueryLog, Chunk


def record_feedback(query_id: int, rating: str, note: Optional[str] = None) -> Feedback:
    db = SessionLocal()
    try:
        fb = Feedback(query_id=query_id, rating=rating, note=note)
        db.add(fb)
        db.commit()
        db.refresh(fb)
        return fb
    finally:
        db.close()


def get_query_with_chunks(query_id: int) -> Tuple[Optional[QueryLog], List[Dict[str, Any]]]:
    """Look up a logged query and re-hydrate its retrieved chunks from SQL
    (by the chunk ids stored on the QueryLog row), for feeding to the
    diagnostic agent or the eval judge.
    """
    db = SessionLocal()
    try:
        query = db.query(QueryLog).filter(QueryLog.id == query_id).first()
        if not query:
            return None, []

        chunk_ids = query.retrieved_chunk_ids or []
        chunks = db.query(Chunk).filter(Chunk.id.in_(chunk_ids)).all()
        by_id = {c.id: c for c in chunks}

        # Preserve original retrieval order.
        chunk_dicts = [
            {
                "chunk_id": cid,
                "content": by_id[cid].content,
                "source": by_id[cid].document_id,
            }
            for cid in chunk_ids if cid in by_id
        ]
        return query, chunk_dicts
    finally:
        db.close()
