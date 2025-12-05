"""Captions API endpoints - ASR streaming, simplification, translation."""

import asyncio
import json
import time
from typing import Dict, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.core.logging import log_metric, logger
from app.schemas.common import (
    FocusCommand,
    GlossEntry,
    GlossRequest,
    GlossResponse,
    SimplifyRequest,
    SimplifyResponse,
)
from app.services.asr_client import ASRSession
from app.services.simplify import simplify_text
from app.services.translate import get_gloss
from app.services.auth import verify_token

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
            try:
                self.asr_session = ASRSession(sample_rate=sample_rate, language=lang)
                log_metric(
                    "asr_session_start",
                    session_id=self.session_id,
                    db_session=self.db_session_id,
                )
                await self.ws.send_json({"type": "started", "asr_enabled": True})
            except Exception as e:
                logger.error(f"Failed to initialize ASR: {e}")
                await self.ws.send_json({
                    "type": "started",
                    "asr_enabled": False,
                    "message": f"ASR initialization failed: {str(e)}",
                })
        else:
            await self.ws.send_json({
                "type": "started",
                "asr_enabled": False,
                "message": "ASR disabled, text-only mode",
            })

    async def handle_audio(self, audio_bytes: bytes):
        """Handle incoming audio bytes."""
        if not self.asr_session:
            return

        self.last_activity = time.time()
        self.asr_session.feed(audio_bytes)

        # Check for partial transcript
        buffer_duration = len(self.asr_session.buffer) / (self.asr_session.sample_rate * 2)
        if buffer_duration > 0.5 and self.asr_session.voiced_frames > 5:
            try:
                partial = self.asr_session._get_partial_transcript()
                if partial and partial != self.asr_session.last_partial:
                    self.asr_session.last_partial = partial
                    await self.ws.send_json({
                        "type": "partial",
                        "text": partial,
                        "ts": [0, buffer_duration],
                    })
            except Exception as e:
                logger.debug(f"Partial transcript error: {e}")

        # Check if we should flush a segment
        if not self.asr_session.is_speaking and buffer_duration > 0.5:
            await self.flush_segment()

    async def flush_segment(self):
        """Flush current ASR buffer and emit final transcript."""
        if not self.asr_session:
            return

        try:
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
                try:
                    gloss_result = get_gloss(segment.text, self.l1, top_k=5)
                    gloss = [{"en": g.en, "l1": g.l1} for g in gloss_result.gloss]
                except Exception as e:
                    logger.debug(f"Gloss error: {e}")

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

        except Exception as e:
            logger.error(f"Flush segment error: {e}")

    async def save_transcript(self, segment, simplified_text: Optional[str]):
        """Save transcript to database."""
        try:
            from app.services.db import get_db_session
            from app.models.transcript import Transcript

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
        log_metric(
            "asr_session_stop",
            session_id=self.session_id,
            segments=self.segment_count,
            duration=duration,
        )


@router.websocket("/stream")
async def stream_captions(ws: WebSocket):
    """
    WebSocket endpoint for live ASR streaming.

    Protocol:
    - Client sends: {"type":"start","sample_rate":16000,"lang":"en",...}
    - Client sends: Binary audio frames (PCM16 LE)
    - Client sends: {"type":"stop"}
    - Server sends: {"type":"ready"}
    - Server sends: {"type":"partial","text":"..."}
    - Server sends: {"type":"final","text":"...","words":[...]}
    """
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
                try:
                    await ws.send_json({"type": "ping"})
                except Exception:
                    break
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
                except Exception as e:
                    logger.error(f"Message handling error: {e}")
                    await ws.send_json({"type": "error", "message": str(e)})

            # Handle binary messages (audio)
            elif "bytes" in message:
                await manager.handle_audio(message["bytes"])

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
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
        ],
    }


@router.post("/simplify", response_model=SimplifyResponse)
def simplify_endpoint(request: SimplifyRequest) -> SimplifyResponse:
    """
    Simplify English text.

    - strength 0: No simplification
    - strength 1: Light simplification
    - strength 2: Medium simplification
    - strength 3: Maximum simplification
    """
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

    result = get_gloss(
        text=request.text,
        l1=request.l1,
        top_k=request.top_k,
    )

    latency = time.time() - start_time
    log_metric("gloss_endpoint", latency=latency, l1=request.l1)

    return GlossResponse(
        translation=result.translation,
        gloss=[GlossEntry(en=g.en, l1=g.l1, definition=g.definition) for g in result.gloss],
    )
