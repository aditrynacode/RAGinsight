from typing import List, Tuple
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config import CHROMA_DIR
from app.rag.embeddings import get_embedding_model

_vector_store = None


def get_vector_store() -> Chroma:
    global _vector_store
    if _vector_store is None:
        _vector_store = Chroma(
            collection_name="rag_chunks",
            embedding_function=get_embedding_model(),
            persist_directory=str(CHROMA_DIR),
        )
    return _vector_store


def add_chunks(chunks: List[Document], ids: List[str]) -> None:
    store = get_vector_store()
    store.add_documents(documents=chunks, ids=ids)


def delete_by_document(document_id: int) -> None:
    """Remove every vector belonging to a document. Used when re-chunking a
    document as part of applying a CHUNKING_PROBLEM fix, so old chunks don't
    linger alongside the new ones.
    """
    store = get_vector_store()
    store._collection.delete(where={"document_id": document_id})


def similarity_search_with_score(query: str, k: int = 4) -> List[Tuple[Document, float]]:
    store = get_vector_store()
    return store.similarity_search_with_score(query, k=k)
