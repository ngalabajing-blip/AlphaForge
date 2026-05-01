"""Slack incoming webhook delivery."""

from __future__ import annotations

from typing import Any

from alphaforge_notifier.channels.base import Channel, DeliveryResult


class SlackChannel(Channel):
    name = "slack"

    def __init__(self, http, default_webhook: str | None) -> None:  # type: ignore[no-untyped-def]
        self._http = http
        self._default = default_webhook

    async def send(self, alert: dict[str, Any], rendered: dict[str, str]) -> DeliveryResult:
        config = (alert.get("channel_config") or {}).get(self.name, {})
        url = config.get("webhook_url") or self._default
        if not url:
            return DeliveryResult(self.name, False, error="missing_webhook")
        try:
            r = await self._http.post(
                url,
                json={
                    "text": rendered["title"],
                    "blocks": [
                        {
                            "type": "header",
                            "text": {"type": "plain_text", "text": rendered["title"]},
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": rendered["markdown"][:2900],
                            },
                        },
                    ],
                },
            )
            r.raise_for_status()
            return DeliveryResult(self.name, True)
        except Exception as exc:  # noqa: BLE001
            return DeliveryResult(self.name, False, error=str(exc))
