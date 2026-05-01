"""AlphaForge ML — Vercel serverless."""
import math
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

app = FastAPI(title="AlphaForge ML", version="0.1.0", default_response_class=ORJSONResponse)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"service": "ml", "status": "running", "capabilities": ["anomaly", "sentiment"]}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/v1/ml/anomaly/score")
async def anomaly_score(body: dict):
    vector = body.get("vector", [])
    if not vector:
        return {"score": 0.0, "is_anomaly": False, "explanations": ["empty vector"]}
    mean = sum(vector) / len(vector)
    variance = sum((x - mean) ** 2 for x in vector) / len(vector) if len(vector) > 1 else 0
    std = math.sqrt(variance) if variance > 0 else 1
    z_scores = [(x - mean) / std for x in vector]
    max_z = max(abs(z) for z in z_scores)
    score = min(max_z / 3.0, 1.0)
    return {"score": round(score, 4), "is_anomaly": score > 0.7, "explanations": [f"max_z={max_z:.2f}"]}

_POSITIVE = {"moon", "bullish", "pump", "rally", "ath", "breakout", "buy", "long", "accumulate", "support", "rebound", "rip", "rocket", "soar"}
_NEGATIVE = {"rug", "dump", "scam", "bearish", "sell", "short", "rekt", "honeypot", "bear", "panic", "crash", "drain", "drop"}
_NEGATIONS = {"not", "no", "never"}

@app.post("/api/v1/ml/sentiment/analyze")
async def sentiment_analyze(body: dict):
    text = body.get("text", "").lower()
    words = set(re.findall(r"\w+", text))
    pos = words & _POSITIVE
    neg = words & _NEGATIVE
    has_negation = bool(words & _NEGATIONS)
    raw = len(pos) - len(neg)
    if has_negation:
        raw = -raw
    total = len(pos) + len(neg)
    score = max(-1.0, min(1.0, raw / max(total, 1)))
    label = "positive" if score > 0.1 else "negative" if score < -0.1 else "neutral"
    return {"score": round(score, 4), "label": label, "confidence": min(total / 5.0, 1.0), "matched_terms": list(pos | neg)}
