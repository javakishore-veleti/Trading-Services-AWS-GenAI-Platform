#!/usr/bin/env bash
set -euo pipefail

if curl -fsS "http://127.0.0.1:8601/health" >/dev/null 2>&1; then
  echo "up    traders-agentic-wfs  http://127.0.0.1:8601/health"
else
  echo "down  traders-agentic-wfs  http://127.0.0.1:8601/health"
fi
