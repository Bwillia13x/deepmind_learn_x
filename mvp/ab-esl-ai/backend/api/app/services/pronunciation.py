"""Pronunciation scoring service for Speaking Coach."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import difflib

from app.core.logging import logger


def load_minimal_pairs() -> Dict:
    """Load minimal pairs exercises from content directory."""
    # Path: backend/api/app/services/pronunciation.py -> content/speaking/minimal_pairs.json
    # Go up 5 levels from this file to reach ab-esl-ai directory
    pairs_path = Path(__file__).parent.parent.parent.parent.parent / "content" / "speaking" / "minimal_pairs.json"
    
    if not pairs_path.exists():
        logger.warning(f"Minimal pairs file not found: {pairs_path}")
        return {"pairs": []}
    
    with open(pairs_path, "r", encoding="utf-8") as f:
        return json.load(f)


def score_word_pronunciation(
    transcribed_text: str,
    target_word: str,
    confidence: float = 0.0
) -> Dict:
    """
    Score pronunciation accuracy for a single word.
    
    Args:
        transcribed_text: What the ASR heard
        target_word: What the student should have said
        confidence: ASR confidence score (0.0-1.0)
    
    Returns:
        Dict with score, feedback, and phoneme-level details
    """
    transcribed = transcribed_text.lower().strip()
    target = target_word.lower().strip()
    
    # Exact match = perfect score
    if transcribed == target:
        return {
            "score": 1.0,
            "match": "exact",
            "transcribed": transcribed,
            "target": target,
            "feedback": "Perfect pronunciation!",
            "confidence": confidence,
        }
    
    # Similarity score using sequence matching
    similarity = difflib.SequenceMatcher(None, transcribed, target).ratio()
    
    # Check if it's a common substitution (minimal pair confusion)
    feedback = "Try again, focus on the sounds."
    
    if similarity > 0.8:
        match_type = "close"
        feedback = "Very close! Pay attention to vowel sounds."
    elif similarity > 0.5:
        match_type = "partial"
        feedback = "Getting there. Focus on the middle sounds."
    else:
        match_type = "poor"
        feedback = "Let's try that again. Listen carefully to the target word."
    
    return {
        "score": similarity,
        "match": match_type,
        "transcribed": transcribed,
        "target": target,
        "feedback": feedback,
        "confidence": confidence,
    }


def score_minimal_pair(
    transcribed_word1: str,
    transcribed_word2: str,
    pair_id: str,
    confidence: float = 0.0
) -> Dict:
    """
    Score a minimal pair exercise (two contrasting sounds).
    
    Args:
        transcribed_word1: First word transcribed
        transcribed_word2: Second word transcribed
        pair_id: ID of the minimal pair exercise
        confidence: Average ASR confidence
    
    Returns:
        Dict with scores for both words and overall assessment
    """
    pairs_data = load_minimal_pairs()
    
    # Find the pair
    pair_info = None
    for pair in pairs_data.get("pairs", []):
        if pair["id"] == pair_id:
            pair_info = pair
            break
    
    if not pair_info:
        return {"error": f"Pair {pair_id} not found"}
    
    # Get target words (using first example)
    if pair_info["words"]:
        target_word1 = pair_info["words"][0]["word1"]
        target_word2 = pair_info["words"][0]["word2"]
    else:
        return {"error": "No words in pair"}
    
    # Score each word
    score1 = score_word_pronunciation(transcribed_word1, target_word1, confidence)
    score2 = score_word_pronunciation(transcribed_word2, target_word2, confidence)
    
    # Overall assessment
    avg_score = (score1["score"] + score2["score"]) / 2
    
    both_perfect = score1["match"] == "exact" and score2["match"] == "exact"
    
    if both_perfect:
        overall_feedback = f"Excellent! You can clearly distinguish between {pair_info['sounds'][0]} and {pair_info['sounds'][1]}."
    elif avg_score > 0.7:
        overall_feedback = f"Good work! Keep practicing the contrast between {pair_info['sounds'][0]} and {pair_info['sounds'][1]}."
    else:
        overall_feedback = f"Focus on the difference between {pair_info['sounds'][0]} and {pair_info['sounds'][1]}. Listen to the model and try again."
    
    return {
        "pair_id": pair_id,
        "sounds": pair_info["sounds"],
        "word1": score1,
        "word2": score2,
        "average_score": round(avg_score, 2),
        "overall_feedback": overall_feedback,
        "difficulty": pair_info["difficulty"],
    }


def get_exercises_for_l1(l1_language: str) -> List[Dict]:
    """
    Get recommended pronunciation exercises for a specific L1.
    
    Args:
        l1_language: ISO language code (e.g., 'es', 'ar', 'zh')
    
    Returns:
        List of minimal pair exercises targeted for this L1
    """
    pairs_data = load_minimal_pairs()
    
    recommended = []
    for pair in pairs_data.get("pairs", []):
        if l1_language in pair.get("target_l1", []):
            recommended.append({
                "pair_id": pair["id"],
                "sounds": pair["sounds"],
                "difficulty": pair["difficulty"],
                "sample_words": pair["words"][:2] if pair["words"] else [],
            })
    
    # Sort by difficulty: easy -> medium -> hard
    difficulty_order = {"easy": 1, "medium": 2, "hard": 3}
    recommended.sort(key=lambda x: difficulty_order.get(x["difficulty"], 2))
    
    return recommended
