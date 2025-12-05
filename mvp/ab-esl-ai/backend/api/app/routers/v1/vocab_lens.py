"""
Vocab Lens API Router

Provides object recognition and vocabulary enrichment for the AR camera feature.
Students point their camera at objects to get English labels, collocations,
sentence frames, and L1 translations.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Vocab Lens"])


# Common object vocabulary with collocations and sentence frames
OBJECT_VOCABULARY: Dict[str, Dict[str, Any]] = {
    "book": {
        "word": "book",
        "definition": "A set of printed pages bound together",
        "collocations": ["read a book", "open the book", "library book", "textbook", "picture book"],
        "sentence_frames": [
            "I am reading a ___.",
            "Can I borrow your ___?",
            "This ___ is about...",
        ],
        "category": "classroom",
        "frequency": "high",
    },
    "pencil": {
        "word": "pencil",
        "definition": "A tool for writing or drawing",
        "collocations": ["sharpen a pencil", "pencil case", "colored pencil", "write with a pencil"],
        "sentence_frames": [
            "I need a ___ to write.",
            "Can I borrow your ___?",
            "My ___ is broken.",
        ],
        "category": "classroom",
        "frequency": "high",
    },
    "desk": {
        "word": "desk",
        "definition": "A table for working or studying",
        "collocations": ["sit at the desk", "clean the desk", "front desk", "teacher's desk"],
        "sentence_frames": [
            "Please sit at your ___.",
            "Put your books on the ___.",
            "The ___ is made of wood.",
        ],
        "category": "classroom",
        "frequency": "high",
    },
    "chair": {
        "word": "chair",
        "definition": "A seat for one person",
        "collocations": ["sit on a chair", "push in the chair", "desk chair", "comfortable chair"],
        "sentence_frames": [
            "Please sit on your ___.",
            "Push in your ___ when you leave.",
            "This ___ is comfortable.",
        ],
        "category": "classroom",
        "frequency": "high",
    },
    "computer": {
        "word": "computer",
        "definition": "An electronic device for storing and processing information",
        "collocations": ["use the computer", "computer screen", "laptop computer", "turn on the computer"],
        "sentence_frames": [
            "I use the ___ for homework.",
            "The ___ is not working.",
            "Can I use the ___?",
        ],
        "category": "technology",
        "frequency": "high",
    },
    "backpack": {
        "word": "backpack",
        "definition": "A bag carried on the back",
        "collocations": ["carry a backpack", "school backpack", "put in the backpack", "heavy backpack"],
        "sentence_frames": [
            "My ___ is very heavy.",
            "I put my books in my ___.",
            "Where is my ___?",
        ],
        "category": "school",
        "frequency": "high",
    },
    "water_bottle": {
        "word": "water bottle",
        "definition": "A container for carrying water",
        "collocations": ["fill the water bottle", "drink from the bottle", "reusable bottle"],
        "sentence_frames": [
            "I need to fill my ___.",
            "Can I drink from my ___?",
            "My ___ is empty.",
        ],
        "category": "everyday",
        "frequency": "high",
    },
    "clock": {
        "word": "clock",
        "definition": "A device that shows the time",
        "collocations": ["tell time", "wall clock", "alarm clock", "the clock shows"],
        "sentence_frames": [
            "What time does the ___ show?",
            "Look at the ___.",
            "The ___ says it is noon.",
        ],
        "category": "classroom",
        "frequency": "high",
    },
    "whiteboard": {
        "word": "whiteboard",
        "definition": "A board for writing with markers",
        "collocations": ["write on the whiteboard", "erase the whiteboard", "whiteboard marker"],
        "sentence_frames": [
            "The teacher writes on the ___.",
            "Please look at the ___.",
            "Can you read what's on the ___?",
        ],
        "category": "classroom",
        "frequency": "high",
    },
    "window": {
        "word": "window",
        "definition": "An opening in a wall to let in light and air",
        "collocations": ["open the window", "close the window", "look out the window", "window seat"],
        "sentence_frames": [
            "Can you open the ___?",
            "I sit by the ___.",
            "Look out the ___.",
        ],
        "category": "building",
        "frequency": "high",
    },
    "door": {
        "word": "door",
        "definition": "An entrance to a room or building",
        "collocations": ["open the door", "close the door", "front door", "knock on the door"],
        "sentence_frames": [
            "Please close the ___.",
            "Someone is at the ___.",
            "The ___ is locked.",
        ],
        "category": "building",
        "frequency": "high",
    },
    "apple": {
        "word": "apple",
        "definition": "A round fruit that is red, green, or yellow",
        "collocations": ["eat an apple", "apple juice", "red apple", "apple tree"],
        "sentence_frames": [
            "I have an ___ for lunch.",
            "This ___ is very sweet.",
            "Would you like an ___?",
        ],
        "category": "food",
        "frequency": "high",
    },
    "lunch_box": {
        "word": "lunch box",
        "definition": "A container to carry food",
        "collocations": ["pack a lunch box", "open the lunch box", "bring a lunch box"],
        "sentence_frames": [
            "I packed my ___ this morning.",
            "What is in your ___?",
            "I forgot my ___.",
        ],
        "category": "school",
        "frequency": "high",
    },
    "scissors": {
        "word": "scissors",
        "definition": "A tool for cutting paper",
        "collocations": ["cut with scissors", "safety scissors", "sharp scissors"],
        "sentence_frames": [
            "Can I use the ___?",
            "Be careful with the ___.",
            "I need ___ for this project.",
        ],
        "category": "classroom",
        "frequency": "medium",
    },
    "eraser": {
        "word": "eraser",
        "definition": "A tool for removing pencil marks",
        "collocations": ["use an eraser", "pencil eraser", "big eraser"],
        "sentence_frames": [
            "I made a mistake. I need an ___.",
            "Can I borrow your ___?",
            "The ___ is on the desk.",
        ],
        "category": "classroom",
        "frequency": "high",
    },
}

# L1 translations for object vocabulary
L1_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "ar": {
        "book": "كتاب", "pencil": "قلم رصاص", "desk": "مكتب", "chair": "كرسي",
        "computer": "حاسوب", "backpack": "حقيبة ظهر", "water bottle": "زجاجة ماء",
        "clock": "ساعة", "whiteboard": "لوحة بيضاء", "window": "نافذة", "door": "باب",
        "apple": "تفاحة", "lunch box": "صندوق الغداء", "scissors": "مقص", "eraser": "ممحاة",
    },
    "es": {
        "book": "libro", "pencil": "lápiz", "desk": "escritorio", "chair": "silla",
        "computer": "computadora", "backpack": "mochila", "water bottle": "botella de agua",
        "clock": "reloj", "whiteboard": "pizarra blanca", "window": "ventana", "door": "puerta",
        "apple": "manzana", "lunch box": "lonchera", "scissors": "tijeras", "eraser": "borrador",
    },
    "zh": {
        "book": "书", "pencil": "铅笔", "desk": "书桌", "chair": "椅子",
        "computer": "电脑", "backpack": "背包", "water bottle": "水瓶",
        "clock": "时钟", "whiteboard": "白板", "window": "窗户", "door": "门",
        "apple": "苹果", "lunch box": "午餐盒", "scissors": "剪刀", "eraser": "橡皮擦",
    },
    "vi": {
        "book": "sách", "pencil": "bút chì", "desk": "bàn", "chair": "ghế",
        "computer": "máy tính", "backpack": "ba lô", "water bottle": "chai nước",
        "clock": "đồng hồ", "whiteboard": "bảng trắng", "window": "cửa sổ", "door": "cửa",
        "apple": "táo", "lunch box": "hộp cơm", "scissors": "kéo", "eraser": "tẩy",
    },
    "ko": {
        "book": "책", "pencil": "연필", "desk": "책상", "chair": "의자",
        "computer": "컴퓨터", "backpack": "배낭", "water bottle": "물병",
        "clock": "시계", "whiteboard": "화이트보드", "window": "창문", "door": "문",
        "apple": "사과", "lunch box": "도시락", "scissors": "가위", "eraser": "지우개",
    },
    "tl": {
        "book": "libro", "pencil": "lapis", "desk": "mesa", "chair": "upuan",
        "computer": "kompyuter", "backpack": "backpack", "water bottle": "bote ng tubig",
        "clock": "orasan", "whiteboard": "whiteboard", "window": "bintana", "door": "pinto",
        "apple": "mansanas", "lunch box": "lunch box", "scissors": "gunting", "eraser": "pambura",
    },
    "fr": {
        "book": "livre", "pencil": "crayon", "desk": "bureau", "chair": "chaise",
        "computer": "ordinateur", "backpack": "sac à dos", "water bottle": "bouteille d'eau",
        "clock": "horloge", "whiteboard": "tableau blanc", "window": "fenêtre", "door": "porte",
        "apple": "pomme", "lunch box": "boîte à lunch", "scissors": "ciseaux", "eraser": "gomme",
    },
    "hi": {
        "book": "किताब", "pencil": "पेंसिल", "desk": "मेज़", "chair": "कुर्सी",
        "computer": "कंप्यूटर", "backpack": "बस्ता", "water bottle": "पानी की बोतल",
        "clock": "घड़ी", "whiteboard": "व्हाइटबोर्ड", "window": "खिड़की", "door": "दरवाज़ा",
        "apple": "सेब", "lunch box": "लंच बॉक्स", "scissors": "कैंची", "eraser": "रबड़",
    },
    "pa": {
        "book": "ਕਿਤਾਬ", "pencil": "ਪੈਨਸਿਲ", "desk": "ਮੇਜ਼", "chair": "ਕੁਰਸੀ",
        "computer": "ਕੰਪਿਊਟਰ", "backpack": "ਬੈਗ", "water bottle": "ਪਾਣੀ ਦੀ ਬੋਤਲ",
        "clock": "ਘੜੀ", "whiteboard": "ਵ੍ਹਾਈਟਬੋਰਡ", "window": "ਖਿੜਕੀ", "door": "ਦਰਵਾਜ਼ਾ",
        "apple": "ਸੇਬ", "lunch box": "ਲੰਚ ਬਾਕਸ", "scissors": "ਕੈਂਚੀ", "eraser": "ਰਬੜ",
    },
    "ur": {
        "book": "کتاب", "pencil": "پنسل", "desk": "میز", "chair": "کرسی",
        "computer": "کمپیوٹر", "backpack": "بیگ", "water bottle": "پانی کی بوتل",
        "clock": "گھڑی", "whiteboard": "وائٹ بورڈ", "window": "کھڑکی", "door": "دروازہ",
        "apple": "سیب", "lunch box": "لنچ باکس", "scissors": "قینچی", "eraser": "ربڑ",
    },
    "so": {
        "book": "buug", "pencil": "qalin", "desk": "miis", "chair": "kursi",
        "computer": "kombuyuutar", "backpack": "shandad", "water bottle": "dhalada biyaha",
        "clock": "saacad", "whiteboard": "sabuurad cad", "window": "daaqad", "door": "albaab",
        "apple": "tufaax", "lunch box": "sanduuqa qadada", "scissors": "maqas", "eraser": "tirtire",
    },
}


class ObjectRecognitionRequest(BaseModel):
    """Request for object recognition from image."""
    image_base64: Optional[str] = Field(None, description="Base64-encoded image data")
    l1: str = Field(default="es", description="Student's L1 language code")


class VocabItem(BaseModel):
    """Vocabulary item with enrichment data."""
    word: str
    definition: str
    l1_translation: str
    collocations: List[str]
    sentence_frames: List[str]
    category: str
    frequency: str
    confidence: float = 1.0


class ObjectRecognitionResponse(BaseModel):
    """Response from object recognition."""
    detected_objects: List[VocabItem]
    image_id: Optional[str] = None
    timestamp: str


class SRSDeckItem(BaseModel):
    """Spaced repetition deck item."""
    word: str
    l1: str
    image_url: Optional[str] = None
    added_at: str
    next_review: str
    interval_days: int = 1
    ease_factor: float = 2.5
    repetitions: int = 0


class SaveToDeckRequest(BaseModel):
    """Request to save vocabulary to SRS deck."""
    participant_id: int
    word: str
    l1: str
    image_base64: Optional[str] = None


# In-memory SRS deck storage (in production, use database)
srs_decks: Dict[int, List[SRSDeckItem]] = {}


@router.post("/recognize", response_model=ObjectRecognitionResponse)
async def recognize_objects(request: ObjectRecognitionRequest):
    """
    Recognize objects in an image and return vocabulary enrichment.
    
    In production, this would use an on-device vision model (MobileNet, YOLO, etc.).
    For MVP, we simulate recognition with common classroom objects.
    """
    # Simulate object detection - in production, run image through vision model
    # For demo, return sample objects based on "detected" items
    simulated_detections = ["book", "pencil", "desk", "chair", "backpack"]
    
    detected_objects = []
    l1 = request.l1 if request.l1 in L1_TRANSLATIONS else "es"
    
    for obj_key in simulated_detections[:3]:  # Return top 3 detections
        if obj_key in OBJECT_VOCABULARY:
            obj_data = OBJECT_VOCABULARY[obj_key]
            l1_trans = L1_TRANSLATIONS.get(l1, {}).get(obj_data["word"], "")
            
            detected_objects.append(VocabItem(
                word=obj_data["word"],
                definition=obj_data["definition"],
                l1_translation=l1_trans,
                collocations=obj_data["collocations"],
                sentence_frames=obj_data["sentence_frames"],
                category=obj_data["category"],
                frequency=obj_data["frequency"],
                confidence=0.85 + (0.1 * (3 - len(detected_objects))),  # Simulated confidence
            ))
    
    return ObjectRecognitionResponse(
        detected_objects=detected_objects,
        image_id=f"img_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/vocabulary/{word}")
async def get_vocabulary_item(word: str, l1: str = "es") -> VocabItem:
    """Get vocabulary enrichment for a specific word."""
    word_key = word.lower().replace(" ", "_")
    
    if word_key not in OBJECT_VOCABULARY:
        # Try without underscore
        word_key = word.lower()
    
    if word_key not in OBJECT_VOCABULARY:
        raise HTTPException(status_code=404, detail=f"Vocabulary not found for '{word}'")
    
    obj_data = OBJECT_VOCABULARY[word_key]
    l1_trans = L1_TRANSLATIONS.get(l1, {}).get(obj_data["word"], "")
    
    return VocabItem(
        word=obj_data["word"],
        definition=obj_data["definition"],
        l1_translation=l1_trans,
        collocations=obj_data["collocations"],
        sentence_frames=obj_data["sentence_frames"],
        category=obj_data["category"],
        frequency=obj_data["frequency"],
    )


@router.get("/categories")
async def get_vocabulary_categories() -> Dict[str, List[str]]:
    """Get available vocabulary by category."""
    categories: Dict[str, List[str]] = {}
    
    for word_key, data in OBJECT_VOCABULARY.items():
        category = data["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(data["word"])
    
    return categories


@router.post("/deck/add")
async def add_to_deck(request: SaveToDeckRequest) -> SRSDeckItem:
    """Add a vocabulary item to the student's SRS deck."""
    participant_id = request.participant_id
    
    if participant_id not in srs_decks:
        srs_decks[participant_id] = []
    
    # Check if word already in deck
    for item in srs_decks[participant_id]:
        if item.word == request.word:
            raise HTTPException(status_code=400, detail="Word already in deck")
    
    now = datetime.utcnow()
    new_item = SRSDeckItem(
        word=request.word,
        l1=request.l1,
        image_url=None,  # In production, save uploaded image
        added_at=now.isoformat(),
        next_review=now.isoformat(),
        interval_days=1,
        ease_factor=2.5,
        repetitions=0,
    )
    
    srs_decks[participant_id].append(new_item)
    logger.info(f"Added '{request.word}' to deck for participant {participant_id}")
    
    return new_item


