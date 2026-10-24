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
  "BU1000-trading-desk-offers"
  "BU1001-trading-desk-bffs"
  "BU1002-trading-desk-io"
  "BU1003-trading-desk-order"
  "BU1004-trading-desk-platforms"
)
export LOCAL_TEAM_NAMES="$(printf '%s\n' "${LOCAL_TEAMS[@]}")"

POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-postgres}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-redis}"
export POSTGRES_PASSWORD REDIS_PASSWORD
PGVECTOR_PORT="${PGVECTOR_PORT:-5433}"
PGVECTOR_USER="${PGVECTOR_USER:-pgvector}"
PGVECTOR_DB="${PGVECTOR_DB:-pgvector}"
PGVECTOR_CONNECTOR_PORT="${PGVECTOR_CONNECTOR_PORT:-8001}"
VLLM_PORT="${VLLM_PORT:-8000}"
SGLANG_PORT="${SGLANG_PORT:-30000}"
OLLAMA_PORT="${OLLAMA_PORT:-11434}"
TEI_PORT="${TEI_PORT:-8080}"
# Qwen3-Embedding-0.6B needs about 5 GB to load. This Docker VM is 7.6 GB and
# Langfuse is already running, so Docker kills that model. bge-small fits.
TEI_MODEL="${TEI_MODEL:-BAAI/bge-small-en-v1.5}"
TEI_EMBEDDING_DIM="${TEI_EMBEDDING_DIM:-384}"
export TEI_PORT TEI_MODEL TEI_EMBEDDING_DIM
LANGFUSE_PORT="${LANGFUSE_PORT:-3000}"
PHOENIX_PORT="${PHOENIX_PORT:-6006}"
OPENWEBUI_PORT="${OPENWEBUI_PORT:-3001}"
OPENWEBUI_ADMIN_EMAIL="${OPENWEBUI_ADMIN_EMAIL:-admin@example.com}"
OPENWEBUI_ADMIN_PASSWORD="${OPENWEBUI_ADMIN_PASSWORD:-openwebui}"
export LANGFUSE_PORT PHOENIX_PORT OPENWEBUI_PORT OPENWEBUI_ADMIN_EMAIL OPENWEBUI_ADMIN_PASSWORD
OLLAMA_MODEL="${OLLAMA_MODEL:-deepseek-r1:8b}"
# false: a proxy named ollama forwards to Ollama on this computer.
# true: the Ollama container is that same name. LiteLLM always calls http://ollama:11434.
case "${OLLAMA_ENABLED:-false}" in
  1|true|TRUE|yes|YES|on|ON) OLLAMA_ENABLED=true ;;
  *) OLLAMA_ENABLED=false ;;
esac
# true: pull OLLAMA_MODEL during docker-all-up. false skips the download.
case "${OLLAMA_PULL:-true}" in
  0|false|FALSE|no|NO|off|OFF) OLLAMA_PULL=false ;;
  *) OLLAMA_PULL=true ;;
esac
export OLLAMA_ENABLED OLLAMA_PULL OLLAMA_MODEL
LITELLM_PORT="${LITELLM_PORT:-4000}"
export LITELLM_UI="http://127.0.0.1:${LITELLM_PORT}/ui"
export LITELLM_DOCS="http://127.0.0.1:${LITELLM_PORT}/"
