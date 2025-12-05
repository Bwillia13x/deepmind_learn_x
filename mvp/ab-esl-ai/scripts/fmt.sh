#!/usr/bin/env bash
set -e

echo "Formatting Python..."
if [ -f "backend/api/.venv/bin/python" ]; then
    backend/api/.venv/bin/pip install black isort ruff >/dev/null 2>&1 || true
    backend/api/.venv/bin/black backend/api
    backend/api/.venv/bin/isort backend/api
    backend/api/.venv/bin/ruff check --fix backend/api || true
fi

echo "Formatting complete!"
