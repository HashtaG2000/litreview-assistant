import numpy as np
from core.embeddings import get_embeddings

# ── Cosine similarity helpers ──────────────────────────────────────────────────

def _cosine(vec_a, vec_b) -> float:
    a, b = np.array(vec_a, dtype=np.float32), np.array(vec_b, dtype=np.float32)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom > 1e-10 else 0.0


def _scale_to_pct(cosine_score: float) -> int:
    """Map cosine similarity to a 0–100 confidence percentage."""
    scaled = max(0.0, min(1.0, (cosine_score - 0.15) / 0.70))
    return int(round(scaled * 100))


# ── Public helpers ─────────────────────────────────────────────────────────────

def confidence_color(pct: int) -> str:
    if pct >= 65:
        return "#4ade80"   # green
    if pct >= 40:
        return "#fbbf24"   # amber
    return "#f87171"       # red


def get_top_chunks_by_similarity(research_idea: str, chunks: list, k: int = 6):
    """
    Rank a candidate paper's own chunks by semantic similarity to the research
    idea and return the top-k most relevant ones.

    Returns:
        top_chunks  – list of Document objects (len <= k)
        confidence  – int 0–100, average similarity of selected chunks
    """
    if not chunks:
        return [], 0

    k = min(k, len(chunks))
    embedder = get_embeddings()

    idea_emb = embedder.embed_query(research_idea)
    chunk_embs = embedder.embed_documents([c.page_content for c in chunks])

    scores = [_cosine(idea_emb, emb) for emb in chunk_embs]
    top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

    top_chunks = [chunks[i] for i in top_idx]
    avg_score = float(np.mean([scores[i] for i in top_idx]))
    return top_chunks, _scale_to_pct(avg_score)


def compute_review_quality(
    research_idea: str,
    paper_titles: list,
    search_fn,
    k_per_paper: int = 4,
):
    """
    Compute per-paper retrieval confidence scores for the Review Quality panel.

    Args:
        search_fn  – callable(query, paper_title, k) -> list[Document]

    Returns:
        paper_stats – dict[title] = {"chunks_retrieved": int, "confidence": int}
        overall     – int 0–100 overall confidence
    """
    embedder = get_embeddings()
    idea_emb = embedder.embed_query(research_idea)

    paper_stats = {}
    all_scores = []

    for title in paper_titles:
        chunks = search_fn(research_idea, title, k_per_paper)
        if not chunks:
            paper_stats[title] = {"chunks_retrieved": 0, "confidence": 0}
            continue
        embs = embedder.embed_documents([c.page_content for c in chunks])
        scores = [_cosine(idea_emb, emb) for emb in embs]
        avg = float(np.mean(scores))
        all_scores.extend(scores)
        paper_stats[title] = {
            "chunks_retrieved": len(chunks),
            "confidence": _scale_to_pct(avg),
        }

    overall = _scale_to_pct(float(np.mean(all_scores))) if all_scores else 0
    return paper_stats, overall
