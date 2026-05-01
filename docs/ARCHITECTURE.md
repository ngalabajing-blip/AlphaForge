# AlphaForge — Architecture

AlphaForge is an autonomous algorithmic-trading & on-chain intelligence
platform. It is intentionally over-engineered: 8 backend services, a
React frontend with a Visual Strategy Builder, a Rust performance core,
and full IaC.

## High-level diagram

```
                                 ┌────────────────────────────────────┐
                                 │             Frontend               │
                                 │ React 18 + Tailwind + ReactFlow    │
                                 │ - Strategy Builder (drag-drop DSL) │
                                 │ - Backtest visualizer              │
                                 │ - Anomaly heatmap                  │
                                 │ - Audit report viewer              │
                                 │ - Live signal feed (WebSocket)     │
                                 └─────────────────┬──────────────────┘
                                                   │ REST / GraphQL / WS
                                                   ▼
                       ┌──────────────────────────────────────────────┐
                       │                    api/                      │
                       │ FastAPI · OAuth2 + API keys + RBAC           │
                       │ REST · GraphQL (strawberry) · WebSocket subs │
                       └────┬───────┬────────────┬───────────┬────────┘
                            │       │            │           │
                            ▼       ▼            ▼           ▼
                          Postgres Redis     Kafka events  ClickHouse
                                                   ▲
            ┌───────────────────────┬──────────────┼──────────────┬───────────────────┐
            ▼                       ▼              ▼              ▼                   ▼
       ingestor/                ml/            worker/         notifier/          auditor/
   multi-chain RPC      anomaly + sentiment   Celery DSL     dispatcher           bytecode
   block/trade fanout    + price forecast      backtest +    + 6 channels         + source
   Solana, Cosmos,        models               live runner                        scanners
   EVM (eth, bsc,                              + indicators
   polygon, arb, base,                         + risk
   op, avax)
                                  ▲                                       ▲
                                  │ uses                                 uses
                                  └─── quantcore (Rust + PyO3) ──────────┘
                                       order book matching · indicators · backtest

CLI:
   services/cli (Typer) — strategies, backtests, signals, audits, market, chains
```

## Service catalogue

| Service     | Language     | Purpose                                                     |
|-------------|--------------|-------------------------------------------------------------|
| api         | Python       | Public-facing REST + GraphQL + WebSocket                    |
| ingestor    | Python       | Multi-chain block/trade ingestion → Kafka                   |
| ml          | Python       | Anomaly detection, sentiment, price forecasting             |
| worker      | Python       | Celery workers, Strategy DSL parser, backtest engine        |
| notifier    | Python       | Multi-channel alert fan-out (Telegram, Discord, …)          |
| auditor     | Python       | Smart contract bytecode + Solidity source scanner           |
| quantcore   | **Rust**     | Order book + vectorised indicators (PyO3 bindings)          |
| cli         | Python       | Typer power-user command-line client                        |
| frontend    | TypeScript   | React + Tailwind + ReactFlow visual builder                 |

## Event topology (Kafka)

The platform's nervous system. All events are JSON over Kafka.

```
T_BLOCKS            (chain, block_number, ts, …)
T_TRANSACTIONS      (chain, tx_hash, from, to, value, gas_used, …)
T_LOGS              (chain, address, topics, data, …)
T_PRICES            (symbol, price, ts)
T_DEX_TRADES        (chain, dex, pool, base, quote, side, amount, …)
T_LIQUIDITY_DELTAS  (chain, pool, delta_token0, delta_token1, …)
T_FEATURES          (window, vector)
T_ANOMALY           (window, score, factors)
T_SENTIMENT         (source, snippet, sentiment, score)
T_PRICE_PREDICTION  (symbol, horizon, mu, sigma)
T_SIGNALS           (strategy_id, symbol, action, strength, reasons[])
T_ORDERS            (strategy_id, symbol, side, qty, price)
T_FILLS             (order_id, price, qty, ts)
T_BACKTEST_PROGRESS (job_id, candles_processed, equity)
T_ALERTS            (rule_id, severity, channels[], payload)
T_NOTIFICATION_RESULT (alert_id, channel, success, error)
T_AUDIT_REQUESTED   (job_id, chain, address, deep)
T_AUDIT_REPORT      (job_id, status, risk_score, findings[])
```

## Strategy DSL

A small declarative language compiled into the worker's runtime. Two
ways to author strategies:

* **YAML/JSON source** (committed to git, reviewable):
  ```yaml
  strategy: "EMA cross"
  universe:
    symbols: [ETH/USDT]
    timeframe: 1h
  indicators:
    - {name: ema, alias: fast, period: 12}
    - {name: ema, alias: slow, period: 26}
    - {name: rsi, alias: rsi14, period: 14}
  rules:
    - when: cross_up(fast, slow) and rsi14 < 70
      then: buy
      size: 0.2
    - when: cross_down(fast, slow) or rsi14 > 80
      then: close
  ```

* **Visual builder** at `/strategies/builder` — drag indicators →
  operators → rules onto a React Flow canvas; on save the graph is
  serialised back to the same YAML format.

The DSL pipeline:

```
YAML source → tokenizer → parser → AST → compiler → expression tree → evaluator
                                                   ▲
                                                   │ at runtime, fed by:
                                                   └ indicator registry (14 indicators)
                                                     portfolio + risk engine
                                                     fee + slippage models
```

## Database design

Postgres tables:

* `users` — accounts (admin / researcher / viewer / service)
* `api_keys` — hashed API tokens
* `strategies` + `strategy_versions` — versioned DSL source
* `backtests` + `backtest_trades` — full equity curves + fills
* `signals` — strategy outputs
* `alerts` + `alert_deliveries` — alert config + delivery audit log
* `audit_jobs` — smart contract audit queue + results
* `chain_events` — flat trail of important on-chain events

ClickHouse holds the time-series data: candles, trades, anomaly scores.

Redis is used for: rate limits, hot caches (price ticks, dominance),
and Celery broker.

## Auth & RBAC

* `POST /auth/token` (OAuth2 password grant) returns access + refresh tokens
* `Authorization: Bearer …` for end users
* `X-API-Key: afk_…` for service-to-service
* Scopes attached to API keys (`read`, `write`, `admin`)
* Role enforcement happens in route dependencies (`require_role`)

## Observability

* Structured JSON logs (`structlog`)
* Prometheus metrics on `/metrics`
* OpenTelemetry traces exported via OTLP to the collector → Tempo
* Grafana dashboard included (`infra/observability/grafana-dashboards/`)

## Deployment story

Three modes:

1. **Local dev** — `docker-compose -f docker-compose.dev.yml up`
2. **Staging / single cluster** — `kubectl apply -k infra/k8s` (Kustomize) or
   `helm upgrade --install alphaforge infra/helm/alphaforge`
3. **Cloud** — `cd infra/terraform && terraform apply` provisions VPC,
   EKS, RDS, ElastiCache, S3, then point `kubectl` and Helm at the new
   cluster.
