"""
UI package for Local RAG Resume Assistant (Streamlit).
"""

from .styles import CUSTOM_CSS
from .components import render_header, render_sidebar, render_stats_metrics
from .views import render_upload_view, render_chat_view, render_critique_view

__all__ = [
    "CUSTOM_CSS",
    "render_header",
    "render_sidebar",
    "render_stats_metrics",
    "render_upload_view",
    "render_chat_view",
    "render_critique_view",
]

