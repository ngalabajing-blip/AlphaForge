"""Telegram bot delivery."""

from __future__ import annotations

from typing import Any

from alphaforge_notifier.channels.base import Channel, DeliveryResult


class TelegramChannel(Channel):
    name = "telegram"

    def __init__(self, http, default_token: str | None) -> None:  # type: ignore[no-untyped-def]
        self._http = http
        self._default_token = default_token

    async def send(self, alert: dict[str, Any], rendered: dict[str, str]) -> DeliveryResult:
        config = (alert.get("channel_config") or {}).get(self.name, {})
        token = config.get("bot_token") or self._default_token
        chat_id = config.get("chat_id")
        if not token or not chat_id:
            return DeliveryResult(self.name, False, error="missing_config")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            r = await self._http.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": rendered["markdown"],
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True,
                },
            )
            r.raise_for_status()
            return DeliveryResult(self.name, True)
        except Exception as exc:  # noqa: BLE001
            return DeliveryResult(self.name, False, error=str(exc))
