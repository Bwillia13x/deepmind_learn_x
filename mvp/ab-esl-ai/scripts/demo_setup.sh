#!/usr/bin/env bash
set -euo pipefail

# Alberta ESL AI - Demo Day Setup Script
# One-command setup for demo/presentation day

echo "🎓 Alberta ESL AI - Demo Day Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.11+ first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites found${NC}"
echo ""

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✅ .env created${NC}"
else
    echo -e "${YELLOW}ℹ️  .env already exists${NC}"
fi
echo ""

# Start infrastructure
echo "🐳 Starting Docker containers (Postgres, Redis, MinIO)..."
docker compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 5

# Check if containers are healthy
if docker compose ps | grep -q "healthy"; then
    echo -e "${GREEN}✅ Infrastructure is healthy${NC}"
elif docker compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Infrastructure is running${NC}"
else
    echo -e "${YELLOW}⚠️  Some containers may still be starting...${NC}"
fi
echo ""

# Install API dependencies
echo "📦 Installing backend API dependencies..."
if [ ! -d "backend/api/.venv" ]; then
    python3 -m venv backend/api/.venv
fi
backend/api/.venv/bin/pip install --upgrade pip -q
backend/api/.venv/bin/pip install -r backend/api/requirements.txt -q
echo -e "${GREEN}✅ API dependencies installed${NC}"
echo ""

# Install frontend dependencies
echo "📦 Installing Teacher Portal dependencies..."
cd apps/teacher-portal
npm install --silent
cd "$PROJECT_ROOT"
echo -e "${GREEN}✅ Teacher Portal dependencies installed${NC}"

echo "📦 Installing Student App dependencies..."
cd apps/student-app
npm install --silent
cd "$PROJECT_ROOT"
echo -e "${GREEN}✅ Student App dependencies installed${NC}"
echo ""

# Create demo-ready instructions
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 Demo Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "To start the demo, open 3 terminals and run:"
echo ""
echo -e "${YELLOW}Terminal 1 - API Backend:${NC}"
echo "  cd $PROJECT_ROOT"
echo "  make api"
echo "  # API will be at http://localhost:8000"
echo ""
echo -e "${YELLOW}Terminal 2 - Teacher Portal:${NC}"
echo "  cd $PROJECT_ROOT/apps/teacher-portal"
echo "  npm run dev"
echo "  # Teacher Portal at http://localhost:3000"
echo ""
echo -e "${YELLOW}Terminal 3 - Student App:${NC}"
echo "  cd $PROJECT_ROOT/apps/student-app"
echo "  npm run dev"
echo "  # Student App at http://localhost:3001"
echo ""
echo -e "${YELLOW}Optional - Seed demo data:${NC}"
echo "  cd $PROJECT_ROOT"
echo "  make seed"
echo "  # Creates demo class session with sample students"
echo ""
echo "=========================================="
echo "Demo Walkthrough: docs/DEMO_WALKTHROUGH.md"
echo "=========================================="
echo ""
