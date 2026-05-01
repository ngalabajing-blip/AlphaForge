"""AlphaForge Notifier — Vercel serverless."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

app = FastAPI(title="AlphaForge Notifier", version="0.1.0", default_response_class=ORJSONResponse)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"service": "notifier", "status": "running", "channels": ["webhook", "telegram", "discord", "slack"]}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/v1/notifier/dispatch")
async def dispatch(body: dict):
    channels = body.get("channels", ["webhook"])
    message = body.get("message", "")
    return {"dispatched": [{"channel": c, "status": "simulated", "message": message[:100]} for c in channels]}

@app.get("/api/v1/notifier/templates")
async def list_templates():
    return {"templates": ["alert", "signal", "anomaly", "audit"]}
