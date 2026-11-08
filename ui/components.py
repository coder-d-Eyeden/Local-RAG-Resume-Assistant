"""
Reusable UI components for Streamlit: Header, Sidebar, Metric Cards, Status indicators.
"""

from typing import Dict, Any
import streamlit as st

from config.settings import (
    AVAILABLE_LLM_MODELS,
    AVAILABLE_EMBEDDING_MODELS,
    DEFAULT_LLM_MODEL,
    DEFAULT_EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
    VECTOR_DB_DIR,
)
from core.llm import check_ollama_connection, categorize_ollama_models, resolve_model_name
from core.vector_store import clear_vector_store, get_vector_store_info


def render_header(llm_model: str, embedding_model: str):
    """Render the top visual banner."""
    st.markdown(
        f"""
        <div class="hero-banner">
            <h1 class="hero-title">Local RAG Resume Assistant</h1>
            <p class="hero-subtitle">
                Powered by <strong>LangChain</strong>, <strong>Ollama</strong> (<code>{llm_model}</code> & <code>{embedding_model}</code>), and <strong>ChromaDB</strong>.
                <br>Upload your resume to perform intelligent conversational Q&A and generate structured critiques locally.
            </p>
            <div class="badge-container">
                <span class="badge badge-green">● Local & Private</span>
                <span class="badge badge-blue">LangChain RAG</span>
                <span class="badge badge-purple">ChromaDB</span>
                <span class="badge badge-amber">Streamlit UI</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> Dict[str, Any]:
    """
    Render configuration sidebar with model controls, connectivity check,
    and vector store status.
    """
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Ollama URL
        base_url = st.text_input(
            "Ollama Base URL",
            value=st.session_state.get("ollama_url", OLLAMA_BASE_URL),
            help="URL where your local Ollama instance is running (default: http://localhost:11434)",
        )
        st.session_state["ollama_url"] = base_url

        # Check Connection and discover installed models
        is_connected, msg, server_models = check_ollama_connection(base_url)
        st.session_state["ollama_connected"] = is_connected
        st.session_state["server_models"] = server_models

        installed_llms, installed_embeddings = categorize_ollama_models(server_models)

        if is_connected:
            st.success("🟢 Ollama Connected", icon="✅")
            if server_models:
                with st.expander(f"Installed Models ({len(server_models)})", expanded=False):
                    for m in server_models:
                        st.markdown(f"- `{m}`")
        else:
            st.warning("🟠 Ollama Not Detected", icon="⚠️")
            st.caption(f"{msg}\nRun `ollama serve` in a terminal.")

        st.divider()

        # Model Selections
        st.subheader("🤖 Models")
        
        # Build LLM options: prioritize installed LLMs, followed by common presets
        llm_options = list(installed_llms)
        for preset in AVAILABLE_LLM_MODELS:
            if preset not in llm_options:
                llm_options.append(preset)

        # Smart default selection
        current_llm = st.session_state.get("llm_model")
        if not current_llm:
            # If nothing set yet, prefer llama3.2:3b if installed, else first installed, else DEFAULT
            if "llama3.2:3b" in installed_llms:
                current_llm = "llama3.2:3b"
            elif installed_llms:
                current_llm = installed_llms[0]
            else:
                current_llm = DEFAULT_LLM_MODEL
        elif installed_llms and current_llm not in installed_llms:
            # If current selection is not installed, try resolving (e.g. llama3.2 -> llama3.2:3b)
            resolved = resolve_model_name(current_llm, installed_llms)
            if resolved in installed_llms:
                current_llm = resolved
            elif "llama3.2:3b" in installed_llms:
                current_llm = "llama3.2:3b"

        if current_llm not in llm_options:
            llm_options.insert(0, current_llm)

        llm_index = llm_options.index(current_llm) if current_llm in llm_options else 0
        llm_model = st.selectbox(
            "LLM Model",
            options=llm_options,
            index=llm_index,
            help="Choose the model used for answering questions and resume critique.",
        )
        st.session_state["llm_model"] = llm_model

        # Embedding Model selection
        emb_options = list(installed_embeddings)
        for preset in AVAILABLE_EMBEDDING_MODELS:
            if preset not in emb_options:
                emb_options.append(preset)

        current_emb = st.session_state.get("embedding_model")
        if not current_emb:
            if installed_embeddings:
                current_emb = installed_embeddings[0]
            else:
                current_emb = DEFAULT_EMBEDDING_MODEL
        elif installed_embeddings and current_emb not in installed_embeddings:
            resolved_emb = resolve_model_name(current_emb, installed_embeddings)
            if resolved_emb in installed_embeddings:
                current_emb = resolved_emb

        if current_emb not in emb_options:
            emb_options.insert(0, current_emb)

        emb_index = emb_options.index(current_emb) if current_emb in emb_options else 0
        embedding_model = st.selectbox(
            "Embedding Model",
            options=emb_options,
            index=emb_index,
            help="Choose the model used to convert text chunks into vector embeddings.",
        )
        st.session_state["embedding_model"] = embedding_model

        st.divider()

        # Resume Index Status
        st.subheader("📚 Index Status")
        vector_store = st.session_state.get("vector_store")
        info = get_vector_store_info(vector_store)
        
        if info["total_chunks"] > 0:
            sources_str = ", ".join(info["sources"]) if info["sources"] else "Uploaded Resume"
            st.success(f"**Loaded:** {sources_str}\n\n**Chunks:** {info['total_chunks']}")
        else:
            st.info("No resume indexed yet. Go to **Upload & Index** tab.")

        # Action Buttons
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Reset DB", use_container_width=True, help="Wipe vector store and reload"):
                vs = st.session_state.get("vector_store")
                deleted = clear_vector_store(VECTOR_DB_DIR, vs)
                st.session_state["vector_store"] = None
                st.session_state["retriever"] = None
                st.session_state["rag_chain"] = None
                st.session_state["active_llm_model"] = None
                st.session_state["critique_data"] = None
                st.session_state["critique_markdown"] = None
                st.session_state["indexed_doc_name"] = None
                st.session_state["doc_stats"] = None
                st.session_state["raw_text"] = None
                if deleted:
                    st.toast("Database wiped from local storage!", icon="🗑️")
                else:
                    st.toast("Database reset and emptied!", icon="✅")
                st.rerun()

        with col2:
            if st.button("🧹 Clear Chat", use_container_width=True, help="Clear message history"):
                st.session_state["messages"] = []
                st.rerun()

        st.caption("v2.1 Smart Model Sync • Streamlit Edition")

    return {
        "base_url": base_url,
        "llm_model": llm_model,
        "embedding_model": embedding_model,
        "server_models": server_models,
    }


def render_stats_metrics(stats: Dict[str, Any]):
    """Render 4 responsive metric tiles for indexed documents."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Source File", stats.get("filename", "N/A"))
    with col2:
        st.metric("Characters", f"{stats.get('total_chars', 0):,}")
    with col3:
        st.metric("Chunks Generated", stats.get("num_chunks", 0))
    with col4:
        st.metric("Chunk Size", f"{stats.get('chunk_size', 1000)} chars")
