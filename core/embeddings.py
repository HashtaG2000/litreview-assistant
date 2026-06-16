from core.config import EMBEDDING_MODEL

# Lazy singleton — torch and sentence-transformers are NOT imported at module
# load time.  They are only pulled in on the first actual call to get_embeddings(),
# which happens when a user uploads a paper, not on the welcome screen.
_embeddings = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        from langchain_huggingface import HuggingFaceEmbeddings
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings
