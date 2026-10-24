#!/usr/bin/env bash
# Start Postgres, wait until it is up, then start LiteLLM.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POSTGRES_FILE="$DIR/Postgres/docker-compose.yaml"
LITELLM_FILE="$DIR/LiteLLM/docker-compose.yaml"

echo "Starting Postgres..."
docker compose -f "$POSTGRES_FILE" up -d --wait --wait-timeout 120

echo "Postgres is up. Starting LiteLLM..."
docker compose -f "$LITELLM_FILE" up -d --wait --wait-timeout 300

echo "LiteLLM is up on port ${LITELLM_PORT:-4000}."
