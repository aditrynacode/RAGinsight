from typing import List
from langchain_core.documents import Document as LCDocument

from app.config import DOCUMENTS_DIR, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP
from app.database.database import create_tables, SessionLocal
from app.database.models import Document, Chunk
from app.rag.document_loader import DocumentLoader
from app.rag.chunker import split_documents
from app.rag.vector_store import add_chunks, delete_by_document


def ingest_documents() -> None:
    """Ingest every PDF in DOCUMENTS_DIR that hasn't been ingested yet:
    load -> chunk -> embed/store in Chroma -> mirror rows into SQL.
    Safe to re-run; already-ingested documents (matched by filename) are skipped.
    """
    create_tables()
    db = SessionLocal()
    loader = DocumentLoader(DOCUMENTS_DIR)
    pdf_files = loader.list_documents()
    print(f"\nFound {len(pdf_files)} PDF(s) in {DOCUMENTS_DIR}\n")

    try:
        for pdf_path in pdf_files:
            existing = db.query(Document).filter(Document.source == pdf_path.name).first()
            if existing:
                print(f"Skipping already-ingested: {pdf_path.name}")
                continue

            print(f"Loading: {pdf_path.name}")
            pages = loader.load_single_document(pdf_path)

            document = Document(
                title=pdf_path.stem,
                source=pdf_path.name,
                chunk_size=DEFAULT_CHUNK_SIZE,
                chunk_overlap=DEFAULT_CHUNK_OVERLAP,
            )
            db.add(document)
            db.commit()
            db.refresh(document)

            n_chunks = _chunk_and_store(db, document, pages, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP)
            print(f"Ingested {pdf_path.name} -> document_id={document.id}, {n_chunks} chunk(s)\n")
    finally:
        db.close()


def _chunk_and_store(
    db,
    document: Document,
    pages: List[LCDocument],
    chunk_size: int,
    chunk_overlap: int,
) -> int:
    """Split pages, write one Chunk row per chunk (so SQL always mirrors the
    vector store), then embed and store the same chunks in Chroma using the
    SQL row id as part of the vector id. This id linkage is what lets the
    retriever map a Chroma hit back to a chunk row for the dashboard / chunk
    inspector.
    """
    split = split_documents(pages, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    langchain_docs = []
    ids = []
    for i, chunk in enumerate(split):
        db_chunk = Chunk(
            chunk_index=i,
            document_id=document.id,
            page=chunk.metadata.get("page"),
            content=chunk.page_content,
        )
        db.add(db_chunk)
        db.commit()
        db.refresh(db_chunk)

        vector_id = f"doc{document.id}_chunk{db_chunk.id}"
        db_chunk.embedding_ref = vector_id
        db.commit()

        chunk.metadata["db_chunk_id"] = db_chunk.id
        chunk.metadata["document_id"] = document.id
        chunk.metadata["source"] = document.source

        langchain_docs.append(chunk)
        ids.append(vector_id)

    if langchain_docs:
        add_chunks(langchain_docs, ids)

    return len(langchain_docs)


def rechunk_document(document_id: int, chunk_size: int, chunk_overlap: int) -> int:
    """Re-load a single document's PDF, delete its existing chunks (SQL +
    Chroma), and re-chunk/re-embed with new chunk_size/chunk_overlap. This is
    what the diagnostic agent's "rechunk_document" fix calls when it decides
    a CHUNKING_PROBLEM needs a different split strategy.
    """
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        pdf_path = DOCUMENTS_DIR / document.source
        loader = DocumentLoader(DOCUMENTS_DIR)
        pages = loader.load_single_document(pdf_path)

        delete_by_document(document_id)
        db.query(Chunk).filter(Chunk.document_id == document_id).delete()
        db.commit()

        document.chunk_size = chunk_size
        document.chunk_overlap = chunk_overlap
        db.commit()

        n_chunks = _chunk_and_store(db, document, pages, chunk_size, chunk_overlap)
        return n_chunks
    finally:
        db.close()


if __name__ == "__main__":
    ingest_documents()
