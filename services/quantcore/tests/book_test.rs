use alphaforge_quantcore::book::{OrderBook, Side};

#[test]
fn fifo_match_full_taker() {
    let mut book = OrderBook::new();
    book.submit(Side::Sell, 100.0, 5.0, 0);
    book.submit(Side::Sell, 100.5, 5.0, 1);

    let trades = book.submit(Side::Buy, 100.5, 7.0, 2);
    let total_qty: f64 = trades.iter().map(|t| t.quantity).sum();
    assert!((total_qty - 7.0).abs() < 1e-9);
    assert_eq!(book.best_ask().unwrap(), 100.5);
}

#[test]
fn partial_buy_rests_remainder() {
    let mut book = OrderBook::new();
    book.submit(Side::Sell, 100.0, 1.0, 0);
    let trades = book.submit(Side::Buy, 100.0, 3.0, 1);
    assert_eq!(trades.len(), 1);
    let (bids, _asks) = book.depth(5);
    assert!(!bids.is_empty());
    assert!((bids[0].1 - 2.0).abs() < 1e-9);
}

#[test]
fn best_bid_ask_consistent() {
    let mut book = OrderBook::new();
    book.submit(Side::Buy, 99.0, 5.0, 0);
    book.submit(Side::Buy, 99.5, 3.0, 1);
    book.submit(Side::Sell, 100.5, 4.0, 2);
    book.submit(Side::Sell, 101.0, 2.0, 3);
    let bid = book.best_bid().unwrap();
    let ask = book.best_ask().unwrap();
    assert!(bid < ask);
    assert_eq!(bid, 99.5);
    assert_eq!(ask, 100.5);
}

#[test]
fn no_match_when_prices_dont_cross() {
    let mut book = OrderBook::new();
    book.submit(Side::Sell, 105.0, 1.0, 0);
    let trades = book.submit(Side::Buy, 100.0, 1.0, 1);
    assert!(trades.is_empty());
    let (bids, asks) = book.depth(5);
    assert!(!bids.is_empty() && !asks.is_empty());
}

#[test]
fn empty_book_has_no_best_quotes() {
    let book = OrderBook::new();
    assert!(book.best_bid().is_none());
    assert!(book.best_ask().is_none());
}
