import random

from alphaforge_ml.models.anomaly import AnomalyDetector


def test_zscore_no_history():
    score = AnomalyDetector._zscore_fallback([1, 2, 3], [])
    assert score.score == 0.0


def test_zscore_with_history():
    rng = random.Random(0)
    history = [[rng.gauss(0, 1) for _ in range(8)] for _ in range(50)]
    outlier = [10] * 8
    score = AnomalyDetector._zscore_fallback(outlier, history)
    assert score.score > 0.5


def test_detector_no_history():
    det = AnomalyDetector()
    s = det.score([1, 1, 1, 1, 1, 0.5, 1, 0])
    assert s.score >= 0.0
