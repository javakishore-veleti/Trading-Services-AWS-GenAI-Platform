#!/usr/bin/env bash
# Start Postgres, Redis, and vLLM in either order. LiteLLM waits for Postgres and Redis.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/../.." && pwd)"
POSTGRES_FILE="$DIR/Postgres/docker-compose.yaml"
REDIS_FILE="$DIR/Redis/docker-compose.yaml"
CLICKHOUSE_FILE="$DIR/ClickHouse/docker-compose.yaml"
LENS_FILE="$DIR/Lens/docker-compose.yaml"
VLLM_FILE="$DIR/vLLM/docker-compose.yaml"
LITELLM_FILE="$DIR/LiteLLM/docker-compose.yaml"

# Read KEY=VALUE lines without executing them. Passwords may contain $ and &.
if [ -f "$ROOT/.env" ]; then
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
fi

POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-postgres}"
REDIS_PORT="${REDIS_PORT:-6379}"
VLLM_PORT="${VLLM_PORT:-8000}"
LENS_PORT="${LENS_PORT:-4318}"
LENS_IMAGE="${LENS_IMAGE:-lens:local}"
LITELLM_PORT="${LITELLM_PORT:-4000}"
LITELLM_UI="http://127.0.0.1:${LITELLM_PORT}/ui"
LITELLM_DOCS="http://127.0.0.1:${LITELLM_PORT}/"

if ! docker network inspect trading-services-local >/dev/null 2>&1; then
  docker network create trading-services-local
fi

echo "Starting Postgres and Redis. Either one may become ready first."
docker compose -f "$POSTGRES_FILE" up -d --wait --wait-timeout 120 &
postgres_pid=$!
docker compose -f "$REDIS_FILE" up -d --wait --wait-timeout 120 &
redis_pid=$!
vllm_pid=""
if docker info 2>/dev/null | grep -Eqi 'nvidia'; then
  echo "Starting vLLM as well. The first model download can take a long time."
  docker compose -f "$VLLM_FILE" up -d &
  vllm_pid=$!
else
  echo "vLLM was not started. vllm/vllm-openai:v0.10.2 needs an NVIDIA GPU, and this machine does not have one."
fi
postgres_status=0
redis_status=0
vllm_status=0
wait "$postgres_pid" || postgres_status=$?
wait "$redis_pid" || redis_status=$?
if [ -n "$vllm_pid" ]; then
  wait "$vllm_pid" || vllm_status=$?
fi
if [ "$postgres_status" -ne 0 ] || [ "$redis_status" -ne 0 ]; then
  echo "Postgres or Redis did not become ready." >&2
  exit 1
fi
if [ "$vllm_status" -ne 0 ]; then
  echo "vLLM did not start. LiteLLM will still start, and calls to deepseek-r1-qwen3-8b will fail until vLLM is up." >&2
fi

echo "Postgres is up. Connect from a database client:"
echo "postgresql://${POSTGRES_USER}@127.0.0.1:${POSTGRES_PORT}/${POSTGRES_DB}"
echo "Redis is up. Connect from a Redis client:"
echo "redis://127.0.0.1:${REDIS_PORT}"
if [ -n "$vllm_pid" ] && [ "$vllm_status" -eq 0 ]; then
  echo "vLLM OpenAI API:"
  echo "http://127.0.0.1:${VLLM_PORT}/v1"
fi

if docker image inspect "$LENS_IMAGE" >/dev/null 2>&1; then
  echo "Starting ClickHouse, then Lens."
  docker compose -f "$CLICKHOUSE_FILE" up -d --wait --wait-timeout 180
  docker compose -f "$LENS_FILE" up -d
  echo "Lens UI:"
  echo "http://127.0.0.1:${LENS_PORT}/ui"
  echo "Lens inside LiteLLM:"
  echo "http://127.0.0.1:${LITELLM_PORT}/ui/lens/"
else
  echo "Lens was not started. No published image matches this LiteLLM build. Build ${LENS_IMAGE} from https://github.com/BerriAI/lens deploy/runtime/Dockerfile, then run this again."
fi

echo "Starting LiteLLM..."
docker compose -f "$LITELLM_FILE" up -d --wait --wait-timeout 300

echo "Ensuring the Admin UI account..."
python3 - "$ROOT/.env" <<'PY'
import base64, json, secrets, string, sys, urllib.error, urllib.request
from pathlib import Path

env = {}
for line in Path(sys.argv[1]).read_text().splitlines():
    raw = line.strip()
    if not raw or raw.startswith("#") or "=" not in raw:
        continue
    key, value = raw.split("=", 1)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        value = value[1:-1]
    env[key] = value

master = env["LITELLM_MASTER_KEY"]
email = env.get("UI_ADMIN_EMAIL", "admin@localhost")
password = env["UI_ADMIN_PASSWORD"]

