#!/usr/bin/env bash
# Alberta ESL AI - Demo Health Check
# Run this before any demo to verify all systems are operational

set -e

echo "🏥 Alberta ESL AI - Demo Health Check"
echo "======================================"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

CHECKS_PASSED=0
CHECKS_FAILED=0

check() {
    local name="$1"
    local result="$2"
    if [ "$result" = "0" ]; then
        echo -e "${GREEN}✅ $name${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}❌ $name${NC}"
        ((CHECKS_FAILED++))
    fi
}

echo "📦 Checking Infrastructure..."
echo ""

# Check Docker
if docker info > /dev/null 2>&1; then
    check "Docker is running" 0
else
    check "Docker is running" 1
fi

# Check Postgres
if docker compose ps 2>/dev/null | grep -q "db.*running\|db.*Up"; then
    check "PostgreSQL container is running" 0
else
    check "PostgreSQL container is running" 1
fi

# Check Redis
if docker compose ps 2>/dev/null | grep -q "redis.*running\|redis.*Up"; then
    check "Redis container is running" 0
else
    check "Redis container is running" 1
fi

# Check MinIO
if docker compose ps 2>/dev/null | grep -q "minio.*running\|minio.*Up"; then
    check "MinIO container is running" 0
else
    check "MinIO container is running" 1
fi

echo ""
echo "🔌 Checking Services..."
echo ""

# Check API
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    check "API server (port 8000)" 0
    
    # Check API health details
    HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)
    if echo "$HEALTH" | grep -q '"status":"healthy"'; then
        check "API health status" 0
    else
        check "API health status" 1
    fi
else
    check "API server (port 8000)" 1
fi

# Check Teacher Portal
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    check "Teacher Portal (port 3000)" 0
else
    check "Teacher Portal (port 3000)" 1
fi

# Check Student App
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    check "Student App (port 3001)" 0
else
    check "Student App (port 3001)" 1
fi

echo ""
echo "🧪 Checking Critical Endpoints..."
echo ""

# Test auth endpoint
if curl -s http://localhost:8000/auth/session/TEST123 2>/dev/null | grep -q -E '"detail"|"session_id"'; then
    check "Auth endpoint responding" 0
else
    check "Auth endpoint responding" 1
fi

# Test reading passages
if curl -s http://localhost:8000/v1/reading/passages 2>/dev/null | grep -q '"passages"'; then
    check "Reading passages endpoint" 0
else
    check "Reading passages endpoint" 1
fi

# Test L1 languages
if curl -s http://localhost:8000/v1/l1-transfer/languages 2>/dev/null | grep -q '"code"'; then
    check "L1 Transfer languages endpoint" 0
else
    check "L1 Transfer languages endpoint" 1
fi

# Test curriculum outcomes
if curl -s http://localhost:8000/v1/curriculum/outcomes/3 2>/dev/null | grep -q -E '"outcomes"|"error"'; then
    check "Curriculum outcomes endpoint" 0
else
    check "Curriculum outcomes endpoint" 1
fi

echo ""
echo "======================================"
echo -e "Results: ${GREEN}$CHECKS_PASSED passed${NC}, ${RED}$CHECKS_FAILED failed${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All systems operational! Ready for demo.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some checks failed. Review issues above before demo.${NC}"
    echo ""
    echo "Quick fixes:"
    echo "  - Infrastructure: make up"
    echo "  - API server: make api"
    echo "  - Teacher Portal: cd apps/teacher-portal && npm run dev"
    echo "  - Student App: cd apps/student-app && npm run dev"
    exit 1
fi
