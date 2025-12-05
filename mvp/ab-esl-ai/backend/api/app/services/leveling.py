"""Text leveling and readability service."""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from app.core.logging import log_metric, logger
from app.core.nlp import get_nlp
from app.services.translate import get_gloss, GlossEntry


# NGSL (New General Service List) - simplified top 500
NGSL_TOP_500 = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
    "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
    "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
    "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
    "even", "new", "want", "because", "any", "these", "give", "day", "most", "us",
    "is", "was", "are", "were", "been", "being", "has", "had", "having",
    "does", "did", "doing", "done", "said", "says", "made", "making",
    "got", "getting", "going", "went", "gone", "came", "coming",
    "know", "knew", "known", "knowing", "think", "thought", "thinking",
    "see", "saw", "seen", "seeing", "look", "looked", "looking",
    "find", "found", "finding", "give", "gave", "given", "giving",
    "tell", "told", "telling", "ask", "asked", "asking",
    "need", "needed", "needing", "feel", "felt", "feeling",
    "become", "became", "becoming", "leave", "left", "leaving",
    "put", "putting", "mean", "meant", "meaning",
    "keep", "kept", "keeping", "let", "begin", "began", "begun",
    "seem", "seemed", "seeming", "help", "helped", "helping",
    "show", "showed", "shown", "showing", "hear", "heard", "hearing",
    "play", "played", "playing", "run", "ran", "running",
    "move", "moved", "moving", "live", "lived", "living",
    "believe", "believed", "believing", "hold", "held", "holding",
    "bring", "brought", "bringing", "happen", "happened", "happening",
    "must", "should", "might", "may", "shall", "would", "could",
    "very", "more", "much", "many", "such", "same", "different",
    "own", "still", "high", "long", "little", "again",
}

# Expanded word replacement dictionary for simplification
WORD_REPLACEMENTS = {
    # Academic to simple
    "utilize": "use",
    "demonstrate": "show",
    "approximately": "about",
    "sufficient": "enough",
    "numerous": "many",
    "assistance": "help",
    "purchase": "buy",
    "obtain": "get",
    "require": "need",
    "commence": "start",
    "terminate": "end",
    "facilitate": "help",
    "implement": "do",
    "accomplish": "do",
    "indicate": "show",
    "observe": "see",
    "attempt": "try",
    "proceed": "go",
    "acquire": "get",
    "construct": "build",
    "manufacture": "make",
    "distribute": "give out",
    "investigate": "look into",
    "evaluate": "check",
    "determine": "find out",
    "establish": "set up",
    "maintain": "keep",
    "participate": "take part",
    "communicate": "talk",
    "collaborate": "work together",
    "comprehend": "understand",
    "perceive": "see",
    "recognize": "know",
    "identify": "find",
    "analyze": "study",
    "synthesize": "combine",
    "modify": "change",
    "transform": "change",
    "generate": "make",
    "produce": "make",
    "consume": "use up",
    "eliminate": "remove",
    "substitute": "replace",
    "incorporate": "include",
    "illustrate": "show",
    "demonstrate": "show",
    "emphasize": "stress",
    "summarize": "sum up",
    "conclude": "end",
    "initiate": "start",
    "finalize": "finish",
    "maximize": "make bigger",
    "minimize": "make smaller",
    "prioritize": "put first",
    "categorize": "sort",
    "organize": "arrange",
    # Science terms
    "photosynthesis": "making food from sunlight",
    "precipitation": "rain and snow",
    "evaporation": "water turning to gas",
    "condensation": "gas turning to water",
    "ecosystem": "living things and their home",
    "habitat": "home",
    "organism": "living thing",
    "species": "type of animal or plant",
    "temperature": "how hot or cold",
    "velocity": "speed",
    "acceleration": "speeding up",
    "hypothesis": "guess",
    "experiment": "test",
    "observation": "what you see",
    "conclusion": "what you learned",
    "molecule": "tiny part",
    "atom": "smallest part",
    "element": "basic material",
    "compound": "mixed materials",
    "solution": "mixture",
    "nutrients": "food for the body",
    "respiration": "breathing",
    "circulation": "blood moving",
    "digestion": "breaking down food",
    # Math terms  
    "equation": "math sentence",
    "calculate": "figure out",
    "computation": "math work",
    "quotient": "answer when you divide",
    "remainder": "what is left over",
    "equivalent": "equal",
    "proportion": "part compared to whole",
    "circumference": "distance around a circle",
    "diameter": "line across a circle",
    "perimeter": "distance around a shape",
    # Transition words
    "however": "but",
    "therefore": "so",
    "nevertheless": "still",
    "furthermore": "also",
    "consequently": "so",
    "subsequently": "then",
    "previously": "before",
    "currently": "now",
    "additionally": "also",
    "moreover": "also",
    "meanwhile": "at the same time",
    "nonetheless": "still",
    "alternatively": "or",
    "conversely": "on the other hand",
    "specifically": "exactly",
    "particularly": "especially",
    "essentially": "basically",
    "ultimately": "in the end",
    "initially": "at first",
    "gradually": "slowly",
    "frequently": "often",
    "occasionally": "sometimes",
    "rarely": "not often",
    "constantly": "all the time",
    "immediately": "right away",
    "eventually": "in the end",
    # Phrases
    "prior to": "before",
    "in order to": "to",
    "due to the fact that": "because",
    "in the event that": "if",
    "at this point in time": "now",
    "in spite of": "even though",
    "with regard to": "about",
    "as a result of": "because of",
    "in addition to": "and also",
    "for the purpose of": "to",
    "in accordance with": "following",
    "with respect to": "about",
    "in the vicinity of": "near",
    "at the present time": "now",
    "in the near future": "soon",
    "in the majority of cases": "usually",
    "a large number of": "many",
    "a small number of": "few",
    "in close proximity to": "near",
    "has the ability to": "can",
    "is able to": "can",
}


