"""
SLIFE Content & Pathways API

Endpoints for accessing content and creating learning pathways
for Students with Limited or Interrupted Formal Education.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

from app.services.slife import (
    get_slife_overview,
    get_all_passages,
    get_passage_by_id,
    get_passages_by_level,
    get_passages_by_topic,
    get_passages_by_age_range,
    get_topic_categories,
    get_scaffolding_strategies,
    get_school_readiness_skills,
    assess_slife_status,
    create_learning_pathway,
    get_vocabulary_by_topic,
    get_level_progression_criteria
)

router = APIRouter(prefix="/v1/slife")


class SLIFEAssessmentRequest(BaseModel):
    """Request to assess SLIFE status."""
    age: int = Field(..., ge=5, le=21, description="Student's age")
    grade: str = Field(..., description="Current grade placement")
    years_schooling: int = Field(..., ge=0, description="Years of formal schooling")
    l1_literacy: str = Field(..., description="L1 literacy: none, limited, functional, strong")
    arrival_date: Optional[str] = Field(None, description="Date of arrival in Canada")


class PathwayRequest(BaseModel):
    """Request to create a learning pathway."""
    student_id: str = Field(..., description="Student identifier")
    current_level: int = Field(..., ge=1, le=3, description="Current reading level 1-3")
    age: int = Field(..., ge=5, le=21, description="Student's age")
    priority_topics: List[str] = Field(
        default=["school_orientation", "daily_life"],
        description="Topics to prioritize"
    )
    l1: str = Field(default="en", description="First language code")


# Overview and Information

@router.get("/overview")
async def get_overview():
    """
    Get overview information about SLIFE students and content approach.
    
    Explains:
    - What SLIFE means
    - Key challenges these students face
    - Content design principles
    - Available reading levels
    """
    return get_slife_overview()


@router.get("/topics")
async def list_topic_categories():
    """
    Get all SLIFE content topic categories.
    
    Topics include school orientation, daily life, health, family,
    Canadian culture, employment, and more.
    """
    categories = get_topic_categories()
    return {
        "categories": categories,
        "count": len(categories)
    }


@router.get("/scaffolding")
async def get_scaffolding():
    """
    Get scaffolding strategies for SLIFE instruction.
    
    Returns visual, language, and comprehension support strategies.
    """
    return get_scaffolding_strategies()


@router.get("/school-readiness")
async def get_school_readiness():
    """
    Get school readiness skills that SLIFE students may need to learn.
    
    Includes skills like using a pencil, following a schedule,
    raising hand, using a computer, etc.
    """
    return get_school_readiness_skills()


@router.get("/progression-criteria")
async def get_progression():
    """
    Get criteria for advancing between SLIFE reading levels.
    
    Describes what students need to demonstrate to move from
    Level 1 → 2 → 3 → grade-level content.
    """
    return get_level_progression_criteria()


# Content Access

@router.get("/passages")
async def list_passages(
    level: Optional[int] = Query(None, ge=1, le=3, description="Filter by level 1-3"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
    min_age: Optional[int] = Query(None, ge=5, description="Minimum age"),
    max_age: Optional[int] = Query(None, le=21, description="Maximum age")
):
    """
    Get SLIFE reading passages with optional filters.
    
    Passages are designed to be age-appropriate but at low reading levels,
    suitable for older students who are still developing basic literacy.
    """
    passages = get_all_passages()
    
    if level is not None:
        passages = [p for p in passages if p.get("level") == level]
    
    if topic is not None:
        passages = [p for p in passages if p.get("topic", "").lower() == topic.lower()]
    
    if min_age is not None and max_age is not None:
        age_appropriate = get_passages_by_age_range(min_age, max_age)
        passage_ids = {p.get("id") for p in age_appropriate}
        passages = [p for p in passages if p.get("id") in passage_ids]
    
    return {
        "passages": passages,
        "count": len(passages)
    }


@router.get("/passages/{passage_id}")
async def get_passage(passage_id: str):
    """
    Get a specific SLIFE passage by ID.
    
    Includes full text, vocabulary, skills, and discussion questions.
    """
    passage = get_passage_by_id(passage_id)
    if not passage:
        raise HTTPException(status_code=404, detail=f"Passage '{passage_id}' not found")
    return passage


@router.get("/vocabulary/{topic}")
async def get_topic_vocabulary(topic: str):
    """
    Get vocabulary words for a specific topic.
    
    Returns all vocabulary from passages in that topic category.
    """
    vocab = get_vocabulary_by_topic(topic)
    if not vocab.get("vocabulary"):
        raise HTTPException(status_code=404, detail=f"No vocabulary found for topic '{topic}'")
    return vocab


# Assessment and Pathways

@router.post("/assess")
async def assess_slife(request: SLIFEAssessmentRequest):
    """
    Assess whether a student may be SLIFE and get recommendations.
    
    Analyzes:
    - Schooling gap (years of schooling vs. expected for grade)
    - L1 literacy level
    - Age-grade mismatch
    
    Returns classification (likely/possible/not SLIFE), recommended
    reading level, and instructional recommendations.
    """
    result = assess_slife_status(
        age=request.age,
        grade=request.grade,
        years_schooling=request.years_schooling,
        l1_literacy=request.l1_literacy,
        arrival_date=request.arrival_date
    )
    return result


@router.post("/pathway")
async def create_pathway(request: PathwayRequest):
    """
    Create a personalized learning pathway for a SLIFE student.
    
    Generates a sequenced set of passages and activities based on
    the student's current level, age, and priority topics.
    
    Returns:
    - Ordered units with passages
    - Estimated sessions and weeks
    - Progress checkpoints
    - Scaffolding suggestions
    """
    pathway = create_learning_pathway(
        student_id=request.student_id,
        current_level=request.current_level,
        age=request.age,
        priority_topics=request.priority_topics,
        l1=request.l1
    )
    return pathway


# Summary

@router.get("/summary")
async def get_slife_summary():
    """
    Get overview of the SLIFE Content & Pathways system.
    """
    passages = get_all_passages()
    categories = get_topic_categories()
    
    # Count by level
    level_counts = {1: 0, 2: 0, 3: 0}
    for p in passages:
        level = p.get("level", 0)
        if level in level_counts:
            level_counts[level] += 1
    
    return {
        "system": "SLIFE Content & Pathways",
        "purpose": "Age-appropriate, low-reading-level content for students with limited/interrupted formal education",
        "total_passages": len(passages),
        "passages_by_level": level_counts,
        "topic_categories": len(categories),
        "features": [
            "SLIFE status assessment",
            "Personalized learning pathways",
            "Age-appropriate but accessible content",
            "School readiness skills curriculum",
            "Level progression criteria",
            "Topic-based vocabulary lists"
        ],
        "alberta_context": [
            "Supports newcomer students from refugee backgrounds",
            "Addresses foundational literacy gaps",
            "Provides age-appropriate content for older learners",
            "Includes Canadian cultural content"
        ],
        "reading_levels": {
            "level_1": "Emergent - single words and simple phrases",
            "level_2": "Early - simple sentences with picture support",
            "level_3": "Transitional - short paragraphs, developing fluency"
        },
        "endpoints": {
            "overview": "/v1/slife/overview",
            "passages": "/v1/slife/passages",
            "assessment": "/v1/slife/assess",
            "pathway": "/v1/slife/pathway",
            "topics": "/v1/slife/topics",
            "vocabulary": "/v1/slife/vocabulary/{topic}"
        }
    }
