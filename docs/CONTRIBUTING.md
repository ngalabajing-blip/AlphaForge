# Contributing

## Repo layout

```
alphaforge/
├── shared/                 # alphaforge-shared (common utilities)
├── services/
│   ├── api/                # FastAPI public surface
│   ├── ingestor/           # Multi-chain event ingestion
│   ├── ml/                 # ML inference
│   ├── worker/             # Celery + Strategy DSL + backtests
│   ├── notifier/           # Multi-channel alert fan-out
│   ├── auditor/            # Smart contract scanner
│   ├── quantcore/          # Rust core (PyO3)
│   └── cli/                # Typer CLI
├── frontend/               # React + Tailwind + ReactFlow
├── infra/
│   ├── k8s/                # Plain manifests (Kustomize)
│   ├── helm/               # Helm chart
│   ├── terraform/          # AWS skeleton
│   └── observability/      # Prometheus, Grafana, OTel collector
├── docs/
└── docker-compose.{yml,dev.yml}
```

## Local dev

* Python 3.11+, Node 20+, optionally Rust 1.78+ for `quantcore`.
* `pip install -e shared && pip install -e services/<svc>` for each
  service you want to develop locally.
* `pre-commit install` enables ruff + black + mypy + eslint.

## Testing

Per service:

```bash
pytest services/api
pytest services/worker
cargo test --manifest-path services/quantcore/Cargo.toml
cd frontend && npm run test
```

End-to-end (requires docker-compose):

```bash
make e2e
```

## Style

* Python: ruff + black + mypy strict (no `Any`, no `getattr`/`setattr` lazy hacks)
* TypeScript: eslint + tsc strict
* Rust: `cargo fmt` + `clippy --all-targets`
* Conventional commits (e.g. `feat(api): add audit endpoints`)

## Submitting

1. Branch from `main`
2. Ensure all tests pass and `make lint` is clean
3. Open a pull request with a clear description and screenshots if UI

We squash-merge after at least one approval.
