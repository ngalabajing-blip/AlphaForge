"""
Locust scenario for AlphaForge.

Targets the dev compose at http://localhost:8000 by default. Override
with `--host`. Authenticates once per user, then exercises the read
heavy endpoints.
"""
from __future__ import annotations

import random

from locust import HttpUser, between, task


SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "AVAX/USDT", "ARB/USDT"]


class AlphaForgeUser(HttpUser):
    wait_time = between(0.5, 2.0)

    def on_start(self) -> None:
        resp = self.client.post(
            "/api/v1/auth/token",
            data={"username": "admin@alphaforge.local", "password": "changeme"},
        )
        if resp.status_code == 200:
            self.token = resp.json()["access_token"]
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            self.token = None

    @task(5)
    def fetch_ticker(self) -> None:
        sym = random.choice(SYMBOLS)
        self.client.get(f"/api/v1/market/ticker/{sym}")

    @task(3)
    def fetch_candles(self) -> None:
        sym = random.choice(SYMBOLS)
        self.client.get(f"/api/v1/market/candles/{sym}", params={"timeframe": "1h", "limit": 200})

    @task(2)
    def list_strategies(self) -> None:
        self.client.get("/api/v1/strategies", params={"limit": 50})

    @task(2)
    def list_signals(self) -> None:
        self.client.get("/api/v1/signals", params={"limit": 100})

    @task(1)
    def list_audits(self) -> None:
        self.client.get("/api/v1/audits", params={"limit": 25})

    @task(1)
    def dominance(self) -> None:
        self.client.get("/api/v1/market/dominance")

    @task(1)
    def movers(self) -> None:
        self.client.get("/api/v1/market/movers", params={"n": 10})
