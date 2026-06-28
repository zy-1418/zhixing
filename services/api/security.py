from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return f"pbkdf2_sha256$120000${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, rounds, salt, expected = password_hash.split("$", 3)
    except ValueError:
        return False
    if scheme != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), int(rounds)
    ).hex()
    return hmac.compare_digest(digest, expected)


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expires_minutes)).timestamp()),
        **(extra_claims or {}),
    }
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = ".".join(
        [
            _b64encode(json.dumps(header, separators=(",", ":")).encode()),
            _b64encode(json.dumps(payload, separators=(",", ":")).encode()),
        ]
    )
    signature = hmac.new(
        settings.secret_key.encode(), signing_input.encode(), hashlib.sha256
    ).digest()
    return f"{signing_input}.{_b64encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        signing_input, signature = token.rsplit(".", 1)
        expected = hmac.new(
            settings.secret_key.encode(), signing_input.encode(), hashlib.sha256
        ).digest()
        if not hmac.compare_digest(_b64decode(signature), expected):
            raise ValueError("bad signature")
        payload = json.loads(_b64decode(signing_input.split(".", 1)[1]))
    except Exception as exc:  # noqa: BLE001 - normalized to HTTP 401 below
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from exc

    if int(payload.get("exp", 0)) < int(datetime.now(UTC).timestamp()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired",
        )
    return payload


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token subject",
        )
    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token subject",
        ) from exc
    result = await db.scalars(select(User).where(User.id == user_uuid))
    user = result.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
