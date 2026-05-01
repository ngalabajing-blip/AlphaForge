//! Risk metrics: Sharpe, max drawdown, value-at-risk.

use pyo3::prelude::*;

pub fn sharpe_native(returns: &[f64]) -> f64 {
    if returns.len() < 2 {
        return 0.0;
    }
    let mean: f64 = returns.iter().sum::<f64>() / returns.len() as f64;
    let var: f64 = returns.iter().map(|r| (r - mean).powi(2)).sum::<f64>() / (returns.len() - 1) as f64;
    let std = var.sqrt();
    if std == 0.0 {
        return 0.0;
    }
    mean / std * (365.0 * 24.0_f64).sqrt()
}

pub fn max_drawdown_native(equity: &[f64]) -> f64 {
    if equity.is_empty() {
        return 0.0;
    }
    let mut peak = equity[0];
    let mut max_dd = 0.0;
    for &v in equity {
        if v > peak {
            peak = v;
        }
        if peak > 0.0 {
            let dd = (peak - v) / peak;
            if dd > max_dd {
                max_dd = dd;
            }
        }
    }
    max_dd
}

pub fn value_at_risk_native(returns: &[f64], confidence: f64) -> f64 {
    if returns.is_empty() {
        return 0.0;
    }
    let mut sorted: Vec<f64> = returns.to_vec();
    sorted.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    let idx = ((1.0 - confidence) * sorted.len() as f64).floor() as usize;
    -sorted[idx.min(sorted.len() - 1)]
}

#[pyfunction(name = "sharpe")]
pub fn py_sharpe(returns: Vec<f64>) -> f64 {
    sharpe_native(&returns)
}

#[pyfunction(name = "max_drawdown")]
pub fn py_max_drawdown(equity: Vec<f64>) -> f64 {
    max_drawdown_native(&equity)
}

#[pyfunction(name = "value_at_risk")]
pub fn py_value_at_risk(returns: Vec<f64>, confidence: f64) -> f64 {
    value_at_risk_native(&returns, confidence)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn drawdown_simple() {
        let eq = vec![100.0, 150.0, 90.0, 130.0];
        let dd = max_drawdown_native(&eq);
        assert!((dd - 0.4).abs() < 1e-9);
    }

    #[test]
    fn var_positive_for_negatives() {
        let r = vec![-0.1, -0.05, 0.0, 0.05, 0.1];
        let v = value_at_risk_native(&r, 0.95);
        assert!(v > 0.0);
    }
}
