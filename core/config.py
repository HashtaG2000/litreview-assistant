import os

# ── Vector store ───────────────────────────────────────────────────────────────
CHROMA_PATH = os.getenv("CHROMA_PERSIST_PATH", "/data/chroma_store")

# ── Embedding model ────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ── Reranker model ─────────────────────────────────────────────────────────────
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# ── LLM ───────────────────────────────────────────────────────────────────────
LLM_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.3
LLM_MAX_RETRIES = 3

# ── Chunking ───────────────────────────────────────────────────────────────────
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
