"""Tests for Writing API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestWritingFeedback:
    """Tests for writing feedback endpoint."""

    def test_get_feedback(self):
        """Test getting writing feedback."""
        response = client.post(
            "/v1/writing/feedback",
            json={
                "text": "I go to school yesterday.",
                "l1": "es",
                "proficiency_level": 2
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "original" in data
        assert "suggestions" in data
        assert "l1_explanations" in data
        assert "vocabulary_suggestions" in data

    def test_feedback_returns_l1_explanations(self):
        """Test that feedback includes L1-specific explanations."""
        response = client.post(
            "/v1/writing/feedback",
            json={
                "text": "The house big is nice.",
                "l1": "es",
                "proficiency_level": 2
            }
        )
        data = response.json()
        assert len(data["l1_explanations"]) > 0
        explanation = data["l1_explanations"][0]
        assert "error_type" in explanation
        assert "explanation" in explanation
        assert "tip" in explanation

    def test_feedback_empty_text(self):
        """Test feedback with empty text."""
        response = client.post(
            "/v1/writing/feedback",
            json={
                "text": "",
                "l1": "es",
                "proficiency_level": 2
            }
        )
        assert response.status_code == 200

    def test_feedback_different_l1(self):
        """Test feedback with different L1 languages."""
        for l1 in ["ar", "zh", "ko", "tl"]:
            response = client.post(
                "/v1/writing/feedback",
                json={
                    "text": "I go to school.",
                    "l1": l1,
                    "proficiency_level": 2
                }
            )
            assert response.status_code == 200


class TestWritingL1Tips:
    """Tests for L1-specific writing tips endpoint."""

    def test_get_l1_tips_spanish(self):
        """Test getting writing tips for Spanish speakers."""
        response = client.get("/v1/writing/l1-tips/es")
        assert response.status_code == 200
        data = response.json()
        assert data["l1_code"] == "es"
        assert "l1_name" in data
        assert "writing_tips" in data
        assert "grammar_focus" in data

    def test_get_l1_tips_arabic(self):
        """Test getting writing tips for Arabic speakers."""
        response = client.get("/v1/writing/l1-tips/ar")
        assert response.status_code == 200
        data = response.json()
        assert data["l1_code"] == "ar"

    def test_get_l1_tips_chinese(self):
        """Test getting writing tips for Chinese speakers."""
        response = client.get("/v1/writing/l1-tips/zh")
        assert response.status_code == 200
        data = response.json()
        assert data["l1_code"] == "zh"

    def test_tips_have_structure(self):
        """Test that tips have required structure."""
        response = client.get("/v1/writing/l1-tips/es")
        data = response.json()
        if data["writing_tips"]:
            tip = data["writing_tips"][0]
            assert "error_type" in tip
            assert "explanation" in tip
            assert "tip" in tip


class TestWritingSentenceFrames:
    """Tests for sentence frames endpoint."""

    def test_get_narrative_frames(self):
        """Test getting narrative sentence frames."""
        response = client.get("/v1/writing/sentence-frames/narrative")
        assert response.status_code == 200
        data = response.json()
        assert data["writing_type"] == "narrative"
        assert "frames" in data
        assert isinstance(data["frames"], list)

    def test_get_descriptive_frames(self):
        """Test getting descriptive sentence frames."""
        response = client.get("/v1/writing/sentence-frames/descriptive")
        assert response.status_code == 200
        data = response.json()
        assert data["writing_type"] == "descriptive"

    def test_get_opinion_frames(self):
        """Test getting opinion sentence frames."""
        response = client.get("/v1/writing/sentence-frames/opinion")
        assert response.status_code == 200
        data = response.json()
        assert data["writing_type"] == "opinion"

    def test_frames_have_structure(self):
        """Test that frames have required structure."""
        response = client.get("/v1/writing/sentence-frames/narrative")
        data = response.json()
        assert "frames" in data
        assert len(data["frames"]) > 0


class TestWritingVocabularyUpgrades:
    """Tests for vocabulary upgrades endpoint."""

    def test_get_vocabulary_upgrades(self):
        """Test getting vocabulary upgrade suggestions."""
        response = client.get("/v1/writing/vocabulary-upgrades")
        assert response.status_code == 200
        data = response.json()
        assert "upgrades" in data
        assert isinstance(data["upgrades"], dict)

    def test_upgrades_have_structure(self):
        """Test that upgrades have required structure."""
        response = client.get("/v1/writing/vocabulary-upgrades")
        data = response.json()
        # Should have upgrade suggestions for common words
        assert len(data["upgrades"]) > 0
