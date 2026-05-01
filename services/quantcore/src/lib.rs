//! AlphaForge quantcore — Rust core (high performance) with PyO3 bindings.
//!
//! Modules:
//!
//! * [`book`]        — limit order book matching engine.
//! * [`indicators`]  — vectorised technical indicators (EMA, RSI, ATR, VWAP).
//! * [`backtest`]    — fast event-driven backtest scaffolding.
//! * [`risk`]        — VaR / Sharpe / drawdown helpers.
//!
//! The Python facade lives in `python/alphaforge_quantcore/__init__.py` and
//! imports the compiled `_native` module emitted by maturin.

pub mod book;
pub mod indicators;
pub mod backtest;
pub mod risk;

use pyo3::prelude::*;

#[pymodule]
fn _native(_py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<book::PyOrderBook>()?;
    m.add_function(wrap_pyfunction!(indicators::py_ema, m)?)?;
    m.add_function(wrap_pyfunction!(indicators::py_rsi, m)?)?;
    m.add_function(wrap_pyfunction!(indicators::py_atr, m)?)?;
    m.add_function(wrap_pyfunction!(indicators::py_vwap, m)?)?;
    m.add_function(wrap_pyfunction!(indicators::py_macd, m)?)?;
    m.add_function(wrap_pyfunction!(indicators::py_bollinger, m)?)?;
    m.add_function(wrap_pyfunction!(risk::py_sharpe, m)?)?;
    m.add_function(wrap_pyfunction!(risk::py_max_drawdown, m)?)?;
    m.add_function(wrap_pyfunction!(risk::py_value_at_risk, m)?)?;
    m.add_function(wrap_pyfunction!(backtest::py_run_event_backtest, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn smoke_modules_present() {
        // Ensures all pub modules are reachable.
        let _ = book::OrderBook::new();
        let _ = indicators::ema_native(&[1.0, 2.0, 3.0], 2);
        let _ = risk::sharpe_native(&[0.01, 0.02, -0.01]);
    }
}
