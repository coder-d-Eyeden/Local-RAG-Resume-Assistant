"""
Document ingestion and chunking module for resumes.
Supports PDF, DOCX, TXT, and Markdown with fallback parsers for high reliability.
"""

import os
import tempfile
from typing import List, Tuple, Dict, Any, Union
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.settings import CHUNK_SIZE, CHUNK_OVERLAP


def extract_text_from_file(file_input: Union[str, Path, Any], filename: str = "") -> str:
    """
    Extract raw text from a file path or file-like object.
    Supports PDF, DOCX, and TXT using layered parsers.
    """
    # Determine filename and extension
    if isinstance(file_input, (str, Path)):
        file_path = str(file_input)
        ext = os.path.splitext(file_path)[1].lower()
        if not filename:
            filename = os.path.basename(file_path)
    else:
        # File-like object (e.g. Streamlit UploadedFile)
        filename = filename or getattr(file_input, "name", "document.txt")
        ext = os.path.splitext(filename)[1].lower()
        
        # Save to temporary file for libraries that require a disk path
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            if hasattr(file_input, "getvalue"):
                temp_file.write(file_input.getvalue())
            elif hasattr(file_input, "read"):
                temp_file.write(file_input.read())
            file_path = temp_file.name

    text = ""
    try:
        # 1. Try Unstructured if available
        try:
            from unstructured.partition.auto import partition
            elements = partition(filename=file_path)
            text = "\n\n".join([str(el) for el in elements if str(el).strip()])
            if text.strip():
                return text
        except Exception:
            # Fall back to format-specific parsers
            pass

        # 2. Format-specific fallbacks
        if ext == ".pdf":
            text = _extract_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            text = _extract_docx(file_path)
        elif ext in [".txt", ".md"]:
            text = _extract_text(file_path)
        else:
            # Generic text fallback
            text = _extract_text(file_path)

        if not text.strip():
            raise ValueError(f"No extractable text was found in '{filename}'.")

        return text

    finally:
        # Clean up temporary file if created
        if not isinstance(file_input, (str, Path)) and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass


def _extract_pdf(file_path: str) -> str:
    """Extract text from PDF using pypdf."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        pages_text = []
        for i, page in enumerate(reader.pages):
            extracted = page.extract_text()
            if extracted:
                pages_text.append(extracted)
        return "\n\n".join(pages_text)
    except Exception as e:
        raise RuntimeError(f"Failed to parse PDF with pypdf: {e}") from e


def _extract_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        import docx
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        # Also extract table text
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)
        return "\n\n".join(paragraphs)
    except Exception as e:
        raise RuntimeError(f"Failed to parse DOCX with python-docx: {e}") from e


def _extract_text(file_path: str) -> str:
    """Read plain text with encoding fallbacks."""
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Unable to decode text file '{file_path}' with common encodings.")


def process_and_chunk_document(
    file_input: Union[str, Path, Any],
    filename: str = "",
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> Tuple[List[Document], str, Dict[str, Any]]:
    """
    Extracts text from a document and splits it into LangChain chunks.
    
    Returns:
        (documents, raw_text, statistics)
    """
    if isinstance(file_input, (str, Path)):
        resolved_name = filename or os.path.basename(str(file_input))
    else:
        resolved_name = filename or getattr(file_input, "name", "Uploaded_Resume")

    raw_text = extract_text_from_file(file_input, filename=resolved_name)

    # Wrap as single root document
    root_doc = Document(
        page_content=raw_text,
        metadata={"source": resolved_name, "total_characters": len(raw_text)},
    )

    # Recursive character text splitting
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = splitter.split_documents([root_doc])

    # Add chunk index metadata
    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = idx
        chunk.metadata["total_chunks"] = len(chunks)

    stats = {
        "filename": resolved_name,
        "total_chars": len(raw_text),
        "num_chunks": len(chunks),
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
    }

    return chunks, raw_text, stats
