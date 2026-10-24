#!/usr/bin/env bash
# Start each Strands example as its own process. Each app has its own uv project.
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

mkdir -p "$RUN/logs" "$RUN/loan-images"

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

start_one calculator-agent 8301
start_one loan-buddy-agent 8302

ready=0
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do
  ready=0
  for port in 8301 8302; do
    if curl -fsS "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
      ready=$((ready + 1))
    fi
  done
  if [ "$ready" -eq 2 ]; then
    break
  fi
  sleep 1
done

if [ "$ready" -ne 2 ]; then
  echo "One or more Strands agents did not become healthy. See $RUN/logs." >&2
  exit 1
fi

echo "Strands agents are up."
echo "calculator-agent   http://127.0.0.1:8301/health"
echo "loan-buddy-agent   http://127.0.0.1:8302/health"
