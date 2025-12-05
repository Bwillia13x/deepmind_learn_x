"""
Family Literacy Co-Pilot Service

Bridges the home-school literacy gap by providing:
- Bilingual homework helpers with L1 translations
- Simple micro-lessons families can do together
- Progress updates in parent's preferred language
- Family-friendly vocabulary practice activities

Critical for Alberta's ESL population where parent engagement
is often limited by language barriers.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path
from functools import lru_cache

logger = logging.getLogger(__name__)


# Supported parent languages (matching existing glossaries)
SUPPORTED_LANGUAGES = {
    "ar": {"name": "Arabic", "native": "العربية", "rtl": True},
    "es": {"name": "Spanish", "native": "Español", "rtl": False},
    "zh": {"name": "Chinese (Simplified)", "native": "中文", "rtl": False},
    "ko": {"name": "Korean", "native": "한국어", "rtl": False},
    "tl": {"name": "Tagalog", "native": "Tagalog", "rtl": False},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ", "rtl": False},
    "uk": {"name": "Ukrainian", "native": "Українська", "rtl": False},
    "so": {"name": "Somali", "native": "Soomaali", "rtl": False},
    "vi": {"name": "Vietnamese", "native": "Tiếng Việt", "rtl": False},
    "fa": {"name": "Farsi", "native": "فارسی", "rtl": True},
    "hi": {"name": "Hindi", "native": "हिन्दी", "rtl": False},
    "ur": {"name": "Urdu", "native": "اردو", "rtl": True},
    "fr": {"name": "French", "native": "Français", "rtl": False},
}


# Family micro-lesson templates
MICRO_LESSONS = {
    "label_the_home": {
        "id": "label_the_home",
        "title": "Label the Home",
        "title_translations": {
            "ar": "تسمية أشياء المنزل",
            "es": "Etiqueta la Casa",
            "zh": "家庭标签",
            "so": "Magacaabi Guriga"
        },
        "duration_minutes": 10,
        "materials": ["sticky_notes", "pen"],
        "grade_range": ["K", "1", "2"],
        "skills": ["vocabulary", "phonics", "reading"],
        "instructions": [
            "Choose 5 items in your home (door, table, chair, window, bed)",
            "Write the English word on a sticky note",
            "Put the sticky note on the item",
            "Have your child read each label every day",
            "Add new labels each week"
        ],
        "instructions_translations": {
            "ar": [
                "اختر 5 أشياء في منزلك (باب، طاولة، كرسي، نافذة، سرير)",
                "اكتب الكلمة الإنجليزية على ورقة لاصقة",
                "ضع الورقة اللاصقة على الشيء",
                "اطلب من طفلك قراءة كل تسمية كل يوم",
                "أضف تسميات جديدة كل أسبوع"
            ],
            "es": [
                "Elige 5 objetos en tu casa (puerta, mesa, silla, ventana, cama)",
                "Escribe la palabra en inglés en una nota adhesiva",
                "Pon la nota adhesiva en el objeto",
                "Pide a tu hijo que lea cada etiqueta todos los días",
                "Agrega nuevas etiquetas cada semana"
            ]
        },
        "why_it_helps": "Connects English words to real objects, building vocabulary naturally"
    },
    "read_together": {
        "id": "read_together",
        "title": "Read Together Daily",
        "title_translations": {
            "ar": "القراءة معاً يومياً",
            "es": "Leer Juntos Diariamente",
            "zh": "每日一起阅读",
            "so": "Akhris Wadajir Maalin Kasta"
        },
        "duration_minutes": 15,
        "materials": ["any_book"],
        "grade_range": ["K", "1", "2", "3", "4", "5", "6"],
        "skills": ["fluency", "comprehension", "vocabulary"],
        "instructions": [
            "Find a quiet time each day (same time helps!)",
            "Let your child choose the book",
            "You can read in your language first, then English",
            "Point to pictures and words as you read",
            "Ask: What happened? Who was in the story?"
        ],
        "why_it_helps": "Daily reading builds fluency and love of reading"
    },
    "sound_hunt": {
        "id": "sound_hunt",
        "title": "Sound Hunt",
        "title_translations": {
            "ar": "البحث عن الأصوات",
            "es": "Búsqueda de Sonidos",
            "zh": "声音寻宝",
            "so": "Raadinta Codka"
        },
        "duration_minutes": 10,
        "materials": ["none"],
        "grade_range": ["K", "1", "2"],
        "skills": ["phonological_awareness", "phonics"],
        "instructions": [
            "Choose a sound (like /b/ or /s/)",
            "Walk around the house or outside",
            "Find things that start with that sound",
            "Say the word together: 'Ball starts with /b/!'",
            "Try to find 5 things for each sound"
        ],
        "why_it_helps": "Helps children hear sounds in words - important for reading"
    },
    "word_of_the_day": {
        "id": "word_of_the_day",
        "title": "Word of the Day",
        "title_translations": {
            "ar": "كلمة اليوم",
            "es": "Palabra del Día",
            "zh": "每日一词",
            "so": "Erayga Maalinta"
        },
        "duration_minutes": 5,
        "materials": ["none"],
        "grade_range": ["K", "1", "2", "3", "4", "5", "6"],
        "skills": ["vocabulary"],
        "instructions": [
            "Choose one new English word each day",
            "Say the word in English and your home language",
            "Use the word in a sentence",
            "Try to use it 5 times during the day",
            "Write it down at the end of the day"
        ],
        "why_it_helps": "Learning words in both languages helps understanding"
    },
    "story_retell": {
        "id": "story_retell",
        "title": "Tell Me the Story",
        "title_translations": {
            "ar": "أخبرني القصة",
            "es": "Cuéntame la Historia",
            "zh": "给我讲故事",
            "so": "Ii Sheeg Sheekooyinka"
        },
        "duration_minutes": 10,
        "materials": ["book_just_read"],
        "grade_range": ["1", "2", "3", "4", "5", "6"],
        "skills": ["comprehension", "speaking"],
        "instructions": [
            "After reading a story, close the book",
            "Ask your child to tell you what happened",
            "Ask: Who? What? Where? When?",
            "They can use your home language if needed",
            "Help them with English words they don't know"
        ],
        "why_it_helps": "Retelling shows understanding and builds language skills"
    },
    "cooking_words": {
        "id": "cooking_words",
        "title": "Cooking Words",
        "title_translations": {
            "ar": "كلمات الطبخ",
            "es": "Palabras de Cocina",
            "zh": "烹饪词汇",
            "so": "Ereyada Karinta"
        },
        "duration_minutes": 15,
        "materials": ["cooking_time"],
        "grade_range": ["K", "1", "2", "3", "4"],
        "skills": ["vocabulary", "following_directions"],
        "instructions": [
            "Cook together with your child",
            "Name ingredients in English: egg, flour, water...",
            "Use action words: stir, mix, pour, cut...",
            "Count together: 'Add 2 eggs'",
            "Talk about what you see and smell"
        ],
        "why_it_helps": "Real activities help children remember new words"
    }
}


# Progress update message templates
PROGRESS_TEMPLATES = {
    "weekly_summary": {
        "en": "This week, {child_name} practiced reading for {minutes} minutes. They learned {words} new words!",
        "ar": "هذا الأسبوع، تدرب {child_name} على القراءة لمدة {minutes} دقيقة. تعلموا {words} كلمات جديدة!",
        "es": "Esta semana, {child_name} practicó lectura por {minutes} minutos. ¡Aprendió {words} palabras nuevas!",
        "zh": "本周，{child_name} 练习阅读了 {minutes} 分钟。他们学会了 {words} 个新单词！",
        "so": "Todobaadkan, {child_name} waxay ku tababartay akhriska {minutes} daqiiqo. Waxay baratay {words} eray cusub!"
    },
    "fluency_update": {
        "en": "{child_name} can now read {wcpm} words per minute. The goal for their grade is {target}.",
        "ar": "{child_name} يمكنه الآن قراءة {wcpm} كلمة في الدقيقة. الهدف لصفهم هو {target}.",
        "es": "{child_name} ahora puede leer {wcpm} palabras por minuto. La meta para su grado es {target}.",
        "zh": "{child_name} 现在每分钟能读 {wcpm} 个单词。他们年级的目标是 {target}。",
        "so": "{child_name} hadda wuxuu akhriyi karaa {wcpm} erey daqiiqad. Hadafka fasalkooda waa {target}."
    },
    "encouragement": {
        "en": "Great job! Keep practicing at home. Every minute of reading helps!",
        "ar": "عمل رائع! استمر في التدرب في المنزل. كل دقيقة من القراءة تساعد!",
        "es": "¡Excelente trabajo! Sigue practicando en casa. ¡Cada minuto de lectura ayuda!",
        "zh": "做得好！继续在家练习。每分钟的阅读都有帮助！",
        "so": "Shaqo wanaagsan! Sii wad tababarka guriga. Daqiiqad kasta oo akhris ah waa caawiso!"
    },
    "homework_help": {
        "en": "Tonight's homework: {homework}. Here's how to help: {help_tips}",
        "ar": "واجب الليلة: {homework}. إليك كيفية المساعدة: {help_tips}",
        "es": "Tarea de esta noche: {homework}. Cómo ayudar: {help_tips}",
        "zh": "今晚的作业：{homework}。帮助方法：{help_tips}",
        "so": "Shaqada habeenkii: {homework}. Halkan waa sida loo caawiyo: {help_tips}"
    }
}


# Homework help templates by skill area
HOMEWORK_HELP_TEMPLATES = {
    "sight_words": {
        "task": "Practice reading sight words",
        "help_tips": {
            "en": [
                "Show the word, say it together",
                "Find the word in a book",
                "Write the word 3 times",
                "Use the word in a sentence"
            ],
            "ar": [
                "أظهر الكلمة، قلها معاً",
                "ابحث عن الكلمة في كتاب",
                "اكتب الكلمة 3 مرات",
                "استخدم الكلمة في جملة"
            ],
            "es": [
                "Muestra la palabra, dila juntos",
                "Busca la palabra en un libro",
                "Escribe la palabra 3 veces",
                "Usa la palabra en una oración"
            ]
        }
    },
    "reading_fluency": {
        "task": "Read aloud for 15 minutes",
        "help_tips": {
            "en": [
                "Find a quiet place",
                "Let your child choose the book",
                "Listen as they read",
                "Help with difficult words",
                "Praise their effort!"
            ]
        }
    },
    "spelling": {
        "task": "Practice spelling words",
        "help_tips": {
            "en": [
                "Say the word",
                "Have your child spell it out loud",
                "Write it down",
                "Check together",
                "Practice the hard ones again"
            ]
        }
    }
}


def get_supported_languages() -> Dict[str, Any]:
    """Get list of supported parent languages."""
    return SUPPORTED_LANGUAGES


def get_micro_lessons(
    grade: Optional[str] = None,
    skill: Optional[str] = None,
    language: str = "en"
) -> List[Dict[str, Any]]:
    """
    Get family micro-lessons, optionally filtered by grade or skill.
    
    Args:
        grade: Optional grade level filter
        skill: Optional skill filter (vocabulary, phonics, etc.)
        language: Language code for translations
        
    Returns:
        List of micro-lessons with translations if available
    """
    lessons = []
    
    for lesson_id, lesson in MICRO_LESSONS.items():
        # Filter by grade if specified
        if grade and grade not in lesson.get("grade_range", []):
            continue
        
        # Filter by skill if specified
        if skill and skill.lower() not in [s.lower() for s in lesson.get("skills", [])]:
            continue
        
        # Add translations if available
        lesson_copy = lesson.copy()
        
        if language != "en" and language in lesson.get("title_translations", {}):
            lesson_copy["title_translated"] = lesson["title_translations"][language]
        
        if language != "en" and language in lesson.get("instructions_translations", {}):
            lesson_copy["instructions_translated"] = lesson["instructions_translations"][language]
        
        lessons.append(lesson_copy)
    
    return lessons


def get_micro_lesson(lesson_id: str, language: str = "en") -> Optional[Dict[str, Any]]:
    """Get a specific micro-lesson by ID."""
    lesson = MICRO_LESSONS.get(lesson_id)
    if not lesson:
        return None
    
    lesson_copy = lesson.copy()
    
    if language != "en":
        if language in lesson.get("title_translations", {}):
            lesson_copy["title_translated"] = lesson["title_translations"][language]
        if language in lesson.get("instructions_translations", {}):
            lesson_copy["instructions_translated"] = lesson["instructions_translations"][language]
    
    return lesson_copy


def generate_progress_message(
    message_type: str,
    language: str,
    **kwargs
) -> str:
    """
    Generate a progress message in the parent's language.
    
    Args:
        message_type: Type of message (weekly_summary, fluency_update, etc.)
        language: Target language code
        **kwargs: Variables to fill in the template
        
    Returns:
        Translated message with variables filled in
    """
    templates = PROGRESS_TEMPLATES.get(message_type, {})
    template = templates.get(language, templates.get("en", ""))
    
    try:
        return template.format(**kwargs)
    except KeyError as e:
        logger.warning(f"Missing variable in progress message: {e}")
        return template


def generate_homework_helper(
    skill_area: str,
    language: str,
    specific_words: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate homework help instructions for parents.
    
    Args:
        skill_area: Area of focus (sight_words, reading_fluency, spelling)
        language: Parent's language
        specific_words: Optional list of specific words to practice
        
    Returns:
        Homework helper with instructions in parent's language
    """
    template = HOMEWORK_HELP_TEMPLATES.get(skill_area, {})
    
    if not template:
        return {
            "task": skill_area.replace("_", " ").title(),
            "help_tips": ["Support your child with their homework"],
            "language": language
        }
    
    tips = template.get("help_tips", {})
    localized_tips = tips.get(language, tips.get("en", []))
    
    result = {
        "task": template.get("task", skill_area),
        "help_tips": localized_tips,
        "language": language
    }
    
    if specific_words:
        result["words_to_practice"] = specific_words
    
    return result


