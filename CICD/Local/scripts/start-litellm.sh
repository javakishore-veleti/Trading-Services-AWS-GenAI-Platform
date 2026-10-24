#!/usr/bin/env bash
# Start the LiteLLM proxy, then the connector that routes each team to its database.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

# The container has its own ollama. The host command is required only for the proxy path.
CONFIGURE_OLLAMA=true
if [ "$OLLAMA_ENABLED" != "true" ] && ! command -v ollama >/dev/null 2>&1; then
  CONFIGURE_OLLAMA=false
  echo "Ollama is not installed. LiteLLM will not list an Ollama model."
fi

python3 - "$LOCAL_DIR/LiteLLM/config.yaml" "$LOCAL_DIR/LiteLLM/config.runtime.yaml" "$CONFIGURE_OLLAMA" <<'PY'
import pathlib, sys
source, dest, keep = sys.argv[1:]
text = pathlib.Path(source).read_text()
start = text.find("  # ollama-models-start\n")
end = text.find("  # ollama-models-end\n")
if start == -1 or end == -1 or end < start:
    raise SystemExit("Ollama model markers are missing from the LiteLLM config.")
end = text.find("\n", end) + 1
if keep != "true":
    text = text[:start] + text[end:]
pathlib.Path(dest).write_text(text)
PY

echo "Starting LiteLLM..."
docker compose -f "$LOCAL_DIR/LiteLLM/docker-compose.yaml" up -d --force-recreate --wait --wait-timeout 300

if [ "$CONFIGURE_OLLAMA" = "false" ]; then
  python3 - <<'PY'
import json, os, urllib.request
key = os.environ["LITELLM_MASTER_KEY"]
def call(method, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:4000" + path,
        data=data,
        method=method,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}
info = call("GET", "/v1/model/info")
for item in info.get("data", []):
    params = item.get("litellm_params") or {}
    model = str(params.get("model") or "")
    base = str(params.get("api_base") or "")
    if model.startswith("ollama/") or "ollama:" in base:
        mid = (item.get("model_info") or {}).get("id")
        if mid:
            call("POST", "/model/delete", {"id": mid})
PY
fi

echo "Starting the pgvector connector..."
docker compose -f "$LOCAL_DIR/pgvector-connector/docker-compose.yaml" up -d --build --wait --wait-timeout 180
echo "pgvector connector:"
echo "http://127.0.0.1:${PGVECTOR_CONNECTOR_PORT}/health"
