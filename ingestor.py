from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

CHROMA_PATH = "chroma_store"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def load_and_split(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    return chunks

def store_chunks(chunks, paper_title):
    embeddings = get_embeddings()
    
    for chunk in chunks:
        chunk.metadata["paper_title"] = paper_title
    
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    db.add_documents(chunks)
    print(f"Stored {len(chunks)} chunks from '{paper_title}'")

if __name__ == "__main__":
    chunks = load_and_split("test.pdf")
    print(f"Total chunks created: {len(chunks)}")
    store_chunks(chunks, "Test Paper")
