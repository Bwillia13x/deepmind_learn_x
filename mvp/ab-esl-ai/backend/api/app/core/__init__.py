"""Core configuration and utilities.

This module exports core functionality for the application including:
- Configuration settings
- Logging utilities
- NLP utilities
- Rate limiting
- Security utilities
"""

from app.core.config import settings
from app.core.logging import logger, log_metric
from app.core.nlp import get_nlp, get_doc, extract_sentences, get_lemma

__all__ = [
    "settings",
    "logger",
    "log_metric",
    "get_nlp",
    "get_doc",
    "extract_sentences",
    "get_lemma",
]
