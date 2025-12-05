"""
Cultural Responsiveness API Endpoints

Provides endpoints for cultural context, teaching recommendations,
and culturally responsive pedagogy support.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.services.cultural_responsiveness import (
    get_supported_cultures,
    get_cultural_profile,
    get_educational_context,
    get_communication_norms,
    get_cultural_celebrations,
    get_dietary_considerations,
    get_family_structure_info,
    get_trauma_considerations,
    get_teaching_recommendations,
    generate_cultural_brief,
    search_cultures
)

router = APIRouter(prefix="/v1/cultural")


# Response Models
class CultureInfo(BaseModel):
    """Basic culture information."""
    code: str
    name: str
    region: str
    languages: List[str] = []


class CommunicationNorms(BaseModel):
    """Communication norms for a culture."""
    eye_contact: str = ""
    personal_space: str = ""
    authority_interaction: str = ""
    gender_dynamics: str = ""
    nonverbal_cues: List[str] = []
    tips: List[str] = []


class Celebration(BaseModel):
    """Cultural celebration or observance."""
    name: str
    timing: str = ""
    significance: str = ""
    school_implications: str = ""


class TeachingRecommendations(BaseModel):
    """Culturally responsive teaching recommendations."""
    do: List[str] = []
    avoid: List[str] = []
    conversation_starters: List[str] = []
    classroom_modifications: List[str] = []


class CulturalBriefRequest(BaseModel):
    """Request for a cultural brief."""
    culture_code: str = Field(..., description="Culture code")
    focus_areas: Optional[List[str]] = Field(
        None,
        description="Areas to include: education, communication, family, celebrations, dietary, trauma, teaching"
    )


# Endpoints
@router.get("/cultures", response_model=List[CultureInfo])
async def list_cultures():
    """Get list of all supported cultural backgrounds."""
    return get_supported_cultures()


@router.get("/cultures/{culture_code}")
async def get_culture(culture_code: str):
    """Get complete profile for a specific culture."""
    profile = get_cultural_profile(culture_code)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Culture '{culture_code}' not found")
    return profile


@router.get("/cultures/{culture_code}/education")
async def get_education_info(culture_code: str):
    """Get educational context for a culture."""
    context = get_educational_context(culture_code)
    if not context:
        raise HTTPException(status_code=404, detail=f"Culture '{culture_code}' not found")
    return context


@router.get("/cultures/{culture_code}/communication", response_model=CommunicationNorms)
async def get_communication_info(culture_code: str):
    """Get communication norms for a culture."""
    norms = get_communication_norms(culture_code)
    if not norms:
        raise HTTPException(status_code=404, detail=f"Culture '{culture_code}' not found")
    return norms


@router.get("/cultures/{culture_code}/celebrations", response_model=List[Celebration])
async def get_celebrations(culture_code: str):
    """Get cultural celebrations and observances."""
    celebrations = get_cultural_celebrations(culture_code)
    return celebrations


@router.get("/cultures/{culture_code}/dietary")
async def get_dietary_info(culture_code: str):
    """Get dietary considerations for a culture."""
    dietary = get_dietary_considerations(culture_code)
    if not dietary:
        raise HTTPException(status_code=404, detail=f"Culture '{culture_code}' not found")
    return dietary


@router.get("/cultures/{culture_code}/family")
async def get_family_info(culture_code: str):
    """Get family structure information for a culture."""
    family = get_family_structure_info(culture_code)
    if not family:
        raise HTTPException(status_code=404, detail=f"Culture '{culture_code}' not found")
    return family


@router.get("/cultures/{culture_code}/trauma")
async def get_trauma_info(culture_code: str):
    """Get trauma-informed considerations for a culture."""
    trauma = get_trauma_considerations(culture_code)
    return trauma


@router.get("/cultures/{culture_code}/teaching", response_model=TeachingRecommendations)
async def get_teaching_info(culture_code: str):
    """Get culturally responsive teaching recommendations."""
    recommendations = get_teaching_recommendations(culture_code)
    if not recommendations:
        raise HTTPException(status_code=404, detail=f"Culture '{culture_code}' not found")
    return recommendations


@router.post("/brief")
async def create_cultural_brief(request: CulturalBriefRequest):
    """Generate a comprehensive cultural brief."""
    brief = generate_cultural_brief(
        culture_code=request.culture_code,
        focus_areas=request.focus_areas
    )
    if "error" in brief:
        raise HTTPException(status_code=404, detail=brief["error"])
    return brief


@router.get("/search")
async def search_for_cultures(
    q: str = Query(..., min_length=1, description="Search query")
):
    """Search cultures by name, region, or language."""
    results = search_cultures(q)
    return results
