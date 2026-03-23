"""Ingest documents with Great Expectations validation and OpenLineage."""
import os
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from great_expectations.dataset import PandasDataset
import pandas as pd
from src.config import (
    CHROMA_PERSIST_DIR, COLLECTION_NAME, DATA_FOLDER,
    OLLAMA_BASE_URL, EMBEDDING_MODEL
)
from src.utils import load_pdfs_from_folder, get_text_splitter
from src.lineage import emit_lineage_event

def validate_documents(docs):
    """Use Great Expectations to validate documents."""
    # Convert to DataFrame with text and metadata
    data = []
    for doc in docs:
        data.append({
            "text": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page", 0)
        })
    df = pd.DataFrame(data)
    ge_df = PandasDataset(df)
    # Expect text not null and length > 0
    ge_df.expect_column_values_to_not_be_null("text")
    ge_df.expect_column_value_lengths_to_be_between("text", min_value=10, max_value=None)
    # Run validation
    results = ge_df.validate()
    if not results["success"]:
        raise ValueError("Document validation failed: " + str(results))
    print("Validation passed.")
    return docs

def main():
    # 1. Load documents
    print("Loading PDFs...")
    docs = load_pdfs_from_folder(DATA_FOLDER)
    if not docs:
        print("No PDFs found. Please add files to data/")
        return

    # 2. Validate with Great Expectations
    print("Validating documents...")
    validate_documents(docs)

    # 3. Split into chunks
    print("Splitting into chunks...")
    text_splitter = get_text_splitter()
    chunks = text_splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks.")

    # 4. Emit lineage for chunks
    emit_lineage_event("START", "chunk_documents", inputs=[], outputs=[])

    # 5. Generate embeddings and store
    print("Generating embeddings and storing in Chroma...")
    embeddings = OllamaEmbeddings(base_url=OLLAMA_BASE_URL, model=EMBEDDING_MODEL)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name=COLLECTION_NAME,
    )
    vectorstore.persist()
    print("Ingestion complete.")

    # 6. Emit lineage for vector store as output
    emit_lineage_event("COMPLETE", "store_embeddings", inputs=[], outputs=[
        {"namespace": "chromadb", "name": COLLECTION_NAME}
    ])

if __name__ == "__main__":
    main()