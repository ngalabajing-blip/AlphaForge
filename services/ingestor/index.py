"""Vercel serverless entrypoint for AlphaForge Ingestor service.

ingestor
This service cannot run on Vercel's serverless platform.
Deploy the full stack on a VPS or Kubernetes for this functionality.
"""

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(title="AlphaForge Ingestor", version="0.1.0", default_response_class=ORJSONResponse)


@app.get("/")
async def root():
    return {
        "service": "ingestor",
        "status": "unavailable",
        "reason": "Blockchain WebSocket listener — requires persistent connections. Cannot run on Vercel serverless.",
    }


@app.get("/healthz")
async def healthz():
    return {"status": "unavailable", "service": "ingestor"}
