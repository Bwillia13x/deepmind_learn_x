"""Authentication schemas."""

from typing import Optional
from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    """Request to create a new class session."""
    teacher_name: str
    grade_level: str = "K-6"
    settings: dict = {}


class CreateSessionResponse(BaseModel):
    """Response from creating a session."""
    class_code: str
    session_id: int
    token: str


class JoinSessionRequest(BaseModel):
    """Request to join an existing session."""
    class_code: str
    nickname: str
    l1: str = "en"
    device_id: Optional[str] = None


class JoinSessionResponse(BaseModel):
    """Response from joining a session."""
    token: str
    session_id: int
    participant_id: int
    settings: dict


class SessionInfoResponse(BaseModel):
    """Session information response."""
    session_id: int
    teacher_name: str
    grade_level: str
    is_active: bool
    participant_count: int
