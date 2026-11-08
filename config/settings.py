"""
Configuration settings for Local RAG Resume Assistant.
Values can be customized here or overridden via environment variables.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", str(BASE_DIR / "chroma_db"))

# Ollama API Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")
DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# Presets for UI dropdowns (prioritizes modern 3B models like llama3.2:3b)
AVAILABLE_LLM_MODELS = [
    "llama3.2:3b",
    "llama3.2:1b",
    "llama3.2",
    "llama3",
    "llama3.1",
    "mistral",
    "qwen2.5",
    "phi3",
    "gemma2",
]

AVAILABLE_EMBEDDING_MODELS = [
    "nomic-embed-text",
    "all-minilm",
    "mxbai-embed-large",
    "bge-m3",
]

# Document Splitting Settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# RAG Retrieval Settings
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "5"))

# Allowed file types for resume uploads
SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md"]