def generate_weekly_family_plan(
    student_name: str,
    grade: str,
    focus_skills: List[str],
    language: str
) -> Dict[str, Any]:
    """
    Generate a weekly family literacy plan.
    
    Args:
        student_name: Child's name
        grade: Current grade level
        focus_skills: Skills to focus on this week
        language: Parent's language
        
    Returns:
        Week-long plan with daily activities
    """
    # Get relevant lessons
    relevant_lessons = []
    for skill in focus_skills:
        lessons = get_micro_lessons(grade=grade, skill=skill, language=language)
        relevant_lessons.extend(lessons)
    
    # Remove duplicates
    seen_ids = set()
    unique_lessons = []
    for lesson in relevant_lessons:
        if lesson["id"] not in seen_ids:
            seen_ids.add(lesson["id"])
            unique_lessons.append(lesson)
    
    # Create daily plan (cycle through lessons)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    daily_activities = []
    
    for i, day in enumerate(days):
        if unique_lessons:
            lesson = unique_lessons[i % len(unique_lessons)]
            daily_activities.append({
                "day": day,
                "activity": lesson.get("title_translated", lesson["title"]),
                "duration_minutes": lesson["duration_minutes"],
                "lesson_id": lesson["id"]
            })
        else:
            daily_activities.append({
                "day": day,
                "activity": "Read Together Daily",
                "duration_minutes": 15,
                "lesson_id": "read_together"
            })
    
    lang_info = SUPPORTED_LANGUAGES.get(language, {"name": "English", "native": "English"})
    
    return {
        "student_name": student_name,
        "grade": grade,
        "week_focus": focus_skills,
        "language": {
            "code": language,
            "name": lang_info["name"],
            "native_name": lang_info["native"]
        },
        "daily_plan": daily_activities,
        "total_weekly_minutes": sum(a["duration_minutes"] for a in daily_activities),
        "tips": [
            "Same time each day works best",
            "Make it fun - learning should be enjoyable!",
            "Praise effort, not just results",
            "It's okay to use your home language too"
        ]
    }


