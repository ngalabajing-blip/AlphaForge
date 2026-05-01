from __future__ import annotations

import pytest

from alphaforge_api.services.dsl_loader import (
    DSLValidationError,
    SOURCE_FORMAT_YAML,
    detect_format,
    load_strategy_source,
    summarise_indicators,
)


VALID_YAML = """\
strategy: "test"
universe: { symbols: [ETH/USDT], timeframe: 1h }
indicators:
  - {name: ema, alias: fast, period: 12}
  - {name: ema, alias: slow, period: 26}
rules:
  - when: cross_up(fast, slow)
    then: buy
"""


def test_detect_yaml_format() -> None:
    assert detect_format(VALID_YAML) == SOURCE_FORMAT_YAML


def test_load_valid_strategy_source() -> None:
    parsed = load_strategy_source(VALID_YAML)
    assert parsed["strategy"] == "test"
    assert len(parsed["indicators"]) == 2
    assert parsed["rules"][0]["then"] == "buy"


def test_load_invalid_yaml_raises() -> None:
    with pytest.raises(DSLValidationError):
        load_strategy_source("this is not: yaml: at all: : :")


def test_load_missing_required_field() -> None:
    bad = "indicators: []\nrules: []\n"  # no strategy/universe
    with pytest.raises(DSLValidationError):
        load_strategy_source(bad)


def test_summarise_indicators_returns_aliases() -> None:
    parsed = load_strategy_source(VALID_YAML)
    summary = summarise_indicators(parsed["indicators"])
    assert "fast" in summary
    assert "slow" in summary
    assert summary["fast"]["name"] == "ema"
