"""Discord webhook delivery."""

from __future__ import annotations

from typing import Any

from alphaforge_notifier.channels.base import Channel, DeliveryResult


class DiscordChannel(Channel):
    name = "discord"

    def __init__(self, http, default_webhook: str | None) -> None:  # type: ignore[no-untyped-def]
        self._http = http
        self._default = default_webhook

    async def send(self, alert: dict[str, Any], rendered: dict[str, str]) -> DeliveryResult:
        config = (alert.get("channel_config") or {}).get(self.name, {})
        webhook = config.get("webhook_url") or self._default
        if not webhook:
            return DeliveryResult(self.name, False, error="missing_webhook")
        try:
            r = await self._http.post(
                webhook,
                json={
                    "username": "AlphaForge",
                    "content": rendered["markdown"][:1900],
                    "embeds": [
                        {
                            "title": rendered["title"],
                            "description": rendered["text"][:2000],
                            "color": (0xE74C3C if rendered["severity"] in {"critical", "high"} else 0x3498DB),
                        }
                    ],
                },
            )
            r.raise_for_status()
            return DeliveryResult(self.name, True)
        except Exception as exc:  # noqa: BLE001
            return DeliveryResult(self.name, False, error=str(exc))
