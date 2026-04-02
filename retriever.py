from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from llm import get_llm

CHROMA_PATH = "chroma_store"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_db():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )


def search_similar(query, k=3):
    """Unfiltered similarity search across the entire vector store."""
    db = get_db()
    return db.similarity_search(query, k=k)


def search_similar_filtered(query, paper_title, k=4):
    """
    Fix 3: Similarity search scoped to a single paper using the paper_title
    metadata filter.  This prevents the review from being dominated by whichever
    paper happens to have the most chunks in the shared collection.

    Falls back to unfiltered search if the filter returns no results
    (e.g. older Chroma builds that ignore the where clause).
    """
    db = get_db()
    try:
        results = db.similarity_search(
            query,
            k=k,
            filter={"paper_title": paper_title}
        )
        if results:
            return results
    except Exception:
        pass
    # Fallback: unfiltered (graceful degradation)
    return db.similarity_search(query, k=k)


def check_relevance(research_idea, paper_title, chunks):
    """
    Ask the LLM whether the candidate paper is relevant to the research idea.
    `chunks` should be the semantically top-ranked chunks from the candidate
    paper itself (via evaluator.get_top_chunks_by_similarity), NOT a DB search.
    """
    context = "\n\n".join([chunk.page_content for chunk in chunks])

    prompt = f"""
You are a strict research assistant validating papers for a literature review.

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
    response = llm.invoke(prompt)

    if hasattr(response, "content"):
        return response.content
    return str(response)


if __name__ == "__main__":
    results = search_similar("gamification assembly training", k=3)
    print(f"Found {len(results)} similar chunks")
    for i, chunk in enumerate(results):
        print(f"\nChunk {i+1} from: {chunk.metadata.get('paper_title', 'Unknown')}")
        print(chunk.page_content[:150])
