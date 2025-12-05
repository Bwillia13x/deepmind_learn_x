"""Pydantic schemas for API requests and responses.

This module exports all schemas used for request validation and response serialization.
"""

from app.schemas.common import (
    # General
    Message,
    HealthResponse,
    # Captions
    SimplifyRequest,
    SimplifyResponse,
    FocusCommand,
    GlossRequest,
    GlossResponse,
    GlossEntry,
    # Reading
    ReadingScoreRequest,
    ReadingScoreResponse,
    ReadingError,
    TimedWord,
    AudioScoreResponse,
    DecodableRequest,
    DecodableResponse,
    # Authoring
    LevelTextRequest,
    LevelTextResponse,
    LeveledText,
    Question,
    ReadabilityScore,
)

from app.schemas.auth import (
    CreateSessionRequest,
    CreateSessionResponse,
    JoinSessionRequest,
    JoinSessionResponse,
    SessionInfoResponse,
)

__all__ = [
    # General
    "Message",
    "HealthResponse",
    # Captions
    "SimplifyRequest",
    "SimplifyResponse",
    "FocusCommand",
    "GlossRequest",
    "GlossResponse",
    "GlossEntry",
    # Reading
    "ReadingScoreRequest",
    "ReadingScoreResponse",
    "ReadingError",
    "TimedWord",
    "AudioScoreResponse",
    "DecodableRequest",
    "DecodableResponse",
    # Authoring
    "LevelTextRequest",
    "LevelTextResponse",
    "LeveledText",
    "Question",
    "ReadabilityScore",
    # Auth
    "CreateSessionRequest",
    "CreateSessionResponse",
    "JoinSessionRequest",
    "JoinSessionResponse",
    "SessionInfoResponse",
]
