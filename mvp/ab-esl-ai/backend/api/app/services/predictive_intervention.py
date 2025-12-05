"""
Predictive Intervention Engine

Uses pattern analysis to identify students at risk of struggling and
generates prescriptive intervention plans before problems become severe.
This is a key differentiator for Alberta's teacher shortage - enabling
targeted support even with limited specialist availability.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class InterventionTier(str, Enum):
    TIER_1 = "tier_1"  # Universal classroom instruction
    TIER_2 = "tier_2"  # Targeted small group intervention
    TIER_3 = "tier_3"  # Intensive individualized intervention


@dataclass
class AssessmentDataPoint:
    """Single assessment data point for trend analysis."""
    date: datetime
    assessment_type: str
    score: float
    benchmark: float
    
    @property
    def percentage_of_benchmark(self) -> float:
        return (self.score / self.benchmark * 100) if self.benchmark > 0 else 0


@dataclass
class StudentRiskProfile:
    """Complete risk profile for a student."""
    student_id: str
    risk_level: RiskLevel
    risk_score: float
    risk_factors: List[Dict[str, Any]]
    protective_factors: List[Dict[str, Any]]
    predicted_areas_of_concern: List[str]
    recommended_intervention_tier: InterventionTier
    intervention_plan: Dict[str, Any]
    confidence: float


# Risk factor weights
RISK_WEIGHTS = {
    "declining_fluency_trend": 15,
    "below_benchmark_fluency": 12,
    "limited_l1_literacy": 10,
    "high_esl_level_gap": 10,  # Gap between current level and grade expectations
    "low_attendance": 8,
    "recent_arrival": 7,
    "slife_indicator": 12,
    "inconsistent_performance": 6,
    "phonological_weakness": 9,
    "vocabulary_gap": 8,
    "comprehension_difficulty": 9,
    "below_benchmark_accuracy": 7
}

# Protective factor weights
PROTECTIVE_WEIGHTS = {
    "improving_trend": 10,
    "strong_l1_literacy": 8,
    "consistent_engagement": 7,
    "family_involvement": 6,
    "cognate_advantage": 5,
    "prior_schooling": 6,
    "peer_support": 4
}

# Grade-level benchmark expectations (WCPM by spring)
WCPM_BENCHMARKS = {
    "K": 20,
    "1": 60,
    "2": 100,
    "3": 120,
    "4": 130,
    "5": 140,
    "6": 150
}


def calculate_trend(data_points: List[AssessmentDataPoint]) -> Dict[str, Any]:
    """
    Calculate trend from assessment data points.
    
    Returns:
        Dictionary with slope, direction, and consistency metrics
    """
    if len(data_points) < 2:
        return {"direction": "insufficient_data", "slope": 0, "consistency": 0}
    
    # Sort by date
    sorted_points = sorted(data_points, key=lambda x: x.date)
    
    # Calculate simple linear trend
    scores = [p.score for p in sorted_points]
    n = len(scores)
    
    # Calculate slope using least squares
    x_mean = (n - 1) / 2
    y_mean = statistics.mean(scores)
    
    numerator = sum((i - x_mean) * (scores[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    
    slope = numerator / denominator if denominator != 0 else 0
    
    # Determine direction
    if slope > 1:
        direction = "improving"
    elif slope < -1:
        direction = "declining"
    else:
        direction = "stable"
    
    # Calculate consistency (coefficient of variation)
    if y_mean > 0:
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
        consistency = 1 - (std_dev / y_mean)  # Higher is more consistent
    else:
        consistency = 0
    
    return {
        "direction": direction,
        "slope": round(slope, 2),
        "consistency": round(max(0, min(1, consistency)), 2),
        "data_points": n
    }


def identify_risk_factors(
    assessment_history: List[Dict[str, Any]],
    student_profile: Dict[str, Any],
    grade: str
) -> List[Dict[str, Any]]:
    """
    Identify risk factors from assessment history and student profile.
    
    Args:
        assessment_history: List of past assessments
        student_profile: Student demographic and background info
        grade: Current grade level
        
    Returns:
        List of identified risk factors with weights
    """
    risk_factors = []
    
    # Convert assessment history to data points for trend analysis
    fluency_points = []
    for assessment in assessment_history:
        if assessment.get("type") in ["orf", "oral_reading_fluency"]:
            try:
                point = AssessmentDataPoint(
                    date=datetime.fromisoformat(assessment.get("date", "")),
                    assessment_type="orf",
                    score=float(assessment.get("wcpm", assessment.get("score", 0))),
                    benchmark=float(WCPM_BENCHMARKS.get(grade, 100))
                )
                fluency_points.append(point)
            except (ValueError, TypeError):
                continue
    
    # Check fluency trend
    if fluency_points:
        trend = calculate_trend(fluency_points)
        
        if trend["direction"] == "declining":
            risk_factors.append({
                "factor": "declining_fluency_trend",
                "weight": RISK_WEIGHTS["declining_fluency_trend"],
                "evidence": f"Fluency declining at rate of {abs(trend['slope'])} WCPM per assessment",
                "severity": "high" if trend["slope"] < -5 else "moderate"
            })
        
        # Check most recent against benchmark
        latest = max(fluency_points, key=lambda x: x.date)
        benchmark = WCPM_BENCHMARKS.get(grade, 100)
        
        if latest.score < benchmark * 0.5:
            risk_factors.append({
                "factor": "below_benchmark_fluency",
                "weight": RISK_WEIGHTS["below_benchmark_fluency"],
                "evidence": f"Current WCPM ({latest.score}) is less than 50% of benchmark ({benchmark})",
                "severity": "critical"
            })
        elif latest.score < benchmark * 0.8:
            risk_factors.append({
                "factor": "below_benchmark_fluency",
                "weight": RISK_WEIGHTS["below_benchmark_fluency"] * 0.7,
                "evidence": f"Current WCPM ({latest.score}) is below 80% of benchmark ({benchmark})",
                "severity": "moderate"
            })
        
        # Check consistency
        if trend["consistency"] < 0.6:
            risk_factors.append({
                "factor": "inconsistent_performance",
                "weight": RISK_WEIGHTS["inconsistent_performance"],
                "evidence": f"Performance varies significantly (consistency: {trend['consistency']})",
                "severity": "moderate"
            })
    
    # Profile-based risk factors
    esl_level = student_profile.get("esl_level", 3)
    if esl_level <= 2:
        risk_factors.append({
            "factor": "high_esl_level_gap",
            "weight": RISK_WEIGHTS["high_esl_level_gap"],
            "evidence": f"ESL Level {esl_level} indicates significant language gap",
            "severity": "high" if esl_level == 1 else "moderate"
        })
    
    # L1 literacy
    l1_literacy = student_profile.get("l1_literacy", "unknown")
    if l1_literacy in ["none", "limited", "non_literate"]:
        risk_factors.append({
            "factor": "limited_l1_literacy",
            "weight": RISK_WEIGHTS["limited_l1_literacy"],
            "evidence": f"Limited or no literacy in first language",
            "severity": "high"
        })
    
    # SLIFE indicator
    if student_profile.get("slife", False) or student_profile.get("interrupted_schooling", False):
        risk_factors.append({
            "factor": "slife_indicator",
            "weight": RISK_WEIGHTS["slife_indicator"],
            "evidence": "Student has limited or interrupted formal education",
            "severity": "high"
        })
    
    # Recent arrival
    arrival_date = student_profile.get("arrival_date")
    if arrival_date:
        try:
            arrival = datetime.fromisoformat(arrival_date)
            months_since_arrival = (datetime.now() - arrival).days / 30
            if months_since_arrival < 6:
                risk_factors.append({
                    "factor": "recent_arrival",
                    "weight": RISK_WEIGHTS["recent_arrival"],
                    "evidence": f"Arrived {int(months_since_arrival)} months ago",
                    "severity": "moderate"
                })
        except (ValueError, TypeError):
            pass
    
    # Phonological weakness indicators
    phonics_assessments = [a for a in assessment_history if a.get("type") in ["phonics", "psf", "phoneme_segmentation"]]
    if phonics_assessments:
        latest_phonics = max(phonics_assessments, key=lambda x: x.get("date", ""))
        if latest_phonics.get("score", 100) < latest_phonics.get("benchmark", 100) * 0.7:
            risk_factors.append({
                "factor": "phonological_weakness",
                "weight": RISK_WEIGHTS["phonological_weakness"],
                "evidence": "Below benchmark on phonological assessments",
                "severity": "moderate"
            })
    
    return risk_factors


def identify_protective_factors(
    assessment_history: List[Dict[str, Any]],
    student_profile: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Identify protective factors that mitigate risk.
    
    Args:
        assessment_history: List of past assessments
        student_profile: Student demographic and background info
        
    Returns:
        List of identified protective factors with weights
    """
    protective_factors = []
    
    # Convert to data points for trend analysis
    all_scores = []
    for assessment in assessment_history:
        try:
            score = float(assessment.get("score", assessment.get("wcpm", 0)))
            if score > 0:
                all_scores.append({
                    "date": datetime.fromisoformat(assessment.get("date", "")),
                    "score": score
                })
        except (ValueError, TypeError):
            continue
    
    # Check for improving trend
    if len(all_scores) >= 2:
        sorted_scores = sorted(all_scores, key=lambda x: x["date"])
        recent_scores = [s["score"] for s in sorted_scores[-3:]]
        earlier_scores = [s["score"] for s in sorted_scores[:3]]
        
        if statistics.mean(recent_scores) > statistics.mean(earlier_scores) * 1.1:
            protective_factors.append({
                "factor": "improving_trend",
                "weight": PROTECTIVE_WEIGHTS["improving_trend"],
                "evidence": "Recent performance showing improvement over earlier assessments"
            })
    
    # L1 literacy strength
    l1_literacy = student_profile.get("l1_literacy", "unknown")
    if l1_literacy in ["strong", "grade_level", "literate"]:
        protective_factors.append({
            "factor": "strong_l1_literacy",
            "weight": PROTECTIVE_WEIGHTS["strong_l1_literacy"],
            "evidence": "Strong literacy foundation in first language"
        })
    
    # Cognate advantage (Romance languages for English)
    l1 = student_profile.get("l1", "")
    cognate_languages = ["es", "fr", "pt", "it"]
    if l1 in cognate_languages:
        protective_factors.append({
            "factor": "cognate_advantage",
            "weight": PROTECTIVE_WEIGHTS["cognate_advantage"],
            "evidence": f"L1 ({l1}) shares many cognates with English"
        })
    
    # Prior schooling
    years_schooling = student_profile.get("years_prior_schooling", 0)
    expected_years = int(student_profile.get("grade", "0").replace("K", "0") or 0)
    if years_schooling >= expected_years:
        protective_factors.append({
            "factor": "prior_schooling",
            "weight": PROTECTIVE_WEIGHTS["prior_schooling"],
            "evidence": f"{years_schooling} years of prior formal education"
        })
    
    # Family involvement
    if student_profile.get("family_involvement", False) or student_profile.get("parent_engagement", False):
        protective_factors.append({
            "factor": "family_involvement",
            "weight": PROTECTIVE_WEIGHTS["family_involvement"],
            "evidence": "Active family involvement in education"
        })
    
    # Engagement metrics
    engagement = student_profile.get("engagement_score", 0)
    if engagement >= 0.8:
        protective_factors.append({
            "factor": "consistent_engagement",
            "weight": PROTECTIVE_WEIGHTS["consistent_engagement"],
            "evidence": "Consistently engaged in learning activities"
        })
    
    return protective_factors


