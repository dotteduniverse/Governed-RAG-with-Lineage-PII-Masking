"""Query API with PII masking and audit logging."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from typing import List, Optional
from src.config import (
    OLLAMA_BASE_URL, EMBEDDING_MODEL, LLM_MODEL,
    CHROMA_PERSIST_DIR, COLLECTION_NAME, PII_DETECTION_ENABLED
)
from src.pii_detector import mask_pii
from src.audit import log_query

app = FastAPI(title="Governed RAG")

# Initialize components
embeddings = OllamaEmbeddings(base_url=OLLAMA_BASE_URL, model=EMBEDDING_MODEL)
vectorstore = Chroma(
    persist_directory=CHROMA_PERSIST_DIR,
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
llm = Ollama(base_url=OLLAMA_BASE_URL, model=LLM_MODEL)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
)

class QueryRequest(BaseModel):
    question: str
    user_id: str

class QueryResponse(BaseModel):
    answer: str
    audit_id: int
    contexts: Optional[List[str]] = []

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        # 1. Retrieve relevant chunks
        result = qa_chain.invoke({"query": request.question})
        answer = result["result"]
        source_docs = result["source_documents"]
        contexts = [doc.page_content for doc in source_docs]

        # 2. Mask PII in contexts (if enabled)
        masked_contexts = []
        for ctx in contexts:
            if PII_DETECTION_ENABLED:
                masked_ctx = mask_pii(ctx)
            else:
                masked_ctx = ctx
            masked_contexts.append(masked_ctx)

        # 3. Log query (store masked contexts as joined string)
        audit_id = log_query(
            user_id=request.user_id,
            question=request.question,
            masked_context="\n---\n".join(masked_contexts),
            answer=answer
        )
        return QueryResponse(
            answer=answer,
            audit_id=audit_id,
            contexts=masked_contexts
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}