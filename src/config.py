import os
from dotenv import load_dotenv

load_dotenv()

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")

# Chroma
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "governed_docs")

# PostgreSQL (audit)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "audit_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# OpenLineage
MARQUEZ_URL = os.getenv("MARQUEZ_URL", "http://localhost:5000")
OPENLINEAGE_DISABLED = os.getenv("OPENLINEAGE_DISABLED", "false").lower() == "true"

# PII
PII_DETECTION_ENABLED = os.getenv("PII_DETECTION_ENABLED", "true").lower() == "true"