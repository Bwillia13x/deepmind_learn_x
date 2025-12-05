# Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
├──────────────────────┬──────────────────────────────────────────┤
│   Student App        │          Teacher Portal                   │
│   (Flutter)          │          (Next.js)                        │
│   - Live Captions    │          - Text Leveler                   │
│   - Reading Buddy    │          - Dashboard                      │
│   - Vocab Lens       │          - Class Manager                  │
└──────────┬───────────┴────────────────┬─────────────────────────┘
           │                            │
           ▼                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API Gateway (FastAPI)                        │
│  /v1/captions/* | /v1/reading/* | /v1/authoring/*               │
└─────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Service Layer                              │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   ASR Service   │  Simplify/NLP   │     LLM Client              │
│   (faster-      │  (spaCy, rules) │     (local/API)             │
│    whisper)     │                 │                             │
├─────────────────┼─────────────────┼─────────────────────────────┤
│   TTS Service   │  Translation    │     Leveling                │
│   (Piper)       │  (NLLB/dict)    │     (readability)           │
└─────────────────┴─────────────────┴─────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Data Layer                                   │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   PostgreSQL    │     Redis       │       MinIO                  │
│   (pgvector)    │     (cache)     │       (audio/files)          │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

## Components

### Frontend

- **Student App (Flutter)**: Offline-first mobile/desktop app for students
  - Live captions with simplification
  - Reading buddy for ORF practice
  - Vocab lens (AR camera feature)

- **Teacher Portal (Next.js)**: Web dashboard for teachers
  - Text leveling and authoring
  - Class management
  - Progress dashboards

### Backend

- **FastAPI**: Main REST/WebSocket API server
- **ASR Service**: Speech-to-text using faster-whisper
- **Simplify Service**: Rule-based + LLM text simplification
- **Translation Service**: Bilingual glossaries and NLLB translation
- **ORF Service**: Oral reading fluency scoring
- **Leveling Service**: Readability analysis and text rewriting

### Infrastructure

- **PostgreSQL + pgvector**: Primary database with vector support
- **Redis**: Caching for translations, sessions
- **MinIO**: S3-compatible storage for audio files

### Edge Deployment (Optional)

- **Raspberry Pi / Jetson**: Local inference for offline classrooms
- On-device ASR, TTS, and small LLM
