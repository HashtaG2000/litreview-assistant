import os
import re
import requests
from core.llm import call_llm_safe

_BASE = "https://api.semanticscholar.org/graph/v1"


class SemanticScholarClient:
    """
    Thin client for the Semantic Scholar Graph API.
    Works unauthenticated (100 req / 5 min) or with an API key (higher limits).
    Set SEMANTIC_SCHOLAR_API_KEY in your environment for the authenticated tier.
    """

    def __init__(self):
        key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        self._headers = {"x-api-key": key} if key else {}

    # ── Low-level HTTP ─────────────────────────────────────────────────────────

    def _get(self, path: str, params: dict) -> dict | None:
        try:
            resp = requests.get(
                f"{_BASE}{path}", params=params, headers=self._headers, timeout=12
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    # ── API methods ────────────────────────────────────────────────────────────

    def search_paper_by_title(self, title: str) -> dict | None:
        """Find the Semantic Scholar record for a paper by its title."""
        clean = title.replace(".pdf", "").replace("_", " ").replace("-", " ").strip()
        data = self._get("/paper/search", {
            "query": clean,
            "fields": "paperId,title,year,citationCount",
            "limit": 1,
        })
        return data["data"][0] if data and data.get("data") else None

    def get_citations(self, paper_id: str, limit: int = 30) -> list:
        """Papers that cited the given paper."""
        data = self._get(f"/paper/{paper_id}/citations", {
            "fields": "title,year,authors,abstract",
            "limit": limit,
        })
        if not data:
            return []
        return [item["citingPaper"] for item in data.get("data", []) if item.get("citingPaper")]

    def get_references(self, paper_id: str, limit: int = 30) -> list:
        """Papers cited by the given paper."""
        data = self._get(f"/paper/{paper_id}/references", {
            "fields": "title,year,authors,abstract",
            "limit": limit,
        })
        if not data:
            return []
        return [item["citedPaper"] for item in data.get("data", []) if item.get("citedPaper")]

    # ── High-level suggestion flow ─────────────────────────────────────────────

    def suggest_papers(
        self,
        root_title: str,
        accepted_titles: list,
        research_idea: str,
        llm,
    ) -> list:
        """
        Fetch the citation network of the root paper, filter out already-accepted
        papers, then ask the LLM to rank the top 5 by relevance.

        Returns a list of dicts: {title, year, abstract, relevance_summary}
        """
        paper = self.search_paper_by_title(root_title)
        if not paper:
            return []

        paper_id = paper["paperId"]
        candidates = self.get_citations(paper_id) + self.get_references(paper_id)

        def _clean(t: str) -> str:
            return t.lower().replace(".pdf", "").replace("_", " ").replace("-", " ").strip()

        accepted_clean = {_clean(t) for t in accepted_titles}
        candidates = [
            p for p in candidates
            if p.get("title") and _clean(p["title"]) not in accepted_clean and p.get("abstract")
        ]

        # Deduplicate
        seen, unique = set(), []
        for p in candidates:
            key = _clean(p["title"])
            if key not in seen:
                seen.add(key)
                unique.append(p)

        if not unique:
            return []

        candidate_list = "\n".join([
            f"{i+1}. [{p['title']} ({p.get('year', 'n/a')})] — {p['abstract'][:200]}"
            for i, p in enumerate(unique[:20])
        ])
        prompt = f"""Research idea: {research_idea}

Below are papers from the citation network of the root paper. Select the 5 MOST RELEVANT.

Candidates:
{candidate_list}

For each selected paper output exactly:
PAPER: [exact title as listed above]
YEAR: [year]
RELEVANCE: [one sentence explanation of why it is relevant]
---
"""
        try:
            response = call_llm_safe(llm, prompt)
            text = response.content if hasattr(response, "content") else str(response)
            return _parse_suggestions(text, unique)
        except Exception:
            return []


# ── Output parsing ─────────────────────────────────────────────────────────────

def _parse_suggestions(text: str, candidates: list) -> list:
    suggestions = []
    for block in text.split("---"):
        block = block.strip()
        if not block:
            continue
        title_m = re.search(r'PAPER:\s*\[?(.+?)\]?\s*\n', block, re.IGNORECASE)
        year_m = re.search(r'YEAR:\s*(\d{4})', block, re.IGNORECASE)
        rel_m = re.search(r'RELEVANCE:\s*(.+)', block, re.IGNORECASE | re.DOTALL)
        if not title_m:
            continue
        title = title_m.group(1).strip()
        abstract = next(
            (p.get("abstract", "")[:300] for p in candidates
             if p.get("title", "").lower()[:40] == title.lower()[:40]),
            "",
        )
        suggestions.append({
            "title": title,
            "year": year_m.group(1) if year_m else "n/a",
            "abstract": abstract,
            "relevance_summary": rel_m.group(1).strip() if rel_m else "",
        })
        if len(suggestions) >= 5:
            break
    return suggestions
