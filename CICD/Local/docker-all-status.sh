#!/usr/bin/env bash
# Show Postgres, then LiteLLM.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POSTGRES_FILE="$DIR/Postgres/docker-compose.yaml"
LITELLM_FILE="$DIR/LiteLLM/docker-compose.yaml"

echo "Postgres"
docker compose -f "$POSTGRES_FILE" ps

echo
echo "LiteLLM"
docker compose -f "$LITELLM_FILE" ps
