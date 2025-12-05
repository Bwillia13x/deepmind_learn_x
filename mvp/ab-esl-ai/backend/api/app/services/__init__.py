"""Service clients and business logic.

This module exports the primary service functions used throughout the application.
Services are organized by domain:

- simplify: Text simplification and focus command extraction
- translate: Translation and glossary generation
- decodable: Phonics-constrained text generation
- orf: Oral reading fluency scoring
- auth: Authentication and session management
- analytics: Student progress and class insights
- curriculum: Alberta curriculum alignment
- l1_transfer: L1 linguistic transfer analysis
- family_literacy: Family engagement tools
- slife: SLIFE student support
- predictive_intervention: Risk prediction and intervention planning
- cultural_responsiveness: Cultural context awareness
"""

# Database utilities
from app.services.db import get_db, get_db_session, init_db

# Cache utilities
from app.services.cache import cache_get, cache_set, cache_delete

# Storage utilities
from app.services.storage import upload_file, upload_bytes, download_file, get_presigned_url

# Core services
from app.services.simplify import simplify_text, extract_focus_commands
from app.services.translate import get_gloss, load_dictionary
from app.services.decodable import generate_decodable
from app.services.orf import score_audio_file, score_simple

# Auth services
from app.services.auth import generate_class_code, generate_token, verify_token

# Reading results
from app.services.reading_results import (
    save_reading_result,
    get_session_results,
    get_participant_results,
    get_result_by_id,
)

__all__ = [
    # Database
    "get_db",
    "get_db_session",
    "init_db",
    # Cache
    "cache_get",
    "cache_set",
    "cache_delete",
    # Storage
    "upload_file",
    "upload_bytes",
    "download_file",
    "get_presigned_url",
    # Core services
    "simplify_text",
    "extract_focus_commands",
    "get_gloss",
    "load_dictionary",
    "generate_decodable",
    "score_audio_file",
    "score_simple",
    # Auth
    "generate_class_code",
    "generate_token",
    "verify_token",
    # Reading results
    "save_reading_result",
    "get_session_results",
    "get_participant_results",
    "get_result_by_id",
]
