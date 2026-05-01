#!/usr/bin/env bash
# Minimal wait-for-it: polls TCP host:port until reachable.
set -euo pipefail
HOST=${1:?usage: wait-for-it.sh host:port}
HOST=${HOST%:*}
PORT=${1#*:}
TIMEOUT=${WAIT_TIMEOUT:-90}
STARTED=$(date +%s)
while true; do
  if (echo > "/dev/tcp/$HOST/$PORT") 2>/dev/null; then
    echo "$1 is available"
    exit 0
  fi
  NOW=$(date +%s)
  if (( NOW - STARTED > TIMEOUT )); then
    echo "Timeout waiting for $1" >&2
    exit 1
  fi
  sleep 1
done