def calculate_risk_score(
    risk_factors: List[Dict[str, Any]],
    protective_factors: List[Dict[str, Any]]
) -> Tuple[float, RiskLevel]:
    """
    Calculate overall risk score from factors.
    
    Returns:
        Tuple of (risk_score 0-100, risk_level)
    """
    total_risk = sum(f.get("weight", 0) for f in risk_factors)
    total_protective = sum(f.get("weight", 0) for f in protective_factors)
    
    # Protective factors reduce risk
    adjusted_risk = max(0, total_risk - (total_protective * 0.5))
    
    # Normalize to 0-100 scale
    max_possible_risk = sum(RISK_WEIGHTS.values())
    risk_score = min(100, (adjusted_risk / max_possible_risk) * 100)
    
    # Determine risk level
    if risk_score >= 70:
        level = RiskLevel.CRITICAL
    elif risk_score >= 50:
        level = RiskLevel.HIGH
    elif risk_score >= 30:
        level = RiskLevel.MODERATE
    else:
        level = RiskLevel.LOW
    
    return round(risk_score, 1), level


def determine_intervention_tier(risk_level: RiskLevel) -> InterventionTier:
    """Determine appropriate intervention tier based on risk level."""
    if risk_level == RiskLevel.CRITICAL:
        return InterventionTier.TIER_3
    elif risk_level == RiskLevel.HIGH:
        return InterventionTier.TIER_2
    elif risk_level == RiskLevel.MODERATE:
        return InterventionTier.TIER_2
    else:
        return InterventionTier.TIER_1


