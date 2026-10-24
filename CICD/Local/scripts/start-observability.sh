#!/usr/bin/env bash
# Start Langfuse and Phoenix as containers. Nothing is installed on the Mac.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

if ! docker network inspect trading-services-local >/dev/null 2>&1; then
  docker network create trading-services-local
fi

postgres_id="$(docker compose -f "$LOCAL_DIR/Postgres/docker-compose.yaml" ps -q postgres)"
redis_id="$(docker compose -f "$LOCAL_DIR/Redis/docker-compose.yaml" ps -q redis)"
if [ -z "$postgres_id" ] || [ -z "$redis_id" ]; then
  echo "Platform Postgres and Redis must be running before Langfuse." >&2
  exit 1
fi

echo "Creating the langfuse database on the platform Postgres."
docker exec -i -e PGPASSWORD="$POSTGRES_PASSWORD" "$postgres_id" \
  psql -U "$POSTGRES_USER" -d postgres -v ON_ERROR_STOP=1 <<'SQL'
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'langfuse') THEN
    CREATE ROLE langfuse LOGIN PASSWORD 'langfuse';
  ELSE
    ALTER ROLE langfuse WITH LOGIN PASSWORD 'langfuse';
  END IF;
END
$$;
SQL
langfuse_db="$(docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" "$postgres_id" \
  psql -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = 'langfuse'")"
if [ "$langfuse_db" != "1" ]; then
  docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" "$postgres_id" \
    psql -U "$POSTGRES_USER" -d postgres -v ON_ERROR_STOP=1 \
    -c "CREATE DATABASE langfuse OWNER langfuse"
fi

echo "Starting Langfuse. The first image download can take a long time."
docker compose -f "$LOCAL_DIR/Langfuse/docker-compose.yaml" up -d --wait --wait-timeout 300 --remove-orphans
docker volume rm trading-services-genai-langfuse_langfuse_postgres_data \
  trading-services-genai-langfuse_langfuse_redis_data >/dev/null 2>&1 || true

echo "Starting Phoenix."
docker compose -f "$LOCAL_DIR/Phoenix/docker-compose.yaml" up -d

ready=0
for _ in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:${LANGFUSE_PORT}/api/public/health" >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 5
done
if [ "$ready" -ne 1 ]; then
  echo "Langfuse did not become ready." >&2
  docker logs --tail 30 trading-services-genai-langfuse-langfuse-web-1 >&2 || true
  exit 1
fi

ready=0
for _ in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:${PHOENIX_PORT}/health" >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 5
done
if [ "$ready" -ne 1 ]; then
  echo "Phoenix did not become ready." >&2
  exit 1
fi

echo "Langfuse:"
echo "http://127.0.0.1:${LANGFUSE_PORT}"
echo "Sign in as admin@example.com. The local password is langfuse."
echo "Phoenix:"
echo "http://127.0.0.1:${PHOENIX_PORT}"
