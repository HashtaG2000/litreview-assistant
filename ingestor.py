import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from chunker import StructureAwareChunker

CHROMA_PATH = os.getenv("CHROMA_PERSIST_PATH", "/data/chroma_store")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def load_and_split(pdf_path: str) -> list:
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    return StructureAwareChunker().split(documents)


def store_chunks(chunks: list, paper_title: str, session_id: str = "default") -> None:
    embeddings = get_embeddings()
    for chunk in chunks:
        chunk.metadata["paper_title"] = paper_title
        chunk.metadata["session_id"] = session_id
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    db.add_documents(chunks)
    print(f"Stored {len(chunks)} chunks from '{paper_title}' (session={session_id})")


if __name__ == "__main__":
    chunks = load_and_split("test.pdf")
    print(f"Total chunks: {len(chunks)}")
    store_chunks(chunks, "Test Paper", "test-session")