def generate_intervention_plan(
    risk_factors: List[Dict[str, Any]],
    protective_factors: List[Dict[str, Any]],
    student_profile: Dict[str, Any],
    tier: InterventionTier
) -> Dict[str, Any]:
    """
    Generate a prescriptive intervention plan based on risk factors.
    
    Args:
        risk_factors: Identified risk factors
        protective_factors: Identified protective factors
        student_profile: Student information
        tier: Intervention tier level
        
    Returns:
        Comprehensive intervention plan
    """
    plan = {
        "tier": tier.value,
        "intensity": get_tier_intensity(tier),
        "focus_areas": [],
        "recommended_activities": [],
        "grouping_recommendation": get_grouping_recommendation(tier),
        "progress_monitoring": get_monitoring_schedule(tier),
        "duration_weeks": get_intervention_duration(tier),
        "success_criteria": []
    }
    
    # Identify focus areas from risk factors
    for risk in risk_factors:
        factor = risk.get("factor", "")
        
        if factor in ["declining_fluency_trend", "below_benchmark_fluency"]:
            if "Fluency" not in plan["focus_areas"]:
                plan["focus_areas"].append("Fluency")
                plan["recommended_activities"].extend([
                    {
                        "activity": "Repeated Reading",
                        "description": "Read same passage 3x until 100 WCPM or better",
                        "frequency": "Daily, 15 minutes",
                        "tool": "Reading Buddy app"
                    },
                    {
                        "activity": "Phrase-Cued Reading",
                        "description": "Read text marked with phrase boundaries",
                        "frequency": "3x per week",
                        "tool": "Teacher-prepared materials"
                    }
                ])
                plan["success_criteria"].append("Increase WCPM by 10+ words over 4 weeks")
        
        if factor == "phonological_weakness":
            if "Phonological Awareness" not in plan["focus_areas"]:
                plan["focus_areas"].append("Phonological Awareness")
                plan["recommended_activities"].extend([
                    {
                        "activity": "Sound Box Activities",
                        "description": "Elkonin boxes for phoneme segmentation",
                        "frequency": "Daily, 10 minutes",
                        "tool": "Manipulatives or digital app"
                    },
                    {
                        "activity": "Phoneme Blending Drills",
                        "description": "Blend sounds to make words",
                        "frequency": "Daily, 5 minutes",
                        "tool": "Speaking practice app"
                    }
                ])
                plan["success_criteria"].append("Reach grade-level phoneme segmentation benchmark")
        
        if factor in ["high_esl_level_gap", "vocabulary_gap"]:
            if "Vocabulary Development" not in plan["focus_areas"]:
                plan["focus_areas"].append("Vocabulary Development")
                plan["recommended_activities"].extend([
                    {
                        "activity": "Tiered Vocabulary Instruction",
                        "description": "Focus on Tier 2 academic vocabulary",
                        "frequency": "Daily, 10 minutes",
                        "tool": "Glossary tool with L1 support"
                    },
                    {
                        "activity": "Word Learning Strategies",
                        "description": "Context clues, morphemic analysis",
                        "frequency": "3x per week",
                        "tool": "Reading Buddy comprehension mode"
                    }
                ])
                plan["success_criteria"].append("Learn 5+ new Tier 2 words per week")
        
        if factor == "limited_l1_literacy":
            if "Foundational Literacy" not in plan["focus_areas"]:
                plan["focus_areas"].append("Foundational Literacy")
                plan["recommended_activities"].extend([
                    {
                        "activity": "Concept of Print Activities",
                        "description": "Book handling, directionality, word concept",
                        "frequency": "Daily",
                        "tool": "Shared reading"
                    },
                    {
                        "activity": "Letter-Sound Correspondence",
                        "description": "Explicit phonics instruction",
                        "frequency": "Daily, 20 minutes",
                        "tool": "Systematic phonics program"
                    }
                ])
                plan["success_criteria"].append("Master all letter-sound correspondences")
        
        if factor == "slife_indicator":
            if "Academic Foundations" not in plan["focus_areas"]:
                plan["focus_areas"].append("Academic Foundations")
                plan["recommended_activities"].extend([
                    {
                        "activity": "School Readiness Skills",
                        "description": "Academic routines, classroom expectations",
                        "frequency": "Ongoing",
                        "tool": "Structured routines"
                    },
                    {
                        "activity": "Age-Appropriate Content",
                        "description": "Use SLIFE-designed materials",
                        "frequency": "All instruction",
                        "tool": "SLIFE content pathway"
                    }
                ])
                plan["success_criteria"].append("Demonstrate understanding of academic routines")
    
    # Leverage protective factors
    plan["leverage_strengths"] = []
    for protective in protective_factors:
        factor = protective.get("factor", "")
        
        if factor == "strong_l1_literacy":
            plan["leverage_strengths"].append({
                "strength": "L1 Literacy",
                "strategy": "Use cognates and L1 literacy skills to support English reading"
            })
        
        if factor == "cognate_advantage":
            plan["leverage_strengths"].append({
                "strength": "Cognate Language",
                "strategy": "Explicitly teach English-L1 cognates for vocabulary building"
            })
        
        if factor == "family_involvement":
            plan["leverage_strengths"].append({
                "strength": "Family Support",
                "strategy": "Send home materials in L1; engage family in reading practice"
            })
    
    # Add L1-specific considerations if available
    l1 = student_profile.get("l1", "")
    if l1:
        plan["l1_considerations"] = get_l1_intervention_considerations(l1)
    
    return plan


