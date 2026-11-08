"""
RAG pipeline implementation for conversational Q&A over the indexed resume.
"""

from typing import Generator, List, Dict, Any, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

try:
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains import create_retrieval_chain
except ImportError:
    create_stuff_documents_chain = None
    create_retrieval_chain = None


RAG_PROMPT_TEMPLATE = """You are a helpful and detailed resume assistant. Your goal is to answer questions based ONLY on the provided context (the user's resume). 
If you cannot find the answer in the context, politely state that the information is not in the resume. 
Do not use any external knowledge.

--- CONTEXT ---
{context}

--- QUESTION ---
{input}
"""


def format_docs(docs: List[Document]) -> str:
    """Format retrieved document chunks into a single readable context string."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(llm, retriever):
    """
    Constructs the RAG chain using LangChain.
    Supports create_retrieval_chain or LCEL pipeline.
    """
    if retriever is None or llm is None:
        return None

    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

    # Prefer standard langchain retrieval chains if available
    if create_stuff_documents_chain and create_retrieval_chain:
        try:
            document_chain = create_stuff_documents_chain(llm, prompt)
            return create_retrieval_chain(retriever, document_chain)
        except Exception:
            pass

    # LCEL pipeline fallback (modern LangChain 1.0+)
    try:
        from langchain_core.output_parsers import StrOutputParser

        def retrieve_and_format(query: str):
            docs = retriever.invoke(query)
            return format_docs(docs)

        chain = (
            {
                "context": (lambda x: retrieve_and_format(x["input"])),
                "input": (lambda x: x["input"]),
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        return chain
    except Exception as e:
        print(f"Error building LCEL RAG chain: {e}")
        return None


def stream_rag_answer(
    question: str,
    rag_chain,
    retriever=None,
) -> Generator[str, None, None]:
    """
    Stream the answer token by token for real-time display in Streamlit.
    Yields string text increments.
    """
    if rag_chain is None:
        yield "System is not ready or resume has not been indexed yet. Please index a resume first in the 'Upload & Index' tab."
        return

    try:
        response_stream = rag_chain.stream({"input": question})

        for chunk in response_stream:
            if isinstance(chunk, dict):
                if "answer" in chunk:
                    yield chunk["answer"]
            elif isinstance(chunk, str):
                yield chunk
            elif hasattr(chunk, "content"):
                yield chunk.content
    except Exception as e:
        err_msg = str(e)
        if "not found" in err_msg.lower() or "404" in err_msg:
            yield (
                f"⚠️ **Ollama Model Error:** The selected model was not found by your Ollama server.\n\n"
                f"**Details:** `{err_msg}`\n\n"
                f"👉 **Quick Fix:** In the left sidebar, check **Installed Models** to see what is loaded, "
                f"or pull the model via terminal: `ollama pull llama3.2:3b`."
            )
        else:
            yield f"⚠️ **Error during response generation:** {err_msg}"


def get_rag_answer(question: str, rag_chain) -> str:
    """Synchronous non-streaming answer retrieval."""
    tokens = list(stream_rag_answer(question, rag_chain))
    return "".join(tokens)
