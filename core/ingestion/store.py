from core.config import CHROMA_PATH
from core.embeddings import get_embeddings


def store_chunks(chunks: list, paper_title: str, session_id: str = "default") -> None:
    """Embed and persist chunks into the Chroma vector store."""
    from langchain_chroma import Chroma  # lazy — chromadb transitively loads torch
    embeddings = get_embeddings()
    for chunk in chunks:
        chunk.metadata["paper_title"] = paper_title
        chunk.metadata["session_id"] = session_id
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    db.add_documents(chunks)
    print(f"Stored {len(chunks)} chunks from '{paper_title}' (session={session_id})")
