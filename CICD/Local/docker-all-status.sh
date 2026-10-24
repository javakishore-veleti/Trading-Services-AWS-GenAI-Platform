#!/usr/bin/env bash
# Show Postgres, Redis, vLLM, then LiteLLM.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POSTGRES_FILE="$DIR/Postgres/docker-compose.yaml"
REDIS_FILE="$DIR/Redis/docker-compose.yaml"
CLICKHOUSE_FILE="$DIR/ClickHouse/docker-compose.yaml"
LENS_FILE="$DIR/Lens/docker-compose.yaml"
VLLM_FILE="$DIR/vLLM/docker-compose.yaml"
LITELLM_FILE="$DIR/LiteLLM/docker-compose.yaml"

POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-postgres}"
REDIS_PORT="${REDIS_PORT:-6379}"
VLLM_PORT="${VLLM_PORT:-8000}"
LENS_PORT="${LENS_PORT:-4318}"
LITELLM_PORT="${LITELLM_PORT:-4000}"

echo "Postgres"
docker compose -f "$POSTGRES_FILE" ps
echo "postgresql://${POSTGRES_USER}@127.0.0.1:${POSTGRES_PORT}/${POSTGRES_DB}"

echo
echo "Redis"
docker compose -f "$REDIS_FILE" ps
echo "redis://127.0.0.1:${REDIS_PORT}"

echo
echo "vLLM"
docker compose -f "$VLLM_FILE" ps
echo "http://127.0.0.1:${VLLM_PORT}/v1"

echo
echo "ClickHouse"
docker compose -f "$CLICKHOUSE_FILE" ps

echo
echo "Lens"
docker compose -f "$LENS_FILE" ps
echo "http://127.0.0.1:${LENS_PORT}/ui"
echo "http://127.0.0.1:${LITELLM_PORT}/ui/lens/"

echo
echo "LiteLLM"
docker compose -f "$LITELLM_FILE" ps
echo "http://127.0.0.1:${LITELLM_PORT}/ui"
echo "http://127.0.0.1:${LITELLM_PORT}/"
