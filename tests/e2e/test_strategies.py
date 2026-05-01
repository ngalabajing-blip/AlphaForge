from __future__ import annotations

import pytest


DSL = """\
strategy: "e2e demo"
universe: { symbols: [ETH/USDT], timeframe: 1h }
indicators:
  - {name: ema, alias: fast, period: 12}
  - {name: ema, alias: slow, period: 26}
rules:
  - when: cross_up(fast, slow)
    then: buy
    size: 0.1
  - when: cross_down(fast, slow)
    then: close
"""


@pytest.fixture()
def strategy_id(auth_client) -> str:
    resp = auth_client.post(
        "/api/v1/strategies",
        json={
            "name": "e2e demo",
            "is_public": False,
            "raw_source": DSL,
            "parameters": {},
        },
    )
    assert resp.status_code in (200, 201), resp.text
    return resp.json()["id"]


def test_list_includes_strategy(auth_client, strategy_id: str) -> None:
    resp = auth_client.get("/api/v1/strategies", params={"limit": 100})
    assert resp.status_code == 200
    ids = [s["id"] for s in resp.json()["items"]]
    assert strategy_id in ids


def test_show_strategy(auth_client, strategy_id: str) -> None:
    resp = auth_client.get(f"/api/v1/strategies/{strategy_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "e2e demo"
    assert body["latest_version"]["version"] == 1


def test_publish_new_version(auth_client, strategy_id: str) -> None:
    resp = auth_client.post(
        f"/api/v1/strategies/{strategy_id}/versions",
        json={"raw_source": DSL.replace("0.1", "0.2"), "notes": "increase size"},
    )
    assert resp.status_code in (200, 201)
    assert resp.json()["version"] >= 2
