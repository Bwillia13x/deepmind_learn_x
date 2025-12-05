"""Writer's Copilot API endpoints - writing assistance with L1-aware feedback."""

import time
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.logging import log_metric
from app.services.l1_transfer import get_l1_profile, predict_likely_errors


router = APIRouter()


class WritingFeedbackRequest(BaseModel):
    """Request for writing feedback."""
    text: str = Field(..., description="Student's writing to analyze")
    l1: str = Field(default="en", description="Student's L1 language code")
    writing_type: str = Field(default="narrative", description="Type: narrative, opinion, descriptive, comparison")
    grade_level: Optional[str] = Field(None, description="Target grade level")


class Suggestion(BaseModel):
    """A writing suggestion."""
    type: str
    original: str
    suggested: str
    explanation: str


class L1Explanation(BaseModel):
    """L1-aware explanation for a grammar/writing issue."""
    error_type: str
    explanation: str
    tip: str


class WritingFeedbackResponse(BaseModel):
    """Response with writing feedback."""
    original: str
    suggestions: List[Suggestion]
    l1_explanations: List[L1Explanation]
    vocabulary_suggestions: List[str]
    sentence_frames: List[str]
    word_count: int
    readability_level: str


# Vocabulary upgrade suggestions
VOCABULARY_UPGRADES = {
    "good": ["nice", "great", "excellent", "wonderful", "amazing", "fantastic"],
    "bad": ["not good", "poor", "terrible", "awful", "dreadful"],
    "big": ["large", "huge", "enormous", "massive", "gigantic"],
    "small": ["little", "tiny", "minute", "microscopic"],
    "happy": ["glad", "pleased", "delighted", "thrilled", "ecstatic"],
    "sad": ["unhappy", "upset", "miserable", "heartbroken"],
    "said": ["stated", "explained", "exclaimed", "whispered", "shouted"],
    "walk": ["stroll", "march", "stride", "trudge", "wander"],
    "run": ["jog", "sprint", "dash", "race", "hurry"],
    "look": ["glance", "stare", "gaze", "peer", "observe"],
    "eat": ["consume", "devour", "munch", "nibble", "feast"],
    "nice": ["pleasant", "lovely", "delightful", "enjoyable"],
    "very": ["extremely", "incredibly", "remarkably", "exceptionally"],
    "thing": ["object", "item", "matter", "aspect"],
    "stuff": ["materials", "items", "belongings", "possessions"],
}

# Sentence frames by writing type
SENTENCE_FRAMES = {
    "narrative": [
        "First, _____.",
        "Next, _____.",
        "Then, _____.",
        "Finally, _____.",
        "In the beginning, _____.",
        "After that, _____.",
        "Meanwhile, _____.",
        "At last, _____.",
    ],
    "opinion": [
        "I think _____ because _____.",
        "In my opinion, _____.",
        "I believe that _____.",
        "I agree/disagree because _____.",
        "The best part is _____.",
        "One reason is _____.",
        "For example, _____.",
    ],
    "descriptive": [
        "It looks like _____.",
        "It feels like _____.",
        "I can see _____.",
        "The _____ is _____.",
        "There is/are _____.",
        "It smells/sounds/tastes like _____.",
    ],
    "comparison": [
        "_____ is similar to _____ because _____.",
        "_____ is different from _____ because _____.",
        "Both _____ and _____ are _____.",
        "Unlike _____, _____ is _____.",
        "While _____, _____ is _____.",
        "On the other hand, _____.",
    ],
}

# Connecting words for suggestions
CONNECTING_WORDS = [
    "First", "Second", "Third", "Next", "Then", "Finally",
    "However", "Although", "Because", "Therefore", "Also",
    "For example", "In addition", "On the other hand", "As a result",
]

