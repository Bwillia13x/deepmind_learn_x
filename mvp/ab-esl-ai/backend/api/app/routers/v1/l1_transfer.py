"""L1 Transfer Intelligence API endpoints.

Provides endpoints for L1-specific linguistic analysis, error prediction,
and intervention recommendations.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.services.l1_transfer import (
    get_supported_l1_languages,
    get_l1_profile,
    get_phonological_difficulties,
    get_grammar_challenges,
    get_cognates,
    get_false_friends,
    get_literacy_transfer_info,
    get_cultural_considerations,
    predict_likely_errors,
    generate_intervention_plan,
    get_contrastive_feedback,
    get_vocabulary_strategies,
    generate_l1_aware_exercise,
)

router = APIRouter(prefix="/v1/l1-transfer", tags=["L1 Transfer Intelligence"])


# Response Models
class L1Language(BaseModel):
    """Supported L1 language info."""
    code: str
    name: str
    family: str
    writing_system: str


class PhonologicalDifficulty(BaseModel):
    """Phonological difficulty for an L1."""
    phoneme: str
    issue: str
    priority: str
    minimal_pairs: List[str] = []
    teaching_tip: str = ""


class GrammarChallenge(BaseModel):
    """Grammar challenge for an L1."""
    feature: str
    priority: str
    issue: str
    common_errors: List[str] = []
    teaching_approach: str = ""
    exercises: List[str] = []


class InterventionItem(BaseModel):
    """Intervention recommendation."""
    skill_area: str
    priority: str
    description: str
    exercises: List[str]
    teaching_tip: str
    estimated_focus_weeks: int


class ErrorPrediction(BaseModel):
    """Predicted error based on L1 transfer."""
    type: str
    feature: str
    location: str
    issue: str
    suggestion: str
    l1_explanation: str


class ContrastiveFeedback(BaseModel):
    """L1-aware feedback for an error."""
    error_type: str
    context: str
    feedback: str
    l1_explanation: str
    practice_tip: str
    l1_name: str


class AnalyzeTextRequest(BaseModel):
    """Request to analyze text for L1 transfer errors."""
    text: str = Field(..., description="Text to analyze", min_length=1)
    l1: str = Field(..., description="L1 language code")


class FeedbackRequest(BaseModel):
    """Request for contrastive feedback."""
    l1: str = Field(..., description="L1 language code")
    error_type: str = Field(..., description="Type of error (article_missing, verb_tense, etc.)")
    context: str = Field(..., description="Context where error occurred")


class ExerciseRequest(BaseModel):
    """Request to generate an L1-aware exercise."""
    l1: str = Field(..., description="L1 language code")
    skill_area: str = Field(..., description="Skill area (articles, word_order, verb_tense)")
    difficulty: str = Field(default="medium", description="Difficulty level")


# Endpoints
@router.get("/languages", response_model=List[L1Language])
def list_supported_languages():
    """Get list of supported L1 languages for transfer analysis."""
    return get_supported_l1_languages()


@router.get("/profile/{l1_code}")
def get_language_profile(l1_code: str):
    """Get complete linguistic profile for a language."""
    profile = get_l1_profile(l1_code)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No profile found for L1: {l1_code}")
    return profile


@router.get("/phonology/{l1_code}", response_model=List[PhonologicalDifficulty])
def get_phonology_difficulties(l1_code: str):
    """Get phonological difficulties for speakers of a given L1."""
    difficulties = get_phonological_difficulties(l1_code)
    if not difficulties:
        raise HTTPException(status_code=404, detail=f"No phonology data for L1: {l1_code}")
    return difficulties


@router.get("/grammar/{l1_code}", response_model=List[GrammarChallenge])
def get_grammar_difficulties(l1_code: str):
    """Get grammar challenges for speakers of a given L1."""
    challenges = get_grammar_challenges(l1_code)
    if not challenges:
        raise HTTPException(status_code=404, detail=f"No grammar data for L1: {l1_code}")
    return challenges


@router.get("/cognates/{l1_code}")
def get_language_cognates(l1_code: str):
    """Get English cognates for a given L1 (helpful for vocabulary learning)."""
    profile = get_l1_profile(l1_code)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No profile found for L1: {l1_code}")
    
    return {
        "l1_code": l1_code,
        "l1_name": profile.get("name", l1_code),
        "cognates": get_cognates(l1_code),
        "false_friends": get_false_friends(l1_code),
        "cognate_strategy": profile.get("vocabulary", {}).get("cognate_strategy", "")
    }


@router.get("/literacy-transfer/{l1_code}")
def get_literacy_info(l1_code: str):
    """Get information about literacy skills that transfer from L1."""
    profile = get_l1_profile(l1_code)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No profile found for L1: {l1_code}")
    
    return {
        "l1_code": l1_code,
        "l1_name": profile.get("name", l1_code),
        "writing_system": profile.get("writing_system", "Unknown"),
        "literacy_transfer": get_literacy_transfer_info(l1_code)
    }


@router.get("/cultural/{l1_code}")
def get_cultural_info(l1_code: str):
    """Get cultural considerations for working with speakers of a given L1."""
    profile = get_l1_profile(l1_code)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No profile found for L1: {l1_code}")
    
    return {
        "l1_code": l1_code,
        "l1_name": profile.get("name", l1_code),
        "cultural_considerations": get_cultural_considerations(l1_code),
        "educational_background_notes": profile.get("educational_background_notes", "")
    }


@router.post("/analyze-text", response_model=List[ErrorPrediction])
def analyze_text_for_errors(request: AnalyzeTextRequest):
    """
    Analyze text for likely errors based on L1 transfer patterns.
    
    This provides predictive feedback based on common transfer errors
    for the student's L1, helping catch issues before they become habits.
    """
    profile = get_l1_profile(request.l1)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No profile found for L1: {request.l1}")
    
    predictions = predict_likely_errors(request.l1, request.text)
    return predictions


@router.get("/intervention-plan/{l1_code}", response_model=List[InterventionItem])
def get_intervention_plan(l1_code: str):
    """
    Generate a prioritized intervention plan based on L1 transfer patterns.
    
    Returns recommended focus areas, exercises, and teaching tips
    ordered by priority for the given L1.
    """
    profile = get_l1_profile(l1_code)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No profile found for L1: {l1_code}")
    
    plan = generate_intervention_plan(l1_code)
    return [
        InterventionItem(
            skill_area=item.skill_area,
            priority=item.priority.value,
            description=item.description,
            exercises=item.exercises,
            teaching_tip=item.teaching_tip,
            estimated_focus_weeks=item.estimated_focus_weeks
        )
        for item in plan
    ]


@router.post("/feedback", response_model=ContrastiveFeedback)
def get_error_feedback(request: FeedbackRequest):
    """
    Get L1-aware contrastive feedback for a specific error.
    
    Returns explanation that references the student's L1 to help them
    understand why they made the error and how to correct it.
    """
    profile = get_l1_profile(request.l1)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No profile found for L1: {request.l1}")
    
    feedback = get_contrastive_feedback(request.l1, request.error_type, request.context)
    return ContrastiveFeedback(**feedback)


@router.get("/vocabulary-strategies/{l1_code}")
def get_vocab_strategies(l1_code: str):
    """
    Get vocabulary learning strategies tailored to L1.
    
    For Romance languages, emphasizes cognates.
    For others, focuses on context and visual support.
    """
    profile = get_l1_profile(l1_code)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No profile found for L1: {l1_code}")
    
    strategies = get_vocabulary_strategies(l1_code)
    strategies["l1_code"] = l1_code
    strategies["l1_name"] = profile.get("name", l1_code)
    return strategies


@router.post("/exercise")
def generate_exercise(request: ExerciseRequest):
    """
    Generate an exercise targeting a skill area with L1-specific scaffolding.
    
    Available skill areas: articles, word_order, verb_tense
    """
    profile = get_l1_profile(request.l1)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No profile found for L1: {request.l1}")
    
    exercise = generate_l1_aware_exercise(request.l1, request.skill_area, request.difficulty)
    exercise["l1_code"] = request.l1
    exercise["l1_name"] = profile.get("name", request.l1)
    return exercise


@router.get("/summary/{l1_code}")
def get_l1_summary(l1_code: str):
    """
    Get a comprehensive summary of L1 transfer considerations.
    
    Useful for teachers to quickly understand what to focus on
    when working with a student from a particular L1 background.
    """
    profile = get_l1_profile(l1_code)
    if not profile:
        raise HTTPException(status_code=404, detail=f"No profile found for L1: {l1_code}")
    
    # Get top challenges
    phonology = get_phonological_difficulties(l1_code)[:3]
    grammar = get_grammar_challenges(l1_code)[:3]
    
    # Determine if script direction is a concern
    literacy = get_literacy_transfer_info(l1_code)
    script_concern = literacy.get("script_direction", "").startswith("RTL")
    
    return {
        "l1_code": l1_code,
        "l1_name": profile.get("name", l1_code),
        "language_family": profile.get("family", "Unknown"),
        "writing_system": profile.get("writing_system", "Unknown"),
        "top_phonological_priorities": [
            {"phoneme": p.get("phoneme", ""), "issue": p.get("issue", "")}
            for p in phonology
        ],
        "top_grammar_priorities": [
            {"feature": g.get("feature", ""), "issue": g.get("issue", "")}
            for g in grammar
        ],
        "script_direction_concern": script_concern,
        "cognate_rich": "HIGH" in profile.get("vocabulary", {}).get("cognate_strategy", "").upper(),
        "cultural_considerations": get_cultural_considerations(l1_code)[:3],
        "educational_notes": profile.get("educational_background_notes", "")
    }