def get_tier_intensity(tier: InterventionTier) -> Dict[str, Any]:
    """Get intervention intensity parameters for tier."""
    intensities = {
        InterventionTier.TIER_1: {
            "minutes_per_day": 90,
            "setting": "Whole class",
            "provider": "Classroom teacher",
            "description": "High-quality classroom instruction with differentiation"
        },
        InterventionTier.TIER_2: {
            "minutes_per_day": 120,  # 90 core + 30 intervention
            "setting": "Small group (3-5 students)",
            "provider": "Classroom teacher or interventionist",
            "description": "Core instruction plus targeted small-group intervention"
        },
        InterventionTier.TIER_3: {
            "minutes_per_day": 150,  # 90 core + 60 intensive
            "setting": "Individual or very small group (1-3)",
            "provider": "Specialist or trained interventionist",
            "description": "Core instruction plus intensive individualized intervention"
        }
    }
    return intensities.get(tier, intensities[InterventionTier.TIER_1])


def get_grouping_recommendation(tier: InterventionTier) -> str:
    """Get grouping recommendation for intervention tier."""
    if tier == InterventionTier.TIER_1:
        return "Flexible groups based on skill needs within classroom"
    elif tier == InterventionTier.TIER_2:
        return "Homogeneous small group (3-5) with similar skill gaps"
    else:
        return "Individual or dyad with intensive support"


