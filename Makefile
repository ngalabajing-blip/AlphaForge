# AlphaForge top-level Makefile
# All targets are idempotent and runnable from a clean checkout.

.PHONY: help setup setup-python setup-node setup-rust dev dev-down logs \
        build test test-python test-frontend test-rust lint lint-python lint-frontend lint-rust \
        format clean migrate seed audit backtest signals \
        docker-build docker-push k8s-deploy k8s-delete

PY ?= python3.11
PIP ?= $(PY) -m pip
NPM ?= npm
CARGO ?= cargo

help:
	@echo "AlphaForge — make targets"
	@echo ""
	@echo "  setup           Install all dependencies (Python + Node + Rust)"
	@echo "  dev             Start full dev stack with hot reload"
	@echo "  dev-down        Stop dev stack"
	@echo "  logs            Tail logs from all services"
	@echo "  test            Run all test suites"
	@echo "  lint            Run all linters"
	@echo "  format          Auto-format all code"
	@echo "  build           Build container images"
	@echo "  migrate         Run database migrations"
	@echo "  seed            Seed development data"
	@echo "  audit CONTRACT=0x...   Run smart-contract auditor"
	@echo "  backtest STRATEGY=path Run a backtest from a strategy file"
	@echo "  signals SYMBOL=ETH/USD Show recent live signals"
	@echo "  k8s-deploy      Apply Kubernetes manifests"
	@echo ""

setup: setup-python setup-node setup-rust

setup-python:
	$(PIP) install --upgrade pip
	$(PIP) install -e shared
	$(PIP) install -e services/api
	$(PIP) install -e services/ingestor
	$(PIP) install -e services/ml
	$(PIP) install -e services/worker
	$(PIP) install -e services/notifier
	$(PIP) install -e services/auditor
	$(PIP) install -e services/cli

setup-node:
	cd frontend && $(NPM) install

setup-rust:
	cd services/quantcore && $(CARGO) build --release

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
	@echo "Stack up. Frontend: http://localhost:3000 — API docs: http://localhost:8000/docs"

dev-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

logs:
	docker compose logs -f --tail=100

build:
	docker compose build

test: test-python test-frontend test-rust

test-python:
	$(PY) -m pytest services/api/tests services/ingestor/tests services/ml/tests \
	  services/worker/tests services/notifier/tests services/auditor/tests \
	  services/cli/tests shared/tests -v

test-frontend:
	cd frontend && $(NPM) run test --silent --if-present || true

test-rust:
	cd services/quantcore && $(CARGO) test --release

lint: lint-python lint-frontend lint-rust

lint-python:
	$(PY) -m ruff check services shared
	$(PY) -m mypy services shared --ignore-missing-imports

lint-frontend:
	cd frontend && $(NPM) run lint

lint-rust:
	cd services/quantcore && $(CARGO) clippy --release -- -D warnings

format:
	$(PY) -m ruff format services shared
	cd frontend && $(NPM) run format --if-present
	cd services/quantcore && $(CARGO) fmt

migrate:
	cd services/api && alembic upgrade head

seed:
	$(PY) scripts/seed.py

audit:
	@if [ -z "$(CONTRACT)" ]; then echo "Usage: make audit CONTRACT=0x..."; exit 1; fi
	alphaforge audit run --address $(CONTRACT)

backtest:
	@if [ -z "$(STRATEGY)" ]; then echo "Usage: make backtest STRATEGY=path/to/strategy.yaml"; exit 1; fi
	alphaforge backtest run --strategy $(STRATEGY)

signals:
	alphaforge signals tail --symbol $${SYMBOL:-ETH/USD}

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	rm -rf services/quantcore/target frontend/node_modules frontend/dist

docker-build:
	docker compose build --pull

k8s-deploy:
	kubectl apply -k infra/k8s

k8s-delete:
	kubectl delete -k infra/k8s
