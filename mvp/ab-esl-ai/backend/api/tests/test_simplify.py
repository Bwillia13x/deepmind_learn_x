"""Tests for text simplification API."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_simplify_strength_0():
    """Test that strength 0 returns original text unchanged."""
    response = client.post(
        "/v1/captions/simplify",
        json={"text": "The photosynthesis process converts light energy.", "strength": 0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["simplified"] == "The photosynthesis process converts light energy."
    assert isinstance(data["focus"], list)


def test_simplify_strength_2():
    """Test that strength 2 simplifies text."""
    response = client.post(
        "/v1/captions/simplify",
        json={
            "text": "Please utilize your notebooks to demonstrate your understanding.",
            "strength": 2,
        },
    )
    assert response.status_code == 200
    data = response.json()
    # Should replace "utilize" with "use" and "demonstrate" with "show"
    assert "use" in data["simplified"].lower()
    assert "utilize" not in data["simplified"].lower()


def test_simplify_focus_commands():
    """Test that focus commands are extracted from classroom instructions."""
    response = client.post(
        "/v1/captions/simplify",
        json={
            "text": "Open your textbooks to page 42. Write the date at the top.",
            "strength": 1,
            "focus_commands": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["focus"]) >= 2  # Should find "open" and "write"
    verbs = [cmd["verb"] for cmd in data["focus"]]
    assert "open" in verbs
    assert "write" in verbs


def test_simplify_long_sentences():
    """Test that long sentences are shortened at higher strength levels."""
    long_text = (
        "The students, who had been working diligently throughout the entire morning session, "
        "were finally ready to take a well-deserved break before continuing with their studies."
    )
    response = client.post(
        "/v1/captions/simplify",
        json={"text": long_text, "strength": 3},
    )
    assert response.status_code == 200
    data = response.json()
    # At strength 3, max sentence length should be ~12 words
    simplified_sentences = data["simplified"].split(". ")
    for sentence in simplified_sentences:
        word_count = len(sentence.split())
        assert word_count <= 15  # Allow some flexibility


def test_simplify_missing_text():
    """Test that missing text returns an error."""
    response = client.post(
        "/v1/captions/simplify",
        json={"strength": 1},
    )
    assert response.status_code == 422  # Validation error


def test_simplify_invalid_strength():
    """Test that invalid strength values are handled."""
    response = client.post(
        "/v1/captions/simplify",
        json={"text": "Test text", "strength": 10},  # Out of range
    )
    # Should either cap at 3 or return validation error
    assert response.status_code in [200, 422]


def test_simplify_empty_text():
    """Test that empty text is handled gracefully."""
    response = client.post(
        "/v1/captions/simplify",
        json={"text": "", "strength": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["simplified"] == ""
    assert data["focus"] == []