@dataclass
class ReadabilityScore:
    """Readability analysis of text."""

    cefr: str  # A1, A2, B1, B2, C1, C2
    avg_sentence_length: float
    avg_word_length: float
    difficult_word_pct: float
    flesch_kincaid: float


@dataclass
class Question:
    """A comprehension question."""

    type: str  # 'literal', 'inferential', 'vocabulary'
    q: str
    a: str


@dataclass
class LeveledText:
    """A text leveled to a target."""

    target: str
    text: str
    questions: List[Question]
    gloss: List[GlossEntry]


@dataclass
class LevelingResult:
    """Result of text leveling."""

    original_score: ReadabilityScore
    levels: List[LeveledText]


def level_text(
    text: str,
    targets: List[str],
    l1: Optional[str] = None,
) -> LevelingResult:
    """
    Level text to multiple readability targets.

    Args:
        text: Original text to level
        targets: Target levels (e.g., ['A2', 'B1', 'Gr5'])
        l1: Target language for glossary

    Returns:
        LevelingResult with original score and leveled versions
    """
    log_metric("leveling_request", targets=targets, text_length=len(text))

    # Score original text
    original_score = score_readability(text)

    # Generate leveled versions
    levels = []
    for target in targets:
        leveled = rewrite_to_level(text, target)
        questions = generate_questions(leveled, target)

        if l1:
            gloss_result = get_gloss(leveled, l1, top_k=8)
            gloss = gloss_result.gloss
        else:
            gloss = []

        levels.append(LeveledText(
            target=target,
            text=leveled,
            questions=questions,
            gloss=gloss,
        ))

    log_metric("leveling_result", level_count=len(levels))

    return LevelingResult(original_score=original_score, levels=levels)


