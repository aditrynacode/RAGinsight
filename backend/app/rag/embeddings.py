from langchain_huggingface import HuggingFaceEmbeddings

from app.config import EMBEDDING_MODEL_NAME

_embedding_model = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    """Lazily load the embedding model once and reuse it. Loading a
    sentence-transformers model is slow enough that you don't want to do it
    on every request.
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return _embedding_model
