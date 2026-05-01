# AlphaForge

> Autonomous Algorithmic Trading & On-Chain Intelligence Platform

AlphaForge is a research-grade platform for designing, backtesting, and operating
algorithmic trading strategies across multiple blockchains. It combines real-time
on-chain event ingestion, a declarative strategy DSL, an ML-powered anomaly
detection pipeline, a smart-contract auditor, and a high-performance execution
core written in Rust.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Rust](https://img.shields.io/badge/Rust-1.78-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![React](https://img.shields.io/badge/React-18-61dafb)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Highlights

- **Multi-chain ingestion** — Ethereum, BSC, Polygon, Arbitrum, Base, Optimism,
  Avalanche, Solana, Cosmos. WebSocket subscribers + REST fallbacks, all
  normalised through a shared event schema and pushed onto a Kafka bus.
- **Strategy DSL** — declarative YAML/JSON DSL with a Python AST-backed parser,
  rich indicator library, walk-forward backtesting, and paper-trading executor.
- **ML pipeline** — Isolation-Forest based anomaly detection, an autoencoder for
  reconstruction-error scoring, a transformer-style sentiment classifier for
  social streams, and an LSTM price-prediction baseline.
- **Smart contract auditor** — heuristic Solidity source analysis, EVM
  bytecode pattern matching (proxy, selfdestruct, delegatecall, hidden mints),
  honeypot detection, and a SARIF-compatible report exporter.
- **QuantCore (Rust)** — high-performance order book simulator and indicator
  engine exposed to Python via PyO3. ~10x faster than the pure-Python fallback.
- **Visual Strategy Builder** — React Flow based node editor that compiles
  visual graphs to the AlphaForge DSL.
- **GraphQL + REST + WebSocket** — every resource exposed through three transports;
  subscriptions stream signals, alerts, and market events.
- **RBAC + API keys + OAuth2** — fine-grained roles (admin, researcher, viewer,
  service), API-key management with scopes, and OAuth2 password / client-credentials
  flows.
- **Observability** — OpenTelemetry traces, Prometheus metrics, structured logs.
- **Cloud-native** — docker-compose for local dev, Kubernetes manifests + Helm
  chart for production, Terraform skeleton for AWS provisioning.

## Architecture

```
                      ┌──────────────┐
                      │   Frontend   │  React + Vite + Tailwind
                      └──────┬───────┘
                             │
                      ┌──────▼───────┐
                      │   API Gateway│  FastAPI: REST + GraphQL + WS
                      └──────┬───────┘
                             │
        ┌────────────┬───────┼────────────┬─────────────┐
        │            │       │            │             │
   ┌────▼────┐ ┌─────▼────┐ ┌▼────────┐ ┌▼─────────┐ ┌──▼─────┐
   │ Worker  │ │   ML     │ │Notifier │ │ Auditor  │ │CLI Tool│
   │ Celery  │ │Inference │ │Fan-out  │ │ EVM/Sol  │ │ Typer  │
   │ + DSL   │ │  Server  │ │         │ │          │ │        │
   └────┬────┘ └────┬─────┘ └────┬────┘ └────┬─────┘ └────────┘
        │           │            │           │
        └───────────┴────┬───────┴───────────┘
                         │
                  ┌──────▼───────┐
                  │ Ingestor(s)  │  multi-chain WS + REST
                  └──────┬───────┘
                         │
        ┌────────────────┼─────────────────┐
        │                │                 │
   ┌────▼────┐    ┌──────▼─────┐   ┌───────▼────┐
   │PostgreSQL│   │ ClickHouse │   │   Redis    │
   └─────────┘    └────────────┘   └────────────┘
                         │
                  ┌──────▼──────┐
                  │    Kafka    │  event bus
                  └─────────────┘
```

The Rust **QuantCore** library is statically linked into the worker via PyO3
and exposed through `from quantcore import OrderBook, IndicatorEngine`.

## Quick start

```bash
make setup              # install all deps (Python + Node + Rust)
make dev                # bring up the full dev stack with hot reload
make test               # run all unit + integration tests
make lint               # ruff + mypy + eslint + cargo clippy
make audit CONTRACT=0x… # run the smart-contract auditor on an address
make backtest STRATEGY=examples/ema_cross.yaml
```

The full stack listens on:

| Component        | URL                              |
|------------------|----------------------------------|
| Frontend         | http://localhost:3000            |
| API REST         | http://localhost:8000/api/v1     |
| API GraphQL      | http://localhost:8000/graphql    |
| API docs         | http://localhost:8000/docs       |
| ML inference     | http://localhost:8001            |
| Auditor          | http://localhost:8002            |
| Notifier         | http://localhost:8003            |
| Prometheus       | http://localhost:9090            |
| Grafana          | http://localhost:3001            |

## Project layout

```
alphaforge/
├── services/
│   ├── api/         FastAPI gateway (REST + GraphQL + WS)
│   ├── ingestor/    Multi-chain event ingester
│   ├── ml/          Inference server & training pipelines
│   ├── worker/      Celery worker + Strategy DSL + backtester
│   ├── notifier/    Multi-channel notification fan-out
│   ├── auditor/     Smart-contract security analyser
│   ├── quantcore/   Rust crate (PyO3) — order book + indicators
│   └── cli/         Typer-based CLI for power users
├── shared/          Shared event schemas, Kafka topics, chain registry
├── frontend/        React + Vite + visual strategy builder
├── infra/
│   ├── k8s/         Kubernetes manifests
│   ├── helm/        Helm chart skeleton
│   └── terraform/   AWS provisioning skeleton
├── docker/          Dockerfiles + nginx config
├── docs/            ARCHITECTURE, STRATEGY_DSL, API, ML_PIPELINE, AUDITOR …
├── scripts/         Init, seed, migrate, backup, load-test scripts
└── tests/e2e/       Cross-service end-to-end tests
```

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — service topology, data flow, capacity model
- [docs/STRATEGY_DSL.md](docs/STRATEGY_DSL.md) — DSL grammar, indicators, examples
- [docs/API.md](docs/API.md) — REST + GraphQL + WebSocket reference
- [docs/ML_PIPELINE.md](docs/ML_PIPELINE.md) — feature engineering, training, drift
- [docs/AUDITOR.md](docs/AUDITOR.md) — heuristics catalogue, SARIF mapping
- [docs/RUST_CORE.md](docs/RUST_CORE.md) — QuantCore API, performance notes
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — k8s + helm + terraform walkthrough

## License

MIT — see [LICENSE](LICENSE).
