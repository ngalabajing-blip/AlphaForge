"""AlphaForge Cli — stub."""
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
app = FastAPI(title="AlphaForge Cli", version="0.1.0", default_response_class=ORJSONResponse)

@app.get("/")
async def root():
    return {"service": "cli", "status": "unavailable", "reason": "Command-line interface tool — not an HTTP service"}

@app.get("/healthz")
async def healthz():
    return {"status": "unavailable", "service": "cli"}
