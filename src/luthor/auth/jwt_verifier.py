from __future__ import annotations

import os
from typing import Any

import jwt
from jwt import PyJWTError


def is_auth_required() -> bool:
    return os.getenv("LUTHOR_AUTH_REQUIRED", "false").lower() == "true"


def get_jwt_secret() -> str | None:
    secret = os.getenv("SUPABASE_JWT_SECRET", "").strip()
    return secret or None


def decode_access_token(token: str) -> dict[str, Any]:
    secret = get_jwt_secret()
    if not secret:
        raise ValueError("SUPABASE_JWT_SECRET is not configured")

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience="authenticated",
            options={"require": ["sub", "exp"]},
        )
    except PyJWTError as exc:
        raise ValueError(f"Invalid token: {exc}") from exc

    return payload
