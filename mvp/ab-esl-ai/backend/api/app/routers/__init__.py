"""API routers.

This module assembles all API routers into a single router for inclusion in the FastAPI app.

Router Organization:
- System: Health checks
- Auth: Session management
- Core Features (v1): captions, reading, authoring, analytics, speaking
- Novel Features (v1): l1-transfer, curriculum, interventions, family, slife, cultural, foip

Note: Core feature routers don't define their own prefix, so we add /v1/* here.
      Novel feature routers define their own /v1/* prefix internally.
"""

from fastapi import APIRouter

from .health import router as health_router
from .auth import router as auth_router
from .v1.captions import router as captions_router
from .v1.reading import router as reading_router
from .v1.authoring import router as authoring_router
from .v1.analytics import router as analytics_router
from .v1.speaking import router as speaking_router
from .v1.writing import router as writing_router
from .v1.l1_transfer import router as l1_transfer_router
from .v1.curriculum import router as curriculum_router
from .v1.interventions import router as interventions_router
from .v1.family import router as family_router
from .v1.slife import router as slife_router
from .v1.cultural import router as cultural_router
from .v1.foip_analytics import router as foip_analytics_router
from .v1.vocab_lens import router as vocab_lens_router

api_router = APIRouter()

# System endpoints
api_router.include_router(health_router, tags=["system"])

# Authentication endpoints
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# Core Feature APIs (v1 namespace - prefix added here since routers don't define it)
api_router.include_router(captions_router, prefix="/v1/captions", tags=["captions"])
api_router.include_router(reading_router, prefix="/v1/reading", tags=["reading"])
api_router.include_router(authoring_router, prefix="/v1/authoring", tags=["authoring"])
api_router.include_router(analytics_router, prefix="/v1/analytics", tags=["analytics"])
api_router.include_router(speaking_router, prefix="/v1/speaking", tags=["speaking"])
api_router.include_router(writing_router, prefix="/v1/writing", tags=["writing"])

# Alberta-Specific Novel Features (v1 namespace - routers define their own /v1/* prefix)
api_router.include_router(l1_transfer_router, tags=["l1-transfer"])
api_router.include_router(curriculum_router, tags=["curriculum"])
api_router.include_router(interventions_router, tags=["interventions"])
api_router.include_router(family_router, tags=["family"])
api_router.include_router(slife_router, tags=["slife"])
api_router.include_router(cultural_router, tags=["cultural"])
api_router.include_router(foip_analytics_router, tags=["privacy"])
api_router.include_router(vocab_lens_router, prefix="/v1/vocab-lens", tags=["vocab-lens"])

__all__ = ["api_router"]
