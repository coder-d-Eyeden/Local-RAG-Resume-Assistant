"""
Q&A Chat View: Interactive conversational interface with streaming answers and suggested prompts.
"""

import streamlit as st

from core.rag_chain import stream_rag_answer, build_rag_chain
from core.llm import get_llm, resolve_model_name
from core.vector_store import get_retriever


SUGGESTED_QUESTIONS = [
    "What are the candidate's core technical skills?",
    "Summarize the most recent work experience and key achievements.",
    "What degrees, education, or certifications are listed?",
    "Does this candidate have leadership or team management experience?",
]


def render_chat_view(config: dict):
    """Render the Interactive Q&A Chat tab."""
    st.markdown("### 💬 Step 2: Interactive Resume Q&A")
    st.markdown(
        "Ask any question about the candidate's skills, qualifications, or past experience. "
        "The assistant retrieves the most relevant resume sections and formulates an answer "
        "strictly based on the document context."
    )

    vector_store = st.session_state.get("vector_store")
    rag_chain = st.session_state.get("rag_chain")
    active_llm = st.session_state.get("active_llm_model")

    # Rebuild chain if missing or if model changed in sidebar
    if (rag_chain is None or active_llm != config["llm_model"]) and vector_store is not None:
        try:
            server_models = config.get("server_models", [])
            resolved_llm = resolve_model_name(config["llm_model"], server_models)
            retriever = get_retriever(vector_store)
            llm = get_llm(
                model_name=resolved_llm,
                base_url=config["base_url"],
                available_models=server_models,
            )
            rag_chain = build_rag_chain(llm, retriever)
            st.session_state["rag_chain"] = rag_chain
            st.session_state["retriever"] = retriever
            st.session_state["active_llm_model"] = resolved_llm
            st.session_state["active_ollama_url"] = config["base_url"]
        except Exception as e:
            st.warning(f"Could not connect to model '{config['llm_model']}': {e}")
            rag_chain = None

    if vector_store is None:
        st.warning(
            "⚠️ **No resume currently loaded.** Please go to the **Upload & Index Resume** tab "
            "and process a resume first before chatting.",
            icon="⚠️",
        )
        return

    # Show active model badge
    active_model_name = st.session_state.get("active_llm_model", config["llm_model"])
    st.caption(f"🧠 Using model: **`{active_model_name}`**")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Quick Question Chips
    st.markdown("##### 💡 Suggested Questions")
    cols = st.columns(len(SUGGESTED_QUESTIONS))
    selected_prompt = None
    for i, question in enumerate(SUGGESTED_QUESTIONS):
        with cols[i]:
            if st.button(question, key=f"quick_q_{i}", use_container_width=True):
                selected_prompt = question

    st.divider()

    # Render previous conversation history
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle Input from either quick button or chat input box
    user_input = st.chat_input("Ask a question about the loaded resume...")
    prompt_to_run = user_input or selected_prompt

    if prompt_to_run:
        # Display user message
        st.session_state["messages"].append({"role": "user", "content": prompt_to_run})
        with st.chat_message("user"):
            st.markdown(prompt_to_run)

        # Generate and stream assistant message
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            try:
                for chunk in stream_rag_answer(prompt_to_run, rag_chain):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"⚠️ Error generating response: {e}"
                response_placeholder.markdown(full_response)

        # Save assistant message to history
        st.session_state["messages"].append({"role": "assistant", "content": full_response})
