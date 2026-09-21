"""Request-scoped middleware."""

import logging
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from backend.core import request_context
from backend.core.rate_limit import client_ip

logger = logging.getLogger("backend.access")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid4())
        request_context.set_request_id(request_id)
        request_context.set_ip_address(client_ip(request))
        started = time.perf_counter()

        try:
            response = await call_next(request)
        finally:
            # Reset before the next task can inherit this context.
            elapsed_ms = (time.perf_counter() - started) * 1000
            actor = request_context.get_actor()
            request_context.reset()

        response.headers["X-Request-ID"] = request_id
        if request.method != "GET":
            logger.info(
                "%s %s -> %s in %.1fms (actor=%s, request_id=%s)",
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
                actor.email or "anonymous",
                request_id,
            )
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Baseline response headers."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Cache-Control", "no-store" if request.url.path != "/api/v1/health" else "no-cache"
        )
        return response
