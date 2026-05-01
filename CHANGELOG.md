# Changelog

All notable changes to AlphaForge are documented here. The project follows
[semantic versioning](https://semver.org).

## [Unreleased]

### Added

* Visual Strategy Builder (React Flow) — drag-drop indicator/operator/rule
  nodes, compiles back to canonical YAML on save.
* Smart contract auditor service with bytecode scanner, Solidity source
  scanner and risk scoring.
* Rust quantcore (PyO3 bindings): order book, vectorised indicators,
  risk metrics, with pure-Python fallback when the extension is not
  built.
* CLI tool (`alphaforge`) covering auth, strategies, backtests,
  signals, audits, market, chains.
* Helm chart (`infra/helm/alphaforge`).
* Terraform AWS skeleton (VPC + EKS + RDS + ElastiCache + S3).
* Postman collection for the entire REST surface.
* Pre-commit hooks (ruff + black + mypy + pre-commit-hooks).

## [0.1.0] — Initial release

* 8 backend services (`api`, `ingestor`, `ml`, `worker`, `notifier`,
  `auditor`, `quantcore`, `cli`).
* React 18 frontend with Tailwind, Apollo, TanStack Query, ReactFlow.
* Strategy DSL parser + compiler + evaluator.
* 14 indicators (sma, ema, rsi, macd, bollinger, atr, stochastic,
  adx, obv, vwap, aroon, cmf, donchian, ichimoku, keltner, supertrend).
* Backtest engine with fee + slippage + risk caps.
* Multi-channel notifier (Telegram, Discord, Slack, PagerDuty,
  email, webhook).
* Multi-chain ingestor (EVM, Solana, Cosmos).
* ML pipeline (anomaly + sentiment + price prediction).
* docker-compose dev + production manifests, Kustomize bundle.
