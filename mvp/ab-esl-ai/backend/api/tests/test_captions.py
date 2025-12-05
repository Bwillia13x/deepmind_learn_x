"""Tests for captions endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_simplify_strength_0():
    """Test simplify with strength 0 (no simplification)."""
    response = client.post(
        "/v1/captions/simplify",
        json={
            "text": "The quick brown fox jumps over the lazy dog.",
            "strength": 0,
            "focus_commands": False,
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["simplified"] == "The quick brown fox jumps over the lazy dog."
    assert data["focus"] == []


def test_simplify_with_word_replacement():
    """Test that simplify replaces complex words."""
    response = client.post(
        "/v1/captions/simplify",
        json={
            "text": "Please utilize the additional materials.",
            "strength": 1,
            "focus_commands": False,
        },
    )
    assert response.status_code == 200
    data = response.json()

    # Should replace "utilize" with "use" and "additional" with "more"
    assert "use" in data["simplified"].lower()
    assert "more" in data["simplified"].lower()


def test_simplify_extract_commands():
    """Test that simplify extracts imperative commands."""
    response = client.post(
        "/v1/captions/simplify",
        json={
            "text": "Open your books to page five.",
            "strength": 1,
            "focus_commands": True,
        },
    )
    assert response.status_code == 200
    data = response.json()

    # Should extract "open" as a command
    assert len(data["focus"]) > 0
    verbs = [f["verb"] for f in data["focus"]]
    assert "open" in verbs


def test_gloss_arabic():
    """Test glossary generation for Arabic."""
    response = client.post(
        "/v1/captions/gloss",
        json={
            "text": "The student read the book.",
            "l1": "ar",
            "top_k": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert "translation" in data
    assert "gloss" in data
    # Should have some glossary entries
    assert isinstance(data["gloss"], list)


def test_gloss_spanish():
    """Test glossary generation for Spanish."""
    response = client.post(
        "/v1/captions/gloss",
        json={
            "text": "The teacher helps the student.",
            "l1": "es",
            "top_k": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert "translation" in data
    assert "gloss" in data
