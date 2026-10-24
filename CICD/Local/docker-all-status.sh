#!/usr/bin/env bash
# Show Postgres, then LiteLLM.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POSTGRES_FILE="$DIR/Postgres/docker-compose.yaml"
LITELLM_FILE="$DIR/LiteLLM/docker-compose.yaml"

POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-postgres}"
LITELLM_PORT="${LITELLM_PORT:-4000}"

echo "Postgres"
docker compose -f "$POSTGRES_FILE" ps
echo "postgresql://${POSTGRES_USER}@127.0.0.1:${POSTGRES_PORT}/${POSTGRES_DB}"

echo
echo "LiteLLM"
docker compose -f "$LITELLM_FILE" ps
echo "http://127.0.0.1:${LITELLM_PORT}/ui"
echo "http://127.0.0.1:${LITELLM_PORT}/"
