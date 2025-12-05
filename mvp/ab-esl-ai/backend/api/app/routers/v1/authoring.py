"""Teacher Copilot API endpoints - text leveling, questions, glossaries."""

import time
from typing import List, Optional

from fastapi import APIRouter

from app.core.logging import log_metric
from app.schemas.common import (
    GlossEntry,
    LeveledText,
    LevelTextRequest,
    LevelTextResponse,
    Question,
    ReadabilityScore,
)
from app.services.leveling import level_text

router = APIRouter()


@router.post("/level-text", response_model=LevelTextResponse)
def level_text_endpoint(request: LevelTextRequest) -> LevelTextResponse:
    """
    Level text to multiple readability targets.

    Generates simplified versions, comprehension questions, and bilingual glossaries.

    Targets can be CEFR levels (A1, A2, B1, B2) or grade levels (Gr3, Gr5, etc.)
    """
    start_time = time.time()

    result = level_text(
        text=request.text,
        targets=request.targets,
        l1=request.l1,
    )

    latency = time.time() - start_time
    log_metric(
        "level_text_endpoint",
        latency=latency,
        targets=request.targets,
        level_count=len(result.levels),
    )

    return LevelTextResponse(
        original_score=ReadabilityScore(
            cefr=result.original_score.cefr,
            avg_sentence_length=result.original_score.avg_sentence_length,
            difficult_word_pct=result.original_score.difficult_word_pct,
        ),
        levels=[
            LeveledText(
                target=level.target,
                text=level.text,
                questions=[
                    Question(type=q.type, q=q.q, a=q.a)
                    for q in level.questions
                ],
                gloss=[
                    GlossEntry(en=g.en, l1=g.l1, definition=g.definition)
                    for g in level.gloss
                ],
            )
            for level in result.levels
        ],
    )
