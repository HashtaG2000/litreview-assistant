from langchain_chroma import Chroma
from core.config import CHROMA_PATH
from core.embeddings import get_embeddings
from core.retrieval.hybrid import HybridRetriever
from core.retrieval.reranker import rerank


def get_db() -> Chroma:
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embeddings())


def search_similar(query: str, k: int = 3, session_id: str = None) -> list:
    """
    Unfiltered dense similarity search across the vector store.
    When session_id is provided, results are scoped to that session.
    Used on the Understand screen (no reranking — speed matters more there).
    """
    db = get_db()
    if session_id:
        try:
            results = db.similarity_search(
                query, k=k, filter={"session_id": {"$eq": session_id}}
            )
            if results:
                return results
        except Exception:
            pass
    return db.similarity_search(query, k=k)


def search_similar_filtered(
    query: str,
    paper_title: str,
    k: int = 4,
    session_id: str = None,
) -> list:
    """
    Hybrid (BM25 + dense) search scoped to a single paper, followed by
    cross-encoder reranking.  Falls back to plain dense search on error.

    Used on the Validate screen (relevance check) and Review screen (context
    retrieval per paper).
    """
    db = get_db()
    try:
        candidates = HybridRetriever(db).search(
            query,
            session_id=session_id or "default",
            paper_title=paper_title,
            k=max(k * 2, 12),
        )
        if candidates:
            return rerank(query, candidates, top_k=k)
    except Exception:
        pass

    # Fallback: plain dense search
    try:
        results = db.similarity_search(
            query, k=k, filter={"paper_title": {"$eq": paper_title}}
        )
        if results:
            return results
    except Exception:
        pass

    return db.similarity_search(query, k=k)
