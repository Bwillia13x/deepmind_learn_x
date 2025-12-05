You’re right to treat this like an urgent design problem, not just “add another app.” With teacher shortages and a multilingual influx, the win is a stack of AI supports that: 1) run at scale with minimal teacher overhead, 2) work on low-cost devices and poor bandwidth, 3) align to Alberta curriculum/benchmarks, and 4) respect FOIP/data-residency. Below is a buildable, novel set of tools plus a pragmatic rollout plan.

Core idea: a three-layer system
- Student tools that remove language barriers in real time and accelerate literacy.
- Teacher/admin tools that automate differentiation, assessment, and reporting.
- Infrastructure that is offline-first, Canada-hosted, and safe by design.

Student-facing (what kids actually use)
1) Live Captions + Simplifier + L1 overlay (Grades 3–12)
   - What: Real-time subtitles of teacher talk on a student device with a “simplify” slider (turns complex sentences into easier English) plus instant, toggleable first-language translation and key-vocabulary glosses.
   - Why: Cuts cognitive load during mainstream classes so newcomers can follow directions/content from day one.
   - How: On-device streaming ASR (Whisper small/medium quantized) for privacy; a lightweight simplifier model tuned for classroom discourse; translation via cached NLLB/M2M and offline bilingual dictionaries per language. Teacher opt-in mic or a small desk mic hub to capture clean audio.
   - Novel: “Focus mode” highlights commands and task verbs; “Note mode” creates cloze notes automatically; “EL1 contrast tips” show likely transfer errors by L1 (e.g., article use for Arabic speakers).

2) AI Reading Buddy (K–8)
   - What: Voice-first reading coach that listens to a child read decodable or leveled texts, gives immediate feedback on phonics, fluency, and comprehension, and can switch to the student’s L1 for explanations without doing the work for them.
   - Why: Scales individualized practice without a 1:1 adult.
   - How: 
     - Decodable-generator: feed phonics scope/sequence to auto-generate stories constrained to taught graphemes.
     - Pronunciation scoring via CTC-based GOP or wav2vec2 fine-tuned for non-native accents, with prosody metrics (WCPM, pauses).
     - Comprehension chat using a guardrailed LLM (level-aware) with hints not answers.
     - Offline-capable TTS (Piper) and ASR.
   - Novel: “Choral read” mode (student echoes with TTS); “Shadow reading” that gradually fades TTS support; picture-walk automation that pre-teaches vocabulary with visuals.

3) Speaking Coach with Visual Articulation (Grades 2–12)
   - What: Students practice minimal pairs, stress/intonation, and conversation. Optional webcam overlay shows lip/tongue placement guidance for tricky phonemes (processed on-device; no video leaves the device).
   - Why: Accurate feedback on pronunciation is a bottleneck for busy classrooms.
   - How: Forced alignment + articulatory feature detectors; intonation scoring versus native contours; L1-specific modules (e.g., /p/ vs /b/ for speakers of languages without aspiration contrast).
   - Novel: “Confidence filter” that celebrates intelligibility over native-like accent; students can choose goals like “be understood in class presentations.”

4) Writer’s Copilot with Contrastive Feedback (Grades 4–12)
   - What: Guided drafting with sentence frames, vocabulary ladders, and feedback on form and content. Explanations can appear in L1. Gives choices, not corrections, and keeps a teacher-visible change log.
   - Why: Reduces marking time, supports independent writing.
   - How: Level-aware LLM with rubrics embedded (CEFR/Alberta ESL Benchmarks); grammar feedback mapped to likely L1 transfer errors; “show me why” button provides short, bilingual micro-lessons.
   - Novel: “One text, many levels”—students can toggle the complexity of a mentor text to see how writers add detail or cohesion.

5) Vocab Lens (AR + camera)
   - What: Point the camera at classroom or home objects to get English labels, high-frequency collocations, and sentence frames; adds to a personal, spaced-repetition deck with images from the student’s real environment.
   - Why: Vocabulary tied to lived context sticks.
   - How: On-device vision model + bilingual dictionary; SRS scheduler; teacher can push topic packs (fractions, lab equipment, map skills).
   - Novel: Offline packs for field trips or home environments.

6) Newcomer Bridge Micro-lessons (SMS/WhatsApp + app)
   - What: Daily 5-minute bilingual mini-lessons for students and caregivers (school routines, key phrases, literacy games), with audio.
   - Why: Brings families into literacy building using the phone they already have.
   - How: Messaging integration; no login needed beyond a class code; opt-in languages (Arabic, Ukrainian, Tagalog, Punjabi, Mandarin, Somali, Amharic, Tigrinya, Dari/Pashto, Spanish, Vietnamese, etc.).

Teacher/admin tools (scale the adults you do have)
7) ESL Teacher Copilot
   - What: Instantly generates:
     - Leveled texts on any topic at multiple readability bands with aligned vocabulary and comprehension questions.
     - Differentiated tasks for the same content (e.g., Grade 7 science lab write-up at three levels).
     - Parent letters and progress notes translated to L1.
     - Phonics-aligned decodables based on your scope/sequence.
   - How: RAG over a curated pedagogy library and Alberta curriculum; readability classifier (CEFR-like); style guardrails; human-in-the-loop.

8) Rapid Placement + Progress Monitoring
   - What: 30–40 minute intake that profiles listening, speaking, reading, writing; then 5–8 minute fortnightly checks (ORF, MAZE/Cloze, vocabulary, listening). Flags dyslexia risk without diagnosing.
   - How: Short adaptive ASR tasks, leveled passages, dictation; norms built over time; dashboards per class/district with growth over weeks, not just end-of-year.
   - Alignment: Map to Alberta ESL Proficiency Benchmarks and K–6 English Language Arts and Literature outcomes; optionally to CEFR bands for secondary.

9) Class Orals Manager
   - What: In a class of 30, run parallel small-group speaking tasks with AI “paraeducators” monitoring accuracy, participation, and turn-taking on shared tablets/Chromebooks. Auto-logs evidence with audio snippets.
   - Why: Converts “dead air” into productive oral language practice without extra adults.

10) “One Text, Five Levels” Authoring
   - What: Paste any article/excerpt and auto-generate five readability levels with teacher controls for target features (relative clauses, cohesive devices), plus bilingual glossaries per L1.
   - Why: Lets ELLs access the same content as peers.

