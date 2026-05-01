"""Price prediction loop."""
from __future__ import annotations

import asyncio
import math
import random
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import Deque

from alphaforge_ml.features.extractors import extract_candle_features
from alphaforge_ml.models.forecaster import RandomForestForecaster
from alphaforge_shared.events import PricePredictionEvent
from alphaforge_shared.kafka import EventProducer
from alphaforge_shared.logging import get_logger
from alphaforge_shared.topics import T_PRICE_PREDICTION

log = get_logger("alphaforge_ml.predict")

SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "ARB/USDT"]


def _synthesise_candles(symbol: str, n: int = 200) -> list[dict]:
    rng = random.Random(hash(symbol))
    base = 100 + rng.random() * 1000
    candles: list[dict] = []
    now = datetime.now(tz=timezone.utc).replace(microsecond=0, second=0)
    for i in range(n):
        ts = now - timedelta(hours=n - i)
        drift = math.sin(i / 12) * 5
        o = base + drift + rng.gauss(0, 0.5)
        c = o + rng.gauss(0, 1)
        h = max(o, c) + abs(rng.gauss(0, 0.5))
        l = min(o, c) - abs(rng.gauss(0, 0.5))
        candles.append({"ts": ts, "open": o, "high": h, "low": l, "close": c, "volume": abs(rng.gauss(100, 20))})
        base = c
    return candles


async def run_prediction_loop(stop: asyncio.Event) -> None:
    forecaster = RandomForestForecaster()
    history: dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=400))
    producer: EventProducer | None = None
    try:
        from alphaforge_ml.config import get_settings
        producer = EventProducer(get_settings().kafka_bootstrap)
        await producer.start()
    except Exception:
        producer = None

    log.info("prediction_loop_started")
    try:
        while not stop.is_set():
            for symbol in SYMBOLS:
                candles = _synthesise_candles(symbol)
                feats = extract_candle_features(candles)
                X = [r.as_vector() for r in feats[:-1]]
                y = [r.c for r in feats[1:]]
                if len(X) >= 30:
                    forecaster.fit(X, y)
                mu, sigma = forecaster.predict([feats[-1].as_vector()])
                last_close = feats[-1].c if feats else 0.0
                direction = "flat"
                if mu > last_close * 1.005:
                    direction = "up"
                elif mu < last_close * 0.995:
                    direction = "down"
                ev = PricePredictionEvent(
                    producer="alphaforge-ml",
                    symbol=symbol,
                    horizon_seconds=3600,
                    predicted_close=mu or last_close,
                    direction=direction,
                    confidence=max(0.0, min(1.0, 1.0 - sigma / max(1.0, last_close))),
                    sigma=sigma,
                    ts=datetime.now(tz=timezone.utc),
                )
                if producer is not None:
                    try:
                        await producer.publish(T_PRICE_PREDICTION, ev, key=symbol)
                    except Exception:
                        pass
            try:
                await asyncio.wait_for(stop.wait(), timeout=10)
            except asyncio.TimeoutError:
                pass
    finally:
        if producer is not None:
            await producer.stop()
        log.info("prediction_loop_stopped")
