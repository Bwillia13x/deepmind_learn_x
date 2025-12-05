# API Reference

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.ab-esl.ca` (example)

## Authentication

Development uses class codes. Production will use OIDC/OAuth.

## Endpoints

### System

#### GET /health

Service status check.

**Response:**
```json
{
  "status": "ok",
  "features": {
    "enable_asr": true,
    "enable_llm": true
  }
}
```

---

### Captions

#### WS /v1/captions/stream

Live ASR streaming via WebSocket.

**Client → Server Messages:**

Start session:
```json
{
  "type": "start",
  "sample_rate": 16000,
  "lang": "en",
  "save": false,
  "l1": "ar",
  "simplify": 2
}
```

Binary audio: PCM16 LE frames (20-50ms each)

Stop session:
```json
{"type": "stop"}
```

**Server → Client Messages:**

Ready:
```json
{"type": "ready"}
```

Partial transcript:
```json
{
  "type": "partial",
  "text": "open your",
  "ts": [0.0, 0.8]
}
```

Final transcript:
```json
{
  "type": "final",
  "text": "Open your books.",
  "words": [
    {"w": "open", "s": 0.0, "e": 0.3},
    {"w": "your", "s": 0.35, "e": 0.55},
    {"w": "books", "s": 0.6, "e": 0.9}
  ],
  "segment_id": 1
}
```

Error:
```json
{"type": "error", "message": "..."}
```

---

#### POST /v1/captions/simplify

Simplify English text.

**Request:**
```json
{
  "text": "Please ensure that all students have completed their assignments before proceeding.",
  "strength": 2,
  "focus_commands": true
}
```

**Response:**
```json
{
  "simplified": "Make sure all students finished their work.",
  "focus": [
    {"verb": "ensure", "object": "students completed assignments"}
  ],
  "explanations": []
}
```

---

#### POST /v1/captions/gloss

Get translation and vocabulary glossary.

**Request:**
```json
{
  "text": "The fraction represents part of a whole number.",
  "l1": "ar",
  "top_k": 8
}
```

**Response:**
```json
{
  "translation": "الكسر يمثل جزءًا من عدد صحيح.",
  "gloss": [
    {"en": "fraction", "l1": "كسر", "def": "جزء من عدد"},
    {"en": "represents", "l1": "يمثل", "def": "يعني أو يظهر"},
    {"en": "whole number", "l1": "عدد صحيح", "def": "رقم بدون كسور"}
  ]
}
```

---

### Reading

#### POST /v1/reading/score

Calculate reading fluency from word counts.

**Request:**
```json
{
  "words_read": 95,
  "seconds": 60,
  "errors": 8
}
```

**Response:**
```json
{
  "wpm": 95.0,
  "wcpm": 87.0,
  "accuracy": 0.916
}
```

---

#### POST /v1/reading/score_audio

Score reading fluency from uploaded audio.

**Request:** `multipart/form-data`
- `audio_file`: WAV/MP3 audio file
- `reference_text`: (optional) Expected text for accuracy calculation
- `passage_id`: (optional) ID of known passage

**Response:**
```json
{
  "wpm": 92.5,
  "wcpm": 85.0,
  "accuracy": 0.92,
  "errors": [
    {"type": "sub", "ref": "cat", "hyp": "cap", "t": 3.2}
  ],
  "words_timed": [
    {"word": "the", "start": 0.1, "end": 0.2},
    {"word": "cat", "start": 0.25, "end": 0.45}
  ]
}
```

---

#### POST /v1/reading/generate_decodable

Generate phonics-constrained decodable text.

**Request:**
```json
{
  "graphemes": ["m", "s", "a", "t", "p"],
  "length_sentences": 6,
  "word_bank": ["the", "a", "is"]
}
```

**Response:**
```json
{
  "text": "Sam sat. The mat is flat. Pat sat on the mat. Sam and Pat sat. A map is on the mat. Sam has a map."
}
```

---

### Authoring

#### POST /v1/authoring/level-text

Level text to multiple readability targets.

**Request:**
```json
{
  "text": "Photosynthesis is the process by which plants convert light energy into chemical energy...",
  "targets": ["A2", "B1", "Gr5"],
  "l1": "ar"
}
```

**Response:**
```json
{
  "original_score": {
    "cefr": "B2",
    "avg_sentence_length": 18.5,
    "difficult_word_pct": 0.23
  },
  "levels": [
    {
      "target": "A2",
      "text": "Plants make food from sunlight. This is called photosynthesis.",
      "questions": [
        {"type": "literal", "q": "What do plants make?", "a": "food"},
        {"type": "inferential", "q": "Why do plants need sunlight?", "a": "to make food"},
        {"type": "vocabulary", "q": "What does 'photosynthesis' mean?", "a": "how plants make food from light"}
      ],
      "gloss": [
        {"en": "photosynthesis", "l1": "التمثيل الضوئي", "def": "صنع الغذاء من الضوء"}
      ]
    }
  ]
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here",
  "code": "ERROR_CODE"
}
```

Common codes:
- `INVALID_REQUEST`: Malformed request body
- `NOT_FOUND`: Resource not found
- `RATE_LIMITED`: Too many requests
- `SERVICE_UNAVAILABLE`: Backend service down
