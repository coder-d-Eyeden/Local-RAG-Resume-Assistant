"""
Critique View: Structured resume analysis, market confidence assessment, and exportable report.
"""

import streamlit as st

from core.llm import get_llm, resolve_model_name
from core.critique import generate_critique


def render_critique_view(config: dict):
    """Render the Structured Critique and Suggestions tab."""
    st.markdown("### ✨ Step 3: Structured Resume Critique & Career Assessment")
    st.markdown(
        "Request an in-depth, executive-level evaluation of the candidate's resume. "
        "The model analyzes strengths, highlights key accomplishments, identifies improvement opportunities, "
        "and suggests optimal career trajectories."
    )

    vector_store = st.session_state.get("vector_store")
    if vector_store is None:
        st.warning(
            "⚠️ **No resume currently loaded.** Please go to the **Upload & Index Resume** tab "
            "and process a resume before requesting a critique.",
            icon="⚠️",
        )
        return

    server_models = config.get("server_models", [])
    resolved_model = resolve_model_name(config["llm_model"], server_models)

    st.caption(f"🧠 Analysis will run using model: **`{resolved_model}`**")

    col1, col2 = st.columns([1, 3])
    with col1:
        generate_btn = st.button(
            "✨ Generate Critique",
            type="primary",
            use_container_width=True,
            help="Perform structured LLM evaluation of the complete resume",
        )

    # Perform Generation
    if generate_btn:
        with st.spinner(f"Analyzing resume content with `{resolved_model}`..."):
            try:
                llm = get_llm(
                    model_name=resolved_model,
                    base_url=config["base_url"],
                    available_models=server_models,
                )
                critique_data, markdown_output = generate_critique(llm, vector_store)
                st.session_state["critique_data"] = critique_data
                st.session_state["critique_markdown"] = markdown_output
                st.toast("Critique generated successfully!", icon="🎉")
            except Exception as e:
                err_msg = str(e)
                if "not found" in err_msg.lower() or "404" in err_msg:
                    st.error(
                        f"⚠️ **Model Not Found in Ollama**: `{resolved_model}`\n\n"
                        f"**Details:** {err_msg}\n\n"
                        f"👉 **Quick Fix:** In the left sidebar, check **Installed Models** to see what is loaded, "
                        f"or run `ollama pull {resolved_model}` in your terminal."
                    )
                else:
                    st.error(f"Failed to generate critique: {e}")
                return

    # Render Display if critique exists in session
    critique_data = st.session_state.get("critique_data")
    critique_markdown = st.session_state.get("critique_markdown")

    if critique_data and critique_markdown:
        st.divider()

        # Score & Metric Cards
        overall = critique_data.get("overall_assessment", "Evaluated")
        confidence = critique_data.get("confidence_level", "High")

        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric("📊 Overall Assessment", overall)
        with m_col2:
            st.metric("🎯 Market Confidence Level", confidence)

        st.markdown("<br>", unsafe_allow_html=True)

        # Full Formatted Output in a styled card
        st.markdown(
            f"""
            <div class="critique-card">
                {critique_markdown}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Download / Export Option
        st.download_button(
            label="📥 Download Critique Report (.md)",
            data=critique_markdown,
            file_name=f"resume_critique_{st.session_state.get('indexed_doc_name', 'candidate')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    elif not generate_btn:
        st.info("Click **Generate Critique** above to start the comprehensive analysis.")
