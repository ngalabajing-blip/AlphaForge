"""
Anomaly detection model.

Uses a small unsupervised Isolation Forest to score per-window feature
vectors. When ``contamination`` is unknown, we fall back to a robust z-score
heuristic so the service can run even without scikit-learn installed.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Sequence
from dataclasses import dataclass

from alphaforge_ml.config import get_settings


@dataclass
class AnomalyScore:
    score: float  # 0..1, higher = more anomalous
    is_anomaly: bool
    explanations: list[str]


class AnomalyDetector:
    """Composite detector: Isolation Forest + z-score fallback."""

    def __init__(self) -> None:
        self.model = None
        self._sklearn_available = False
        try:
            from sklearn.ensemble import IsolationForest  # type: ignore[import-not-found]

            self.model = IsolationForest(
                contamination=get_settings().anomaly_contamination,
                n_estimators=128,
                random_state=42,
            )
            self._sklearn_available = True
        except ImportError:
            self.model = None

    def fit(self, vectors: Sequence[Sequence[float]]) -> None:
        if not self._sklearn_available or not vectors:
            return
        try:
            self.model.fit(vectors)  # type: ignore[union-attr]
        except Exception:
            pass

    def score(
        self,
        vector: Sequence[float],
        *,
        history: Sequence[Sequence[float]] | None = None,
    ) -> AnomalyScore:
        if self._sklearn_available and self.model is not None:
            try:
                # IsolationForest score: higher = normal, so invert
                raw = float(self.model.decision_function([list(vector)])[0])
                normalised = 1.0 / (1.0 + math.exp(raw))  # sigmoid → 0..1
                pred = self.model.predict([list(vector)])[0]
                return AnomalyScore(
                    score=round(normalised, 4),
                    is_anomaly=bool(pred == -1),
                    explanations=self._explain(vector, history or []),
                )
            except Exception:
                pass

        # Fallback: robust z-score
        return self._zscore_fallback(vector, history or [])

    @staticmethod
    def _zscore_fallback(vector: Sequence[float], history: Sequence[Sequence[float]]) -> AnomalyScore:
        if not history:
            return AnomalyScore(score=0.0, is_anomaly=False, explanations=["no_history"])
        zs: list[float] = []
        for i, v in enumerate(vector):
            col = [row[i] for row in history if len(row) > i]
            if len(col) < 5:
                continue
            mu = statistics.mean(col)
            sd = statistics.pstdev(col) or 1.0
            zs.append(abs((v - mu) / sd))
        if not zs:
            return AnomalyScore(score=0.0, is_anomaly=False, explanations=[])
        max_z = max(zs)
        score = min(1.0, max_z / 6.0)
        return AnomalyScore(
            score=round(score, 4),
            is_anomaly=score > 0.5,
            explanations=[f"z_max={max_z:.2f}"],
        )

    @staticmethod
    def _explain(vector: Sequence[float], history: Sequence[Sequence[float]]) -> list[str]:
        if not history:
            return []
        names = [
            "n_trades",
            "total_volume",
            "mean_size",
            "std_size",
            "max_size",
            "buy_ratio",
            "unique_addresses",
            "price_change_pct",
        ]
        notes: list[str] = []
        for i, v in enumerate(vector):
            col = [row[i] for row in history if len(row) > i]
            if not col:
                continue
            mu = statistics.mean(col)
            sd = statistics.pstdev(col) or 1.0
            z = (v - mu) / sd
            if abs(z) > 2.5 and i < len(names):
                notes.append(f"{names[i]} z={z:+.1f}")
        return notes[:5]
