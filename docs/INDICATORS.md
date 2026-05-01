# Indicator catalogue

The worker service ships with 16 indicators. Each accepts a parameter
dictionary and returns a `list[float]` of the same length as the
underlying candle stream. Where an indicator returns multiple lines
(e.g. MACD), the runtime registers the additional aliases (`macd_line`,
`macd_signal`, `macd_hist`) automatically.

## Trend

| Name        | Parameters             | Output                                    |
|-------------|------------------------|-------------------------------------------|
| `sma`       | `period`, `source`     | simple moving average                     |
| `ema`       | `period`, `source`     | exponentially-weighted moving average     |
| `wma`       | `period`, `source`     | weighted moving average                   |
| `dema`      | `period`, `source`     | double exponential moving average         |
| `ichimoku`  | `tenkan`, `kijun`, `b` | tenkan / kijun / senkou_a / senkou_b      |
| `supertrend`| `atr_period`, `mult`   | trend line, current direction (-1/+1)     |

## Momentum

| Name      | Parameters                | Output                              |
|-----------|---------------------------|-------------------------------------|
| `rsi`     | `period`                  | RSI in [0, 100]                     |
| `macd`    | `fast`, `slow`, `signal`  | macd_line, macd_signal, macd_hist   |
| `stoch`   | `k_period`, `d_period`    | %K, %D                              |
| `aroon`   | `period`                  | aroon_up, aroon_down                |

## Volatility

| Name        | Parameters             | Output                          |
|-------------|------------------------|---------------------------------|
| `atr`       | `period`               | average true range              |
| `bollinger` | `period`, `k`          | bb_upper, bb_mid, bb_lower      |
| `keltner`   | `period`, `multiplier` | k_upper, k_mid, k_lower         |
| `donchian`  | `period`               | dc_upper, dc_lower              |

## Volume / flow

| Name   | Parameters | Output                |
|--------|------------|-----------------------|
| `obv`  | -          | on-balance volume     |
| `vwap` | -          | volume-weighted price |
| `cmf`  | `period`   | Chaikin money flow    |
| `adx`  | `period`   | ADX (+DI, -DI exposed)|

## Implementation note

When the Rust `quantcore` extension is built, the registry
transparently delegates `ema`, `rsi`, `atr`, `vwap`, `bollinger`, and
`macd` to the native implementation for ~10–50× speedup.