def score_readability(text: str) -> ReadabilityScore:
    """Analyze readability of text."""
    nlp = get_nlp()

    if nlp:
        doc = nlp(text)
        sentences = list(doc.sents)
        words = [token for token in doc if token.is_alpha]
    else:
        sentences = text.split(".")
        words = text.split()

    # Calculate metrics
    sentence_count = max(len(sentences), 1)
    word_count = max(len(words), 1)

    avg_sentence_length = word_count / sentence_count

    # Average word length
    total_chars = sum(len(w.text if hasattr(w, "text") else w) for w in words)
    avg_word_length = total_chars / word_count

    # Difficult word percentage (words not in NGSL top 500)
    difficult_count = 0
    for w in words:
        word_text = w.text.lower() if hasattr(w, "text") else w.lower()
        if word_text not in NGSL_TOP_500 and len(word_text) > 3:
            difficult_count += 1
    difficult_word_pct = difficult_count / word_count

    # Flesch-Kincaid Grade Level
    syllable_count = estimate_syllables(text)
    flesch_kincaid = (
        0.39 * (word_count / sentence_count)
        + 11.8 * (syllable_count / word_count)
        - 15.59
    )

    # Estimate CEFR level
    cefr = estimate_cefr(avg_sentence_length, difficult_word_pct, flesch_kincaid)

    return ReadabilityScore(
        cefr=cefr,
        avg_sentence_length=round(avg_sentence_length, 1),
        avg_word_length=round(avg_word_length, 1),
        difficult_word_pct=round(difficult_word_pct, 2),
        flesch_kincaid=round(flesch_kincaid, 1),
    )


def estimate_syllables(text: str) -> int:
    """Estimate syllable count (simple heuristic)."""
    text = text.lower()
    count = 0
    vowels = "aeiouy"
    prev_vowel = False

    for char in text:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel

    return max(count, 1)


def estimate_cefr(avg_sent_len: float, difficult_pct: float, fk_grade: float) -> str:
    """Estimate CEFR level from metrics."""
    if fk_grade <= 2 or (avg_sent_len <= 8 and difficult_pct <= 0.1):
        return "A1"
    elif fk_grade <= 4 or (avg_sent_len <= 12 and difficult_pct <= 0.15):
        return "A2"
    elif fk_grade <= 6 or (avg_sent_len <= 16 and difficult_pct <= 0.2):
        return "B1"
    elif fk_grade <= 9 or (avg_sent_len <= 20 and difficult_pct <= 0.25):
        return "B2"
    elif fk_grade <= 12:
        return "C1"
    else:
        return "C2"


def rewrite_to_level(text: str, target: str) -> str:
    """Rewrite text to a target level with intelligent sentence restructuring."""
    # Get target parameters
    level_config = {
        "A1": {"max_sent_len": 8, "max_word_len": 5, "use_simple_vocab": True},
        "Gr1": {"max_sent_len": 8, "max_word_len": 5, "use_simple_vocab": True},
        "Gr2": {"max_sent_len": 10, "max_word_len": 5, "use_simple_vocab": True},
        "A2": {"max_sent_len": 12, "max_word_len": 6, "use_simple_vocab": True},
        "Gr3": {"max_sent_len": 12, "max_word_len": 6, "use_simple_vocab": True},
        "Gr4": {"max_sent_len": 14, "max_word_len": 7, "use_simple_vocab": False},
        "B1": {"max_sent_len": 16, "max_word_len": 8, "use_simple_vocab": False},
        "Gr5": {"max_sent_len": 16, "max_word_len": 8, "use_simple_vocab": False},
        "Gr6": {"max_sent_len": 18, "max_word_len": 8, "use_simple_vocab": False},
        "B2": {"max_sent_len": 20, "max_word_len": 10, "use_simple_vocab": False},
        "Gr7": {"max_sent_len": 20, "max_word_len": 10, "use_simple_vocab": False},
        "Gr8": {"max_sent_len": 22, "max_word_len": 10, "use_simple_vocab": False},
    }
    
    config = level_config.get(target, {"max_sent_len": 20, "max_word_len": 10, "use_simple_vocab": False})
    max_sent_len = config["max_sent_len"]
    use_simple_vocab = config["use_simple_vocab"]

    # First, apply word replacements (especially for simpler levels)
    result = text
    if use_simple_vocab:
        for complex_word, simple_word in WORD_REPLACEMENTS.items():
            result = re.sub(rf"\b{re.escape(complex_word)}\b", simple_word, result, flags=re.IGNORECASE)
    else:
        # Still replace the most complex academic words for B1/B2
        academic_words = ["utilize", "demonstrate", "approximately", "sufficient", "numerous", 
                        "facilitate", "implement", "accomplish", "subsequently", "consequently"]
        for word in academic_words:
            if word in WORD_REPLACEMENTS:
                result = re.sub(rf"\b{word}\b", WORD_REPLACEMENTS[word], result, flags=re.IGNORECASE)

    # Parse sentences
    nlp = get_nlp()
    if nlp:
        doc = nlp(result)
        sentences = [sent.text.strip() for sent in doc.sents]
    else:
        sentences = [s.strip() + "." for s in result.split(".") if s.strip()]

    rewritten = []
    for sent in sentences:
        rewritten_sent = rewrite_sentence(sent, max_sent_len, use_simple_vocab)
        rewritten.extend(rewritten_sent)

    return " ".join(rewritten)


