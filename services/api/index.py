"""AlphaForge API — Vercel serverless."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from datetime import UTC, datetime

app = FastAPI(title="AlphaForge API", version="0.1.0", default_response_class=ORJSONResponse)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"name": "AlphaForge API", "version": "0.1.0", "status": "running"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "time": datetime.now(tz=UTC).isoformat()}

@app.get("/api/v1/chains")
async def list_chains():
    return {"chains": [
        {"id": "eth", "name": "Ethereum", "type": "evm", "chain_id": 1},
        {"id": "bsc", "name": "BNB Chain", "type": "evm", "chain_id": 56},
        {"id": "polygon", "name": "Polygon", "type": "evm", "chain_id": 137},
        {"id": "arbitrum", "name": "Arbitrum", "type": "evm", "chain_id": 42161},
        {"id": "base", "name": "Base", "type": "evm", "chain_id": 8453},
        {"id": "optimism", "name": "Optimism", "type": "evm", "chain_id": 10},
        {"id": "avalanche", "name": "Avalanche", "type": "evm", "chain_id": 43114},
        {"id": "solana", "name": "Solana", "type": "solana"},
        {"id": "cosmos", "name": "Cosmos", "type": "cosmos"},
    ]}

@app.get("/api/v1/strategies")
async def list_strategies():
    return {"strategies": [], "total": 0}

@app.get("/api/v1/signals")
async def list_signals():
    return {"signals": [], "total": 0}

@app.get("/api/v1/backtests")
async def list_backtests():
    return {"backtests": [], "total": 0}

@app.get("/api/v1/alerts")
async def list_alerts():
    return {"alerts": [], "total": 0}

@app.get("/api/v1/audits")
async def list_audits():
    return {"audits": [], "total": 0}

@app.get("/api/v1/market/latest")
async def market_latest():
    return {"symbol": "ETH/USD", "price": 0.0, "change_24h": 0.0, "volume": 0.0}

@app.get("/api/v1/market/candles")
async def market_candles():
    return {"symbol": "ETH/USD", "interval": "1h", "candles": []}

@app.get("/api/v1/market/orderbook")
async def market_orderbook():
    return {"symbol": "ETH/USD", "bids": [], "asks": []}

@app.post("/api/v1/auth/login")
async def login():
    return {"error": "Auth requires full backend deployment"}
