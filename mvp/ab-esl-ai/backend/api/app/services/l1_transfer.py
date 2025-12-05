"""L1 Linguistic Transfer Intelligence Service.

Provides language-specific transfer analysis, error prediction, and targeted
intervention recommendations based on the student's first language (L1).
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TransferPattern:
    """Represents a language transfer pattern."""
    category: str  # grammar, phonology, vocabulary
    feature: str  # articles, verb_tense, etc.
    priority: Priority
    common_errors: List[str]
    teaching_approach: str
    exercises: List[str]


@dataclass
class InterventionRecommendation:
    """A recommended intervention for a student."""
    skill_area: str
    priority: Priority
    description: str
    exercises: List[str]
    teaching_tip: str
    estimated_focus_weeks: int


# Cache for loaded transfer patterns
_transfer_patterns_cache: Optional[Dict[str, Any]] = None


def load_transfer_patterns() -> Dict[str, Any]:
    """Load L1 transfer patterns from content directory."""
    global _transfer_patterns_cache
    
    if _transfer_patterns_cache is not None:
        return _transfer_patterns_cache
    
    # From services/l1_transfer.py -> services -> app -> api -> backend -> ab-esl-ai (5 parents)
    patterns_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "content" / "l1_transfer" / "linguistic_patterns.json"
    
    if not patterns_path.exists():
        logger.warning(f"L1 transfer patterns file not found: {patterns_path}")
        return {"languages": {}}
    
    with open(patterns_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        _transfer_patterns_cache = data
    
    num_languages = len(_transfer_patterns_cache.get("languages", {})) if _transfer_patterns_cache else 0
    logger.info(f"Loaded L1 transfer patterns for {num_languages} languages")
    return _transfer_patterns_cache if _transfer_patterns_cache else {"languages": {}}


def get_supported_l1_languages() -> List[Dict[str, str]]:
    """Get list of supported L1 languages with metadata."""
    patterns = load_transfer_patterns()
    languages = []
    
    for code, data in patterns.get("languages", {}).items():
        languages.append({
            "code": code,
            "name": data.get("name", code),
            "family": data.get("family", "Unknown"),
            "writing_system": data.get("writing_system", "Unknown")
        })
    
    return sorted(languages, key=lambda x: x["name"])


def get_l1_profile(l1_code: str) -> Optional[Dict[str, Any]]:
    """Get complete linguistic profile for a language."""
    patterns = load_transfer_patterns()
    return patterns.get("languages", {}).get(l1_code.lower())


def get_phonological_difficulties(l1_code: str) -> List[Dict[str, Any]]:
    """Get list of difficult phonemes for speakers of a given L1."""
    profile = get_l1_profile(l1_code)
    if not profile:
        return []
    
    phonology = profile.get("phonology", {})
    difficulties = phonology.get("difficult_phonemes", [])
    
    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    difficulties.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 4))
    
    return difficulties


def get_grammar_challenges(l1_code: str) -> List[Dict[str, Any]]:
    """Get grammar areas that are challenging for speakers of a given L1."""
    profile = get_l1_profile(l1_code)
    if not profile:
        return []
    
    grammar = profile.get("grammar", {})
    challenges = []
    
    for feature, data in grammar.items():
        if isinstance(data, dict) and "priority" in data:
            challenges.append({
                "feature": feature,
                "priority": data.get("priority", "medium"),
                "issue": data.get("issue", ""),
                "common_errors": data.get("common_errors", []),
                "teaching_approach": data.get("teaching_approach", ""),
                "exercises": data.get("exercises", [])
            })
    
    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    challenges.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 4))
    
    return challenges


def get_cognates(l1_code: str) -> List[Dict[str, str]]:
    """Get English cognates for a given L1."""
    profile = get_l1_profile(l1_code)
    if not profile:
        return []
    
    vocabulary = profile.get("vocabulary", {})
    return vocabulary.get("cognates", [])


def get_false_friends(l1_code: str) -> List[Dict[str, str]]:
    """Get false friends (deceptive cognates) for a given L1."""
    profile = get_l1_profile(l1_code)
    if not profile:
        return []
    
    vocabulary = profile.get("vocabulary", {})
    return vocabulary.get("false_friends", [])


def get_literacy_transfer_info(l1_code: str) -> Dict[str, Any]:
    """Get information about literacy skills that may transfer from L1."""
    profile = get_l1_profile(l1_code)
    if not profile:
        return {}
    
    return profile.get("literacy_transfer", {})


def get_cultural_considerations(l1_code: str) -> List[str]:
    """Get cultural considerations for working with speakers of a given L1."""
    profile = get_l1_profile(l1_code)
    if not profile:
        return []
    
    return profile.get("cultural_considerations", [])


def predict_likely_errors(l1_code: str, text: str) -> List[Dict[str, Any]]:
    """
    Analyze text and predict likely errors based on L1 transfer patterns.
    
    This is a rule-based analysis that flags potential issues based on
    known transfer patterns for the given L1.
    """
    profile = get_l1_profile(l1_code)
    if not profile:
        return []
    
    predictions = []
    text_lower = text.lower()
    words = text_lower.split()
    
    grammar = profile.get("grammar", {})
    
    # Check for article issues (common for many L1s)
    article_data = grammar.get("articles", {})
    if article_data.get("priority") in ["critical", "high"]:
        # Check for missing articles before common nouns
        common_nouns = ["book", "pencil", "teacher", "student", "school", "class", "desk", "dog", "cat", "car"]
        for noun in common_nouns:
            if noun in words:
                idx = words.index(noun)
                if idx == 0 or words[idx-1] not in ["a", "an", "the", "my", "your", "his", "her", "this", "that"]:
                    predictions.append({
                        "type": "grammar",
                        "feature": "articles",
                        "location": f"before '{noun}'",
                        "issue": f"Possible missing article before '{noun}'",
                        "suggestion": f"Consider: 'a {noun}' or 'the {noun}'",
                        "l1_explanation": article_data.get("issue", "Article usage differs from English")
                    })
    
    # Check for verb 'be' issues (common for Arabic, Chinese)
    verb_be_data = grammar.get("verb_be", {})
    if verb_be_data.get("priority") in ["critical", "high"]:
        # Simple pattern: pronoun + adjective without 'be'
        pronouns = ["i", "he", "she", "it", "we", "they", "you"]
        adjectives = ["happy", "sad", "tired", "hungry", "good", "bad", "big", "small", "new", "old"]
        for i, word in enumerate(words):
            if word in pronouns and i + 1 < len(words):
                if words[i + 1] in adjectives:
                    predictions.append({
                        "type": "grammar",
                        "feature": "verb_be",
                        "location": f"'{word} {words[i+1]}'",
                        "issue": f"Possible missing 'is/are/am' between '{word}' and '{words[i+1]}'",
                        "suggestion": f"Consider: '{word} {'am' if word == 'i' else 'is' if word in ['he', 'she', 'it'] else 'are'} {words[i+1]}'",
                        "l1_explanation": verb_be_data.get("issue", "")
                    })
    
    # Check for word order issues (SOV languages)
    word_order_data = grammar.get("word_order", {})
    if word_order_data.get("priority") in ["critical", "high"]:
        # Flag if sentence appears to end with a verb
        common_verbs = ["go", "eat", "drink", "read", "write", "play", "like", "want", "need", "have"]
        if words and words[-1].rstrip(".,!?") in common_verbs:
            predictions.append({
                "type": "grammar",
                "feature": "word_order",
                "location": "end of sentence",
                "issue": f"Sentence may have verb at end (SOV pattern from {profile.get('name', 'L1')})",
                "suggestion": "Check word order - English typically uses Subject-Verb-Object",
                "l1_explanation": word_order_data.get("issue", "")
            })
    
    return predictions


def generate_intervention_plan(
    l1_code: str,
    assessment_data: Optional[Dict[str, Any]] = None
) -> List[InterventionRecommendation]:
    """
    Generate a prioritized intervention plan based on L1 transfer patterns
    and optional assessment data.
    """
    patterns = load_transfer_patterns()
    profile = get_l1_profile(l1_code)
    
    if not profile:
        logger.warning(f"No profile found for L1: {l1_code}")
        return []
    
    recommendations = []
    
    # Get priority intervention areas for this L1
    priority_areas = patterns.get("intervention_priority_by_l1", {}).get(l1_code.lower(), [])
    
    # Add phonology interventions
    for phoneme_data in get_phonological_difficulties(l1_code)[:3]:  # Top 3
        recommendations.append(InterventionRecommendation(
            skill_area="pronunciation",
            priority=Priority(phoneme_data.get("priority", "medium")),
            description=phoneme_data.get("issue", ""),
            exercises=phoneme_data.get("minimal_pairs", []),
            teaching_tip=phoneme_data.get("teaching_tip", ""),
            estimated_focus_weeks=2 if phoneme_data.get("priority") == "critical" else 1
        ))
    
    # Add grammar interventions
    for grammar_data in get_grammar_challenges(l1_code)[:3]:  # Top 3
        recommendations.append(InterventionRecommendation(
            skill_area=f"grammar_{grammar_data['feature']}",
            priority=Priority(grammar_data.get("priority", "medium")),
            description=grammar_data.get("issue", ""),
            exercises=grammar_data.get("exercises", []),
            teaching_tip=grammar_data.get("teaching_approach", ""),
            estimated_focus_weeks=3 if grammar_data.get("priority") == "critical" else 2
        ))
    
    # Add literacy transfer considerations
    literacy_info = get_literacy_transfer_info(l1_code)
    if literacy_info.get("script_direction") == "RTL_to_LTR":
        recommendations.append(InterventionRecommendation(
            skill_area="print_concepts",
            priority=Priority.HIGH,
            description="RTL to LTR script direction transition",
            exercises=["directionality_tracking", "left_to_right_practice"],
            teaching_tip="Explicit modeling of left-to-right reading; finger tracking",
            estimated_focus_weeks=2
        ))
    
    if literacy_info.get("phonemic_awareness", {}).get("critical_gap"):
        recommendations.append(InterventionRecommendation(
            skill_area="phonemic_awareness",
            priority=Priority.CRITICAL,
            description="May lack phoneme-level awareness due to logographic L1",
            exercises=["sound_segmentation", "phoneme_isolation", "blending"],
            teaching_tip="Start with phonemic awareness basics even for older students",
            estimated_focus_weeks=4
        ))
    
    # Sort by priority
    priority_order = {Priority.CRITICAL: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
    recommendations.sort(key=lambda x: priority_order.get(x.priority, 4))
    
    return recommendations


def get_contrastive_feedback(
    l1_code: str,
    error_type: str,
    error_context: str
) -> Dict[str, Any]:
    """
    Generate L1-aware contrastive feedback for a specific error.
    
    Returns explanation that references the L1 and helps student understand
    why they made the error and how to correct it.
    """
    profile = get_l1_profile(l1_code)
    if not profile:
        return {
            "feedback": "Please check this part of your writing.",
            "l1_explanation": None
        }
    
    l1_name = profile.get("name", "your first language")
    grammar = profile.get("grammar", {})
    
    feedback_templates = {
        "article_missing": {
            "feedback": f"You may need an article (a, an, the) here.",
            "l1_explanation": f"In {l1_name}, articles work differently or don't exist. In English, we usually need 'a/an' (first mention, non-specific) or 'the' (known/specific) before singular countable nouns.",
            "practice_tip": "Ask yourself: 'Is this noun countable? Is it specific or general?'"
        },
        "verb_tense": {
            "feedback": "Check the verb form for this time (past, present, future).",
            "l1_explanation": f"In {l1_name}, verbs may not change form for tense. In English, we must change the verb to show when something happens.",
            "practice_tip": "Look for time words (yesterday, now, tomorrow) to help choose the right verb form."
        },
        "word_order": {
            "feedback": "The word order might need adjustment.",
            "l1_explanation": f"{l1_name} often puts words in a different order than English. English typically uses Subject-Verb-Object order.",
            "practice_tip": "Try: WHO did it + WHAT they did + to WHAT/WHOM"
        },
        "plural_missing": {
            "feedback": "When there's more than one, we usually add -s or -es to the noun.",
            "l1_explanation": f"In {l1_name}, nouns may not change form for plural. In English, most plural nouns need -s.",
            "practice_tip": "If there's a number > 1, check if the noun has -s."
        },
        "pronunciation": {
            "feedback": "This sound might be tricky - let's practice!",
            "l1_explanation": f"This sound doesn't exist in {l1_name}, so your brain needs to learn a new mouth position.",
            "practice_tip": "Watch the mouth position and practice slowly."
        }
    }
    
    template = feedback_templates.get(error_type, {
        "feedback": "Let's look at this more closely.",
        "l1_explanation": f"This works differently in English than in {l1_name}.",
        "practice_tip": "Keep practicing - this will get easier!"
    })
    
    return {
        "error_type": error_type,
        "context": error_context,
        "feedback": template["feedback"],
        "l1_explanation": template["l1_explanation"],
        "practice_tip": template["practice_tip"],
        "l1_name": l1_name
    }


def get_vocabulary_strategies(l1_code: str) -> Dict[str, Any]:
    """
    Get vocabulary learning strategies tailored to L1.
    
    For Romance languages, emphasize cognates.
    For others, focus on context and visual support.
    """
    profile = get_l1_profile(l1_code)
    if not profile:
        return {"strategy": "general", "tips": []}
    
    cognates = get_cognates(l1_code)
    false_friends = get_false_friends(l1_code)
    cognate_strategy = profile.get("vocabulary", {}).get("cognate_strategy", "")
    
    if "HIGH" in cognate_strategy.upper() or len(cognates) >= 5:
        return {
            "strategy": "cognate_rich",
            "description": f"{profile.get('name')} has many English cognates - use them!",
            "tips": [
                "Look for words that look/sound similar to your language",
                "Academic vocabulary often has Latin/Greek roots shared with English",
                "Be careful of false friends (words that look similar but mean different things)"
            ],
            "cognates_sample": cognates[:5],
            "false_friends_warning": false_friends[:3] if false_friends else []
        }
    else:
        return {
            "strategy": "context_visual",
            "description": "Build vocabulary through context, pictures, and real-world connections",
            "tips": [
                "Use pictures and real objects to learn new words",
                "Learn words in phrases and sentences, not alone",
                "Connect new words to your daily life and experiences",
                "Use the word in speaking and writing to remember it"
            ],
            "cognates_sample": cognates[:3] if cognates else [],
            "false_friends_warning": []
        }


def generate_l1_aware_exercise(
    l1_code: str,
    skill_area: str,
    difficulty: str = "medium"
) -> Dict[str, Any]:
    """
    Generate an exercise targeting a skill area with L1-specific scaffolding.
    """
    profile = get_l1_profile(l1_code)
    if not profile:
        return {"error": f"Unknown L1: {l1_code}"}
    
    l1_name = profile.get("name", "L1")
    
    if skill_area == "articles":
        return {
            "type": "article_decision",
            "skill": "articles",
            "l1_scaffolding": True,
            "instructions": "Choose the correct article (a, an, the, or Ø for no article)",
            "l1_note": f"Remember: {profile.get('grammar', {}).get('articles', {}).get('issue', 'English articles may be new to you')}",
            "items": [
                {"sentence": "I saw ___ movie yesterday.", "options": ["a", "an", "the", "Ø"], "correct": "a", "explanation": "First mention, non-specific movie"},
                {"sentence": "___ sun is bright today.", "options": ["A", "An", "The", "Ø"], "correct": "The", "explanation": "There's only one sun - it's unique"},
                {"sentence": "She is ___ teacher.", "options": ["a", "an", "the", "Ø"], "correct": "a", "explanation": "Job/profession uses 'a/an'"},
                {"sentence": "I like ___ music.", "options": ["a", "an", "the", "Ø"], "correct": "Ø", "explanation": "General category - no article needed"},
                {"sentence": "Please close ___ door.", "options": ["a", "an", "the", "Ø"], "correct": "the", "explanation": "Specific door that we both know about"}
            ]
        }
    
    elif skill_area == "word_order":
        return {
            "type": "sentence_unscramble",
            "skill": "word_order",
            "l1_scaffolding": True,
            "instructions": "Put the words in the correct English order (Subject - Verb - Object)",
            "l1_note": f"In {l1_name}, the verb often comes at the end. In English, it comes after the subject.",
            "items": [
                {"words": ["pizza", "likes", "She"], "correct": "She likes pizza", "structure": "S-V-O"},
                {"words": ["the", "book", "reads", "He"], "correct": "He reads the book", "structure": "S-V-O"},
                {"words": ["to", "school", "go", "I"], "correct": "I go to school", "structure": "S-V-Prep Phrase"},
                {"words": ["an", "apple", "eating", "is", "The", "boy"], "correct": "The boy is eating an apple", "structure": "S-V-O"},
                {"words": ["plays", "soccer", "My", "brother"], "correct": "My brother plays soccer", "structure": "S-V-O"}
            ]
        }
    
    elif skill_area == "verb_tense":
        return {
            "type": "tense_selection",
            "skill": "verb_tense",
            "l1_scaffolding": True,
            "instructions": "Choose the correct verb form based on the time expression",
            "l1_note": f"In {l1_name}, verbs may not change for time. In English, we MUST change the verb form.",
            "items": [
                {"sentence": "Yesterday, I ___ to the store.", "options": ["go", "went", "will go"], "correct": "went", "time": "past"},
                {"sentence": "Right now, she ___ her homework.", "options": ["does", "did", "is doing"], "correct": "is doing", "time": "present progressive"},
                {"sentence": "Tomorrow, we ___ the museum.", "options": ["visit", "visited", "will visit"], "correct": "will visit", "time": "future"},
                {"sentence": "Every day, he ___ breakfast at 7.", "options": ["eats", "ate", "eating"], "correct": "eats", "time": "present habit"},
                {"sentence": "Last week, they ___ a movie.", "options": ["watch", "watched", "watching"], "correct": "watched", "time": "past"}
            ]
        }
    
    else:
        return {
            "type": "general",
            "skill": skill_area,
            "message": f"Exercise type '{skill_area}' not yet implemented"
        }
