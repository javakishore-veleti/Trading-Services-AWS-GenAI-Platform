#!/usr/bin/env bash
# Stop LiteLLM first, then Postgres.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POSTGRES_FILE="$DIR/Postgres/docker-compose.yaml"
LITELLM_FILE="$DIR/LiteLLM/docker-compose.yaml"

echo "Stopping LiteLLM..."
docker compose -f "$LITELLM_FILE" down

echo "Stopping Postgres..."
docker compose -f "$POSTGRES_FILE" down

echo "Local containers are down."
