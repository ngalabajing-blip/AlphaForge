#!/usr/bin/env python3
"""
Emit synthetic Kafka events to drive the rest of the stack during a
local dev session. Useful when you want to see anomalies, signals, and
notifications light up without wiring real RPC endpoints.
"""
from __future__ import annotations

import asyncio
import math
import os
import random
import sys
import time
from datetime import datetime, timezone

import orjson


async def main() -> None:
    try:
        from aiokafka import AIOKafkaProducer
    except ImportError:
        print("aiokafka not installed", file=sys.stderr)
        return

    bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap)
    await producer.start()
    try:
        symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "AVAX/USDT"]
        prices = {s: random.uniform(0.5, 50_000) for s in symbols}
        i = 0
        while True:
            for s in symbols:
                drift = math.sin(i / 24) * 0.002
                shock = random.gauss(0, 0.005)
                prices[s] *= max(0.001, 1 + drift + shock)
                payload = {
                    "symbol": s,
                    "price": round(prices[s], 4),
                    "ts": datetime.now(tz=timezone.utc).isoformat(),
                }
                await producer.send_and_wait("T_PRICES", orjson.dumps(payload))
                if random.random() < 0.05:
                    score = random.uniform(0.85, 0.99)
                    anomaly = {
                        "symbol": s,
                        "score": round(score, 3),
                        "factors": ["volume_spike", "volatility"],
                        "ts": payload["ts"],
                    }
                    await producer.send_and_wait("T_ANOMALY", orjson.dumps(anomaly))
                    if score > 0.92:
                        await producer.send_and_wait("T_ALERTS", orjson.dumps({
                            "rule_id": f"{s}-anomaly",
                            "severity": "high",
                            "channels": ["webhook"],
                            "payload": anomaly,
                        }))
            i += 1
            await asyncio.sleep(0.5)
    finally:
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(main())
