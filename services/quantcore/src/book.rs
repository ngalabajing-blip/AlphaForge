//! Limit order book matching engine.
//!
//! Design notes:
//!
//! * Bids are sorted descending by price, asks ascending; orders within a
//!   price level are FIFO.
//! * Each level uses a `Vec<Order>` because we expect modest depth (~50
//!   levels) and benchmarking shows the cache locality wins over a linked
//!   list for typical crypto-spot books.
//! * `submit` returns the resulting trades in execution order.

use ordered_float::OrderedFloat;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::collections::BTreeMap;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Side {
    Buy,
    Sell,
}

impl Side {
    pub fn from_str(s: &str) -> Option<Self> {
        match s.to_ascii_lowercase().as_str() {
            "buy" => Some(Side::Buy),
            "sell" => Some(Side::Sell),
            _ => None,
        }
    }

    pub fn as_str(&self) -> &'static str {
        match self {
            Side::Buy => "buy",
            Side::Sell => "sell",
        }
    }
}

#[derive(Debug, Clone)]
pub struct Order {
    pub id: u64,
    pub side: Side,
    pub price: OrderedFloat<f64>,
    pub quantity: f64,
    pub ts: i64,
}

#[derive(Debug, Clone)]
pub struct Trade {
    pub price: f64,
    pub quantity: f64,
    pub aggressor: Side,
    pub maker_id: u64,
    pub taker_id: u64,
}

#[derive(Debug, Default)]
struct Level {
    orders: Vec<Order>,
}

impl Level {
    fn total_qty(&self) -> f64 {
        self.orders.iter().map(|o| o.quantity).sum()
    }
}

#[derive(Debug, Default)]
pub struct OrderBook {
    bids: BTreeMap<OrderedFloat<f64>, Level>,
    asks: BTreeMap<OrderedFloat<f64>, Level>,
    next_id: u64,
}

impl OrderBook {
    pub fn new() -> Self {
        Self {
            bids: BTreeMap::new(),
            asks: BTreeMap::new(),
            next_id: 1,
        }
    }

    pub fn submit(&mut self, side: Side, price: f64, quantity: f64, ts: i64) -> Vec<Trade> {
        let mut taker = Order {
            id: self.next_id,
            side,
            price: OrderedFloat(price),
            quantity,
            ts,
        };
        self.next_id += 1;
        let trades = self.match_taker(&mut taker);
        if taker.quantity > 0.0 {
            self.rest(taker);
        }
        trades
    }

    fn match_taker(&mut self, taker: &mut Order) -> Vec<Trade> {
        let mut trades = Vec::new();
        match taker.side {
            Side::Buy => {
                while taker.quantity > 0.0 {
                    let best = match self.asks.iter().next() {
                        Some((k, _)) => *k,
                        None => break,
                    };
                    if best > taker.price {
                        break;
                    }
                    self.match_at_level(taker, &mut trades, best, true);
                }
            }
            Side::Sell => {
                while taker.quantity > 0.0 {
                    let best = match self.bids.iter().next_back() {
                        Some((k, _)) => *k,
                        None => break,
                    };
                    if best < taker.price {
                        break;
                    }
                    self.match_at_level(taker, &mut trades, best, false);
                }
            }
        }
        trades
    }

    fn match_at_level(
        &mut self,
        taker: &mut Order,
        trades: &mut Vec<Trade>,
        level_key: OrderedFloat<f64>,
        is_ask_side: bool,
    ) {
        let level = if is_ask_side {
            self.asks.get_mut(&level_key)
        } else {
            self.bids.get_mut(&level_key)
        };
        let level = match level {
            Some(level) => level,
            None => return,
        };
        let mut consumed = 0;
        for maker in level.orders.iter_mut() {
            if taker.quantity == 0.0 {
                break;
            }
            let qty = maker.quantity.min(taker.quantity);
            trades.push(Trade {
                price: level_key.into_inner(),
                quantity: qty,
                aggressor: taker.side,
                maker_id: maker.id,
                taker_id: taker.id,
            });
            maker.quantity -= qty;
            taker.quantity -= qty;
            if maker.quantity <= 0.0 {
                consumed += 1;
            }
        }
        level.orders.drain(..consumed);
        if level.orders.is_empty() {
            if is_ask_side {
                self.asks.remove(&level_key);
            } else {
                self.bids.remove(&level_key);
            }
        }
    }

