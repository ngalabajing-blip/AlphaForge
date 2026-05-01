use alphaforge_quantcore::book::{Order, OrderBook, Side};

#[test]
fn fifo_match_full_taker() {
    let mut book = OrderBook::default();
    book.submit(Order::new(1, Side::Sell, 100.0, 5.0, 0));
    book.submit(Order::new(2, Side::Sell, 100.5, 5.0, 1));

    let trades = book.submit(Order::new(3, Side::Buy, 100.5, 7.0, 2));
    let total_qty: f64 = trades.iter().map(|t| t.quantity).sum();
    assert!((total_qty - 7.0).abs() < 1e-9);
    assert_eq!(book.best_ask().unwrap().0, 100.5);
}

#[test]
fn partial_buy_rests_remainder() {
    let mut book = OrderBook::default();
    book.submit(Order::new(1, Side::Sell, 100.0, 1.0, 0));
    let trades = book.submit(Order::new(2, Side::Buy, 100.0, 3.0, 1));
    assert_eq!(trades.len(), 1);
    let depth = book.depth(5);
    let bid_levels: Vec<_> = depth.bids;
    assert!(!bid_levels.is_empty());
    assert!((bid_levels[0].1 - 2.0).abs() < 1e-9);
}

#[test]
fn best_bid_ask_consistent() {
    let mut book = OrderBook::default();
    book.submit(Order::new(1, Side::Buy, 99.0, 5.0, 0));
    book.submit(Order::new(2, Side::Buy, 99.5, 3.0, 1));
    book.submit(Order::new(3, Side::Sell, 100.5, 4.0, 2));
    book.submit(Order::new(4, Side::Sell, 101.0, 2.0, 3));
    let (bid, _) = book.best_bid().unwrap();
    let (ask, _) = book.best_ask().unwrap();
    assert!(bid < ask);
    assert_eq!(bid, 99.5);
    assert_eq!(ask, 100.5);
}
