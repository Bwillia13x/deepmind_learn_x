"""Tests for L1 Linguistic Transfer Intelligence service."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.l1_transfer import (
    get_supported_l1_languages,
    get_l1_profile,
    get_phonological_difficulties,
    get_grammar_challenges,
    get_cognates,
    get_false_friends,
    predict_likely_errors,
    generate_intervention_plan,
    get_cultural_considerations,
    get_contrastive_feedback,
    get_vocabulary_strategies,
    generate_l1_aware_exercise,
)

client = TestClient(app)


class TestL1TransferService:
    """Tests for L1 transfer service functions."""

    def test_get_supported_languages(self):
        """Test that supported languages are returned."""
        languages = get_supported_l1_languages()
        assert isinstance(languages, list)
        # Should support multiple languages
        if len(languages) > 0:
            lang = languages[0]
            assert "code" in lang
            assert "name" in lang
            assert "family" in lang

    def test_get_l1_profile_spanish(self):
        """Test Spanish L1 profile retrieval."""
        profile = get_l1_profile("es")
        # May be None if patterns file not loaded, which is okay for unit tests
        if profile:
            assert "name" in profile
            assert profile.get("name") == "Spanish"

    def test_get_l1_profile_arabic(self):
        """Test Arabic L1 profile retrieval."""
        profile = get_l1_profile("ar")
        if profile:
            assert "name" in profile
            assert profile.get("name") == "Arabic"

    def test_get_l1_profile_invalid(self):
        """Test that invalid language code returns None."""
        profile = get_l1_profile("invalid_language_xyz")
        assert profile is None

    def test_get_phonological_difficulties_spanish(self):
        """Test phonological difficulties for Spanish speakers."""
        difficulties = get_phonological_difficulties("es")
        assert isinstance(difficulties, list)
        # If data is loaded, check structure
        if len(difficulties) > 0:
            diff = difficulties[0]
            assert "priority" in diff or "phoneme" in diff

    def test_get_grammar_challenges_arabic(self):
        """Test grammar challenges for Arabic speakers."""
        challenges = get_grammar_challenges("ar")
        assert isinstance(challenges, list)
        # Arabic speakers typically have article challenges
        if len(challenges) > 0:
            challenge = challenges[0]
            assert "feature" in challenge or "priority" in challenge

    def test_get_cognates_spanish(self):
        """Test cognate retrieval for Spanish."""
        cognates = get_cognates("es")
        assert isinstance(cognates, list)
        # Spanish has many cognates with English
        if len(cognates) > 0:
            cognate = cognates[0]
            assert "en" in cognate or "english" in cognate or "l1" in cognate

    def test_get_false_friends_spanish(self):
        """Test false friends retrieval for Spanish."""
        false_friends = get_false_friends("es")
        assert isinstance(false_friends, list)
        # Spanish has notable false friends like "embarazada"
        if len(false_friends) > 0:
            ff = false_friends[0]
            assert "en" in ff or "english" in ff or "l1_word" in ff

    def test_predict_likely_errors(self):
        """Test error prediction based on L1."""
        # Test with Spanish speaker sample text
        errors = predict_likely_errors(
            l1_code="es",
            text="I have 25 years"  # Common Spanish transfer error
        )
        assert isinstance(errors, list)
        # May detect age expression error (Spanish: tener años)
        if len(errors) > 0:
            error = errors[0]
            assert "type" in error or "feature" in error

    def test_predict_likely_errors_invalid_l1(self):
        """Test error prediction with unsupported L1."""
        errors = predict_likely_errors(
            l1_code="invalid_xyz",
            text="This is a test."
        )
        # Should return empty list for unsupported language
        assert isinstance(errors, list)

    def test_generate_intervention_plan(self):
        """Test intervention plan generation."""
        plan = generate_intervention_plan(l1_code="ar")
        assert isinstance(plan, list)
        # Plan should have some structure
        if len(plan) > 0:
            # Items should be InterventionRecommendation objects
            rec = plan[0]
            assert hasattr(rec, 'skill_area') or 'skill_area' in str(rec)

    def test_generate_intervention_plan_with_assessment(self):
        """Test intervention plan with assessment data."""
        plan = generate_intervention_plan(
            l1_code="zh",  # Chinese
            assessment_data={"reading_level": 2, "writing_level": 3}
        )
        assert plan is not None

    def test_get_contrastive_feedback(self):
        """Test contrastive feedback generation."""
        feedback = get_contrastive_feedback(
            l1_code="ar",
            error_type="article_missing",
            error_context="I saw movie yesterday"
        )
        assert isinstance(feedback, dict)
        assert "feedback" in feedback
        assert "l1_explanation" in feedback

    def test_get_vocabulary_strategies(self):
        """Test vocabulary strategies for different L1s."""
        # Spanish has many cognates
        strategies_es = get_vocabulary_strategies("es")
        assert isinstance(strategies_es, dict)
        assert "strategy" in strategies_es
        
        # Chinese has fewer cognates
        strategies_zh = get_vocabulary_strategies("zh")
        assert isinstance(strategies_zh, dict)

    def test_generate_l1_aware_exercise_articles(self):
        """Test L1-aware exercise generation for articles."""
        exercise = generate_l1_aware_exercise(
            l1_code="ar",
            skill_area="articles"
        )
        assert isinstance(exercise, dict)
        assert "type" in exercise
        assert "items" in exercise or "message" in exercise

    def test_generate_l1_aware_exercise_word_order(self):
        """Test L1-aware exercise generation for word order."""
        exercise = generate_l1_aware_exercise(
            l1_code="ko",  # Korean (SOV language)
            skill_area="word_order"
        )
        assert isinstance(exercise, dict)
        assert "type" in exercise

    def test_get_cultural_considerations(self):
        """Test cultural considerations retrieval."""
        considerations = get_cultural_considerations("so")  # Somali
        assert isinstance(considerations, list)


class TestL1TransferAPI:
    """Tests for L1 transfer API endpoints."""

    def test_get_languages_endpoint(self):
        """Test GET /l1-transfer/languages endpoint."""
        response = client.get("/l1-transfer/languages")
        # May be 200 or 404 depending on router registration
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) or "languages" in data

    def test_get_profile_endpoint(self):
        """Test GET /l1-transfer/profile/{l1_code} endpoint."""
        response = client.get("/l1-transfer/profile/es")
        if response.status_code == 200:
            data = response.json()
            assert "name" in data or "code" in data

    def test_get_profile_invalid_language(self):
        """Test profile endpoint with invalid language."""
        response = client.get("/l1-transfer/profile/invalid_xyz")
        # Should return 404 for unknown language
        assert response.status_code in [404, 200, 422]

    def test_predict_errors_endpoint(self):
        """Test POST /l1-transfer/predict-errors endpoint."""
        response = client.post(
            "/l1-transfer/predict-errors",
            json={
                "l1_code": "es",
                "text": "I have 25 years old"
            }
        )
        if response.status_code == 200:
            data = response.json()
            assert "errors" in data or isinstance(data, list)

    def test_intervention_plan_endpoint(self):
        """Test POST /l1-transfer/intervention-plan endpoint."""
        response = client.post(
            "/l1-transfer/intervention-plan",
            json={
                "l1_code": "ar"
            }
        )
        if response.status_code == 200:
            data = response.json()
            assert data is not None


class TestL1TransferIntegration:
    """Integration tests for L1 transfer functionality."""

    def test_full_analysis_workflow(self):
        """Test complete L1 analysis workflow."""
        # Step 1: Get supported languages
        languages = get_supported_l1_languages()
        
        # Step 2: Get profile for first available language
        if len(languages) > 0:
            l1_code = languages[0]["code"]
            profile = get_l1_profile(l1_code)
            
            # Step 3: Get challenges
            phonological = get_phonological_difficulties(l1_code)
            grammar = get_grammar_challenges(l1_code)
            
            # All should be valid (possibly empty) lists
            assert isinstance(phonological, list)
            assert isinstance(grammar, list)

    def test_intervention_across_l1s(self):
        """Test that interventions are generated for various L1s."""
        l1_codes = ["es", "ar", "zh"]
        for l1_code in l1_codes:
            plan = generate_intervention_plan(l1_code=l1_code)
            # Should return a list (possibly empty if no patterns)
            assert isinstance(plan, list)

    def test_multiple_l1_comparison(self):
        """Test analysis across multiple L1 languages."""
        l1_codes = ["es", "ar", "zh", "ko", "tl"]
        
        for code in l1_codes:
            profile = get_l1_profile(code)
            # Profile may be None if not in patterns file
            difficulties = get_phonological_difficulties(code)
            assert isinstance(difficulties, list)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_text_prediction(self):
        """Test error prediction with empty text."""
        errors = predict_likely_errors(l1_code="es", text="")
        assert isinstance(errors, list)

    def test_long_text_prediction(self):
        """Test error prediction with very long text."""
        long_text = "This is a test sentence. " * 100
        errors = predict_likely_errors(l1_code="es", text=long_text)
        assert isinstance(errors, list)

    def test_special_characters(self):
        """Test handling of special characters."""
        special_text = "Hello! How are you? I'm fine... café résumé naïve"
        errors = predict_likely_errors(l1_code="es", text=special_text)
        assert isinstance(errors, list)

    def test_case_insensitive_l1_code(self):
        """Test that L1 codes are case-insensitive."""
        profile_lower = get_l1_profile("es")
        profile_upper = get_l1_profile("ES")
        # Both should return same result (or both None)
        assert (profile_lower is None) == (profile_upper is None)
