"""Vercel serverless entrypoint for AlphaForge ML service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

app = FastAPI(title="AlphaForge ML", version="0.1.0", default_response_class=ORJSONResponse)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/")
async def root():
    return {"service": "ml", "status": "running (serverless mode)", "capabilities": ["anomaly", "sentiment", "features"]}


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/api/v1/ml/anomaly/score")
async def anomaly_score(body: dict):
    """Score a feature vector for anomalies."""
    from alphaforge_ml.models.anomaly import AnomalyDetector
    vector = body.get("vector", [])
    history = body.get("history")
    detector = AnomalyDetector()
    if history:
        detector.fit(history)
    result = detector.score(vector, history=history)
    return {"score": result.score, "is_anomaly": result.is_anomaly, "explanations": result.explanations}


@app.post("/api/v1/ml/sentiment/analyze")
async def sentiment_analyze(body: dict):
    """Analyze text sentiment."""
    from alphaforge_ml.models.sentiment import SentimentAnalyser
    text = body.get("text", "")
    analyser = SentimentAnalyser()
    result = analyser.analyse(text)
    return {"score": result.score, "label": result.label, "confidence": result.confidence, "matched_terms": result.matched_terms}


@app.post("/api/v1/ml/features/trades")
async def extract_trade_features(body: dict):
    """Extract features from trade data."""
    from alphaforge_ml.features.extractors import extract_trade_window
    trades = body.get("trades", [])
    result = extract_trade_window(trades)
    return result


@app.post("/api/v1/ml/features/candles")
async def extract_candle_features(body: dict):
    """Extract features from candle data."""
    from alphaforge_ml.features.extractors import extract_candle_features
    candles = body.get("candles", [])
    result = extract_candle_features(candles)
    return {"features": result}
