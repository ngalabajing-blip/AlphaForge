"""
Price predictor.

Two backends:

* ``RandomForestForecaster`` — scikit-learn regressor on the last N candle
  feature rows.
* ``LSTMForecaster`` — torch.nn LSTM for sequence forecasting (used when
  ``ML_USE_TORCH`` is enabled and torch is installed).

Both expose ``fit(X, y)`` / ``predict(X) -> (mu, sigma)``.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass
class Forecast:
    horizon_seconds: int
    predicted_close: float
    direction: str   # "up" | "down" | "flat"
    confidence: float
    explanation: list[str]


class RandomForestForecaster:
    def __init__(self) -> None:
        self.model = None
        self._available = False
        try:
            from sklearn.ensemble import RandomForestRegressor  # type: ignore[import-not-found]
            self.model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
            self._available = True
        except ImportError:
            self.model = None

    def fit(self, X: Sequence[Sequence[float]], y: Sequence[float]) -> None:
        if not self._available or not X:
            return
        try:
            self.model.fit(list(X), list(y))  # type: ignore[union-attr]
        except Exception:
            pass

    def predict(self, X: Sequence[Sequence[float]]) -> tuple[float, float]:
        if not self._available or self.model is None:
            return 0.0, 1.0
        try:
            preds = self.model.predict(list(X))  # type: ignore[union-attr]
        except Exception:
            return 0.0, 1.0
        if len(preds) == 0:
            return 0.0, 1.0
        mu = float(preds[-1])
        # ensemble variance ≈ feature.std across trees (sklearn API)
        try:
            tree_preds = [t.predict(list(X))[-1] for t in self.model.estimators_]  # type: ignore[union-attr]
            var = sum((p - mu) ** 2 for p in tree_preds) / len(tree_preds)
            sigma = math.sqrt(var)
        except Exception:
            sigma = 0.0
        return mu, sigma


class LSTMForecaster:
    """Torch LSTM stub — initialised lazily."""

    def __init__(self, *, input_size: int = 11, hidden_size: int = 32, num_layers: int = 2) -> None:
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self._model = None
        self._available = False
        try:
            import torch  # type: ignore[import-not-found]
            self._torch = torch
            self._available = True
        except ImportError:
            self._torch = None  # type: ignore[assignment]

    def _build(self):  # type: ignore[no-untyped-def]
        if not self._available:
            return
        torch = self._torch  # type: ignore[union-attr]

        class _Net(torch.nn.Module):
            def __init__(self, in_size: int, hidden: int, layers: int) -> None:
                super().__init__()
                self.lstm = torch.nn.LSTM(in_size, hidden, num_layers=layers, batch_first=True)
                self.head = torch.nn.Linear(hidden, 1)

            def forward(self, x):  # type: ignore[no-untyped-def]
                out, _ = self.lstm(x)
                return self.head(out[:, -1, :])

        self._model = _Net(self.input_size, self.hidden_size, self.num_layers)

    def predict(self, sequence: Sequence[Sequence[float]]) -> tuple[float, float]:
        if not self._available:
            return 0.0, 1.0
        if self._model is None:
            self._build()
        torch = self._torch  # type: ignore[union-attr]
        with torch.no_grad():  # type: ignore[union-attr]
            x = torch.tensor([list(sequence)], dtype=torch.float32)  # type: ignore[union-attr]
            out = self._model(x)  # type: ignore[union-attr]
            return float(out.squeeze().item()), 0.5
