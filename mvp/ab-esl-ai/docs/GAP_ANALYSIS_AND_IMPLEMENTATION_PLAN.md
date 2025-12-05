# Alberta ESL AI - GAP Analysis & Implementation Plan for Demo MVP

## Executive Summary

This document provides a comprehensive GAP analysis comparing the current implementation state against requirements for a fully functional demo MVP suitable for educator feedback. It includes a detailed implementation plan designed for execution by an agentic programmer (Opus 4.5).

---

## Part 1: GAP Analysis

### 1.1 Current State Assessment

#### Backend API (FastAPI) - ~65% Complete

| Component | Status | Notes |
|-----------|--------|-------|
| Project Structure | ✅ Complete | Well-organized monorepo with proper separation |
| Core Config | ✅ Complete | Feature flags, env loading, settings |
| Health Endpoint | ✅ Complete | Returns status and feature flags |
| Logging | ✅ Complete | Loguru with metrics logging |
| CORS/Middleware | ✅ Complete | Configured for dev |
| Schemas (Pydantic) | ✅ Complete | All request/response models defined |
| ASR Client | ⚠️ Partial | Streaming session exists, needs testing/hardening |
| Simplify Service | ✅ Complete | Rule-based with spaCy, word replacements |
| Translate Service | ⚠️ Partial | Dictionary-based only, 6 languages, limited vocab |
| Leveling Service | ⚠️ Partial | Basic heuristics, no LLM integration |
| Decodable Service | ✅ Complete | Phonics-constrained generation working |
| ORF Service | ✅ Complete | WPM/WCPM calculation, Levenshtein alignment |
| Captions Router | ⚠️ Partial | WebSocket stub, REST endpoints complete |
| Reading Router | ✅ Complete | Score, score_audio, generate_decodable |
| Authoring Router | ✅ Complete | Level-text endpoint functional |
| Database Layer | ❌ Missing | No persistence for sessions/transcripts |
| Authentication | ❌ Missing | No auth system |
| Tests | ⚠️ Partial | Basic tests exist, need expansion |


#### Teacher Portal (Next.js) - ~40% Complete

| Component | Status | Notes |
|-----------|--------|-------|
| Project Setup | ✅ Complete | Next.js 14, Tailwind, TypeScript |
| Layout/Navigation | ✅ Complete | Basic nav with links |
| Home Page | ✅ Complete | Feature cards, quick start guide |
| Text Leveler Page | ✅ Complete | Full UI with level selection, L1, results |
| Decodable Generator | ✅ Complete | Scope/sequence UI, generation, copy |
| Live Captions Page | ❌ Missing | Listed in nav but not implemented |
| Glossary Page | ❌ Missing | Listed in nav but not implemented |
| API Client Layer | ❌ Missing | Direct fetch calls, no abstraction |
| Error Handling | ⚠️ Partial | Basic error display |
| Loading States | ✅ Complete | Spinner components |
| Export/Download | ⚠️ Partial | JSON download only |
| Print-friendly Views | ❌ Missing | No print styles |
| Dashboard/Analytics | ❌ Missing | No class/student views |
| Settings/Preferences | ❌ Missing | No user preferences |

#### Student App (Flutter) - ❌ Not Started

| Component | Status | Notes |
|-----------|--------|-------|
| Project Structure | ❌ Missing | Only README placeholder |
| Captions Feature | ❌ Missing | Core feature not built |
| Reading Buddy | ❌ Missing | Core feature not built |
| Audio Recording | ❌ Missing | No mic integration |
| WebSocket Client | ❌ Missing | No real-time connection |
| Offline Support | ❌ Missing | No caching/PWA |

#### Infrastructure - ~70% Complete

| Component | Status | Notes |
|-----------|--------|-------|
| Docker Compose | ✅ Complete | Postgres, Redis, MinIO |
| Makefile | ✅ Complete | Dev commands |
| CI/CD | ⚠️ Partial | Basic GitHub Actions |
| Database Init | ✅ Complete | pgvector extension |
| Edge Box Stubs | ⚠️ Partial | Docker compose files only |

---

### 1.2 Critical Gaps for Demo MVP

#### Priority 1: BLOCKING for Demo

1. **Live Captions Page (Teacher Portal)** - Educators need to see real-time captioning
2. **WebSocket ASR Integration** - Backend WS handler needs hardening
3. **Database Persistence** - Need to save demo sessions/results
4. **Basic Authentication** - Class codes for demo sessions
5. **Sample Content** - Pre-loaded passages, glossaries for demo

#### Priority 2: HIGH VALUE for Demo

6. **Glossary/Translation Page** - Standalone translation tool
7. **Enhanced Dictionaries** - More vocabulary for top L1s
8. **Print/Export Views** - Teachers need printable worksheets
9. **Demo Mode** - Pre-configured demo scenarios
10. **Error Recovery** - Graceful handling of service failures

#### Priority 3: NICE TO HAVE for Demo

11. **Student App (Web PWA)** - Simpler than Flutter for demo
12. **Dashboard Mockups** - Show future analytics vision
13. **Onboarding Flow** - Guided first-use experience
14. **Sample Audio** - Pre-recorded readings for demo

---

### 1.3 Feature Completeness Matrix

