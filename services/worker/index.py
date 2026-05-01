"""AlphaForge Worker — stub."""
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
app = FastAPI(title="AlphaForge Worker", version="0.1.0", default_response_class=ORJSONResponse)

@app.get("/")
async def root():
    return {"service": "worker", "status": "unavailable", "reason": "Celery task queue — requires Redis broker"}

@app.get("/healthz")
async def healthz():
    return {"status": "unavailable", "service": "worker"}
