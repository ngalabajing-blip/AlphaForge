# Strategy DSL

Declarative DSL for AlphaForge strategies. Designed to be:

* **Reviewable** — diffable YAML committed to git
* **Composable** — every block is independently testable
* **Safe** — no `eval`, hand-written tokenizer + recursive descent parser

## Top-level shape

```yaml
strategy: "EMA cross"
description: "Trend-following EMA crossover with RSI filter"
universe:
  symbols: [ETH/USDT, BTC/USDT]
  timeframe: 1h
parameters:
  fast_period: 12
  slow_period: 26
  rsi_period: 14
  position_size: 0.2
indicators:
  - {name: ema,    alias: fast,  period: param("fast_period")}
  - {name: ema,    alias: slow,  period: param("slow_period")}
  - {name: rsi,    alias: rsi14, period: param("rsi_period")}
  - {name: atr,    alias: atr14, period: 14}
rules:
  - when: cross_up(fast, slow) and rsi14 < 70
    then: buy
    size: param("position_size")
  - when: cross_down(fast, slow) or rsi14 > 80
    then: close
risk:
  max_drawdown: 0.2
  max_concurrent_positions: 3
  per_trade_stop_loss_pct: 0.05
  per_trade_take_profit_pct: 0.15
```

## Indicator catalogue

| name        | params                                     |
|-------------|--------------------------------------------|
| sma         | period, source                             |
| ema         | period, source                             |
| rsi         | period, source                             |
| macd        | fast, slow, signal                         |
| bollinger   | period, k                                  |
| atr         | period                                     |
| stochastic  | k_period, d_period                         |
| adx         | period                                     |
| obv         |                                            |
| vwap        |                                            |
| aroon       | period                                     |
| cmf         | period                                     |
| donchian    | period                                     |
| ichimoku    | tenkan, kijun, senkou_b                    |
| keltner     | period, multiplier                         |
| supertrend  | atr_period, multiplier                     |

## Operators

Arithmetic: `+ - * / %`
Comparison: `> < >= <= == !=`
Logical: `and or not`
Function calls:

```
cross_up(a, b)        # a crossed above b in last bar
cross_down(a, b)
above(a, b)           # a > b
below(a, b)
in_range(x, lo, hi)
abs(x)
min(...), max(...)
pct_change(x, n)
position(symbol)      # current open position size in [-1, 1]
param(name)           # parameter substitution
```

## Rules grammar

```
rule := { when: <expr>, then: <action>, [size: <expr>], [stop_loss: <expr>], [take_profit: <expr>] }

action := buy | sell | close | alert | rebalance
```

## Risk block

```yaml
risk:
  max_drawdown: 0.20
  max_concurrent_positions: 5
  per_trade_stop_loss_pct: 0.05
  per_trade_take_profit_pct: 0.15
  daily_loss_limit_pct: 0.05
```

If `max_drawdown` is breached during backtests or live, the runtime
issues an automatic close-all + halt event (`T_ALERTS`) until manual
re-arming.

## Visual builder

The `/strategies/builder` page lets users compose the same DSL on a
React Flow canvas. Each node belongs to one of:

* **Indicator** — produces a stream value
* **Operator** — combines streams (`cross_up`, `>`, `and`, …)
* **Constant** — literal numeric or symbol reference
* **Rule** — terminal node tagged with action + size

The frontend serialiser (`src/strategyBuilder/compile.ts`) walks the
graph and emits canonical YAML — round-tripping with the manually
authored format.
