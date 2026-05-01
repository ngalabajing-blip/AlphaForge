"""Template rendering for alert payloads."""

from __future__ import annotations

from typing import Any

DEFAULT_TEMPLATE = """\
[AlphaForge] {title}
Symbol: {symbol}
Severity: {severity}
Message: {message}

{details}
"""


def render_template(alert: dict[str, Any]) -> dict[str, str]:
    title = str(alert.get("title") or alert.get("name") or "Alert")
    symbol = str(alert.get("symbol") or "-")
    severity = str(alert.get("severity") or "info")
    message = str(alert.get("message") or "")
    details = _render_details(alert.get("payload", {}) or {})
    body_text = DEFAULT_TEMPLATE.format(
        title=title, symbol=symbol, severity=severity, message=message, details=details
    )
    body_md = _to_markdown(title, symbol, severity, message, details)
    return {
        "title": title,
        "text": body_text,
        "markdown": body_md,
        "severity": severity,
    }


def _render_details(payload: dict) -> str:
    if not payload:
        return ""
    return "\n".join(f"- {k}: {v}" for k, v in payload.items() if not isinstance(v, (dict, list)))


def _to_markdown(title: str, symbol: str, severity: str, message: str, details: str) -> str:
    return (
        f"**{title}**\n"
        f"`Symbol: {symbol}`  · `Severity: {severity}`\n\n"
        f"{message}\n\n"
        f"{details or '_no details_'}"
    )
