"""Redis cache client with graceful fallback when Redis is unavailable."""

import json
import logging
from typing import Any, Optional

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to connect to Redis, but gracefully handle unavailability
_redis_available = False
try:
    redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    redis_client.ping()
    _redis_available = True
    logger.info("Redis connected successfully")
except Exception as e:
    redis_client = None
    logger.warning(f"Redis unavailable, caching disabled: {e}")


def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache. Returns None if Redis is unavailable."""
    if not _redis_available or redis_client is None:
        return None
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
    except redis.exceptions.ConnectionError:
        logger.debug(f"Redis connection error on get({key})")
    except Exception as e:
        logger.debug(f"Cache get error: {e}")
    return None


def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    """Set a value in cache with TTL in seconds. No-op if Redis is unavailable."""
    if not _redis_available or redis_client is None:
        return
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except redis.exceptions.ConnectionError:
        logger.debug(f"Redis connection error on set({key})")
    except Exception as e:
        logger.debug(f"Cache set error: {e}")


def cache_delete(key: str) -> None:
    """Delete a value from cache. No-op if Redis is unavailable."""
    if not _redis_available or redis_client is None:
        return
    try:
        redis_client.delete(key)
    except redis.exceptions.ConnectionError:
        logger.debug(f"Redis connection error on delete({key})")
    except Exception as e:
        logger.debug(f"Cache delete error: {e}")
