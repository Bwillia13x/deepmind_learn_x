"""Decodable text generation service."""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from app.core.logging import log_metric, logger

# Phonics scope and sequence (simplified)
# Maps graphemes to common words that use only those graphemes
PHONICS_WORDS: Dict[str, List[str]] = {
    # CVC patterns with short vowels
    "a": ["at", "an", "am", "as", "ax"],
    "e": ["Ed", "em"],
    "i": ["in", "it", "is", "if"],
    "o": ["on", "ox"],
    "u": ["up", "us"],
    "m": ["am", "mom", "him", "sum", "map", "mat", "man", "mop"],
    "s": ["sat", "sip", "sit", "sun", "sad", "Sam", "sis", "sob"],
    "t": ["at", "it", "sat", "sit", "tap", "top", "tip", "tin", "tan", "tot"],
    "p": ["pat", "pan", "pip", "pop", "pup", "pin", "pen", "pot", "pad"],
    "n": ["an", "in", "on", "nap", "nip", "not", "nut", "nod", "net"],
    "c": ["cat", "can", "cap", "cot", "cup", "cab", "cub"],
    "d": ["dad", "did", "dig", "dot", "dip", "dim", "den", "dud"],
    "g": ["got", "gap", "gum", "gas", "gag", "pig", "big", "dig", "wig"],
    "b": ["bat", "bit", "bun", "bus", "but", "bad", "big", "bib", "bud", "bed"],
    "h": ["hat", "hit", "hot", "hum", "hug", "hip", "hop", "had", "hid"],
    "r": ["rat", "ran", "rip", "rot", "rub", "rug", "rim", "ram", "red"],
    "f": ["fat", "fan", "fit", "fun", "fad", "fig", "fin", "fog"],
    "l": ["lap", "let", "lit", "lot", "log", "lid"],
    "w": ["was", "wet", "wig", "win", "wit", "wag"],
    "j": ["jam", "jab", "jet", "jig", "jot", "jug"],
    "k": ["kid", "kit", "Kim"],
    "x": ["ax", "ox", "six", "fix", "mix", "box", "fox", "wax"],
    "v": ["van", "vat", "vet"],
    "y": ["yam", "yes", "yet"],
    "z": ["zap", "zip", "zig"],
    # Digraphs
    "sh": ["ship", "shop", "shot", "shut", "shin", "shed", "shag"],
    "ch": ["chat", "chop", "chip", "chin", "chap"],
    "th": ["that", "them", "this", "than", "thin"],
    "wh": ["when", "whip"],
    "ck": ["back", "pack", "tack", "kick", "pick", "sick", "tick", "duck", "luck", "rock", "sock"],
    # Long vowels
    "ee": ["see", "bee", "fee", "free", "tree", "keep", "feet", "meet"],
    "ea": ["eat", "sea", "tea", "bead", "read", "team", "seat"],
    "ai": ["rain", "tail", "mail", "sail", "wait", "paid"],
    "ay": ["day", "say", "way", "play", "stay", "may", "pay"],
    "oa": ["boat", "coat", "goat", "road", "toad"],
    "ow": ["low", "row", "bow", "slow", "show", "know", "grow"],
    "oo": ["too", "zoo", "moon", "soon", "food", "room", "boot"],
    "ie": ["pie", "tie", "lie", "die"],
    "igh": ["high", "night", "light", "right", "fight", "might", "sight"],
}

# High-frequency sight words (allowed regardless of graphemes)
SIGHT_WORDS = {
    "a", "the", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did",
    "I", "you", "he", "she", "it", "we", "they",
    "my", "your", "his", "her", "its", "our", "their",
    "to", "for", "of", "on", "in", "at", "by", "with",
    "and", "or", "but", "so", "if", "then",
    "what", "when", "where", "who", "why", "how",
    "this", "that", "these", "those",
    "can", "will", "would", "could", "should",
    "not", "no", "yes",
    "said", "says",
}

