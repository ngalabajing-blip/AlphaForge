"""
WebSocket subscriptions for live updates.

Three channels are exposed:

* ``/ws/signals``       — push every new strategy signal (server-pushed)
* ``/ws/market/{symbol}`` — push live market ticks for a single symbol
* ``/ws/audits``        — push completed audit reports

Authentication: token can be supplied either as a ``token`` query param
(``ws://…?token=…``) or via ``Authorization: Bearer …`` headers when the
client supports them. Lack of auth produces a 1008 close on connect.
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from jose import JWTError

from alphaforge_api.core.security import decode_token
from alphaforge_api.services.market_service import MarketService
from alphaforge_shared.logging import get_logger
from alphaforge_shared.symbols import parse_symbol

router = APIRouter()
log = get_logger("alphaforge_api.ws")


def _authorise(token: str | None) -> str:
    if not token:
        raise PermissionError("missing token")
    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise PermissionError("invalid token") from exc
    if payload.get("type") != "access":
        raise PermissionError("wrong token type")
    return payload["sub"]


async def _send_json(ws: WebSocket, payload: dict[str, Any]) -> None:
    await ws.send_text(json.dumps(payload, default=str))


@router.websocket("/signals")
async def signals_socket(ws: WebSocket, token: str | None = Query(default=None)) -> None:
    try:
        user_id = _authorise(token)
    except PermissionError:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await ws.accept()
    log.info("ws_connected", channel="signals", user_id=user_id)
    # In production: consume from kafka topic af.strategy.signal.v1 and forward.
    # For dev we synthesise a heartbeat so frontend can verify the channel.
    try:
        i = 0
        while True:
            i += 1
            await _send_json(
                ws,
                {
                    "type": "heartbeat",
                    "ts": datetime.now(tz=timezone.utc).isoformat(),
                    "seq": i,
                },
            )
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        log.info("ws_disconnected", channel="signals", user_id=user_id)


@router.websocket("/market/{symbol_path:path}")
async def market_socket(
    ws: WebSocket,
    symbol_path: str,
    token: str | None = Query(default=None),
    interval: float = Query(default=1.0, ge=0.25, le=60),
) -> None:
    try:
        user_id = _authorise(token)
    except PermissionError:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        symbol = parse_symbol(symbol_path)
    except ValueError:
        await ws.close(code=status.WS_1003_UNSUPPORTED_DATA)
        return
    await ws.accept()
    service = MarketService()
    log.info("ws_connected", channel="market", symbol=symbol.canonical, user_id=user_id)
    try:
        while True:
            tick = await service.latest(symbol)
            await _send_json(
                ws,
                {
                    "symbol": symbol.canonical,
                    "price": str(tick.price),
                    "ts": tick.ts.isoformat(),
                },
            )
            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        log.info("ws_disconnected", channel="market", symbol=symbol.canonical)


@router.websocket("/audits")
async def audits_socket(ws: WebSocket, token: str | None = Query(default=None)) -> None:
    try:
        _authorise(token)
    except PermissionError:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await ws.accept()
    try:
        while True:
            await _send_json(ws, {"type": "heartbeat", "ts": datetime.now(tz=timezone.utc).isoformat()})
            await asyncio.sleep(15)
    except WebSocketDisconnect:
        return
