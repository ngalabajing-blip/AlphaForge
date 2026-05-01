"""AlphaForge Ingestor — stub."""
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
app = FastAPI(title="AlphaForge Ingestor", version="0.1.0", default_response_class=ORJSONResponse)

@app.get("/")
async def root():
    return {"service": "ingestor", "status": "unavailable", "reason": "Blockchain WebSocket listener — requires persistent connections"}

@app.get("/healthz")
async def healthz():
    return {"status": "unavailable", "service": "ingestor"}