# Simple sentence templates
SENTENCE_TEMPLATES = [
    "{subject} {verb} {object}.",
    "{subject} {verb}.",
    "The {noun} is {adjective}.",
    "{subject} can {verb} the {object}.",
    "{subject} has a {object}.",
    "{subject} and {subject2} {verb}.",
    "I see a {noun}.",
    "Look at the {noun}!",
    "The {noun} is on the {location}.",
]

# Story templates for generating coherent decodable stories
STORY_TEMPLATES = [
    # Pet stories
    {
        "theme": "pet_cat",
        "sentences": [
            "{name} has a cat.",
            "The cat is {adjective}.",
            "The cat can sit.",
            "{name} and the cat play.",
            "The cat likes to nap.",
            "{name} loves the cat.",
        ]
    },
    {
        "theme": "pet_dog",
        "sentences": [
            "{name} has a dog.",
            "The dog is {adjective}.",
            "The dog can run fast.",
            "The dog likes to dig.",
            "{name} and the dog play.",
            "The dog is fun!",
        ]
    },
    # Activity stories
    {
        "theme": "at_home",
        "sentences": [
            "{name} is at home.",
            "{name} sits on the {location}.",
            "{name} can see the {noun}.",
            "The {noun} is {adjective}.",
            "{name} likes to play.",
            "It is fun at home.",
        ]
    },
    {
        "theme": "playing",
        "sentences": [
            "{name} likes to play.",
            "{name} can run.",
            "Look at {name} go!",
            "{name} is {adjective}.",
            "{name} has fun.",
            "We like to play too!",
        ]
    },
    # Nature stories
    {
        "theme": "sunny_day",
        "sentences": [
            "The sun is up.",
            "It is a {adjective} day.",
            "{name} can go out.",
            "{name} sees a {noun}.",
            "The {noun} is {adjective}.",
            "What a fun day!",
        ]
    },
    {
        "theme": "in_the_park",
        "sentences": [
            "{name} is in the park.",
            "{name} can see a {noun}.",
            "The {noun} is {adjective}.",
            "{name} likes the park.",
            "{name} can run and play.",
            "The park is fun!",
        ]
    },
    # Simple action stories
    {
        "theme": "getting_ready",
        "sentences": [
            "{name} gets up.",
            "{name} can sit.",
            "{name} puts on a hat.",
            "{name} is ready.",
            "Time to go!",
            "{name} is happy.",
        ]
    },
    {
        "theme": "helping",
        "sentences": [
            "{name} likes to help.",
            "{name} can get the {noun}.",
            "Mom says thanks.",
            "{name} is a good helper.",
            "Helping is fun.",
            "{name} is happy.",
        ]
    },
]


@dataclass
class DecodableResult:
    """Result of decodable text generation."""

    text: str
    word_count: int
    sentence_count: int
    graphemes_used: List[str]


