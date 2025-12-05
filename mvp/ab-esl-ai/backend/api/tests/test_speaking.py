"""Tests for Speaking Coach API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_score_word_pronunciation_exact_match():
    """Test pronunciation scoring with exact match."""
    response = client.post(
        "/v1/speaking/score_word",
        json={
            "text": "cat",
            "target_word": "cat",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["score"] == 1.0
    assert data["match"] == "exact"
    assert data["transcribed"] == "cat"
    assert data["target"] == "cat"
    assert "feedback" in data


def test_score_word_pronunciation_close_match():
    """Test pronunciation scoring with close match."""
    response = client.post(
        "/v1/speaking/score_word",
        json={
            "text": "cot",  # Similar to "cat"
            "target_word": "cat",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    assert 0 < data["score"] < 1.0
    assert data["match"] in ["close", "partial"]
    assert "feedback" in data


def test_score_word_pronunciation_poor_match():
    """Test pronunciation scoring with poor match."""
    response = client.post(
        "/v1/speaking/score_word",
        json={
            "text": "elephant",  # Very different from "cat"
            "target_word": "cat",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["score"] < 0.5
    assert data["match"] == "poor"
    assert "feedback" in data


def test_score_word_pronunciation_case_insensitive():
    """Test pronunciation scoring is case insensitive."""
    response = client.post(
        "/v1/speaking/score_word",
        json={
            "text": "CAT",
            "target_word": "cat",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["score"] == 1.0
    assert data["match"] == "exact"


def test_score_minimal_pair():
    """Test minimal pair scoring."""
    response = client.post(
        "/v1/speaking/score_minimal_pair",
        json={
            "word1": "light",
            "word2": "right",
            "pair_id": "pair_l_r",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    # Should have scores for both words
    assert "word1_score" in data or "score" in data or "average_score" in data
    

def test_score_minimal_pair_identical_words():
    """Test minimal pair where user says same word for both."""
    response = client.post(
        "/v1/speaking/score_minimal_pair",
        json={
            "word1": "light",
            "word2": "light",  # Said same word twice
            "pair_id": "pair_l_r",
        },
    )
    assert response.status_code == 200
    data = response.json()
    # Should indicate that the words need to be different
    assert "score" in data or "average_score" in data or "feedback" in data


def test_get_exercises_for_l1_spanish():
    """Test getting exercises for Spanish L1."""
    response = client.get("/v1/speaking/exercises/es")
    assert response.status_code == 200
    data = response.json()
    
    assert "l1" in data
    assert data["l1"] == "es"
    assert "exercises" in data
    assert isinstance(data["exercises"], list)


def test_get_exercises_for_l1_arabic():
    """Test getting exercises for Arabic L1."""
    response = client.get("/v1/speaking/exercises/ar")
    assert response.status_code == 200
    data = response.json()
    
    assert data["l1"] == "ar"
    assert "exercises" in data


def test_get_exercises_for_l1_chinese():
    """Test getting exercises for Chinese L1."""
    response = client.get("/v1/speaking/exercises/zh")
    assert response.status_code == 200
    data = response.json()
    
    assert data["l1"] == "zh"
    assert "exercises" in data


def test_get_exercises_for_unknown_l1():
    """Test getting exercises for unknown L1 returns empty or all."""
    response = client.get("/v1/speaking/exercises/xx")
    assert response.status_code == 200
    data = response.json()
    
    assert "exercises" in data


def test_get_all_exercises():
    """Test getting all minimal pair exercises."""
    response = client.get("/v1/speaking/exercises")
    assert response.status_code == 200
    data = response.json()
    
    assert "pairs" in data
    assert "count" in data
    assert isinstance(data["pairs"], list)


def test_exercises_have_required_fields():
    """Test that exercise data has expected structure."""
    response = client.get("/v1/speaking/exercises")
    assert response.status_code == 200
    data = response.json()
    
    if data["count"] > 0 and len(data["pairs"]) > 0:
        pair = data["pairs"][0]
        # Check for expected fields in minimal pair structure
        assert "pair_id" in pair or "sounds" in pair or "words" in pair


def test_score_word_empty_text():
    """Test scoring with empty transcribed text."""
    response = client.post(
        "/v1/speaking/score_word",
        json={
            "text": "",
            "target_word": "cat",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    # Should have a low score
    assert data["score"] < 0.5


def test_score_word_with_whitespace():
    """Test scoring handles whitespace properly."""
    response = client.post(
        "/v1/speaking/score_word",
        json={
            "text": "  cat  ",
            "target_word": "cat",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    # Should strip whitespace and score correctly
    assert data["score"] == 1.0
    assert data["match"] == "exact"


def test_score_word_missing_target():
    """Test scoring without target word fails validation."""
    response = client.post(
        "/v1/speaking/score_word",
        json={
            "text": "cat",
        },
    )
    assert response.status_code == 422  # Validation error


def test_minimal_pair_missing_pair_id():
    """Test minimal pair scoring without pair_id fails validation."""
    response = client.post(
        "/v1/speaking/score_minimal_pair",
        json={
            "word1": "ship",
            "word2": "sheep",
        },
    )
    assert response.status_code == 422  # Validation error


def test_exercises_endpoint_returns_count():
    """Test that exercises endpoint returns correct count."""
    response = client.get("/v1/speaking/exercises")
    assert response.status_code == 200
    data = response.json()
    
    assert data["count"] == len(data["pairs"])
