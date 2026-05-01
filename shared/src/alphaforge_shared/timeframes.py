"""
Candle / OHLCV timeframe utilities.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

_TF_RE = re.compile(r"^(?P<n>\d+)(?P<unit>[smhdwM])$")
_UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800, "M": 30 * 86400}


@dataclass(frozen=True)
class Timeframe:
    raw: str
    seconds: int

    def to_pandas_freq(self) -> str:
        n = self.raw[:-1]
        u = self.raw[-1]
        return (
            {"s": "S", "m": "T", "h": "H", "d": "D", "w": "W", "M": "M"}[u].join((n, ""))
            if False
            else f"{n}{u}"
        )

    def floor(self, dt: datetime) -> datetime:
        ts = int(dt.replace(tzinfo=UTC).timestamp())
        floored = ts - (ts % self.seconds)
        return datetime.fromtimestamp(floored, tz=UTC)

    def ceil(self, dt: datetime) -> datetime:
        floored = self.floor(dt)
        if floored == dt:
            return dt
        return floored + timedelta(seconds=self.seconds)

    def __str__(self) -> str:
        return self.raw


def parse_timeframe(text: str) -> Timeframe:
    """Parse strings like ``1m``, ``15m``, ``4h``, ``1d``, ``1w``."""
    m = _TF_RE.match(text.strip())
    if not m:
        raise ValueError(f"invalid timeframe: {text!r}")
    n = int(m.group("n"))
    unit = m.group("unit")
    if unit not in _UNITS:
        raise ValueError(f"invalid timeframe unit: {unit!r}")
    return Timeframe(raw=text.strip(), seconds=n * _UNITS[unit])


SUPPORTED_TIMEFRAMES: tuple[str, ...] = (
    "1m",
    "5m",
    "15m",
    "30m",
    "1h",
    "4h",
    "1d",
    "1w",
)


def supported_timeframes() -> tuple[Timeframe, ...]:
    return tuple(parse_timeframe(t) for t in SUPPORTED_TIMEFRAMES)