@router.get("/deck/{participant_id}")
async def get_deck(participant_id: int) -> List[SRSDeckItem]:
    """Get the student's vocabulary deck."""
    return srs_decks.get(participant_id, [])


@router.get("/deck/{participant_id}/review")
async def get_review_items(participant_id: int, limit: int = 10) -> List[SRSDeckItem]:
    """Get items due for review from the student's deck."""
    deck = srs_decks.get(participant_id, [])
    now = datetime.utcnow()
    
    due_items = [
        item for item in deck
        if datetime.fromisoformat(item.next_review) <= now
    ]
    
    return due_items[:limit]


class ReviewResultRequest(BaseModel):
    """Request to record review result."""
    participant_id: int
    word: str
    quality: int = Field(..., ge=0, le=5, description="Review quality 0-5 (0=forgot, 5=perfect)")


@router.post("/deck/review")
async def record_review(request: ReviewResultRequest) -> SRSDeckItem:
    """
    Record the result of a vocabulary review using SM-2 algorithm.
    
    Quality ratings:
    - 0: Complete blackout
    - 1: Incorrect, remembered on seeing answer
    - 2: Incorrect, answer seemed easy to recall
    - 3: Correct with serious difficulty
    - 4: Correct after hesitation
    - 5: Perfect response
    """
    deck = srs_decks.get(request.participant_id, [])
    
    item = None
    for i, deck_item in enumerate(deck):
        if deck_item.word == request.word:
            item = deck_item
            break
    
    if not item:
        raise HTTPException(status_code=404, detail="Word not found in deck")
    
    # SM-2 Algorithm
    quality = request.quality
    
    if quality < 3:
        # Reset on failure
        item.repetitions = 0
        item.interval_days = 1
    else:
        # Successful recall
        if item.repetitions == 0:
            item.interval_days = 1
        elif item.repetitions == 1:
            item.interval_days = 6
        else:
            item.interval_days = round(item.interval_days * item.ease_factor)
        
        item.repetitions += 1
    
    # Update ease factor
    item.ease_factor = max(1.3, item.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    
    # Calculate next review date
    from datetime import timedelta
    next_review = datetime.utcnow() + timedelta(days=item.interval_days)
    item.next_review = next_review.isoformat()
    
    logger.info(f"Reviewed '{request.word}' for participant {request.participant_id}: quality={quality}, next_review={item.next_review}")
    
    return item


@router.get("/topic-packs")
async def get_topic_packs() -> List[Dict[str, Any]]:
    """Get available vocabulary topic packs that teachers can push to students."""
    return [
        {
            "id": "classroom",
            "name": "Classroom Essentials",
            "description": "Common classroom objects and supplies",
            "word_count": 8,
            "words": ["book", "pencil", "desk", "chair", "whiteboard", "eraser", "scissors", "backpack"],
        },
        {
            "id": "food",
            "name": "Food & Lunch",
            "description": "Food items and lunchtime vocabulary",
            "word_count": 5,
            "words": ["apple", "lunch box", "water bottle"],
        },
        {
            "id": "building",
            "name": "Building & Rooms",
            "description": "Parts of buildings and rooms",
            "word_count": 3,
            "words": ["window", "door", "clock"],
        },
        {
            "id": "technology",
            "name": "Technology",
            "description": "Computers and electronic devices",
            "word_count": 1,
            "words": ["computer"],
        },
    ]
