//! Vectorised technical indicators.

use pyo3::prelude::*;

pub fn ema_native(values: &[f64], period: usize) -> Vec<f64> {
    if values.is_empty() {
        return Vec::new();
    }
    let alpha = 2.0 / (period as f64 + 1.0);
    let mut prev = values[0];
    values
        .iter()
        .map(|v| {
            prev = prev + alpha * (v - prev);
            prev
        })
        .collect()
}

pub fn rsi_native(values: &[f64], period: usize) -> Vec<f64> {
    let n = values.len();
    if n < period + 1 {
        return vec![50.0; n];
    }
    let mut gains = vec![0.0_f64; n];
    let mut losses = vec![0.0_f64; n];
    for i in 1..n {
        let d = values[i] - values[i - 1];
        if d >= 0.0 {
            gains[i] = d;
        } else {
            losses[i] = -d;
        }
    }
    let mut out = vec![50.0_f64; n];
    for i in period..n {
        let avg_g: f64 = gains[i + 1 - period..=i].iter().sum::<f64>() / period as f64;
        let avg_l: f64 = losses[i + 1 - period..=i].iter().sum::<f64>() / period as f64;
        if avg_l == 0.0 {
            out[i] = 100.0;
        } else {
            let rs = avg_g / avg_l;
            out[i] = 100.0 - 100.0 / (1.0 + rs);
        }
    }
    out
}

pub fn atr_native(highs: &[f64], lows: &[f64], closes: &[f64], period: usize) -> Vec<f64> {
    let n = closes.len();
    if n == 0 {
        return Vec::new();
    }
    let mut trs = Vec::with_capacity(n);
    for i in 0..n {
        let tr = if i == 0 {
            highs[i] - lows[i]
        } else {
            let a = highs[i] - lows[i];
            let b = (highs[i] - closes[i - 1]).abs();
            let c = (lows[i] - closes[i - 1]).abs();
            a.max(b).max(c)
        };
        trs.push(tr);
    }
    let mut out = Vec::with_capacity(n);
    for i in 0..n {
        let start = if i + 1 >= period { i + 1 - period } else { 0 };
        let slice = &trs[start..=i];
        out.push(slice.iter().sum::<f64>() / slice.len() as f64);
    }
    out
}

pub fn vwap_native(prices: &[f64], volumes: &[f64]) -> Vec<f64> {
    let mut cum_pv = 0.0;
    let mut cum_v = 0.0;
    prices
        .iter()
        .zip(volumes.iter())
        .map(|(p, v)| {
            cum_pv += p * v;
            cum_v += v;
            if cum_v == 0.0 {
                *p
            } else {
                cum_pv / cum_v
            }
        })
        .collect()
}

pub fn bollinger_native(values: &[f64], period: usize, k: f64) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
    let n = values.len();
    let mut upper = vec![0.0_f64; n];
    let mut mid = vec![0.0_f64; n];
    let mut lower = vec![0.0_f64; n];
    for i in 0..n {
        if i + 1 < period {
            upper[i] = values[i];
            mid[i] = values[i];
            lower[i] = values[i];
            continue;
        }
        let slice = &values[i + 1 - period..=i];
        let mu: f64 = slice.iter().sum::<f64>() / period as f64;
        let var: f64 = slice.iter().map(|v| (v - mu).powi(2)).sum::<f64>() / period as f64;
        let std = var.sqrt();
        upper[i] = mu + k * std;
        lower[i] = mu - k * std;
        mid[i] = mu;
    }
    (upper, mid, lower)
}

pub fn macd_native(values: &[f64], fast: usize, slow: usize, signal: usize) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
    let f = ema_native(values, fast);
    let s = ema_native(values, slow);
    let macd: Vec<f64> = f.iter().zip(s.iter()).map(|(a, b)| a - b).collect();
    let sig = ema_native(&macd, signal);
    let hist: Vec<f64> = macd.iter().zip(sig.iter()).map(|(a, b)| a - b).collect();
    (macd, sig, hist)
}

// ── PyO3 wrappers ────────────────────────────────────────────────────────────
#[pyfunction(name = "ema")]
pub fn py_ema(values: Vec<f64>, period: usize) -> Vec<f64> {
    ema_native(&values, period)
}

#[pyfunction(name = "rsi")]
pub fn py_rsi(values: Vec<f64>, period: usize) -> Vec<f64> {
    rsi_native(&values, period)
}

#[pyfunction(name = "atr")]
pub fn py_atr(highs: Vec<f64>, lows: Vec<f64>, closes: Vec<f64>, period: usize) -> Vec<f64> {
    atr_native(&highs, &lows, &closes, period)
}

#[pyfunction(name = "vwap")]
pub fn py_vwap(prices: Vec<f64>, volumes: Vec<f64>) -> Vec<f64> {
    vwap_native(&prices, &volumes)
}

#[pyfunction(name = "bollinger")]
pub fn py_bollinger(values: Vec<f64>, period: usize, k: f64) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
    bollinger_native(&values, period, k)
}

#[pyfunction(name = "macd")]
pub fn py_macd(values: Vec<f64>, fast: usize, slow: usize, signal: usize) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
    macd_native(&values, fast, slow, signal)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ema_constant_returns_constant() {
        let out = ema_native(&[5.0; 50], 10);
        for v in out.iter() {
            assert!((v - 5.0).abs() < 1e-9);
        }
    }

    #[test]
    fn rsi_bounds() {
        let v: Vec<f64> = (0..100).map(|i| (i as f64).sin()).collect();
        let r = rsi_native(&v, 14);
        for x in r {
            assert!((0.0..=100.0).contains(&x));
        }
    }

    #[test]
    fn vwap_increasing_prices() {
        let p = vec![10.0, 20.0, 30.0];
        let v = vec![1.0, 1.0, 1.0];
        let w = vwap_native(&p, &v);
        assert_eq!(w[0], 10.0);
        assert!((w[1] - 15.0).abs() < 1e-6);
        assert!((w[2] - 20.0).abs() < 1e-6);
    }
}
