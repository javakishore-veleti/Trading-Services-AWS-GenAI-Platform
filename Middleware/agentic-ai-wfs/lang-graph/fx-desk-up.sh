#!/usr/bin/env bash
# Start the LangGraph FX question service. The API services must already be up.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$DIR/traders-agentic-wfs"
RUN="$APP/.run"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it from https://docs.astral.sh/uv/." >&2
  exit 1
fi

export AUTH_BASE_URL="${AUTH_BASE_URL:-http://127.0.0.1:8501}"
export TRADERS_BASE_URL="${TRADERS_BASE_URL:-http://127.0.0.1:8502}"
export CUSTOMER_BASE_URL="${CUSTOMER_BASE_URL:-http://127.0.0.1:8503}"
export CATALOG_BASE_URL="${CATALOG_BASE_URL:-http://127.0.0.1:8504}"
export OFFERS_BASE_URL="${OFFERS_BASE_URL:-http://127.0.0.1:8505}"

mkdir -p "$RUN/logs"

if curl -fsS "http://127.0.0.1:8601/health" >/dev/null 2>&1; then
  echo "traders-agentic-wfs already listening on 8601"
  exit 0
fi

uv sync --project "$APP" --quiet
nohup uv run --directory "$APP" python app.py >"$RUN/logs/traders-agentic-wfs.log" 2>&1 &
echo $! >"$RUN/traders-agentic-wfs.pid"
echo "Starting traders-agentic-wfs on 8601"

for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do
  if curl -fsS "http://127.0.0.1:8601/health" >/dev/null 2>&1; then
    echo "traders-agentic-wfs  http://127.0.0.1:8601/health"
    exit 0
  fi
  sleep 1
done

echo "traders-agentic-wfs did not become healthy. See $RUN/logs." >&2
exit 1
