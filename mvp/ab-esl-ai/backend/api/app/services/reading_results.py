"""Reading results service for persistence and retrieval."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.reading_result import ReadingResult


def save_reading_result(
    db: Session,
    session_id: int,
    participant_id: Optional[int],
    passage_id: Optional[str],
    wpm: float,
    wcpm: Optional[float],
    accuracy: Optional[float],
    errors: list,
    audio_url: Optional[str] = None,
) -> ReadingResult:
    """Save a reading assessment result."""
    result = ReadingResult(
        session_id=session_id,
        participant_id=participant_id,
        passage_id=passage_id,
        wpm=wpm,
        wcpm=wcpm,
        accuracy=accuracy,
        errors=errors,
        audio_url=audio_url,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_session_results(db: Session, session_id: int) -> List[ReadingResult]:
    """Get all reading results for a session."""
    return (
        db.query(ReadingResult)
        .filter(ReadingResult.session_id == session_id)
        .order_by(ReadingResult.created_at.desc())
        .all()
    )


def get_participant_results(db: Session, participant_id: int) -> List[ReadingResult]:
    """Get all reading results for a participant."""
    return (
        db.query(ReadingResult)
        .filter(ReadingResult.participant_id == participant_id)
        .order_by(ReadingResult.created_at.desc())
        .all()
    )


def get_result_by_id(db: Session, result_id: int) -> Optional[ReadingResult]:
    """Get a specific reading result by ID."""
    return db.query(ReadingResult).filter(ReadingResult.id == result_id).first()