def get_monitoring_schedule(tier: InterventionTier) -> Dict[str, Any]:
    """Get progress monitoring schedule for tier."""
    schedules = {
        InterventionTier.TIER_1: {
            "frequency": "3 times per year",
            "tool": "Universal screening (ORF, MAZE)",
            "decision_point": "Fall, Winter, Spring benchmarks"
        },
        InterventionTier.TIER_2: {
            "frequency": "Every 2 weeks",
            "tool": "Curriculum-based measurement (CBM)",
            "decision_point": "6-8 week review for tier change"
        },
        InterventionTier.TIER_3: {
            "frequency": "Weekly",
            "tool": "Progress monitoring probes",
            "decision_point": "4-6 week review for adjustments"
        }
    }
    return schedules.get(tier, schedules[InterventionTier.TIER_1])


def get_intervention_duration(tier: InterventionTier) -> int:
    """Get recommended intervention duration in weeks."""
    if tier == InterventionTier.TIER_1:
        return 36  # Full school year
    elif tier == InterventionTier.TIER_2:
        return 12  # One intervention cycle
    else:
        return 8  # Intensive short-term


def get_l1_intervention_considerations(l1: str) -> List[Dict[str, str]]:
    """Get L1-specific intervention considerations."""
    considerations = {
        "ar": [
            {"area": "Directionality", "note": "Arabic reads right-to-left; reinforce left-to-right"},
            {"area": "Vowels", "note": "Arabic has 3 vowels; explicitly teach English vowel sounds"}
        ],
        "zh": [
            {"area": "Phonological Awareness", "note": "Chinese is logographic; extensive PA instruction needed"},
            {"area": "Morphology", "note": "Chinese lacks inflections; teach English word forms"}
        ],
        "es": [
            {"area": "Cognates", "note": "Leverage Spanish-English cognates for vocabulary"},
            {"area": "Phonics", "note": "Spanish is more transparent; teach English spelling patterns"}
        ],
        "so": [
            {"area": "Literacy Transfer", "note": "Somali uses Latin alphabet; positive transfer possible"},
            {"area": "Vowels", "note": "Somali vowel system differs; focus on English vowels"}
        ],
        "uk": [
            {"area": "Alphabet", "note": "Cyrillic alphabet; teach letter-sound correspondences"},
            {"area": "Articles", "note": "Ukrainian lacks articles; explicit article instruction"}
        ]
    }
    return considerations.get(l1, [{"area": "General", "note": "Assess for specific L1 transfer issues"}])


