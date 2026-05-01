use alphaforge_quantcore::indicators::{atr_native, bollinger_native, ema_native, macd_native, rsi_native, vwap_native};

#[test]
fn ema_short_series() {
    let v = vec![1.0, 2.0, 3.0, 4.0, 5.0];
    let ema = ema_native(&v, 3);
    assert_eq!(ema.len(), v.len());
    assert!(ema.last().unwrap() > &3.0);
    assert!(ema.last().unwrap() < &5.0);
}

#[test]
fn rsi_bounded() {
    let v: Vec<f64> = (0..50).map(|i| (i as f64).sin() * 10.0 + 50.0).collect();
    let rsi = rsi_native(&v, 14);
    for r in rsi.iter().filter(|x| !x.is_nan()) {
        assert!(*r >= 0.0 && *r <= 100.0);
    }
}

#[test]
fn atr_non_negative() {
    let highs: Vec<f64> = (0..40).map(|i| 100.0 + (i as f64 * 0.5)).collect();
    let lows: Vec<f64> = highs.iter().map(|h| h - 1.0).collect();
    let closes: Vec<f64> = highs.iter().map(|h| h - 0.5).collect();
    let atr = atr_native(&highs, &lows, &closes, 14);
    for a in atr.iter().filter(|x| !x.is_nan()) {
        assert!(*a >= 0.0);
    }
}

#[test]
fn vwap_monotonic_with_constant_price() {
    let prices = vec![100.0; 10];
    let volumes = vec![1.0; 10];
    let vwap = vwap_native(&prices, &volumes);
    for v in vwap {
        assert!((v - 100.0).abs() < 1e-9);
    }
}

#[test]
fn bollinger_band_envelopes_mid() {
    let v: Vec<f64> = (0..30).map(|i| (i as f64).cos() + 100.0).collect();
    let (upper, mid, lower) = bollinger_native(&v, 20, 2.0);
    for i in 19..v.len() {
        assert!(upper[i] >= mid[i]);
        assert!(mid[i] >= lower[i]);
    }
}

#[test]
fn macd_lengths_match() {
    let v: Vec<f64> = (0..200).map(|i| (i as f64).sin() * 5.0 + 50.0).collect();
    let (macd, signal, hist) = macd_native(&v, 12, 26, 9);
    assert_eq!(macd.len(), v.len());
    assert_eq!(signal.len(), v.len());
    assert_eq!(hist.len(), v.len());
}