```
Feature                    Backend  Frontend  Integration  Demo-Ready
─────────────────────────────────────────────────────────────────────
Text Leveling              ✅ 90%   ✅ 85%    ⚠️ 70%       ⚠️ 75%
Decodable Generation       ✅ 95%   ✅ 90%    ✅ 85%       ✅ 85%
Text Simplification        ✅ 85%   ❌ 0%     ❌ 0%        ❌ 0%
Live Captions (ASR)        ⚠️ 60%   ❌ 0%     ❌ 0%        ❌ 0%
Translation/Glossary       ⚠️ 50%   ❌ 0%     ❌ 0%        ❌ 0%
ORF Scoring                ✅ 90%   ❌ 0%     ❌ 0%        ❌ 0%
Reading Buddy UI           ❌ N/A   ❌ 0%     ❌ 0%        ❌ 0%
Authentication             ❌ 0%    ❌ 0%     ❌ 0%        ❌ 0%
Data Persistence           ❌ 0%    ❌ N/A    ❌ 0%        ❌ 0%
─────────────────────────────────────────────────────────────────────
Overall Demo Readiness: ~35%
```

---

## Part 2: Implementation Plan for Agentic Programmer

### 2.0 Execution Guidelines for Opus 4.5

```yaml
execution_mode: sequential_with_validation
validation_after_each_ticket: true
rollback_on_failure: true
test_coverage_minimum: 70%
commit_frequency: per_ticket
branch_strategy: feature_branches_to_main
```

**Agent Instructions:**
1. Execute tickets in order (dependencies are sequential)
2. Run tests after each ticket before proceeding
3. Commit with message format: `[TICKET-XX] Description`
4. If a ticket fails validation, debug before continuing
5. Log blockers and decisions in ticket comments

---


### Phase 1: Foundation & Critical Fixes (Tickets 1-5)

---

#### TICKET-01: Database Models and Persistence Layer

**Priority:** P0 - BLOCKING  
**Estimated Time:** 2-3 hours  
**Dependencies:** None

**Objective:** Implement SQLAlchemy models and database session management for storing demo data.

**Files to Create/Modify:**
```
backend/api/app/models/__init__.py (new)
backend/api/app/models/base.py (new)
backend/api/app/models/session.py (new)
backend/api/app/models/transcript.py (new)
backend/api/app/models/reading_result.py (new)
backend/api/app/services/db.py (modify)
backend/api/alembic.ini (new)
backend/api/alembic/env.py (new)
backend/api/alembic/versions/ (new directory)
```

**Implementation Details:**

```python
# backend/api/app/models/base.py
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

```python
# backend/api/app/models/session.py
from sqlalchemy import Column, String, Integer, Boolean, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class ClassSession(Base, TimestampMixin):
    __tablename__ = "class_sessions"
    
    id = Column(Integer, primary_key=True)
    class_code = Column(String(8), unique=True, index=True)
    teacher_name = Column(String(100))
    grade_level = Column(String(20))
    settings = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    
    transcripts = relationship("Transcript", back_populates="session")
    reading_results = relationship("ReadingResult", back_populates="session")

class Participant(Base, TimestampMixin):
    __tablename__ = "participants"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id"))
    nickname = Column(String(50))
    l1 = Column(String(10))
    device_id = Column(String(100))
```

```python
# backend/api/app/models/transcript.py
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, Text
from .base import Base, TimestampMixin

class Transcript(Base, TimestampMixin):
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id"))
    segment_id = Column(Integer)
    text = Column(Text)
    simplified_text = Column(Text, nullable=True)
    words = Column(JSON)  # [{w, s, e}, ...]
    ts_start = Column(Float)
    ts_end = Column(Float)
    
    session = relationship("ClassSession", back_populates="transcripts")
```

```python
# backend/api/app/models/reading_result.py
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey
from .base import Base, TimestampMixin

class ReadingResult(Base, TimestampMixin):
    __tablename__ = "reading_results"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id"))
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=True)
    passage_id = Column(String(50), nullable=True)
    wpm = Column(Float)
    wcpm = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    errors = Column(JSON)
    audio_url = Column(String(500), nullable=True)
    
    session = relationship("ClassSession", back_populates="reading_results")
```

```python
# backend/api/app/services/db.py (replace existing)
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.models.base import Base

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session():
    """Context manager for services."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

**Validation Steps:**
1. Run `make up` to ensure Postgres is running
2. Add to `main.py`: `from app.services.db import init_db; init_db()` in startup
3. Verify tables created: `docker exec -it ab_esl_db psql -U dev -d ab_esl_ai -c "\dt"`
4. Run existing tests: `pytest backend/api/tests/ -v`

**Definition of Done:**
- [ ] All model files created
- [ ] Database tables created on startup
- [ ] get_db dependency works in routes
- [ ] No test regressions

---

#### TICKET-02: Basic Authentication with Class Codes

**Priority:** P0 - BLOCKING  
**Estimated Time:** 2-3 hours  
**Dependencies:** TICKET-01

**Objective:** Implement simple class code authentication for demo sessions.

**Files to Create/Modify:**
```
backend/api/app/routers/auth.py (new)
backend/api/app/services/auth.py (new)
backend/api/app/routers/__init__.py (modify)
backend/api/app/schemas/auth.py (new)
backend/api/tests/test_auth.py (new)
```

**Implementation Details:**

```python
# backend/api/app/schemas/auth.py
from pydantic import BaseModel
from typing import Optional

class CreateSessionRequest(BaseModel):
    teacher_name: str
    grade_level: str = "K-6"
    settings: dict = {}

class CreateSessionResponse(BaseModel):
    class_code: str
    session_id: int

class JoinSessionRequest(BaseModel):
    class_code: str
    nickname: str
    l1: str = "en"
    device_id: Optional[str] = None

class JoinSessionResponse(BaseModel):
    token: str
    session_id: int
    participant_id: int
    settings: dict

class TokenPayload(BaseModel):
    session_id: int
    participant_id: Optional[int] = None
    is_teacher: bool = False
    exp: int
```

```python
# backend/api/app/services/auth.py
import secrets
import time
import hashlib
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.session import ClassSession, Participant
from app.core.config import settings

TOKEN_EXPIRY = 86400  # 24 hours for demo

def generate_class_code() -> str:
    """Generate a 6-character alphanumeric class code."""
    return secrets.token_hex(3).upper()

def generate_token(session_id: int, participant_id: Optional[int], is_teacher: bool) -> str:
    """Generate a simple demo token (not production-grade)."""
    exp = int(time.time()) + TOKEN_EXPIRY
    payload = f"{session_id}:{participant_id or 0}:{int(is_teacher)}:{exp}"
    signature = hashlib.sha256(f"{payload}:{settings.minio_secret_key}".encode()).hexdigest()[:16]
    return f"{payload}:{signature}"

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a demo token."""
    try:
        parts = token.split(":")
        if len(parts) != 5:
            return None
        session_id, participant_id, is_teacher, exp, signature = parts
        payload = f"{session_id}:{participant_id}:{is_teacher}:{exp}"
        expected_sig = hashlib.sha256(f"{payload}:{settings.minio_secret_key}".encode()).hexdigest()[:16]
        if signature != expected_sig:
            return None
        if int(exp) < time.time():
            return None
        return {
            "session_id": int(session_id),
            "participant_id": int(participant_id) if int(participant_id) > 0 else None,
            "is_teacher": bool(int(is_teacher)),
        }
    except Exception:
        return None

