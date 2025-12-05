"""ASR (Automatic Speech Recognition) client using faster-whisper."""

import io
import struct
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

from app.core.config import settings
from app.core.logging import log_metric, logger

# Lazy load heavy dependencies
_whisper_model = None
_vad = None


def get_whisper_model():
    """Lazy load the Whisper model."""
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel

            logger.info(f"Loading Whisper model: {settings.asr_model}")
            _whisper_model = WhisperModel(
                settings.asr_model,
                device=settings.asr_device,
                compute_type=settings.asr_compute_type,
            )
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    return _whisper_model


def get_vad():
    """Lazy load the VAD."""
    global _vad
    if _vad is None:
        try:
            import webrtcvad

            _vad = webrtcvad.Vad(3)  # Aggressiveness level 3
        except Exception as e:
            logger.warning(f"VAD not available: {e}")
    return _vad


@dataclass
class Word:
    """A transcribed word with timing."""

    word: str
    start: float
    end: float


@dataclass
class TranscriptSegment:
    """A segment of transcription."""

    text: str
    words: List[Word]
    start: float
    end: float


@dataclass
class ASRSession:
    """Maintains state for a streaming ASR session."""

    sample_rate: int = 16000
    language: str = "en"
    buffer: bytes = field(default_factory=bytes)
    segments: List[TranscriptSegment] = field(default_factory=list)
    segment_id: int = 0
    last_partial: str = ""
    voiced_frames: int = 0
    silent_frames: int = 0
    is_speaking: bool = False
    min_segment_duration: float = 0.5
    max_segment_duration: float = 10.0
    silence_threshold: int = 15  # frames of silence to trigger end

    def feed(self, audio_bytes: bytes) -> Optional[str]:
        """
        Feed audio bytes and return partial transcript if available.
        Returns None if no update, or partial text string.
        """
        self.buffer += audio_bytes

        # Check VAD every 20ms frame (320 bytes at 16kHz, 16-bit)
        frame_size = int(self.sample_rate * 0.02 * 2)  # 20ms frames
        vad = get_vad()

        if vad and len(self.buffer) >= frame_size:
            frame = self.buffer[-frame_size:]
            try:
                is_speech = vad.is_speech(frame, self.sample_rate)
                if is_speech:
                    self.voiced_frames += 1
                    self.silent_frames = 0
                    self.is_speaking = True
                else:
                    self.silent_frames += 1
                    if self.silent_frames > self.silence_threshold:
                        self.is_speaking = False
            except Exception:
                pass

        # Generate partial every ~500ms of audio
        buffer_duration = len(self.buffer) / (self.sample_rate * 2)
        if buffer_duration > 0.5 and self.voiced_frames > 5:
            partial = self._get_partial_transcript()
            if partial and partial != self.last_partial:
                self.last_partial = partial
                return partial

        return None

    def _get_partial_transcript(self) -> str:
        """Get partial transcript of current buffer."""
        try:
            audio_array = self._bytes_to_array(self.buffer)
            if len(audio_array) < self.sample_rate * 0.3:
                return ""

            model = get_whisper_model()
            segments, _ = model.transcribe(
                audio_array,
                language=self.language,
                vad_filter=True,
                word_timestamps=False,
            )
            text = " ".join(seg.text.strip() for seg in segments)
            return text
        except Exception as e:
            logger.debug(f"Partial transcription error: {e}")
            return ""

    def flush_segment(self) -> Optional[TranscriptSegment]:
        """
        Flush the current buffer and return a final segment.
        Returns None if buffer is too short.
        """
        start_time = time.time()

        if len(self.buffer) < self.sample_rate * 2 * self.min_segment_duration:
            return None

        try:
            audio_array = self._bytes_to_array(self.buffer)
            model = get_whisper_model()

            segments, info = model.transcribe(
                audio_array,
                language=self.language,
                vad_filter=True,
                word_timestamps=True,
            )

            words = []
            full_text = []

            for seg in segments:
                full_text.append(seg.text.strip())
                if seg.words:
                    for w in seg.words:
                        words.append(Word(word=w.word.strip(), start=w.start, end=w.end))

            text = " ".join(full_text)
            if not text.strip():
                return None

            duration = len(audio_array) / self.sample_rate
            segment = TranscriptSegment(
                text=text,
                words=words,
                start=0,
                end=duration,
            )

            self.segment_id += 1
            self.segments.append(segment)

            # Log metrics
            latency = time.time() - start_time
            log_metric(
                "asr_segment",
                segment_id=self.segment_id,
                duration=duration,
                latency=latency,
                word_count=len(words),
            )

            # Reset buffer
            self.buffer = bytes()
            self.last_partial = ""
            self.voiced_frames = 0
            self.silent_frames = 0

            return segment

        except Exception as e:
            logger.error(f"Segment transcription error: {e}")
            return None

    def _bytes_to_array(self, audio_bytes: bytes) -> np.ndarray:
        """Convert PCM16 bytes to numpy array."""
        samples = struct.unpack(f"<{len(audio_bytes)//2}h", audio_bytes)
        return np.array(samples, dtype=np.float32) / 32768.0


def batch_transcribe(audio_path: str, language: str = "en") -> TranscriptSegment:
    """Transcribe an audio file in batch mode."""
    start_time = time.time()
    model = get_whisper_model()

    segments, info = model.transcribe(
        audio_path,
        language=language,
        vad_filter=True,
        word_timestamps=True,
    )

    words = []
    full_text = []

    for seg in segments:
        full_text.append(seg.text.strip())
        if seg.words:
            for w in seg.words:
                words.append(Word(word=w.word.strip(), start=w.start, end=w.end))

    text = " ".join(full_text)
    duration = info.duration if hasattr(info, "duration") else 0

    latency = time.time() - start_time
    log_metric("asr_batch", duration=duration, latency=latency, word_count=len(words))

    return TranscriptSegment(text=text, words=words, start=0, end=duration)


def transcribe_bytes(audio_bytes: bytes, sample_rate: int = 16000, language: str = "en") -> TranscriptSegment:
    """Transcribe audio bytes directly."""
    # Save to temp file for faster-whisper
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        import soundfile as sf

        samples = struct.unpack(f"<{len(audio_bytes)//2}h", audio_bytes)
        audio_array = np.array(samples, dtype=np.float32) / 32768.0
        sf.write(f.name, audio_array, sample_rate)
        result = batch_transcribe(f.name, language)
        Path(f.name).unlink(missing_ok=True)
        return result


# Singleton client wrapper for easier access
class ASRClient:
    """Singleton client wrapper for ASR operations."""
    
    _instance: Optional["ASRClient"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._model = None
    
    @property
    def model(self):
        """Get the Whisper model (lazy load)."""
        if self._model is None:
            self._model = get_whisper_model()
        return self._model
    
    def transcribe(self, audio_path: str, language: str = "en") -> TranscriptSegment:
        """Transcribe an audio file."""
        return batch_transcribe(audio_path, language)
    
    def create_session(self, sample_rate: int = 16000, language: str = "en") -> ASRSession:
        """Create a new streaming ASR session."""
        return ASRSession(sample_rate=sample_rate, language=language)


_asr_client: Optional[ASRClient] = None


def get_asr_client() -> ASRClient:
    """Get the singleton ASR client instance."""
    global _asr_client
    if _asr_client is None:
        _asr_client = ASRClient()
    return _asr_client