def generate_decodable(
    graphemes: List[str],
    length_sentences: int = 6,
    word_bank: Optional[List[str]] = None,
    include_sight_words: bool = True,
    theme: Optional[str] = None,
) -> DecodableResult:
    """
    Generate decodable text constrained to specific graphemes.

    Args:
        graphemes: List of taught graphemes (e.g., ['m', 's', 'a', 't'])
        length_sentences: Target number of sentences
        word_bank: Additional allowed words
        include_sight_words: Whether to include high-frequency sight words
        theme: Optional story theme for coherent generation

    Returns:
        DecodableResult with generated text
    """
    log_metric("decodable_request", graphemes=graphemes, length=length_sentences)

    # Build allowed word set
    allowed_words = set()

    for g in graphemes:
        if g in PHONICS_WORDS:
            allowed_words.update(PHONICS_WORDS[g])

    # Filter to words that only use the specified graphemes
    grapheme_set = set(graphemes)
    filtered_words = set()
    for word in allowed_words:
        if word_uses_only_graphemes(word.lower(), grapheme_set):
            filtered_words.add(word.lower())

    if word_bank:
        filtered_words.update(w.lower() for w in word_bank)

    if include_sight_words:
        filtered_words.update(w.lower() for w in SIGHT_WORDS)

    # Generate sentences
    words_list = list(filtered_words)

    if not words_list:
        # Fallback if no words available
        return DecodableResult(
            text="No words available for these graphemes.",
            word_count=0,
            sentence_count=0,
            graphemes_used=graphemes,
        )

    # Categorize words for story generation
    word_categories = categorize_words(filtered_words)
    
    # Try to generate a coherent story using templates
    if theme:
        sentences = generate_themed_story(theme, word_categories, length_sentences, filtered_words)
    else:
        # Pick a random theme that works with available words
        sentences = generate_best_story(word_categories, length_sentences, filtered_words)

    text = " ".join(sentences)
    word_count = len(text.split())

    log_metric(
        "decodable_result",
        sentence_count=len(sentences),
        word_count=word_count,
    )

    return DecodableResult(
        text=text,
        word_count=word_count,
        sentence_count=len(sentences),
        graphemes_used=graphemes,
    )


def categorize_words(words: Set[str]) -> Dict[str, List[str]]:
    """Categorize words for story generation."""
    categories = {
        "names": [],
        "nouns": [],
        "verbs": [],
        "adjectives": [],
        "locations": [],
    }
    
    # Known word categories
    name_words = {"sam", "tim", "kim", "pat", "mom", "dad", "tom", "dan", "max", "ben", "pam", "nan"}
    verb_words = {"sat", "sit", "run", "ran", "hit", "bit", "got", "get", "can", "has", "had", "put", 
                  "cut", "hop", "pop", "nap", "tap", "dip", "sip", "rub", "hug", "dig", "jog", "fit",
                  "win", "see", "eat", "play", "jump", "read", "make", "like", "look", "go", "come"}
    adjective_words = {"big", "hot", "fat", "sad", "mad", "bad", "red", "wet", "fun", "fit", "tan", 
                       "dim", "hip", "top", "fat", "thin", "soft", "good", "new", "old"}
    location_words = {"mat", "bed", "tub", "bus", "box", "cup", "pot", "pan", "bag", "rug", "hut",
                      "log", "top", "den", "pit"}
    
    for word in words:
        word_lower = word.lower()
        if word_lower in name_words:
            categories["names"].append(word.capitalize())
        elif word_lower in verb_words:
            categories["verbs"].append(word_lower)
        elif word_lower in adjective_words:
            categories["adjectives"].append(word_lower)
        elif word_lower in location_words:
            categories["locations"].append(word_lower)
        elif word_lower not in SIGHT_WORDS and len(word) > 2:
            categories["nouns"].append(word_lower)
    
    # Ensure we have at least some words in each category
    if not categories["names"]:
        categories["names"] = ["Sam", "I"]
    if not categories["verbs"]:
        categories["verbs"] = ["is", "can"]
    if not categories["adjectives"]:
        categories["adjectives"] = ["big", "fun"]
    if not categories["nouns"]:
        categories["nouns"] = list(words - SIGHT_WORDS)[:5] if words else ["cat"]
    if not categories["locations"]:
        categories["locations"] = ["mat", "box"]
    
    return categories


def generate_themed_story(theme: str, categories: Dict[str, List[str]], 
                          num_sentences: int, allowed_words: Set[str]) -> List[str]:
    """Generate a story using a specific theme template."""
    # Find matching template
    template = None
    for t in STORY_TEMPLATES:
        if t["theme"] == theme:
            template = t
            break
    
    if not template:
        # Fall back to random generation
        return generate_random_sentences(categories, num_sentences, allowed_words)
    
    sentences = []
    name = random.choice(categories["names"])
    
    for sent_template in template["sentences"][:num_sentences]:
        try:
            sentence = sent_template.format(
                name=name,
                noun=random.choice(categories["nouns"]) if categories["nouns"] else "cat",
                verb=random.choice(categories["verbs"]) if categories["verbs"] else "is",
                adjective=random.choice(categories["adjectives"]) if categories["adjectives"] else "big",
                location=random.choice(categories["locations"]) if categories["locations"] else "mat",
            )
            sentences.append(sentence)
        except (KeyError, IndexError):
            continue
    
    return sentences


