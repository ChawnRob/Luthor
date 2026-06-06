from __future__ import annotations

from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from luthor.api.quota_service import check_and_increment_usage, is_complex_endpoint
from luthor.api.user_store import UserStore
from luthor.auth.jwt_verifier import decode_access_token, is_auth_required

PUBLIC_EXACT = {
    "/health",
    "/metrics",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/label-ui",
    "/demo-ui",
}
PUBLIC_PREFIXES = ("/auth/",)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        if not is_auth_required():
            return await call_next(request)

        path = request.url.path
        if path in PUBLIC_EXACT or any(path.startswith(prefix) for prefix in PUBLIC_PREFIXES):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing Bearer token"})

        token = auth_header.removeprefix("Bearer ").strip()
        try:
            claims = decode_access_token(token)
        except ValueError as exc:
            return JSONResponse(status_code=401, content={"detail": str(exc)})

        user_id = str(claims.get("sub", ""))
        email = str(claims.get("email", ""))
        if not user_id or not email:
            return JSONResponse(status_code=401, content={"detail": "Invalid token claims"})

        user_store: UserStore = request.app.state.user_store
        metadata = claims.get("user_metadata") or {}
        name = metadata.get("name") if isinstance(metadata, dict) else None
        try:
            user = user_store.upsert_from_jwt(user_id=user_id, email=email, name=name)
        except Exception as exc:
            return JSONResponse(status_code=503, content={"detail": f"User store error: {exc}"})

        request.state.user = user
        request.state.jwt_claims = claims

        try:
            request.state.quota = check_and_increment_usage(
                request,
                user,
                path=path,
                is_complex=is_complex_endpoint(path),
            )
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

        return await call_next(request)
