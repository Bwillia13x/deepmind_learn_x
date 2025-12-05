"""Oral Reading Fluency (ORF) scoring service."""

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from app.core.logging import log_metric, logger
from app.services.asr_client import batch_transcribe, transcribe_bytes


@dataclass
class ReadingError:
    """A reading error."""

    type: str  # 'sub' (substitution), 'del' (deletion), 'ins' (insertion)
    ref: Optional[str]  # reference word (expected)
    hyp: Optional[str]  # hypothesis word (what was said)
    time: Optional[float]  # timestamp in audio


@dataclass
class TimedWord:
    """A word with timing information."""

    word: str
    start: float
    end: float


@dataclass
class ORFResult:
    """Result of ORF scoring."""

    wpm: float  # words per minute
    wcpm: Optional[float]  # words correct per minute
    accuracy: Optional[float]  # 0-1
    errors: List[ReadingError]
    words_timed: List[TimedWord]
    duration: float


def score_simple(words_read: int, seconds: int, errors: int = 0) -> dict:
    """
    Simple WPM/WCPM calculation without audio.

    Args:
        words_read: Total words read
        seconds: Duration in seconds
        errors: Number of errors

    Returns:
        Dict with wpm, wcpm, accuracy
    """
    wpm = (words_read / max(seconds, 1)) * 60.0
    wcpm = ((words_read - errors) / max(seconds, 1)) * 60.0
    accuracy = max(0.0, 1.0 - errors / max(words_read, 1))

    log_metric("orf_simple", words_read=words_read, seconds=seconds, errors=errors, wpm=wpm)

    return {
        "wpm": round(wpm, 1),
        "wcpm": round(wcpm, 1),
        "accuracy": round(accuracy, 3),
    }


def score_audio(
    audio_bytes: bytes,
    sample_rate: int = 16000,
    reference_text: Optional[str] = None,
    language: str = "en",
) -> ORFResult:
    """
    Score reading fluency from audio.

    Args:
        audio_bytes: PCM16 audio bytes
        sample_rate: Sample rate (default 16kHz)
        reference_text: Expected text for accuracy calculation
        language: Language code

    Returns:
        ORFResult with WPM, WCPM, accuracy, errors
    """
    log_metric("orf_audio_start", has_reference=reference_text is not None)

    # Transcribe audio
    segment = transcribe_bytes(audio_bytes, sample_rate, language)

    duration = segment.end
    hyp_words = [w.word.lower().strip(".,!?\"'") for w in segment.words]
    timed_words = [TimedWord(word=w.word, start=w.start, end=w.end) for w in segment.words]

    # Calculate WPM
    word_count = len(hyp_words)
    wpm = (word_count / max(duration, 0.1)) * 60.0

    if reference_text:
        # Normalize reference
        ref_words = normalize_text(reference_text).split()

        # Align and find errors
        errors, correct_count = align_and_score(ref_words, hyp_words, segment.words)

        wcpm = (correct_count / max(duration, 0.1)) * 60.0
        accuracy = correct_count / max(len(ref_words), 1)

        log_metric(
            "orf_audio_result",
            wpm=wpm,
            wcpm=wcpm,
            accuracy=accuracy,
            error_count=len(errors),
        )

        return ORFResult(
            wpm=round(wpm, 1),
            wcpm=round(wcpm, 1),
            accuracy=round(accuracy, 3),
            errors=errors,
            words_timed=timed_words,
            duration=duration,
        )
    else:
        # No reference, just return WPM
        log_metric("orf_audio_result", wpm=wpm)

        return ORFResult(
            wpm=round(wpm, 1),
            wcpm=None,
            accuracy=None,
            errors=[],
            words_timed=timed_words,
            duration=duration,
        )


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    import re

    # Lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r"[.,!?;:\"'()\[\]{}]", "", text)
    # Normalize whitespace
    text = " ".join(text.split())
    return text


def align_and_score(
    ref_words: List[str],
    hyp_words: List[str],
    timed_hyp: List,
) -> Tuple[List[ReadingError], int]:
    """
    Align reference and hypothesis using Levenshtein distance.
    Returns list of errors and count of correct words.
    """
    errors = []
    correct_count = 0

    # Simple Levenshtein alignment
    m, n = len(ref_words), len(hyp_words)

    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # deletion
                    dp[i][j - 1],      # insertion
                    dp[i - 1][j - 1],  # substitution
                )

    # Backtrack to find alignment
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and ref_words[i - 1] == hyp_words[j - 1]:
            correct_count += 1
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            # Substitution
            time_val = timed_hyp[j - 1].start if j - 1 < len(timed_hyp) else None
            errors.append(ReadingError(
                type="sub",
                ref=ref_words[i - 1],
                hyp=hyp_words[j - 1],
                time=time_val,
            ))
            i -= 1
            j -= 1
        elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
            # Insertion (extra word)
            time_val = timed_hyp[j - 1].start if j - 1 < len(timed_hyp) else None
            errors.append(ReadingError(
                type="ins",
                ref=None,
                hyp=hyp_words[j - 1],
                time=time_val,
            ))
            j -= 1
        elif i > 0:
            # Deletion (missed word)
            errors.append(ReadingError(
                type="del",
                ref=ref_words[i - 1],
                hyp=None,
                time=None,
            ))
            i -= 1

    errors.reverse()
    return errors, correct_count


def score_audio_file(
    audio_path: str,
    reference_text: Optional[str] = None,
    language: str = "en",
) -> ORFResult:
    """Score reading fluency from an audio file."""
    segment = batch_transcribe(audio_path, language)

    duration = segment.end
    hyp_words = [w.word.lower().strip(".,!?\"'") for w in segment.words]
    timed_words = [TimedWord(word=w.word, start=w.start, end=w.end) for w in segment.words]

    word_count = len(hyp_words)
    wpm = (word_count / max(duration, 0.1)) * 60.0

    if reference_text:
        ref_words = normalize_text(reference_text).split()
        errors, correct_count = align_and_score(ref_words, hyp_words, segment.words)
        wcpm = (correct_count / max(duration, 0.1)) * 60.0
        accuracy = correct_count / max(len(ref_words), 1)

        return ORFResult(
            wpm=round(wpm, 1),
            wcpm=round(wcpm, 1),
            accuracy=round(accuracy, 3),
            errors=errors,
            words_timed=timed_words,
            duration=duration,
        )
    else:
        return ORFResult(
            wpm=round(wpm, 1),
            wcpm=None,
            accuracy=None,
            errors=[],
            words_timed=timed_words,
            duration=duration,
        )
