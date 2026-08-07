from pathlib import Path
from dotenv import load_dotenv
import os

# This file lives at backend/app/config.py, so two levels up is backend/,
# where .env, documents/, and chroma_db/ actually live in this repo.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DOCUMENTS_DIR = BASE_DIR / "documents"

CHROMA_DIR = BASE_DIR / "chroma_db"

DATABASE_PATH = BASE_DIR / "rag.db"

# JSON file that stores fixes applied by the diagnostic agent (synonym
# mappings, top_k overrides, system-prompt additions, etc). Read at request
# time by the retriever / query service so applied fixes take effect
# immediately without a restart.
DYNAMIC_CONFIG_PATH = BASE_DIR / "dynamic_config.json"

# Get a free key at https://aistudio.google.com -> "Get API key"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Model used to answer questions and to run the diagnostic agent.
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-flash-latest")
# Model used as the LLM-judge for correctness/groundedness/completeness scoring.
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gemini-flash-latest")

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_TOP_K = 4
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 100