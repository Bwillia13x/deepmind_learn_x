"""
Alberta Curriculum Alignment Service

Maps student activities, assessments, and content to Alberta ELA outcomes
and ESL Proficiency Benchmarks. Provides teachers with standards-aligned
progress reporting and helps identify curriculum gaps.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from functools import lru_cache
from datetime import datetime

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_curriculum_data() -> Dict[str, Any]:
    """Load Alberta curriculum outcomes and ESL benchmarks."""
    # From services/curriculum.py -> services -> app -> api -> backend -> ab-esl-ai (5 parents)
    content_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "content" / "curriculum"
    curriculum_file = content_path / "alberta_ela_outcomes.json"
    
    try:
        with open(curriculum_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Curriculum file not found: {curriculum_file}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing curriculum JSON: {e}")
        return {}


def get_esl_benchmark_level(level: int) -> Optional[Dict[str, Any]]:
    """
    Get details about a specific ESL proficiency benchmark level.
    
    Args:
        level: ESL level 1-5
        
    Returns:
        Dictionary with level details or None if not found
    """
    curriculum = load_curriculum_data()
    benchmarks = curriculum.get("esl_proficiency_benchmarks", {}).get("levels", {})
    level_key = f"level_{level}"
    return benchmarks.get(level_key)


def get_all_benchmark_levels() -> Dict[str, Any]:
    """Get all ESL proficiency benchmark levels."""
    curriculum = load_curriculum_data()
    return curriculum.get("esl_proficiency_benchmarks", {}).get("levels", {})


def assess_esl_level(
    reading_level: Optional[str] = None,
    wcpm: Optional[int] = None,
    can_follow_directions: Optional[bool] = None,
    writes_sentences: Optional[bool] = None,
    participates_discussions: Optional[bool] = None,
    uses_academic_vocab: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Assess a student's likely ESL proficiency level based on indicators.
    
    Args:
        reading_level: Description of reading ability
        wcpm: Words correct per minute
        can_follow_directions: Can follow multi-step directions
        writes_sentences: Can write complete sentences
        participates_discussions: Participates in class discussions
        uses_academic_vocab: Uses academic vocabulary
        
    Returns:
        Estimated level and confidence score
    """
    indicators = {
        "level_1": 0,
        "level_2": 0,
        "level_3": 0,
        "level_4": 0,
        "level_5": 0
    }
    
    # Analyze indicators
    if wcpm is not None:
        if wcpm < 20:
            indicators["level_1"] += 2
        elif wcpm < 50:
            indicators["level_2"] += 2
        elif wcpm < 80:
            indicators["level_3"] += 2
        elif wcpm < 120:
            indicators["level_4"] += 2
        else:
            indicators["level_5"] += 2
    
    if can_follow_directions is not None:
        if can_follow_directions:
            indicators["level_2"] += 1
            indicators["level_3"] += 1
        else:
            indicators["level_1"] += 2
    
    if writes_sentences is not None:
        if writes_sentences:
            indicators["level_2"] += 1
            indicators["level_3"] += 1
            indicators["level_4"] += 1
        else:
            indicators["level_1"] += 2
    
    if participates_discussions is not None:
        if participates_discussions:
            indicators["level_3"] += 1
            indicators["level_4"] += 1
        else:
            indicators["level_1"] += 1
            indicators["level_2"] += 1
    
    if uses_academic_vocab is not None:
        if uses_academic_vocab:
            indicators["level_3"] += 1
            indicators["level_4"] += 2
            indicators["level_5"] += 1
        else:
            indicators["level_1"] += 1
            indicators["level_2"] += 1
    
    # Determine most likely level
    max_score = max(indicators.values())
    if max_score == 0:
        return {
            "estimated_level": None,
            "confidence": "low",
            "message": "Insufficient data to estimate ESL level"
        }
    
    likely_level = None
    for level, score in indicators.items():
        if score == max_score:
            likely_level = int(level.split("_")[1])
            break
    
    total_indicators = sum(1 for v in [wcpm, can_follow_directions, writes_sentences, 
                                        participates_discussions, uses_academic_vocab] if v is not None)
    
    confidence = "high" if total_indicators >= 4 else "medium" if total_indicators >= 2 else "low"
    
    level_info = get_esl_benchmark_level(likely_level) if likely_level else None
    
    return {
        "estimated_level": likely_level,
        "level_name": level_info.get("name") if level_info else None,
        "level_description": level_info.get("description") if level_info else None,
        "confidence": confidence,
        "indicators_analyzed": total_indicators,
        "score_breakdown": indicators
    }


