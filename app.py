"""
Local RAG Resume Assistant - Streamlit Application Entrypoint.

A modular, local-first RAG application for document parsing, semantic search,
conversational Q&A, and structured resume critique powered by Ollama and LangChain.
"""

import streamlit as st

from config.settings import (
    DEFAULT_LLM_MODEL,
    DEFAULT_EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
    VECTOR_DB_DIR,
)
from core.llm import (
    get_embeddings,
    get_llm,
    check_ollama_connection,
    resolve_model_name,
    categorize_ollama_models,
)
from core.vector_store import (
    load_existing_vector_store,
    get_retriever,
    get_vector_store_info,
)
from core.rag_chain import build_rag_chain
from ui import (
    CUSTOM_CSS,
    render_header,
    render_sidebar,
    render_upload_view,
    render_chat_view,
    render_critique_view,
)


def initialize_session_state():
    """Set up initial Streamlit session state and load existing index if present."""
    if "ollama_url" not in st.session_state:
        st.session_state["ollama_url"] = OLLAMA_BASE_URL
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "critique_data" not in st.session_state:
        st.session_state["critique_data"] = None
    if "critique_markdown" not in st.session_state:
        st.session_state["critique_markdown"] = None
    if "doc_stats" not in st.session_state:
        st.session_state["doc_stats"] = None
    if "indexed_doc_name" not in st.session_state:
        st.session_state["indexed_doc_name"] = None
    if "active_llm_model" not in st.session_state:
        st.session_state["active_llm_model"] = None
    if "active_ollama_url" not in st.session_state:
        st.session_state["active_ollama_url"] = None

    # Auto-load existing Chroma vector store on startup if not already loaded
    if "vector_store" not in st.session_state:
        try:
            # Check available models on server
            _, _, server_models = check_ollama_connection(st.session_state["ollama_url"])
            installed_llms, installed_emb = categorize_ollama_models(server_models)

            # Determine embedding model
            target_emb = st.session_state.get("embedding_model", DEFAULT_EMBEDDING_MODEL)
            target_emb = resolve_model_name(target_emb, server_models)
            st.session_state["embedding_model"] = target_emb

            embeddings = get_embeddings(
                model_name=target_emb,
                base_url=st.session_state["ollama_url"],
                available_models=server_models,
            )
            vs = load_existing_vector_store(embeddings, VECTOR_DB_DIR)
            if vs is not None:
                info = get_vector_store_info(vs)
                if info["total_chunks"] > 0:
                    st.session_state["vector_store"] = vs
                    if info["sources"]:
                        st.session_state["indexed_doc_name"] = ", ".join(info["sources"])
                    st.session_state["doc_stats"] = {
                        "filename": st.session_state["indexed_doc_name"] or "Existing Chroma DB",
                        "total_chars": 0,
                        "num_chunks": info["total_chunks"],
                        "chunk_size": "N/A",
                    }
                else:
                    st.session_state["vector_store"] = None
            else:
                st.session_state["vector_store"] = None
        except Exception as e:
            print(f"Warning during vector store auto-load: {e}")
            st.session_state["vector_store"] = None


def sync_active_chain(config: dict):
    """
    Ensure the active RAG chain is synchronized with the selected LLM model.
    Rebuilds the chain automatically when the model or base URL changes.
    """
    selected_llm = config["llm_model"]
    selected_url = config["base_url"]
    server_models = config.get("server_models", [])

    resolved_llm = resolve_model_name(selected_llm, server_models)

    active_llm = st.session_state.get("active_llm_model")
    active_url = st.session_state.get("active_ollama_url")

    vs = st.session_state.get("vector_store")
    if vs is not None:
        # Rebuild if chain is missing OR if model/url has changed
        if (
            st.session_state.get("rag_chain") is None
            or active_llm != resolved_llm
            or active_url != selected_url
        ):
            try:
                retriever = get_retriever(vs)
                llm = get_llm(
                    model_name=resolved_llm,
                    base_url=selected_url,
                    available_models=server_models,
                )
                st.session_state["rag_chain"] = build_rag_chain(llm, retriever)
                st.session_state["retriever"] = retriever
                st.session_state["active_llm_model"] = resolved_llm
                st.session_state["active_ollama_url"] = selected_url
            except Exception as e:
                print(f"Failed to synchronize RAG chain: {e}")
                st.session_state["rag_chain"] = None


def main():
    # 1. Page Configuration
    st.set_page_config(
        page_title="Local RAG Resume Assistant",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 2. Inject Custom Theme & CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # 3. Initialize State
    initialize_session_state()

    # 4. Render Sidebar (Controls, Health Check & Model Discovery)
    config = render_sidebar()

    # 5. Synchronize RAG chain with current model selection
    sync_active_chain(config)

    # 6. Render Header Hero
    render_header(config["llm_model"], config["embedding_model"])

    # 7. Tabbed Navigation
    tab_upload, tab_chat, tab_critique = st.tabs(
        [
            "📄 Upload & Index Resume",
            "💬 Ask Q&A",
            "🎯 ATS Checker & Critique",
        ]
    )

    with tab_upload:
        render_upload_view(config)

    with tab_chat:
        render_chat_view(config)

    with tab_critique:
        render_critique_view(config)


if __name__ == "__main__":
    main()
