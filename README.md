# RAGInsight

**A RAG system that diagnoses and repairs its own failures, and shows you the improvement happening live.**

Most RAG demos show a chatbot answering questions. RAGInsight shows what happens *after* it gets one wrong: a diagnostic agent inspects the failure, classifies the root cause, proposes a concrete fix, applies it, and re-scores the answer. All of it logged, all of it visible on a dashboard that traces the system's eval score improving over time.

---

## The idea

```
Ask a question
      │
      ▼
Retrieve chunks → generate answer → log it
      │
      ▼
   Thumbs down?
      │
      ▼
Diagnostic agent inspects the question, the chunks,
and the answer to decide what actually went wrong
      │
      ▼
Proposes a specific fix (not "improve retrieval," but
"add these two synonym terms," "re-chunk this document
with more overlap," or "raise top_k to 6")
      │
      ▼
Fix gets applied → same question re-run → before/after
score compared and logged
```

That last loop is the whole point. This isn't just a RAG app, it's the thing that watches a RAG app and repairs it.

## Features

**Core RAG pipeline**
- PDF ingestion, chunking, local embeddings (`sentence-transformers`), and a Chroma vector store
- Every chunk mirrored into SQL, so chunk lineage (which document, which chunking strategy) is always inspectable
- Retrieval-augmented answers with inline chunk citations and a self-reported confidence score

**Diagnostic agent**
- Classifies a flagged answer into one of five failure modes: `RETRIEVAL_MISS`, `CHUNKING_PROBLEM`, `AMBIGUOUS_QUERY`, `GENERATION_ERROR`, `NO_INFORMATION`
- Returns a structured, applicable fix instead of a vague suggestion, with a confidence score and an estimate of how broadly the fix would generalize
- Sanity-checkable against five manufactured failure cases (one per category) without waiting on organic bad answers

**Fix application**
- Fixes take effect immediately, no restart required: synonym expansion and `top_k` adjustments are read live from a config store on every request
- A `rechunk_document` fix actually re-ingests the affected document with new chunk size/overlap, replacing its vectors in both SQL and Chroma
- Every applied fix is re-tested against its original failing question and scored before vs. after

**LLM-as-judge evaluation**
- Every answer is scored on correctness, groundedness, and completeness, not just vibes
- Score history is what powers the "watch it improve" timeline

**Ops dashboard**
- Eval score trend over time
- Failure category breakdown
- Full experiment log: which fix, what it changed, before/after score, whether it actually helped
- Chunk inspector to browse a document's current chunks and verify a re-chunk fix took effect

## Architecture

| Layer | Tech |
|---|---|
| Backend API | FastAPI |
| Relational data | SQLite + SQLAlchemy |
| Vector store | Chroma |
| Embeddings | `sentence-transformers` (local, free) |
| LLM (chat / diagnosis / judge) | Gemini API |
| Frontend | React + Vite |
| Charts | Recharts |

```
backend/
  app/
    database/         SQLAlchemy models and session (database.py, models.py)
    rag/              ingestion, chunking, embeddings, vector store,
                      retriever, LLM-judge evaluator, manufactured-failure
                      test loader
    llm/              LLM client
    diagnostics/      diagnostic agent prompt, agent runner, fix applier
    services/         orchestration layer: query, feedback, eval,
                      experiment, and dynamic-config services
    routes/           FastAPI endpoints (ask, feedback, diagnostics,
                      experiments, dashboard, documents)
    utils/            shared helpers (LLM JSON parsing)
    config.py
    main.py
    schemas.py
  documents/          PDFs to ingest
  chroma_db/          vector store (generated, not committed)
  rag.db              SQLite database (generated, not committed)

frontend/
  src/
    pages/             Chat view, Ops dashboard
    components/        charts, diagnosis panel, chunk inspector, nav, etc.
    api/               fetch wrapper around every backend endpoint
    styles/            design tokens and global styles
    categoryMeta.js    shared failure-category labels/colors
    App.jsx, main.jsx
```

## Getting started

### Backend
```bash
cd backend
python -m venv venv && venv\Scripts\Activate.ps1   # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

# .env
GEMINI_API_KEY=your-key-from-aistudio.google.com
CHAT_MODEL=gemini-flash-latest
JUDGE_MODEL=gemini-flash-latest

# drop 1-2 PDFs in backend/documents/, then:
python -m app.rag.ingest
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## API reference

| Endpoint | Purpose |
|---|---|
| `POST /ask` | Ask a question, get an answer plus retrieved chunks |
| `POST /feedback` | Rate an answer; a thumbs-down triggers diagnosis |
| `GET /diagnoses` | List all diagnoses |
| `POST /diagnoses/{id}/apply-fix` | Apply a proposed fix and re-test |
| `GET /experiments` | Before/after log of every applied fix |
| `GET /documents` and `GET /documents/{id}/chunks` | Document list and chunk inspector |
| `GET /dashboard/summary`, `/timeline`, `/failures` | Dashboard data |

## Try the loop yourself

1. Ask a question the system answers well
2. Ask one it gets wrong, thumbs it down, and add a note on what's missing
3. Watch the diagnostic agent categorize the failure and propose a fix
4. Click **Apply fix and re-test**, then watch the score move
5. Check the dashboard: the timeline, failure breakdown, and experiment log all update

## License

MIT. 