#!/usr/bin/env bash
# Stop LiteLLM first, then Postgres, and delete their volumes.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POSTGRES_FILE="$DIR/Postgres/docker-compose.yaml"
LITELLM_FILE="$DIR/LiteLLM/docker-compose.yaml"

echo "Stopping LiteLLM..."
docker compose -f "$LITELLM_FILE" down --volumes

echo "Stopping Postgres and deleting its data volume..."
docker compose -f "$POSTGRES_FILE" down --volumes

echo "Local containers are down and their volumes are deleted."
