#!/usr/bin/env bash
# Show Postgres, Redis, each model engine, then LiteLLM.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/scripts/env.sh"
POSTGRES_FILE="$DIR/Postgres/docker-compose.yaml"
REDIS_FILE="$DIR/Redis/docker-compose.yaml"
PGVECTOR_FILE="$DIR/pgvector/docker-compose.yaml"
PGVECTOR_CONNECTOR_FILE="$DIR/pgvector-connector/docker-compose.yaml"
VLLM_FILE="$DIR/vLLM/docker-compose.yaml"
SGLANG_FILE="$DIR/SGLang/docker-compose.yaml"
OLLAMA_FILE="$DIR/Ollama/docker-compose.yaml"
OLLAMA_PROXY_FILE="$DIR/OllamaProxy/docker-compose.yaml"
TEI_FILE="$DIR/TEI/docker-compose.yaml"
LITELLM_FILE="$DIR/LiteLLM/docker-compose.yaml"

POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-postgres}"
REDIS_PORT="${REDIS_PORT:-6379}"
PGVECTOR_PORT="${PGVECTOR_PORT:-5433}"
PGVECTOR_USER="${PGVECTOR_USER:-pgvector}"
PGVECTOR_DB="${PGVECTOR_DB:-pgvector}"
PGVECTOR_CONNECTOR_PORT="${PGVECTOR_CONNECTOR_PORT:-8001}"
VLLM_PORT="${VLLM_PORT:-8000}"
SGLANG_PORT="${SGLANG_PORT:-30000}"
OLLAMA_PORT="${OLLAMA_PORT:-11434}"
TEI_PORT="${TEI_PORT:-8080}"
LITELLM_PORT="${LITELLM_PORT:-4000}"

echo "Postgres"
docker compose -f "$POSTGRES_FILE" ps
echo "postgresql://${POSTGRES_USER}@127.0.0.1:${POSTGRES_PORT}/${POSTGRES_DB}"

echo
echo "Redis"
docker compose -f "$REDIS_FILE" ps
echo "redis://127.0.0.1:${REDIS_PORT}"

echo
echo "pgvector"
docker compose -f "$PGVECTOR_FILE" ps
echo "postgresql://${PGVECTOR_USER}@127.0.0.1:${PGVECTOR_PORT}/${PGVECTOR_DB}"
docker exec trading-services-genai-pgvector-pgvector-1 \
  psql -U "${PGVECTOR_USER}" -d "${PGVECTOR_DB}" -At -c \
  "SELECT datname FROM pg_database WHERE datname LIKE 'vs\\_%' ORDER BY 1" 2>/dev/null || true

echo
echo "pgvector connector"
docker compose -f "$PGVECTOR_CONNECTOR_FILE" ps
echo "http://127.0.0.1:${PGVECTOR_CONNECTOR_PORT}/health"

echo
echo "vLLM"
docker compose -f "$VLLM_FILE" ps
echo "http://127.0.0.1:${VLLM_PORT}/v1"

echo
echo "SGLang"
docker compose -f "$SGLANG_FILE" ps
echo "http://127.0.0.1:${SGLANG_PORT}/v1"

echo
echo "Ollama"
echo "OLLAMA_ENABLED=${OLLAMA_ENABLED}  LiteLLM calls http://ollama:11434"
if [ "$OLLAMA_ENABLED" = "true" ]; then
  docker compose -f "$OLLAMA_FILE" ps
else
  docker compose -f "$OLLAMA_PROXY_FILE" ps
fi
echo "http://127.0.0.1:${OLLAMA_PORT}"

echo
echo "TEI"
docker compose -f "$TEI_FILE" ps
echo "http://127.0.0.1:${TEI_PORT}/embed"

echo
echo "LiteLLM"
docker compose -f "$LITELLM_FILE" ps
echo "http://127.0.0.1:${LITELLM_PORT}/ui"
echo "http://127.0.0.1:${LITELLM_PORT}/"
