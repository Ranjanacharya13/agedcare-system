import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import bcrypt
import jwt

from backend.config.settings import get_settings

ALGORITHM = "HS256"

BCRYPT_ROUNDS = 12


class TokenError(Exception):
    """Token absent, malformed, expired or badly signed."""


def _prepare(password: str) -> bytes:
    """SHA-256 first so bcrypt never truncates at 72 bytes."""
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_prepare(password), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(_prepare(plain_password), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        # A malformed stored hash must read as "wrong password", never as an
        # exception that leaks the difference to the caller.
        return False


def create_access_token(
    subject: str,
    *,
    role: str | None = None,
    email: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Mint a signed access token."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": now,
        "jti": str(uuid4()),
    }
    if role is not None:
        payload["role"] = role
    if email is not None:
        payload["email"] = email
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc
