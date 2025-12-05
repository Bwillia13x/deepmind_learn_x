"""V1 API namespace.

This package contains all v1 API routers organized by feature:

Core Features:
- captions: Real-time ASR, text simplification, and translation
- reading: Reading fluency scoring and decodable text generation
- authoring: Text leveling and content adaptation
- analytics: Student progress tracking and class insights
- speaking: Pronunciation practice and feedback

Alberta-Specific Features:
- l1_transfer: L1 linguistic transfer intelligence
- curriculum: Alberta curriculum alignment
- interventions: Predictive intervention engine
- family: Family literacy co-pilot
- slife: SLIFE content and pathways
- cultural: Cultural responsiveness support
- foip_analytics: FOIP-compliant analytics
"""

from .captions import router as captions_router
from .reading import router as reading_router
from .authoring import router as authoring_router
from .analytics import router as analytics_router
from .speaking import router as speaking_router
from .l1_transfer import router as l1_transfer_router
from .curriculum import router as curriculum_router
from .interventions import router as interventions_router
from .family import router as family_router
from .slife import router as slife_router
from .cultural import router as cultural_router
from .foip_analytics import router as foip_analytics_router

__all__ = [
    "captions_router",
    "reading_router",
    "authoring_router",
    "analytics_router",
    "speaking_router",
    "l1_transfer_router",
    "curriculum_router",
    "interventions_router",
    "family_router",
    "slife_router",
    "cultural_router",
    "foip_analytics_router",
]
