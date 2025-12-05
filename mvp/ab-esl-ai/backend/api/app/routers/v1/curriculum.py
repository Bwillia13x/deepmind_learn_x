"""
Alberta Curriculum Alignment API

Endpoints for mapping student progress to Alberta ELA outcomes
and ESL Proficiency Benchmarks.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from enum import Enum

from app.services.curriculum import (
    get_esl_benchmark_level,
    get_all_benchmark_levels,
    assess_esl_level,
    get_grade_outcomes,
    get_outcomes_by_skill,
    align_assessment_to_outcomes,
    get_benchmark_targets,
    evaluate_fluency_progress,
    generate_progress_report,
    get_canadian_content_themes,
    get_pat_preparation_info,
    get_assessment_tool_info
)

router = APIRouter(prefix="/v1/curriculum")


class AssessmentPeriod(str, Enum):
    fall = "fall"
    winter = "winter"
    spring = "spring"


class ESLLevelRequest(BaseModel):
    """Request to assess ESL level from indicators."""
    wcpm: Optional[int] = Field(None, ge=0, description="Words correct per minute")
    can_follow_directions: Optional[bool] = Field(None, description="Can follow multi-step directions")
    writes_sentences: Optional[bool] = Field(None, description="Can write complete sentences")
    participates_discussions: Optional[bool] = Field(None, description="Participates in class discussions")
    uses_academic_vocab: Optional[bool] = Field(None, description="Uses academic vocabulary")


class AssessmentAlignmentRequest(BaseModel):
    """Request to align an assessment to curriculum outcomes."""
    assessment_type: str = Field(..., description="Type of assessment (e.g., 'orf', 'maze')")
    skills_assessed: List[str] = Field(..., description="Skills measured by the assessment")
    grade: str = Field(..., description="Target grade level")


class FluencyEvaluationRequest(BaseModel):
    """Request to evaluate fluency progress."""
    grade: str = Field(..., description="Grade level")
    wcpm: int = Field(..., ge=0, description="Words correct per minute")
    assessment_period: AssessmentPeriod = Field(AssessmentPeriod.spring, description="Assessment period")
    accuracy: Optional[float] = Field(None, ge=0, le=1, description="Reading accuracy (0-1)")


class AssessmentRecord(BaseModel):
    """Single assessment record."""
    type: str
    date: str
    score: Any
    skills: List[str] = []
    status: Optional[str] = None


class ProgressReportRequest(BaseModel):
    """Request for comprehensive progress report."""
    student_name: str
    grade: str
    esl_level: int = Field(..., ge=1, le=5)
    l1: str = Field(..., description="First language code")
    assessments: List[AssessmentRecord]


# ESL Benchmark Endpoints

@router.get("/esl-benchmarks")
async def get_all_esl_benchmarks():
    """
    Get all ESL proficiency benchmark levels (1-5).
    
    Returns details on expectations for reading, writing, listening,
    and speaking at each proficiency level.
    """
    levels = get_all_benchmark_levels()
    return {
        "description": "Alberta ESL Proficiency Benchmarks for K-12 students",
        "levels": levels
    }


@router.get("/esl-benchmarks/{level}")
async def get_esl_benchmark(level: int):
    """
    Get details for a specific ESL proficiency level.
    
    Args:
        level: ESL level 1-5
    """
    if level < 1 or level > 5:
        raise HTTPException(status_code=400, detail="ESL level must be between 1 and 5")
    
    benchmark = get_esl_benchmark_level(level)
    if not benchmark:
        raise HTTPException(status_code=404, detail=f"Benchmark level {level} not found")
    
    return {
        "level": level,
        **benchmark
    }


@router.post("/esl-level/assess")
async def assess_student_esl_level(request: ESLLevelRequest):
    """
    Estimate a student's ESL proficiency level based on observable indicators.
    
    Provide as many indicators as available for more accurate assessment.
    """
    result = assess_esl_level(
        wcpm=request.wcpm,
        can_follow_directions=request.can_follow_directions,
        writes_sentences=request.writes_sentences,
        participates_discussions=request.participates_discussions,
        uses_academic_vocab=request.uses_academic_vocab
    )
    return result


# Grade Level Outcomes

@router.get("/grades")
async def list_available_grades():
    """List all grade levels with curriculum outcomes."""
    return {
        "grades": ["K", "1", "2", "3", "4", "5", "6"],
        "description": "Alberta ELA outcomes mapped for each grade"
    }


@router.get("/grades/{grade}/outcomes")
async def get_grade_level_outcomes(grade: str):
    """
    Get all curriculum outcomes for a specific grade.
    
    Args:
        grade: Grade level (K, 1, 2, 3, 4, 5, 6)
    """
    outcomes = get_grade_outcomes(grade)
    if not outcomes:
        raise HTTPException(status_code=404, detail=f"No outcomes found for grade {grade}")
    return outcomes


@router.get("/grades/{grade}/benchmarks")
async def get_grade_benchmarks(grade: str):
    """
    Get fluency benchmark targets for a grade level.
    
    Returns WCPM targets for fall, winter, and spring.
    """
    benchmarks = get_benchmark_targets(grade)
    if not benchmarks:
        raise HTTPException(status_code=404, detail=f"No benchmarks found for grade {grade}")
    return {
        "grade": grade,
        "benchmarks": benchmarks
    }


# Skill-Based Search

@router.get("/outcomes/by-skill/{skill}")
async def find_outcomes_by_skill(skill: str):
    """
    Find all curriculum outcomes involving a specific skill.
    
    Args:
        skill: Skill to search for (e.g., "phonics", "fluency", "comprehension")
    """
    outcomes = get_outcomes_by_skill(skill)
    return {
        "skill": skill,
        "matching_outcomes": outcomes,
        "count": len(outcomes)
    }


# Assessment Alignment

@router.post("/assessments/align")
async def align_assessment(request: AssessmentAlignmentRequest):
    """
    Map an assessment to relevant Alberta curriculum outcomes.
    
    Helps teachers understand which outcomes are being measured
    and identify curriculum coverage gaps.
    """
    alignment = align_assessment_to_outcomes(
        assessment_type=request.assessment_type,
        skills_assessed=request.skills_assessed,
        grade=request.grade
    )
    return alignment


@router.post("/fluency/evaluate")
async def evaluate_student_fluency(request: FluencyEvaluationRequest):
    """
    Evaluate a student's fluency against grade-level benchmarks.
    
    Returns status (at/above, approaching, below, well below)
    and recommendations.
    """
    result = evaluate_fluency_progress(
        grade=request.grade,
        wcpm=request.wcpm,
        assessment_period=request.assessment_period.value,
        accuracy=request.accuracy
    )
    return result


# Progress Reports

@router.post("/reports/progress")
async def generate_student_progress_report(request: ProgressReportRequest):
    """
    Generate a comprehensive progress report aligned to Alberta curriculum.
    
    Includes ESL level expectations, benchmark comparison,
    curriculum coverage, and personalized recommendations.
    """
    assessments_dict = [
        {
            "type": a.type,
            "date": a.date,
            "score": a.score,
            "skills": a.skills,
            "status": a.status
        }
        for a in request.assessments
    ]
    
    report = generate_progress_report(
        student_name=request.student_name,
        grade=request.grade,
        esl_level=request.esl_level,
        l1=request.l1,
        assessments=assessments_dict
    )
    return report


# Canadian Content

@router.get("/content/themes")
async def get_content_themes(
    level: str = Query("elementary", description="Content level: elementary or middle_school")
):
    """
    Get Canadian content themes appropriate for the specified level.
    
    Themes include Canadian geography, culture, history, and
    First Nations, Métis, and Inuit perspectives.
    """
    themes = get_canadian_content_themes(level)
    return {
        "level": level,
        "themes": themes
    }


# Assessment Tools

@router.get("/assessment-tools/{tool}")
async def get_assessment_tool(tool: str):
    """
    Get information about an assessment tool.
    
    Args:
        tool: Tool name (orf, maze, psf, lnf)
    """
    tool_info = get_assessment_tool_info(tool)
    if not tool_info:
        raise HTTPException(status_code=404, detail=f"Assessment tool '{tool}' not found")
    return tool_info


@router.get("/assessment-tools")
async def list_assessment_tools():
    """List all available assessment tools."""
    tools = ["orf", "maze", "psf", "lnf"]
    return {
        "tools": [
            {"code": "orf", "name": "Oral Reading Fluency"},
            {"code": "maze", "name": "MAZE Comprehension"},
            {"code": "psf", "name": "Phoneme Segmentation Fluency"},
            {"code": "lnf", "name": "Letter Naming Fluency"}
        ]
    }


# PAT Preparation

@router.get("/pat/{grade}")
async def get_pat_info(grade: str):
    """
    Get Provincial Achievement Test preparation information.
    
    Args:
        grade: Grade level (6 or 9)
    """
    if grade not in ["6", "9"]:
        raise HTTPException(
            status_code=400, 
            detail="PAT information available only for grades 6 and 9"
        )
    
    info = get_pat_preparation_info(grade)
    if not info:
        raise HTTPException(status_code=404, detail=f"PAT info not found for grade {grade}")
    
    return {
        "grade": grade,
        "test": "Provincial Achievement Test - English Language Arts",
        **info
    }


# Summary endpoint

@router.get("/summary")
async def get_curriculum_summary():
    """
    Get a summary of the curriculum alignment system.
    
    Returns overview of available outcomes, benchmarks, and features.
    """
    return {
        "system": "Alberta Curriculum Alignment",
        "features": [
            "ESL Proficiency Benchmarks (Levels 1-5)",
            "Grade-level ELA outcomes (K-6)",
            "Fluency benchmark targets by grade and season",
            "Assessment-to-curriculum alignment",
            "Progress report generation",
            "Canadian content themes",
            "PAT preparation support"
        ],
        "grades_covered": ["K", "1", "2", "3", "4", "5", "6"],
        "esl_levels": 5,
        "endpoints": {
            "esl_benchmarks": "/v1/curriculum/esl-benchmarks",
            "grade_outcomes": "/v1/curriculum/grades/{grade}/outcomes",
            "skill_search": "/v1/curriculum/outcomes/by-skill/{skill}",
            "fluency_evaluation": "/v1/curriculum/fluency/evaluate",
            "progress_reports": "/v1/curriculum/reports/progress"
        }
    }
