from core.llm import get_llm, call_llm_safe


def check_relevance(research_idea: str, paper_title: str, chunks: list) -> str:
    """
    Ask the LLM whether the candidate paper is relevant to the research idea.
    Expects the top-ranked chunks from the paper (not a DB search result).
    Returns a string starting with RELEVANT or NOT RELEVANT.
    """
    context = "\n\n".join([chunk.page_content for chunk in chunks])
    prompt = f"""You are a strict research assistant validating papers for a literature review.

Research idea: {research_idea}

Paper title: {paper_title}

Relevant excerpts from the paper:
{context}

Your task: decide if this paper directly supports the research idea above.

Rules:
- If the paper is clearly about the same topic, respond with: RELEVANT
- If the paper is only loosely related or off-topic, respond with: NOT RELEVANT
- You must start your response with either RELEVANT or NOT RELEVANT
- Follow with one sentence explaining why

Be strict. Only accept papers that directly contribute to the research idea.
"""
    llm = get_llm()
    response = call_llm_safe(llm, prompt)
    return response.content if hasattr(response, "content") else str(response)


def check_counter_relevance(research_idea: str, paper_title: str, chunks: list) -> str:
    """
    Devil's advocate: one concrete reason a researcher might NOT include this paper.
    Returns a 1–2 sentence string, or empty string on failure.
    """
    context = "\n\n".join([chunk.page_content for chunk in chunks[:4]])
    prompt = f"""You are a critical research reviewer playing devil's advocate.

Research idea: {research_idea}
Paper: {paper_title}

Excerpts:
{context}

Give ONE specific, concrete reason why a researcher might decide NOT to include this paper \
in their literature review. Focus on methodological limitations, scope mismatch, or relevance \
gaps. Be direct and specific. One or two sentences only.
"""
    try:
        llm = get_llm()
        response = call_llm_safe(llm, prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception:
        return ""
