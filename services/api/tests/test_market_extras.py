from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from alphaforge_api.services.market_service import MarketService
from alphaforge_shared.symbols import MarketSymbol


@pytest.fixture()
def market() -> MarketService:
    return MarketService()


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_latest_returns_recent_point(market: MarketService) -> None:
    sym = MarketSymbol("ETH", "USDT")
    point = _run(market.latest(sym))
    assert point.price > 0
    age = (datetime.now(tz=timezone.utc) - point.ts).total_seconds()
    assert abs(age) < 5


def test_candles_respect_limit(market: MarketService) -> None:
    sym = MarketSymbol("BTC", "USDT")
    end = datetime.now(tz=timezone.utc)
    start = end - timedelta(days=1)
    candles = _run(market.candles(sym, timeframe="1h", start=start, end=end, limit=12))
    assert 0 < len(candles) <= 12
    for c in candles:
        assert c["high"] >= c["low"]
        assert c["volume"] >= 0


def test_orderbook_has_bids_and_asks(market: MarketService) -> None:
    sym = MarketSymbol("SOL", "USDT")
    snap = _run(market.orderbook_snapshot(sym, depth=5))
    assert snap["symbol"] == "SOL/USDT"
    assert len(snap["bids"]) == 5
    assert len(snap["asks"]) == 5
    best_bid = snap["bids"][0][0]
    best_ask = snap["asks"][0][0]
    assert best_bid < best_ask


def test_dominance_weights_sum_close_to_one(market: MarketService) -> None:
    weights = _run(market.dominance(quote="USDT"))
    total = sum(weights.values())
    assert abs(total - 1.0) < 0.05


def test_top_movers_returns_n(market: MarketService) -> None:
    movers = _run(market.top_movers(n=5, direction="up"))
    assert len(movers) == 5
    sorted_changes = [m["change_24h"] for m in movers]
    assert sorted_changes == sorted(sorted_changes, reverse=True)
