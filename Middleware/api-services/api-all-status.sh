#!/usr/bin/env bash
# Report whether each FX API service answers /health.
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

status_one app-auth-service 8501
status_one traders-service 8502
status_one customer-service 8503
status_one trades-catalog-service 8504
status_one trades-offers-services 8505
status_one trades-orders-service 8506
