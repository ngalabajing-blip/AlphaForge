#!/usr/bin/env bash
set -euo pipefail

# Apply migrations and seed demo data into a running Postgres.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/services/api"

echo "→ alembic upgrade head"
alembic upgrade head

echo "→ seed demo data"
python "$ROOT/scripts/seed.py"

echo "✓ database ready"
