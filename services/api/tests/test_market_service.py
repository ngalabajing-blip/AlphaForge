from datetime import UTC, datetime, timedelta

import pytest
from alphaforge_api.services.market_service import MarketService
from alphaforge_shared.symbols import parse_symbol


@pytest.mark.asyncio
async def test_latest_price_is_positive():
    svc = MarketService()
    p = await svc.latest(parse_symbol("ETH/USDC"))
    assert float(p.price) > 0


@pytest.mark.asyncio
async def test_candles_emit_requested_count():
    svc = MarketService()
    end = datetime.now(tz=UTC)
    start = end - timedelta(hours=10)
    rows = await svc.candles(parse_symbol("BTC/USDT"), timeframe="1h", start=start, end=end, limit=10)
    assert 1 <= len(rows) <= 10
    for r in rows:
        assert r["high"] >= r["low"]
        assert r["volume"] >= 0


@pytest.mark.asyncio
async def test_orderbook_shape():
    svc = MarketService()
    book = await svc.orderbook_snapshot(parse_symbol("ETH/USDT"), depth=5)
    assert len(book["bids"]) == 5 and len(book["asks"]) == 5
    assert all(b[0] < a[0] for b, a in zip(book["bids"], book["asks"]))


@pytest.mark.asyncio
async def test_dominance_sums_to_one():
    svc = MarketService()
    dom = await svc.dominance(quote="USDT")
    assert abs(sum(dom.values()) - 1.0) < 1e-3
