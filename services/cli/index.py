"""Vercel serverless entrypoint for AlphaForge Cli service.

cli
This service cannot run on Vercel's serverless platform.
Deploy the full stack on a VPS or Kubernetes for this functionality.
"""

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(title="AlphaForge Cli", version="0.1.0", default_response_class=ORJSONResponse)


@app.get("/")
async def root():
    return {
        "service": "cli",
        "status": "unavailable",
        "reason": "Command-line interface tool — not an HTTP service.",
    }


@app.get("/healthz")
async def healthz():
    return {"status": "unavailable", "service": "cli"}
