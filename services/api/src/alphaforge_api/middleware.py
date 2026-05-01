"""Custom middleware: request id, structured logging context."""

from __future__ import annotations

import time
import uuid

from alphaforge_shared.logging import get_logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from structlog.contextvars import bind_contextvars, clear_contextvars

log = get_logger("alphaforge_api.middleware")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        bind_contextvars(request_id=request_id, path=request.url.path, method=request.method)
        request.state.request_id = request_id
        started = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            log.exception("request_failed")
            raise
        else:
            elapsed_ms = (time.perf_counter() - started) * 1000
            log.info(
                "request_done",
                status=response.status_code,
                elapsed_ms=round(elapsed_ms, 2),
            )
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            clear_contextvars()
