# AlphaForge frontend

React 18 + TypeScript + Vite + Tailwind frontend for AlphaForge.

## Highlights

* **Visual Strategy Builder** — drag-drop nodes (indicators, operators, rules,
  triggers) on a React Flow canvas → compiles to AlphaForge Strategy DSL YAML
  on save.
* **Backtest visualizer** — equity curve + per-trade PnL + summary stats.
* **Anomaly heatmap** — symbol × hour grid with composite anomaly score.
* **Audit report viewer** — finding-level severity tags, source/bytecode
  metadata.
* **Live signals stream** — WebSocket subscription to `/ws/signals`.
* **Admin panel** — user management for `admin` role.
* **Settings** — API key generation + revocation.

## Run

```bash
cd frontend
pnpm install         # or npm / yarn
pnpm dev
```

The dev server proxies `/api`, `/graphql`, and `/ws` to `localhost:8000`
where the AlphaForge API service listens.

## Test

```bash
pnpm test            # vitest
pnpm typecheck
pnpm lint
```
