.PHONY: up down api install-api seed fmt test demo demo-setup health

up:
	docker compose up -d

down:
	docker compose down -v

install-api:
	python3 -m venv backend/api/.venv
	backend/api/.venv/bin/pip install --upgrade pip
	backend/api/.venv/bin/pip install -r backend/api/requirements.txt

api:
	BACKEND_ENV=.env backend/api/.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend/api

seed:
	bash scripts/seed_db.sh

fmt:
	bash scripts/fmt.sh

test:
	backend/api/.venv/bin/pytest backend/api/tests -v

health:
	bash scripts/health_check.sh

# Demo Day Commands
demo-setup:
	./scripts/demo_setup.sh

demo: up
	@echo "Starting all services for demo..."
	@echo "1. Starting API server in background..."
	@BACKEND_ENV=.env backend/api/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend/api &
	@echo "2. Starting Teacher Portal..."
	@cd apps/teacher-portal && npm run dev &
	@echo "3. Starting Student App..."
	@cd apps/student-app && npm run dev &
	@echo ""
	@echo "All services starting..."
	@echo "  API:             http://localhost:8000"
	@echo "  Teacher Portal:  http://localhost:3000"
	@echo "  Student App:     http://localhost:3001"
	@echo ""
	@echo "Press Ctrl+C to stop all services"
	@wait