def predict_areas_of_concern(risk_factors: List[Dict[str, Any]]) -> List[str]:
    """Predict specific areas likely to cause difficulty."""
    concerns = []
    
    factor_mapping = {
        "declining_fluency_trend": "Reading fluency may continue to decline without intervention",
        "below_benchmark_fluency": "Fluency gap will widen without targeted support",
        "limited_l1_literacy": "Foundational literacy concepts may need explicit instruction",
        "high_esl_level_gap": "Academic language gap may impact content area learning",
        "slife_indicator": "Academic and literacy foundations may need building",
        "phonological_weakness": "Decoding accuracy and spelling may be affected",
        "vocabulary_gap": "Comprehension will be limited by vocabulary",
        "inconsistent_performance": "May struggle with test-taking or attention"
    }
    
    for risk in risk_factors:
        factor = risk.get("factor", "")
        if factor in factor_mapping:
            concerns.append(factor_mapping[factor])
    
    return concerns


def analyze_student_risk(
    student_id: str,
    assessment_history: List[Dict[str, Any]],
    student_profile: Dict[str, Any]
) -> StudentRiskProfile:
    """
    Perform comprehensive risk analysis for a student.
    
    This is the main entry point for the predictive intervention engine.
    
    Args:
        student_id: Unique student identifier
        assessment_history: List of past assessments with dates and scores
        student_profile: Student demographic and background information
        
    Returns:
        Complete StudentRiskProfile with intervention recommendations
    """
    grade = student_profile.get("grade", "3")
    
    # Identify factors
    risk_factors = identify_risk_factors(assessment_history, student_profile, grade)
    protective_factors = identify_protective_factors(assessment_history, student_profile)
    
    # Calculate risk
    risk_score, risk_level = calculate_risk_score(risk_factors, protective_factors)
    
    # Determine intervention needs
    tier = determine_intervention_tier(risk_level)
    intervention_plan = generate_intervention_plan(
        risk_factors, protective_factors, student_profile, tier
    )
    
    # Predict concerns
    predicted_concerns = predict_areas_of_concern(risk_factors)
    
    # Calculate confidence based on data quality
    data_points = len(assessment_history)
    profile_completeness = sum(1 for k in ["esl_level", "l1", "l1_literacy", "grade"] 
                               if student_profile.get(k) is not None) / 4
    confidence = min(1.0, (data_points / 5) * 0.5 + profile_completeness * 0.5)
    
    return StudentRiskProfile(
        student_id=student_id,
        risk_level=risk_level,
        risk_score=risk_score,
        risk_factors=risk_factors,
        protective_factors=protective_factors,
        predicted_areas_of_concern=predicted_concerns,
        recommended_intervention_tier=tier,
        intervention_plan=intervention_plan,
        confidence=round(confidence, 2)
    )


