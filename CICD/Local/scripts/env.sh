# Shared paths, .env loading, and the local team list. Source this file.
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_DIR="$(cd "$SCRIPTS_DIR/.." && pwd)"
ROOT="$(cd "$LOCAL_DIR/../.." && pwd)"

load_env() {
  if [ ! -f "$ROOT/.env" ]; then
    return
  fi
  local line key value
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      ''|\#*) continue ;;
      *=*) ;;
      *) continue ;;
    esac
    key="${line%%=*}"
    value="${line#*=}"
    case "$value" in
      \'*\') value="${value#\'}"; value="${value%\'}" ;;
      \"*\") value="${value#\"}"; value="${value%\"}" ;;
    esac
    export "$key=$value"
  done < "$ROOT/.env"
}
load_env

LOCAL_TEAMS=(
  "222043-sales-offers"
  "222044-sales-bffs"
  "222045-sales-io"
  "221373-sales-order"
  "222045-sales-platforms"
)
export LOCAL_TEAM_NAMES="$(printf '%s\n' "${LOCAL_TEAMS[@]}")"

POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-postgres}"
REDIS_PORT="${REDIS_PORT:-6379}"
PGVECTOR_PORT="${PGVECTOR_PORT:-5433}"
PGVECTOR_USER="${PGVECTOR_USER:-pgvector}"
PGVECTOR_DB="${PGVECTOR_DB:-pgvector}"
PGVECTOR_CONNECTOR_PORT="${PGVECTOR_CONNECTOR_PORT:-8001}"
VLLM_PORT="${VLLM_PORT:-8000}"
LITELLM_PORT="${LITELLM_PORT:-4000}"
export LITELLM_UI="http://127.0.0.1:${LITELLM_PORT}/ui"
export LITELLM_DOCS="http://127.0.0.1:${LITELLM_PORT}/"
