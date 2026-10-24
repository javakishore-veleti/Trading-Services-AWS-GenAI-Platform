#!/usr/bin/env bash
# Start Postgres, Redis, and pgvector. Start vLLM when this machine has an NVIDIA GPU.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

if ! docker network inspect trading-services-local >/dev/null 2>&1; then
  docker network create trading-services-local
fi

echo "Starting Postgres, Redis, and pgvector. Any one may become ready first."
docker compose -f "$LOCAL_DIR/Postgres/docker-compose.yaml" up -d --wait --wait-timeout 120 &
postgres_pid=$!
docker compose -f "$LOCAL_DIR/Redis/docker-compose.yaml" up -d --wait --wait-timeout 120 &
redis_pid=$!
docker compose -f "$LOCAL_DIR/pgvector/docker-compose.yaml" up -d --wait --wait-timeout 120 &
pgvector_pid=$!
vllm_pid=""
if docker info 2>/dev/null | grep -Eqi 'nvidia'; then
  echo "Starting vLLM as well. The first model download can take a long time."
  docker compose -f "$LOCAL_DIR/vLLM/docker-compose.yaml" up -d &
  vllm_pid=$!
else
  echo "vLLM was not started. vllm/vllm-openai:v0.10.2 needs an NVIDIA GPU, and this machine does not have one."
fi

postgres_status=0
redis_status=0
pgvector_status=0
vllm_status=0
wait "$postgres_pid" || postgres_status=$?
wait "$redis_pid" || redis_status=$?
wait "$pgvector_pid" || pgvector_status=$?
if [ -n "$vllm_pid" ]; then
  wait "$vllm_pid" || vllm_status=$?
fi
if [ "$postgres_status" -ne 0 ] || [ "$redis_status" -ne 0 ] || [ "$pgvector_status" -ne 0 ]; then
  echo "Postgres, Redis, or pgvector did not become ready." >&2
  exit 1
fi
if [ "$vllm_status" -ne 0 ]; then
  echo "vLLM did not start. LiteLLM will still start, and calls to deepseek-r1-qwen3-8b will fail until vLLM is up." >&2
fi

echo "Postgres is up. Connect from a database client:"
echo "postgresql://${POSTGRES_USER}@127.0.0.1:${POSTGRES_PORT}/${POSTGRES_DB}"
echo "Redis is up. Connect from a Redis client:"
echo "redis://127.0.0.1:${REDIS_PORT}"
echo "pgvector is up. Connect from a database client:"
echo "postgresql://${PGVECTOR_USER}@127.0.0.1:${PGVECTOR_PORT}/${PGVECTOR_DB}"
if [ -n "$vllm_pid" ] && [ "$vllm_status" -eq 0 ]; then
  echo "vLLM OpenAI API:"
  echo "http://127.0.0.1:${VLLM_PORT}/v1"
fi
