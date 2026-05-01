"""
Sentiment analyser.

By default uses a hand-curated lexicon (no external deps) so the service
remains useful in dev. When ``ML_SENTIMENT_BACKEND=transformer`` is set and
``transformers`` is installed, swaps in a fine-tuned sentiment model.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence


@dataclass
class SentimentResult:
    score: float        # -1.0 (very negative) .. 1.0 (very positive)
    label: str          # "negative" | "neutral" | "positive"
    confidence: float
    matched_terms: list[str]


_POSITIVE_TERMS = {
    "moon", "bullish", "pump", "rally", "ath", "breakout", "buy", "long", "accumulate",
    "support", "rebound", "rip", "rocket", "send it", "mooning", "soar",
}
_NEGATIVE_TERMS = {
    "rug", "dump", "scam", "bearish", "sell", "short", "exit liquidity", "rekt",
    "honeypot", "exit scam", "bear", "panic", "crash", "drain", "drop",
}
_INTENSIFIERS = {"very", "super", "extremely", "huge", "massive"}
_NEGATIONS = {"not", "no", "never", "nope"}


_TOKEN_RE = re.compile(r"[A-Za-z']+")


class LexiconSentiment:
    def predict(self, text: str) -> SentimentResult:
        if not text:
            return SentimentResult(0.0, "neutral", 0.0, [])
        tokens = [t.lower() for t in _TOKEN_RE.findall(text)]
        score = 0.0
        terms: list[str] = []
        for i, tok in enumerate(tokens):
            multiplier = 1.0
            if i > 0 and tokens[i - 1] in _INTENSIFIERS:
                multiplier *= 1.5
            if i > 0 and tokens[i - 1] in _NEGATIONS:
                multiplier *= -1.0
            if tok in _POSITIVE_TERMS:
                score += 1.0 * multiplier
                terms.append(tok)
            elif tok in _NEGATIVE_TERMS:
                score -= 1.0 * multiplier
                terms.append(tok)
        n = max(1, len(tokens))
        normalised = max(-1.0, min(1.0, score / max(2.0, n / 4)))
        label = "neutral"
        if normalised > 0.2:
            label = "positive"
        elif normalised < -0.2:
            label = "negative"
        return SentimentResult(
            score=round(normalised, 4),
            label=label,
            confidence=min(1.0, abs(normalised) * 1.2),
            matched_terms=terms[:8],
        )


class TransformerSentiment:
    """Lazy-loaded HuggingFace pipeline."""

    def __init__(self, *, max_length: int = 160) -> None:
        self.max_length = max_length
        self._pipe = None

    def _ensure_pipeline(self):  # type: ignore[no-untyped-def]
        if self._pipe is not None:
            return self._pipe
        try:
            from transformers import pipeline  # type: ignore[import-not-found]
        except ImportError:
            return None
        try:
            self._pipe = pipeline("sentiment-analysis", model="finiteautomata/bertweet-base-sentiment-analysis")
        except Exception:
            self._pipe = None
        return self._pipe

    def predict(self, text: str) -> SentimentResult:
        pipe = self._ensure_pipeline()
        if pipe is None:
            return LexiconSentiment().predict(text)
        out = pipe(text[: self.max_length])[0]
        label_raw = (out.get("label") or "neutral").lower()
        score_raw = float(out.get("score") or 0.0)
        sign = 1.0 if "pos" in label_raw else (-1.0 if "neg" in label_raw else 0.0)
        return SentimentResult(
            score=round(sign * score_raw, 4),
            label="positive" if sign > 0 else "negative" if sign < 0 else "neutral",
            confidence=round(score_raw, 4),
            matched_terms=[],
        )


def get_sentiment_model(backend: str):  # type: ignore[no-untyped-def]
    if backend == "transformer":
        return TransformerSentiment()
    return LexiconSentiment()
