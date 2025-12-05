"""Speaking Coach API endpoints - pronunciation practice and feedback."""

import tempfile
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel

from app.core.logging import log_metric, logger
from app.services import pronunciation
from app.services.asr_client import get_asr_client


router = APIRouter()


class WordPronunciationRequest(BaseModel):
    """Request for word pronunciation scoring."""
    text: str
    target_word: str


class MinimalPairRequest(BaseModel):
    """Request for minimal pair scoring."""
    word1: str
    word2: str
    pair_id: str


@router.post("/score_word")
async def score_word_pronunciation(request: WordPronunciationRequest):
    """
    Score pronunciation accuracy for a single word.
    
    Compares transcribed text to target word.
    """
    result = pronunciation.score_word_pronunciation(
        transcribed_text=request.text,
        target_word=request.target_word,
    )
    
    log_metric(
        "pronunciation_score_word",
        target=request.target_word,
        score=result["score"],
    )
    
    return result


@router.post("/score_audio_word")
async def score_audio_word(
    audio_file: UploadFile = File(...),
    target_word: str = Form(...),
):
    """
    Score pronunciation from uploaded audio.
    
    Transcribes audio and scores against target word.
    """
    start_time = time.time()
    
    # Save uploaded file
    suffix = Path(audio_file.filename or "audio.wav").suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await audio_file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Transcribe using ASR
        asr = get_asr_client()
        segments, _ = asr.model.transcribe(tmp_path, language="en")
        
        # Get transcribed text
        transcribed = " ".join([seg.text for seg in segments]).strip()
        
        # Score pronunciation
        result = pronunciation.score_word_pronunciation(
            transcribed_text=transcribed,
            target_word=target_word,
        )
        
        latency = time.time() - start_time
        log_metric(
            "pronunciation_score_audio",
            latency=latency,
            target=target_word,
            score=result["score"],
        )
        
        return result
        
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.post("/score_minimal_pair")
def score_minimal_pair(request: MinimalPairRequest):
    """
    Score a minimal pair exercise.
    
    Evaluates student's ability to distinguish between two contrasting sounds.
    """
    result = pronunciation.score_minimal_pair(
        transcribed_word1=request.word1,
        transcribed_word2=request.word2,
        pair_id=request.pair_id,
    )
    
    log_metric(
        "pronunciation_minimal_pair",
        pair_id=request.pair_id,
        avg_score=result.get("average_score", 0),
    )
    
    return result


@router.get("/exercises/{l1_language}")
def get_exercises(l1_language: str):
    """
    Get recommended pronunciation exercises for a specific L1.
    
    Returns minimal pairs targeted for common pronunciation challenges
    for speakers of the specified native language.
    """
    exercises = pronunciation.get_exercises_for_l1(l1_language)
    
    log_metric("pronunciation_get_exercises", l1=l1_language, count=len(exercises))
    
    return {
        "l1": l1_language,
        "count": len(exercises),
        "exercises": exercises,
    }


@router.get("/exercises")
def get_all_exercises():
    """Get all available minimal pair exercises."""
    pairs_data = pronunciation.load_minimal_pairs()
    
    return {
        "count": len(pairs_data.get("pairs", [])),
        "pairs": pairs_data.get("pairs", []),
        "practice_sentences": pairs_data.get("practice_sentences", []),
    }
