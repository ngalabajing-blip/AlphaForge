"""FastAPI application entry point for AlphaForge API gateway."""
from __future__ import annotations

import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from alphaforge_api import __version__
from alphaforge_api.api.v1 import router as v1_router
from alphaforge_api.core.config import get_settings
from alphaforge_api.core.database import db
from alphaforge_api.core.kafka_client import kafka_producer
from alphaforge_api.core.redis_client import redis_client
from alphaforge_api.errors import register_error_handlers
from alphaforge_api.graphql.schema import graphql_router
from alphaforge_api.middleware import RequestContextMiddleware
from alphaforge_api.ws.router import router as ws_router
from alphaforge_shared.logging import configure_logging, get_logger
from alphaforge_shared.telemetry import configure_tracing

settings = get_settings()
configure_logging(level=settings.app_log_level, json_logs=settings.is_production)
configure_tracing("alphaforge-api", settings.otel_endpoint)

log = get_logger("alphaforge_api")

# Prometheus metrics
HTTP_REQUESTS = Counter(
    "alphaforge_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
HTTP_LATENCY = Histogram(
    "alphaforge_http_request_seconds",
    "Request latency in seconds",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    log.info("api_startup", version=__version__, env=settings.app_env)
    await db.connect()
    await redis_client.connect()
    await kafka_producer.start()
    log.info("api_ready")
    try:
        yield
    finally:
        log.info("api_shutdown_begin")
        await kafka_producer.stop()
        await redis_client.close()
        await db.disconnect()
        log.info("api_shutdown_complete")


app = FastAPI(
    title="AlphaForge API",
    version=__version__,
    description=(
        "REST + GraphQL + WebSocket gateway for AlphaForge — "
        "the autonomous algorithmic trading & on-chain intelligence platform."
    ),
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    docs_url="/docs" if settings.app_debug else None,
    redoc_url="/redoc" if settings.app_debug else None,
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(RequestContextMiddleware)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    started = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - started
    path = request.scope.get("route").path if request.scope.get("route") else request.url.path  # type: ignore[union-attr]
    HTTP_REQUESTS.labels(request.method, path, str(response.status_code)).inc()
    HTTP_LATENCY.labels(request.method, path).observe(elapsed)
    response.headers["X-Process-Time-ms"] = f"{elapsed * 1000:.2f}"
    return response


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(v1_router, prefix="/api/v1")
app.include_router(graphql_router, prefix="/graphql")
app.include_router(ws_router, prefix="/ws")


# ── Misc endpoints ────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {
        "name": "AlphaForge API",
        "version": __version__,
        "docs": "/docs",
        "graphql": "/graphql",
    }


@app.get("/healthz", tags=["meta"])
async def healthz() -> dict[str, object]:
    return {
        "status": "ok",
        "version": __version__,
        "time": datetime.now(tz=timezone.utc).isoformat(),
    }


@app.get("/readyz", tags=["meta"])
async def readyz() -> JSONResponse:
    checks = {
        "database": await db.is_healthy(),
        "redis": await redis_client.is_healthy(),
        "kafka": kafka_producer.is_started,
    }
    healthy = all(checks.values())
    return JSONResponse({"ready": healthy, "checks": checks}, status_code=200 if healthy else 503)


@app.get("/metrics", include_in_schema=False)
async def metrics() -> JSONResponse:
    data = generate_latest()
    return JSONResponse(content=data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


register_error_handlers(app)