Infrastructure and guardrails
- Offline-first delivery
  - PWA or Flutter app with local caching.
  - On-device models: Whisper-small/int8 for ASR, Piper for TTS, a 3–8B instruction-tuned LLM quantized via GGUF for basic scaffolding; server fallback for heavy tasks.
  - School “edge box” option (Jetson/RPi5) to host models locally for a lab or classroom with no cloud dependency.

- Privacy, FOIP/PIPA, and data residency
  - Default: host in Canada (e.g., AWS ca-central-1, GCP Montréal).
  - Audio/video process on-device by default; if uploaded (with consent) for scoring, anonymize and store transiently with 24–72h retention.
  - Minimal PII: student ID, L1, grade band; no biometric templates stored.
  - Admin controls to disable translation for assessments, lock prompts, and export/delete data.

- Equity and access
  - Works on Chromebooks and low-end Android/iOS.
  - Low bandwidth modes; download language packs over Wi‑Fi.
  - Accessibility: dyslexia-friendly fonts, color contrast, captions.

- Safety
  - Age-appropriate response filters; content whitelists; audit trails for admin.
  - “Explain, don’t do” heuristics for writing support.

Technical blueprint (buildable with a small team)
- Frontend: Flutter (mobile/desktop) or React PWA + WebAssembly for on-device inference (onnxruntime-web or WebGPU).
- Realtime audio: WebRTC + VAD; echo cancellation for classroom noise.
- ASR: OpenAI Whisper small/medium distilled/quantized; streaming segmentation; accent augmentation in fine-tuning using public L2 corpora.
- TTS: rhasspy/piper or Azure Neural (if cloud allowed) with caching.
- LLM: Llama 3.1 8B or Qwen 7B instruct for on-device/edge; server-side larger model for teacher-authoring; RAG over Alberta curriculum docs and your text bank.
- Pronunciation: wav2vec2-CTC or Kaldi GOP pipeline; forced alignment for per-phoneme error highlighting.
- Readability + leveling: transformer-based CEFR classifier + classic readability metrics; frequency lists (COCA/NGSL) for vocabulary staging.
- Data: Postgres; pgvector for embeddings; event pipeline to BigQuery/Snowflake optional; analytics dashboards via Metabase/Redash.
- Integrations: Google Classroom/Microsoft 365 for rostering; SSO via OAuth/OpenID; SIS adapters (e.g., PowerSchool export).

Novel program elements (beyond typical apps)
- Real-time classroom “Simplify + Translate” layer that coexists with mainstream instruction.
- L1-specific contrastive teaching embedded everywhere (not just generic grammar correction).
- Authoring pipeline that lets any teacher turn their content into five levels with bilingual supports in minutes.
- Visual articulation coach with privacy-first on-device processing.
- Community mode: library and settlement-agency kiosks with offline packs, ensuring learning continues beyond school.

Alignment to Alberta context
- Curriculum: Map literacy targets to Alberta’s K–6 English Language Arts and Literature and secondary ELA outcomes; tie content to Canadian contexts (weather, provinces, Indigenous perspectives with care and consultation).
- Benchmarks: Use Alberta ESL Proficiency Benchmarks for reporting; optionally crosswalk to CEFR A1–B2 to leverage existing L2 research.
- Assessments: Track WCPM, accuracy, retell quality, MAZE/Cloze, and writing rubric scores; prepare for Provincial Achievement Tests by building academic vocabulary and comprehension for content areas (science/social).

Rollout and measurement plan
- Phase 0 (4 weeks): Co-design with 2–3 divisions (e.g., one urban, one rural). Identify target grades, languages, device inventory, consent requirements.
- Phase 1 MVP (12 weeks):
  - Build Live Captions + Simplifier (English + top 6 L1s).
  - Build Reading Buddy with decodable generator and ORF measures.
  - Build Teacher Copilot (leveled texts + bilingual glossaries).
  - Pilot with ~300 students across 10 classrooms.
  - Metrics: adoption, minutes of use/week, WCPM gain (aim +20–30), MAZE gain, student/teacher satisfaction, reduction in translation load on teachers.
- Phase 2 (3–6 months):
  - Speaking Coach, Class Orals Manager, rapid placement, dashboards, WhatsApp family packs.
  - Expand L1 coverage to top 12 languages.
  - Quasi-experimental evaluation vs. matched classrooms; aim for 0.3–0.5 SD effect on reading fluency and vocabulary over one term.
- Phase 3 (year 1):
  - Edge boxes for bandwidth-poor schools; content partnerships; RCT if feasible.

Costing rough order (build + run, first 6–9 months)
- Team: 1 PM, 2–3 full-stack/ML engineers, 1 ASR/Signal specialist, 1 curriculum designer, 0.5 privacy/compliance, 1 QA. Add 1–2 part-time ELL educators for prompt/content tuning.
- Cloud: If most inference is on-device/edge, per-student cost can be <$1/month at scale; teacher authoring and analytics add pennies per request. Canada data residency adds modest premium.
- Hardware: Optional $80–$150 per “edge box” per classroom; otherwise use existing Chromebooks/iPads.

Sustainability and trust
- Offer a free core (Captions, basic Reading Buddy) to maximize reach; premium for advanced analytics/authoring.
- Open-source key components (e.g., decodable generator, readability classifier) to build trust with districts and enable community contributions.
- Advisory circle with Alberta ELL leads and newcomer organizations to keep content culturally responsive.

What we need from you to scope v1
- Grade bands and settings to prioritize (e.g., Grades 3–6 mainstream; Grade 9 newcomers).
- Top L1s in your target divisions and whether you want L1 overlays on by default.
- Device mix and bandwidth constraints (Chromebooks vs. iPads; home access).
- District policies on audio capture and translation tools (for FOIP consent design).
- Your phonics scope/sequence and any required curriculum tie-ins.

If helpful, I can sketch a sprint plan and starter repos for:
- Live captions pipeline (WebRTC + onnxruntime-web Whisper streaming).
- Decodable text generator (phonics-aware constrained decoding).
- Readability/leveling microservice with a simple REST API.
- Teacher Copilot prompt+RAG templates aligned to Alberta outcomes.

Where would you like to start: the real-time classroom Simplifier, the Reading Buddy, or the Teacher Copilot?

Below is a pragmatic monorepo scaffold you can drop into your IDE and start building. It’s set up for Phase 1 features (Live Captions + Simplifier, Reading Buddy, Teacher Copilot), with room to grow. It includes a FastAPI backend, placeholders for a Flutter student app and a Next.js teacher portal, local infra (Postgres/pgvector, Redis, MinIO), and edge-box stubs.