def create_session(db: Session, teacher_name: str, grade_level: str, settings_dict: dict) -> Tuple[str, int]:
    """Create a new class session."""
    class_code = generate_class_code()
    session = ClassSession(
        class_code=class_code,
        teacher_name=teacher_name,
        grade_level=grade_level,
        settings=settings_dict,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return class_code, session.id

def join_session(db: Session, class_code: str, nickname: str, l1: str, device_id: str) -> Optional[Tuple[int, int, dict]]:
    """Join an existing session."""
    session = db.query(ClassSession).filter(
        ClassSession.class_code == class_code.upper(),
        ClassSession.is_active == True
    ).first()
    if not session:
        return None
    
    participant = Participant(
        session_id=session.id,
        nickname=nickname,
        l1=l1,
        device_id=device_id or "",
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return session.id, participant.id, session.settings
```

```python
# backend/api/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.db import get_db
from app.services import auth as auth_service
from app.schemas.auth import (
    CreateSessionRequest, CreateSessionResponse,
    JoinSessionRequest, JoinSessionResponse
)

router = APIRouter()

@router.post("/create-session", response_model=CreateSessionResponse)
def create_session(request: CreateSessionRequest, db: Session = Depends(get_db)):
    """Create a new class session (teacher)."""
    class_code, session_id = auth_service.create_session(
        db, request.teacher_name, request.grade_level, request.settings
    )
    return CreateSessionResponse(class_code=class_code, session_id=session_id)

@router.post("/join", response_model=JoinSessionResponse)
def join_session(request: JoinSessionRequest, db: Session = Depends(get_db)):
    """Join an existing session (student)."""
    result = auth_service.join_session(
        db, request.class_code, request.nickname, request.l1, request.device_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Session not found or inactive")
    
    session_id, participant_id, settings = result
    token = auth_service.generate_token(session_id, participant_id, is_teacher=False)
    return JoinSessionResponse(
        token=token,
        session_id=session_id,
        participant_id=participant_id,
        settings=settings,
    )

@router.get("/session/{class_code}")
def get_session_info(class_code: str, db: Session = Depends(get_db)):
    """Get session info by class code."""
    from app.models.session import ClassSession
    session = db.query(ClassSession).filter(
        ClassSession.class_code == class_code.upper()
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session.id,
        "teacher_name": session.teacher_name,
        "grade_level": session.grade_level,
        "is_active": session.is_active,
    }
```

**Update routers/__init__.py:**
```python
from .auth import router as auth_router
# Add to api_router:
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
```

**Validation Steps:**
1. Create session: `curl -X POST http://localhost:8000/auth/create-session -H "Content-Type: application/json" -d '{"teacher_name":"Demo Teacher"}'`
2. Join session with returned code
3. Verify token generation and validation
4. Run `pytest backend/api/tests/test_auth.py -v`

**Definition of Done:**
- [ ] Create session returns class code
- [ ] Join session returns token
- [ ] Token verification works
- [ ] Session lookup by code works
- [ ] Tests pass

---


#### TICKET-03: WebSocket ASR Handler Hardening

**Priority:** P0 - BLOCKING  
**Estimated Time:** 3-4 hours  
**Dependencies:** TICKET-01, TICKET-02

**Objective:** Harden the WebSocket ASR streaming handler with proper error handling, session management, and integration with persistence.

**Files to Modify:**
```
backend/api/app/routers/v1/captions.py (major refactor)
backend/api/app/services/asr_client.py (add error handling)
backend/api/tests/test_captions_ws.py (new)
```

**Implementation Details:**

```python
# backend/api/app/routers/v1/captions.py (refactored)
"""Captions API endpoints - ASR streaming, simplification, translation."""

import asyncio
import json
import time
from typing import Dict, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import log_metric, logger
from app.schemas.common import (
    FocusCommand, GlossEntry, GlossRequest, GlossResponse,
    SimplifyRequest, SimplifyResponse,
)
from app.services.asr_client import ASRSession
from app.services.simplify import simplify_text
from app.services.translate import get_gloss
from app.services.db import get_db_session
from app.services.auth import verify_token
from app.models.transcript import Transcript

router = APIRouter()

# Active WebSocket sessions with metadata
active_sessions: Dict[str, dict] = {}

class CaptionSessionManager:
    """Manages a single caption streaming session."""
    
    def __init__(self, ws: WebSocket, session_id: str):
        self.ws = ws
        self.session_id = session_id
        self.asr_session: Optional[ASRSession] = None
        self.db_session_id: Optional[int] = None
        self.participant_id: Optional[int] = None
        self.save_transcripts: bool = False
        self.simplify_strength: int = 0
        self.l1: Optional[str] = None
        self.segment_count: int = 0
        self.start_time: float = time.time()
        self.last_activity: float = time.time()
        
    async def handle_start(self, data: dict):
        """Handle start message."""
        sample_rate = data.get("sample_rate", 16000)
        lang = data.get("lang", "en")
        self.save_transcripts = data.get("save", settings.save_transcripts_by_default)
        self.simplify_strength = data.get("simplify", 0)
        self.l1 = data.get("l1")
        
        # Verify token if provided
        token = data.get("token")
        if token:
            payload = verify_token(token)
            if payload:
                self.db_session_id = payload.get("session_id")
                self.participant_id = payload.get("participant_id")
        
        # Initialize ASR session
        if settings.enable_asr:
            self.asr_session = ASRSession(sample_rate=sample_rate, language=lang)
            log_metric("asr_session_start", session_id=self.session_id, 
                      db_session=self.db_session_id)
            await self.ws.send_json({"type": "started", "asr_enabled": True})
        else:
            await self.ws.send_json({"type": "started", "asr_enabled": False, 
                                     "message": "ASR disabled, text-only mode"})
    
    async def handle_audio(self, audio_bytes: bytes):
        """Handle incoming audio bytes."""
        if not self.asr_session:
            return
            
        self.last_activity = time.time()
        self.asr_session.feed(audio_bytes)
        
        # Check for partial transcript
        buffer_duration = len(self.asr_session.buffer) / (self.asr_session.sample_rate * 2)
        if buffer_duration > 0.5 and self.asr_session.voiced_frames > 5:
            partial = self.asr_session._get_partial_transcript()
            if partial and partial != self.asr_session.last_partial:
                self.asr_session.last_partial = partial
                await self.ws.send_json({
                    "type": "partial",
                    "text": partial,
                    "ts": [0, buffer_duration],
                })
        
        # Check if we should flush a segment
        if not self.asr_session.is_speaking and buffer_duration > 0.5:
            await self.flush_segment()
    
    async def flush_segment(self):
        """Flush current ASR buffer and emit final transcript."""
        if not self.asr_session:
            return
            
        segment = self.asr_session.flush_segment()
        if not segment or not segment.text.strip():
            return
        
        self.segment_count += 1
        
        # Apply simplification if requested
        simplified_text = None
        focus_commands = []
        if self.simplify_strength > 0:
            result = simplify_text(segment.text, self.simplify_strength, focus_commands=True)
            simplified_text = result.simplified
            focus_commands = [{"verb": f.verb, "object": f.object} for f in result.focus]
        
        # Get glossary if L1 specified
        gloss = []
        if self.l1:
            gloss_result = get_gloss(segment.text, self.l1, top_k=5)
            gloss = [{"en": g.en, "l1": g.l1} for g in gloss_result.gloss]
        
        # Build response
        response = {
            "type": "final",
            "text": segment.text,
            "words": [{"w": w.word, "s": w.start, "e": w.end} for w in segment.words],
            "segment_id": self.segment_count,
        }
        if simplified_text:
            response["simplified"] = simplified_text
            response["focus"] = focus_commands
        if gloss:
            response["gloss"] = gloss
        
        await self.ws.send_json(response)
        
        # Persist if enabled
        if self.save_transcripts and self.db_session_id:
            await self.save_transcript(segment, simplified_text)
    
    async def save_transcript(self, segment, simplified_text: Optional[str]):
        """Save transcript to database."""
        try:
            with get_db_session() as db:
                transcript = Transcript(
                    session_id=self.db_session_id,
                    segment_id=self.segment_count,
                    text=segment.text,
                    simplified_text=simplified_text,
                    words=[{"w": w.word, "s": w.start, "e": w.end} for w in segment.words],
                    ts_start=segment.start,
                    ts_end=segment.end,
                )
                db.add(transcript)
        except Exception as e:
            logger.error(f"Failed to save transcript: {e}")
    
    async def handle_stop(self):
        """Handle stop message."""
        if self.asr_session:
            await self.flush_segment()
        
        duration = time.time() - self.start_time
        log_metric("asr_session_stop", session_id=self.session_id,
                  segments=self.segment_count, duration=duration)


@router.websocket("/stream")
async def stream_captions(ws: WebSocket):
    """WebSocket endpoint for live ASR streaming."""
    await ws.accept()
    session_id = str(id(ws))
    manager = CaptionSessionManager(ws, session_id)
    active_sessions[session_id] = {"manager": manager, "start": time.time()}
    
    try:
        await ws.send_json({"type": "ready"})
        
        while True:
            try:
                message = await asyncio.wait_for(ws.receive(), timeout=60.0)
            except asyncio.TimeoutError:
                # Send keepalive
                await ws.send_json({"type": "ping"})
                continue
            
            if message["type"] == "websocket.disconnect":
                break
            
            # Handle text messages (JSON commands)
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    msg_type = data.get("type")
                    
                    if msg_type == "start":
                        await manager.handle_start(data)
                    elif msg_type == "stop":
                        await manager.handle_stop()
                        break
                    elif msg_type == "pong":
                        manager.last_activity = time.time()
                except json.JSONDecodeError:
                    await ws.send_json({"type": "error", "message": "Invalid JSON"})
            
            # Handle binary messages (audio)
            elif "bytes" in message:
                await manager.handle_audio(message["bytes"])
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except:
            pass
    finally:
        if session_id in active_sessions:
            del active_sessions[session_id]
        log_metric("asr_session_end", session_id=session_id)


@router.get("/active-sessions")
def get_active_sessions():
    """Get count of active streaming sessions (admin/debug)."""
    return {
        "count": len(active_sessions),
        "sessions": [
            {"id": sid, "duration": time.time() - s["start"]}
            for sid, s in active_sessions.items()
        ]
    }


# Keep existing REST endpoints (simplify, gloss) unchanged
@router.post("/simplify", response_model=SimplifyResponse)
def simplify_endpoint(request: SimplifyRequest) -> SimplifyResponse:
    """Simplify English text."""
    start_time = time.time()
    result = simplify_text(
        text=request.text,
        strength=request.strength,
        focus_commands=request.focus_commands,
    )
    latency = time.time() - start_time
    log_metric("simplify_endpoint", latency=latency, strength=request.strength)
    return SimplifyResponse(
        simplified=result.simplified,
        focus=[FocusCommand(verb=f.verb, object=f.object) for f in result.focus],
        explanations=result.explanations,
    )


@router.post("/gloss", response_model=GlossResponse)
def gloss_endpoint(request: GlossRequest) -> GlossResponse:
    """Get translation and vocabulary glossary for text."""
    start_time = time.time()
    result = get_gloss(text=request.text, l1=request.l1, top_k=request.top_k)
    latency = time.time() - start_time
    log_metric("gloss_endpoint", latency=latency, l1=request.l1)
    return GlossResponse(
        translation=result.translation,
        gloss=[GlossEntry(en=g.en, l1=g.l1, definition=g.definition) for g in result.gloss],
    )
```

**Validation Steps:**
1. Start backend: `make api`
2. Test WebSocket with wscat: `wscat -c ws://localhost:8000/v1/captions/stream`
3. Send: `{"type":"start","sample_rate":16000}`
4. Verify "started" response
5. Send: `{"type":"stop"}`
6. Check active-sessions endpoint

**Definition of Done:**
- [ ] WebSocket accepts connections reliably
- [ ] Start/stop protocol works
- [ ] Timeout handling with keepalive
- [ ] Error messages sent to client
- [ ] Transcripts saved when enabled
- [ ] Active sessions tracking works

---


#### TICKET-04: Live Captions Page (Teacher Portal)

**Priority:** P0 - BLOCKING  
**Estimated Time:** 4-5 hours  
**Dependencies:** TICKET-03

**Objective:** Implement the Live Captions page in the teacher portal with real-time ASR display, simplification controls, and L1 glossary.

**Files to Create/Modify:**
```
apps/teacher-portal/src/app/captions/page.tsx (new)
apps/teacher-portal/src/lib/api.ts (new)
apps/teacher-portal/src/lib/websocket.ts (new)
apps/teacher-portal/src/components/CaptionDisplay.tsx (new)
apps/teacher-portal/src/components/AudioRecorder.tsx (new)
apps/teacher-portal/next.config.js (modify for API proxy)
```

**Implementation Details:**

```typescript
// apps/teacher-portal/src/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function createSession(teacherName: string, gradeLevel: string = 'K-6') {
  const res = await fetch(`${API_BASE}/auth/create-session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ teacher_name: teacherName, grade_level: gradeLevel }),
  });
  if (!res.ok) throw new Error('Failed to create session');
  return res.json();
}

