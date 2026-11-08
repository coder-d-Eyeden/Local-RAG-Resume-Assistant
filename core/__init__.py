"""
Core module for RAG Assistant: LLM, Embeddings, Ingestion, Vector Store, RAG Chain, and Critique.
"""

from .llm import (
    get_llm,
    get_embeddings,
    check_ollama_connection,
    resolve_model_name,
    categorize_ollama_models,
)
from .document_loader import extract_text_from_file, process_and_chunk_document
from .vector_store import (
    load_existing_vector_store,
    create_vector_store,
    get_retriever,
    clear_vector_store,
    get_vector_store_info,
    vector_store_exists,
)
from .rag_chain import build_rag_chain, stream_rag_answer, get_rag_answer
from .critique import generate_critique, format_critique_markdown

__all__ = [
    "get_llm",
    "get_embeddings",
    "check_ollama_connection",
    "resolve_model_name",
    "categorize_ollama_models",
    "extract_text_from_file",
    "process_and_chunk_document",
    "load_existing_vector_store",
    "create_vector_store",
    "get_retriever",
    "clear_vector_store",
    "get_vector_store_info",
    "vector_store_exists",
    "build_rag_chain",
    "stream_rag_answer",
    "get_rag_answer",
    "generate_critique",
    "format_critique_markdown",
]
