"""SMTP email delivery."""
from __future__ import annotations

import asyncio
from email.message import EmailMessage
from typing import Any

from alphaforge_notifier.channels.base import Channel, DeliveryResult


class EmailChannel(Channel):
    name = "email"

    def __init__(self, *, host: str | None, port: int, user: str | None,
                 password: str | None, sender: str) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.sender = sender

    async def send(self, alert: dict[str, Any], rendered: dict[str, str]) -> DeliveryResult:
        config = (alert.get("channel_config") or {}).get(self.name, {})
        recipients = config.get("recipients") or alert.get("recipients") or []
        if isinstance(recipients, str):
            recipients = [recipients]
        if not recipients or not self.host:
            return DeliveryResult(self.name, False, error="missing_recipients_or_smtp_host")

        msg = EmailMessage()
        msg["From"] = self.sender
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = f"[AlphaForge] {rendered['title']}"
        msg.set_content(rendered["text"])

        try:
            await asyncio.to_thread(self._send_smtp, msg)
            return DeliveryResult(self.name, True)
        except Exception as exc:  # noqa: BLE001
            return DeliveryResult(self.name, False, error=str(exc))

    def _send_smtp(self, msg) -> None:  # type: ignore[no-untyped-def]
        import smtplib
        with smtplib.SMTP(self.host, self.port, timeout=8) as smtp:
            smtp.starttls()
            if self.user and self.password:
                smtp.login(self.user, self.password)
            smtp.send_message(msg)