Directory overview
ab-esl-ai/
  apps/
    student-app/              # Flutter app (student-facing). Placeholder with README; use flutter create
    teacher-portal/           # Next.js app (teacher/admin). Placeholder with README; use create-next-app
  backend/
    api/
      app/
        __init__.py
        main.py               # FastAPI entrypoint with health route + CORS
        core/
          config.py           # Env config loading
          logging.py
        routers/
          __init__.py
          health.py
          v1/
            __init__.py
            captions.py       # stub: live captions endpoints
            reading.py        # stub: reading buddy endpoints
            authoring.py      # stub: teacher copilot endpoints
        services/
          __init__.py
          storage.py          # MinIO/S3 wrapper
          cache.py            # Redis wrapper
          db.py               # Postgres session
          llm_client.py       # LLM calls stub
          asr_client.py       # ASR calls stub
          tts_client.py       # TTS calls stub
        schemas/
          __init__.py
          common.py
      requirements.txt
      Dockerfile
      .env.example
  ml/
    asr-service/              # Python microservice stubs for on-edge/cloud inference
      service/
        main.py
      requirements.txt
      Dockerfile
    llm-service/
      service/
        main.py
      requirements.txt
      Dockerfile
    tts-service/
      service/
        main.py
      requirements.txt
      Dockerfile
    README.md
  packages/
    ts/
      api-client/
        package.json          # Generated API client (OpenAPI) placeholder
        src/index.ts
      ui-kit/
        package.json          # Shared React UI components placeholder
        src/index.ts
    py/
      shared/
        pyproject.toml        # Shared Python helpers placeholder
        shared/__init__.py
  infra/
    docker/
      postgres/
        init.sql
    k8s/
      base/                   # K8s stubs for later
      overlays/dev/
    terraform/                # Cloud IaC stubs for later (CA region)
  edge-box/
    rpi/
      docker-compose.yml      # Run on-device ASR/TTS/LLM locally
      README.md
    jetson/
      docker-compose.yml
      README.md
  content/
    curriculum/
    prompts/
    language-packs/
    decodables/
    glossaries/
  data/
    seeds/
    samples/
  scripts/
    dev.sh
    seed_db.sh
    fmt.sh
  docs/
    architecture.md
    api.md
    privacy-foip.md
    roadmap.md
    onboarding.md
  .github/
    workflows/
      ci.yml
  .env.example
  docker-compose.yml
  Makefile
  .gitignore
  README.md
  .editorconfig
  .vscode/settings.json

One-shot scaffold script
- Save this as scaffold.sh in an empty directory and run: bash scaffold.sh ab-esl-ai
- It creates the tree above plus minimal runnable backend and local infra.

#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-ab-esl-ai}"
mkdir -p "$REPO"
cd "$REPO"

