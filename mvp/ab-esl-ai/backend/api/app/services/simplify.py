"""Text simplification service."""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from app.core.logging import log_metric, logger
from app.core.nlp import get_nlp


# High-frequency word replacements (complex -> simple)
WORD_REPLACEMENTS = {
    "utilize": "use",
    "demonstrate": "show",
    "approximately": "about",
    "sufficient": "enough",
    "commence": "start",
    "terminate": "end",
    "obtain": "get",
    "require": "need",
    "assistance": "help",
    "additional": "more",
    "numerous": "many",
    "substantial": "large",
    "frequently": "often",
    "subsequently": "then",
    "however": "but",
    "therefore": "so",
    "nevertheless": "still",
    "furthermore": "also",
    "consequently": "so",
    "previously": "before",
    "currently": "now",
    "immediately": "right away",
    "approximately": "about",
    "accomplish": "do",
    "facilitate": "help",
    "implement": "do",
    "purchase": "buy",
    "inquire": "ask",
    "respond": "answer",
    "indicate": "show",
    "observe": "see",
    "attempt": "try",
    "proceed": "go",
    "ensure": "make sure",
    "regarding": "about",
    "concerning": "about",
    "prior to": "before",
    "in order to": "to",
    "due to the fact that": "because",
    "in the event that": "if",
    "at this point in time": "now",
    "in spite of": "despite",
    "with regard to": "about",
}

# Sentence length limits by simplification strength
MAX_SENTENCE_LENGTH = {
    0: 100,  # No limit
    1: 25,
    2: 18,
    3: 12,
}


@dataclass
class FocusCommand:
    """An extracted focus/command from text."""

    verb: str
    object: Optional[str] = None


@dataclass
class SimplifyResult:
    """Result of text simplification."""

    simplified: str
    focus: List[FocusCommand]
    explanations: List[str]


def simplify_text(text: str, strength: int = 1, focus_commands: bool = True) -> SimplifyResult:
    """
    Simplify English text.

    Args:
        text: Input text to simplify
        strength: Simplification level 0-3 (0=none, 3=maximum)
        focus_commands: Whether to extract imperative commands

    Returns:
        SimplifyResult with simplified text, focus commands, and explanations
    """
    log_metric("simplify_request", strength=strength, input_length=len(text))

    if strength == 0:
        focus = extract_focus_commands(text) if focus_commands else []
        return SimplifyResult(simplified=text, focus=focus, explanations=[])

    # Process text
    simplified_sentences = []
    nlp = get_nlp()
    doc = nlp(text)

    for sent in doc.sents:
        simplified = simplify_sentence(sent.text, strength)
        simplified_sentences.append(simplified)

    simplified_text = " ".join(simplified_sentences)

    # Extract focus commands
    focus = extract_focus_commands(text) if focus_commands else []

    log_metric(
        "simplify_result",
        strength=strength,
        input_length=len(text),
        output_length=len(simplified_text),
        focus_count=len(focus),
    )

    return SimplifyResult(simplified=simplified_text, focus=focus, explanations=[])


def simplify_sentence(sentence: str, strength: int) -> str:
    """Simplify a single sentence."""
    result = sentence

    # Replace complex words with simpler alternatives
    for complex_word, simple_word in WORD_REPLACEMENTS.items():
        pattern = re.compile(re.escape(complex_word), re.IGNORECASE)
        result = pattern.sub(simple_word, result)

    # Convert passive to active voice (basic heuristic)
    if strength >= 2:
        result = simplify_passive_voice(result)

    # Shorten long sentences
    max_len = MAX_SENTENCE_LENGTH.get(strength, 100)
    words = result.split()
    if len(words) > max_len:
        # Try to split at conjunctions
        result = shorten_sentence(result, max_len)

    return result.strip()


def simplify_passive_voice(sentence: str) -> str:
    """
    Basic passive to active voice conversion.
    This is a simplified heuristic, not perfect.
    """
    # Pattern: "X was/were VERB-ed by Y" -> "Y VERB X"
    passive_pattern = r"(\w+)\s+(was|were)\s+(\w+ed)\s+by\s+(\w+)"
    match = re.search(passive_pattern, sentence, re.IGNORECASE)
    if match:
        subject, _, verb, agent = match.groups()
        # Convert past participle to simple past (basic)
        simple_verb = verb
        return re.sub(passive_pattern, f"{agent} {simple_verb} {subject}", sentence, flags=re.IGNORECASE)
    return sentence


def shorten_sentence(sentence: str, max_words: int) -> str:
    """Shorten a sentence by splitting at conjunctions."""
    words = sentence.split()
    if len(words) <= max_words:
        return sentence

    # Find split points (conjunctions, commas with conjunctions)
    split_words = ["and", "but", "or", "so", "because", "although", "however", "therefore"]

    for i, word in enumerate(words):
        if word.lower().rstrip(",") in split_words and i >= max_words // 2:
            first_part = " ".join(words[:i])
            if not first_part.endswith("."):
                first_part += "."
            return first_part

    # If no good split point, just truncate
    truncated = " ".join(words[:max_words])
    if not truncated.endswith("."):
        truncated += "..."
    return truncated


def extract_focus_commands(text: str) -> List[FocusCommand]:
    """
    Extract imperative commands from text.
    Useful for highlighting instructions in classroom context.
    """
    commands = []
    nlp = get_nlp()
    doc = nlp(text)

    # Common classroom command verbs
    command_verbs = {
        "open", "close", "read", "write", "listen", "look", "turn",
        "sit", "stand", "come", "go", "take", "put", "get", "give",
        "show", "tell", "answer", "ask", "find", "make", "draw",
        "circle", "underline", "highlight", "copy", "complete",
        "finish", "start", "begin", "stop", "continue", "repeat",
        "remember", "think", "try", "practice", "study", "review",
    }

    for sent in doc.sents:
        # Check if sentence starts with a verb (imperative)
        tokens = list(sent)
        if not tokens:
            continue

        first_token = tokens[0]

        # Skip if starts with subject pronoun
        if first_token.text.lower() in ["i", "you", "he", "she", "it", "we", "they"]:
            continue

        # Check for imperative (starts with verb base form)
        if first_token.pos_ == "VERB" or first_token.lemma_.lower() in command_verbs:
            verb = first_token.lemma_.lower()

            # Find direct object
            obj = None
            for child in first_token.children:
                if child.dep_ in ["dobj", "pobj", "attr"]:
                    # Get the full noun phrase
                    obj_tokens = [child.text]
                    for c in child.children:
                        if c.dep_ in ["compound", "amod", "det"]:
                            obj_tokens.insert(0, c.text)
                    obj = " ".join(obj_tokens)
                    break

            commands.append(FocusCommand(verb=verb, object=obj))

        # Also check for "please + verb" pattern
        if first_token.text.lower() == "please" and len(tokens) > 1:
            second_token = tokens[1]
            if second_token.pos_ == "VERB":
                verb = second_token.lemma_.lower()
                obj = None
                for child in second_token.children:
                    if child.dep_ in ["dobj", "pobj"]:
                        obj = child.text
                        break
                commands.append(FocusCommand(verb=verb, object=obj))

    return commands
