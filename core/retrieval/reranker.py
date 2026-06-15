from core.config import RERANKER_MODEL

_reranker = None


def get_reranker():
    """Lazy-load the cross-encoder model (cached at module level)."""
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        _reranker = CrossEncoder(RERANKER_MODEL)
    return _reranker


def rerank(query: str, documents: list, top_k: int = 6) -> list:
    """Score (query, chunk) pairs with the cross-encoder and return top_k."""
    if not documents:
        return documents
    try:
        reranker = get_reranker()
        pairs = [(query, doc.page_content) for doc in documents]
        scores = reranker.predict(pairs)
        ranked = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
        return [doc for _, doc in ranked[:top_k]]
    except Exception:
        return documents[:top_k]
