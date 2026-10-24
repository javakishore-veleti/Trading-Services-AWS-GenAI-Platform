#!/usr/bin/env bash
# Start the LiteLLM proxy, then the connector that routes each team to its database.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

echo "Starting LiteLLM..."
docker compose -f "$LOCAL_DIR/LiteLLM/docker-compose.yaml" up -d --force-recreate --wait --wait-timeout 300

echo "Starting the pgvector connector..."
docker compose -f "$LOCAL_DIR/pgvector-connector/docker-compose.yaml" up -d --build --wait --wait-timeout 180
echo "pgvector connector:"
echo "http://127.0.0.1:${PGVECTOR_CONNECTOR_PORT}/health"
