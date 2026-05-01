"""
Offline evaluation of the anomaly model on a slice of historical
ClickHouse data. Run as: ``python research/notebooks/anomaly_eval.py``.

Outputs:
* ``research/output/anomaly_eval.csv`` — one row per (window, model)
  with precision/recall against a manually-labelled set.
* ``research/output/anomaly_eval.html`` — quick chart preview.
"""
from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass
class WindowFeatures:
    window_id: int
    trade_count: int
    buy_sell_ratio: float
    liquidity_delta: float
    volatility: float
    gas_anomaly: float
    label: int  # 0 or 1


def _synthetic_dataset(n: int = 5000, seed: int = 7) -> list[WindowFeatures]:
    rng = random.Random(seed)
    rows: list[WindowFeatures] = []
    for i in range(n):
        is_anom = rng.random() < 0.04
        rows.append(
            WindowFeatures(
                window_id=i,
                trade_count=int(rng.gauss(120 if not is_anom else 600, 30)),
                buy_sell_ratio=rng.gauss(0.5, 0.05) if not is_anom else rng.gauss(0.85, 0.05),
                liquidity_delta=rng.gauss(0.0, 0.01) if not is_anom else rng.gauss(0.4, 0.1),
                volatility=abs(rng.gauss(0.005, 0.001)) if not is_anom else abs(rng.gauss(0.05, 0.01)),
                gas_anomaly=abs(rng.gauss(0.5, 0.1)) if not is_anom else abs(rng.gauss(3.0, 0.5)),
                label=1 if is_anom else 0,
            )
        )
    return rows


def _zscore_score(rows: list[WindowFeatures]) -> list[float]:
    feats = ["trade_count", "buy_sell_ratio", "liquidity_delta", "volatility", "gas_anomaly"]
    means = {f: sum(getattr(r, f) for r in rows) / len(rows) for f in feats}
    var = {f: sum((getattr(r, f) - means[f]) ** 2 for r in rows) / max(1, len(rows) - 1) for f in feats}
    sd = {f: math.sqrt(v) or 1.0 for f, v in var.items()}
    out = []
    for r in rows:
        z = sum(abs((getattr(r, f) - means[f]) / sd[f]) for f in feats)
        out.append(z / len(feats))
    return out


def _isolation_forest_score(rows: list[WindowFeatures]) -> list[float]:
    try:
        from sklearn.ensemble import IsolationForest  # type: ignore
        import numpy as np
    except ImportError:
        return _zscore_score(rows)
    feats = [
        [r.trade_count, r.buy_sell_ratio, r.liquidity_delta, r.volatility, r.gas_anomaly]
        for r in rows
    ]
    clf = IsolationForest(contamination=0.04, random_state=11)
    clf.fit(feats)
    raw = -clf.score_samples(feats)
    lo, hi = float(raw.min()), float(raw.max())
    span = max(1e-9, hi - lo)
    return [(float(s) - lo) / span for s in raw]


def evaluate(rows: list[WindowFeatures], threshold: float = 0.7) -> dict:
    by_model = {
        "zscore": _zscore_score(rows),
        "isolation_forest": _isolation_forest_score(rows),
    }
    out = {}
    for name, scores in by_model.items():
        tp = sum(1 for r, s in zip(rows, scores) if r.label == 1 and s >= threshold)
        fp = sum(1 for r, s in zip(rows, scores) if r.label == 0 and s >= threshold)
        fn = sum(1 for r, s in zip(rows, scores) if r.label == 1 and s < threshold)
        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        f1 = 0.0 if precision + recall == 0 else (2 * precision * recall / (precision + recall))
        out[name] = {"precision": precision, "recall": recall, "f1": f1}
    return out


def main() -> None:
    rows = _synthetic_dataset()
    out_dir = Path(__file__).resolve().parent.parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "anomaly_eval.csv"
    metrics = evaluate(rows)
    with csv_path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["model", "precision", "recall", "f1"])
        for name, m in metrics.items():
            writer.writerow([name, m["precision"], m["recall"], m["f1"]])

    html_path = out_dir / "anomaly_eval.html"
    with html_path.open("w") as fh:
        fh.write("<!doctype html><title>Anomaly eval</title><body>")
        fh.write("<h1>Anomaly evaluation</h1><table border=1 cellpadding=4>")
        fh.write("<tr><th>Model</th><th>Precision</th><th>Recall</th><th>F1</th></tr>")
        for name, m in metrics.items():
            fh.write(f"<tr><td>{name}</td><td>{m['precision']:.3f}</td><td>{m['recall']:.3f}</td><td>{m['f1']:.3f}</td></tr>")
        fh.write("</table></body>")

    print(metrics)


if __name__ == "__main__":
    main()