# Root files
cat > .gitignore <<'EOF'
# Node
node_modules/
pnpm-lock.yaml
yarn.lock
.next/
dist/
# Python
.venv/
__pycache__/
*.pyc
.env
# Flutter
build/
.dart_tool/
.flutter-plugins
.flutter-plugins-dependencies
.packages
# OS/IDE
.DS_Store
.idea/
.vscode/*
!.vscode/settings.json
# Models/large assets
models/
checkpoints/
EOF

cat > .editorconfig <<'EOF'
root = true
[*]
end_of_line = lf
insert_final_newline = true
charset = utf-8
indent_style = space
indent_size = 2
EOF

mkdir -p .vscode
cat > .vscode/settings.json <<'EOF'
{
  "editor.formatOnSave": true,
  "[python]": { "editor.defaultFormatter": "ms-python.black-formatter" },
  "python.analysis.typeCheckingMode": "basic"
}
EOF

cat > .env.example <<'EOF'
# Local services
POSTGRES_USER=dev
POSTGRES_PASSWORD=devpass
POSTGRES_DB=ab_esl_ai
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://dev:devpass@localhost:5432/ab_esl_ai

REDIS_URL=redis://localhost:6379/0

MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=ab-esl

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
EOF

cat > docker-compose.yml <<'EOF'
version: "3.9"
services:
  db:
    image: pgvector/pgvector:pg16
    container_name: ab_esl_db
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-dev}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-devpass}
      POSTGRES_DB: ${POSTGRES_DB:-ab_esl_ai}
    ports: ["5432:5432"]
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./infra/docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro

  redis:
    image: redis:7
    container_name: ab_esl_redis
    ports: ["6379:6379"]

  minio:
    image: minio/minio:latest
    container_name: ab_esl_minio
    environment:
      MINIO_ROOT_USER: ${MINIO_ACCESS_KEY:-minioadmin}
      MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY:-minioadmin}
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

volumes:
  db_data:
  minio_data:
EOF

cat > Makefile <<'EOF'
.PHONY: up down api install-api seed fmt

up:
\tdocker compose up -d

down:
\tdocker compose down -v

install-api:
\tpython3 -m venv backend/api/.venv
\tbackend/api/.venv/bin/pip install --upgrade pip
\tbackend/api/.venv/bin/pip install -r backend/api/requirements.txt

api:
\tBACKEND_ENV=.env backend/api/.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend/api

seed:
\tbash scripts/seed_db.sh

fmt:
\tbash scripts/fmt.sh
EOF

cat > README.md <<'EOF'
# Alberta ESL AI Monorepo

Phase 1: Live Captions + Simplifier, Reading Buddy, Teacher Copilot.

Quickstart
1) cp .env.example .env
2) make up
3) make install-api
4) make api
API runs at http://localhost:8000 (health: /health)

Apps
- Student app (Flutter): run `flutter create apps/student-app` (see apps/student-app/README.md).
- Teacher portal (Next.js): run `npx create-next-app apps/teacher-portal --ts` (see apps/teacher-portal/README.md).

Infra
- Postgres (pgvector): localhost:5432
- Redis: localhost:6379
- MinIO: S3-compatible at localhost:9000 (console at 9001)

Docs: see docs/architecture.md and docs/privacy-foip.md
EOF

# Infra stubs
mkdir -p infra/docker/postgres infra/k8s/base infra/k8s/overlays/dev infra/terraform
cat > infra/docker/postgres/init.sql <<'EOF'
CREATE EXTENSION IF NOT EXISTS vector;
EOF

# Scripts
mkdir -p scripts
cat > scripts/dev.sh <<'EOF'
#!/usr/bin/env bash
set -e
export $(grep -v '^#' .env | xargs)
make up
make api
EOF
chmod +x scripts/dev.sh

cat > scripts/seed_db.sh <<'EOF'
#!/usr/bin/env bash
set -e
echo "Seeding DB ... (add your SQL or Python seeders here)"
EOF
chmod +x scripts/seed_db.sh

cat > scripts/fmt.sh <<'EOF'
#!/usr/bin/env bash
set -e
echo "Formatting Python..."
backend/api/.venv/bin/python -m pip install black isort >/dev/null 2>&1 || true
backend/api/.venv/bin/black backend/api
backend/api/.venv/bin/isort backend/api
EOF
chmod +x scripts/fmt.sh

# Docs
mkdir -p docs
cat > docs/architecture.md <<'EOF'
High-level:
- apps/student-app (Flutter): offline-first learning tools
- apps/teacher-portal (Next.js): authoring, dashboards
- backend/api (FastAPI): REST/WebSocket + RAG + scoring
- ml/* services: optional separate inference endpoints
- infra: Postgres+pgvector, Redis, MinIO; edge-box for on-prem
EOF

cat > docs/privacy-foip.md <<'EOF'
Data handling principles (draft):
- Default to on-device processing; minimize PII (ID, grade, L1).
- Host in Canada for cloud workloads.
- Audio/video processed locally when possible; if uploaded, anonymize and set short retention.
- Provide admin export/delete and audit trails.
EOF

cat > docs/api.md <<'EOF'
- GET /health: service status
- WS /v1/captions/stream: (stub) live ASR
- POST /v1/reading/score: (stub) compute ORF/WCPM
- POST /v1/authoring/level-text: (stub) readability leveling
EOF

# GitHub Actions
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'EOF'
name: CI
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r backend/api/requirements.txt
      - run: python -m compileall backend/api
EOF

# Apps
mkdir -p apps/student-app apps/teacher-portal
cat > apps/student-app/README.md <<'EOF'
Run:
  flutter create .
  flutter run
Feature modules to add:
  - captions (ASR + simplify)
  - reading_buddy
  - vocab_lens
EOF

cat > apps/teacher-portal/README.md <<'EOF'
Run:
  npx create-next-app@latest . --ts
Then configure env to call http://localhost:8000
EOF

# Backend FastAPI service
mkdir -p backend/api/app/{core,routers/v1,services,schemas}
cat > backend/api/requirements.txt <<'EOF'
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.8.2
pydantic-settings==2.4.0
orjson==3.10.7
sqlalchemy==2.0.35
psycopg[binary]==3.2.3
redis==5.0.7
boto3==1.35.21
httpx==0.27.2
loguru==0.7.2
python-dotenv==1.0.1
EOF

cat > backend/api/Dockerfile <<'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > backend/api/app/__init__.py <<'EOF'
__all__ = []
EOF

cat > backend/api/app/core/config.py <<'EOF'
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    app_name: str = "Alberta ESL AI API"
    cors_origins: List[str] = ["http://localhost:3000"]
    database_url: str = "postgresql+psycopg://dev:devpass@localhost:5432/ab_esl_ai"
    redis_url: str = "redis://localhost:6379/0"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "ab-esl"

    class Config:
        env_file = ".env"

settings = Settings()
EOF

cat > backend/api/app/core/logging.py <<'EOF'
from loguru import logger
logger.add("logs/app.log", rotation="5 MB", retention="7 days", level="INFO")
EOF

cat > backend/api/app/routers/__init__.py <<'EOF'
from fastapi import APIRouter
from .health import router as health_router
from .v1.captions import router as captions_router
from .v1.reading import router as reading_router
from .v1.authoring import router as authoring_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["system"])
api_router.include_router(captions_router, prefix="/v1/captions", tags=["captions"])
api_router.include_router(reading_router, prefix="/v1/reading", tags=["reading"])
api_router.include_router(authoring_router, prefix="/v1/authoring", tags=["authoring"])
EOF

cat > backend/api/app/routers/health.py <<'EOF'
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}
EOF

cat > backend/api/app/routers/v1/__init__.py <<'EOF'
# v1 API namespace
EOF

cat > backend/api/app/routers/v1/captions.py <<'EOF'
from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/stream")
async def stream_captions(ws: WebSocket):
    await ws.accept()
    await ws.send_json({"message": "ASR stream stub: send audio chunks here"})
    await ws.close()
EOF

cat > backend/api/app/routers/v1/reading.py <<'EOF'
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ReadingScoreIn(BaseModel):
    words_read: int
    seconds: int
    errors: int = 0

@router.post("/score")
def score_reading(payload: ReadingScoreIn):
    wpm = (payload.words_read / max(payload.seconds, 1)) * 60.0
    accuracy = max(0.0, 1.0 - payload.errors / max(payload.words_read, 1))
    return {"wpm": round(wpm, 1), "accuracy": round(accuracy, 3)}
EOF

cat > backend/api/app/routers/v1/authoring.py <<'EOF'
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class LevelTextIn(BaseModel):
    text: str
    target_level: str  # e.g., "A2","B1","Gr4"

@router.post("/level-text")
def level_text(payload: LevelTextIn):
    # Stub: replace with real readability/CEFR leveling
    return {"level": payload.target_level, "text": payload.text}
EOF

cat > backend/api/app/services/__init__.py <<'EOF'
# service clients init
EOF

cat > backend/api/app/services/storage.py <<'EOF'
from typing import Optional
import boto3
from app.core.config import settings

def get_minio_client():
    return boto3.client(
        "s3",
        endpoint_url=f"http://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
    )

def ensure_bucket(name: Optional[str] = None):
    s3 = get_minio_client()
    bucket = name or settings.minio_bucket
    existing = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    if bucket not in existing:
        s3.create_bucket(Bucket=bucket)
    return bucket
EOF

cat > backend/api/app/services/cache.py <<'EOF'
import redis
from app.core.config import settings

redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
EOF

mkdir -p backend/api/app/schemas
cat > backend/api/app/schemas/__init__.py <<'EOF'
# pydantic schemas
EOF

cat > backend/api/app/schemas/common.py <<'EOF'
from pydantic import BaseModel

class Message(BaseModel):
    message: str
EOF

cat > backend/api/app/main.py <<'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import api_router

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
EOF

# ML service stubs
mkdir -p ml/asr-service/service ml/llm-service/service ml/tts-service/service
cat > ml/README.md <<'EOF'
ML services are optional standalone inference endpoints (ASR/LLM/TTS).
For local dev, keep most inference on-device or in the main API.
EOF

for svc in asr llm tts; do
  cat > ml/${svc}-service/requirements.txt <<'EOF'
fastapi
uvicorn[standard]
EOF
  cat > ml/${svc}-service/service/main.py <<'EOF'
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
EOF
  cat > ml/${svc}-service/Dockerfile <<'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY service ./service
EXPOSE 8000
CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
done

# Packages stubs
mkdir -p packages/ts/api-client/src packages/ts/ui-kit/src packages/py/shared/shared
cat > packages/ts/api-client/package.json <<'EOF'
{
  "name": "@ab-esl/api-client",
  "version": "0.0.1",
  "type": "module",
  "main": "dist/index.js",
  "scripts": { "build": "tsc -p ." },
  "devDependencies": { "typescript": "^5.6.2" }
}
EOF
cat > packages/ts/api-client/src/index.ts <<'EOF'
// Placeholder: generate from backend OpenAPI later
export const hello = () => "api-client";
EOF

cat > packages/ts/ui-kit/package.json <<'EOF'
{
  "name": "@ab-esl/ui-kit",
  "version": "0.0.1",
  "type": "module",
  "main": "dist/index.js",
  "scripts": { "build": "tsc -p ." },
  "devDependencies": { "typescript": "^5.6.2" }
}
EOF
cat > packages/ts/ui-kit/src/index.ts <<'EOF'
// Placeholder for shared React components
export {};
EOF

cat > packages/py/shared/pyproject.toml <<'EOF'
[project]
name = "ab_shared"
version = "0.0.1"
requires-python = ">=3.11"
dependencies = []
[tool.setuptools.packages.find]
where = ["."]
EOF
cat > packages/py/shared/shared/__init__.py <<'EOF'
__all__ = []
EOF

# Edge-box stubs
mkdir -p edge-box/rpi edge-box/jetson
cat > edge-box/rpi/docker-compose.yml <<'EOF'
version: "3.9"
services:
  asr:
    image: your-asr-image-arm
    restart: unless-stopped
  tts:
    image: your-tts-image-arm
    restart: unless-stopped
  llm:
    image: your-llm-image-arm
    restart: unless-stopped
EOF
cat > edge-box/rpi/README.md <<'EOF'
Raspberry Pi edge stack (ARM). Build or pull ARM images for ASR/TTS/LLM.
EOF
cat > edge-box/jetson/docker-compose.yml <<'EOF'
version: "3.9"
services:
  asr:
    image: your-asr-image-jetson
    runtime: nvidia
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
  tts:
    image: your-tts-image-jetson
  llm:
    image: your-llm-image-jetson
EOF
cat > edge-box/jetson/README.md <<'EOF'
Jetson edge stack with GPU acceleration (ASR/TTS/LLM).
EOF

# Content and data
mkdir -p content/{curriculum,prompts,language-packs,decodables,glossaries} data/{seeds,samples}
touch content/prompts/.keep data/seeds/.keep

echo "Scaffold created in $(pwd)"

Done.

How to use
1) Run the scaffold
- Save scaffold.sh and run: bash scaffold.sh ab-esl-ai
- cd ab-esl-ai
- cp .env.example .env

2) Start local infra and backend
- make up
- make install-api
- make api
- Open http://localhost:8000/health -> {"status":"ok"}

3) Bootstrap the apps
- Student app (Flutter)
  - cd apps/student-app
  - flutter create .
  - flutter run
- Teacher portal (Next.js)
  - cd apps/teacher-portal
  - npx create-next-app@latest . --ts
  - Start it (npm run dev) and call the backend at http://localhost:8000

4) Next steps
- Wire /v1/captions/stream to a streaming ASR (e.g., Whisper small int8) via WebRTC or WS.
- Implement reading ORF scoring and decodable generation in backend/app/routers/v1/reading.py.
- Add a RAG/readability module to authoring.py and generate an OpenAPI spec to feed packages/ts/api-client.
- Decide on auth (local dev with session tokens; production via OIDC). Add an auth router later.
- Set FOIP defaults in docs/privacy-foip.md and ensure on-device options before uploading audio.

If you want this scaffold trimmed to a different stack (e.g., all-in-React PWA, or no Flutter), tell me your preferences and I’ll regenerate it.

Here’s a concrete, step-by-step implementation plan your agentic programmer can follow in the IDE to deliver Phase 1 features (Live Captions + Simplifier, Reading Buddy, Teacher Copilot) using the scaffold you already have. It’s organized as executable tickets with dependencies, file paths to touch, API contracts, pseudocode, test steps, and definitions of done. You can paste these tickets into your tracker or feed them sequentially to an autonomous coding agent.

Scope and priorities
- Priority 1: Live Captions + Simplifier (student app + backend WS + simplify/translate)
- Priority 2: Reading Buddy (ORF/WCPM, decodable generator, basic feedback)
- Priority 3: Teacher Copilot (Level a text, bilingual glossary, questions)
- Cross-cutting: Privacy defaults, local infra, CI, logging, telemetry

Pre-flight setup (once)
- Ensure docker, Python 3.11, Node 18+, Flutter SDK installed
- Repo: use the provided ab-esl-ai scaffold
- Commands:
  - cp .env.example .env
  - make up
  - make install-api
  - make api
  - curl http://localhost:8000/health -> {"status":"ok"}

Conventions
- Python: FastAPI, pydantic v2, loguru logging
- Frontend student app: Flutter with a modular feature folder structure
- Frontend teacher portal: Next.js/React TS
- Streaming: WebSocket (simple to start); plan WebRTC later
- ASR: Start with server-hosted Whisper small (whisperx/whisper.cpp binding or faster-whisper); later move to edge/on-device
- Simplifier: Rule-based + small LLM fallback (server) with guardrails
- Translation: Start with cloud-free offline dictionaries + NLLB small via server; cache results
- Data residency: Only store non-PII and transcripts if “save” is explicitly set

Ticket 0: Dev ergonomics and safety rails
- Description: Set up logging, error handling, CORS, .env, and a simple feature flag system.
- Files: backend/api/app/core/config.py, backend/api/app/core/logging.py, backend/api/app/main.py
- Add to Settings:
  - feature flags: enable_asr, enable_llm, save_audio_by_default=False
  - environment: dev|staging|prod
- Acceptance:
  - GET /health returns ok
  - Logs written to logs/app.log
  - Feature flags available via /health (for dev)

Ticket 1: WebSocket ASR API skeleton
- Description: Replace stub /v1/captions/stream with a binary-friendly WS protocol that accepts 16kHz PCM16 chunks and emits partial/final transcripts.
- Files:
  - backend/api/app/routers/v1/captions.py
  - backend/api/app/services/asr_client.py (implement)
- WS message protocol:
  - Client -> server
    - {"type":"start","sample_rate":16000,"lang":"en"}
    - Binary messages of PCM16 LE audio frames (e.g., 20–50 ms per frame)
    - {"type":"stop"}
  - Server -> client
    - {"type":"ready"}
    - {"type":"partial","text":"...","ts":[start,end]}
    - {"type":"final","text":"...","words":[{"w":"go","s":0.24,"e":0.35}], "segment_id": n}
    - {"type":"error","message":"..."}
- Server behavior:
  - Accept WS, send ready
  - Buffer incoming PCM, run VAD + incremental ASR decode
  - Emit partial captions every ~300–600ms, final on VAD endpoint or stop
- Pseudocode:
  - on start: init ASR session = asr_client.create_session(sr)
  - on binary audio: asr_session.feed(bytes); if asr_session.has_partial(): send partial
  - on VAD endpoint: text, words = asr_session.flush_segment(); send final
  - on stop: flush remaining and close
- Acceptance:
  - Local WS echo test: sends a small prerecorded wave and receives partial/final messages
  - Handles 20 concurrent connections

Ticket 2: ASR engine integration (faster-whisper)
- Description: Implement asr_client with faster-whisper streaming, basic VAD, punctuation.
- Files:
  - backend/api/app/services/asr_client.py
  - requirements: add faster-whisper, numpy, webrtcvad, soundfile
- Implementation notes:
  - Use webrtcvad for endpoints; frame size 20ms
  - Use faster-whisper model="small" or "distil-small.en", compute_type="int8"
  - Segment-level decode every ~1–2 seconds or on VAD endpoint
  - Keep per-session state in a Python object keyed by WS connection
- Acceptance:
  - 1-hour soak test across 5 streams, CPU < 200% on dev box, latency < 800ms for partials

Ticket 3: Simplify endpoint + service
- Description: Provide a REST endpoint to simplify English sentences to easier English with a strength 0–3. Start with a composable rule-based approach and optional LLM fallback.
- Files:
  - backend/api/app/routers/v1/captions.py (add REST /simplify)
  - backend/api/app/services/llm_client.py (stub fallback)
  - backend/api/app/services/simplify.py (new)
- API:
  - POST /v1/captions/simplify { "text": "…", "strength": 0..3, "focus_commands": true }
  - Response: { "simplified": "…", "focus": [{"verb":"open","object":"book"}], "explanations": [] }
- Logic:
  - Sentence split; for each sentence:
    - Shorten clauses, active voice heuristics, replace low-frequency words with higher-frequency synonyms (use NGSL list in content/glossaries)
    - Limit sentence length to threshold based on strength
  - Extract focus commands: imperative verb detection (POS tagging; simple spaCy small)
  - Optional: if strength=3 and len(text)>200, call llm_client.simplify_guardrailed()
- Acceptance:
  - Given complex classroom directives, returns shorter sentences and detects commands
  - Round-trip < 200ms for 30-word input without LLM

Ticket 4: Translate + glossary endpoint (MVP)
- Description: Provide bilingual glossing for top L1s and sentence-level translation using cached NLLB server or dictionary fallback.
- Files:
  - backend/api/app/routers/v1/captions.py (add /gloss)
  - backend/api/app/services/translate.py (new)
  - content/glossaries/{lang}.json (seed small dictionaries)
- API:
  - POST /v1/captions/gloss { "text":"…", "l1":"ar", "top_k":8 }
  - Response: { "translation":"…", "gloss":[{"en":"fraction","l1":"…","def":"…"}] }
- Acceptance:
  - For 10 classroom words, returns plausible L1 glosses and an approximate sentence translation
  - Response cached in Redis

Ticket 5: Student app captions UI (Flutter)
- Description: Implement a Captions screen with: connect/disconnect, captions area, partial/final rendering, simplify slider, L1 toggle, focus chips.
- Files:
  - apps/student-app/lib/features/captions/*
- Components:
  - WebSocket manager
  - Audio recorder (16kHz mono PCM)
  - CaptionsView with:
    - Live text area (partial in gray, final in black)
    - Slider 0–3 for simplify
    - Toggle L1; when on, call /gloss in background and show gloss popovers
    - Focus chips updated from /simplify
- Acceptance:
  - On desktop/mobile, streaming works for built-in mic
  - Slider updates simplified view within 300ms for last sentence
  - Toggle L1 shows translations/gloss

Ticket 6: Backend persistence for transcripts (opt-in)
- Description: Persist final segments if save=true, with minimal PII.
- Files:
  - backend/api/app/services/db.py (implement SQLAlchemy engine)
  - backend/api/app/models.py (new)
  - migrations optional
- Tables:
  - transcripts(id, session_id, user_id, ts_start, ts_end, text, words jsonb)
- Acceptance:
  - POST /v1/captions/save with a payload stores records; export endpoint returns CSV for a session
  - Default does not save unless save=true in WS start event

Ticket 7: Reading Buddy API: upload audio and compute ORF
- Description: Add endpoint to accept an audio recording for a known passage or free read, compute WPM, accuracy, error types if reference provided.
- Files:
  - backend/api/app/routers/v1/reading.py (extend)
  - backend/api/app/services/orf.py (new)
  - backend/api/app/services/asr_client.py (batch decode function)
- API:
  - POST /v1/reading/score_audio form-data: audio_file, passage_id?, reference_text?
  - Response: { "wpm": 92.5, "wcpm": 85.0, "accuracy": 0.92, "errors": [{"type":"sub","ref":"cat","hyp":"cap","t":3.2}], "words_timed":[...] }
- Logic:
  - Transcribe audio to words with timestamps
  - If reference_text provided:
    - Normalize both (lowercase, strip punctuation)
    - Align with Levenshtein on token list to count subs/del/ins
    - Compute WPM = words_read*60/seconds; WCPM = (words_read-errors)*60/seconds
  - Else:
    - WPM = hyp_word_count*60/seconds; accuracy null
- Acceptance:
  - Unit tests with synthetic audio or stubbed transcripts match expected ORF metrics

Ticket 8: Reading Buddy decodable generator (MVP)
- Description: Generate decodable texts constrained to taught graphemes and a target length; fall back to templated patterns if no LLM.
- Files:
  - backend/api/app/routers/v1/reading.py (add /generate_decodable)
  - backend/api/app/services/decodable.py (new)
  - content/decodables/scope_sequence.json (phonics scope)
- API:
  - POST /v1/reading/generate_decodable { "graphemes":["m","s","a","t"], "length_sentences":6, "word_bank":[] }
  - Response: { "text":"Sam sat. ..." }
- Logic:
  - Hard-constraint generator:
    - Build syllable patterns from graphemes
    - Use small wordlist allowed by graphemes; few high-frequency sight words
    - Assemble sentences with simple templates
  - Optional: llm_client.generate_decodable with rejection sampling filter
- Acceptance:
  - Generated text only uses allowed graphemes plus whitelisted sight words
  - 6–10 sentences within 1–2s

Ticket 9: Reading Buddy UI (Flutter)
- Description: Implement a Reading Buddy screen: pick passage/decodable, record reading, playback, upload for scoring, display WPM/WCPM and feedback.
- Files:
  - apps/student-app/lib/features/reading_buddy/*
- Components:
  - Passage selector; call /generate_decodable or list from content
  - Recorder with level meter; 1-tap upload; progress spinner
  - Results view: WPM, WCPM, accuracy, error highlights; “Try again” button
- Acceptance:
  - A test passage flow end-to-end works; results update within 3–5s

Ticket 10: Teacher Copilot: Level text endpoint
- Description: Implement readability scoring and rewriting to target levels A1–B2 or Gr2–Gr10 readability bands; generate 3–5 comprehension questions and glossary.
- Files:
  - backend/api/app/routers/v1/authoring.py (replace stub)
  - backend/api/app/services/leveling.py (new)
  - backend/api/app/services/llm_client.py (extend)
  - content/glossaries/frequency_lists.json
- API:
  - POST /v1/authoring/level-text { "text":"…", "targets":["A2","B1","Gr5"], "l1":"ar" }
  - Response: { "levels":[{"target":"A2","text":"…","questions":[...],"gloss":[...]}] }
- Logic:
  - Score original text: sentence length, word frequency, CEFR classifier (lightweight)
  - For each target:
    - Rewrite heuristics + LLM rewrite with instructions and guardrails
    - Generate 3 Qs: 1 literal, 1 inferential, 1 vocabulary
    - Build glossary: top 8–12 difficult words with L1 gloss
- Acceptance:
  - Produces 2+ target levels with decreasing complexity; no hallucinated facts
  - Average latency under 6s on dev

Ticket 11: Teacher portal MVP page
- Description: Add a simple Next.js page to paste text, select target levels, and preview outputs.
- Files:
  - apps/teacher-portal/pages/leveler.tsx (or app/leveler/page.tsx if app router)
  - packages/ts/api-client (add functions for authoring API)
- Acceptance:
  - Paste in text, select A2/B1, click Generate, shows leveled outputs and allows copy/download JSON

Ticket 12: Focus mode extraction improvements
- Description: Improve imperative detection with POS tagging and heuristics for classroom directives (verbs like “open, turn, write”).
- Files:
  - backend/api/app/services/simplify.py
  - Add spaCy small en model; cache lemmatizer
- Acceptance:
  - Given “Everyone, please open your notebooks and write the date,” returns focus_commands: open notebook; write date

Ticket 13: Basic auth and class sessions (dev)
- Description: Lightweight auth for dev with class code and device nickname; later replace with OIDC.
- Files:
  - backend/api/app/routers/auth.py (new)
  - backend/api/app/models.py (User, ClassSession)
  - teacher portal add a page to create class code
  - student app add simple login screen
- Acceptance:
  - Students enter class code and name; backend issues a short-lived token used in WS start; token includes class_session_id

Ticket 14: Privacy flags and admin controls
- Description: Add per-session flags for save_audio, save_transcripts, l1_enabled; default off.
- Files:
  - backend/api/app/core/config.py (defaults)
  - WS start payload, backend enforcement
- Acceptance:
  - If save_transcripts=false, no DB writes occur when streaming captions

Ticket 15: Telemetry and logging
- Description: Add minimal telemetry for latency, ASR partial frequency, simplify calls, reading scores; export as JSONL for analysis.
- Files:
  - backend/api/app/middleware/metrics.py (new)
  - Log schema: metrics/*.jsonl files
- Acceptance:
  - Metrics lines appear; can compute median partial latency and 95th percentile

Ticket 16: Content ingestion
- Description: Seed frequency lists, glossaries, phonics scope, sample passages.
- Files:
  - content/glossaries/*.json
  - content/decodables/scope_sequence.json
  - data/seeds/
  - scripts/seed_db.sh
- Acceptance:
  - Running seed script loads content and can be used by services

Ticket 17: CI updates and unit tests
- Description: Add pytest, test endpoints, and a basic TS lint for teacher portal.
- Files:
  - backend/api/requirements.txt (pytest, httpx[cli], pytest-asyncio)
  - backend/api/tests/test_health.py, test_simplify.py, test_reading_orf.py
  - .github/workflows/ci.yml extend to run pytest
- Acceptance:
  - CI passes on PR with backend tests

Ticket 18: Offline caches and failure modes
- Description: Add timeouts and fallbacks for simplify/translate; in Flutter, cache last N gloss results; show “offline” banner when WS drops.
- Files:
  - backend: add timeouts in httpx calls
  - student app: local storage via shared_preferences
- Acceptance:
  - Simulate network loss; app shows cached captions/simplifications without crash

Ticket 19: Edge box stubs hookup (optional in Phase 1)
- Description: Document how to point ASR client to edge-box URLs via env; test with a local container simulating edge.
- Files:
  - docs/architecture.md, edge-box/* README updates
- Acceptance:
  - Changing ASR_URL env reroutes ASR calls without code changes

Key backend code details

asr_client.py (sketch)
- create_session(sr): returns session object with VAD state, audio ring buffer, model handle
- feed(pcm16_bytes): append to buffer; run VAD frames; when voiced segment length > min_window, decode candidate chunk using faster-whisper transcribe with no_vad=True; maintain partial hypothesis; debounce emissions
- flush_segment(): finalize current segment, reset partial
- batch_transcribe(wav_path): convenience for Reading Buddy

simplify.py (sketch)
- simplify(text, strength):
  - sent_tokenize(text)
  - for s in sentences: s = replace_complex_constructions(s); s = replace_low_freq_words(s); s = shorten(s, max_len[strength])
  - return join(sentences)
- extract_focus_commands(text):
  - doc = spacy(text)
  - For each sentence, if root POS is VERB and subject is implicit or second-person, extract lemma + direct object tokens

translate.py (sketch)
- glossary(text, l1):
  - tokenize, filter by low frequency or subject terms; map to bilingual lexicon; return top_k unique entries
- translate(text, l1):
  - if nllb_available: call nllb; else dictionary/phrase-based approximation; always mark as “approximate” in metadata

orf.py (sketch)
- score(audio, reference_text=None):
  - hyp_words = asr.batch_transcribe(audio).words
  - if reference_text:
    - ref_words = normalize(reference_text).split()
    - ops = levenshtein_align(ref_words, [w.word for w in hyp_words])
    - errors = list of ops not equal matches
    - wpm, wcpm, accuracy computed
  - else:
    - wpm derived from hyp count and duration
  - return scores + timed words

leveling.py (sketch)
- score_readability(text): compute avg sentence length, % of NGSL words, simple CEFR classifier
- rewrite(text, target): rules + llm_client.rewrite_with_instructions
- questions(text): extractive and inferential via small prompt; limit to 3–5
- glossary(text, l1): reuse translate.glossary

Teacher Copilot guardrails for LLM
- System prompt: “You rewrite for English learners in Alberta. Preserve facts. Avoid idioms. Use short sentences. No invented information. If uncertain, ask for clarification.”
- Post-processing: sentence-length clamp; forbidden content filter; profanity check

Student app details (Flutter)
- features/captions/
  - captions_bloc.dart or Riverpod providers
  - ws_service.dart: open WS, send start, stream mic audio using flutter_sound at 16kHz PCM, send stop
  - captions_screen.dart: text rendering of partial + final; simplify slider; L1 toggle
- features/reading_buddy/
  - recorder_service.dart
  - reading_api.dart: POST audio; GET generated decodable
  - reading_screen.dart

Teacher portal MVP (Next.js)
- pages/leveler.tsx or app/leveler/page.tsx
- Component:
  - TextArea, TargetLevelSelector (checkbox A2/B1/Gr5)
  - Generate button -> POST /v1/authoring/level-text
  - Output cards with copy buttons; save JSON

API contracts (copy into docs/api.md)
- WS /v1/captions/stream
  - Start: {"type":"start","sample_rate":16000,"lang":"en","save":false,"l1":"ar","simplify":2}
  - Binary audio frames
  - Stop: {"type":"stop"}
  - Server messages: ready, partial, final, error
- POST /v1/captions/simplify
  - In: {text, strength, focus_commands?}
  - Out: {simplified, focus[], explanations[]}
- POST /v1/captions/gloss
  - In: {text, l1, top_k?}
  - Out: {translation, gloss[]}
- POST /v1/reading/score_audio (multipart)
  - Out: {wpm, wcpm?, accuracy?, errors[], words_timed[]}
- POST /v1/reading/generate_decodable
  - Out: {text}
- POST /v1/authoring/level-text
  - Out: {levels: [{target,text,questions,gloss}]}

Definition of done (Phase 1)
- Live Captions + Simplifier:
  - A student can join a class session, stream audio, see live captions with partial and final updates
  - The simplify slider reduces complexity perceptibly; focus commands extracted
  - Optional L1 toggled gloss/translation appear for last sentence
  - No audio saved by default; transcripts only saved when save=true
- Reading Buddy:
  - Student can select a decodable or provided passage, record reading, upload, and receive WPM/WCPM and simple error feedback
  - Teacher can download a CSV of class reading scores (basic)
- Teacher Copilot:
  - Teacher pastes a text and receives at least two leveled rewrites with 3–5 questions and a small glossary
  - Outputs are safe, fact-preserving, and shorter for lower levels
- DevOps:
  - make up, make api works
  - CI runs pytest and compiles TypeScript packages
  - Privacy doc exists; feature flags wired

Testing plan
- Unit tests
  - simplify: sentences reduced in length; command extraction matches fixtures
  - orf: alignment on controlled inputs; WPM and WCPM formulas correct
  - leveling: ensures lower levels have lower avg sentence length and higher %NGSL words
- Integration tests
  - WS streaming happy path: feed a short wav; expect partial and final messages
  - Reading upload: sample audio -> scores within ±10% of expected
- Manual
  - Device mic test on Mac, Windows, Chromebook
  - Network loss during WS -> graceful reconnection with banner
- Performance
  - 10 concurrent WS sessions: median partial latency < 600ms
  - Level-text endpoint p95 < 8s for 400-word input (with LLM fallback)

Security and privacy checklist (Phase 1)
- No PII beyond user_id/class_code in requests
- Audio not persisted unless save=true
- Logs exclude raw audio and full transcripts; include metrics only
- CORS limited to localhost dev origins
- Content filters for Teacher Copilot outputs (basic profanity/PII in llm_client)

Next stretch goals (post-Phase 1)
- Speaking Coach module with minimal pairs and basic pronunciation scoring
- Family micro-lessons via WhatsApp/SMS
- On-device ASR in Flutter using whisper.cpp via FFI (Android/iOS)
- Edge box deployment with GPU Jetson acceleration and local discovery

Suggested agent execution order
- 0 Dev ergonomics
- 1–2 WS + ASR integration
- 3–4 Simplify + Gloss REST
- 5 Student captions UI
- 6 Transcript persistence (opt-in)
- 7–9 Reading Buddy API + UI
- 10–11 Teacher Copilot API + UI
- 12 Focus improvements
- 13 Minimal auth
- 14–18 Privacy, telemetry, tests, offline behavior
- 19 Edge docs

Quick commands reference
- Backend dev server: make api
- Install backend deps: make install-api
- Infra: make up
- Run backend tests (after adding pytest): backend/api/.venv/bin/pytest -q
- Teacher portal (after create-next-app): npm run dev
- Flutter student app: flutter run

If you want, I can generate starter code for any specific ticket (e.g., the full WS ASR handler with faster-whisper and VAD) so your agent can drop it in and iterate.