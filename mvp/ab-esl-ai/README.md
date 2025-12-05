# Alberta ESL AI

**AI-powered literacy tools for ESL educators and students in Alberta schools.**

[![Tests](https://img.shields.io/badge/tests-192%20passing-green)](./backend/api/tests)
[![Languages](https://img.shields.io/badge/L1%20languages-13-blue)](./content/l1_transfer)
[![FOIP](https://img.shields.io/badge/FOIP-compliant-green)](./docs/privacy-foip.md)

## 🎯 Overview

AB-ESL-AI addresses Alberta's literacy crisis by embedding ESL specialist expertise into AI that works at scale. Unlike generic EdTech, this solution is:

- **Purpose-built** for Canadian K-12 ELL instruction
- **Alberta curriculum native** (ELA outcomes + ESL Benchmarks)
- **L1-informed** (not generic—13 languages with transfer pattern intelligence)
- **Teacher amplifier** (not replacement)
- **Family inclusive** (bilingual support for parents)
- **FOIP compliant** (Canadian data residency)
- **Offline-first** (works in rural Alberta)

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ (backend)
- Node.js 18+ (frontend apps)
- Docker & Docker Compose (optional, for PostgreSQL/Redis)

### Quick Local Development (No Docker Required)

```bash
# 1. Start the API (uses SQLite, no external dependencies)
cd mvp/ab-esl-ai/backend/api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
DATABASE_URL="sqlite:///./test.db" uvicorn app.main:app --port 8000

# 2. Start Teacher Portal (new terminal)
cd mvp/ab-esl-ai/apps/teacher-portal
npm install && npm run dev

# 3. Start Student App (new terminal)  
cd mvp/ab-esl-ai/apps/student-app
npm install && npm run dev
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Teacher Portal | <http://localhost:3000> | Main teacher interface |
| Student App | <http://localhost:3001> | Student-facing PWA |
| API Docs | <http://localhost:8000/docs> | Swagger API documentation |
| API Health | <http://localhost:8000/health> | Health check endpoint |

### One-Command Demo Setup (with Docker)

```bash
cd mvp/ab-esl-ai
./scripts/demo_setup.sh
```

This script will:

1. ✅ Check prerequisites
2. ✅ Start Docker containers (Postgres, Redis, MinIO)
3. ✅ Install all dependencies
4. ✅ Print instructions for starting the demo

### Manual Start (Alternative)

\`\`\`bash

# Clone and enter directory

cd mvp/ab-esl-ai

# Copy environment file

cp .env.example .env

# Start infrastructure (Postgres, Redis, MinIO)

make up

# Install API dependencies

make install-api

# Start API server

make api
\`\`\`

### Start Frontend Apps

\`\`\`bash

# Terminal 1: Teacher Portal (<http://localhost:3000>)

cd apps/teacher-portal
npm install
npm run dev

# Terminal 2: Student App (<http://localhost:3001>)

cd apps/student-app
npm install
npm run dev
\`\`\`

### Seed Demo Data (Optional)

\`\`\`bash
make seed

# Creates: Class "Ms. Johnson - Grade 4 ESL" with 5 sample students

# Outputs: Class code you can use to join as a student

\`\`\`

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Teacher Portal | <http://localhost:3000> | Main teacher interface |
| Student App | <http://localhost:3001> | Student-facing PWA |
| API Docs | <http://localhost:8000/docs> | Swagger API documentation |
| API Health | <http://localhost:8000/health> | Health check endpoint |

## 📚 Features

### Core Tools

| Feature | Description |
|---------|-------------|
| **Text Leveler** | Generate multiple readability levels with comprehension questions |
| **Decodable Generator** | Phonics-constrained texts for early readers |
| **Reading Buddy** | ORF scoring with WPM and accuracy feedback |
| **Live Captions** | Real-time ASR with simplification and translation |
| **Translation & Glossary** | Bilingual glossaries in 13 languages |
| **Analytics Dashboard** | Track student progress and identify struggling learners |

### Alberta-Specific Features (NEW)

| Feature | Description |
|---------|-------------|
| **L1 Transfer Intelligence** | Predict and address L1-specific errors for 13 languages |
| **Curriculum Mapping** | Auto-map activities to Alberta ELA outcomes & ESL Benchmarks |
| **Predictive Interventions** | Identify at-risk students 4-6 weeks early |
| **Family Literacy Co-Pilot** | Bilingual homework helpers and SMS micro-lessons |
| **SLIFE Pathways** | Content for students with limited/interrupted schooling |
| **Cultural Responsiveness** | Adapt content for cultural context |
| **FOIP Analytics** | Privacy-by-design with k-anonymity |

### Supported Languages

Arabic 🇸🇦 | Spanish 🇪🇸 | Chinese 🇨🇳 | Korean 🇰🇷 | Tagalog 🇵🇭 | Punjabi 🇮🇳 | Ukrainian 🇺🇦 | Somali 🇸🇴 | Vietnamese 🇻🇳 | Farsi 🇮🇷 | Hindi 🇮🇳 | Urdu 🇵🇰 | French 🇫🇷

## 🏗️ Architecture

\`\`\`
mvp/ab-esl-ai/
├── apps/
│   ├── teacher-portal/     # Next.js 14 PWA for teachers
│   └── student-app/        # Next.js 14 PWA for students
├── backend/
│   └── api/                # FastAPI backend
│       ├── app/
│       │   ├── routers/    # API endpoints
│       │   ├── services/   # Business logic
│       │   └── models/     # Database models
│       └── tests/          # Pytest test suite
├── content/
│   ├── l1_transfer/        # L1 linguistic patterns (13 languages)
│   ├── curriculum/         # Alberta ELA outcomes & ESL benchmarks
│   ├── cultural/           # Cultural responsiveness profiles
│   ├── slife/              # SLIFE-appropriate content
│   ├── glossaries/         # Bilingual dictionaries
│   └── passages/           # Sample reading passages
├── docs/                   # Documentation
└── infra/                  # Terraform & Docker configs
\`\`\`

## 📖 API Reference

### Core Endpoints

\`\`\`
POST /v1/captions/simplify      - Simplify text
POST /v1/captions/gloss         - Generate glossary
POST /v1/reading/score          - Score reading fluency
POST /v1/reading/score_audio    - Score from audio
POST /v1/authoring/level-text   - Generate leveled versions
\`\`\`

### Novel Feature Endpoints

\`\`\`
GET  /v1/l1-transfer/patterns/{code}      - L1 transfer patterns
POST /v1/l1-transfer/predict-errors       - Predict L1-specific errors
POST /v1/curriculum/map-activity          - Map to Alberta outcomes
POST /v1/interventions/assess-risk        - Assess student risk
POST /v1/interventions/generate-plan      - Generate intervention plan
POST /v1/family/homework-helper           - Bilingual homework support
POST /v1/family/micro-lesson              - SMS-ready micro-lesson
GET  /v1/slife/content                    - SLIFE content library
GET  /v1/cultural/profile/{code}          - Cultural profile
POST /v1/privacy/analytics/aggregate      - Privacy-safe analytics
\`\`\`

## 🧪 Testing

\`\`\`bash

# Run all tests

cd backend/api
pytest

# Run with coverage

pytest --cov=app --cov-report=html

# Run specific test file

pytest tests/test_l1_transfer.py -v
\`\`\`

## 🐳 Docker

\`\`\`bash

# Start all services

docker-compose up -d

# View logs

docker-compose logs -f api

# Rebuild after changes

docker-compose up -d --build

# Stop all

docker-compose down
\`\`\`

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| Weekly teacher time saved | 7+ hours |
| Languages supported | 13 |
| Grade levels | K-9 |
| ESL Benchmark levels | 5 |
| Test coverage | 192+ tests |
| API endpoints | 50+ |

## 📁 Documentation

- [Executive Summary](./docs/EXECUTIVE_SUMMARY.md) - Board presentation materials
- [Demo Walkthrough](./docs/DEMO_WALKTHROUGH.md) - Step-by-step demo guide
- [Architecture](./docs/architecture.md) - System design
- [API Reference](./docs/api.md) - Full API documentation
- [Privacy & FOIP](./docs/privacy-foip.md) - Data handling principles
- [Implementation Status](./docs/IMPLEMENTATION_STATUS.md) - Feature completion status
- [Novel Features Roadmap](./docs/NOVEL_FEATURES_ROADMAP.md) - Alberta-specific features

## 🔐 Security & Privacy

- **FOIP Compliant**: Designed for Alberta's Freedom of Information and Protection of Privacy Act
- **Canadian Data Residency**: All data stays in Canada
- **K-Anonymity**: Aggregate analytics with privacy guarantees
- **Audit Trails**: Full logging for compliance
- **JWT Authentication**: Secure token-based auth
- **Rate Limiting**: Protection against abuse

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (\`git checkout -b feature/amazing-feature\`)
3. Commit your changes (\`git commit -m 'Add amazing feature'\`)
4. Push to the branch (\`git push origin feature/amazing-feature\`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for Alberta's ESL educators and students**
