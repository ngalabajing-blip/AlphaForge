"""Dispatcher — picks the right channel(s) for each alert and fan-outs."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from alphaforge_shared.logging import get_logger

from alphaforge_notifier.channels.base import Channel, DeliveryResult
from alphaforge_notifier.channels.discord import DiscordChannel
from alphaforge_notifier.channels.email import EmailChannel
from alphaforge_notifier.channels.pagerduty import PagerDutyChannel
from alphaforge_notifier.channels.slack import SlackChannel
from alphaforge_notifier.channels.telegram import TelegramChannel
from alphaforge_notifier.channels.webhook import WebhookChannel
from alphaforge_notifier.config import get_settings
from alphaforge_notifier.templates import render_template

log = get_logger("alphaforge_notifier.dispatcher")


class NotifierDispatcher:
    def __init__(self) -> None:
        self._channels: dict[str, Channel] = {}
        self._http: httpx.AsyncClient | None = None
        self._dedup: dict[str, datetime] = {}
        self._rate_buckets: dict[str, list[datetime]] = defaultdict(list)

    async def start(self) -> None:
        settings = get_settings()
        self._http = httpx.AsyncClient(timeout=10.0)
        self._channels = {
            "telegram": TelegramChannel(self._http, settings.telegram_bot_token),
            "discord": DiscordChannel(self._http, settings.discord_default_webhook),
            "slack": SlackChannel(self._http, settings.slack_default_webhook),
            "webhook": WebhookChannel(self._http),
            "email": EmailChannel(
                host=settings.email_smtp_host,
                port=settings.email_smtp_port,
                user=settings.email_smtp_user,
                password=settings.email_smtp_password,
                sender=settings.email_from,
            ),
            "pagerduty": PagerDutyChannel(self._http, settings.pagerduty_routing_key),
        }

    async def stop(self) -> None:
        if self._http is not None:
            await self._http.aclose()

    async def dispatch(self, alert: dict[str, Any]) -> list[DeliveryResult]:
        results: list[DeliveryResult] = []
        channels = alert.get("channels") or ["webhook"]
        dedup_key = self._dedup_key(alert)
        if self._is_duplicate(dedup_key):
            log.info("duplicate_skipped", dedup_key=dedup_key)
            return [DeliveryResult(channel="dedup", success=False, error="duplicate")]
        if not self._consume_rate_token(alert):
            return [DeliveryResult(channel="rate_limit", success=False, error="rate_limited")]
        rendered = render_template(alert)
        coros = [self._send_one(name, alert, rendered) for name in channels]
        for coro in await asyncio.gather(*coros, return_exceptions=True):
            if isinstance(coro, Exception):
                results.append(DeliveryResult(channel="error", success=False, error=str(coro)))
            else:
                results.append(coro)
        return results

    async def _send_one(
        self, channel_name: str, alert: dict[str, Any], rendered: dict[str, str]
    ) -> DeliveryResult:
        channel = self._channels.get(channel_name)
        if channel is None:
            return DeliveryResult(channel=channel_name, success=False, error="unknown_channel")
        try:
            return await channel.send(alert, rendered)
        except Exception as exc:  # noqa: BLE001
            log.exception("dispatch_failed", channel=channel_name)
            return DeliveryResult(channel=channel_name, success=False, error=str(exc))

    # ── helpers ───────────────────────────────────────────────────────────────
    def _dedup_key(self, alert: dict[str, Any]) -> str:
        return f"{alert.get('alert_id')}:{alert.get('rule_type')}:{alert.get('symbol')}:{alert.get('payload', {}).get('digest', '')}"

    def _is_duplicate(self, key: str) -> bool:
        now = datetime.now(tz=UTC)
        ttl = timedelta(seconds=get_settings().dedupe_window_seconds)
        last = self._dedup.get(key)
        self._dedup[key] = now
        if last is None:
            return False
        return now - last < ttl

    def _consume_rate_token(self, alert: dict[str, Any]) -> bool:
        owner = str(alert.get("owner_id") or "global")
        bucket = self._rate_buckets[owner]
        now = datetime.now(tz=UTC)
        cutoff = now - timedelta(minutes=1)
        # purge old
        self._rate_buckets[owner] = [t for t in bucket if t > cutoff]
        if len(self._rate_buckets[owner]) >= get_settings().rate_limit_per_minute:
            return False
        self._rate_buckets[owner].append(now)
        return True
