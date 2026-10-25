#!/usr/bin/env bash
# Start the FX API services. Each one is its own process.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/../.." && pwd)"
RUN="$DIR/.run"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it from https://docs.astral.sh/uv/." >&2
  exit 1
fi

export DATASETS_DIR="$ROOT/CICD/Local/DataSets"
export AUTH_BASE_URL="${AUTH_BASE_URL:-http://127.0.0.1:8501}"
export TRADER_PASSWORD="${TRADER_PASSWORD:-local-trader}"

mkdir -p "$RUN/logs"

start_one() {
  local name="$1"
  local port="$2"
  if curl -fsS "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
    echo "${name} already listening on ${port}"
    return
  fi
  uv sync --project "$DIR/${name}" --quiet
  nohup uv run --directory "$DIR/${name}" python app.py >"$RUN/logs/${name}.log" 2>&1 &
  echo $! >"$RUN/${name}.pid"
  echo "Starting ${name} on ${port}"
}

start_one app-auth-service 8501
start_one traders-service 8502
start_one customer-service 8503
start_one trades-catalog-service 8504
start_one trades-offers-services 8505
start_one trades-orders-service 8506

ready=0
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do
  ready=0
  for port in 8501 8502 8503 8504 8505 8506; do
    if curl -fsS "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
      ready=$((ready + 1))
    fi
  done
  if [ "$ready" -eq 6 ]; then
    break
  fi
  sleep 1
done

if [ "$ready" -ne 6 ]; then
  echo "One or more API services did not become healthy. See $RUN/logs." >&2
  exit 1
fi

echo "API services are up."
echo "app-auth-service        http://127.0.0.1:8501/health"
echo "traders-service         http://127.0.0.1:8502/health"
echo "customer-service        http://127.0.0.1:8503/health"
echo "trades-catalog-service  http://127.0.0.1:8504/health"
echo "trades-offers-services  http://127.0.0.1:8505/health"
echo "trades-orders-service   http://127.0.0.1:8506/health"
