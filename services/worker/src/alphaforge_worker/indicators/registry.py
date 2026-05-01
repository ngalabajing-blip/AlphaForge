"""Indicator base class and registry."""
from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Sequence


class Indicator(abc.ABC):
    """Indicators are stateful — they accept candles in stream order via ``update``."""

    name: str

    @abc.abstractmethod
    def update(self, candle: dict) -> Any:
        ...

    @abc.abstractmethod
    def latest(self) -> Any:
        ...

    def history(self, n: int = 200) -> list[float]:
        return list(getattr(self, "_values", []))[-n:]


INDICATORS: dict[str, type[Indicator]] = {}


def register_indicator(name: str):  # type: ignore[no-untyped-def]
    def deco(cls: type[Indicator]) -> type[Indicator]:
        cls.name = name
        INDICATORS[name] = cls
        return cls
    return deco
