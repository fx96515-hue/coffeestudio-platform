from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

"""Security primitives.

We intentionally use PBKDF2 (pbkdf2_sha256) instead of bcrypt.

Reason:
- passlib+bcrypt can break in container builds when bcrypt's internal version
  metadata layout changes (e.g. bcrypt 4.x removed bcrypt.__about__).
- PBKDF2 is implemented without native bcrypt bindings and is stable across
  Windows/Docker environments.

NOTE:
- This is a local/dev product, but we still use a strong KDF and fail-fast
  if required secrets are missing.
"""

# ~300k rounds is a good baseline on modern CPUs; adjust later if needed.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__rounds=300_000,
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(sub: str, role: str, expires_minutes: int = 60 * 24) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        "sub": sub,
        "role": role,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=["HS256"],
        audience=settings.JWT_AUDIENCE,
        issuer=settings.JWT_ISSUER,
    )
