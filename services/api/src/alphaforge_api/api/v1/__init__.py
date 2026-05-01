"""API v1 — REST routers."""

from fastapi import APIRouter

from alphaforge_api.api.v1.routes import (
    alerts,
    apikeys,
    audits,
    auth,
    backtests,
    chains,
    healthz,
    market,
    signals,
    strategies,
    users,
    webhook,
)

router = APIRouter()
router.include_router(healthz.router, tags=["meta"])
router.include_router(auth.router, tags=["auth"])
router.include_router(users.router, tags=["users"])
router.include_router(apikeys.router, tags=["api-keys"])
router.include_router(strategies.router, tags=["strategies"])
router.include_router(backtests.router, tags=["backtests"])
router.include_router(signals.router, tags=["signals"])
router.include_router(alerts.router, tags=["alerts"])
router.include_router(audits.router, tags=["audits"])
router.include_router(chains.router, tags=["chains"])
router.include_router(market.router, tags=["market"])
router.include_router(webhook.router, tags=["webhooks"])
