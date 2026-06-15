from rank_bm25 import BM25Okapi


class HybridRetriever:
    """
    Combines Chroma dense search with BM25 sparse search.
    Results are fused using Reciprocal Rank Fusion (RRF).
    """

    def __init__(self, db):
        self._db = db

    # ── Internal helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _tokenize(text: str) -> list:
        return text.lower().split()

    @staticmethod
    def _rrf(rank: int, k: int = 60) -> float:
        return 1.0 / (k + rank + 1)

    def _build_filter(self, session_id: str, paper_title: str = None) -> dict | None:
        if paper_title and session_id:
            return {"$and": [
                {"paper_title": {"$eq": paper_title}},
                {"session_id": {"$eq": session_id}},
            ]}
        if session_id:
            return {"session_id": {"$eq": session_id}}
        if paper_title:
            return {"paper_title": {"$eq": paper_title}}
        return None

    # ── Public API ─────────────────────────────────────────────────────────────

    def search(self, query: str, session_id: str, paper_title: str = None, k: int = 6) -> list:
        chroma_filter = self._build_filter(session_id, paper_title)
        fetch_k = min(k * 6, 120)

        try:
            dense_results = (
                self._db.similarity_search(query, k=fetch_k, filter=chroma_filter)
                if chroma_filter
                else self._db.similarity_search(query, k=fetch_k)
            )
        except Exception:
            try:
                dense_results = self._db.similarity_search(query, k=fetch_k)
            except Exception:
                return []

        if not dense_results:
            return []
        if len(dense_results) <= k:
            return dense_results

        # BM25 over the dense candidate pool
        corpus = [doc.page_content for doc in dense_results]
        bm25 = BM25Okapi([self._tokenize(t) for t in corpus])
        bm25_scores = bm25.get_scores(self._tokenize(query))

        bm25_rank = {
            idx: rank
            for rank, idx in enumerate(
                sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)
            )
        }

        # Fuse: dense rank is its position in dense_results
        fused = {
            i: self._rrf(i) + self._rrf(bm25_rank.get(i, len(dense_results)))
            for i in range(len(dense_results))
        }

        top_indices = sorted(fused, key=fused.__getitem__, reverse=True)[:k]
        return [dense_results[i] for i in top_indices]
