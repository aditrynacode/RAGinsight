from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


def split_documents(
    docs: List[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Document]:
    """Split loaded pages into chunks. Kept as a standalone function (rather
    than inline in ingest.py) so the diagnostic agent's "rechunk_document" fix
    can call it with different parameters on a single document without
    touching the rest of the ingestion pipeline.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(docs)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
    return chunks
