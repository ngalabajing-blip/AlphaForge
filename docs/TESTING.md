# Testing

## Unit tests

Per service:

```bash
pytest services/api -q
pytest services/worker -q
pytest services/ml -q
pytest services/ingestor -q
pytest services/notifier -q
pytest services/auditor -q
pytest services/cli -q
cargo test --manifest-path services/quantcore/Cargo.toml
cd frontend && npm run test
```

## Integration tests

Compose-based, requires Docker:

```bash
docker-compose -f docker-compose.dev.yml up -d postgres redis kafka clickhouse
make e2e
```

The `make e2e` target runs `pytest tests/e2e -q` which exercises:

* `auth` → token acquisition
* `strategies` → CRUD + version publish
* `backtests` → enqueue → poll until `completed`
* `signals` → WebSocket subscribe → assert at least one signal
* `audits` → submit known address → assert findings list

## Smoke / load

```bash
locust -f tests/load/locustfile.py --headless -u 50 -r 10 --run-time 5m
```

This drives `/strategies`, `/market/candles`, `/signals` at 50 RPS
against the dev compose. Goal: p99 < 250 ms.

## Coverage targets

| Service     | Coverage |
|-------------|----------|
| api         | ≥ 70%    |
| worker      | ≥ 75%    |
| ml          | ≥ 60%    |
| auditor     | ≥ 70%    |
| quantcore   | ≥ 80%    |
| frontend    | ≥ 50%    |
