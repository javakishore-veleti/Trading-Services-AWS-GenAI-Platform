#!/usr/bin/env bash
# Start the Agno calculator as its own process.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/../../.." && pwd)"
RUN="$DIR/.run"

# shellcheck disable=SC1091
source "$ROOT/CICD/Local/scripts/env.sh"
export LITELLM_BASE_URL="${LITELLM_BASE_URL:-http://127.0.0.1:4000}"
export LITELLM_MODEL_NAME="${LITELLM_MODEL_NAME:-deepseek-r1-8b-ollama}"
export LITELLM_API_KEY="${LITELLM_API_KEY:-${LITELLM_MASTER_KEY:-}}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it from https://docs.astral.sh/uv/." >&2
  exit 1
fi

mkdir -p "$RUN/logs"

name="calculator-agent"
port=8401
if curl -fsS "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
  echo "${name} already listening on ${port}"
else
  uv sync --project "$DIR/${name}" --quiet
  nohup uv run --directory "$DIR/${name}" python app.py >"$RUN/logs/${name}.log" 2>&1 &
  echo $! >"$RUN/${name}.pid"
  echo "Starting ${name} on ${port}"
fi

ready=0
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do
  if curl -fsS "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 1
done

if [ "$ready" -ne 1 ]; then
  echo "The Agno calculator did not become healthy. See $RUN/logs." >&2
  exit 1
fi

echo "Agno calculator is up."
echo "calculator-agent   http://127.0.0.1:8401/health"
