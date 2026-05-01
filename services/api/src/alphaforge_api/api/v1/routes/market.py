from __future__ import annotations

from datetime import UTC, datetime, timedelta

from alphaforge_shared.symbols import parse_symbol
from fastapi import APIRouter, Depends, HTTPException, Query

from alphaforge_api.core.security import CurrentUser, get_current_user
from alphaforge_api.services.market_service import MarketService

router = APIRouter(prefix="/market")


@router.get("/price")
async def latest_price(
    symbol: str = Query(..., examples=["ETH/USDC"]),
    _: CurrentUser = Depends(get_current_user),
) -> dict:
    try:
        sym = parse_symbol(symbol)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    service = MarketService()
    price = await service.latest(sym)
    return {
        "symbol": sym.canonical,
        "price": str(price.price),
        "ts": price.ts.isoformat(),
    }


@router.get("/candles")
async def candles(
    symbol: str = Query(..., examples=["ETH/USDC"]),
    timeframe: str = Query("1h"),
    since: datetime | None = None,
    limit: int = Query(default=200, ge=1, le=2000),
    _: CurrentUser = Depends(get_current_user),
) -> list[dict]:
    sym = parse_symbol(symbol)
    service = MarketService()
    end = datetime.now(tz=UTC)
    start = since or (end - timedelta(days=30))
    return await service.candles(sym, timeframe=timeframe, start=start, end=end, limit=limit)


@router.get("/orderbook")
async def orderbook(
    symbol: str = Query(...),
    depth: int = Query(default=20, ge=1, le=200),
    _: CurrentUser = Depends(get_current_user),
) -> dict:
    sym = parse_symbol(symbol)
    service = MarketService()
    return await service.orderbook_snapshot(sym, depth=depth)


@router.get("/dominance")
async def dominance(
    quote: str = "USDT",
    _: CurrentUser = Depends(get_current_user),
) -> dict[str, float]:
    service = MarketService()
    return await service.dominance(quote=quote)


@router.get("/movers")
async def movers(
    n: int = Query(default=10, ge=1, le=100),
    direction: str = Query(default="up", pattern="^(up|down)$"),
    _: CurrentUser = Depends(get_current_user),
) -> list[dict]:
    service = MarketService()
    return await service.top_movers(n=n, direction=direction)