def get_grade_outcomes(grade: str) -> Dict[str, Any]:
    """
    Get curriculum outcomes for a specific grade.
    
    Args:
        grade: Grade level (K, 1, 2, 3, 4, 5, 6)
        
    Returns:
        Dictionary with grade outcomes and benchmarks
    """
    curriculum = load_curriculum_data()
    grade_levels = curriculum.get("grade_level_outcomes", {})
    
    # Map grade string to key
    grade_key_map = {
        "K": "kindergarten",
        "k": "kindergarten",
        "kindergarten": "kindergarten",
        "0": "kindergarten"
    }
    
    grade_key = grade_key_map.get(grade, f"grade_{grade}")
    return grade_levels.get(grade_key, {})


def get_outcomes_by_skill(skill: str) -> List[Dict[str, Any]]:
    """
    Find all curriculum outcomes that involve a specific skill.
    
    Args:
        skill: Skill to search for (e.g., "phonics", "fluency", "comprehension")
        
    Returns:
        List of matching outcomes across all grades
    """
    curriculum = load_curriculum_data()
    grade_levels = curriculum.get("grade_level_outcomes", {})
    
    matching_outcomes = []
    skill_lower = skill.lower()
    
    for grade_key, grade_data in grade_levels.items():
        outcomes = grade_data.get("outcomes", [])
        for outcome in outcomes:
            outcome_skills = [s.lower() for s in outcome.get("skills", [])]
            if skill_lower in outcome_skills or skill_lower in outcome.get("area", "").lower():
                matching_outcomes.append({
                    "grade": grade_data.get("grade"),
                    **outcome
                })
    
    return matching_outcomes


def align_assessment_to_outcomes(
    assessment_type: str,
    skills_assessed: List[str],
    grade: str
) -> Dict[str, Any]:
    """
    Map an assessment to relevant curriculum outcomes.
    
    Args:
        assessment_type: Type of assessment (e.g., "orf", "maze", "phonics_screening")
        skills_assessed: List of skills the assessment measures
        grade: Target grade level
        
    Returns:
        Dictionary with aligned outcomes and recommendations
    """
    grade_outcomes = get_grade_outcomes(grade)
    outcomes = grade_outcomes.get("outcomes", [])
    
    aligned_outcomes = []
    for outcome in outcomes:
        outcome_skills = set(s.lower() for s in outcome.get("skills", []))
        assessed_skills = set(s.lower() for s in skills_assessed)
        
        overlap = outcome_skills.intersection(assessed_skills)
        if overlap:
            aligned_outcomes.append({
                "outcome_code": outcome.get("code"),
                "outcome_description": outcome.get("description"),
                "area": outcome.get("area"),
                "matching_skills": list(overlap),
                "esl_considerations": outcome.get("esl_considerations")
            })
    
    benchmark_targets = grade_outcomes.get("benchmark_targets", {})
    
    return {
        "assessment_type": assessment_type,
        "grade": grade,
        "aligned_outcomes": aligned_outcomes,
        "benchmark_targets": benchmark_targets,
        "coverage_percentage": len(aligned_outcomes) / len(outcomes) * 100 if outcomes else 0
    }


