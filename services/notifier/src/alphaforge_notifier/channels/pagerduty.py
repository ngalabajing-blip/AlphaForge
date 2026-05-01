"""PagerDuty Events API v2 delivery."""

from __future__ import annotations

from typing import Any

from alphaforge_notifier.channels.base import Channel, DeliveryResult


class PagerDutyChannel(Channel):
    name = "pagerduty"
    URL = "https://events.pagerduty.com/v2/enqueue"

    SEVERITY_MAP = {
        "info": "info",
        "low": "info",
        "medium": "warning",
        "high": "error",
        "critical": "critical",
    }

    def __init__(self, http, default_routing_key: str | None) -> None:  # type: ignore[no-untyped-def]
        self._http = http
        self._default = default_routing_key

    async def send(self, alert: dict[str, Any], rendered: dict[str, str]) -> DeliveryResult:
        config = (alert.get("channel_config") or {}).get(self.name, {})
        routing_key = config.get("routing_key") or self._default
        if not routing_key:
            return DeliveryResult(self.name, False, error="missing_routing_key")
        severity = self.SEVERITY_MAP.get(rendered.get("severity", "info"), "info")
        payload = {
            "routing_key": routing_key,
            "event_action": "trigger",
            "dedup_key": str(alert.get("alert_id") or rendered["title"])[:255],
            "payload": {
                "summary": rendered["title"][:1024],
                "severity": severity,
                "source": "alphaforge",
                "custom_details": alert.get("payload", {}),
            },
        }
        try:
            r = await self._http.post(self.URL, json=payload)
            r.raise_for_status()
            return DeliveryResult(self.name, True)
        except Exception as exc:  # noqa: BLE001
            return DeliveryResult(self.name, False, error=str(exc))
