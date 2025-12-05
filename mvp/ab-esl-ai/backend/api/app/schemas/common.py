"""Common schemas used across the API."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Message(BaseModel):
    """Simple message response."""

    message: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    features: Dict[str, bool]


# Captions schemas
class SimplifyRequest(BaseModel):
    """Request to simplify text."""

    text: str
    strength: int = 1  # 0-3
    focus_commands: bool = True


class FocusCommand(BaseModel):
    """A focus command extracted from text."""

    verb: str
    object: Optional[str] = None


class SimplifyResponse(BaseModel):
    """Response from simplify endpoint."""

    simplified: str
    focus: List[FocusCommand]
    explanations: List[str]


class GlossRequest(BaseModel):
    """Request for glossary/translation."""

    text: str
    l1: str
    top_k: int = 8


class GlossEntry(BaseModel):
    """A glossary entry."""

    en: str
    l1: str
    definition: Optional[str] = None


class GlossResponse(BaseModel):
    """Response from gloss endpoint."""

    translation: str
    gloss: List[GlossEntry]


# Reading schemas
class ReadingScoreRequest(BaseModel):
    """Request to score reading (simple)."""

    words_read: int
    seconds: int
    errors: int = 0


class ReadingScoreResponse(BaseModel):
    """Response from reading score endpoint."""

    wpm: float
    wcpm: Optional[float] = None
    accuracy: Optional[float] = None


class ReadingError(BaseModel):
    """A reading error."""

    type: str  # 'sub', 'del', 'ins'
    ref: Optional[str] = None
    hyp: Optional[str] = None
    t: Optional[float] = None


class TimedWord(BaseModel):
    """A word with timing."""

    word: str
    start: float
    end: float


class AudioScoreResponse(BaseModel):
    """Response from audio scoring endpoint."""

    wpm: float
    wcpm: Optional[float] = None
    accuracy: Optional[float] = None
    errors: List[ReadingError]
    words_timed: List[TimedWord]


class DecodableRequest(BaseModel):
    """Request to generate decodable text."""

    graphemes: List[str]
    length_sentences: int = 6
    word_bank: Optional[List[str]] = None


class DecodableResponse(BaseModel):
    """Response from decodable generation."""

    text: str


# Authoring schemas
class LevelTextRequest(BaseModel):
    """Request to level text."""

    text: str
    targets: List[str]  # e.g., ['A2', 'B1', 'Gr5']
    l1: Optional[str] = None


class Question(BaseModel):
    """A comprehension question."""

    type: str
    q: str
    a: str


class ReadabilityScore(BaseModel):
    """Readability analysis."""

    cefr: str
    avg_sentence_length: float
    difficult_word_pct: float


class LeveledText(BaseModel):
    """A leveled version of text."""

    target: str
    text: str
    questions: List[Question]
    gloss: List[GlossEntry]


class LevelTextResponse(BaseModel):
    """Response from level-text endpoint."""

    original_score: ReadabilityScore
    levels: List[LeveledText]
