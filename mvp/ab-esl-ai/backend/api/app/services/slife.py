"""
SLIFE (Students with Limited or Interrupted Formal Education) Service

Provides age-appropriate, low-reading-level content and pathways
for newcomer students who have had gaps in their formal schooling.

Critical for Alberta's refugee and newcomer population.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_slife_content() -> Dict[str, Any]:
    """Load SLIFE content library."""
    content_path = Path(__file__).parent.parent.parent.parent.parent / "content" / "slife"
    slife_file = content_path / "slife_content.json"
    
    try:
        with open(slife_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"SLIFE content file not found: {slife_file}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing SLIFE JSON: {e}")
        return {}


def get_slife_overview() -> Dict[str, Any]:
    """Get overview information about SLIFE students and approach."""
    content = load_slife_content()
    return {
        "overview": content.get("slife_overview", {}),
        "content_principles": content.get("content_principles", {}),
        "reading_levels": content.get("reading_levels", {})
    }


def get_all_passages() -> List[Dict[str, Any]]:
    """Get all SLIFE passages."""
    content = load_slife_content()
    return content.get("passages", [])


def get_passage_by_id(passage_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific passage by ID."""
    passages = get_all_passages()
    for passage in passages:
        if passage.get("id") == passage_id:
            return passage
    return None


def get_passages_by_level(level: int) -> List[Dict[str, Any]]:
    """
    Get passages filtered by reading level.
    
    Args:
        level: Reading level 1-3 (emergent, early, transitional)
        
    Returns:
        List of passages at that level
    """
    passages = get_all_passages()
    return [p for p in passages if p.get("level") == level]


def get_passages_by_topic(topic: str) -> List[Dict[str, Any]]:
    """
    Get passages filtered by topic.
    
    Args:
        topic: Topic category (e.g., "daily_life", "health", "school_orientation")
        
    Returns:
        List of passages on that topic
    """
    passages = get_all_passages()
    return [p for p in passages if p.get("topic", "").lower() == topic.lower()]


def get_passages_by_age_range(min_age: int, max_age: int) -> List[Dict[str, Any]]:
    """
    Get passages appropriate for an age range.
    
    Args:
        min_age: Minimum age
        max_age: Maximum age
        
    Returns:
        List of passages appropriate for the age range
    """
    passages = get_all_passages()
    appropriate = []
    
    for passage in passages:
        age_range = passage.get("age_range", "10-18")
        try:
            p_min, p_max = map(int, age_range.split("-"))
            # Check for overlap
            if p_min <= max_age and p_max >= min_age:
                appropriate.append(passage)
        except (ValueError, AttributeError):
            continue
    
    return appropriate


def get_topic_categories() -> Dict[str, Any]:
    """Get all topic categories with descriptions."""
    content = load_slife_content()
    return content.get("topic_categories", {})


def get_scaffolding_strategies() -> Dict[str, Any]:
    """Get scaffolding strategies for SLIFE instruction."""
    content = load_slife_content()
    return content.get("scaffolding_strategies", {})


def get_school_readiness_skills() -> Dict[str, Any]:
    """Get school readiness skills that SLIFE students may need."""
    content = load_slife_content()
    return content.get("school_readiness_skills", {})


def assess_slife_status(
    age: int,
    grade: str,
    years_schooling: int,
    l1_literacy: str,
    arrival_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Assess whether a student may be SLIFE and recommend appropriate level.
    
    Args:
        age: Student's age
        grade: Current grade placement
        years_schooling: Years of formal education
        l1_literacy: L1 literacy level (none, limited, functional, strong)
        arrival_date: Date of arrival in Canada
        
    Returns:
        Assessment with SLIFE indicators and recommendations
    """
    # Calculate expected years of schooling
    grade_num = 0 if grade.upper() == "K" else int(grade) if grade.isdigit() else 0
    expected_years = grade_num + 1  # K + grade years
    
    # Calculate schooling gap
    schooling_gap = expected_years - years_schooling
    
    # Determine SLIFE indicators
    indicators = []
    slife_score = 0
    
    if schooling_gap >= 2:
        indicators.append(f"Schooling gap of {schooling_gap} years (2+ indicates SLIFE)")
        slife_score += 30
    elif schooling_gap >= 1:
        indicators.append(f"Schooling gap of {schooling_gap} year")
        slife_score += 15
    
    if l1_literacy in ["none", "limited"]:
        indicators.append(f"Limited L1 literacy ({l1_literacy})")
        slife_score += 30
    elif l1_literacy == "functional":
        indicators.append("Functional L1 literacy - positive factor")
        slife_score += 10
    
    if age >= 12 and grade_num <= 4:
        indicators.append(f"Age-grade mismatch: age {age} in grade {grade}")
        slife_score += 20
    
    if age >= 15 and grade_num <= 6:
        indicators.append(f"Significant age-grade mismatch")
        slife_score += 25
    
    # Determine classification
    if slife_score >= 50:
        classification = "likely_slife"
        recommended_level = 1 if l1_literacy in ["none", "limited"] else 2
    elif slife_score >= 30:
        classification = "possible_slife"
        recommended_level = 2
    else:
        classification = "not_slife"
        recommended_level = 3
    
    # Get level info
    content = load_slife_content()
    reading_levels = content.get("reading_levels", {})
    level_info = reading_levels.get(f"level_{recommended_level}", {})
    
    return {
        "classification": classification,
        "slife_score": slife_score,
        "indicators": indicators,
        "recommended_reading_level": recommended_level,
        "level_name": level_info.get("name", "Unknown"),
        "level_characteristics": level_info.get("characteristics", []),
        "recommendations": generate_slife_recommendations(classification, l1_literacy, age, grade),
        "additional_needs": identify_additional_needs(l1_literacy, schooling_gap)
    }


def generate_slife_recommendations(
    classification: str,
    l1_literacy: str,
    age: int,
    grade: str
) -> List[str]:
    """Generate recommendations based on SLIFE assessment."""
    recommendations = []
    
    if classification == "likely_slife":
        recommendations.extend([
            "Use SLIFE-designated content with age-appropriate topics",
            "Provide extended time for foundational skill development",
            "Include explicit instruction in school readiness skills",
            "Use visual supports extensively",
            "Consider pull-out literacy intervention"
        ])
        
        if l1_literacy in ["none", "limited"]:
            recommendations.append("Begin with concepts of print and emergent literacy instruction")
        
        if age >= 14:
            recommendations.append("Include practical life skills content (employment, transportation)")
    
    elif classification == "possible_slife":
        recommendations.extend([
            "Monitor progress closely with frequent assessments",
            "Provide additional scaffolding for grade-level content",
            "Use SLIFE-appropriate materials for intervention",
            "Build academic vocabulary explicitly"
        ])
    
    else:
        recommendations.extend([
            "Standard ESL instruction appropriate",
            "Monitor for any gaps in foundational skills",
            "Provide grade-level content with ESL support"
        ])
    
    return recommendations


def identify_additional_needs(l1_literacy: str, schooling_gap: int) -> List[str]:
    """Identify additional needs based on profile."""
    needs = []
    
    if l1_literacy in ["none", "limited"]:
        needs.extend([
            "Concepts of print instruction",
            "Phonological awareness building",
            "Basic numeracy concepts"
        ])
    
    if schooling_gap >= 2:
        needs.extend([
            "School routine orientation",
            "Study skills instruction",
            "Test-taking preparation"
        ])
    
    if schooling_gap >= 4:
        needs.extend([
            "Extended newcomer support",
            "Potential need for modified programming",
            "Case conference recommended"
        ])
    
    return needs


def create_learning_pathway(
    student_id: str,
    current_level: int,
    age: int,
    priority_topics: List[str],
    l1: str
) -> Dict[str, Any]:
    """
    Create a personalized learning pathway for a SLIFE student.
    
    Args:
        student_id: Student identifier
        current_level: Current reading level (1-3)
        age: Student's age
        priority_topics: Topics to prioritize (e.g., ["school", "health"])
        l1: First language code
        
    Returns:
        Structured learning pathway with sequenced content
    """
    all_passages = get_all_passages()
    
    # Filter passages by level and age appropriateness
    eligible_passages = [
        p for p in all_passages
        if p.get("level") == current_level and 
        _is_age_appropriate(p, age)
    ]
    
    # Prioritize by topic
    prioritized = []
    for topic in priority_topics:
        topic_passages = [p for p in eligible_passages if p.get("topic") == topic]
        prioritized.extend(topic_passages)
    
    # Add remaining passages
    remaining = [p for p in eligible_passages if p not in prioritized]
    prioritized.extend(remaining)
    
    # Create pathway units
    units = []
    for i, passage in enumerate(prioritized[:10]):  # First 10 passages
        unit = {
            "unit_number": i + 1,
            "passage_id": passage.get("id"),
            "title": passage.get("title"),
            "topic": passage.get("topic"),
            "word_count": passage.get("word_count"),
            "vocabulary_focus": passage.get("vocabulary", [])[:5],
            "skills": passage.get("skills", []),
            "estimated_sessions": 2 if current_level == 1 else 1
        }
        units.append(unit)
    
    # Calculate totals
    total_sessions = sum(u["estimated_sessions"] for u in units)
    total_words = sum(u["word_count"] for u in units)
    
    return {
        "student_id": student_id,
        "pathway_name": f"SLIFE Level {current_level} Pathway",
        "current_level": current_level,
        "target_level": min(current_level + 1, 3),
        "units": units,
        "total_units": len(units),
        "estimated_sessions": total_sessions,
        "estimated_weeks": total_sessions // 3 + 1,  # ~3 sessions per week
        "total_vocabulary_words": total_words,
        "scaffolding_suggestions": get_scaffolding_strategies(),
        "progress_checkpoints": [
            {"after_unit": 3, "check": "Vocabulary quiz, fluency check"},
            {"after_unit": 6, "check": "Comprehension assessment, consider level change"},
            {"after_unit": 10, "check": "Full assessment, pathway review"}
        ]
    }


def _is_age_appropriate(passage: Dict[str, Any], age: int) -> bool:
    """Check if a passage is appropriate for the student's age."""
    age_range = passage.get("age_range", "10-18")
    try:
        p_min, p_max = map(int, age_range.split("-"))
        return p_min <= age <= p_max
    except (ValueError, AttributeError):
        return True  # Default to appropriate if can't parse


def get_vocabulary_by_topic(topic: str) -> Dict[str, Any]:
    """
    Get vocabulary words grouped by topic for SLIFE instruction.
    
    Args:
        topic: Topic category
        
    Returns:
        Vocabulary words from passages in that topic
    """
    passages = get_passages_by_topic(topic)
    
    all_vocabulary = []
    for passage in passages:
        vocab = passage.get("vocabulary", [])
        for word in vocab:
            if word not in all_vocabulary:
                all_vocabulary.append(word)
    
    return {
        "topic": topic,
        "vocabulary": all_vocabulary,
        "word_count": len(all_vocabulary),
        "passages_included": [p.get("title") for p in passages]
    }


def get_level_progression_criteria() -> Dict[str, Any]:
    """Get criteria for advancing between SLIFE reading levels."""
    return {
        "level_1_to_2": {
            "name": "Emergent to Early",
            "criteria": [
                "Recognizes 50+ high-frequency sight words",
                "Can decode CVC words consistently",
                "Demonstrates basic concepts of print",
                "Can identify main idea with picture support",
                "Can answer simple comprehension questions"
            ],
            "assessments": ["Sight word list", "Phonics screener", "ORF at 20+ WCPM"]
        },
        "level_2_to_3": {
            "name": "Early to Transitional",
            "criteria": [
                "Reads simple sentences fluently (30+ WCPM)",
                "Can decode words with common vowel patterns",
                "Identifies main idea and key details",
                "Uses context clues for unknown words",
                "Can retell simple texts"
            ],
            "assessments": ["ORF at 40+ WCPM", "MAZE comprehension", "Vocabulary assessment"]
        },
        "level_3_exit": {
            "name": "Transitional to Grade-Level",
            "criteria": [
                "Reads at 60+ WCPM with 95% accuracy",
                "Comprehends paragraph-level text",
                "Uses reading strategies independently",
                "Can access grade-level content with support",
                "Demonstrates academic vocabulary growth"
            ],
            "assessments": ["ORF at grade-level benchmark", "Content area reading"]
        }
    }
