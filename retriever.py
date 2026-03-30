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
    db = get_db()
    results = db.similarity_search(query, k=k)
    return results

def check_relevance(research_idea, paper_title, chunks):
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
    
    if hasattr(response, 'content'):
        return response.content
    return str(response)

if __name__ == "__main__":
    results = search_similar("gamification assembly training", k=3)
    print(f"Found {len(results)} similar chunks")
    for i, chunk in enumerate(results):
        print(f"\nChunk {i+1} from: {chunk.metadata.get('paper_title', 'Unknown')}")
        print(chunk.page_content[:150])
