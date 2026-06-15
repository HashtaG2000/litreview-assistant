import re
from typing import TypedDict
from core.llm import call_llm_safe


class SynthesisMatrix(TypedDict):
    paper_title: str
    sample_size: str
    methodology: str
    key_findings: str
    limitations: str


# ── LLM output parsing ─────────────────────────────────────────────────────────

def _parse_field(text: str, label: str) -> str:
    pattern = rf'{label}:\s*(.+?)(?=\n[A-Z_]{{3,}}:|$)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else "Not specified"


# ── Per-paper extraction ───────────────────────────────────────────────────────

def extract_matrix_row(llm, paper_title: str, chunks: list, research_idea: str) -> SynthesisMatrix:
    """Extract structured metadata from a single paper's chunks."""
    context = "\n\n".join([c.page_content for c in chunks[:6]])
    prompt = f"""You are extracting structured data from an academic paper for a literature review synthesis matrix.

Research idea: {research_idea}
Paper: {paper_title}

Excerpts from the paper:
{context}

Extract the following. Write "Not specified" if a field cannot be determined.
Output ONLY these four labeled fields:

SAMPLE_SIZE: (dataset size, number of participants, or data scope)
METHODOLOGY: (research method or experimental approach)
KEY_FINDINGS: (main results or conclusions, 1-2 sentences)
LIMITATIONS: (limitations acknowledged by the authors)
"""
    try:
        response = call_llm_safe(llm, prompt)
        text = response.content if hasattr(response, "content") else str(response)
        return SynthesisMatrix(
            paper_title=paper_title,
            sample_size=_parse_field(text, "SAMPLE_SIZE"),
            methodology=_parse_field(text, "METHODOLOGY"),
            key_findings=_parse_field(text, "KEY_FINDINGS"),
            limitations=_parse_field(text, "LIMITATIONS"),
        )
    except Exception:
        return SynthesisMatrix(
            paper_title=paper_title,
            sample_size="Could not extract",
            methodology="Could not extract",
            key_findings="Could not extract",
            limitations="Could not extract",
        )


# ── Batch extraction ───────────────────────────────────────────────────────────

def build_synthesis_matrix(
    llm,
    accepted_papers: list,
    search_fn,
    research_idea: str,
    session_id: str,
) -> list:
    """Build a synthesis matrix row for every accepted paper."""
    return [
        extract_matrix_row(
            llm,
            paper,
            search_fn(research_idea, paper, k=6, session_id=session_id),
            research_idea,
        )
        for paper in accepted_papers
    ]


# ── Contradiction / consensus detection ───────────────────────────────────────

def detect_contradictions(llm, matrix: list, research_idea: str) -> str:
    """
    Compare key findings across all papers and highlight where they agree
    or contradict each other.  Returns a formatted prose string.
    """
    if len(matrix) < 2:
        return ""

    findings_list = "\n".join([
        f"{i+1}. [{row['paper_title']}]: {row['key_findings']}"
        for i, row in enumerate(matrix)
    ])
    prompt = f"""You are a research analyst comparing findings across papers on: {research_idea}

Key findings per paper:
{findings_list}

Identify contradictions and consensus. Output exactly two labeled sections:

CONTRADICTIONS: (specific disagreements between papers, citing paper names; or "No significant contradictions identified.")
CONSENSUS: (findings that multiple papers agree on)
"""
    try:
        response = call_llm_safe(llm, prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception:
        return ""
