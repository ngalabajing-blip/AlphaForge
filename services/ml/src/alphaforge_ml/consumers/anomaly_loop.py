"""Anomaly consumer loop — synthetic when no Kafka is available."""
from __future__ import annotations

import asyncio
import random
from collections import defaultdict, deque
from datetime import datetime, timezone
from decimal import Decimal

from alphaforge_ml.features.extractors import TradeWindowFeatures, extract_trade_window
from alphaforge_ml.models.anomaly import AnomalyDetector
from alphaforge_ml.models.autoencoder import PCAReconstruction
from alphaforge_shared.events import AnomalyEvent
from alphaforge_shared.kafka import EventProducer
from alphaforge_shared.logging import get_logger
from alphaforge_shared.topics import T_ANOMALY

log = get_logger("alphaforge_ml.anomaly")

WINDOW_SIZE = 32
HISTORY_SIZE = 256


async def run_anomaly_loop(stop: asyncio.Event) -> None:
    """Synthetic loop: produces fake trade windows so the pipeline has signal in dev."""
    detector = AnomalyDetector()
    pca = PCAReconstruction(n_components=4)
    history: dict[str, deque[list[float]]] = defaultdict(lambda: deque(maxlen=HISTORY_SIZE))
    producer: EventProducer | None = None
    try:
        from alphaforge_ml.config import get_settings
        producer = EventProducer(get_settings().kafka_bootstrap)
        await producer.start()
    except Exception:
        producer = None

    pairs = ["ETH/USDC", "BTC/USDC", "SOL/USDC", "BNB/USDT", "ARB/USDT"]
    log.info("anomaly_loop_started")
    try:
        while not stop.is_set():
            for pair in pairs:
                trades = _synthesize_trades(pair)
                feats = extract_trade_window(trades)
                vector = feats.as_vector()
                history[pair].append(vector)
                if len(history[pair]) >= 30:
                    detector.fit(list(history[pair]))
                    pca.fit(list(history[pair]))
                score = detector.score(vector, history=list(history[pair]))
                recon = pca.score(vector)
                if score.is_anomaly or recon.score > 0.95:
                    event = AnomalyEvent(
                        producer="alphaforge-ml",
                        symbol=pair,
                        score=max(score.score, recon.score),
                        is_anomaly=True,
                        signals=score.explanations + ([f"reconstruction_error={recon.error:.3f}"] if recon.error else []),
                        window_seconds=60,
                        ts=datetime.now(tz=timezone.utc),
                    )
                    if producer is not None:
                        await producer.publish(T_ANOMALY, event, key=pair)
                    log.info("anomaly_detected", symbol=pair, score=event.score, signals=event.signals)
            try:
                await asyncio.wait_for(stop.wait(), timeout=2.5)
            except asyncio.TimeoutError:
                pass
    finally:
        if producer is not None:
            await producer.stop()
        log.info("anomaly_loop_stopped")


def _synthesize_trades(pair: str) -> list[dict]:
    rng = random.Random(hash(pair) ^ int(datetime.now(tz=timezone.utc).timestamp()))
    n = rng.randint(50, 250)
    base_price = 100 + rng.random() * 1000
    out: list[dict] = []
    for _ in range(n):
        size = abs(rng.gauss(1, 5))
        if rng.random() < 0.005:
            size *= 100  # simulate whale trade
        out.append({
            "ts": datetime.now(tz=timezone.utc),
            "amount_in": size,
            "side": "buy" if rng.random() > 0.5 else "sell",
            "buyer": f"0x{rng.randint(0, 16**40 - 1):040x}",
            "price": base_price * (1 + rng.gauss(0, 0.005)),
        })
    return out
