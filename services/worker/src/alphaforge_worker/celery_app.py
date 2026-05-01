"""Celery app — broker / backend wiring for the worker service."""

from __future__ import annotations

from celery import Celery

from alphaforge_worker.config import get_settings

_settings = get_settings()
celery_app = Celery(
    "alphaforge_worker",
    broker=_settings.celery_broker_url,
    backend=_settings.celery_result_backend,
    include=["alphaforge_worker.tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)
