"""
Tiny PCA-based autoencoder fallback.

When PyTorch is available we'd swap in an actual MLP autoencoder; for the
default install we provide a numpy-only PCA reconstruction error scorer.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class ReconstructionScore:
    score: float
    error: float


class PCAReconstruction:
    def __init__(self, *, n_components: int = 4) -> None:
        self.n_components = n_components
        self._mean: list[float] | None = None
        self._components: list[list[float]] | None = None

    def fit(self, vectors: Sequence[Sequence[float]]) -> None:
        try:
            import numpy as np  # type: ignore[import-not-found]
        except ImportError:
            return
        X = np.array([list(v) for v in vectors], dtype=float)
        if X.size == 0:
            return
        mean = X.mean(axis=0)
        Xc = X - mean
        u, s, vt = np.linalg.svd(Xc, full_matrices=False)
        comps = vt[: self.n_components].tolist()
        self._mean = mean.tolist()
        self._components = comps

    def score(self, vector: Sequence[float]) -> ReconstructionScore:
        if self._mean is None or self._components is None:
            return ReconstructionScore(0.0, 0.0)
        try:
            import numpy as np  # type: ignore[import-not-found]
        except ImportError:
            return ReconstructionScore(0.0, 0.0)
        v = np.array(list(vector), dtype=float) - np.array(self._mean)
        comps = np.array(self._components)
        proj = comps @ v
        recon = comps.T @ proj
        err = float(np.linalg.norm(v - recon))
        score = 1.0 - math.exp(-err)
        return ReconstructionScore(score=round(score, 4), error=round(err, 6))
