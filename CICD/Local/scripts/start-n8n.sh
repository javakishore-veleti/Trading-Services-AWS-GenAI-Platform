#!/usr/bin/env bash
# Start n8n when N8N_ENABLED is true. The default is false.
# Workflows are stored in the platform Postgres database n8n.
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"

if [ "$N8N_ENABLED" != "true" ]; then
  echo "n8n was not started. N8N_ENABLED is false."
  exit 0
fi

if ! docker network inspect trading-services-local >/dev/null 2>&1; then
  docker network create trading-services-local
fi

postgres_id="$(docker compose -f "$LOCAL_DIR/Postgres/docker-compose.yaml" ps -q postgres)"
if [ -z "$postgres_id" ]; then
  echo "Platform Postgres must be running before n8n." >&2
  exit 1
fi

echo "Creating the n8n database on the platform Postgres."
docker exec -i -e PGPASSWORD="$POSTGRES_PASSWORD" "$postgres_id" \
  psql -U "$POSTGRES_USER" -d postgres -v ON_ERROR_STOP=1 <<'SQL'
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'n8n') THEN
    CREATE ROLE n8n LOGIN PASSWORD 'n8n';
  ELSE
    ALTER ROLE n8n WITH LOGIN PASSWORD 'n8n';
  END IF;
END
$$;
SQL
n8n_db="$(docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" "$postgres_id" \
  psql -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = 'n8n'")"
if [ "$n8n_db" != "1" ]; then
  docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" "$postgres_id" \
    psql -U "$POSTGRES_USER" -d postgres -v ON_ERROR_STOP=1 \
    -c "CREATE DATABASE n8n OWNER n8n"
fi

echo "Starting n8n. The first image download can take a long time."
docker compose -f "$LOCAL_DIR/n8n/docker-compose.yaml" up -d

ready=0
for _ in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:${N8N_PORT}/healthz" >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 5
done
if [ "$ready" -ne 1 ]; then
  echo "n8n did not become ready." >&2
  docker logs --tail 40 trading-services-genai-n8n-n8n-1 >&2 || true
  exit 1
fi

echo "n8n:"
echo "http://127.0.0.1:${N8N_PORT}"
echo "The first visit asks you to create the owner account."
