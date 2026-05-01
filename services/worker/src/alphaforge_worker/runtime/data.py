"""
Synthetic OHLCV provider for backtests when no real history is available.

In production this is replaced with a ClickHouse-backed provider; we keep the
interface identical so swapping is a one-line change.
"""

from __future__ import annotations

import math
import random
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from alphaforge_shared.timeframes import parse_timeframe


@dataclass
class CandleProvider:
    seed: int = 7

    def stream(
        self,
        *,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> Iterator[dict]:
        tf = parse_timeframe(timeframe)
        rng = random.Random(self.seed ^ hash(symbol))
        ts = tf.floor(start.replace(tzinfo=UTC) if start.tzinfo is None else start)
        end_ts = end.replace(tzinfo=UTC) if end.tzinfo is None else end
        price = 100 + rng.random() * 1000
        i = 0
        while ts < end_ts:
            drift = math.sin(i / 24) * 5
            o = price + drift + rng.gauss(0, 0.5)
            c = o + rng.gauss(0, 1.0)
            h = max(o, c) + abs(rng.gauss(0, 0.3))
            l = min(o, c) - abs(rng.gauss(0, 0.3))
            v = abs(rng.gauss(100, 25))
            yield {"ts": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}
            price = c
            ts += timedelta(seconds=tf.seconds)
            i += 1
