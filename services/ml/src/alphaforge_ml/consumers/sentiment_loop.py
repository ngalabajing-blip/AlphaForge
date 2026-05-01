"""
Sentiment consumer loop.

In production this consumes social-media webhook events; for dev we
synthesise a stream of crypto-related comments and publish per-asset rolling
sentiment.
"""

from __future__ import annotations

import asyncio
import random
from collections import defaultdict, deque
from datetime import UTC, datetime

from alphaforge_shared.events import SentimentEvent
from alphaforge_shared.kafka import EventProducer
from alphaforge_shared.logging import get_logger
from alphaforge_shared.topics import T_SENTIMENT

from alphaforge_ml.config import get_settings
from alphaforge_ml.models.sentiment import get_sentiment_model

log = get_logger("alphaforge_ml.sentiment")

SAMPLE_TEXTS = [
    "ETH absolutely mooning right now, breakout above resistance",
    "BTC is dumping hard, looks like a bear flag",
    "SOL pumping, network is FAST",
    "rug pull on this new memecoin, lots of rekt people",
    "AAVE looking bullish, accumulating here",
    "Layer 2 fees are soaring",
    "Whales are buying the dip",
    "Looks like a honeypot, careful",
    "panic sell incoming",
    "send it, ETH to 5k",
]
SYMBOLS = ["BTC", "ETH", "SOL", "BNB", "ARB"]


async def run_sentiment_loop(stop: asyncio.Event) -> None:
    settings = get_settings()
    model = get_sentiment_model(settings.sentiment_backend)
    rolling: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=64))

    producer: EventProducer | None = None
    try:
        producer = EventProducer(settings.kafka_bootstrap)
        await producer.start()
    except Exception:
        producer = None

    log.info("sentiment_loop_started", backend=settings.sentiment_backend)
    rng = random.Random(42)
    try:
        while not stop.is_set():
            text = rng.choice(SAMPLE_TEXTS)
            symbol = rng.choice(SYMBOLS)
            result = model.predict(text)
            rolling[symbol].append(result.score)
            avg = sum(rolling[symbol]) / len(rolling[symbol])
            event = SentimentEvent(
                producer="alphaforge-ml",
                symbol=symbol,
                score=result.score,
                rolling_score=round(avg, 4),
                label=result.label,
                confidence=result.confidence,
                source="synthetic",
                sample_size=len(rolling[symbol]),
                ts=datetime.now(tz=UTC),
            )
            if producer is not None:
                try:
                    await producer.publish(T_SENTIMENT, event, key=symbol)
                except Exception:
                    pass
            try:
                await asyncio.wait_for(stop.wait(), timeout=1.0)
            except TimeoutError:
                pass
    finally:
        if producer is not None:
            await producer.stop()
        log.info("sentiment_loop_stopped")
