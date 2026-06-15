from langchain_huggingface import HuggingFaceEmbeddings
from core.config import EMBEDDING_MODEL

# Single module-level instance shared across ingestion, retrieval, and analysis.
_embeddings = None


def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings
