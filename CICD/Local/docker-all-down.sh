#!/usr/bin/env bash
# Stop LiteLLM first, then vLLM, Redis, and Postgres, and delete their volumes.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Compose interpolates the connector file before it can stop the container.
source "$DIR/scripts/env.sh"
POSTGRES_FILE="$DIR/Postgres/docker-compose.yaml"
REDIS_FILE="$DIR/Redis/docker-compose.yaml"
PGVECTOR_FILE="$DIR/pgvector/docker-compose.yaml"
PGVECTOR_CONNECTOR_FILE="$DIR/pgvector-connector/docker-compose.yaml"
VLLM_FILE="$DIR/vLLM/docker-compose.yaml"
LITELLM_FILE="$DIR/LiteLLM/docker-compose.yaml"

echo "Stopping LiteLLM..."
docker compose -f "$LITELLM_FILE" down --volumes

echo "Stopping the pgvector connector..."
docker compose -f "$PGVECTOR_CONNECTOR_FILE" down --volumes

echo "Stopping pgvector and deleting its data volume..."
docker compose -f "$PGVECTOR_FILE" down --volumes

echo "Stopping vLLM and deleting its model cache..."
docker compose -f "$VLLM_FILE" down --volumes

echo "Stopping Redis and deleting its data volume..."
docker compose -f "$REDIS_FILE" down --volumes

echo "Stopping Postgres and deleting its data volume..."
docker compose -f "$POSTGRES_FILE" down --volumes

echo "Local containers are down and their volumes are deleted."
