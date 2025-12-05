"""Analytics service for student progress and class insights."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.models.reading_result import ReadingResult
from app.models.session import ClassSession, Participant


def get_class_summary(db: Session, session_id: int) -> Dict[str, Any]:
    """Get summary statistics for a class session."""
    results = db.query(ReadingResult).filter(
        ReadingResult.session_id == session_id
    ).all()

    if not results:
        return {
            "session_id": session_id,
            "total_assessments": 0,
            "avg_wpm": 0,
            "avg_wcpm": 0,
            "avg_accuracy": 0,
            "participants_count": 0,
        }

    total = len(results)
    avg_wpm = sum(r.wpm for r in results) / total
    avg_wcpm = sum(r.wcpm for r in results if r.wcpm) / len([r for r in results if r.wcpm]) if any(r.wcpm for r in results) else 0
    avg_accuracy = sum(r.accuracy for r in results if r.accuracy) / len([r for r in results if r.accuracy]) if any(r.accuracy for r in results) else 0

    # Count unique participants
    participants = set(r.participant_id for r in results if r.participant_id)

    return {
        "session_id": session_id,
        "total_assessments": total,
        "avg_wpm": round(avg_wpm, 1),
        "avg_wcpm": round(avg_wcpm, 1),
        "avg_accuracy": round(avg_accuracy, 3),
        "participants_count": len(participants),
    }


def get_student_progress(db: Session, participant_id: int) -> Dict[str, Any]:
    """Get progress metrics for a specific student."""
    results = db.query(ReadingResult).filter(
        ReadingResult.participant_id == participant_id
    ).order_by(ReadingResult.created_at).all()

    if not results:
        return {
            "participant_id": participant_id,
            "total_readings": 0,
            "current_wpm": 0,
            "wpm_trend": [],
            "growth_rate": 0,
        }

    # Calculate growth rate (first to last)
    first_wpm = results[0].wpm
    last_wpm = results[-1].wpm
    growth_rate = ((last_wpm - first_wpm) / first_wpm * 100) if first_wpm > 0 else 0

    # Build trend data
    wpm_trend = [
        {
            "date": r.created_at.isoformat() if r.created_at else None,
            "wpm": r.wpm,
            "wcpm": r.wcpm,
            "accuracy": r.accuracy,
        }
        for r in results
    ]

    return {
        "participant_id": participant_id,
        "total_readings": len(results),
        "current_wpm": last_wpm,
        "first_wpm": first_wpm,
        "wpm_trend": wpm_trend,
        "growth_rate": round(growth_rate, 1),
    }


def get_interventions(db: Session, session_id: int, threshold_wpm: float = 60.0) -> List[Dict[str, Any]]:
    """Identify students who may need intervention based on performance."""
    # Get latest result for each participant in session
    subquery = (
        db.query(
            ReadingResult.participant_id,
            func.max(ReadingResult.created_at).label("max_date")
        )
        .filter(ReadingResult.session_id == session_id)
        .group_by(ReadingResult.participant_id)
        .subquery()
    )

    latest_results = (
        db.query(ReadingResult)
        .join(
            subquery,
            and_(
                ReadingResult.participant_id == subquery.c.participant_id,
                ReadingResult.created_at == subquery.c.max_date
            )
        )
        .all()
    )

    interventions = []
    for result in latest_results:
        needs_help = False
        reasons = []

        # Check WPM threshold
        if result.wpm < threshold_wpm:
            needs_help = True
            reasons.append(f"WPM below threshold ({result.wpm:.1f} < {threshold_wpm})")

        # Check accuracy
        if result.accuracy and result.accuracy < 0.85:
            needs_help = True
            reasons.append(f"Low accuracy ({result.accuracy * 100:.0f}%)")

        # Get participant info
        participant = db.query(Participant).filter(
            Participant.id == result.participant_id
        ).first()

        if needs_help:
            interventions.append({
                "participant_id": result.participant_id,
                "nickname": participant.nickname if participant else f"Student {result.participant_id}",
                "l1": participant.l1 if participant else "unknown",
                "wpm": result.wpm,
                "accuracy": result.accuracy,
                "reasons": reasons,
                "last_assessed": result.created_at.isoformat() if result.created_at else None,
            })

    return interventions


def get_class_trends(db: Session, session_id: int, days: int = 30) -> Dict[str, Any]:
    """Get class performance trends over time."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    results = (
        db.query(ReadingResult)
        .filter(
            ReadingResult.session_id == session_id,
            ReadingResult.created_at >= cutoff_date
        )
        .order_by(ReadingResult.created_at)
        .all()
    )

    if not results:
        return {
            "session_id": session_id,
            "days": days,
            "data_points": 0,
            "trend": [],
        }

    # Group by date
    by_date: Dict[str, List[ReadingResult]] = {}
    for r in results:
        if r.created_at:
            date_key = r.created_at.date().isoformat()
            if date_key not in by_date:
                by_date[date_key] = []
            by_date[date_key].append(r)

    # Calculate daily averages
    trend = []
    for date_key in sorted(by_date.keys()):
        day_results = by_date[date_key]
        avg_wpm = sum(r.wpm for r in day_results) / len(day_results)
        avg_accuracy = (
            sum(r.accuracy for r in day_results if r.accuracy) /
            len([r for r in day_results if r.accuracy])
            if any(r.accuracy for r in day_results)
            else 0
        )

        trend.append({
            "date": date_key,
            "avg_wpm": round(avg_wpm, 1),
            "avg_accuracy": round(avg_accuracy, 3),
            "count": len(day_results),
        })

    return {
        "session_id": session_id,
        "days": days,
        "data_points": len(trend),
        "trend": trend,
    }
