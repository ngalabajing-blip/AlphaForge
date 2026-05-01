"""Vercel serverless entrypoint for AlphaForge Worker service.

worker
This service cannot run on Vercel's serverless platform.
Deploy the full stack on a VPS or Kubernetes for this functionality.
"""

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(title="AlphaForge Worker", version="0.1.0", default_response_class=ORJSONResponse)


@app.get("/")
async def root():
    return {
        "service": "worker",
        "status": "unavailable",
        "reason": "Celery task queue — requires Redis broker. Cannot run on Vercel serverless.",
    }


@app.get("/healthz")
async def healthz():
    return {"status": "unavailable", "service": "worker"}
