from langchain_community.document_loaders import PyPDFLoader
from core.ingestion.chunker import StructureAwareChunker


def load_and_split(pdf_path: str) -> list:
    """Load a PDF and return structure-aware chunks with section metadata."""
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    return StructureAwareChunker().split(documents)