def get_benchmark_targets(grade: str) -> Dict[str, Any]:
    """
    Get fluency benchmark targets for a grade.
    
    Args:
        grade: Grade level
        
    Returns:
        Dictionary with WCPM and other benchmark targets
    """
    grade_outcomes = get_grade_outcomes(grade)
    return grade_outcomes.get("benchmark_targets", {})


def evaluate_fluency_progress(
    grade: str,
    wcpm: int,
    assessment_period: str = "spring",
    accuracy: Optional[float] = None
) -> Dict[str, Any]:
    """
    Evaluate a student's fluency against grade-level benchmarks.
    
    Args:
        grade: Grade level
        wcpm: Words correct per minute
        assessment_period: "fall", "winter", or "spring"
        accuracy: Optional accuracy percentage (0-1)
        
    Returns:
        Evaluation with status and recommendations
    """
    benchmarks = get_benchmark_targets(grade)
    
    period_key = f"wcpm_{assessment_period.lower()}"
    target_wcpm = benchmarks.get(period_key)
    
    if target_wcpm is None:
        return {
            "status": "unknown",
            "message": f"No benchmark available for grade {grade} {assessment_period}"
        }
    
    percentage_of_target = (wcpm / target_wcpm * 100) if target_wcpm > 0 else 0
    
    if percentage_of_target >= 100:
        status = "at_or_above_benchmark"
        recommendation = "Continue with grade-level instruction"
    elif percentage_of_target >= 80:
        status = "approaching_benchmark"
        recommendation = "Provide targeted fluency practice; monitor progress"
    elif percentage_of_target >= 50:
        status = "below_benchmark"
        recommendation = "Implement intensive fluency intervention; consider additional support"
    else:
        status = "well_below_benchmark"
        recommendation = "Urgent intervention needed; assess for underlying skill gaps"
    
    result = {
        "grade": grade,
        "assessment_period": assessment_period,
        "wcpm": wcpm,
        "target_wcpm": target_wcpm,
        "percentage_of_target": round(percentage_of_target, 1),
        "status": status,
        "recommendation": recommendation
    }
    
    if accuracy is not None:
        target_accuracy = benchmarks.get("oral_reading_accuracy", 0.95)
        result["accuracy"] = accuracy
        result["target_accuracy"] = target_accuracy
        result["accuracy_status"] = "meets_standard" if accuracy >= target_accuracy else "below_standard"
    
    return result


