# ADR 0001 — Language choices

* Status: accepted
* Date: 2026-04-01

## Context

We needed to balance velocity (a single language for most services)
against the demand for low-latency primitives in the trading core.
Pure Python was tempting because all our developers speak it, but
order book matching and indicator computation become quickly
unsuitable for Python's GIL once the universe grows.

## Decision

* **Python 3.11** for every service that lives close to data /
  business logic — `api`, `ingestor`, `ml`, `worker`, `notifier`,
  `auditor`, `cli`. We use type-checked Python (mypy strict) so the
  loss of compile-time guarantees relative to e.g. Go is partially
  compensated.
* **Rust** for `quantcore`. Order book, vectorised indicators, risk
  metrics. PyO3 bindings expose the same surface to Python.
* **TypeScript** for the frontend. React 18 + Vite + Tailwind. The
  Visual Strategy Builder uses ReactFlow.
* **YAML** for the Strategy DSL — it's diffable, reviewable, and the
  parser stays pure (no `eval`).

## Consequences

* Hot paths can move from Python to Rust without changing the public
  Python API (the facade detects the extension and falls back to the
  pure-Python implementation otherwise).
* The build needs `maturin` for the Rust extension. Acceptable cost.
* Mixed-language CI is more complex but is mitigated by separate
  workflows per language.
