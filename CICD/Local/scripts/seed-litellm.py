#!/usr/bin/env python3
"""Create the local teams, budgets, vector stores, indexes, and admin login."""

import base64
import json
import os
import secrets
import string
import subprocess
import sys
import urllib.error
import urllib.request
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
names = [line for line in os.environ["LOCAL_TEAM_NAMES"].splitlines() if line]


def call(method, path, body=None, token=None):
    data = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token or master}"}
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
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


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
            status, _result = call("POST", "/team/update", body)
        else:
            status, _result = call("POST", "/team/new", body)
        if status != 200:
            raise SystemExit(f"Could not save team {name}.")
        print(name)


def ensure_default_team_settings():
    status, _result = call("PATCH", "/update/default_team_settings", {
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


def list_vector_stores():
    stores = []
    page = 1
    while True:
        status, payload = call("GET", f"/vector_store/list?page={page}&page_size=100")
        if status != 200 or not isinstance(payload, dict):
            raise SystemExit("Could not list vector stores.")
        stores.extend(payload.get("data") or [])
        if page >= payload.get("total_pages", 1):
            return stores
        page += 1


def catalog_keys():
    result = subprocess.run(
        [
            "docker", "exec", "-e", "PGPASSWORD=" + env.get("PGVECTOR_PASSWORD", "pgvector"),
            "trading-services-genai-pgvector-pgvector-1",
            "psql", "-U", env.get("PGVECTOR_USER", "pgvector"),
            "-d", env.get("PGVECTOR_DB", "pgvector"),
            "-At", "-c",
            "SELECT team_id || ' ' || connector_key FROM team_vector_databases",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit("Could not read the team vector catalog.")
    keys = {}
    for line in result.stdout.splitlines():
        team_id, connector_key = line.split(" ", 1)
        keys[team_id] = connector_key
    return keys


def ensure_vector_stores():
    call("POST", "/vector_store/delete", {"vector_store_id": "local-pgvector"})
    keys = catalog_keys()
    stores = {store.get("vector_store_id"): store for store in list_vector_stores()}
    for name in names:
        if any(char not in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in name):
            raise SystemExit(f"Unsafe team id {name}.")
        connector_key = keys.get(name)
        if not connector_key:
            raise SystemExit(f"No vector database is registered for {name}.")
        status, _result = call("POST", "/team/update", {
            "team_id": name,
            "object_permission": {"vector_stores": [name]},
        })
        if status != 200:
            raise SystemExit(f"Could not grant {name} its vector store.")
        body = {
            "vector_store_id": name,
            "custom_llm_provider": "pg_vector",
            "vector_store_name": name,
            "vector_store_description": "pgvector database " + name,
            "litellm_params": {
                "api_base": "http://pgvector-connector:8000",
                "api_key": connector_key,
            },
        }
        found = stores.get(name)
        if found:
            status, _result = call("POST", "/vector_store/update", body)
            ok = status == 200
        else:
            status, _result = call("POST", "/vector_store/new", body)
            ok = status in (200, 201)
        if ok:
            stamped = subprocess.run(
                [
                    "docker", "exec", "-e", "PGPASSWORD=" + env.get("POSTGRES_PASSWORD", "postgres"),
                    "trading-services-genai-platform-postgres-1",
                    "psql", "-U", env.get("POSTGRES_USER", "postgres"),
                    "-d", env.get("POSTGRES_DB", "postgres"),
                    "-v", "ON_ERROR_STOP=1", "-c",
                    "UPDATE \"LiteLLM_ManagedVectorStoresTable\" "
                    f"SET team_id = '{name}' WHERE vector_store_id = '{name}';",
                ],
                capture_output=True,
                text=True,
            )
            ok = stamped.returncode == 0
        if not ok:
            raise SystemExit(f"Could not save vector store {name}.")
        print("vector store " + name)


def ensure_indexes():
    status, payload = call("GET", "/v1/indexes")
    if status != 200 or not isinstance(payload, dict):
        raise SystemExit("Could not list indexes.")
    existing = {row.get("index_name") for row in payload.get("data") or []}
    for name in names:
        if name in existing:
            print("index " + name)
            continue
        status, _result = call("POST", "/v1/indexes", {
            "index_name": name,
            "litellm_params": {
                "vector_store_index": "embeddings_embedding_hnsw",
                "vector_store_name": name,
            },
            "index_info": {"database": "vs_" + name.replace("-", "_")},
        })
        if status not in (200, 201):
            raise SystemExit(f"Could not register index {name}.")
        print("index " + name)


def ensure_admin():
    if login(password):
        return
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
    status, _changed = call(
        "POST",
        "/user/password/change",
        {"current_password": temporary, "new_password": password},
        token=key,
    )
    if status != 200:
        raise SystemExit("Could not finish the Admin UI password change.")


def main():
    ensure_teams()
    ensure_default_team_settings()
    ensure_access_groups()
    ensure_budgets()
    ensure_vector_stores()
    ensure_indexes()
    ensure_admin()


if __name__ == "__main__":
    main()
