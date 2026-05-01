"""AlphaForge API - Vercel serverless."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from datetime import UTC, datetime
import random

app = FastAPI(title="AlphaForge API", version="0.1.0", default_response_class=ORJSONResponse)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"name": "AlphaForge API", "version": "0.1.0", "status": "running"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "time": datetime.now(tz=UTC).isoformat()}

# Market
@app.get("/market/ticker/{symbol:path}")
async def market_ticker(symbol: str):
    prices = {"BTC/USDT": 67500, "ETH/USDT": 3450, "SOL/USDT": 145, "BNB/USDT": 580, "ARB/USDT": 1.15}
    price = prices.get(symbol, 100.0)
    return {"symbol": symbol, "price": str(round(price * random.uniform(0.98, 1.02), 2)), "ts": datetime.now(tz=UTC).isoformat()}

@app.get("/market/candles/{symbol:path}")
async def market_candles(symbol: str, timeframe: str = "1h", limit: int = 96):
    base = {"ETH/USDT": 3450}.get(symbol, 100.0)
    return {"candles": [{"ts": f"2026-05-01T{i%24:02d}:00:00", "close": str(round(base * random.uniform(0.95, 1.05), 2))} for i in range(limit)]}

@app.get("/market/dominance")
async def market_dominance():
    return {"quote": "USDT", "values": {"BTC": 0.523, "ETH": 0.178, "SOL": 0.032, "BNB": 0.028, "Others": 0.239}}

@app.get("/market/movers")
async def market_movers(direction: str = "up", n: int = 8):
    movers = [
        {"symbol": "SOL/USDT", "price": "148.50", "change_pct": 0.052},
        {"symbol": "ARB/USDT", "price": "1.18", "change_pct": 0.038},
        {"symbol": "ETH/USDT", "price": "3480.00", "change_pct": 0.021},
        {"symbol": "BTC/USDT", "price": "68200.00", "change_pct": 0.015},
        {"symbol": "BNB/USDT", "price": "585.00", "change_pct": 0.012},
    ]
    return {"direction": direction, "movers": movers[:n]}

# All list endpoints return {items: [...], total: N} format
@app.get("/strategies")
async def list_strategies(limit: int = 200):
    return {"items": [], "total": 0}

@app.get("/signals")
async def list_signals(limit: int = 200):
    return {"items": [], "total": 0}

@app.get("/backtests")
async def list_backtests(limit: int = 200):
    return {"items": [], "total": 0}

@app.get("/backtests/{backtest_id}")
async def get_backtest(backtest_id: str):
    return {"id": backtest_id, "status": "demo", "strategy_id": "demo", "strategy_version": 1,
            "start_at": "2026-01-01", "end_at": "2026-04-01", "initial_balance": "10000",
            "trades": [], "created_at": datetime.now(tz=UTC).isoformat()}

@app.get("/alerts")
async def list_alerts(limit: int = 200):
    return {"items": [], "total": 0}

@app.get("/audits")
async def list_audits(limit: int = 200):
    return {"items": [], "total": 0}

@app.post("/audits")
async def create_audit(body: dict):
    return {"id": "demo-audit", "status": "queued", "chain": body.get("chain", "eth"), "address": body.get("address", "")}

@app.get("/audits/{audit_id}")
async def get_audit(audit_id: str):
    return {"id": audit_id, "chain": "eth", "address": "0x0000...0000", "status": "completed",
            "risk_score": 0, "risk_level": "low", "findings": [], "created_at": datetime.now(tz=UTC).isoformat()}

@app.get("/users")
async def list_users(limit: int = 200):
    return {"items": [{"id": "demo-user", "email": "demo@alphaforge.io", "full_name": "Demo User",
            "role": "admin", "is_active": True, "created_at": datetime.now(tz=UTC).isoformat()}], "total": 1}

@app.get("/users/me")
async def users_me():
    return {"id": "demo-user", "email": "demo@alphaforge.io", "full_name": "Demo User", "role": "admin"}

@app.post("/auth/token")
async def auth_token():
    return {"access_token": "demo-token", "token_type": "bearer", "refresh_token": "demo-refresh"}

@app.get("/api-keys")
async def list_api_keys():
    return []

@app.post("/api-keys")
async def create_api_key(body: dict):
    return {"id": "key-1", "label": body.get("label", "default"), "scopes": ["read"], "token": "demo-api-key-token", "created_at": datetime.now(tz=UTC).isoformat()}

@app.get("/chains")
async def list_chains():
    return {"chains": [
        {"id": "eth", "name": "Ethereum", "type": "evm", "chain_id": 1},
        {"id": "bsc", "name": "BNB Chain", "type": "evm", "chain_id": 56},
        {"id": "solana", "name": "Solana", "type": "solana"},
    ]}
