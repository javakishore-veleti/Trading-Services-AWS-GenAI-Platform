#!/usr/bin/env bash
# Start each LangGraph desk agent as its own process. Each app has its own uv project.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/../../.." && pwd)"
RUN="$DIR/.run"

# shellcheck disable=SC1091
source "$ROOT/CICD/Local/scripts/env.sh"
export REDIS_PASSWORD="${REDIS_PASSWORD:-redis}"
export REDIS_PORT="${REDIS_PORT:-6379}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it from https://docs.astral.sh/uv/." >&2
  exit 1
fi

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

start_one trading-desk-offers 8201
start_one trading-desk-bffs 8202
start_one trading-desk-io 8203
start_one trading-desk-order 8204
start_one trading-desk-platforms 8205

ready=0
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  ready=0
  for port in 8201 8202 8203 8204 8205; do
    if curl -fsS "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
      ready=$((ready + 1))
    fi
  done
  if [ "$ready" -eq 5 ]; then
    break
  fi
  sleep 1
done

if [ "$ready" -ne 5 ]; then
  echo "One or more desk agents did not become healthy. See $RUN/logs." >&2
  exit 1
fi

echo "Desk agents are up."
echo "trading-desk-offers      http://127.0.0.1:8201/health"
echo "trading-desk-bffs        http://127.0.0.1:8202/health"
echo "trading-desk-io          http://127.0.0.1:8203/health"
echo "trading-desk-order       http://127.0.0.1:8204/health"
echo "trading-desk-platforms   http://127.0.0.1:8205/health"
