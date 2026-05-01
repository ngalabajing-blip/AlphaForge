import asyncio

import pytest

from alphaforge_notifier.dispatcher import NotifierDispatcher


@pytest.mark.asyncio
async def test_dedup_blocks_duplicates():
    d = NotifierDispatcher()
    await d.start()
    try:
        alert = {"alert_id": "x", "rule_type": "anomaly", "symbol": "ETH",
                 "payload": {"digest": "y"}, "channels": ["webhook"], "owner_id": "u1"}
        first = await d.dispatch(alert)
        second = await d.dispatch(alert)
        assert any(r.channel != "dedup" for r in first)
        assert any(r.channel == "dedup" for r in second)
    finally:
        await d.stop()


@pytest.mark.asyncio
async def test_rate_limiter():
    d = NotifierDispatcher()
    await d.start()
    try:
        # Exceed the per-minute budget by sending 200 alerts
        alerts = [{"alert_id": str(i), "rule_type": "x", "symbol": "Y",
                   "payload": {"digest": str(i)}, "channels": ["webhook"], "owner_id": "u1"}
                  for i in range(200)]
        rate_limited = 0
        for a in alerts:
            res = await d.dispatch(a)
            if any(r.channel == "rate_limit" for r in res):
                rate_limited += 1
        assert rate_limited > 0
    finally:
        await d.stop()
