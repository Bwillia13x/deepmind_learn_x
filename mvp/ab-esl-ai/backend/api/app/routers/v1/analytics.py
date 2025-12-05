"""Analytics API endpoints - class insights and student progress tracking."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.logging import log_metric
from app.services.db import get_db
from app.services import analytics

router = APIRouter()


@router.get("/class/{session_id}/summary")
def get_class_summary(session_id: int, db: Session = Depends(get_db)):
    """
    Get summary statistics for a class session.
    
    Returns:
    - total_assessments: Number of reading assessments
    - avg_wpm: Average words per minute
    - avg_wcpm: Average words correct per minute
    - avg_accuracy: Average accuracy percentage
    - participants_count: Number of unique students
    """
    summary = analytics.get_class_summary(db, session_id)
    log_metric("analytics_class_summary", session_id=session_id)
    return summary


@router.get("/student/{participant_id}/progress")
def get_student_progress(participant_id: int, db: Session = Depends(get_db)):
    """
    Get progress metrics for a specific student.
    
    Returns:
    - total_readings: Total assessments completed
    - current_wpm: Most recent WPM score
    - wpm_trend: Array of {date, wpm, wcpm, accuracy}
    - growth_rate: Percentage improvement from first to last
    """
    progress = analytics.get_student_progress(db, participant_id)
    log_metric("analytics_student_progress", participant_id=participant_id)
    return progress


@router.get("/class/{session_id}/interventions")
def get_interventions(
    session_id: int,
    threshold_wpm: float = 60.0,
    db: Session = Depends(get_db)
):
    """
    Identify students who may need intervention.
    
    Args:
    - threshold_wpm: Minimum WPM to be considered on-track (default: 60)
    
    Returns list of students with:
    - participant_id, nickname, l1
    - wpm, accuracy
    - reasons: List of intervention triggers
    """
    interventions = analytics.get_interventions(db, session_id, threshold_wpm)
    log_metric(
        "analytics_interventions",
        session_id=session_id,
        count=len(interventions)
    )
    return {"session_id": session_id, "interventions": interventions}


@router.get("/class/{session_id}/trends")
def get_class_trends(
    session_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get class performance trends over time.
    
    Args:
    - days: Number of days to look back (default: 30)
    
    Returns:
    - trend: Array of {date, avg_wpm, avg_accuracy, count}
    """
    trends = analytics.get_class_trends(db, session_id, days)
    log_metric("analytics_class_trends", session_id=session_id, days=days)
    return trends
