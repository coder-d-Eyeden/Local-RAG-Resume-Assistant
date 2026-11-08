"""
ChromaDB vector store operations and retriever configuration.
"""

import os
import shutil
import stat
import time
import gc
from typing import List, Optional, Dict, Any
from pathlib import Path

from langchain_core.documents import Document

from config.settings import VECTOR_DB_DIR, RETRIEVER_K


def _get_chroma_class():
    """Import Chroma from langchain_community or langchain_chroma."""
    try:
        from langchain_community.vectorstores import Chroma
        return Chroma
    except ImportError:
        try:
            from langchain_chroma import Chroma
            return Chroma
        except ImportError as exc:
            raise ImportError(
                "Neither langchain_community nor langchain_chroma is installed. "
                "Please run: pip install langchain-community chromadb"
            ) from exc


def vector_store_exists(persist_directory: str = VECTOR_DB_DIR) -> bool:
    """Check if a populated ChromaDB directory exists on disk."""
    path = Path(persist_directory)
    if not path.exists() or not path.is_dir():
        return False
    sqlite_file = path / "chroma.sqlite3"
    return sqlite_file.exists() or any(path.iterdir())


def load_existing_vector_store(
    embeddings,
    persist_directory: str = VECTOR_DB_DIR,
):
    """
    Load an existing Chroma vector store if present on disk.
    Returns None if the directory does not exist or has no documents.
    """
    if not vector_store_exists(persist_directory):
        return None

    Chroma = _get_chroma_class()
    try:
        vs = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
        )
        data = vs.get()
        if data and data.get("ids") and len(data["ids"]) > 0:
            return vs
        return None
    except Exception as e:
        print(f"Warning: Failed to load vector store from {persist_directory}: {e}")
        return None


def create_vector_store(
    documents: List[Document],
    embeddings,
    persist_directory: str = VECTOR_DB_DIR,
):
    """
    Create a new ChromaDB vector store from chunked documents and persist to disk.
    """
    Chroma = _get_chroma_class()
    os.makedirs(persist_directory, exist_ok=True)

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory,
    )
    
    if hasattr(vector_store, "persist"):
        try:
            vector_store.persist()
        except Exception:
            pass

    return vector_store


def get_retriever(vector_store, k: int = RETRIEVER_K):
    """Return a retriever instance from the vector store."""
    if vector_store is None:
        return None
    return vector_store.as_retriever(search_kwargs={"k": k})


def clear_vector_store(
    persist_directory: str = VECTOR_DB_DIR,
    vector_store=None,
) -> bool:
    """
    Completely clear the Chroma vector store from local storage and memory.
    Closes database connections, purges Chroma's system cache, and deletes
    the persist directory from disk.
    """
    import chromadb
    from chromadb.api.client import SharedSystemClient

    # 1. Close and delete all collections from the active client
    client = getattr(vector_store, "_client", None)
    if client is None and os.path.exists(persist_directory):
        try:
            client = chromadb.PersistentClient(path=persist_directory)
        except Exception:
            client = None

    if client is not None:
        try:
            for c in client.list_collections():
                try:
                    client.delete_collection(c.name)
                except Exception:
                    pass
        except Exception:
            pass

        try:
            client.close()
        except Exception:
            pass

    # 2. Purge Chroma's global system cache to release memory-mapped handles
    try:
        SharedSystemClient.clear_system_cache()
    except Exception:
        pass

    # 3. Clean references and force garbage collection
    vector_store = None
    client = None
    gc.collect()
    time.sleep(0.15)

    # 4. Remove persist directory from disk with retry loop
    def _handle_readonly(func, path, exc_info):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass

    success = False
    for _ in range(5):
        if not os.path.exists(persist_directory):
            success = True
            break
        try:
            shutil.rmtree(persist_directory, onerror=_handle_readonly)
            success = not os.path.exists(persist_directory)
            if success:
                break
        except Exception:
            time.sleep(0.15)

    return success


def get_vector_store_info(vector_store) -> Dict[str, Any]:
    """
    Inspect the vector store and return document and chunk statistics.
    """
    if vector_store is None:
        return {"total_chunks": 0, "sources": []}

    try:
        data = vector_store.get()
        ids = data.get("ids", [])
        metadatas = data.get("metadatas", []) or []
        sources = sorted(list(set(m.get("source", "Unknown") for m in metadatas if isinstance(m, dict))))
        return {
            "total_chunks": len(ids),
            "sources": sources,
        }
    except Exception:
        return {"total_chunks": 0, "sources": []}