# L1-specific common errors and explanations
L1_GRAMMAR_TIPS = {
    "ar": [
        {
            "error_type": "articles",
            "explanation": "English uses 'a/an' for one thing (first mention) and 'the' for specific things. Arabic doesn't have indefinite articles.",
            "tip": "Ask: Is this the first time? Use 'a/an'. Is it specific? Use 'the'."
        },
        {
            "error_type": "verb_be",
            "explanation": "English ALWAYS needs 'is/are/am' for descriptions. Arabic doesn't use 'be' verbs the same way.",
            "tip": "Example: 'She teacher' → 'She is a teacher'"
        },
    ],
    "zh": [
        {
            "error_type": "articles",
            "explanation": "English requires articles (a, an, the) before nouns. Chinese doesn't have articles.",
            "tip": "Every singular countable noun needs 'a/an' or 'the' before it."
        },
        {
            "error_type": "plural_s",
            "explanation": "English marks plural nouns with -s/-es. Chinese uses quantity words instead.",
            "tip": "More than one? Add -s: 'two book' → 'two books'"
        },
        {
            "error_type": "verb_tense",
            "explanation": "English changes verb forms for past/present/future. Chinese uses time words.",
            "tip": "Yesterday = past tense (-ed): 'I go yesterday' → 'I went yesterday'"
        },
    ],
    "es": [
        {
            "error_type": "word_order",
            "explanation": "In English, adjectives come BEFORE nouns. Spanish puts them after.",
            "tip": "'Casa grande' → 'big house' (not 'house big')"
        },
        {
            "error_type": "subject_pronoun",
            "explanation": "English requires subject pronouns. Spanish can drop them.",
            "tip": "'Is good' → 'It is good' or 'He is good'"
        },
    ],
    "ko": [
        {
            "error_type": "articles",
            "explanation": "English requires articles (a, an, the). Korean doesn't have articles.",
            "tip": "Add 'a/an' for first mention, 'the' for specific things."
        },
        {
            "error_type": "word_order",
            "explanation": "English uses Subject-Verb-Object order. Korean is Subject-Object-Verb.",
            "tip": "'I apple eat' → 'I eat an apple'"
        },
    ],
    "vi": [
        {
            "error_type": "plural_s",
            "explanation": "English marks plurals with -s/-es. Vietnamese doesn't change noun forms.",
            "tip": "'Three cat' → 'Three cats'"
        },
        {
            "error_type": "verb_tense",
            "explanation": "English changes verb forms for tense. Vietnamese uses time words.",
            "tip": "Use -ed for past: 'I walk yesterday' → 'I walked yesterday'"
        },
    ],
    "tl": [
        {
            "error_type": "verb_tense",
            "explanation": "English uses different verb forms for different times.",
            "tip": "Past = -ed: 'I cook yesterday' → 'I cooked yesterday'"
        },
    ],
    "so": [
        {
            "error_type": "articles",
            "explanation": "English uses 'a/an' and 'the' before nouns.",
            "tip": "New thing = a/an. Known thing = the."
        },
    ],
    "uk": [
        {
            "error_type": "articles",
            "explanation": "English requires articles. Ukrainian doesn't have articles.",
            "tip": "'I have book' → 'I have a book'"
        },
    ],
    "pa": [
        {
            "error_type": "word_order",
            "explanation": "English uses Subject-Verb-Object order consistently.",
            "tip": "Keep subject first, then verb, then object."
        },
    ],
}


def analyze_writing(text: str, l1: str) -> List[Suggestion]:
    """Analyze writing for common issues and vocabulary upgrades."""
    suggestions = []
    words = text.lower().split()
    
    # Check for vocabulary upgrades
    for word in words:
        clean_word = word.strip('.,!?;:')
        if clean_word in VOCABULARY_UPGRADES:
            upgrades = VOCABULARY_UPGRADES[clean_word]
            suggestions.append(Suggestion(
                type="vocabulary",
                original=clean_word,
                suggested=upgrades[min(1, len(upgrades) - 1)],
                explanation=f"Try a more specific word: {', '.join(upgrades[:3])}",
            ))
    
    # Check for sentence-initial lowercase (except 'i')
    sentences = text.split('.')
    for sent in sentences:
        sent = sent.strip()
        if sent and sent[0].islower() and sent[0] != 'i':
            suggestions.append(Suggestion(
                type="capitalization",
                original=sent[:20] + "...",
                suggested=sent[0].upper() + sent[1:20] + "...",
                explanation="Start sentences with a capital letter.",
            ))
    
    # Check for repeated words
    for i in range(len(words) - 1):
        if words[i] == words[i + 1] and words[i] not in ['the', 'a', 'an', 'very']:
            suggestions.append(Suggestion(
                type="repetition",
                original=f"{words[i]} {words[i + 1]}",
                suggested=words[i],
                explanation="Avoid repeating the same word.",
            ))
    
    # Check for common ESL patterns based on L1
    if l1 in ['ar', 'zh', 'ko', 'ja', 'vi']:
        # Check for missing articles
        import re
        patterns = [
            (r'\b(is|was|have|has|see|need|want|like|buy|get)\s+([a-z]+ing|[a-z]+ed|[a-z]+)\b', 'article'),
        ]
        for pattern, error_type in patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                word = match.group(2)
                if word not in ['a', 'an', 'the', 'my', 'your', 'his', 'her', 'going', 'doing', 'being']:
                    if not word.endswith('ing') and not word.endswith('ed'):
                        suggestions.append(Suggestion(
                            type="article",
                            original=match.group(0),
                            suggested=f"{match.group(1)} a {word}",
                            explanation="Consider adding an article (a/an/the) before the noun.",
                        ))
    
    return suggestions[:10]  # Limit suggestions