    fn rest(&mut self, order: Order) {
        let book = match order.side {
            Side::Buy => &mut self.bids,
            Side::Sell => &mut self.asks,
        };
        book.entry(order.price).or_default().orders.push(order);
    }

    pub fn best_bid(&self) -> Option<f64> {
        self.bids.iter().next_back().map(|(p, _)| p.into_inner())
    }

    pub fn best_ask(&self) -> Option<f64> {
        self.asks.iter().next().map(|(p, _)| p.into_inner())
    }

    pub fn depth(&self, levels: usize) -> (Vec<(f64, f64)>, Vec<(f64, f64)>) {
        let bids: Vec<(f64, f64)> = self
            .bids
            .iter()
            .rev()
            .take(levels)
            .map(|(p, lv)| (p.into_inner(), lv.total_qty()))
            .collect();
        let asks: Vec<(f64, f64)> = self
            .asks
            .iter()
            .take(levels)
            .map(|(p, lv)| (p.into_inner(), lv.total_qty()))
            .collect();
        (bids, asks)
    }
}

// ── PyO3 binding ─────────────────────────────────────────────────────────────
#[pyclass(name = "OrderBook")]
pub struct PyOrderBook {
    inner: OrderBook,
}

#[pymethods]
impl PyOrderBook {
    #[new]
    fn new() -> Self {
        Self {
            inner: OrderBook::new(),
        }
    }

    fn submit(&mut self, py: Python<'_>, side: &str, price: f64, quantity: f64) -> PyResult<Py<PyList>> {
        let s = Side::from_str(side).ok_or_else(|| pyo3::exceptions::PyValueError::new_err("invalid side"))?;
        let trades = self.inner.submit(s, price, quantity, 0);
        let py_trades = PyList::empty_bound(py);
        for t in trades {
            let d = PyDict::new_bound(py);
            d.set_item("price", t.price)?;
            d.set_item("quantity", t.quantity)?;
            d.set_item("aggressor", t.aggressor.as_str())?;
            d.set_item("maker_id", t.maker_id as i64)?;
            d.set_item("taker_id", t.taker_id as i64)?;
            py_trades.append(d)?;
        }
        Ok(py_trades.into())
    }

    fn best_bid(&self) -> f64 {
        self.inner.best_bid().unwrap_or(0.0)
    }

    fn best_ask(&self) -> f64 {
        self.inner.best_ask().unwrap_or(0.0)
    }

    fn depth(&self, py: Python<'_>, levels: usize) -> PyResult<Py<PyDict>> {
        let (bids, asks) = self.inner.depth(levels);
        let d = PyDict::new_bound(py);
        d.set_item("bids", bids)?;
        d.set_item("asks", asks)?;
        Ok(d.into())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn submits_resting_order() {
        let mut book = OrderBook::new();
        let trades = book.submit(Side::Buy, 100.0, 1.0, 0);
        assert!(trades.is_empty());
        assert_eq!(book.best_bid(), Some(100.0));
    }

    #[test]
    fn matches_full() {
        let mut book = OrderBook::new();
        book.submit(Side::Sell, 101.0, 5.0, 0);
        let trades = book.submit(Side::Buy, 102.0, 5.0, 1);
        assert_eq!(trades.len(), 1);
        assert_eq!(trades[0].price, 101.0);
        assert_eq!(trades[0].quantity, 5.0);
        assert_eq!(book.best_ask(), None);
    }

    #[test]
    fn fifo_ordering() {
        let mut book = OrderBook::new();
        book.submit(Side::Sell, 100.0, 2.0, 0);
        book.submit(Side::Sell, 100.0, 3.0, 1);
        let trades = book.submit(Side::Buy, 100.0, 4.0, 2);
        assert_eq!(trades.len(), 2);
        assert_eq!(trades[0].quantity, 2.0);
        assert_eq!(trades[1].quantity, 2.0);
    }
}
