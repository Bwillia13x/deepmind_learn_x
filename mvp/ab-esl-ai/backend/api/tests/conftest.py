"""Pytest configuration for API tests."""

import os

# Set TESTING env var BEFORE any imports
os.environ["TESTING"] = "true"

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables before running tests."""
    # Set required environment variables for tests
    os.environ["CORS_ORIGINS"] = '["http://localhost:3000"]'
    os.environ["DATABASE_URL"] = "postgresql+psycopg://dev:devpass@localhost:5433/ab_esl_ai"
    os.environ["REDIS_URL"] = "redis://localhost:6380/0"
    
    # Disable external services for unit tests
    os.environ["ENABLE_ASR"] = "false"
    os.environ["ENABLE_LLM"] = "false"
    
    yield
