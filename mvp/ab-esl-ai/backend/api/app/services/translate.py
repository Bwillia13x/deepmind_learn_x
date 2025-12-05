"""Translation and glossary service."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from app.core.logging import log_metric, logger
from app.core.nlp import get_nlp
from app.services.cache import cache_get, cache_set


@dataclass
class GlossEntry:
    """A glossary entry."""

    en: str
    l1: str
    definition: Optional[str] = None


@dataclass
class GlossResult:
    """Result of glossary/translation request."""

    translation: str
    gloss: List[GlossEntry]


# Built-in bilingual dictionaries (subset for MVP)
# In production, load from content/glossaries/*.json
DICTIONARIES: Dict[str, Dict[str, str]] = {
    "ar": {  # Arabic
        "book": "كتاب",
        "pen": "قلم",
        "paper": "ورقة",
        "teacher": "معلم",
        "student": "طالب",
        "class": "فصل",
        "school": "مدرسة",
        "read": "اقرأ",
        "write": "اكتب",
        "listen": "استمع",
        "open": "افتح",
        "close": "أغلق",
        "sit": "اجلس",
        "stand": "قف",
        "number": "رقم",
        "word": "كلمة",
        "sentence": "جملة",
        "page": "صفحة",
        "question": "سؤال",
        "answer": "جواب",
        "help": "مساعدة",
        "please": "من فضلك",
        "thank you": "شكرا",
        "yes": "نعم",
        "no": "لا",
        "good": "جيد",
        "great": "عظيم",
        "try": "حاول",
        "again": "مرة أخرى",
        "fraction": "كسر",
        "whole number": "عدد صحيح",
        "represents": "يمثل",
    },
    "uk": {  # Ukrainian
        "book": "книга",
        "pen": "ручка",
        "paper": "папір",
        "teacher": "вчитель",
        "student": "учень",
        "class": "клас",
        "school": "школа",
        "read": "читати",
        "write": "писати",
        "listen": "слухати",
        "open": "відкрити",
        "close": "закрити",
        "sit": "сидіти",
        "stand": "стояти",
        "number": "число",
        "word": "слово",
        "sentence": "речення",
        "page": "сторінка",
        "question": "питання",
        "answer": "відповідь",
    },
    "es": {  # Spanish
        "book": "libro",
        "pen": "bolígrafo",
        "paper": "papel",
        "teacher": "maestro",
        "student": "estudiante",
        "class": "clase",
        "school": "escuela",
        "read": "leer",
        "write": "escribir",
        "listen": "escuchar",
        "open": "abrir",
        "close": "cerrar",
        "sit": "sentarse",
        "stand": "pararse",
        "number": "número",
        "word": "palabra",
        "sentence": "oración",
        "page": "página",
        "question": "pregunta",
        "answer": "respuesta",
    },
    "zh": {  # Chinese (Simplified)
        "book": "书",
        "pen": "笔",
        "paper": "纸",
        "teacher": "老师",
        "student": "学生",
        "class": "班级",
        "school": "学校",
        "read": "读",
        "write": "写",
        "listen": "听",
        "open": "打开",
        "close": "关闭",
        "sit": "坐",
        "stand": "站",
        "number": "数字",
        "word": "词",
        "sentence": "句子",
        "page": "页",
        "question": "问题",
        "answer": "答案",
    },
    "tl": {  # Tagalog
        "book": "libro",
        "pen": "panulat",
        "paper": "papel",
        "teacher": "guro",
        "student": "estudyante",
        "class": "klase",
        "school": "paaralan",
        "read": "magbasa",
        "write": "magsulat",
        "listen": "makinig",
        "open": "buksan",
        "close": "isara",
    },
    "pa": {  # Punjabi
        "book": "ਕਿਤਾਬ",
        "pen": "ਕਲਮ",
        "paper": "ਕਾਗਜ਼",
        "teacher": "ਅਧਿਆਪਕ",
        "student": "ਵਿਦਿਆਰਥੀ",
        "school": "ਸਕੂਲ",
        "read": "ਪੜ੍ਹੋ",
        "write": "ਲਿਖੋ",
        "listen": "ਸੁਣੋ",
    },
}

# NGSL (New General Service List) - top frequent words (subset)
NGSL_TOP_1000 = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
    # ... abbreviated for MVP
}


def get_gloss(text: str, l1: str, top_k: int = 8) -> GlossResult:
    """
    Get translation and vocabulary glossary for text.

    Args:
        text: English text to translate/gloss
        l1: Target language code (e.g., 'ar', 'uk', 'es')
        top_k: Maximum number of glossary entries

    Returns:
        GlossResult with translation and glossary entries
    """
    # Check cache
    cache_key = f"gloss:{l1}:{hashlib.md5(text.encode()).hexdigest()}"
    cached = cache_get(cache_key)
    if cached:
        log_metric("gloss_cache_hit", l1=l1)
        return GlossResult(
            translation=cached["translation"],
            gloss=[GlossEntry(**g) for g in cached["gloss"]],
        )

    log_metric("gloss_request", l1=l1, text_length=len(text))

    # Get dictionary for language
    dictionaries = get_dictionaries()
    dictionary = dictionaries.get(l1, {})

    # Extract key words
    nlp = get_nlp()
    if nlp:
        doc = nlp(text.lower())
        words = []
        for token in doc:
            if token.pos_ in ["NOUN", "VERB", "ADJ"] and token.lemma_ not in NGSL_TOP_1000:
                words.append(token.lemma_)
            elif token.text in dictionary:
                words.append(token.text)
    else:
        # Fallback: simple word extraction
        words = [w.lower().strip(".,!?") for w in text.split()]

    # Build glossary
    gloss = []
    seen = set()
    for word in words:
        if word in seen:
            continue
        if word in dictionary:
            gloss.append(GlossEntry(en=word, l1=dictionary[word]))
            seen.add(word)
            if len(gloss) >= top_k:
                break

    # Generate translation (word-by-word for MVP, use NLLB in production)
    translation = translate_text(text, l1, dictionary)

    result = GlossResult(translation=translation, gloss=gloss)

    # Cache result
    cache_set(
        cache_key,
        {
            "translation": result.translation,
            "gloss": [{"en": g.en, "l1": g.l1, "definition": g.definition} for g in result.gloss],
        },
        ttl=3600,
    )

    return result


def translate_text(text: str, l1: str, dictionary: Optional[Dict[str, str]] = None) -> str:
    """
    Translate text to target language.
    For MVP, uses dictionary-based translation. Production would use NLLB.
    """
    if dictionary is None:
        dictionaries = get_dictionaries()
        dictionary = dictionaries.get(l1, {})

    if not dictionary:
        return f"[Translation to {l1} not available]"

    # Simple word-by-word translation
    words = text.split()
    translated = []
    for word in words:
        clean_word = word.lower().strip(".,!?")
        if clean_word in dictionary:
            # Preserve punctuation
            punct = ""
            if word[-1] in ".,!?":
                punct = word[-1]
            translated.append(dictionary[clean_word] + punct)
        else:
            translated.append(word)

    return " ".join(translated)


def load_dictionary(l1: str, path: Optional[Path] = None) -> Dict[str, str]:
    """Load a dictionary from JSON file."""
    if path is None:
        # Try multiple potential paths
        # From services/translate.py -> services -> app -> api -> backend -> ab-esl-ai (5 parents)
        base_paths = [
            Path(__file__).resolve().parent.parent.parent.parent.parent / "content" / "glossaries",
            Path("content/glossaries"),
        ]
        for base in base_paths:
            path = base / f"{l1}.json"
            if path.exists():
                break
        else:
            return {}

    if path.exists():
        try:
            with open(path) as f:
                data = json.load(f)
                # Handle both dict format and {entries: [...]} format
                if isinstance(data, dict) and "entries" in data:
                    result = {}
                    for entry in data["entries"]:
                        if "en" in entry and l1 in entry:
                            result[entry["en"].lower()] = entry[l1]
                    return result
                return data
        except Exception:
            return {}
    return {}


def load_all_dictionaries() -> Dict[str, Dict[str, str]]:
    """Load all available dictionaries from glossary files."""
    result = dict(DICTIONARIES)  # Start with built-in dictionaries
    
    # Find glossary directory
    # From services/translate.py -> services -> app -> api -> backend -> ab-esl-ai (5 parents)
    base_paths = [
        Path(__file__).resolve().parent.parent.parent.parent.parent / "content" / "glossaries",
        Path("content/glossaries"),
    ]
    
    for base in base_paths:
        if base.exists():
            for f in base.glob("*.json"):
                lang = f.stem
                if lang == "expanded_ar":
                    lang = "ar"  # Use expanded Arabic dict
                if lang not in result or lang == "ar":  # Override ar with expanded
                    loaded = load_dictionary(lang, f)
                    if loaded:
                        if lang in result:
                            result[lang].update(loaded)
                        else:
                            result[lang] = loaded
            break
    
    return result


# Load dictionaries on import
_loaded_dictionaries: Optional[Dict[str, Dict[str, str]]] = None


def get_dictionaries() -> Dict[str, Dict[str, str]]:
    """Get all dictionaries, loading from files if needed."""
    global _loaded_dictionaries
    if _loaded_dictionaries is None:
        _loaded_dictionaries = load_all_dictionaries()
        logger.info(f"Loaded dictionaries for {len(_loaded_dictionaries)} languages")
    return _loaded_dictionaries
