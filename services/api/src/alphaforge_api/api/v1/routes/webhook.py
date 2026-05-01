"""Inbound webhooks (e.g. payment provider, third-party data sources)."""
from __future__ import annotations

import hmac
from hashlib import sha256

from fastapi import APIRouter, Header, HTTPException, Request

from alphaforge_api.core.config import get_settings

router = APIRouter(prefix="/webhooks")


def _verify_signature(secret: str, payload: bytes, signature: str | None) -> bool:
    if not signature:
        return False
    expected = hmac.new(secret.encode("utf-8"), payload, sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/inbound/{provider}")
async def inbound(
    provider: str,
    request: Request,
    x_signature: str | None = Header(default=None, alias="X-Signature"),
) -> dict:
    raw = await request.body()
    settings = get_settings()
    if not _verify_signature(settings.app_secret_key, raw, x_signature):
        raise HTTPException(status_code=401, detail="invalid signature")
    return {"provider": provider, "received": True, "size": len(raw)}
