from __future__ import annotations


def test_ticker_returns_price(auth_client) -> None:
    resp = auth_client.get("/api/v1/market/ticker/ETH/USDT")
    assert resp.status_code == 200
    body = resp.json()
    assert "price" in body
    assert float(body["price"]) > 0


def test_candles_return_list(auth_client) -> None:
    resp = auth_client.get(
        "/api/v1/market/candles/ETH/USDT",
        params={"timeframe": "1h", "limit": 24},
    )
    assert resp.status_code == 200
    candles = resp.json()
    assert isinstance(candles, list)
    assert 0 < len(candles) <= 24
    for c in candles:
        assert c["high"] >= c["low"]
        assert c["volume"] >= 0


def test_dominance_sums_close_to_one(auth_client) -> None:
    resp = auth_client.get("/api/v1/market/dominance")
    assert resp.status_code == 200
    weights = resp.json()
    total = sum(weights.values())
    assert abs(total - 1.0) < 0.05


def test_movers(auth_client) -> None:
    resp = auth_client.get("/api/v1/market/movers", params={"n": 5, "direction": "up"})
    assert resp.status_code == 200
    movers = resp.json()
    assert len(movers) == 5
    deltas = [m["change_24h"] for m in movers]
    assert deltas == sorted(deltas, reverse=True)
