//! Event-driven backtest scaffold (called from Python for hot paths).
//!
//! The Python worker drives candle pacing & signal evaluation; this Rust
//! piece exposes a fast `run_event_backtest` that takes a vector of trades
//! (price, qty) and returns the resulting fills + equity curve. Used for
//! benchmarking and stress tests.

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

use crate::book::{OrderBook, Side};

#[pyfunction(name = "run_event_backtest")]
pub fn py_run_event_backtest(py: Python<'_>, events: Vec<(String, f64, f64)>) -> PyResult<Py<PyDict>> {
    let mut book = OrderBook::new();
    let mut total_volume = 0.0_f64;
    let mut trade_count: usize = 0;
    let mut last_price = 0.0_f64;

    let trade_log = PyList::empty_bound(py);
    for (side, price, qty) in events {
        let s = match Side::from_str(&side) {
            Some(s) => s,
            None => continue,
        };
        let trades = book.submit(s, price, qty, 0);
        for t in trades {
            total_volume += t.quantity * t.price;
            trade_count += 1;
            last_price = t.price;
            let d = PyDict::new_bound(py);
            d.set_item("price", t.price)?;
            d.set_item("quantity", t.quantity)?;
            d.set_item("aggressor", t.aggressor.as_str())?;
            trade_log.append(d)?;
        }
    }

    let result = PyDict::new_bound(py);
    result.set_item("trade_count", trade_count)?;
    result.set_item("total_notional", total_volume)?;
    result.set_item("last_price", last_price)?;
    result.set_item("best_bid", book.best_bid().unwrap_or(0.0))?;
    result.set_item("best_ask", book.best_ask().unwrap_or(0.0))?;
    result.set_item("trades", trade_log)?;
    Ok(result.into())
}
