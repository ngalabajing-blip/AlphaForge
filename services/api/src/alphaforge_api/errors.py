"""Centralised error handling."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from alphaforge_shared.exceptions import APIError, AlphaForgeError
from alphaforge_shared.logging import get_logger

log = get_logger("alphaforge_api.errors")


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def _api_error(_: Request, exc: APIError) -> JSONResponse:
        return JSONResponse(
            {"error": {"type": type(exc).__name__, "message": str(exc)}},
            status_code=exc.status_code,
        )

    @app.exception_handler(AlphaForgeError)
    async def _generic_error(_: Request, exc: AlphaForgeError) -> JSONResponse:
        log.warning("domain_error", error=type(exc).__name__, message=str(exc))
        return JSONResponse(
            {"error": {"type": type(exc).__name__, "message": str(exc)}},
            status_code=400,
        )

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
        log.exception("unhandled_error", error=type(exc).__name__)
        return JSONResponse(
            {"error": {"type": "InternalServerError", "message": "internal error"}},
            status_code=500,
        )
