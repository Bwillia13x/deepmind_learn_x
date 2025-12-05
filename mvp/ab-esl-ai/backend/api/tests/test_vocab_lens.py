"""Tests for Vocab Lens API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestVocabLensCategories:
    """Tests for vocabulary categories endpoint."""

    def test_get_categories(self):
        """Test getting vocabulary categories."""
        response = client.get("/v1/vocab-lens/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "classroom" in data
        assert "technology" in data
        assert isinstance(data["classroom"], list)

    def test_categories_contain_expected_items(self):
        """Test that categories contain expected vocabulary items."""
        response = client.get("/v1/vocab-lens/categories")
        data = response.json()
        # Should have common classroom items
        classroom_items = data.get("classroom", [])
        assert len(classroom_items) > 0


class TestVocabLensRecognize:
    """Tests for object recognition endpoint."""

    def test_recognize_returns_detections(self):
        """Test that recognize endpoint returns detected objects."""
        response = client.post(
            "/v1/vocab-lens/recognize",
            json={"participant_id": 1}
        )
        assert response.status_code == 200
        data = response.json()
        assert "detected_objects" in data
        assert isinstance(data["detected_objects"], list)

    def test_recognize_objects_have_required_fields(self):
        """Test that detected objects have all required fields."""
        response = client.post(
            "/v1/vocab-lens/recognize",
            json={"participant_id": 1}
        )
        data = response.json()
        if data["detected_objects"]:
            obj = data["detected_objects"][0]
            assert "word" in obj
            assert "definition" in obj
            assert "l1_translation" in obj
            assert "collocations" in obj
            assert "sentence_frames" in obj

    def test_recognize_with_l1_override(self):
        """Test recognition with L1 language override."""
        response = client.post(
            "/v1/vocab-lens/recognize",
            json={"participant_id": 1, "l1": "ar"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "detected_objects" in data


class TestVocabLensVocabulary:
    """Tests for vocabulary lookup endpoint."""

    def test_get_vocabulary_word(self):
        """Test looking up a specific word."""
        response = client.get("/v1/vocab-lens/vocabulary/book")
        assert response.status_code == 200
        data = response.json()
        assert data["word"] == "book"
        assert "definition" in data
        assert "collocations" in data
        assert "sentence_frames" in data

    def test_get_vocabulary_with_l1(self):
        """Test vocabulary lookup with L1 translation."""
        response = client.get("/v1/vocab-lens/vocabulary/book?l1=es")
        assert response.status_code == 200
        data = response.json()
        assert "l1_translation" in data

    def test_get_unknown_word(self):
        """Test looking up an unknown word returns 404."""
        response = client.get("/v1/vocab-lens/vocabulary/xyznonexistent123")
        # Unknown words return 404
        assert response.status_code == 404


class TestVocabLensTopicPacks:
    """Tests for topic packs endpoint."""

    def test_get_topic_packs(self):
        """Test getting available topic packs."""
        response = client.get("/v1/vocab-lens/topic-packs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_topic_packs_have_structure(self):
        """Test that topic packs have required structure."""
        response = client.get("/v1/vocab-lens/topic-packs")
        data = response.json()
        if data:
            pack = data[0]
            assert "id" in pack
            assert "name" in pack
            assert "words" in pack
            assert isinstance(pack["words"], list)


class TestVocabLensDeck:
    """Tests for flashcard deck endpoints."""

    def test_add_to_deck(self):
        """Test adding a word to the deck."""
        response = client.post(
            "/v1/vocab-lens/deck/add",
            json={
                "participant_id": 1,
                "word": "book",
                "l1": "es"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data or "word" in data  # Accept either response format

    def test_get_deck(self):
        """Test getting a participant's deck."""
        response = client.get("/v1/vocab-lens/deck/1")
        assert response.status_code == 200
        data = response.json()
        # Response is a list of deck items
        assert isinstance(data, list)

    def test_review_deck(self):
        """Test getting cards due for review."""
        response = client.get("/v1/vocab-lens/deck/1/review")
        assert response.status_code == 200
        data = response.json()
        assert "due_cards" in data or isinstance(data, list)  # Accept either format

    def test_submit_review(self):
        """Test submitting a review result."""
        response = client.post(
            "/v1/vocab-lens/deck/review",
            json={
                "participant_id": 1,
                "word": "book",
                "quality": 4  # 0-5 rating scale
            }
        )
        assert response.status_code == 200