def rewrite_sentence(sentence: str, max_words: int, use_simple_vocab: bool) -> List[str]:
    """Rewrite a single sentence, potentially splitting it."""
    words = sentence.split()
    
    if len(words) <= max_words:
        return [sentence]
    
    # Try to split at natural break points
    split_points = []
    conjunctions = ["and", "but", "so", "because", "although", "however", "therefore", "while", "when", "if", "since", "unless"]
    punctuation_splits = [",", ";", "—", "-"]
    
    for i, word in enumerate(words):
        word_lower = word.lower().rstrip(".,;:!?")
        # Check for conjunctions
        if word_lower in conjunctions and i >= 3 and i < len(words) - 3:
            split_points.append((i, "conjunction", word_lower))
        # Check for comma followed by conjunction pattern
        if i > 0 and words[i-1].endswith(",") and word_lower in conjunctions:
            split_points.append((i, "comma_conj", word_lower))
        # Check for punctuation that indicates a natural break
        for punct in punctuation_splits:
            if punct in word and i >= 3:
                split_points.append((i + 1, "punctuation", punct))
    
    if not split_points:
        # No good split points, just truncate gracefully
        first_part = " ".join(words[:max_words])
        if not first_part.rstrip().endswith((".", "!", "?")):
            first_part = first_part.rstrip(".,;:") + "."
        return [first_part]
    
    # Find the best split point (closest to middle, but not too short)
    middle = len(words) // 2
    best_split = min(split_points, key=lambda x: abs(x[0] - middle))
    split_idx = best_split[0]
    split_type = best_split[1]
    
    # Create two parts
    if split_type == "conjunction":
        first_part = " ".join(words[:split_idx])
        second_part = " ".join(words[split_idx+1:])  # Skip the conjunction
    elif split_type == "comma_conj":
        first_part = " ".join(words[:split_idx-1]).rstrip(",")
        second_part = " ".join(words[split_idx+1:])
    else:
        first_part = " ".join(words[:split_idx])
        second_part = " ".join(words[split_idx:])
    
    # Clean up and ensure proper punctuation
    first_part = first_part.strip().rstrip(".,;:")
    if first_part and not first_part.endswith((".", "!", "?")):
        first_part += "."
    
    second_part = second_part.strip()
    if second_part:
        # Capitalize first letter
        second_part = second_part[0].upper() + second_part[1:] if len(second_part) > 1 else second_part.upper()
        if not second_part.endswith((".", "!", "?")):
            second_part = second_part.rstrip(".,;:") + "."
    
    results = []
    if first_part:
        results.append(first_part)
    if second_part:
        # Recursively process if still too long
        if len(second_part.split()) > max_words:
            results.extend(rewrite_sentence(second_part, max_words, use_simple_vocab))
        else:
            results.append(second_part)
    
    return results


