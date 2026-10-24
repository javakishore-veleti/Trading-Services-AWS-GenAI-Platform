#!/usr/bin/env bash
# Start Postgres, Redis, and pgvector. Model engines start from start-llm-models.sh.
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

postgres_status=0
redis_status=0
pgvector_status=0
wait "$postgres_pid" || postgres_status=$?
wait "$redis_pid" || redis_status=$?
wait "$pgvector_pid" || pgvector_status=$?
if [ "$postgres_status" -ne 0 ] || [ "$redis_status" -ne 0 ] || [ "$pgvector_status" -ne 0 ]; then
  echo "Postgres, Redis, or pgvector did not become ready." >&2
  exit 1
fi

echo "Postgres is up. Connect from a database client:"
echo "postgresql://${POSTGRES_USER}@127.0.0.1:${POSTGRES_PORT}/${POSTGRES_DB}"
echo "Redis is up. Connect from a Redis client:"
echo "redis://127.0.0.1:${REDIS_PORT}"
echo "pgvector is up. Connect from a database client:"
echo "postgresql://${PGVECTOR_USER}@127.0.0.1:${PGVECTOR_PORT}/${PGVECTOR_DB}"
