"""
LLM and Embeddings management for Ollama integration.
Includes smart model resolution, server diagnostics, and tag normalization.
"""

from typing import List, Tuple, Optional
import requests

from config.settings import OLLAMA_BASE_URL, DEFAULT_LLM_MODEL, DEFAULT_EMBEDDING_MODEL


def check_ollama_connection(base_url: str = OLLAMA_BASE_URL) -> Tuple[bool, str, List[str]]:
    """
    Check if the Ollama server is accessible and retrieve available models.
    
    Returns:
        (is_online, status_message, list_of_model_names)
    """
    url = f"{base_url.rstrip('/')}/api/tags"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
            return True, "Ollama server is active and responding.", models
        return False, f"Ollama returned HTTP status {response.status_code}", []
    except requests.exceptions.ConnectionError:
        return (
            False,
            f"Cannot connect to Ollama at {base_url}. Ensure Ollama is running (`ollama serve`).",
            [],
        )
    except Exception as e:
        return False, f"Ollama connection check failed: {e}", []


def categorize_ollama_models(models: List[str]) -> Tuple[List[str], List[str]]:
    """
    Separate Ollama models into LLMs and Embedding models.
    """
    embedding_keywords = ("embed", "bge", "minilm", "nomic")
    llms = []
    embeddings = []
    for m in models:
        m_lower = m.lower()
        if any(k in m_lower for k in embedding_keywords):
            embeddings.append(m)
        else:
            llms.append(m)
    return llms, embeddings


def resolve_model_name(requested_model: str, available_models: Optional[List[str]] = None) -> str:
    """
    Intelligently match requested model name against actual Ollama model tags.
    Handles tag mismatches like 'llama3.2' -> 'llama3.2:3b' or 'llama3.2:latest'.
    """
    if not available_models or not requested_model:
        return requested_model

    # Exact match
    if requested_model in available_models:
        return requested_model

    # Case-insensitive exact match
    for m in available_models:
        if m.lower() == requested_model.lower():
            return m

    # Tag variation: requested + ':latest'
    if f"{requested_model}:latest" in available_models:
        return f"{requested_model}:latest"

    # If requested has ':latest', strip and search
    if requested_model.endswith(":latest"):
        base = requested_model[:-7]
        for m in available_models:
            if m.lower() == base.lower() or m.lower().startswith(f"{base.lower()}:"):
                return m

    # Match base prefix, e.g. 'llama3.2' matching 'llama3.2:3b' or 'llama3.2:1b'
    base_prefix = requested_model.split(":")[0].lower()
    matches = [m for m in available_models if m.split(":")[0].lower() == base_prefix]
    if matches:
        return matches[0]

    return requested_model


def get_llm(
    model_name: str = DEFAULT_LLM_MODEL,
    base_url: str = OLLAMA_BASE_URL,
    temperature: float = 0.2,
    available_models: Optional[List[str]] = None,
):
    """
    Instantiate an Ollama LLM for response generation.
    Supports langchain_community.llms.Ollama with fallback to langchain_ollama.
    """
    if available_models:
        model_name = resolve_model_name(model_name, available_models)

    try:
        from langchain_community.llms import Ollama
        return Ollama(
            model=model_name,
            base_url=base_url,
            temperature=temperature,
            num_ctx=4096,
        )
    except ImportError:
        try:
            from langchain_ollama import OllamaLLM
            return OllamaLLM(
                model=model_name,
                base_url=base_url,
                temperature=temperature,
                num_ctx=4096,
            )
        except ImportError as exc:
            raise ImportError(
                "Neither langchain_community nor langchain_ollama is installed. "
                "Please run: pip install langchain-community langchain-ollama"
            ) from exc


def get_embeddings(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    base_url: str = OLLAMA_BASE_URL,
    available_models: Optional[List[str]] = None,
):
    """
    Instantiate an Ollama embeddings model.
    Supports langchain_community.embeddings.OllamaEmbeddings with fallback to langchain_ollama.
    """
    if available_models:
        model_name = resolve_model_name(model_name, available_models)

    try:
        from langchain_community.embeddings import OllamaEmbeddings
        return OllamaEmbeddings(
            model=model_name,
            base_url=base_url,
            model_kwargs={"keep_alive": -1},
        )
    except ImportError:
        try:
            from langchain_ollama import OllamaEmbeddings
            return OllamaEmbeddings(
                model=model_name,
                base_url=base_url,
            )
        except ImportError as exc:
            raise ImportError(
                "Neither langchain_community nor langchain_ollama is installed. "
                "Please run: pip install langchain-community langchain-ollama"
            ) from exc