def generate_questions(text: str, target: str) -> List[Question]:
    """Generate comprehension questions appropriate for the target level."""
    questions = []
    
    # Determine question complexity based on target level
    simple_levels = ["A1", "A2", "Gr1", "Gr2", "Gr3"]
    is_simple = target in simple_levels

    # Extract key information
    nlp = get_nlp()
    if nlp:
        doc = nlp(text)
        sentences = list(doc.sents)
        
        # Find main topic/subject from first sentence
        first_sent = sentences[0] if sentences else None
        main_subject = None
        main_verb = None
        
        if first_sent:
            for token in first_sent:
                if token.dep_ == "nsubj" and not main_subject:
                    main_subject = token.text
                if token.pos_ == "VERB" and not main_verb:
                    main_verb = token.lemma_

        # Question 1: Literal comprehension (who/what is the text about)
        if main_subject:
            if is_simple:
                questions.append(Question(
                    type="literal",
                    q=f"What is this text about?",
                    a=f"This text is about {main_subject.lower()}.",
                ))
            else:
                questions.append(Question(
                    type="literal",
                    q="What is the main topic of this passage?",
                    a=f"The main topic is {main_subject.lower()}.",
                ))
        else:
            questions.append(Question(
                type="literal",
                q="What is the main idea?" if is_simple else "What is the central theme of this passage?",
                a="The text describes...",
            ))

        # Question 2: Detail question
        # Find a specific fact in the text
        for sent in sentences[1:3] if len(sentences) > 1 else sentences:
            for token in sent:
                if token.pos_ == "NUM" or token.ent_type_ in ["DATE", "TIME", "QUANTITY"]:
                    if is_simple:
                        questions.append(Question(
                            type="literal",
                            q=f"Can you find a number in the text?",
                            a=f"Yes, the text mentions {token.text}.",
                        ))
                    else:
                        questions.append(Question(
                            type="literal",
                            q=f"What specific detail does the text provide?",
                            a=f"The text mentions {token.text}.",
                        ))
                    break
            else:
                continue
            break
        
        # Question 3: Inferential/thinking question
        if is_simple:
            questions.append(Question(
                type="inferential",
                q="Why is this important?",
                a="This is important because it helps us understand...",
            ))
        else:
            questions.append(Question(
                type="inferential",
                q="What can you conclude from this information?",
                a="We can conclude that...",
            ))

        # Question 4: Vocabulary question
        difficult_words = []
        for token in doc:
            if (token.pos_ in ["NOUN", "VERB", "ADJ"] and 
                token.text.lower() not in NGSL_TOP_500 and 
                len(token.text) > 4 and
                token.is_alpha):
                difficult_words.append(token.text)
        
        if difficult_words:
            word = difficult_words[0]
            if is_simple:
                questions.append(Question(
                    type="vocabulary",
                    q=f"What does '{word}' mean?",
                    a=f"'{word.capitalize()}' means...",
                ))
            else:
                questions.append(Question(
                    type="vocabulary",
                    q=f"How is the word '{word}' used in this context?",
                    a=f"In this context, '{word}' refers to...",
                ))
        else:
            questions.append(Question(
                type="vocabulary",
                q="What new word did you learn?",
                a="I learned the word...",
            ))

    else:
        # Fallback questions when NLP is not available
        if is_simple:
            questions = [
                Question(type="literal", q="What is this text about?", a="This text is about..."),
                Question(type="literal", q="What did you learn?", a="I learned that..."),
                Question(type="inferential", q="Why is this important?", a="This is important because..."),
            ]
        else:
            questions = [
                Question(type="literal", q="What is the main idea of this passage?", a="The main idea is..."),
                Question(type="inferential", q="What conclusions can you draw from this text?", a="We can conclude that..."),
                Question(type="vocabulary", q="What is a key vocabulary word from this passage?", a="A key word is..."),
            ]

    return questions[:4]  # Return up to 4 questions
