#!/usr/bin/env bash
# Start each MCP server as its own process. Each app has its own uv project.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN="$DIR/.run"
mkdir -p "$RUN/logs"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it from https://docs.astral.sh/uv/." >&2
  exit 1
fi

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

start_one trades-catalog-mcp 8101
start_one trades-offers-mcp 8102
start_one trades-orders-mcp 8103
start_one trades-partners-mcp 8104
start_one traders-master-data-mcp 8105
start_one traders-analytics-mcp 8106

ready=0
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  ready=0
  for port in 8101 8102 8103 8104 8105 8106; do
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
  echo "One or more MCP servers did not become healthy. See $RUN/logs." >&2
  exit 1
fi

echo "MCP servers are up."
echo "trades-catalog-mcp        http://127.0.0.1:8101/health   MCP http://127.0.0.1:8101/mcp"
echo "trades-offers-mcp         http://127.0.0.1:8102/health   MCP http://127.0.0.1:8102/mcp"
echo "trades-orders-mcp         http://127.0.0.1:8103/health   MCP http://127.0.0.1:8103/mcp"
echo "trades-partners-mcp       http://127.0.0.1:8104/health   MCP http://127.0.0.1:8104/mcp"
echo "traders-master-data-mcp   http://127.0.0.1:8105/health   MCP http://127.0.0.1:8105/mcp"
echo "traders-analytics-mcp     http://127.0.0.1:8106/health   MCP http://127.0.0.1:8106/mcp"
