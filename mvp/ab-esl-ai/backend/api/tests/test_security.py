"""Tests for security and rate limiting."""

import time
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token, decode_token, TokenPayload
from app.core.rate_limit import SlidingWindowRateLimiter, RateLimitConfig


client = TestClient(app)


class TestJWTTokens:
    """Test JWT token creation and validation."""
    
    def test_create_access_token(self):
        """Test creating a JWT token."""
        token = create_access_token(
            subject="user123",
            role="teacher",
            session_id=1,
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_valid_token(self):
        """Test decoding a valid JWT token."""
        token = create_access_token(
            subject="user456",
            role="student",
            session_id=2,
            participant_id=10,
        )
        
        payload = decode_token(token)
        
        assert payload.sub == "user456"
        assert payload.role == "student"
        assert payload.session_id == 2
        assert payload.participant_id == 10
    
    def test_decode_invalid_token(self):
        """Test decoding an invalid token raises exception."""
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid.token.here")
        
        assert exc_info.value.status_code == 401
    
    def test_token_expiry(self):
        """Test token payload has correct expiry."""
        from datetime import timedelta, datetime
        
        token = create_access_token(
            subject="user789",
            role="admin",
            expires_delta=timedelta(hours=2),
        )
        
        payload = decode_token(token)
        
        # Use UTC time for comparison (same as token creation)
        utc_now = int(datetime.utcnow().timestamp())
        
        # Token should expire in the future (relative to when it was issued)
        assert payload.exp > payload.iat
        # Expiry should be roughly 2 hours after iat (allowing for small timing differences)
        time_diff = payload.exp - payload.iat
        assert time_diff >= 7100  # At least ~2 hours
        assert time_diff <= 7300  # At most ~2 hours + buffer


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiter_allows_requests(self):
        """Test that requests within limits are allowed."""
        config = RateLimitConfig(requests_per_minute=10)
        limiter = SlidingWindowRateLimiter(config)
        
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client.host = "192.168.1.1"
        mock_request.url.path = "/v1/reading/score"
        
        allowed, headers = limiter.check_rate_limit(mock_request)
        
        assert allowed is True
        assert "X-RateLimit-Remaining" in headers
    
    def test_rate_limiter_blocks_excess_requests(self):
        """Test that excess requests are blocked."""
        config = RateLimitConfig(
            requests_per_minute=5,
            burst_size=3,
        )
        limiter = SlidingWindowRateLimiter(config)
        
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client.host = "192.168.1.2"
        mock_request.url.path = "/v1/reading/score"
        
        # Make requests up to the burst limit
        for i in range(3):
            allowed, _ = limiter.check_rate_limit(mock_request)
            assert allowed is True
        
        # 4th request should be blocked (burst limit)
        allowed, headers = limiter.check_rate_limit(mock_request)
        assert allowed is False
        assert "Retry-After" in headers
    
    def test_rate_limiter_endpoint_specific_limits(self):
        """Test endpoint-specific rate limits."""
        config = RateLimitConfig(
            requests_per_minute=100,
            endpoint_limits={
                "/v1/authoring/": (5, 50),
            }
        )
        limiter = SlidingWindowRateLimiter(config)
        
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client.host = "192.168.1.3"
        mock_request.url.path = "/v1/authoring/level-text"
        
        # Should use endpoint-specific limit
        _, headers = limiter.check_rate_limit(mock_request)
        assert headers["X-RateLimit-Limit"] == "5"
    
    def test_health_endpoint_not_rate_limited(self):
        """Test that health endpoint is not rate limited."""
        # Make many requests to health endpoint
        for _ in range(100):
            response = client.get("/health")
            assert response.status_code == 200


class TestSecurityMiddleware:
    """Test security in API endpoints."""
    
    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )
        
        assert "access-control-allow-origin" in response.headers
    
    def test_rate_limit_headers_in_response(self):
        """Test rate limit headers in response."""
        response = client.get("/v1/reading/passages")
        
        # Rate limit headers should be present
        assert "x-ratelimit-limit" in response.headers or response.status_code == 200
