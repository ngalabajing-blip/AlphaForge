"""Generic HTTP webhook delivery (with HMAC signing)."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

from alphaforge_notifier.channels.base import Channel, DeliveryResult


class WebhookChannel(Channel):
    name = "webhook"

    def __init__(self, http) -> None:  # type: ignore[no-untyped-def]
        self._http = http

    async def send(self, alert: dict[str, Any], rendered: dict[str, str]) -> DeliveryResult:
        config = (alert.get("channel_config") or {}).get(self.name, {})
        url = config.get("url") or alert.get("webhook_url")
        secret = config.get("secret") or alert.get("webhook_secret")
        if not url:
            return DeliveryResult(self.name, False, error="missing_url")
        body = {
            "alert_id": alert.get("alert_id"),
            "title": rendered["title"],
            "severity": rendered["severity"],
            "text": rendered["text"],
            "raw": alert,
        }
        body_bytes = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        headers = {"Content-Type": "application/json"}
        if secret:
            sig = hmac.new(secret.encode(), body_bytes, hashlib.sha256).hexdigest()
            headers["X-AlphaForge-Signature"] = f"sha256={sig}"
        try:
            r = await self._http.post(url, content=body_bytes, headers=headers)
            r.raise_for_status()
            return DeliveryResult(self.name, True)
        except Exception as exc:  # noqa: BLE001
            return DeliveryResult(self.name, False, error=str(exc))
