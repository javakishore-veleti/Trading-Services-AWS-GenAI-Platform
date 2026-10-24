#!/usr/bin/env bash
# Report whether each Strands agent answers /health.
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

status_one calculator-agent 8301
status_one loan-buddy-agent 8302
