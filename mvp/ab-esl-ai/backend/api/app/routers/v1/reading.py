"""Reading Buddy API endpoints - ORF scoring, decodable generation."""

import csv
import io
import json
import tempfile
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.logging import log_metric, logger
from app.schemas.common import (
    AudioScoreResponse,
    DecodableRequest,
    DecodableResponse,
    ReadingError,
    ReadingScoreRequest,
    ReadingScoreResponse,
    TimedWord,
)
from app.services.db import get_db
from app.services.decodable import generate_decodable
from app.services.orf import score_audio_file, score_simple
from app.services import reading_results

router = APIRouter()

# Load passages from content directory
_passages_cache: list = []


def load_passages() -> list:
    """Load sample passages from JSON file."""
    global _passages_cache
    if _passages_cache:
        return _passages_cache
    
    # From app/routers/v1/reading.py, need to go up 6 levels to reach ab-esl-ai/
    # reading.py -> v1 -> routers -> app -> api -> backend -> ab-esl-ai
    base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
    
    # Try multiple paths (from most specific to least)
    paths = [
        # Primary: from project root
        base_dir / "content" / "passages" / "sample_passages.json",
        # Fallback: relative from current working directory
        Path("content/passages/sample_passages.json"),
        # Another fallback: from backend directory
        Path(__file__).resolve().parent.parent.parent.parent / "content" / "passages" / "sample_passages.json",
    ]
    
    for path in paths:
        resolved = path.resolve() if hasattr(path, 'resolve') else path
        logger.debug(f"Trying path: {resolved}")
        if resolved.exists():
            try:
                with open(resolved) as f:
                    data = json.load(f)
                    _passages_cache = data.get("passages", [])
                    logger.info(f"Loaded {len(_passages_cache)} passages from {resolved}")
                    return _passages_cache
            except Exception as e:
                logger.warning(f"Failed to load passages from {resolved}: {e}")
    
    logger.warning("Could not find passages file, using defaults")
    
    # Return default passages if file not found
    _passages_cache = [
        {
            "id": "sample1",
            "title": "The Cat",
            "grade": "K-2",
            "cefr": "A1",
            "text": "The cat sat on the mat. The cat is fat. The cat can nap.",
            "word_count": 15,
            "key_vocabulary": ["cat", "sat", "mat", "fat", "nap"]
        },
        {
            "id": "sample2",
            "title": "The Dog",
            "grade": "K-2",
            "cefr": "A1",
            "text": "A dog can run. The dog is fun. The dog can jump and play.",
            "word_count": 14,
            "key_vocabulary": ["dog", "run", "fun", "jump", "play"]
        },
    ]
    return _passages_cache


@router.get("/passages")
def get_passages(grade: Optional[str] = None, cefr: Optional[str] = None):
    """
    Get available reading passages.
    
    Optionally filter by grade level or CEFR level.
    """
    passages = load_passages()
    
    if grade:
        passages = [p for p in passages if p.get("grade", "").lower() == grade.lower()]
    if cefr:
        passages = [p for p in passages if p.get("cefr", "").upper() == cefr.upper()]
    
    return {
        "count": len(passages),
        "passages": passages
    }


@router.post("/score", response_model=ReadingScoreResponse)
def score_reading(request: ReadingScoreRequest) -> ReadingScoreResponse:
    """
    Calculate reading fluency metrics from word counts.

    Simple calculation without audio.
    """
    result = score_simple(
        words_read=request.words_read,
        seconds=request.seconds,
        errors=request.errors,
    )

    return ReadingScoreResponse(
        wpm=result["wpm"],
        wcpm=result["wcpm"],
        accuracy=result["accuracy"],
    )


@router.post("/score_audio", response_model=AudioScoreResponse)
async def score_audio_endpoint(
    audio_file: UploadFile = File(...),
    reference_text: Optional[str] = Form(None),
    passage_id: Optional[str] = Form(None),
):
    """
    Score reading fluency from uploaded audio.

    Accepts WAV or MP3 audio files.
    If reference_text is provided, calculates accuracy and error types.
    """
    start_time = time.time()

    # Save uploaded file temporarily
    suffix = Path(audio_file.filename or "audio.wav").suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await audio_file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Score the audio
        result = score_audio_file(
            audio_path=tmp_path,
            reference_text=reference_text,
        )

        latency = time.time() - start_time
        log_metric(
            "score_audio_endpoint",
            latency=latency,
            wpm=result.wpm,
            has_reference=reference_text is not None,
        )

        return AudioScoreResponse(
            wpm=result.wpm,
            wcpm=result.wcpm,
            accuracy=result.accuracy,
            errors=[
                ReadingError(
                    type=e.type,
                    ref=e.ref,
                    hyp=e.hyp,
                    t=e.time,
                )
                for e in result.errors
            ],
            words_timed=[
                TimedWord(word=w.word, start=w.start, end=w.end)
                for w in result.words_timed
            ],
        )
    finally:
        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)


