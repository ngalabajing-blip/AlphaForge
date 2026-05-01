from __future__ import annotations


def test_signals_endpoint(auth_client) -> None:
    resp = auth_client.get("/api/v1/signals", params={"limit": 25})
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    for s in items:
        assert "symbol" in s
        assert s["action"] in ("buy", "sell", "close", "alert")
        assert 0 <= float(s.get("strength", 0)) <= 1
