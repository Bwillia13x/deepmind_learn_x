"""Rate limiting middleware using sliding window algorithm."""

import time
from collections import defaultdict
from typing import Dict, Tuple, Optional, Callable
from dataclasses import dataclass, field
from functools import wraps

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logging import logger


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10  # Max requests in 1 second
    
    # Endpoint-specific limits (path pattern -> (per_minute, per_hour))
    endpoint_limits: Dict[str, Tuple[int, int]] = field(default_factory=lambda: {
        "/v1/captions/": (30, 500),  # Lower limits for expensive ASR
        "/v1/authoring/": (20, 200),  # Lower limits for LLM calls
        "/auth/": (20, 200),  # Protect auth endpoints
    })


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter."""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        # Store: {client_key: [(timestamp, count), ...]}
        self._minute_windows: Dict[str, list] = defaultdict(list)
        self._hour_windows: Dict[str, list] = defaultdict(list)
        self._second_windows: Dict[str, list] = defaultdict(list)
        self._last_cleanup = time.time()
        self._cleanup_interval = 60  # Cleanup every minute
    
    def _get_client_key(self, request: Request) -> str:
        """Get unique client identifier."""
        # Use X-Forwarded-For if behind proxy, otherwise client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take first IP in chain (original client)
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Optionally include user ID if authenticated
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"{client_ip}:{user_id}"
        return client_ip
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove expired entries from windows."""
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        minute_cutoff = current_time - 60
        hour_cutoff = current_time - 3600
        second_cutoff = current_time - 1
        
        for key in list(self._minute_windows.keys()):
            self._minute_windows[key] = [
                (ts, c) for ts, c in self._minute_windows[key] if ts > minute_cutoff
            ]
            if not self._minute_windows[key]:
                del self._minute_windows[key]
        
        for key in list(self._hour_windows.keys()):
            self._hour_windows[key] = [
                (ts, c) for ts, c in self._hour_windows[key] if ts > hour_cutoff
            ]
            if not self._hour_windows[key]:
                del self._hour_windows[key]
        
        for key in list(self._second_windows.keys()):
            self._second_windows[key] = [
                (ts, c) for ts, c in self._second_windows[key] if ts > second_cutoff
            ]
            if not self._second_windows[key]:
                del self._second_windows[key]
        
        self._last_cleanup = current_time
    
    def _get_endpoint_limits(self, path: str) -> Tuple[int, int]:
        """Get rate limits for specific endpoint."""
        for pattern, limits in self.config.endpoint_limits.items():
            if path.startswith(pattern):
                return limits
        return (self.config.requests_per_minute, self.config.requests_per_hour)
    
    def _count_requests(self, entries: list, cutoff: float) -> int:
        """Count requests after cutoff time."""
        return sum(count for ts, count in entries if ts > cutoff)
    
    def check_rate_limit(self, request: Request) -> Tuple[bool, Dict[str, str]]:
        """
        Check if request is within rate limits.
        Returns (allowed, headers_dict).
        """
        current_time = time.time()
        self._cleanup_old_entries(current_time)
        
        client_key = self._get_client_key(request)
        path = request.url.path
        
        # Get limits for this endpoint
        limit_minute, limit_hour = self._get_endpoint_limits(path)
        
        # Check burst limit (per second)
        second_cutoff = current_time - 1
        second_count = self._count_requests(self._second_windows[client_key], second_cutoff)
        
        if second_count >= self.config.burst_size:
            return False, {
                "X-RateLimit-Limit": str(self.config.burst_size),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(current_time) + 1),
                "Retry-After": "1",
            }
        
        # Check minute limit
        minute_cutoff = current_time - 60
        minute_count = self._count_requests(self._minute_windows[client_key], minute_cutoff)
        
        if minute_count >= limit_minute:
            reset_time = int(current_time) + 60
            return False, {
                "X-RateLimit-Limit": str(limit_minute),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time),
                "Retry-After": str(60 - int(current_time - minute_cutoff)),
            }
        
        # Check hour limit
        hour_cutoff = current_time - 3600
        hour_count = self._count_requests(self._hour_windows[client_key], hour_cutoff)
        
        if hour_count >= limit_hour:
            reset_time = int(current_time) + 3600
            return False, {
                "X-RateLimit-Limit": str(limit_hour),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time),
                "Retry-After": str(3600 - int(current_time - hour_cutoff)),
            }
        
        # Request allowed - record it
        self._second_windows[client_key].append((current_time, 1))
        self._minute_windows[client_key].append((current_time, 1))
        self._hour_windows[client_key].append((current_time, 1))
        
        return True, {
            "X-RateLimit-Limit": str(limit_minute),
            "X-RateLimit-Remaining": str(limit_minute - minute_count - 1),
            "X-RateLimit-Reset": str(int(current_time) + 60),
        }


# Global rate limiter instance
rate_limiter = SlidingWindowRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""
    
    def __init__(self, app, limiter: Optional[SlidingWindowRateLimiter] = None):
        super().__init__(app)
        self.limiter = limiter or rate_limiter
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health checks and docs
        path = request.url.path
        if path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        allowed, headers = self.limiter.check_rate_limit(request)
        
        if not allowed:
            logger.warning(
                f"Rate limit exceeded for {request.client.host if request.client else 'unknown'} "
                f"on {path}"
            )
            response = Response(
                content='{"detail": "Rate limit exceeded. Please slow down."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
            )
            for key, value in headers.items():
                response.headers[key] = value
            return response
        
        response = await call_next(request)
        
        # Add rate limit headers to successful responses
        for key, value in headers.items():
            response.headers[key] = value
        
        return response


def rate_limit(requests_per_minute: int = 10):
    """Decorator for endpoint-specific rate limiting."""
    def decorator(func: Callable):
        # Store per-function rate limits
        func_limits: Dict[str, list] = defaultdict(list)
        
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            current_time = time.time()
            client_key = f"{request.client.host if request.client else 'unknown'}:{func.__name__}"
            
            # Clean old entries
            cutoff = current_time - 60
            func_limits[client_key] = [ts for ts in func_limits[client_key] if ts > cutoff]
            
            if len(func_limits[client_key]) >= requests_per_minute:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Max {requests_per_minute} requests per minute.",
                )
            
            func_limits[client_key].append(current_time)
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator
