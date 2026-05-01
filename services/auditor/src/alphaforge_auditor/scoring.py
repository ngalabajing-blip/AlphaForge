"""Aggregate findings into a risk score."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

SEVERITY_WEIGHTS = {
    "info": 0,
    "low": 5,
    "medium": 15,
    "high": 35,
    "critical": 60,
}


@dataclass
class ScoredReport:
    risk_score: int
    risk_level: str
    summary: str


def score_findings(findings: Sequence[dict]) -> ScoredReport:
    score = 0
    for f in findings:
        score += SEVERITY_WEIGHTS.get(f.get("severity", "info"), 0)
    score = min(100, score)

    if score >= 80:
        level = "critical"
    elif score >= 50:
        level = "high"
    elif score >= 25:
        level = "medium"
    elif score >= 10:
        level = "low"
    else:
        level = "info"

    summary_parts: list[str] = []
    severities = [f.get("severity") for f in findings]
    for sev in ("critical", "high", "medium", "low"):
        n = sum(1 for s in severities if s == sev)
        if n:
            summary_parts.append(f"{n} {sev}")
    if not summary_parts:
        summary = "No notable findings."
    else:
        summary = "Detected " + ", ".join(summary_parts) + " findings."

    return ScoredReport(risk_score=score, risk_level=level, summary=summary)
