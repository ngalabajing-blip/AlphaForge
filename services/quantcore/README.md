# alphaforge-quantcore

High-performance Rust core for AlphaForge. Exposes:

* Limit order book matching (FIFO, price-time priority)
* Vectorised indicators: EMA, RSI, ATR, VWAP, MACD, Bollinger
* Risk metrics: Sharpe, max drawdown, Value-at-Risk
* Event-driven backtest scaffold

## Building

```bash
cd services/quantcore
maturin develop --release
```

A pure-Python fallback ships in `python/alphaforge_quantcore/__init__.py` so
unit tests + the Python worker run even without the compiled extension.

## Layout

```
services/quantcore/
├── Cargo.toml                    # Rust workspace member
├── pyproject.toml                # maturin build config
├── src/
│   ├── lib.rs                    # PyO3 module entry
│   ├── book.rs                   # order book matching engine
│   ├── indicators.rs             # vectorised TA indicators
│   ├── backtest.rs               # event-driven backtest scaffold
│   └── risk.rs                   # Sharpe / drawdown / VaR
└── python/
    └── alphaforge_quantcore/
        ├── __init__.py           # pure-Python facade + fallbacks
        └── _native.{so,pyd}      # compiled by maturin (gitignored)
```
