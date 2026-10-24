#!/usr/bin/env bash
# Stop LiteLLM first, then vLLM, Redis, and Postgres, and delete their volumes.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POSTGRES_FILE="$DIR/Postgres/docker-compose.yaml"
REDIS_FILE="$DIR/Redis/docker-compose.yaml"
CLICKHOUSE_FILE="$DIR/ClickHouse/docker-compose.yaml"
LENS_FILE="$DIR/Lens/docker-compose.yaml"
VLLM_FILE="$DIR/vLLM/docker-compose.yaml"
LITELLM_FILE="$DIR/LiteLLM/docker-compose.yaml"

echo "Stopping LiteLLM..."
docker compose -f "$LITELLM_FILE" down --volumes

echo "Stopping Lens..."
docker compose -f "$LENS_FILE" down --volumes

echo "Stopping ClickHouse and deleting its data volume..."
docker compose -f "$CLICKHOUSE_FILE" down --volumes

echo "Stopping vLLM and deleting its model cache..."
docker compose -f "$VLLM_FILE" down --volumes

echo "Stopping Redis and deleting its data volume..."
docker compose -f "$REDIS_FILE" down --volumes

echo "Stopping Postgres and deleting its data volume..."
docker compose -f "$POSTGRES_FILE" down --volumes

echo "Local containers are down and their volumes are deleted."
