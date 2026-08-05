import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DOCUMENT_FOLDER = r"C:\Users\adity\RAGInsight\backend\documents"

docs = []

for file in os.listdir(DOCUMENT_FOLDER):
    if file.endswith(".pdf"):
        loader = PyPDFLoader(os.path.join(DOCUMENT_FOLDER, file))
        docs.extend(loader.load())

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
chunks = splitter.split_documents(docs)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory=r"C:\Users\adity\RAGInsight\backend\chroma_db"
)

print(f"Stored {len(chunks)} chunks in ChromaDB")

results = db.similarity_search(
    "What are the limitations of LLMs?",
    k=3
)

for r in results:
    print("-" * 40)
    print(r.page_content)