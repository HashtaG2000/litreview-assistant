import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from llm import get_llm, call_llm_safe
from hybrid_retriever import HybridRetriever
from reranker import rerank

CHROMA_PATH = os.getenv("CHROMA_PERSIST_PATH", "/data/chroma_store")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_db():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)


def search_similar(query: str, k: int = 3, session_id: str = None) -> list:
    """Unfiltered similarity search, optionally scoped to a session."""
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


def search_similar_filtered(query: str, paper_title: str, k: int = 4, session_id: str = None) -> list:
    """
    Hybrid (BM25 + dense) search scoped to a single paper, with cross-encoder reranking.
    Falls back to plain dense search if hybrid retrieval fails.
    """
    db = get_db()
    retriever = HybridRetriever(db)
    try:
        candidates = retriever.search(
            query,
            session_id=session_id or "default",
            paper_title=paper_title,
            k=max(k * 2, 12),
        )
        if candidates:
            return rerank(query, candidates, top_k=k)
    except Exception:
        pass
    # Fallback: plain dense search filtered by paper_title
    try:
        results = db.similarity_search(
            query, k=k, filter={"paper_title": {"$eq": paper_title}}
        )
        if results:
            return results
    except Exception:
        pass
    return db.similarity_search(query, k=k)


def check_relevance(research_idea: str, paper_title: str, chunks: list) -> str:
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
    """Devil's advocate: one specific reason NOT to include this paper."""
    context = "\n\n".join([chunk.page_content for chunk in chunks[:4]])
    prompt = f"""You are a critical research reviewer playing devil's advocate.

Research idea: {research_idea}
Paper: {paper_title}

Excerpts:
{context}

Give ONE specific, concrete reason why a researcher might decide NOT to include this paper in their literature review. Focus on methodological limitations, scope mismatch, or relevance gaps. Be direct and specific. One or two sentences only.
"""
    try:
        llm = get_llm()
        response = call_llm_safe(llm, prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception:
        return ""


if __name__ == "__main__":
    results = search_similar("gamification assembly training", k=3)
    print(f"Found {len(results)} chunks")
    for i, chunk in enumerate(results):
        print(f"\nChunk {i+1} from: {chunk.metadata.get('paper_title', 'Unknown')}")
        print(chunk.page_content[:150])
