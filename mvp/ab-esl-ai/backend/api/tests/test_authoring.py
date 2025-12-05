"""Tests for authoring/teacher copilot endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_level_text_single_target():
    """Test text leveling with single target."""
    response = client.post(
        "/v1/authoring/level-text",
        json={
            "text": "Photosynthesis is the process by which plants convert sunlight into chemical energy.",
            "targets": ["A2"],
            "l1": "ar",
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert "original_score" in data
    assert "levels" in data
    assert len(data["levels"]) == 1
    assert data["levels"][0]["target"] == "A2"
    assert "text" in data["levels"][0]
    assert "questions" in data["levels"][0]


def test_level_text_multiple_targets():
    """Test text leveling with multiple targets."""
    response = client.post(
        "/v1/authoring/level-text",
        json={
            "text": "The water cycle describes how water moves continuously through Earth's systems.",
            "targets": ["A2", "B1", "Gr5"],
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert len(data["levels"]) == 3
    targets = [level["target"] for level in data["levels"]]
    assert "A2" in targets
    assert "B1" in targets
    assert "Gr5" in targets


def test_level_text_with_glossary():
    """Test that leveling includes glossary entries."""
    response = client.post(
        "/v1/authoring/level-text",
        json={
            "text": "The fraction represents a part of the whole number.",
            "targets": ["A2"],
            "l1": "ar",
        },
    )
    assert response.status_code == 200
    data = response.json()

    # Should have glossary entries
    level = data["levels"][0]
    assert "gloss" in level
    assert isinstance(level["gloss"], list)


def test_level_text_generates_questions():
    """Test that leveling generates comprehension questions."""
    response = client.post(
        "/v1/authoring/level-text",
        json={
            "text": "Plants need water and sunlight to grow. They make their own food through photosynthesis.",
            "targets": ["B1"],
        },
    )
    assert response.status_code == 200
    data = response.json()

    level = data["levels"][0]
    assert "questions" in level
    assert len(level["questions"]) > 0

    # Check question structure
    q = level["questions"][0]
    assert "type" in q
    assert "q" in q
    assert "a" in q


def test_original_score():
    """Test that original text readability is scored."""
    response = client.post(
        "/v1/authoring/level-text",
        json={
            "text": "The cat sat on the mat.",
            "targets": ["A1"],
        },
    )
    assert response.status_code == 200
    data = response.json()

    score = data["original_score"]
    assert "cefr" in score
    assert "avg_sentence_length" in score
    assert "difficult_word_pct" in score