def get_l1_explanations(l1: str) -> List[L1Explanation]:
    """Get L1-specific grammar explanations."""
    tips = L1_GRAMMAR_TIPS.get(l1, [])
    return [L1Explanation(**tip) for tip in tips[:3]]


def estimate_readability(text: str) -> str:
    """Simple readability estimate."""
    words = text.split()
    sentences = text.split('.')
    
    if not words or not sentences:
        return "A1"
    
    avg_sentence_len = len(words) / max(len(sentences), 1)
    avg_word_len = sum(len(w) for w in words) / len(words)
    
    if avg_sentence_len <= 8 and avg_word_len <= 4:
        return "A1"
    elif avg_sentence_len <= 12 and avg_word_len <= 5:
        return "A2"
    elif avg_sentence_len <= 18:
        return "B1"
    else:
        return "B2"


@router.post("/feedback", response_model=WritingFeedbackResponse)
def get_writing_feedback(request: WritingFeedbackRequest) -> WritingFeedbackResponse:
    """
    Get writing feedback with L1-aware suggestions.
    
    Provides:
    - Vocabulary upgrade suggestions
    - Grammar corrections with L1 explanations
    - Sentence frames for the writing type
    - Readability assessment
    """
    start_time = time.time()
    
    # Analyze writing
    suggestions = analyze_writing(request.text, request.l1)
    l1_explanations = get_l1_explanations(request.l1)
    
    # Get sentence frames for writing type
    frames = SENTENCE_FRAMES.get(request.writing_type, SENTENCE_FRAMES["narrative"])
    
    # Estimate readability
    readability = estimate_readability(request.text)
    
    # Word count
    word_count = len(request.text.split())
    
    latency = time.time() - start_time
    log_metric(
        "writing_feedback",
        latency=latency,
        l1=request.l1,
        word_count=word_count,
        suggestion_count=len(suggestions),
    )
    
    return WritingFeedbackResponse(
        original=request.text,
        suggestions=suggestions,
        l1_explanations=l1_explanations,
        vocabulary_suggestions=CONNECTING_WORDS[:8],
        sentence_frames=frames,
        word_count=word_count,
        readability_level=readability,
    )


@router.get("/sentence-frames/{writing_type}")
def get_sentence_frames(writing_type: str):
    """Get sentence frames for a specific writing type."""
    frames = SENTENCE_FRAMES.get(writing_type, SENTENCE_FRAMES["narrative"])
    return {
        "writing_type": writing_type,
        "frames": frames,
    }


@router.get("/vocabulary-upgrades")
def get_vocabulary_upgrades():
    """Get vocabulary upgrade ladders."""
    return {
        "upgrades": VOCABULARY_UPGRADES,
        "connecting_words": CONNECTING_WORDS,
    }


@router.get("/l1-tips/{l1_code}")
def get_l1_writing_tips(l1_code: str):
    """Get L1-specific writing tips."""
    tips = L1_GRAMMAR_TIPS.get(l1_code, [])
    
    # Also get info from L1 transfer service
    profile = get_l1_profile(l1_code)
    
    return {
        "l1_code": l1_code,
        "l1_name": profile.get("name", l1_code) if profile else l1_code,
        "writing_tips": tips,
        "grammar_focus": profile.get("grammar", {}) if profile else {},
    }
