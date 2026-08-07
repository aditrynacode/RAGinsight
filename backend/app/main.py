from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import create_tables
from app.routes import ask, feedback, diagnostics, experiments, dashboard, documents

app = FastAPI(title="RAGInsight")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_tables()


app.include_router(ask.router)
app.include_router(feedback.router)
app.include_router(diagnostics.router)
app.include_router(experiments.router)
app.include_router(dashboard.router)
app.include_router(documents.router)


@app.get("/")
def root():
    return {"message": "RAGInsight backend running"}
