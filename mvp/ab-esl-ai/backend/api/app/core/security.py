"""Security utilities for OAuth2/OIDC authentication."""

import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class OIDCSettings(BaseSettings):
    """OIDC/OAuth2 configuration."""
    
    # OIDC Provider settings (Azure AD B2C example)
    oidc_authority: str = ""  # e.g., https://login.microsoftonline.com/{tenant}/v2.0
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    oidc_audience: str = ""  # API audience/resource
    
    # JWT settings for local tokens
    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    
    # Feature flag
    enable_oidc: bool = False  # Set True in production
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_oidc_settings() -> OIDCSettings:
    return OIDCSettings()


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # Subject (user ID or session ID)
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp
    role: str = "student"  # student, teacher, admin
    session_id: Optional[int] = None
    participant_id: Optional[int] = None
    iss: str = "ab-esl-ai"  # Issuer


class User(BaseModel):
    """Authenticated user model."""
    id: str
    role: str
    session_id: Optional[int] = None
    participant_id: Optional[int] = None
    email: Optional[str] = None
    name: Optional[str] = None


# Security schemes
http_bearer = HTTPBearer(auto_error=False)


def create_access_token(
    subject: str,
    role: str = "student",
    session_id: Optional[int] = None,
    participant_id: Optional[int] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""
    settings = get_oidc_settings()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiry_hours)
    
    payload = TokenPayload(
        sub=subject,
        exp=int(expire.timestamp()),
        iat=int(datetime.utcnow().timestamp()),
        role=role,
        session_id=session_id,
        participant_id=participant_id,
    )
    
    return jwt.encode(
        payload.model_dump(),
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token."""
    settings = get_oidc_settings()
    
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_iat": False},  # Disable iat verification to avoid clock skew issues
        )
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
) -> Optional[User]:
    """Get current authenticated user from token."""
    if not credentials:
        return None
    
    token_payload = decode_token(credentials.credentials)
    
    return User(
        id=token_payload.sub,
        role=token_payload.role,
        session_id=token_payload.session_id,
        participant_id=token_payload.participant_id,
    )


async def get_current_user_required(
    user: Optional[User] = Depends(get_current_user),
) -> User:
    """Require an authenticated user."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_teacher_user(
    user: User = Depends(get_current_user_required),
) -> User:
    """Require a teacher or admin user."""
    if user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required",
        )
    return user


async def get_admin_user(
    user: User = Depends(get_current_user_required),
) -> User:
    """Require an admin user."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


# OIDC token validation (for production with Azure AD B2C)
class OIDCValidator:
    """Validates tokens from an OIDC provider."""
    
    def __init__(self):
        self._jwks_client = None
        self._last_refresh = 0
        self._refresh_interval = 3600  # Refresh JWKS every hour
    
    async def get_jwks_client(self):
        """Get or create JWKS client with caching."""
        settings = get_oidc_settings()
        current_time = time.time()
        
        if not settings.oidc_authority:
            return None
        
        if self._jwks_client is None or (current_time - self._last_refresh) > self._refresh_interval:
            try:
                jwks_uri = f"{settings.oidc_authority}/.well-known/jwks.json"
                self._jwks_client = jwt.PyJWKClient(jwks_uri)
                self._last_refresh = current_time
            except Exception:
                return None
        
        return self._jwks_client
    
    async def validate_oidc_token(self, token: str) -> Dict[str, Any]:
        """Validate an OIDC token from the identity provider."""
        settings = get_oidc_settings()
        
        if not settings.enable_oidc:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="OIDC authentication not configured",
            )
        
        jwks_client = await self.get_jwks_client()
        if not jwks_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to fetch OIDC keys",
            )
        
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.oidc_audience,
                issuer=settings.oidc_authority,
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OIDC token has expired",
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid OIDC token: {str(e)}",
            )


oidc_validator = OIDCValidator()
