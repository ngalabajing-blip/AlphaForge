# Machine learning pipeline

The `ml/` service runs three independent inference loops, each backed by
a Kafka topic.

## 1. Anomaly detection

* **Window**: 5-minute tumbling, per-symbol
* **Features** (per window):
  * trade count, buy/sell ratio
  * net liquidity delta (token0 / token1)
  * price volatility (stdev / mean)
  * gas anomaly score (z-score against rolling 24h)
  * MEV-likeness signal (tx ordering ratio)
* **Models**: composite of
  * `sklearn.ensemble.IsolationForest` (contamination configurable
    via `ML_ANOMALY_CONTAMINATION`, default 0.02)
  * PCA-based autoencoder reconstruction error
  * rolling z-score (fallback when `sklearn` unavailable)
* **Output**: `T_ANOMALY` events with `score ∈ [0, 1]` + factor
  contributions.

## 2. Sentiment

* **Sources**: simulated chat / news snippets (real deployment plugs
  Twitter / Telegram / Reddit collectors via the ingestor service).
* **Backends** (selected via `ML_SENTIMENT_BACKEND`):
  * `lexicon` — VADER-style polarity scoring (no model dependencies)
  * `transformer` — distilbert classifier (loaded lazily)
* **Output**: `T_SENTIMENT` events with score in `[-1, 1]`.

## 3. Price prediction

* **Horizon**: configurable; default 1h ahead
* **Backends**:
  * `naive` — random walk + drift
  * `ridge` — ridge regression on rolling features (lag returns,
    volume z-score)
  * `lstm` — placeholder for a torch LSTM (loaded only when torch
    is available)
* **Output**: `T_PRICE_PREDICTION` events with `mu`, `sigma` and
  selected backend.

## Training & evaluation

Training is offline. Datasets come from the ClickHouse trade /
candle store; the `worker` service exposes Celery tasks
(`tasks.train_anomaly_model`, `tasks.train_forecaster`) that pickle
the trained estimator into S3 and then push a `T_MODEL_PROMOTION`
event the ML service consumes to swap models live.

## Metrics

* `alphaforge_ml_anomaly_score` (histogram)
* `alphaforge_ml_anomaly_inference_seconds` (summary)
* `alphaforge_ml_predictions_total{backend=…}` (counter)
* `alphaforge_ml_sentiment_score` (histogram)
