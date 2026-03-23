import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import CHROMA_PERSIST_DIR, COLLECTION_NAME, OLLAMA_BASE_URL, EMBEDDING_MODEL
from src.lineage import emit_lineage_event

def load_pdfs_from_folder(folder_path):
    """Load PDFs, emit lineage for each document."""
    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            loader = PyPDFLoader(file_path)
            loaded = loader.load()
            docs.extend(loaded)
            # Emit lineage for this file as an input dataset
            emit_lineage_event(
                "START", 
                f"load_document:{filename}",
                inputs=[{"namespace": "file", "name": file_path}],
                outputs=[]
            )
    return docs

def get_text_splitter(chunk_size=1000, chunk_overlap=200):
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )