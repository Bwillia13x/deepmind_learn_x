"""
Cultural Responsiveness Service

Provides cultural context, background information, and instructional
recommendations for working with students from diverse cultural backgrounds.
Aligned with Alberta's commitment to culturally responsive pedagogy.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_cultural_data() -> Dict[str, Any]:
    """Load cultural data from content directory."""
    content_path = Path(__file__).parent.parent.parent.parent.parent / "content" / "cultural"
    cultural_file = content_path / "cultural_profiles.json"
    
    try:
        with open(cultural_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Cultural data file not found: {cultural_file}")
        return {"cultural_profiles": {}}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing cultural JSON: {e}")
        return {"cultural_profiles": {}}


def get_supported_cultures() -> List[Dict[str, str]]:
    """Get list of supported cultural backgrounds with metadata."""
    data = load_cultural_data()
    cultures = []
    
    for code, info in data.get("cultural_profiles", {}).items():
        cultures.append({
            "code": code,
            "name": info.get("name", code),
            "region": info.get("region", "Unknown"),
            "languages": info.get("languages", [])
        })
    
    return sorted(cultures, key=lambda x: x["name"])


def get_cultural_profile(culture_code: str) -> Optional[Dict[str, Any]]:
    """Get complete cultural profile for a culture."""
    data = load_cultural_data()
    return data.get("cultural_profiles", {}).get(culture_code.lower())


def get_educational_context(culture_code: str) -> Dict[str, Any]:
    """Get educational background and expectations for a culture."""
    profile = get_cultural_profile(culture_code)
    if not profile:
        return {}
    
    return {
        "education_system": profile.get("education_system", {}),
        "classroom_expectations": profile.get("classroom_expectations", {}),
        "parent_involvement_norms": profile.get("parent_involvement_norms", {}),
        "teaching_adaptations": profile.get("teaching_adaptations", [])
    }


def get_communication_norms(culture_code: str) -> Dict[str, Any]:
    """Get communication norms and considerations."""
    profile = get_cultural_profile(culture_code)
    if not profile:
        return {}
    
    return {
        "eye_contact": profile.get("communication", {}).get("eye_contact", "varies"),
        "personal_space": profile.get("communication", {}).get("personal_space", "varies"),
        "authority_interaction": profile.get("communication", {}).get("authority_interaction", ""),
        "gender_dynamics": profile.get("communication", {}).get("gender_dynamics", ""),
        "nonverbal_cues": profile.get("communication", {}).get("nonverbal_cues", []),
        "tips": profile.get("communication", {}).get("tips", [])
    }


def get_cultural_celebrations(culture_code: str) -> List[Dict[str, Any]]:
    """Get important cultural celebrations and observances."""
    profile = get_cultural_profile(culture_code)
    if not profile:
        return []
    
    return profile.get("celebrations", [])


def get_dietary_considerations(culture_code: str) -> Dict[str, Any]:
    """Get dietary restrictions and considerations."""
    profile = get_cultural_profile(culture_code)
    if not profile:
        return {}
    
    return {
        "restrictions": profile.get("dietary", {}).get("restrictions", []),
        "common_foods": profile.get("dietary", {}).get("common_foods", []),
        "fasting_periods": profile.get("dietary", {}).get("fasting_periods", []),
        "school_lunch_notes": profile.get("dietary", {}).get("school_lunch_notes", "")
    }


def get_family_structure_info(culture_code: str) -> Dict[str, Any]:
    """Get information about family structure and dynamics."""
    profile = get_cultural_profile(culture_code)
    if not profile:
        return {}
    
    return {
        "structure": profile.get("family", {}).get("structure", ""),
        "decision_making": profile.get("family", {}).get("decision_making", ""),
        "extended_family_role": profile.get("family", {}).get("extended_family_role", ""),
        "child_rearing": profile.get("family", {}).get("child_rearing", ""),
        "school_engagement_tips": profile.get("family", {}).get("school_engagement_tips", [])
    }


def get_trauma_considerations(culture_code: str) -> Dict[str, Any]:
    """Get trauma-informed considerations for refugee/newcomer populations."""
    profile = get_cultural_profile(culture_code)
    if not profile:
        return {}
    
    trauma_info = profile.get("trauma_considerations", {})
    return {
        "common_experiences": trauma_info.get("common_experiences", []),
        "triggers_to_avoid": trauma_info.get("triggers_to_avoid", []),
        "supportive_practices": trauma_info.get("supportive_practices", []),
        "referral_indicators": trauma_info.get("referral_indicators", [])
    }


def get_teaching_recommendations(culture_code: str) -> Dict[str, Any]:
    """Get culturally responsive teaching recommendations."""
    profile = get_cultural_profile(culture_code)
    if not profile:
        return {}
    
    return {
        "do": profile.get("recommendations", {}).get("do", []),
        "avoid": profile.get("recommendations", {}).get("avoid", []),
        "conversation_starters": profile.get("recommendations", {}).get("conversation_starters", []),
        "classroom_modifications": profile.get("recommendations", {}).get("classroom_modifications", [])
    }


def generate_cultural_brief(
    culture_code: str,
    focus_areas: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate a cultural brief for a specific culture.
    
    Args:
        culture_code: The culture code
        focus_areas: Optional list of areas to focus on
        
    Returns:
        Comprehensive cultural brief
    """
    profile = get_cultural_profile(culture_code)
    if not profile:
        return {"error": f"Culture '{culture_code}' not found"}
    
    if focus_areas is None:
        focus_areas = ["education", "communication", "family", "celebrations"]
    
    brief = {
        "culture": {
            "code": culture_code,
            "name": profile.get("name", culture_code),
            "region": profile.get("region", "Unknown"),
            "languages": profile.get("languages", [])
        }
    }
    
    if "education" in focus_areas:
        brief["education"] = get_educational_context(culture_code)
    if "communication" in focus_areas:
        brief["communication"] = get_communication_norms(culture_code)
    if "family" in focus_areas:
        brief["family"] = get_family_structure_info(culture_code)
    if "celebrations" in focus_areas:
        brief["celebrations"] = get_cultural_celebrations(culture_code)
    if "dietary" in focus_areas:
        brief["dietary"] = get_dietary_considerations(culture_code)
    if "trauma" in focus_areas:
        brief["trauma"] = get_trauma_considerations(culture_code)
    if "teaching" in focus_areas:
        brief["teaching"] = get_teaching_recommendations(culture_code)
    
    return brief


def search_cultures(query: str) -> List[Dict[str, Any]]:
    """Search cultures by name, region, or language."""
    data = load_cultural_data()
    results = []
    query_lower = query.lower()
    
    for code, info in data.get("cultures", {}).items():
        match_score = 0
        
        # Check name
        if query_lower in info.get("name", "").lower():
            match_score += 3
        
        # Check region
        if query_lower in info.get("region", "").lower():
            match_score += 2
        
        # Check languages
        for lang in info.get("languages", []):
            if query_lower in lang.lower():
                match_score += 1
                break
        
        if match_score > 0:
            results.append({
                "code": code,
                "name": info.get("name", code),
                "region": info.get("region", "Unknown"),
                "languages": info.get("languages", []),
                "match_score": match_score
            })
    
    return sorted(results, key=lambda x: -x["match_score"])
