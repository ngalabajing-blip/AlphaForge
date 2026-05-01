"""AlphaForge Quantcore — stub."""
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
app = FastAPI(title="AlphaForge Quantcore", version="0.1.0", default_response_class=ORJSONResponse)

@app.get("/")
async def root():
    return {"service": "quantcore", "status": "unavailable", "reason": "Rust native library — compiled extension"}

@app.get("/healthz")
async def healthz():
    return {"status": "unavailable", "service": "quantcore"}
