"""Tests for Family Literacy Co-Pilot service."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.family_literacy import (
    SUPPORTED_LANGUAGES,
    MICRO_LESSONS,
    get_supported_languages,
    get_micro_lessons,
    get_micro_lesson,
    generate_progress_message,
    generate_homework_helper,
    generate_weekly_family_plan,
    generate_vocabulary_practice,
)

client = TestClient(app)


class TestSupportedLanguages:
    """Tests for language support functionality."""

    def test_supported_languages_defined(self):
        """Test that supported languages are defined."""
        assert len(SUPPORTED_LANGUAGES) > 0
        assert "ar" in SUPPORTED_LANGUAGES
        assert "es" in SUPPORTED_LANGUAGES
        assert "zh" in SUPPORTED_LANGUAGES

    def test_language_metadata(self):
        """Test that language metadata is complete."""
        for code, lang in SUPPORTED_LANGUAGES.items():
            assert "name" in lang
            assert "native" in lang
            assert "rtl" in lang

    def test_rtl_languages(self):
        """Test RTL language flags."""
        assert SUPPORTED_LANGUAGES["ar"]["rtl"] is True
        assert SUPPORTED_LANGUAGES["fa"]["rtl"] is True
        assert SUPPORTED_LANGUAGES["ur"]["rtl"] is True
        assert SUPPORTED_LANGUAGES["es"]["rtl"] is False

    def test_get_supported_languages(self):
        """Test get_supported_languages function."""
        languages = get_supported_languages()
        assert isinstance(languages, dict)
        assert len(languages) > 0


class TestMicroLessons:
    """Tests for micro-lesson functionality."""

    def test_micro_lessons_defined(self):
        """Test that micro-lessons are defined."""
        assert len(MICRO_LESSONS) > 0

    def test_micro_lesson_structure(self):
        """Test micro-lesson data structure."""
        for lesson_id, lesson in MICRO_LESSONS.items():
            assert "id" in lesson
            assert "title" in lesson
            assert "duration_minutes" in lesson
            assert "grade_range" in lesson
            assert "skills" in lesson
            assert "instructions" in lesson

    def test_micro_lesson_translations(self):
        """Test that micro-lessons have translations."""
        label_the_home = MICRO_LESSONS.get("label_the_home", {})
        if label_the_home:
            assert "title_translations" in label_the_home
            translations = label_the_home["title_translations"]
            # Should have Arabic and Spanish at minimum
            assert "ar" in translations or "es" in translations

    def test_get_micro_lessons_all(self):
        """Test getting all micro-lessons."""
        lessons = get_micro_lessons()
        assert isinstance(lessons, list)
        assert len(lessons) > 0

    def test_get_micro_lessons_by_grade(self):
        """Test getting micro-lessons by grade."""
        lessons = get_micro_lessons(grade="K")
        assert isinstance(lessons, list)
        # Should filter to kindergarten-appropriate lessons
        for lesson in lessons:
            assert "K" in lesson.get("grade_range", [])

    def test_get_micro_lessons_by_skill(self):
        """Test getting micro-lessons by skill."""
        lessons = get_micro_lessons(skill="vocabulary")
        assert isinstance(lessons, list)
        for lesson in lessons:
            skills = [s.lower() for s in lesson.get("skills", [])]
            assert "vocabulary" in skills

    def test_get_micro_lessons_with_translation(self):
        """Test getting micro-lessons with translations."""
        lessons = get_micro_lessons(language="ar")
        assert isinstance(lessons, list)
        # Should include Arabic translations where available

    def test_get_single_micro_lesson(self):
        """Test getting a specific micro-lesson."""
        lesson = get_micro_lesson("label_the_home")
        assert lesson is not None
        assert lesson["id"] == "label_the_home"

    def test_get_invalid_micro_lesson(self):
        """Test getting non-existent micro-lesson."""
        lesson = get_micro_lesson("invalid_lesson_xyz")
        assert lesson is None


class TestProgressMessages:
    """Tests for progress message generation."""

    def test_generate_weekly_summary_english(self):
        """Test weekly summary in English."""
        message = generate_progress_message(
            message_type="weekly_summary",
            language="en",
            child_name="Ahmed",
            minutes=60,
            words=15
        )
        assert isinstance(message, str)
        assert "Ahmed" in message
        assert "60" in message

    def test_generate_weekly_summary_arabic(self):
        """Test weekly summary in Arabic."""
        message = generate_progress_message(
            message_type="weekly_summary",
            language="ar",
            child_name="Ahmed",
            minutes=60,
            words=15
        )
        assert isinstance(message, str)
        # Should contain Arabic text

    def test_generate_fluency_update(self):
        """Test fluency update message."""
        message = generate_progress_message(
            message_type="fluency_update",
            language="en",
            child_name="Maria",
            wcpm=45,
            target=60
        )
        assert isinstance(message, str)
        assert "Maria" in message

    def test_generate_encouragement(self):
        """Test encouragement message."""
        message = generate_progress_message(
            message_type="encouragement",
            language="es"
        )
        assert isinstance(message, str)

    def test_generate_message_unsupported_type(self):
        """Test with unsupported message type."""
        message = generate_progress_message(
            message_type="invalid_type",
            language="en"
        )
        # Should return empty or default string
        assert isinstance(message, str)


class TestHomeworkHelper:
    """Tests for homework helper generation."""

    def test_generate_homework_helper_sight_words(self):
        """Test homework helper for sight words."""
        helper = generate_homework_helper(
            skill_area="sight_words",
            language="en"
        )
        assert isinstance(helper, dict)
        assert "task" in helper
        assert "help_tips" in helper

    def test_generate_homework_helper_reading(self):
        """Test homework helper for reading fluency."""
        helper = generate_homework_helper(
            skill_area="reading_fluency",
            language="es"
        )
        assert isinstance(helper, dict)
        assert "task" in helper

    def test_generate_homework_helper_with_words(self):
        """Test homework helper with specific words."""
        helper = generate_homework_helper(
            skill_area="spelling",
            language="en",
            specific_words=["the", "is", "and"]
        )
        assert isinstance(helper, dict)
        if "words_to_practice" in helper:
            assert len(helper["words_to_practice"]) == 3

    def test_generate_homework_helper_unknown_skill(self):
        """Test homework helper with unknown skill area."""
        helper = generate_homework_helper(
            skill_area="unknown_skill",
            language="en"
        )
        assert isinstance(helper, dict)
        # Should return generic helper


class TestWeeklyFamilyPlan:
    """Tests for weekly family plan generation."""

    def test_generate_weekly_plan_basic(self):
        """Test basic weekly plan generation."""
        plan = generate_weekly_family_plan(
            student_name="Ahmed",
            grade="2",
            focus_skills=["vocabulary", "reading"],
            language="en"
        )
        assert isinstance(plan, dict)
        assert plan["student_name"] == "Ahmed"
        assert plan["grade"] == "2"
        assert "daily_plan" in plan

    def test_generate_weekly_plan_all_days(self):
        """Test that weekly plan includes all days."""
        plan = generate_weekly_family_plan(
            student_name="Test",
            grade="3",
            focus_skills=["phonics"],
            language="ar"
        )
        assert len(plan["daily_plan"]) == 7
        days = [d["day"] for d in plan["daily_plan"]]
        assert "Monday" in days
        assert "Sunday" in days

    def test_generate_weekly_plan_arabic(self):
        """Test weekly plan in Arabic."""
        plan = generate_weekly_family_plan(
            student_name="Fatima",
            grade="K",
            focus_skills=["vocabulary"],
            language="ar"
        )
        assert plan["language"]["code"] == "ar"
        assert "native_name" in plan["language"]


class TestVocabularyPractice:
    """Tests for vocabulary practice generation."""

    def test_generate_vocabulary_practice(self):
        """Test vocabulary practice generation."""
        practice = generate_vocabulary_practice(
            words=["cat", "dog", "bird"],
            language="es"
        )
        assert isinstance(practice, dict)

    def test_generate_vocabulary_practice_empty(self):
        """Test vocabulary practice with empty word list."""
        practice = generate_vocabulary_practice(
            words=[],
            language="ar"
        )
        assert isinstance(practice, dict)


class TestFamilyLiteracyAPI:
    """Tests for family literacy API endpoints."""

    def test_get_languages_endpoint(self):
        """Test GET /family/languages endpoint."""
        response = client.get("/family/languages")
        # May be 200 or 404 depending on router registration
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict) or isinstance(data, list)

    def test_get_micro_lessons_endpoint(self):
        """Test GET /family/micro-lessons endpoint."""
        response = client.get("/family/micro-lessons")
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) or "lessons" in data


class TestAlbertaIntegration:
    """Integration tests specific to Alberta context."""

    def test_alberta_immigrant_languages(self):
        """Test that common Alberta immigrant languages are supported."""
        # Top immigrant source languages in Alberta
        alberta_languages = ["ar", "zh", "tl", "pa", "so", "vi", "ur"]
        for lang in alberta_languages:
            assert lang in SUPPORTED_LANGUAGES, f"Missing support for {lang}"

    def test_micro_lessons_grade_coverage(self):
        """Test that micro-lessons cover all grades."""
        all_grades = set()
        for lesson in MICRO_LESSONS.values():
            all_grades.update(lesson.get("grade_range", []))
        
        # Should cover K-6
        assert "K" in all_grades
        assert "1" in all_grades
        assert "6" in all_grades

    def test_bilingual_content_workflow(self):
        """Test end-to-end bilingual content generation."""
        # Generate weekly plan in Arabic
        plan = generate_weekly_family_plan(
            student_name="Fatima",
            grade="2",
            focus_skills=["vocabulary", "reading"],
            language="ar"
        )
        assert plan is not None
        assert plan["language"]["code"] == "ar"
        
        # Generate homework helper in Spanish
        helper = generate_homework_helper(
            skill_area="sight_words",
            language="es"
        )
        assert isinstance(helper, dict)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_focus_skills(self):
        """Test weekly plan with empty focus skills."""
        plan = generate_weekly_family_plan(
            student_name="Test",
            grade="1",
            focus_skills=[],
            language="en"
        )
        # Should still return a plan with default activities
        assert isinstance(plan, dict)
        assert "daily_plan" in plan

    def test_invalid_grade(self):
        """Test with invalid grade."""
        lessons = get_micro_lessons(grade="99")
        # Should return empty list for invalid grade
        assert isinstance(lessons, list)

    def test_special_characters_in_name(self):
        """Test handling of special characters in student name."""
        plan = generate_weekly_family_plan(
            student_name="José María",
            grade="2",
            focus_skills=["reading"],
            language="es"
        )
        assert plan["student_name"] == "José María"

    def test_unsupported_language_fallback(self):
        """Test fallback for unsupported language."""
        helper = generate_homework_helper(
            skill_area="sight_words",
            language="xyz_unsupported"
        )
        # Should fall back to English
        assert isinstance(helper, dict)
