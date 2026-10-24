#!/usr/bin/env bash
# Start Postgres, wait until it is up, then start LiteLLM.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/../.." && pwd)"
POSTGRES_FILE="$DIR/Postgres/docker-compose.yaml"
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
LITELLM_PORT="${LITELLM_PORT:-4000}"
LITELLM_UI="http://127.0.0.1:${LITELLM_PORT}/ui"
LITELLM_DOCS="http://127.0.0.1:${LITELLM_PORT}/"

echo "Starting Postgres..."
docker compose -f "$POSTGRES_FILE" up -d --wait --wait-timeout 120

echo "Postgres is up. Connect from a database client:"
echo "postgresql://${POSTGRES_USER}@127.0.0.1:${POSTGRES_PORT}/${POSTGRES_DB}"

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
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Admin UI login failed ({e.code}).")
    payload = json.loads(base64.urlsafe_b64decode(token.split(".")[1] + "=="))
    return payload["key"]

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
