"""
Helpers for parsing the AlphaForge Strategy DSL.

The actual DSL parser lives in the worker service (it's heavy: needs an AST
walker, indicator registry, etc). The API service only needs to:

1. Validate that a strategy document is well-formed YAML/JSON.
2. Extract a normalised dict to store on the StrategyVersion.

For full semantic validation we POST to the worker.
"""

from __future__ import annotations

from typing import Any

import orjson


def loads(text: str) -> dict[str, Any]:
    """Try YAML first, fall back to JSON."""
    text = text.strip()
    if not text:
        raise ValueError("empty strategy document")
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        yaml = None  # type: ignore[assignment]

    if yaml is not None:
        try:
            data = yaml.safe_load(text)
            if isinstance(data, dict):
                return _normalise(data)
        except yaml.YAMLError:  # type: ignore[attr-defined]
            pass

    try:
        data = orjson.loads(text)
    except Exception as exc:  # noqa: BLE001 - parser variability
        raise ValueError(f"invalid strategy document: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("strategy document must be a mapping at top level")
    return _normalise(data)


_REQUIRED_TOP_KEYS = ("strategy", "universe", "rules")


def _normalise(data: dict[str, Any]) -> dict[str, Any]:
    missing = [k for k in _REQUIRED_TOP_KEYS if k not in data]
    if missing:
        raise ValueError(f"missing required keys: {missing}")
    out = dict(data)
    out.setdefault("parameters", {})
    out.setdefault("risk", {})
    out.setdefault("indicators", [])
    if not isinstance(out["rules"], list) or not out["rules"]:
        raise ValueError("'rules' must be a non-empty list")
    return out
