#!/usr/bin/env bash
# Start Open WebUI. It calls LiteLLM, so the gateway must already be up.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

if ! docker network inspect trading-services-local >/dev/null 2>&1; then
  docker network create trading-services-local
fi

litellm_id="$(docker compose -f "$LOCAL_DIR/LiteLLM/docker-compose.yaml" ps -q litellm)"
if [ -z "$litellm_id" ]; then
  echo "LiteLLM must be running before Open WebUI." >&2
  exit 1
fi

: "${LITELLM_MASTER_KEY:?LITELLM_MASTER_KEY is required}"

echo "Starting Open WebUI. The first image download can take a long time."
docker compose -f "$LOCAL_DIR/OpenWebUI/docker-compose.yaml" up -d

ready=0
for _ in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:${OPENWEBUI_PORT}/health" >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 5
done
if [ "$ready" -ne 1 ]; then
  echo "Open WebUI did not become ready." >&2
  docker logs --tail 40 trading-services-genai-openwebui-openwebui-1 >&2 || true
  exit 1
fi

echo "Open WebUI:"
echo "http://127.0.0.1:${OPENWEBUI_PORT}"
echo "Sign in as ${OPENWEBUI_ADMIN_EMAIL}. The local password is ${OPENWEBUI_ADMIN_PASSWORD}."
