"""
Upload & Index View: Handles file uploading, parsing, chunking, and ChromaDB indexing.
"""

import streamlit as st

from config.settings import VECTOR_DB_DIR
from core.document_loader import process_and_chunk_document
from core.llm import get_embeddings, get_llm, resolve_model_name
from core.vector_store import create_vector_store, get_retriever, get_vector_store_info
from core.rag_chain import build_rag_chain
from ui.components import render_stats_metrics


def render_upload_view(config: dict):
    """Render the Upload & Index Resume tab."""
    st.markdown("### 📄 Step 1: Upload & Index Your Resume")
    st.markdown(
        "Upload your resume document below. The file will be parsed, split into contextual chunks, "
        "and converted into numerical vector embeddings using your local Ollama embedding model."
    )

    uploaded_file = st.file_uploader(
        "Select Resume File",
        type=["pdf", "docx", "txt", "md"],
        help="Supported formats: PDF (.pdf), Microsoft Word (.docx), Plain Text (.txt, .md)",
    )

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        process_btn = st.button(
            "⚡ Process & Index Resume",
            type="primary",
            use_container_width=True,
            disabled=uploaded_file is None,
        )

    server_models = config.get("server_models", [])

    if process_btn and uploaded_file is not None:
        with st.status("Processing and indexing resume...", expanded=True) as status:
            try:
                # 1. Parse & Chunk
                st.write(f"📖 Parsing `{uploaded_file.name}` and generating chunks...")
                chunks, raw_text, stats = process_and_chunk_document(
                    uploaded_file,
                    filename=uploaded_file.name,
                )
                st.write(f"✓ Extracted {stats['total_chars']:,} characters into {stats['num_chunks']} chunks.")

                # 2. Embedding Model
                resolved_emb = resolve_model_name(config["embedding_model"], server_models)
                st.write(f"🧠 Connecting to embedding model `{resolved_emb}`...")
                embeddings = get_embeddings(
                    model_name=resolved_emb,
                    base_url=config["base_url"],
                    available_models=server_models,
                )

                # 3. Vector Database
                st.write(f"💾 Storing vectors in ChromaDB (`{VECTOR_DB_DIR}`)...")
                vector_store = create_vector_store(
                    documents=chunks,
                    embeddings=embeddings,
                    persist_directory=VECTOR_DB_DIR,
                )

                # 4. Retriever & Chain
                resolved_llm = resolve_model_name(config["llm_model"], server_models)
                st.write(f"🔗 Initializing RAG pipeline with `{resolved_llm}`...")
                retriever = get_retriever(vector_store)
                llm = get_llm(
                    model_name=resolved_llm,
                    base_url=config["base_url"],
                    available_models=server_models,
                )
                rag_chain = build_rag_chain(llm, retriever)

                # Update session state
                st.session_state["vector_store"] = vector_store
                st.session_state["retriever"] = retriever
                st.session_state["rag_chain"] = rag_chain
                st.session_state["active_llm_model"] = resolved_llm
                st.session_state["active_ollama_url"] = config["base_url"]
                st.session_state["indexed_doc_name"] = uploaded_file.name
                st.session_state["doc_stats"] = stats
                st.session_state["raw_text"] = raw_text
                st.session_state["critique_data"] = None
                st.session_state["critique_markdown"] = None

                status.update(
                    label="🎉 Resume successfully processed and indexed!",
                    state="complete",
                    expanded=False,
                )
                st.toast("Resume indexed successfully!", icon="✅")

            except Exception as e:
                status.update(
                    label=f"❌ Error during processing: {e}",
                    state="error",
                    expanded=True,
                )
                st.error(f"Processing failed: {e}")
                return

    # Display Current Index Info if available
    vector_store = st.session_state.get("vector_store")
    doc_stats = st.session_state.get("doc_stats")

    if doc_stats:
        st.divider()
        st.markdown("#### 📊 Document Summary")
        render_stats_metrics(doc_stats)
    elif vector_store:
        info = get_vector_store_info(vector_store)
        if info["total_chunks"] > 0:
            st.divider()
            st.info(f"Existing vector index loaded with **{info['total_chunks']}** chunks.")

    # Extracted text preview
    raw_text = st.session_state.get("raw_text")
    if raw_text:
        with st.expander("👀 View Extracted Document Text Preview", expanded=False):
            st.text_area(
                "Extracted Text",
                value=raw_text[:4000] + ("\n\n... [truncated preview]" if len(raw_text) > 4000 else ""),
                height=250,
                disabled=True,
            )
