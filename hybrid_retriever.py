from rank_bm25 import BM25Okapi


class HybridRetriever:
    """Combines Chroma dense search with BM25 sparse search via Reciprocal Rank Fusion."""

    def __init__(self, db):
        self._db = db

    @staticmethod
    def _tokenize(text: str) -> list:
        return text.lower().split()

    @staticmethod
    def _rrf(rank: int, k: int = 60) -> float:
        return 1.0 / (k + rank + 1)

    def search(self, query: str, session_id: str, paper_title: str = None, k: int = 6) -> list:
        if paper_title and session_id:
            chroma_filter = {"$and": [
                {"paper_title": {"$eq": paper_title}},
                {"session_id": {"$eq": session_id}},
            ]}
        elif session_id:
            chroma_filter = {"session_id": {"$eq": session_id}}
        elif paper_title:
            chroma_filter = {"paper_title": {"$eq": paper_title}}
        else:
            chroma_filter = None

        fetch_k = min(k * 6, 120)
        try:
            if chroma_filter:
                dense_results = self._db.similarity_search(query, k=fetch_k, filter=chroma_filter)
            else:
                dense_results = self._db.similarity_search(query, k=fetch_k)
        except Exception:
            try:
                dense_results = self._db.similarity_search(query, k=fetch_k)
            except Exception:
                return []

        if not dense_results:
            return []

        if len(dense_results) <= k:
            return dense_results

        # BM25 over the dense candidate set
        corpus = [doc.page_content for doc in dense_results]
        tokenized = [self._tokenize(t) for t in corpus]
        bm25 = BM25Okapi(tokenized)
        bm25_scores = bm25.get_scores(self._tokenize(query))

        # Dense rank map: position in dense_results is its rank
        dense_rank = {i: i for i in range(len(dense_results))}

        # BM25 rank map: sort by score descending
        bm25_rank = {
            idx: rank
            for rank, idx in enumerate(
                sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)
            )
        }

        # Fuse
        fused = {
            i: self._rrf(dense_rank[i]) + self._rrf(bm25_rank.get(i, len(dense_results)))
            for i in range(len(dense_results))
        }

        top_indices = sorted(fused, key=fused.__getitem__, reverse=True)[:k]
        return [dense_results[i] for i in top_indices]