@router.post("/generate_decodable", response_model=DecodableResponse)
def generate_decodable_endpoint(request: DecodableRequest) -> DecodableResponse:
    """
    Generate phonics-constrained decodable text.

    Text will only use words that can be decoded with the specified graphemes.
    """
    start_time = time.time()

    result = generate_decodable(
        graphemes=request.graphemes,
        length_sentences=request.length_sentences,
        word_bank=request.word_bank,
    )

    latency = time.time() - start_time
    log_metric(
        "generate_decodable_endpoint",
        latency=latency,
        graphemes=request.graphemes,
        sentences=result.sentence_count,
    )

    return DecodableResponse(text=result.text)


# Reading Results Endpoints

@router.post("/results")
def save_reading_result_endpoint(
    session_id: int,
    wpm: float,
    participant_id: Optional[int] = None,
    passage_id: Optional[str] = None,
    wcpm: Optional[float] = None,
    accuracy: Optional[float] = None,
    errors: list = [],
    audio_url: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Save a reading assessment result.
    
    Used by the frontend and seed scripts to persist reading scores.
    """
    result = reading_results.save_reading_result(
        db=db,
        session_id=session_id,
        participant_id=participant_id,
        passage_id=passage_id,
        wpm=wpm,
        wcpm=wcpm,
        accuracy=accuracy,
        errors=errors,
        audio_url=audio_url,
    )
    return {
        "id": result.id,
        "session_id": result.session_id,
        "participant_id": result.participant_id,
        "wpm": result.wpm,
        "wcpm": result.wcpm,
        "accuracy": result.accuracy,
        "created_at": result.created_at.isoformat() if result.created_at else None,
    }


@router.get("/session/{session_id}/results")
def get_session_reading_results(session_id: int, db: Session = Depends(get_db)):
    """Get all reading results for a session (UI-friendly endpoint)."""
    results = reading_results.get_session_results(db, session_id)
    return {
        "session_id": session_id,
        "count": len(results),
        "results": [
            {
                "id": r.id,
                "participant_id": r.participant_id,
                "passage_id": r.passage_id,
                "wpm": r.wpm,
                "wcpm": r.wcpm,
                "accuracy": r.accuracy,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in results
        ],
    }


@router.get("/results/{session_id}")
def get_reading_results(session_id: int, db: Session = Depends(get_db)):
    """Get all reading results for a session."""
    results = reading_results.get_session_results(db, session_id)
    return {
        "session_id": session_id,
        "count": len(results),
        "results": [
            {
                "id": r.id,
                "participant_id": r.participant_id,
                "passage_id": r.passage_id,
                "wpm": r.wpm,
                "wcpm": r.wcpm,
                "accuracy": r.accuracy,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in results
        ],
    }


@router.get("/results/{session_id}/export")
def export_reading_results(session_id: int, db: Session = Depends(get_db)):
    """Export reading results as CSV."""
    results = reading_results.get_session_results(db, session_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Participant", "Passage", "WPM", "WCPM", "Accuracy", "Date"])

    for r in results:
        writer.writerow([
            r.id,
            r.participant_id or "",
            r.passage_id or "",
            r.wpm,
            r.wcpm or "",
            r.accuracy or "",
            r.created_at.isoformat() if r.created_at else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=reading-results-{session_id}.csv"
        },
    )


@router.get("/participant/{participant_id}/results")
def get_participant_reading_results(participant_id: int, db: Session = Depends(get_db)):
    """Get all reading results for a specific participant."""
    results = reading_results.get_participant_results(db, participant_id)
    return {
        "participant_id": participant_id,
        "count": len(results),
        "results": [
            {
                "id": r.id,
                "session_id": r.session_id,
                "passage_id": r.passage_id,
                "wpm": r.wpm,
                "wcpm": r.wcpm,
                "accuracy": r.accuracy,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in results
        ],
    }
