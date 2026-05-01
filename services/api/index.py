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

# Market endpoints that frontend expects
@app.get("/market/ticker/{symbol:path}")
async def market_ticker(symbol: str):
    base_prices = {"BTC/USDT": 67500, "ETH/USDT": 3450, "SOL/USDT": 145, "BNB/USDT": 580, "ARB/USDT": 1.15}
    price = base_prices.get(symbol, 100.0)
    return {"symbol": symbol, "price": str(round(price * random.uniform(0.98, 1.02), 2)), "ts": datetime.now(tz=UTC).isoformat()}

@app.get("/market/candles/{symbol:path}")
async def market_candles(symbol: str, timeframe: str = "1h", limit: int = 96):
    base = {"ETH/USDT": 3450}.get(symbol, 100.0)
    candles = []
    for i in range(limit):
        close = base * random.uniform(0.95, 1.05)
        candles.append({"ts": f"2026-05-01T{i%24:02d}:00:00", "close": str(round(close, 2))})
    return {"candles": candles}

@app.get("/market/dominance")
async def market_dominance():
    return {"quote": "USDT", "values": {"BTC": 52.3, "ETH": 17.8, "SOL": 3.2, "BNB": 2.8, "Others": 23.9}}

@app.get("/market/movers")
async def market_movers(direction: str = "up", n: int = 8):
    movers = [
        {"symbol": "SOL/USDT", "price": "148.50", "change_pct": 5.2},
        {"symbol": "ARB/USDT", "price": "1.18", "change_pct": 3.8},
        {"symbol": "ETH/USDT", "price": "3480.00", "change_pct": 2.1},
        {"symbol": "BTC/USDT", "price": "68200.00", "change_pct": 1.5},
        {"symbol": "BNB/USDT", "price": "585.00", "change_pct": 1.2},
    ]
    return {"direction": direction, "movers": movers[:n]}

@app.get("/market/latest")
async def market_latest():
    return {"symbol": "ETH/USDT", "price": 3450.0, "change_24h": 2.1, "volume": 15000000000}

# Other endpoints
@app.get("/chains")
async def list_chains():
    return {"chains": [
        {"id": "eth", "name": "Ethereum", "type": "evm", "chain_id": 1},
        {"id": "bsc", "name": "BNB Chain", "type": "evm", "chain_id": 56},
        {"id": "polygon", "name": "Polygon", "type": "evm", "chain_id": 137},
        {"id": "arbitrum", "name": "Arbitrum", "type": "evm", "chain_id": 42161},
        {"id": "base", "name": "Base", "type": "evm", "chain_id": 8453},
        {"id": "solana", "name": "Solana", "type": "solana"},
    ]}

@app.get("/strategies")
async def list_strategies():
    return {"strategies": [], "total": 0}

@app.get("/signals")
async def list_signals():
    return {"signals": [], "total": 0}

@app.get("/backtests")
async def list_backtests():
    return {"backtests": [], "total": 0}

@app.get("/alerts")
async def list_alerts():
    return {"alerts": [], "total": 0}

@app.get("/audits")
async def list_audits(limit: int = 5):
    return {"items": [], "total": 0}

@app.get("/users/me")
async def users_me():
    return {"id": "demo-user", "email": "demo@alphaforge.io", "full_name": "Demo User", "role": "admin"}

@app.post("/auth/token")
async def auth_token():
    return {"access_token": "demo-serverless-token", "token_type": "bearer", "refresh_token": "demo-refresh"}
