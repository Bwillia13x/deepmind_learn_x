"""Authentication router for class sessions."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.db import get_db
from app.services.auth import generate_class_code, generate_token
from app.models.session import ClassSession, Participant
from app.schemas.auth import (
    CreateSessionRequest,
    CreateSessionResponse,
    JoinSessionRequest,
    JoinSessionResponse,
    SessionInfoResponse,
)

router = APIRouter()


@router.post("/create-session", response_model=CreateSessionResponse)
def create_session(request: CreateSessionRequest, db: Session = Depends(get_db)):
    """Create a new class session (teacher)."""
    class_code = generate_class_code()
    
    # Ensure unique code
    while db.query(ClassSession).filter(ClassSession.class_code == class_code).first():
        class_code = generate_class_code()
    
    session = ClassSession(
        class_code=class_code,
        teacher_name=request.teacher_name,
        grade_level=request.grade_level,
        settings=request.settings,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Generate teacher token
    token = generate_token(session.id, participant_id=None, is_teacher=True)
    
    return CreateSessionResponse(class_code=class_code, session_id=session.id, token=token)


@router.post("/join", response_model=JoinSessionResponse)
def join_session(request: JoinSessionRequest, db: Session = Depends(get_db)):
    """Join an existing session (student)."""
    session = db.query(ClassSession).filter(
        ClassSession.class_code == request.class_code.upper(),
        ClassSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or inactive")
    
    participant = Participant(
        session_id=session.id,
        nickname=request.nickname,
        l1=request.l1,
        device_id=request.device_id or "",
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    
    token = generate_token(session.id, participant.id, is_teacher=False)
    
    return JoinSessionResponse(
        token=token,
        session_id=session.id,
        participant_id=participant.id,
        settings=session.settings or {},
    )


@router.get("/session/{class_code}", response_model=SessionInfoResponse)
def get_session_info(class_code: str, db: Session = Depends(get_db)):
    """Get session info by class code."""
    session = db.query(ClassSession).filter(
        ClassSession.class_code == class_code.upper()
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    participant_count = db.query(Participant).filter(
        Participant.session_id == session.id
    ).count()
    
    return SessionInfoResponse(
        session_id=session.id,
        teacher_name=session.teacher_name,
        grade_level=session.grade_level,
        is_active=session.is_active,
        participant_count=participant_count,
    )


@router.post("/session/{session_id}/close")
def close_session(session_id: int, db: Session = Depends(get_db)):
    """Close a session (teacher)."""
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.is_active = False
    db.commit()
    
    return {"message": "Session closed", "session_id": session_id}


@router.get("/session/{session_id}/participants")
def get_participants(session_id: int, db: Session = Depends(get_db)):
    """Get all participants in a session."""
    participants = db.query(Participant).filter(
        Participant.session_id == session_id
    ).all()
    
    return {
        "session_id": session_id,
        "count": len(participants),
        "participants": [
            {
                "id": p.id,
                "nickname": p.nickname,
                "l1": p.l1,
                "joined_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in participants
        ],
    }
