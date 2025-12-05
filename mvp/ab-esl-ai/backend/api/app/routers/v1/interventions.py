"""
Predictive Intervention API

Endpoints for student risk analysis and intervention planning.
Enables early identification of struggling students and generates
prescriptive intervention plans.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

from app.services.predictive_intervention import (
    analyze_student_risk,
    batch_analyze_classroom,
    RiskLevel,
    InterventionTier
)

router = APIRouter(prefix="/v1/interventions")


class AssessmentRecord(BaseModel):
    """Single assessment record for analysis."""
    type: str = Field(..., description="Assessment type (e.g., 'orf', 'maze', 'phonics')")
    date: str = Field(..., description="Assessment date in ISO format")
    score: Optional[float] = Field(None, description="Raw score")
    wcpm: Optional[int] = Field(None, description="Words correct per minute (for ORF)")
    benchmark: Optional[float] = Field(None, description="Expected benchmark")
    accuracy: Optional[float] = Field(None, ge=0, le=1, description="Accuracy rate")


class StudentProfile(BaseModel):
    """Student demographic and background information."""
    grade: str = Field(..., description="Current grade level")
    esl_level: Optional[int] = Field(None, ge=1, le=5, description="ESL proficiency level")
    l1: Optional[str] = Field(None, description="First language code")
    l1_literacy: Optional[str] = Field(None, description="L1 literacy level (none/limited/strong)")
    slife: Optional[bool] = Field(False, description="Student with Limited/Interrupted Formal Education")
    interrupted_schooling: Optional[bool] = Field(False, description="Has interrupted schooling")
    arrival_date: Optional[str] = Field(None, description="Date of arrival in Canada")
    years_prior_schooling: Optional[int] = Field(None, ge=0, description="Years of prior schooling")
    family_involvement: Optional[bool] = Field(None, description="Active family involvement")
    engagement_score: Optional[float] = Field(None, ge=0, le=1, description="Student engagement metric")


class StudentRiskAnalysisRequest(BaseModel):
    """Request for individual student risk analysis."""
    student_id: str = Field(..., description="Unique student identifier")
    assessment_history: List[AssessmentRecord] = Field(
        default=[], description="Historical assessment data"
    )
    profile: StudentProfile


class ClassroomAnalysisStudent(BaseModel):
    """Student data for classroom batch analysis."""
    student_id: str
    assessment_history: List[AssessmentRecord] = []
    profile: StudentProfile


class ClassroomAnalysisRequest(BaseModel):
    """Request for classroom-wide risk analysis."""
    students: List[ClassroomAnalysisStudent]


class InterventionFeedbackRequest(BaseModel):
    """Feedback on intervention effectiveness."""
    student_id: str
    intervention_tier: str
    focus_areas: List[str]
    weeks_implemented: int = Field(..., ge=1)
    pre_score: float
    post_score: float
    notes: Optional[str] = None


# Endpoints

@router.post("/analyze/student")
async def analyze_student(request: StudentRiskAnalysisRequest):
    """
    Analyze risk level for a single student and generate intervention plan.
    
    Provides:
    - Risk level (low, moderate, high, critical)
    - Risk score (0-100)
    - Identified risk and protective factors
    - Recommended intervention tier (1, 2, or 3)
    - Detailed intervention plan with activities
    - Predicted areas of concern
    
    This enables proactive intervention before students fall significantly behind.
    """
    # Convert Pydantic models to dicts
    assessment_history = [
        {
            "type": a.type,
            "date": a.date,
            "score": a.score or a.wcpm or 0,
            "wcpm": a.wcpm,
            "benchmark": a.benchmark,
            "accuracy": a.accuracy
        }
        for a in request.assessment_history
    ]
    
    profile_dict = request.profile.model_dump()
    
    # Analyze
    result = analyze_student_risk(
        student_id=request.student_id,
        assessment_history=assessment_history,
        student_profile=profile_dict
    )
    
    return {
        "student_id": result.student_id,
        "analysis_date": datetime.now().isoformat(),
        "risk_level": result.risk_level.value,
        "risk_score": result.risk_score,
        "confidence": result.confidence,
        "risk_factors": result.risk_factors,
        "protective_factors": result.protective_factors,
        "predicted_concerns": result.predicted_areas_of_concern,
        "recommended_tier": result.recommended_intervention_tier.value,
        "intervention_plan": result.intervention_plan
    }


@router.post("/analyze/classroom")
async def analyze_classroom(request: ClassroomAnalysisRequest):
    """
    Analyze risk levels for an entire classroom of students.
    
    Returns:
    - Individual risk profiles for each student
    - Classroom-level summary statistics
    - Tier distribution (how many need Tier 1/2/3)
    - Priority list of highest-risk students
    - Classroom-level recommendations
    
    This helps teachers prioritize limited intervention resources.
    """
    students_data = []
    for student in request.students:
        assessment_history = [
            {
                "type": a.type,
                "date": a.date,
                "score": a.score or a.wcpm or 0,
                "wcpm": a.wcpm,
                "benchmark": a.benchmark
            }
            for a in student.assessment_history
        ]
        
        students_data.append({
            "student_id": student.student_id,
            "assessment_history": assessment_history,
            "profile": student.profile.model_dump()
        })
    
    result = batch_analyze_classroom(students_data)
    
    return {
        "analysis_date": datetime.now().isoformat(),
        "classroom_summary": result["classroom_summary"],
        "student_results": result["student_results"],
        "priority_students": result["priority_students"],
        "recommendations": result["recommendations"]
    }


@router.get("/tiers")
async def get_intervention_tiers():
    """
    Get information about intervention tiers.
    
    Explains the RTI (Response to Intervention) framework:
    - Tier 1: Universal classroom instruction
    - Tier 2: Targeted small-group intervention
    - Tier 3: Intensive individualized intervention
    """
    return {
        "framework": "Response to Intervention (RTI)",
        "tiers": {
            "tier_1": {
                "name": "Universal Instruction",
                "description": "High-quality classroom instruction for all students",
                "setting": "Whole class",
                "minutes_per_day": 90,
                "students_served": "All students (100%)",
                "monitoring": "3x per year (benchmark assessments)"
            },
            "tier_2": {
                "name": "Targeted Intervention",
                "description": "Additional support for students not meeting benchmarks",
                "setting": "Small group (3-5 students)",
                "minutes_per_day": "90 core + 30 intervention",
                "students_served": "Some students (15-20%)",
                "monitoring": "Every 2 weeks"
            },
            "tier_3": {
                "name": "Intensive Intervention",
                "description": "Individualized, intensive support for highest-need students",
                "setting": "Individual or very small group (1-3)",
                "minutes_per_day": "90 core + 60 intensive",
                "students_served": "Few students (3-5%)",
                "monitoring": "Weekly"
            }
        }
    }


@router.get("/risk-levels")
async def get_risk_levels():
    """
    Get information about risk level classifications.
    """
    return {
        "levels": {
            "low": {
                "score_range": "0-29",
                "description": "Student is making adequate progress",
                "action": "Continue Tier 1 instruction; monitor at benchmark periods"
            },
            "moderate": {
                "score_range": "30-49",
                "description": "Student showing some risk factors; may struggle without support",
                "action": "Consider Tier 2 intervention; increase monitoring frequency"
            },
            "high": {
                "score_range": "50-69",
                "description": "Student at significant risk; likely to fall further behind",
                "action": "Implement Tier 2 intervention immediately; consider Tier 3"
            },
            "critical": {
                "score_range": "70-100",
                "description": "Student at severe risk; urgent intervention needed",
                "action": "Implement Tier 3 intervention; assess for additional needs"
            }
        }
    }


@router.get("/risk-factors")
async def get_risk_factor_definitions():
    """
    Get definitions of risk factors used in analysis.
    """
    return {
        "risk_factors": {
            "declining_fluency_trend": {
                "description": "Fluency scores decreasing over time",
                "weight": 15,
                "how_detected": "Trend analysis of ORF scores"
            },
            "below_benchmark_fluency": {
                "description": "Current fluency below grade-level expectations",
                "weight": 12,
                "how_detected": "Comparison to WCPM benchmarks"
            },
            "limited_l1_literacy": {
                "description": "Limited literacy development in first language",
                "weight": 10,
                "how_detected": "Student profile data"
            },
            "high_esl_level_gap": {
                "description": "ESL level significantly below grade expectations",
                "weight": 10,
                "how_detected": "ESL level vs. grade comparison"
            },
            "slife_indicator": {
                "description": "Student has limited or interrupted formal education",
                "weight": 12,
                "how_detected": "Student profile data"
            },
            "phonological_weakness": {
                "description": "Below benchmark on phonological awareness",
                "weight": 9,
                "how_detected": "Phonics/PSF assessment results"
            },
            "vocabulary_gap": {
                "description": "Significant vocabulary knowledge gaps",
                "weight": 8,
                "how_detected": "Assessment data and observations"
            }
        },
        "protective_factors": {
            "improving_trend": {
                "description": "Recent scores showing improvement",
                "weight": 10,
                "how_detected": "Trend analysis"
            },
            "strong_l1_literacy": {
                "description": "Strong literacy skills in first language",
                "weight": 8,
                "how_detected": "Student profile data"
            },
            "cognate_advantage": {
                "description": "L1 shares many cognates with English",
                "weight": 5,
                "how_detected": "L1 language classification"
            },
            "family_involvement": {
                "description": "Active family involvement in education",
                "weight": 6,
                "how_detected": "Student profile data"
            }
        }
    }


@router.post("/feedback")
async def submit_intervention_feedback(request: InterventionFeedbackRequest):
    """
    Submit feedback on intervention effectiveness.
    
    This data helps improve the prediction model over time.
    """
    # Calculate growth
    growth = request.post_score - request.pre_score
    growth_per_week = growth / request.weeks_implemented if request.weeks_implemented > 0 else 0
    
    # Evaluate effectiveness (simplified - in production would be more sophisticated)
    if growth_per_week >= 2:  # 2+ WCPM growth per week is excellent
        effectiveness = "highly_effective"
    elif growth_per_week >= 1:
        effectiveness = "effective"
    elif growth_per_week >= 0:
        effectiveness = "minimal_progress"
    else:
        effectiveness = "declining"
    
    return {
        "student_id": request.student_id,
        "feedback_recorded": True,
        "analysis": {
            "total_growth": growth,
            "growth_per_week": round(growth_per_week, 2),
            "effectiveness": effectiveness,
            "weeks_implemented": request.weeks_implemented
        },
        "recommendation": get_feedback_recommendation(effectiveness, request.intervention_tier)
    }


def get_feedback_recommendation(effectiveness: str, current_tier: str) -> str:
    """Generate recommendation based on intervention feedback."""
    if effectiveness == "highly_effective":
        return "Continue current intervention; consider gradual reduction of support"
    elif effectiveness == "effective":
        return "Continue current intervention; maintain monitoring schedule"
    elif effectiveness == "minimal_progress":
        if current_tier == "tier_2":
            return "Consider increasing intensity to Tier 3 intervention"
        else:
            return "Review intervention fidelity; consider adjusting focus areas"
    else:
        return "Urgent review needed; consider diagnostic assessment and intervention change"


@router.get("/summary")
async def get_intervention_system_summary():
    """
    Get overview of the Predictive Intervention Engine.
    """
    return {
        "system": "Predictive Intervention Engine",
        "purpose": "Early identification of at-risk students with prescriptive intervention plans",
        "capabilities": [
            "Individual student risk analysis",
            "Classroom-wide batch analysis",
            "Multi-factor risk scoring",
            "L1-aware intervention recommendations",
            "RTI tier assignment",
            "Progress monitoring schedules",
            "Intervention effectiveness tracking"
        ],
        "alberta_alignment": [
            "Supports Response to Intervention (RTI) framework",
            "Aligns with Alberta ESL Proficiency Benchmarks",
            "Uses Alberta-appropriate WCPM benchmarks",
            "Considers SLIFE and newcomer factors"
        ],
        "key_benefits": [
            "Proactive rather than reactive intervention",
            "Maximizes impact of limited specialist time",
            "Data-driven tier assignment",
            "Personalized intervention plans"
        ]
    }