def call(method, path, body=None, token=None):
    data = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    headers["Authorization"] = f"Bearer {token or master}"
    req = urllib.request.Request(
        "http://127.0.0.1:4000" + path,
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

def login(login_password):
    data = json.dumps({"username": email, "password": login_password}).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:4000/v2/login",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            token = json.loads(resp.read().decode())["token"]
    except urllib.error.HTTPError:
        return None
    payload = json.loads(base64.urlsafe_b64decode(token.split(".")[1] + "=="))
    return payload["key"]

names = [
    "222043-sales-offers",
    "222044-sales-bffs",
    "222045-sales-io",
    "221373-sales-order",
    "222045-sales-platforms",
]

def ensure_teams():
    limits = {
        "max_budget": 10,
        "budget_duration": "30d",
        "tpm_limit": 1000,
        "rpm_limit": 100,
        "tpd_limit": 10000,
        "models": ["all-proxy-models"],
    }
    status, existing = call("GET", "/team/list")
    if status != 200 or not isinstance(existing, list):
        raise SystemExit("Could not list teams.")
    by_id = {team.get("team_id"): team for team in existing}
    by_alias = {team.get("team_alias"): team for team in existing}
    for name in names:
        body = {"team_alias": name, "team_id": name, **limits}
        found = by_id.get(name) or by_alias.get(name)
        if found:
            body["team_id"] = found["team_id"]
            status, result = call("POST", "/team/update", body)
        else:
            status, result = call("POST", "/team/new", body)
        if status != 200:
            raise SystemExit(f"Could not save team {name}.")
        print(name)

def ensure_default_team_settings():
    # Tokens-per-day is not a field on this page. Models here apply to SSO-created teams.
    status, result = call("PATCH", "/update/default_team_settings", {
        "max_budget": 10,
        "budget_duration": "30d",
        "tpm_limit": 1000,
        "rpm_limit": 100,
        "models": ["all-proxy-models"],
    })
    if status != 200:
        raise SystemExit("Could not save default team settings.")

def ensure_access_groups():
    status, groups = call("GET", "/v1/access_group")
    if status != 200 or not isinstance(groups, list):
        raise SystemExit("Could not list access groups.")
    by_name = {group.get("access_group_name"): group for group in groups}
    for name in names:
        body = {
            "access_group_name": name,
            "description": name,
            "access_model_names": ["all-proxy-models"],
            "assigned_team_ids": [name],
        }
        found = by_name.get(name)
        if found:
            status, _result = call("PUT", "/v1/access_group/" + found["access_group_id"], body)
            ok = status == 200
        else:
            status, _result = call("POST", "/v1/access_group", body)
            ok = status == 201
        if not ok:
            raise SystemExit(f"Could not save access group {name}.")
        print("access group " + name)

def ensure_budgets():
    limits = {
        "max_budget": 10,
        "budget_duration": "30d",
        "tpm_limit": 1000,
        "rpm_limit": 100,
        "tpd_limit": 10000,
    }
    status, existing = call("GET", "/budget/list")
    if status != 200 or not isinstance(existing, list):
        raise SystemExit("Could not list budgets.")
    by_id = {budget.get("budget_id"): budget for budget in existing}
    for name in names:
        body = {"budget_id": name, **limits}
        if name in by_id:
            status, _result = call("POST", "/budget/update", body)
            ok = status == 200
        else:
            status, _result = call("POST", "/budget/new", body)
            ok = status in (200, 201)
        if not ok:
            raise SystemExit(f"Could not save budget {name}.")
        print("budget " + name)

ensure_teams()
ensure_default_team_settings()
ensure_access_groups()
ensure_budgets()

if login(password):
    raise SystemExit(0)

status, created = call("POST", "/user/new", {
    "user_email": email,
    "user_alias": "Local admin",
    "user_role": "proxy_admin",
    "auto_create_key": False,
    "send_invite_email": False,
})
if status == 200 and isinstance(created, dict):
    user_id = created["user_id"]
else:
    status, listing = call("GET", "/user/list")
    users = listing.get("users", []) if isinstance(listing, dict) else []
    user_id = next(
        (user["user_id"] for user in users if (user.get("user_email") or "").lower() == email.lower()),
        None,
    )
    if not user_id:
        raise SystemExit("Could not create or find the Admin UI account.")

rng = secrets.SystemRandom()
alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
temporary = [
    rng.choice(string.ascii_uppercase),
    rng.choice(string.ascii_lowercase),
    rng.choice(string.digits),
    rng.choice("!@#$%^&*"),
]
temporary += [rng.choice(alphabet) for _ in range(16)]
rng.shuffle(temporary)
temporary = "".join(temporary)
if temporary == password:
    temporary += "aA1!"

status, _updated = call("POST", "/user/update", {
    "user_id": user_id,
    "user_role": "proxy_admin",
    "password": temporary,
})
if status != 200:
    raise SystemExit("Could not set the Admin UI password.")

key = login(temporary)
if not key:
    raise SystemExit("Admin UI login failed.")
status, changed = call(
    "POST",
    "/user/password/change",
    {"current_password": temporary, "new_password": password},
    token=key,
)
if status != 200:
    raise SystemExit("Could not finish the Admin UI password change.")
PY

echo "LiteLLM is up."
echo "Username: ${UI_ADMIN_EMAIL:-admin@localhost}"
echo "Password: ${UI_ADMIN_PASSWORD:-}"
echo "Admin UI:"
echo "${LITELLM_UI}"
echo "API docs:"
echo "${LITELLM_DOCS}"
if [ "$(uname -s)" = "Darwin" ]; then
  open "${LITELLM_UI}"
fi
