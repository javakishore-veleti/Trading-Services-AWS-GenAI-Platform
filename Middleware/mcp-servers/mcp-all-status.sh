#!/usr/bin/env bash
# Report whether each MCP server answers /health.
set -euo pipefail

status_one() {
  local name="$1"
  local port="$2"
  if curl -fsS "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
    echo "up    ${name}  http://127.0.0.1:${port}/health"
  else
    echo "down  ${name}  http://127.0.0.1:${port}/health"
  fi
}

status_one trades-catalog-mcp 8101
status_one trades-offers-mcp 8102
status_one trades-orders-mcp 8103
status_one trades-partners-mcp 8104
status_one traders-master-data-mcp 8105
status_one traders-analytics-mcp 8106
