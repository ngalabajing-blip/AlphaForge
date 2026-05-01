"""
Common settings primitives shared by all services.

Each service has its own :class:`pydantic_settings.BaseSettings` subclass that
extends :class:`CommonSettings` to pick up everything below.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application meta
    app_env: Literal["development", "staging", "production", "test"] = Field("development", alias="APP_ENV")
    app_debug: bool = Field(True, alias="APP_DEBUG")
    app_secret_key: str = Field("change-me", alias="APP_SECRET_KEY")
    app_log_level: str = Field("INFO", alias="APP_LOG_LEVEL")

    # PostgreSQL
    database_url: str = Field(
        "postgresql+asyncpg://alphaforge:alphaforge_dev@localhost:5432/alphaforge",
        alias="DATABASE_URL",
    )

    # ClickHouse
    clickhouse_host: str = Field("localhost", alias="CLICKHOUSE_HOST")
    clickhouse_port: int = Field(8123, alias="CLICKHOUSE_PORT")
    clickhouse_db: str = Field("alphaforge_ts", alias="CLICKHOUSE_DB")
    clickhouse_user: str = Field("default", alias="CLICKHOUSE_USER")
    clickhouse_password: str = Field("", alias="CLICKHOUSE_PASSWORD")

    # Redis
    redis_url: str = Field("redis://localhost:6379/0", alias="REDIS_URL")
    celery_broker_url: str = Field("redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field("redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND")

    # Kafka
    kafka_bootstrap: str = Field("localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS")
    kafka_client_id: str = Field("alphaforge", alias="KAFKA_CLIENT_ID")
    kafka_consumer_group: str = Field("alphaforge", alias="KAFKA_CONSUMER_GROUP")

    # Telemetry
    otel_endpoint: str | None = Field(None, alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    sentry_dsn: str | None = Field(None, alias="SENTRY_DSN")

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_test(self) -> bool:
        return self.app_env == "test"


@lru_cache(maxsize=1)
def get_common_settings() -> CommonSettings:
    return CommonSettings()