def generate_vocabulary_practice(
    words: List[str],
    language: str,
    glossary_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate vocabulary practice activities for families.
    
    Args:
        words: English words to practice
        language: Parent's language
        glossary_data: Optional glossary data for translations
        
    Returns:
        Vocabulary practice activities with translations
    """
    word_activities = []
    
    for word in words:
        activity = {
            "english_word": word,
            "activities": [
                f"Say '{word}' together 3 times",
                f"Find something that shows '{word}'",
                f"Use '{word}' in a sentence",
                f"Draw a picture of '{word}'"
            ]
        }
        
        # Add translation if glossary data available
        if glossary_data and word.lower() in glossary_data:
            activity["translation"] = glossary_data[word.lower()]
        
        word_activities.append(activity)
    
    return {
        "language": language,
        "words": word_activities,
        "instructions": {
            "en": "Practice these words with your child each day",
            "ar": "تدرب على هذه الكلمات مع طفلك كل يوم",
            "es": "Practica estas palabras con tu hijo cada día",
            "zh": "每天与孩子练习这些单词"
        }.get(language, "Practice these words with your child each day")
    }


def generate_sms_message(
    message_type: str,
    language: str,
    **kwargs
) -> str:
    """
    Generate a short SMS-friendly message for parents.
    Max 160 characters for SMS compatibility.
    
    Args:
        message_type: Type of message
        language: Target language
        **kwargs: Message variables
        
    Returns:
        Short message suitable for SMS
    """
    sms_templates = {
        "practice_reminder": {
            "en": "Hi! Time to read with {child_name} today! Even 10 min helps. 📚",
            "ar": "مرحباً! حان وقت القراءة مع {child_name} اليوم! حتى 10 دقائق تساعد. 📚",
            "es": "¡Hola! ¡Hora de leer con {child_name} hoy! Incluso 10 min ayudan. 📚"
        },
        "achievement": {
            "en": "Great news! {child_name} reached their reading goal this week! Keep it up! 🌟",
            "ar": "أخبار رائعة! {child_name} وصل لهدفه في القراءة هذا الأسبوع! استمروا! 🌟",
            "es": "¡Buenas noticias! {child_name} alcanzó su meta de lectura! ¡Sigan así! 🌟"
        },
        "weekly_words": {
            "en": "This week's words: {words}. Practice together! 💪",
            "ar": "كلمات هذا الأسبوع: {words}. تدربوا معاً! 💪",
            "es": "Palabras de la semana: {words}. ¡Practiquen juntos! 💪"
        }
    }
    
    templates = sms_templates.get(message_type, {})
    template = templates.get(language, templates.get("en", ""))
    
    try:
        message = template.format(**kwargs)
        # Truncate if too long
        if len(message) > 160:
            message = message[:157] + "..."
        return message
    except KeyError:
        return template


def get_family_resources(language: str) -> Dict[str, Any]:
    """
    Get family literacy resources and tips in the parent's language.
    
    Returns:
        Collection of resources for family literacy
    """
    return {
        "language": language,
        "resources": {
            "reading_tips": [
                {
                    "tip": "Read every day, even for just 10 minutes",
                    "tip_translated": {
                        "ar": "اقرأ كل يوم، حتى لو 10 دقائق فقط",
                        "es": "Lee todos los días, aunque sean solo 10 minutos",
                        "zh": "每天阅读，即使只有10分钟"
                    }.get(language)
                },
                {
                    "tip": "It's okay to read in your home language too",
                    "tip_translated": {
                        "ar": "لا بأس بالقراءة بلغتك الأم أيضاً",
                        "es": "Está bien leer en tu idioma también",
                        "zh": "用你的母语阅读也可以"
                    }.get(language)
                },
                {
                    "tip": "Talk about what you read - ask questions",
                    "tip_translated": {
                        "ar": "تحدث عما تقرأه - اطرح أسئلة",
                        "es": "Habla sobre lo que lees - haz preguntas",
                        "zh": "讨论你读的内容 - 提问"
                    }.get(language)
                }
            ],
            "library_info": {
                "note": "Your local library has free books and programs!",
                "note_translated": {
                    "ar": "مكتبتك المحلية لديها كتب وبرامج مجانية!",
                    "es": "¡Tu biblioteca local tiene libros y programas gratis!",
                    "zh": "你当地的图书馆有免费的书籍和项目！"
                }.get(language)
            }
        }
    }