export async function simplifyText(text: string, strength: number) {
  const res = await fetch(`${API_BASE}/v1/captions/simplify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, strength, focus_commands: true }),
  });
  if (!res.ok) throw new Error('Failed to simplify');
  return res.json();
}

export async function getGloss(text: string, l1: string) {
  const res = await fetch(`${API_BASE}/v1/captions/gloss`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, l1, top_k: 8 }),
  });
  if (!res.ok) throw new Error('Failed to get gloss');
  return res.json();
}
```

```typescript
// apps/teacher-portal/src/lib/websocket.ts
export interface CaptionSegment {
  type: 'partial' | 'final';
  text: string;
  simplified?: string;
  words?: { w: string; s: number; e: number }[];
  focus?: { verb: string; object?: string }[];
  gloss?: { en: string; l1: string }[];
  segment_id?: number;
}

export class CaptionWebSocket {
  private ws: WebSocket | null = null;
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private processor: ScriptProcessorNode | null = null;
  
  constructor(
    private onSegment: (segment: CaptionSegment) => void,
    private onStatus: (status: string) => void,
    private onError: (error: string) => void,
  ) {}
  
  async connect(options: {
    sampleRate?: number;
    lang?: string;
    simplify?: number;
    l1?: string;
    save?: boolean;
    token?: string;
  } = {}) {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    this.ws = new WebSocket(`${wsUrl}/v1/captions/stream`);
    
    this.ws.onopen = () => {
      this.onStatus('connected');
      this.ws?.send(JSON.stringify({
        type: 'start',
        sample_rate: options.sampleRate || 16000,
        lang: options.lang || 'en',
        simplify: options.simplify || 0,
        l1: options.l1,
        save: options.save || false,
        token: options.token,
      }));
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'ready') {
        this.onStatus('ready');
      } else if (data.type === 'started') {
        this.onStatus('streaming');
      } else if (data.type === 'partial' || data.type === 'final') {
        this.onSegment(data);
      } else if (data.type === 'error') {
        this.onError(data.message);
      } else if (data.type === 'ping') {
        this.ws?.send(JSON.stringify({ type: 'pong' }));
      }
    };
    
    this.ws.onerror = () => {
      this.onError('WebSocket connection error');
    };
    
    this.ws.onclose = () => {
      this.onStatus('disconnected');
    };
  }
  
  async startRecording() {
    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ 
        audio: { sampleRate: 16000, channelCount: 1, echoCancellation: true } 
      });
      
      this.audioContext = new AudioContext({ sampleRate: 16000 });
      const source = this.audioContext.createMediaStreamSource(this.mediaStream);
      this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
      
      this.processor.onaudioprocess = (e) => {
        if (this.ws?.readyState === WebSocket.OPEN) {
          const inputData = e.inputBuffer.getChannelData(0);
          const pcm16 = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            pcm16[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
          }
          this.ws.send(pcm16.buffer);
        }
      };
      
      source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);
      this.onStatus('recording');
    } catch (err) {
      this.onError('Microphone access denied');
    }
  }
  
  stopRecording() {
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }
  }
  
  disconnect() {
    this.stopRecording();
    if (this.ws) {
      this.ws.send(JSON.stringify({ type: 'stop' }));
      this.ws.close();
      this.ws = null;
    }
  }
}
```

```tsx
// apps/teacher-portal/src/app/captions/page.tsx
'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Settings, Languages, Zap, Copy, Trash2 } from 'lucide-react';
import { CaptionWebSocket, CaptionSegment } from '@/lib/websocket';

const LANGUAGES = [
  { code: 'ar', name: 'Arabic' },
  { code: 'uk', name: 'Ukrainian' },
  { code: 'es', name: 'Spanish' },
  { code: 'zh', name: 'Chinese' },
  { code: 'tl', name: 'Tagalog' },
  { code: 'pa', name: 'Punjabi' },
];

export default function CaptionsPage() {
  const [isRecording, setIsRecording] = useState(false);
  const [status, setStatus] = useState<string>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [segments, setSegments] = useState<CaptionSegment[]>([]);
  const [partialText, setPartialText] = useState<string>('');
  const [simplifyStrength, setSimplifyStrength] = useState(0);
  const [l1, setL1] = useState<string>('');
  const [showSettings, setShowSettings] = useState(false);
  
  const wsRef = useRef<CaptionWebSocket | null>(null);
  const captionsEndRef = useRef<HTMLDivElement>(null);
  
  const scrollToBottom = () => {
    captionsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [segments, partialText]);
  
  const handleSegment = useCallback((segment: CaptionSegment) => {
    if (segment.type === 'partial') {
      setPartialText(segment.text);
    } else if (segment.type === 'final') {
      setSegments(prev => [...prev, segment]);
      setPartialText('');
    }
  }, []);
  
  const handleStatus = useCallback((newStatus: string) => {
    setStatus(newStatus);
    if (newStatus === 'disconnected') {
      setIsRecording(false);
    }
  }, []);
  
  const handleError = useCallback((errorMsg: string) => {
    setError(errorMsg);
    setIsRecording(false);
  }, []);
  
  const startCapturing = async () => {
    setError(null);
    wsRef.current = new CaptionWebSocket(handleSegment, handleStatus, handleError);
    await wsRef.current.connect({
      simplify: simplifyStrength,
      l1: l1 || undefined,
    });
    await wsRef.current.startRecording();
    setIsRecording(true);
  };
  
  const stopCapturing = () => {
    wsRef.current?.disconnect();
    wsRef.current = null;
    setIsRecording(false);
  };
  
  const clearCaptions = () => {
    setSegments([]);
    setPartialText('');
  };
  
  const copyAllText = () => {
    const text = segments.map(s => s.simplified || s.text).join(' ');
    navigator.clipboard.writeText(text);
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Live Captions</h1>
          <p className="mt-1 text-gray-600">
            Real-time speech-to-text with simplification and translation
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`px-3 py-1 rounded-full text-sm ${
            status === 'recording' ? 'bg-red-100 text-red-700' :
            status === 'streaming' ? 'bg-green-100 text-green-700' :
            'bg-gray-100 text-gray-600'
          }`}>
            {status}
          </span>
        </div>
      </div>
      
      {/* Controls */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={isRecording ? stopCapturing : startCapturing}
              className={`flex items-center px-6 py-3 rounded-lg font-medium transition-colors ${
                isRecording 
                  ? 'bg-red-500 hover:bg-red-600 text-white' 
                  : 'bg-primary-600 hover:bg-primary-700 text-white'
              }`}
            >
              {isRecording ? (
                <>
                  <MicOff className="w-5 h-5 mr-2" />
                  Stop Capturing
                </>
              ) : (
                <>
                  <Mic className="w-5 h-5 mr-2" />
                  Start Capturing
                </>
              )}
            </button>
            
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-3 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
            >
              <Settings className="w-5 h-5 text-gray-600" />
            </button>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={copyAllText}
              disabled={segments.length === 0}
              className="flex items-center px-3 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
            >
              <Copy className="w-4 h-4 mr-1" />
              Copy All
            </button>
            <button
              onClick={clearCaptions}
              disabled={segments.length === 0}
              className="flex items-center px-3 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
            >
              <Trash2 className="w-4 h-4 mr-1" />
              Clear
            </button>
          </div>
        </div>
        
        {/* Settings Panel */}
        {showSettings && (
          <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Zap className="w-4 h-4 inline mr-1" />
                Simplification Level
              </label>
              <input
                type="range"
                min="0"
                max="3"
                value={simplifyStrength}
                onChange={(e) => setSimplifyStrength(parseInt(e.target.value))}
                className="w-full"
                disabled={isRecording}
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>Off</span>
                <span>Light</span>
                <span>Medium</span>
                <span>Max</span>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Languages className="w-4 h-4 inline mr-1" />
                Student L1 (for glossary)
              </label>
              <select
                value={l1}
                onChange={(e) => setL1(e.target.value)}
                className="input-field"
                disabled={isRecording}
              >
                <option value="">None</option>
                {LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
      </div>
      
      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}
      
      {/* Captions Display */}
      <div className="card min-h-[400px] max-h-[600px] overflow-y-auto">
        <div className="space-y-4">
          {segments.length === 0 && !partialText && (
            <p className="text-gray-400 text-center py-12">
              Click "Start Capturing" and speak to see live captions...
            </p>
          )}
          
          {segments.map((segment, idx) => (
            <div key={idx} className="border-b border-gray-100 pb-3 last:border-0">
              <p className="text-lg text-gray-900">
                {simplifyStrength > 0 && segment.simplified ? segment.simplified : segment.text}
              </p>
              
              {/* Show original if simplified */}
              {simplifyStrength > 0 && segment.simplified && segment.simplified !== segment.text && (
                <p className="text-sm text-gray-500 mt-1">
                  Original: {segment.text}
                </p>
              )}
              
              {/* Focus commands */}
              {segment.focus && segment.focus.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {segment.focus.map((f, i) => (
                    <span key={i} className="px-2 py-0.5 bg-yellow-100 text-yellow-800 rounded text-xs">
                      {f.verb} {f.object && `→ ${f.object}`}
                    </span>
                  ))}
                </div>
              )}
              
              {/* Glossary */}
              {segment.gloss && segment.gloss.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {segment.gloss.map((g, i) => (
                    <span key={i} className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-sm">
                      {g.en} → {g.l1}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
          
          {/* Partial (in-progress) text */}
          {partialText && (
            <p className="text-lg text-gray-400 italic">
              {partialText}...
            </p>
          )}
          
          <div ref={captionsEndRef} />
        </div>
      </div>
    </div>
  );
}
```

**Update next.config.js for API proxy:**
```javascript
// apps/teacher-portal/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
```

**Validation Steps:**
1. Start backend: `make api`
2. Start frontend: `cd apps/teacher-portal && npm run dev`
3. Navigate to http://localhost:3000/captions
4. Click "Start Capturing" and grant microphone permission
5. Speak and verify captions appear
6. Test simplification slider
7. Test L1 glossary selection

**Definition of Done:**
- [ ] Page loads without errors
- [ ] Microphone permission request works
- [ ] WebSocket connects successfully
- [ ] Partial captions appear while speaking
- [ ] Final captions appear after pauses
- [ ] Simplification slider affects output
- [ ] L1 glossary shows translations
- [ ] Copy and Clear buttons work
- [ ] Status indicator updates correctly

---


#### TICKET-05: Glossary/Translation Page (Teacher Portal)

**Priority:** P1 - HIGH VALUE  
**Estimated Time:** 2-3 hours  
**Dependencies:** TICKET-04

**Objective:** Implement a standalone Glossary/Translation page for teachers to generate bilingual vocabulary lists and translations.

**Files to Create:**
```
apps/teacher-portal/src/app/glossary/page.tsx (new)
```

**Implementation Details:**

```tsx
// apps/teacher-portal/src/app/glossary/page.tsx
'use client';

import { useState } from 'react';
import { Loader2, Copy, Download, Languages, BookOpen } from 'lucide-react';

interface GlossEntry {
  en: string;
  l1: string;
  definition?: string;
}

interface GlossResult {
  translation: string;
  gloss: GlossEntry[];
}

const LANGUAGES = [
  { code: 'ar', name: 'Arabic', dir: 'rtl' },
  { code: 'uk', name: 'Ukrainian', dir: 'ltr' },
  { code: 'es', name: 'Spanish', dir: 'ltr' },
  { code: 'zh', name: 'Chinese', dir: 'ltr' },
  { code: 'tl', name: 'Tagalog', dir: 'ltr' },
  { code: 'pa', name: 'Punjabi', dir: 'ltr' },
];

const SAMPLE_TEXTS = [
  {
    title: 'Math - Fractions',
    text: 'A fraction represents part of a whole number. The top number is called the numerator. The bottom number is called the denominator.',
  },
  {
    title: 'Science - Water Cycle',
    text: 'Water evaporates from lakes and oceans. It rises into the sky and forms clouds. When clouds get heavy, precipitation falls as rain or snow.',
  },
  {
    title: 'Classroom Instructions',
    text: 'Please open your textbooks to page twenty-five. Read the passage quietly. Then answer the questions at the bottom of the page.',
  },
];

export default function GlossaryPage() {
  const [text, setText] = useState('');
  const [l1, setL1] = useState('ar');
  const [topK, setTopK] = useState(10);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GlossResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!text.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/captions/gloss', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, l1, top_k: topK }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate glossary');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const copyGlossary = () => {
    if (!result) return;
    const glossText = result.gloss
      .map((g) => `${g.en} - ${g.l1}`)
      .join('\n');
    navigator.clipboard.writeText(glossText);
  };

  const downloadCSV = () => {
    if (!result) return;
    const csv = [
      'English,Translation',
      ...result.gloss.map((g) => `"${g.en}","${g.l1}"`),
    ].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `glossary-${l1}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const selectedLang = LANGUAGES.find((lang) => lang.code === l1);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Translation & Glossary</h1>
        <p className="mt-2 text-gray-600">
          Generate bilingual glossaries and translations for any content. Perfect for
          creating vocabulary lists and translated materials.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="card">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              English Text
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="input-field min-h-[150px] resize-y"
              placeholder="Enter or paste English text to translate and create a glossary..."
            />
            <div className="mt-2 flex items-center justify-between">
              <span className="text-sm text-gray-500">
                {text.split(/\s+/).filter(Boolean).length} words
              </span>
              <div className="flex space-x-2">
                {SAMPLE_TEXTS.map((sample, idx) => (
                  <button
                    key={idx}
                    onClick={() => setText(sample.text)}
                    className="text-xs text-primary-600 hover:text-primary-700"
                  >
                    {sample.title}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="card">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Languages className="w-4 h-4 inline mr-1" />
              Target Language
            </label>
            <select
              value={l1}
              onChange={(e) => setL1(e.target.value)}
              className="input-field"
            >
              {LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>

          <div className="card">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <BookOpen className="w-4 h-4 inline mr-1" />
              Vocabulary Words (max)
            </label>
            <input
              type="range"
              min="5"
              max="20"
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="text-center text-gray-600">{topK} words</div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading || !text.trim()}
            className="btn-primary w-full flex items-center justify-center"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              'Generate Glossary'
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          {/* Translation */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Translation</h2>
              <button
                onClick={() => navigator.clipboard.writeText(result.translation)}
                className="text-gray-500 hover:text-gray-700"
              >
                <Copy className="w-4 h-4" />
              </button>
            </div>
            <div
              className={`bg-gray-50 p-4 rounded-lg text-lg ${
                selectedLang?.dir === 'rtl' ? 'text-right' : ''
              }`}
              dir={selectedLang?.dir}
            >
              {result.translation}
            </div>
          </div>

          {/* Glossary */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                Vocabulary Glossary ({result.gloss.length} words)
              </h2>
              <div className="flex space-x-2">
                <button
                  onClick={copyGlossary}
                  className="flex items-center text-gray-600 hover:text-gray-800"
                >
                  <Copy className="w-4 h-4 mr-1" />
                  Copy
                </button>
                <button
                  onClick={downloadCSV}
                  className="flex items-center text-primary-600 hover:text-primary-700"
                >
                  <Download className="w-4 h-4 mr-1" />
                  CSV
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {result.gloss.map((entry, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between bg-gray-50 p-3 rounded-lg"
                >
                  <span className="font-medium text-gray-900">{entry.en}</span>
                  <span
                    className={`text-primary-600 ${
                      selectedLang?.dir === 'rtl' ? 'text-right' : ''
                    }`}
                    dir={selectedLang?.dir}
                  >
                    {entry.l1}
                  </span>
                </div>
              ))}
            </div>

            {result.gloss.length === 0 && (
              <p className="text-gray-500 text-center py-4">
                No vocabulary words found. Try adding more content-specific terms.
              </p>
            )}
          </div>

          {/* Print-friendly view hint */}
          <div className="text-center text-sm text-gray-500">
            <p>
              Tip: Use Ctrl+P (Cmd+P on Mac) to print this glossary for classroom use.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
```

**Validation Steps:**
1. Navigate to http://localhost:3000/glossary
2. Enter sample text or use quick-fill buttons
3. Select target language
4. Click Generate Glossary
5. Verify translation appears
6. Verify glossary entries appear
7. Test Copy and CSV download
8. Test RTL display for Arabic

**Definition of Done:**
- [ ] Page loads without errors
- [ ] Sample text buttons work
- [ ] Language selection works
- [ ] Glossary generation returns results
- [ ] Translation displays correctly (including RTL)
- [ ] Copy and CSV export work
- [ ] Word count slider affects results

---

### Phase 2: Reading Features (Tickets 6-9)

---

#### TICKET-06: Reading Results Persistence

**Priority:** P1 - HIGH VALUE  
**Estimated Time:** 2 hours  
**Dependencies:** TICKET-01

**Objective:** Add persistence for reading assessment results to enable demo of progress tracking.

**Files to Modify:**
```
backend/api/app/routers/v1/reading.py (modify)
backend/api/app/services/reading_results.py (new)
```

**Implementation Details:**

```python
# backend/api/app/services/reading_results.py
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
    return db.query(ReadingResult).filter(
        ReadingResult.session_id == session_id
    ).order_by(ReadingResult.created_at.desc()).all()

def get_participant_results(db: Session, participant_id: int) -> List[ReadingResult]:
    """Get all reading results for a participant."""
    return db.query(ReadingResult).filter(
        ReadingResult.participant_id == participant_id
    ).order_by(ReadingResult.created_at.desc()).all()
```

**Add to reading.py router:**
```python
from app.services.db import get_db
from app.services import reading_results

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
                "created_at": r.created_at.isoformat(),
            }
            for r in results
        ],
    }

@router.get("/results/{session_id}/export")
def export_reading_results(session_id: int, db: Session = Depends(get_db)):
    """Export reading results as CSV."""
    results = reading_results.get_session_results(db, session_id)
    
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Participant', 'Passage', 'WPM', 'WCPM', 'Accuracy', 'Date'])
    
    for r in results:
        writer.writerow([
            r.id, r.participant_id, r.passage_id,
            r.wpm, r.wcpm, r.accuracy, r.created_at.isoformat()
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=reading-results-{session_id}.csv"}
    )
```

**Validation Steps:**
1. Score some readings via the API
2. Call GET /v1/reading/results/{session_id}
3. Verify results returned
4. Test CSV export endpoint

**Definition of Done:**
- [ ] Results saved to database
- [ ] Results retrieval endpoint works
- [ ] CSV export works
- [ ] Results include timestamps

---

