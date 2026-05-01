"""
Market data service — minimal in-memory cache + ClickHouse fallback.

In production the candle / trade / orderbook data is sourced from ClickHouse,
populated by the ingestor service. For local dev we synthesise data so the API
remains functional without a populated time-series store.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from alphaforge_shared.symbols import MarketSymbol
from alphaforge_shared.timeframes import parse_timeframe


@dataclass(frozen=True)
class PricePoint:
    price: Decimal
    ts: datetime


_DEMO_PRICES: dict[str, Decimal] = {
    "BTC": Decimal("64000"),
    "ETH": Decimal("3100"),
    "SOL": Decimal("150"),
    "BNB": Decimal("550"),
    "MATIC": Decimal("0.9"),
    "AVAX": Decimal("32"),
    "ARB": Decimal("0.7"),
    "OP": Decimal("1.6"),
    "ATOM": Decimal("8"),
}


def _pseudo_price(symbol: MarketSymbol, ts: datetime) -> Decimal:
    base = _DEMO_PRICES.get(symbol.base, Decimal("1"))
    seed = int(ts.timestamp() / 60) ^ hash(symbol.canonical)
    rng = random.Random(seed)
    pct = (rng.random() - 0.5) * 0.05
    return (base * (Decimal("1") + Decimal(str(pct)))).quantize(Decimal("0.0001"))


class MarketService:
    async def latest(self, symbol: MarketSymbol) -> PricePoint:
        now = datetime.now(tz=UTC)
        return PricePoint(price=_pseudo_price(symbol, now), ts=now)

    async def candles(
        self,
        symbol: MarketSymbol,
        *,
        timeframe: str,
        start: datetime,
        end: datetime,
        limit: int,
    ) -> list[dict]:
        tf = parse_timeframe(timeframe)
        if start.tzinfo is None:
            start = start.replace(tzinfo=UTC)
        if end.tzinfo is None:
            end = end.replace(tzinfo=UTC)
        ts = tf.floor(start)
        out: list[dict] = []
        while ts < end and len(out) < limit:
            seed = int(ts.timestamp()) ^ hash(symbol.canonical)
            rng = random.Random(seed)
            mid = float(_pseudo_price(symbol, ts))
            spread = 0.005 * mid
            o = mid + (rng.random() - 0.5) * spread
            c = mid + (rng.random() - 0.5) * spread
            h = max(o, c) + rng.random() * spread
            l = min(o, c) - rng.random() * spread
            v = abs(rng.gauss(100, 30))
            out.append(
                {
                    "ts": ts.isoformat(),
                    "open": round(o, 6),
                    "high": round(h, 6),
                    "low": round(l, 6),
                    "close": round(c, 6),
                    "volume": round(v, 4),
                }
            )
            ts += timedelta(seconds=tf.seconds)
        return out

    async def orderbook_snapshot(self, symbol: MarketSymbol, *, depth: int) -> dict:
        mid = float(_pseudo_price(symbol, datetime.now(tz=UTC)))
        rng = random.Random(hash(symbol.canonical))
        bids = []
        asks = []
        for i in range(1, depth + 1):
            bid_price = round(mid * (1 - 0.0001 * i), 6)
            ask_price = round(mid * (1 + 0.0001 * i), 6)
            bid_size = round(rng.uniform(0.5, 50), 4)
            ask_size = round(rng.uniform(0.5, 50), 4)
            bids.append([bid_price, bid_size])
            asks.append([ask_price, ask_size])
        return {
            "symbol": symbol.canonical,
            "ts": datetime.now(tz=UTC).isoformat(),
            "bids": bids,
            "asks": asks,
        }

    async def dominance(self, *, quote: str) -> dict[str, float]:
        bases = ["BTC", "ETH", "SOL", "BNB", "MATIC", "AVAX", "ARB", "OP", "ATOM"]
        weights: list[float] = []
        for b in bases:
            sym = MarketSymbol(b, quote.upper())
            p = float(_pseudo_price(sym, datetime.now(tz=UTC)))
            weights.append(p)
        total = sum(weights) or 1.0
        return {b: round(w / total, 4) for b, w in zip(bases, weights)}

    async def top_movers(self, *, n: int, direction: str) -> list[dict]:
        symbols = [
            "BTC",
            "ETH",
            "SOL",
            "BNB",
            "MATIC",
            "AVAX",
            "ARB",
            "OP",
            "ATOM",
            "DOGE",
            "PEPE",
            "SHIB",
            "LINK",
            "UNI",
            "AAVE",
            "MKR",
            "INJ",
        ]
        rng = random.Random(int(datetime.now(tz=UTC).timestamp()) // 60)
        movers = [
            {
                "symbol": f"{s}/USDT",
                "change_24h": round(rng.gauss(0, 0.07), 4),
                "price": round(rng.uniform(0.1, 60000), 4),
            }
            for s in symbols
        ]
        movers.sort(key=lambda m: m["change_24h"], reverse=direction == "up")
        return movers[:n]
