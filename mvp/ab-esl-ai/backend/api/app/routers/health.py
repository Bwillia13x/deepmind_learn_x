"""Health check endpoint with detailed status information."""

import time
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import logger

router = APIRouter()

# Track service start time
_start_time = time.time()


class ServiceStatus(BaseModel):
    """Individual service status."""
    healthy: bool
    latency_ms: Optional[float] = None
    message: Optional[str] = None


class DetailedHealthResponse(BaseModel):
    """Detailed health response with service checks."""
    status: str  # "healthy", "degraded", "unhealthy"
    version: str = "0.1.0"
    environment: str
    uptime_seconds: float
    timestamp: str
    features: Dict[str, bool]
    services: Dict[str, ServiceStatus]


def check_database() -> ServiceStatus:
    """Check database connectivity."""
    try:
        from sqlalchemy import text
        from app.services.db import SessionLocal
        start = time.time()
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        latency = (time.time() - start) * 1000
        return ServiceStatus(healthy=True, latency_ms=round(latency, 2))
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return ServiceStatus(healthy=False, message=str(e)[:100])


def check_redis() -> ServiceStatus:
    """Check Redis connectivity."""
    try:
        import redis
        start = time.time()
        r = redis.from_url(settings.redis_url, socket_timeout=2)
        r.ping()
        latency = (time.time() - start) * 1000
        return ServiceStatus(healthy=True, latency_ms=round(latency, 2))
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        return ServiceStatus(healthy=False, message=str(e)[:100])


@router.get("/health", response_model=DetailedHealthResponse)
def health() -> DetailedHealthResponse:
    """Check service health with detailed status."""
    # Check individual services
    db_status = check_database()
    redis_status = check_redis()
    
    # Determine overall status
    all_healthy = db_status.healthy and redis_status.healthy
    any_critical_unhealthy = not db_status.healthy  # DB is critical
    
    if all_healthy:
        status = "healthy"
    elif any_critical_unhealthy:
        status = "unhealthy"
    else:
        status = "degraded"
    
    return DetailedHealthResponse(
        status=status,
        environment=settings.environment,
        uptime_seconds=round(time.time() - _start_time, 2),
        timestamp=datetime.utcnow().isoformat() + "Z",
        features={
            "enable_asr": settings.enable_asr,
            "enable_llm": settings.enable_llm,
            "l1_enabled": settings.l1_enabled_by_default,
        },
        services={
            "database": db_status,
            "redis": redis_status,
        },
    )


@router.get("/health/live")
def liveness() -> Dict[str, str]:
    """Kubernetes liveness probe - just check if service is running."""
    return {"status": "alive"}


@router.get("/health/ready")
def readiness() -> Dict[str, Any]:
    """Kubernetes readiness probe - check if service can handle requests."""
    db_status = check_database()
    
    if db_status.healthy:
        return {"status": "ready", "database": "connected"}
    else:
        # Return 503 for readiness failures
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not ready", "database": db_status.message}
        )