def generate_best_story(categories: Dict[str, List[str]], 
                       num_sentences: int, allowed_words: Set[str]) -> List[str]:
    """Generate the best possible story from available words."""
    # Try each template and score based on word availability
    best_sentences = []
    
    for template in STORY_TEMPLATES:
        sentences = generate_themed_story(template["theme"], categories, num_sentences, allowed_words)
        if len(sentences) > len(best_sentences):
            best_sentences = sentences
    
    # If templates didn't work well, fall back to random generation
    if len(best_sentences) < num_sentences // 2:
        return generate_random_sentences(categories, num_sentences, allowed_words)
    
    return best_sentences


def generate_random_sentences(categories: Dict[str, List[str]], 
                             num_sentences: int, allowed_words: Set[str]) -> List[str]:
    """Generate random sentences from available words."""
    sentences = []
    
    for _ in range(num_sentences):
        sentence = generate_sentence(
            categories["names"],
            categories["verbs"],
            categories["nouns"],
            allowed_words,
        )
        if sentence:
            sentences.append(sentence)
    
    return sentences


def word_uses_only_graphemes(word: str, graphemes: Set[str]) -> bool:
    """Check if a word uses only the specified graphemes."""
    # Handle digraphs first
    digraphs = ["sh", "ch", "th", "wh", "ck", "ee", "ea", "ai", "ay", "oa", "ow", "oo", "ie", "igh"]

    remaining = word.lower()
    for digraph in digraphs:
        if digraph in remaining:
            if digraph not in graphemes:
                return False
            remaining = remaining.replace(digraph, "")

    # Check remaining single letters
    for char in remaining:
        if char not in graphemes and char.isalpha():
            return False

    return True


def generate_sentence(
    subjects: List[str],
    verbs: List[str],
    nouns: List[str],
    allowed_words: Set[str],
) -> str:
    """Generate a simple sentence from available words."""
    templates = [
        lambda: f"{random.choice(subjects)} {random.choice(verbs)}.",
        lambda: f"The {random.choice(nouns)} is {random.choice(['big', 'hot', 'fun', 'sad']) if any(w in allowed_words for w in ['big', 'hot', 'fun', 'sad']) else 'on the mat'}.",
        lambda: f"{random.choice(subjects)} {random.choice(verbs)} the {random.choice(nouns)}." if nouns else f"{random.choice(subjects)} {random.choice(verbs)}.",
        lambda: f"I see a {random.choice(nouns)}." if nouns else "I can see.",
    ]

    try:
        return random.choice(templates)()
    except (IndexError, ValueError):
        return f"{random.choice(subjects or ['I'])} {random.choice(verbs or ['is'])}."


def get_scope_sequence() -> Dict[str, List[str]]:
    """Get the phonics scope and sequence."""
    return {
        "unit_1": ["m", "s", "a", "t"],
        "unit_2": ["p", "n", "i"],
        "unit_3": ["c", "d", "o"],
        "unit_4": ["g", "b", "e"],
        "unit_5": ["h", "r", "u"],
        "unit_6": ["f", "l", "w"],
        "unit_7": ["j", "k", "x"],
        "unit_8": ["v", "y", "z"],
        "unit_9": ["sh", "ch", "th"],
        "unit_10": ["wh", "ck"],
        "unit_11": ["ee", "ea"],
        "unit_12": ["ai", "ay"],
        "unit_13": ["oa", "ow"],
        "unit_14": ["oo", "ie", "igh"],
    }
