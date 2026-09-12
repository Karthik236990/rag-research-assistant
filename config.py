"""
Central configuration for the RAG research assistant.
Override any of these via environment variables (see .env.example).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Paths -------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
VECTOR_DB_DIR = BASE_DIR / ".chroma_db"
COLLECTION_NAME = "research_documents"

# --- Chunking ------------------------------------------------------------
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))        # characters per chunk
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 150))  # overlap between chunks

# --- Retrieval -----------------------------------------------------------
TOP_K = int(os.getenv("TOP_K", 5))

# --- Embeddings ------------------------------------------------------------
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# --- LLM (Google Gemini) --------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1024))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.2))

# Supported file extensions for ingestion
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}
