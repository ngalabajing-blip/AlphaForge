from alphaforge_worker.dsl.evaluator import EvalContext, StrategyEvaluator
from alphaforge_worker.dsl.parser import parse_strategy

YAML = """
strategy: t
universe: {symbols: [A], timeframe: 1h}
indicators:
  - {name: ema, period: 5, alias: fast}
  - {name: ema, period: 20, alias: slow}
rules:
  - when: cross_up(fast, slow)
    then: buy
    size: 0.5
  - when: cross_down(fast, slow)
    then: close
"""


def test_evaluator_no_signal_when_not_crossed():
    doc = parse_strategy(YAML)
    ev = StrategyEvaluator(doc)
    ctx = EvalContext(
        indicators={"fast": [10, 11, 12], "slow": [20, 20, 20]},
        indicators_history={"fast": [10, 11, 12], "slow": [20, 20, 20]},
    )
    out = ev.evaluate(ctx)
    assert all(not o.fired for o in out)


def test_evaluator_cross_up_fires():
    doc = parse_strategy(YAML)
    ev = StrategyEvaluator(doc)
    ctx = EvalContext(
        indicators={"fast": [9, 11], "slow": [10, 10]},
        indicators_history={"fast": [9, 11], "slow": [10, 10]},
    )
    out = ev.evaluate(ctx)
    fired = [o for o in out if o.fired]
    assert len(fired) == 1
    assert fired[0].action == "buy"
    assert fired[0].size == 0.5
