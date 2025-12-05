"""Authentication service for class sessions.

IMPORTANT: DEMO-GRADE AUTHENTICATION
=====================================
This authentication system is designed for MVP demonstration purposes only.
It is NOT suitable for production deployment without significant enhancements.

Current Limitations:
-------------------
1. Token Format: Simple colon-delimited string with SHA256 signature
   - Vulnerable to timing attacks on signature comparison
   - No encryption, only signing (payload is readable)

2. Secret Management: Reuses MinIO secret key as signing secret
   - Should use dedicated, rotatable JWT secret
   - No key rotation mechanism

3. Token Storage: Tokens are stateless (not revocable)
   - Cannot invalidate tokens before expiry
   - No refresh token mechanism

4. Session Security:
   - 6-character class codes are guessable with brute force
   - No rate limiting on code guessing (rate limiting exists elsewhere)
   - No CAPTCHA for join attempts

5. Missing Production Features:
   - No password hashing (teachers have no accounts)
   - No multi-factor authentication
   - No OAuth2/OIDC integration
   - No audit logging of auth events
   - No IP-based session binding
   - No device fingerprinting

For Production:
--------------
- Replace with proper JWT library (python-jose, PyJWT)
- Implement OAuth2 with proper flows
- Add teacher account system with bcrypt password hashing
- Implement token refresh and revocation
- Add rate limiting on authentication endpoints
- Consider SAML integration for school district SSO
- Add comprehensive audit logging for FOIP compliance

Why this is acceptable for demo:
-------------------------------
- Short-lived demo sessions (24 hours max)
- No real student data in demo
- Demonstrates authentication flow patterns
- Easy to understand for technical due diligence
- Quick to replace with production implementation
"""

import secrets
import time
import hashlib
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.session import ClassSession, Participant


TOKEN_EXPIRY = 86400  # 24 hours for demo


def generate_class_code() -> str:
    """Generate a 6-character alphanumeric class code.
    
    Note: For production, consider longer codes or time-limited validity
    to prevent brute-force guessing attacks.
    """
    return secrets.token_hex(3).upper()


def generate_token(session_id: int, participant_id: Optional[int], is_teacher: bool) -> str:
    """Generate a simple demo token (not production-grade).
    
    WARNING: This is a demo implementation. For production:
    - Use proper JWT with RS256 or ES256 signing
    - Include 'iat', 'nbf', 'jti' claims
    - Use dedicated secret management (Azure Key Vault, AWS Secrets Manager)
    """
    exp = int(time.time()) + TOKEN_EXPIRY
    payload = f"{session_id}:{participant_id or 0}:{int(is_teacher)}:{exp}"
    secret = settings.minio_secret_key  # Reuse existing secret for demo
    signature = hashlib.sha256(f"{payload}:{secret}".encode()).hexdigest()[:16]
    return f"{payload}:{signature}"


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a demo token.
    
    WARNING: This is a demo implementation. For production:
    - Use constant-time comparison for signatures
    - Add token revocation checking
    - Log verification attempts for audit
    """
    try:
        parts = token.split(":")
        if len(parts) != 5:
            return None
        session_id, participant_id, is_teacher, exp, signature = parts
        payload = f"{session_id}:{participant_id}:{is_teacher}:{exp}"
        secret = settings.minio_secret_key
        expected_sig = hashlib.sha256(f"{payload}:{secret}".encode()).hexdigest()[:16]
        if signature != expected_sig:
            return None
        if int(exp) < time.time():
            return None
        return {
            "session_id": int(session_id),
            "participant_id": int(participant_id) if int(participant_id) > 0 else None,
            "is_teacher": bool(int(is_teacher)),
        }
    except Exception:
        return None
