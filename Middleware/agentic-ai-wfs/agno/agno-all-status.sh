#!/usr/bin/env bash
# Report whether the Agno calculator answers /health.
set -euo pipefail

if curl -fsS "http://127.0.0.1:8401/health" >/dev/null 2>&1; then
  echo "up    calculator-agent  http://127.0.0.1:8401/health"
else
  echo "down  calculator-agent  http://127.0.0.1:8401/health"
fi
