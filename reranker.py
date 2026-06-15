_reranker = None
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def get_reranker():
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        _reranker = CrossEncoder(RERANKER_MODEL)
    return _reranker


def rerank(query: str, documents: list, top_k: int = 6) -> list:
    if not documents:
        return documents
    try:
        reranker = get_reranker()
        pairs = [(query, doc.page_content) for doc in documents]
        scores = reranker.predict(pairs)
        scored = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]
    except Exception:
        return documents[:top_k]
