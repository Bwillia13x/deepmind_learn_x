"""
Family Literacy Co-Pilot API

Endpoints for family engagement in literacy development.
Bridges the home-school gap with bilingual support.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

from app.services.family_literacy import (
    get_supported_languages,
    get_micro_lessons,
    get_micro_lesson,
    generate_progress_message,
    generate_homework_helper,
    generate_weekly_family_plan,
    generate_vocabulary_practice,
    generate_sms_message,
    get_family_resources
)

router = APIRouter(prefix="/v1/family")


class WeeklyPlanRequest(BaseModel):
    """Request for weekly family literacy plan."""
    student_name: str = Field(..., description="Child's name")
    grade: str = Field(..., description="Current grade level")
    focus_skills: List[str] = Field(
        default=["reading", "vocabulary"],
        description="Skills to focus on"
    )
    language: str = Field(default="en", description="Parent's language code")


class ProgressMessageRequest(BaseModel):
    """Request for progress message generation."""
    message_type: str = Field(..., description="Type: weekly_summary, fluency_update, encouragement")
    language: str = Field(default="en", description="Target language")
    child_name: str = Field(..., description="Child's name")
    minutes: Optional[int] = Field(None, description="Minutes practiced")
    words: Optional[int] = Field(None, description="Words learned")
    wcpm: Optional[int] = Field(None, description="Words correct per minute")
    target: Optional[int] = Field(None, description="Target WCPM")


class HomeworkHelperRequest(BaseModel):
    """Request for homework help instructions."""
    skill_area: str = Field(..., description="Skill: sight_words, reading_fluency, spelling")
    language: str = Field(default="en", description="Parent's language")
    specific_words: Optional[List[str]] = Field(None, description="Words to practice")


class VocabularyPracticeRequest(BaseModel):
    """Request for vocabulary practice activities."""
    words: List[str] = Field(..., description="English words to practice")
    language: str = Field(default="en", description="Parent's language")


class SMSRequest(BaseModel):
    """Request for SMS message generation."""
    message_type: str = Field(..., description="Type: practice_reminder, achievement, weekly_words")
    language: str = Field(default="en", description="Target language")
    child_name: Optional[str] = None
    words: Optional[str] = None


# Language Support

@router.get("/languages")
async def list_supported_languages():
    """
    Get list of supported parent languages.
    
    These are the languages available for family communications.
    """
    languages = get_supported_languages()
    return {
        "supported_languages": [
            {
                "code": code,
                "name": info["name"],
                "native_name": info["native"],
                "rtl": info.get("rtl", False)
            }
            for code, info in languages.items()
        ],
        "count": len(languages)
    }


# Micro-Lessons

@router.get("/micro-lessons")
async def list_micro_lessons(
    grade: Optional[str] = Query(None, description="Filter by grade level"),
    skill: Optional[str] = Query(None, description="Filter by skill"),
    language: str = Query("en", description="Language for translations")
):
    """
    Get family micro-lessons.
    
    These are simple 5-15 minute activities families can do together
    to support literacy development at home.
    """
    lessons = get_micro_lessons(grade=grade, skill=skill, language=language)
    return {
        "lessons": lessons,
        "count": len(lessons),
        "language": language
    }


@router.get("/micro-lessons/{lesson_id}")
async def get_lesson(
    lesson_id: str,
    language: str = Query("en", description="Language for translations")
):
    """
    Get a specific micro-lesson by ID.
    """
    lesson = get_micro_lesson(lesson_id, language)
    if not lesson:
        raise HTTPException(status_code=404, detail=f"Lesson '{lesson_id}' not found")
    return lesson


# Weekly Planning

@router.post("/weekly-plan")
async def create_weekly_plan(request: WeeklyPlanRequest):
    """
    Generate a weekly family literacy plan.
    
    Creates a 7-day plan with daily activities tailored to the
    student's grade and focus skills, with instructions in
    the parent's language.
    """
    plan = generate_weekly_family_plan(
        student_name=request.student_name,
        grade=request.grade,
        focus_skills=request.focus_skills,
        language=request.language
    )
    return plan


# Progress Communication

@router.post("/progress-message")
async def create_progress_message(request: ProgressMessageRequest):
    """
    Generate a progress message in the parent's language.
    
    Use this to communicate student progress to families who
    may not be fluent in English.
    """
    kwargs: Dict[str, Any] = {
        "child_name": request.child_name
    }
    if request.minutes is not None:
        kwargs["minutes"] = request.minutes
    if request.words is not None:
        kwargs["words"] = request.words
    if request.wcpm is not None:
        kwargs["wcpm"] = request.wcpm
    if request.target is not None:
        kwargs["target"] = request.target
    
    message = generate_progress_message(
        message_type=request.message_type,
        language=request.language,
        **kwargs
    )
    
    return {
        "message": message,
        "message_type": request.message_type,
        "language": request.language
    }


@router.get("/progress-message-types")
async def list_progress_message_types():
    """List available progress message types."""
    return {
        "message_types": [
            {
                "type": "weekly_summary",
                "description": "Weekly practice summary",
                "required_fields": ["child_name", "minutes", "words"]
            },
            {
                "type": "fluency_update",
                "description": "Fluency progress update",
                "required_fields": ["child_name", "wcpm", "target"]
            },
            {
                "type": "encouragement",
                "description": "General encouragement message",
                "required_fields": []
            },
            {
                "type": "homework_help",
                "description": "Homework assistance message",
                "required_fields": ["homework", "help_tips"]
            }
        ]
    }


# Homework Help

@router.post("/homework-helper")
async def create_homework_helper(request: HomeworkHelperRequest):
    """
    Generate homework help instructions for parents.
    
    Provides step-by-step instructions in the parent's language
    for helping with specific homework tasks.
    """
    helper = generate_homework_helper(
        skill_area=request.skill_area,
        language=request.language,
        specific_words=request.specific_words
    )
    return helper


@router.get("/homework-skills")
async def list_homework_skills():
    """List available homework skill areas."""
    return {
        "skill_areas": [
            {"id": "sight_words", "name": "Sight Words Practice"},
            {"id": "reading_fluency", "name": "Reading Aloud"},
            {"id": "spelling", "name": "Spelling Practice"}
        ]
    }


# Vocabulary Practice

@router.post("/vocabulary-practice")
async def create_vocabulary_practice(request: VocabularyPracticeRequest):
    """
    Generate vocabulary practice activities for families.
    
    Creates activities for practicing specific words at home,
    with translations when available.
    """
    practice = generate_vocabulary_practice(
        words=request.words,
        language=request.language
    )
    return practice


# SMS Messages

@router.post("/sms")
async def create_sms_message(request: SMSRequest):
    """
    Generate a short SMS message for parents.
    
    Messages are limited to 160 characters for SMS compatibility.
    Useful for quick reminders and celebrations.
    """
    kwargs = {}
    if request.child_name:
        kwargs["child_name"] = request.child_name
    if request.words:
        kwargs["words"] = request.words
    
    message = generate_sms_message(
        message_type=request.message_type,
        language=request.language,
        **kwargs
    )
    
    return {
        "message": message,
        "character_count": len(message),
        "message_type": request.message_type
    }


@router.get("/sms-types")
async def list_sms_types():
    """List available SMS message types."""
    return {
        "sms_types": [
            {"type": "practice_reminder", "description": "Daily practice reminder"},
            {"type": "achievement", "description": "Goal achievement celebration"},
            {"type": "weekly_words", "description": "Weekly vocabulary words"}
        ]
    }


# Resources

@router.get("/resources")
async def get_resources(
    language: str = Query("en", description="Language for content")
):
    """
    Get family literacy resources and tips.
    
    Provides general advice and resources for supporting
    literacy at home, in the parent's language.
    """
    resources = get_family_resources(language)
    return resources


# Summary

@router.get("/summary")
async def get_family_copilot_summary():
    """
    Get overview of the Family Literacy Co-Pilot.
    """
    languages = get_supported_languages()
    lessons = get_micro_lessons()
    
    return {
        "system": "Family Literacy Co-Pilot",
        "purpose": "Bridge the home-school literacy gap with bilingual support for families",
        "supported_languages": len(languages),
        "available_micro_lessons": len(lessons),
        "features": [
            "Bilingual micro-lessons for home practice",
            "Weekly family literacy plans",
            "Progress messages in parent's language",
            "Homework help instructions",
            "Vocabulary practice activities",
            "SMS notifications for quick updates"
        ],
        "alberta_context": [
            "Supports diverse language communities in Alberta",
            "Addresses parent engagement challenges",
            "Low-barrier activities requiring minimal materials",
            "Builds home-school partnership"
        ],
        "endpoints": {
            "languages": "/v1/family/languages",
            "micro_lessons": "/v1/family/micro-lessons",
            "weekly_plan": "/v1/family/weekly-plan",
            "progress_message": "/v1/family/progress-message",
            "homework_helper": "/v1/family/homework-helper",
            "vocabulary_practice": "/v1/family/vocabulary-practice",
            "sms": "/v1/family/sms",
            "resources": "/v1/family/resources"
        }
    }