def batch_analyze_classroom(
    students: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyze risk for an entire classroom of students.
    
    Args:
        students: List of dictionaries containing student_id, assessment_history, and profile
        
    Returns:
        Summary with individual results and classroom-level insights
    """
    results = []
    tier_counts = {tier.value: 0 for tier in InterventionTier}
    risk_distribution = {level.value: 0 for level in RiskLevel}
    
    for student in students:
        profile = analyze_student_risk(
            student_id=student.get("student_id", "unknown"),
            assessment_history=student.get("assessment_history", []),
            student_profile=student.get("profile", {})
        )
        
        results.append({
            "student_id": profile.student_id,
            "risk_level": profile.risk_level.value,
            "risk_score": profile.risk_score,
            "tier": profile.recommended_intervention_tier.value,
            "top_concerns": profile.predicted_areas_of_concern[:2],
            "confidence": profile.confidence
        })
        
        tier_counts[profile.recommended_intervention_tier.value] += 1
        risk_distribution[profile.risk_level.value] += 1
    
    # Sort by risk score descending
    results.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return {
        "classroom_summary": {
            "total_students": len(students),
            "tier_distribution": tier_counts,
            "risk_distribution": risk_distribution,
            "students_needing_intensive_support": tier_counts.get("tier_3", 0),
            "students_needing_targeted_support": tier_counts.get("tier_2", 0)
        },
        "student_results": results,
        "priority_students": results[:5],  # Top 5 highest risk
        "recommendations": generate_classroom_recommendations(tier_counts, risk_distribution)
    }


def generate_classroom_recommendations(
    tier_counts: Dict[str, int],
    risk_distribution: Dict[str, int]
) -> List[str]:
    """Generate classroom-level recommendations based on analysis."""
    recommendations = []
    
    total = sum(tier_counts.values())
    if total == 0:
        return ["Insufficient data for recommendations"]
    
    tier_3_pct = tier_counts.get("tier_3", 0) / total * 100
    tier_2_pct = tier_counts.get("tier_2", 0) / total * 100
    
    if tier_3_pct > 20:
        recommendations.append(
            "High proportion of students need Tier 3 support. Consider requesting additional "
            "intervention specialist time or small-group intensive instruction blocks."
        )
    
    if tier_2_pct > 40:
        recommendations.append(
            "Many students need Tier 2 support. Organize flexible intervention groups "
            "targeting common skill gaps. Consider 30-minute daily intervention blocks."
        )
    
    critical_pct = risk_distribution.get("critical", 0) / total * 100
    if critical_pct > 15:
        recommendations.append(
            "Multiple students at critical risk level. Prioritize immediate assessment "
            "of foundational skills and consider intensive daily intervention."
        )
    
    if tier_counts.get("tier_1", 0) / total > 0.6:
        recommendations.append(
            "Most students responding well to core instruction. Maintain high-quality "
            "Tier 1 instruction with differentiation for diverse learners."
        )
    
    return recommendations if recommendations else [
        "Continue monitoring student progress with regular assessments."
    ]
