"""Vercel serverless entrypoint for AlphaForge Notifier service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

app = FastAPI(title="AlphaForge Notifier", version="0.1.0", default_response_class=ORJSONResponse)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/")
async def root():
    return {"service": "notifier", "status": "running (serverless mode)", "channels": ["webhook", "telegram", "discord", "slack", "email", "pagerduty"]}


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/api/v1/notifier/dispatch")
async def dispatch_alert(body: dict):
    """Dispatch a notification alert."""
    from alphaforge_notifier.dispatcher import NotifierDispatcher
    dispatcher = NotifierDispatcher()
    await dispatcher.start()
    try:
        results = await dispatcher.dispatch(body)
        return {"results": [{"channel": r.channel, "status": r.status, "error": r.error} for r in results]}
    finally:
        await dispatcher.stop()


@app.get("/api/v1/notifier/templates")
async def list_templates():
    """List available notification templates."""
    return {
        "templates": [
            {"name": "alert", "description": "Default alert notification"},
            {"name": "signal", "description": "Trading signal notification"},
            {"name": "anomaly", "description": "Anomaly detection alert"},
            {"name": "audit", "description": "Smart contract audit result"},
        ]
    }