def generate_progress_report(
    student_name: str,
    grade: str,
    esl_level: int,
    l1: str,
    assessments: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate a comprehensive progress report aligned to Alberta curriculum.
    
    Args:
        student_name: Student's name
        grade: Current grade level
        esl_level: ESL proficiency level (1-5)
        l1: Student's first language
        assessments: List of assessment results
        
    Returns:
        Comprehensive progress report
    """
    level_info = get_esl_benchmark_level(esl_level)
    grade_outcomes = get_grade_outcomes(grade)
    benchmarks = get_benchmark_targets(grade)
    
    # Process assessments
    assessment_summary = []
    skills_assessed = set()
    
    for assessment in assessments:
        skills_assessed.update(assessment.get("skills", []))
        assessment_summary.append({
            "type": assessment.get("type"),
            "date": assessment.get("date"),
            "score": assessment.get("score"),
            "benchmark_status": assessment.get("status")
        })
    
    # Determine outcomes coverage
    outcomes = grade_outcomes.get("outcomes", [])
    outcomes_addressed = []
    outcomes_not_addressed = []
    
    for outcome in outcomes:
        outcome_skills = set(s.lower() for s in outcome.get("skills", []))
        if outcome_skills.intersection(skills_assessed):
            outcomes_addressed.append(outcome.get("code"))
        else:
            outcomes_not_addressed.append({
                "code": outcome.get("code"),
                "description": outcome.get("description"),
                "skills": outcome.get("skills")
            })
    
    return {
        "report_date": datetime.now().isoformat(),
        "student_info": {
            "name": student_name,
            "grade": grade,
            "esl_level": esl_level,
            "esl_level_name": level_info.get("name") if level_info else None,
            "first_language": l1
        },
        "proficiency_expectations": {
            "reading": level_info.get("reading") if level_info else None,
            "writing": level_info.get("writing") if level_info else None,
            "listening": level_info.get("listening") if level_info else None,
            "speaking": level_info.get("speaking") if level_info else None
        },
        "benchmark_targets": benchmarks,
        "assessment_summary": assessment_summary,
        "curriculum_coverage": {
            "outcomes_addressed": outcomes_addressed,
            "outcomes_not_yet_addressed": outcomes_not_addressed,
            "coverage_percentage": len(outcomes_addressed) / len(outcomes) * 100 if outcomes else 0
        },
        "recommendations": generate_recommendations(esl_level, l1, grade, assessments)
    }


def generate_recommendations(
    esl_level: int,
    l1: str,
    grade: str,
    assessments: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Generate personalized recommendations based on student profile."""
    recommendations = []
    
    # ESL level-based recommendations
    if esl_level <= 2:
        recommendations.append({
            "area": "Language Support",
            "priority": "high",
            "recommendation": "Provide visual supports and sentence frames for all activities",
            "rationale": f"Students at ESL Level {esl_level} benefit from extensive scaffolding"
        })
        recommendations.append({
            "area": "Vocabulary",
            "priority": "high",
            "recommendation": "Pre-teach key vocabulary before introducing new content",
            "rationale": "Building vocabulary is essential for comprehension development"
        })
    
    if esl_level == 3:
        recommendations.append({
            "area": "Academic Language",
            "priority": "medium",
            "recommendation": "Focus on academic vocabulary and text structures",
            "rationale": "Level 3 students are ready to bridge to academic language"
        })
    
    # Check for fluency concerns in assessments
    for assessment in assessments:
        if assessment.get("type") == "orf" and assessment.get("status") in ["below_benchmark", "well_below_benchmark"]:
            recommendations.append({
                "area": "Fluency",
                "priority": "high",
                "recommendation": "Implement daily fluency practice with repeated reading",
                "rationale": "ORF assessment indicates need for fluency intervention"
            })
            break
    
    # L1-based recommendations
    non_alphabetic_l1s = ["zh", "ko", "ja", "ar"]
    if l1 in non_alphabetic_l1s:
        recommendations.append({
            "area": "Phonics",
            "priority": "medium",
            "recommendation": "Provide additional explicit phonics instruction",
            "rationale": f"Students from {l1} background may need extra support with alphabetic principle"
        })
    
    return recommendations


def get_canadian_content_themes(level: str = "elementary") -> List[str]:
    """Get Canadian content themes appropriate for the specified level."""
    curriculum = load_curriculum_data()
    themes = curriculum.get("canadian_content_themes", {})
    return themes.get(level, [])


def get_pat_preparation_info(grade: str) -> Dict[str, Any]:
    """Get Provincial Achievement Test preparation information."""
    curriculum = load_curriculum_data()
    pat_info = curriculum.get("pat_preparation", {})
    
    if grade in ["6", "grade_6"]:
        return pat_info.get("grade_6_ela", {})
    elif grade in ["9", "grade_9"]:
        return pat_info.get("grade_9_ela", {})
    
    return {}


def get_assessment_tool_info(tool_name: str) -> Dict[str, Any]:
    """Get information about an assessment tool."""
    curriculum = load_curriculum_data()
    tools = curriculum.get("assessment_tools", {})
    
    tool_key_map = {
        "orf": "oral_reading_fluency",
        "oral_reading_fluency": "oral_reading_fluency",
        "maze": "maze",
        "psf": "phoneme_segmentation",
        "phoneme_segmentation": "phoneme_segmentation",
        "lnf": "letter_naming",
        "letter_naming": "letter_naming"
    }
    
    tool_key = tool_key_map.get(tool_name.lower())
    return tools.get(tool_key, {}) if tool_key else {}
