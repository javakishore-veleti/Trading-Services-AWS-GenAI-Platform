#!/usr/bin/env bash
# Start Text Embeddings Inference. The first model download can take a long time.
# https://huggingface.co/docs/text-embeddings-inference/supported_models
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

if ! docker network inspect trading-services-local >/dev/null 2>&1; then
  docker network create trading-services-local
fi

case "$(uname -m)" in
  arm64|aarch64)
    TEI_IMAGE="${TEI_IMAGE:-ghcr.io/huggingface/text-embeddings-inference:cpu-arm64-1.9}"
    TEI_PLATFORM="${TEI_PLATFORM:-linux/arm64}"
    ;;
  x86_64|amd64)
    TEI_IMAGE="${TEI_IMAGE:-ghcr.io/huggingface/text-embeddings-inference:cpu-1.9}"
    TEI_PLATFORM="${TEI_PLATFORM:-linux/amd64}"
    ;;
  *)
    echo "TEI was not started. The supported-models page has no CPU image for $(uname -m)." >&2
    exit 1
    ;;
esac
export TEI_IMAGE TEI_PLATFORM

echo "Starting TEI (${TEI_IMAGE}). The first download of ${TEI_MODEL} can take a long time."
docker compose -f "$LOCAL_DIR/TEI/docker-compose.yaml" up -d

ready=0
for _ in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:${TEI_PORT}/health" >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 5
done
if [ "$ready" -ne 1 ]; then
  echo "TEI did not become ready." >&2
  exit 1
fi

python3 - <<PY
import json, urllib.request
body = json.dumps({"inputs": "hello world"}).encode()
req = urllib.request.Request(
    "http://127.0.0.1:${TEI_PORT}/embed",
    data=body,
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=60) as resp:
    data = json.load(resp)
if data and isinstance(data[0], list):
    data = data[0]
if not data or not isinstance(data[0], (int, float)):
    raise SystemExit("TEI /embed did not return a vector.")
if len(data) != 1024:
    raise SystemExit(f"TEI returned {len(data)} numbers, expected 1024.")
print("TEI /embed returned a vector of 1024 numbers.")
PY

echo "TEI embed API:"
echo "http://127.0.0.1:${TEI_PORT}/embed"
