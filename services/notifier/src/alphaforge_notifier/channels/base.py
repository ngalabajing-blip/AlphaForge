"""Base classes for delivery channels."""
from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any


@dataclass
class DeliveryResult:
    channel: str
    success: bool
    error: str | None = None
    payload: dict[str, Any] | None = None


class Channel(abc.ABC):
    name: str

    @abc.abstractmethod
    async def send(self, alert: dict[str, Any], rendered: dict[str, str]) -> DeliveryResult:
        ...
