use alphaforge_quantcore::risk::{max_drawdown_native, sharpe_native, value_at_risk_native};

#[test]
fn sharpe_zero_for_constant_returns() {
    let returns = vec![0.0; 30];
    assert_eq!(sharpe_native(&returns), 0.0);
}

#[test]
fn sharpe_positive_for_positive_drift() {
    let returns: Vec<f64> = (0..200).map(|i| if i % 5 == 0 { 0.02 } else { 0.001 }).collect();
    assert!(sharpe_native(&returns) > 0.0);
}

#[test]
fn drawdown_zero_for_monotonic() {
    let equity: Vec<f64> = (0..50).map(|i| 1000.0 + i as f64).collect();
    assert!(max_drawdown_native(&equity).abs() < 1e-9);
}

#[test]
fn drawdown_captures_dip() {
    let equity = vec![100.0, 110.0, 120.0, 90.0, 95.0];
    let dd = max_drawdown_native(&equity);
    assert!((dd - 0.25).abs() < 1e-9);
}

#[test]
fn var_is_non_negative_at_high_confidence() {
    let returns: Vec<f64> = (0..1000).map(|i| ((i as f64).sin() / 100.0)).collect();
    let var95 = value_at_risk_native(&returns, 0.95);
    assert!(var95 >= 0.0);
}
