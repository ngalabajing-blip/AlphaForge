from __future__ import annotations

from functools import lru_cache

from alphaforge_shared.settings import CommonSettings
from pydantic import Field


class NotifierSettings(CommonSettings):
    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    discord_default_webhook: str | None = Field(default=None, alias="DISCORD_WEBHOOK_URL")
    slack_default_webhook: str | None = Field(default=None, alias="SLACK_WEBHOOK_URL")
    email_smtp_host: str | None = Field(default=None, alias="EMAIL_SMTP_HOST")
    email_smtp_port: int = Field(default=587, alias="EMAIL_SMTP_PORT")
    email_smtp_user: str | None = Field(default=None, alias="EMAIL_SMTP_USER")
    email_smtp_password: str | None = Field(default=None, alias="EMAIL_SMTP_PASSWORD")
    email_from: str = Field(default="alerts@alphaforge.local", alias="EMAIL_FROM")
    pagerduty_routing_key: str | None = Field(default=None, alias="PAGERDUTY_ROUTING_KEY")
    rate_limit_per_minute: int = Field(default=120, alias="NOTIFIER_RATE_LIMIT_PER_MIN")
    dedupe_window_seconds: int = Field(default=60, alias="NOTIFIER_DEDUPE_WINDOW")


@lru_cache(maxsize=1)
def get_settings() -> NotifierSettings:
    return NotifierSettings()
