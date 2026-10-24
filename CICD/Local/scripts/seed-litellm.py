#!/usr/bin/env python3
"""Create the local teams, budgets, vector stores, indexes, MCP servers, toolsets, skills, guardrails, desk agents, app users, and admin login."""

import base64
import json
import os
import secrets
import string
import subprocess
import sys
import urllib.error
import urllib.parse
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

# The proxy runs in Docker and calls these later. Registration does not connect.
# LiteLLM uses "-" to prefix tool names, so server_name and alias cannot contain it.
MCP_SERVERS = [
    ("trades-catalog-mcp", "8101", "FX product catalog for customers"),
    ("trades-offers-mcp", "8102", "Customer ratings, discounts, and all-in FX pricing"),
    ("trades-orders-mcp", "8103", "Create and retrieve FX orders"),
    ("trades-partners-mcp", "8104", "Correspondent banks on FX integrations"),
    ("traders-master-data-mcp", "8105", "Traders, books, channels, and desk installations"),
    ("traders-analytics-mcp", "8106", "Read-only end-of-day, intraday, and hourly analytics"),
]

# One toolset per server, containing that server's own tool names.
MCP_TOOLS = {
    "trades-catalog-mcp": ["list_fx_products", "get_fx_product"],
    "trades-offers-mcp": ["list_customer_ratings", "list_rating_discounts", "quote_fx_offer"],
    "trades-orders-mcp": ["list_fx_orders", "get_fx_order", "create_fx_order"],
    "trades-partners-mcp": ["list_fx_partners", "get_fx_partner"],
    "traders-master-data-mcp": [
        "list_omni_channels",
        "list_desk_countries",
        "list_trading_desks",
        "list_desk_installations",
        "list_trading_books",
        "list_book_defaults",
        "list_book_channels",
        "list_traders",
    ],
    "traders-analytics-mcp": ["list_analytics_grains", "read_fx_analytics"],
}

SKILL_REPO = "https://github.com/javakishore-veleti/Trading-Services-AWS-GenAI-Platform.git"
SKILLS = [
    (
        "trading-desk-offers",
        "offers",
        "Build the FOREX all-in from the customer rating band, the product spread, and a fresh mid. AAA removes 8 basis points, BB removes 1, and the net never prints below 0.5. A missing mid, a due data release, or an unknown product is no quote.",
        ["forex", "all-in", "rating-band", "basis-points", "mid"],
    ),
    (
        "trading-desk-bffs",
        "screen-apis",
        "Carry Advisor, Partner, Dealer, Mobile, Web, and Kiosk requests to the FOREX offer book and the order book, then show the all-in and the change those books returned. This backend does not compute a second price and does not pick immediate or bill-through.",
        ["advisor", "partner", "dealer", "mobile", "web", "kiosk"],
    ),
    (
        "trading-desk-order",
        "orders",
        "Book a FOREX new order, cancel, upgrade, or downgrade. An upgrade or downgrade is an immediate cancel of the current order or a bill-through date, never an edit in place. New risk waits when the book has stopped for the day, and the notional cannot exceed the quote.",
        ["new-order", "cancel", "upgrade", "downgrade", "bill-through"],
    ),
    (
        "trading-desk-io",
        "international-operations",
        "Run product, price, and order as one FOREX book for South Korea, Japan, China, Australia, New Zealand, Brazil, Belgium, and France. Take a new mid when a release is due for that country, and keep an upgrade or downgrade on immediate or bill-through timing.",
        ["south-korea", "japan", "china", "australia", "new-zealand", "brazil", "belgium", "france"],
    ),
    (
        "trading-desk-platforms",
        "platforms",
        "Pass a Salesforce CRM or Shopify request that names a FOREX customer, pair, and change to the offer book and the order book, then store their result on the platform. The platform supplies no discount, no all-in, and no timing.",
        ["salesforce", "shopify", "crm"],
    ),
]

# One LangGraph agent per trading desk. LiteLLM calls host.docker.internal, the same way it calls MCP.
DESK_AGENTS = [
    ("trading-desk-offers", "8201", "BU1000-trading-desk-offers", "Runs the offer process: rating, discount, then the all-in quote."),
    ("trading-desk-bffs", "8202", "BU1001-trading-desk-bffs", "Carries a screen request to the offer book and the order book and returns their answer."),
    ("trading-desk-io", "8203", "BU1002-trading-desk-io", "Runs catalog, the offer book, and the order book as one process for the eight countries."),
    ("trading-desk-order", "8204", "BU1003-trading-desk-order", "Books a new order, cancel, upgrade, or downgrade. An upgrade or downgrade is immediate or bill-through."),
    ("trading-desk-platforms", "8205", "BU1004-trading-desk-platforms", "Carries a Salesforce or Shopify request to the offer book and the order book and writes the result back."),
]

GUARDRAILS = [
    ("offer-price", ["post_call"], "Block an FX quote whose net spread breaks the rating discount or the 0.5 basis point floor."),
    ("order-change", ["pre_call", "pre_mcp_call"], "An order change is new, cancel, upgrade, or downgrade. Upgrade and downgrade name immediate or bill-through."),
    ("international-country", ["pre_call", "pre_mcp_call"], "International operations runs only for its eight countries."),
    ("screen-boundary", ["pre_call", "pre_mcp_call"], "A trading desk screen can carry a request. It cannot set the discount or the upgrade timing."),
    ("platform-boundary", ["pre_call", "pre_mcp_call"], "A selling platform can carry the change. It cannot set the price or the timing."),
    ("analytics-read-only", ["pre_call", "pre_mcp_call"], "Analytics allows an end-of-day, intraday, or hourly read. A write is blocked."),
    ("team-tools", ["pre_call", "pre_mcp_call"], "A team key can call only the tools for its own business."),
]


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
        if any(char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-" for char in name):
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


def ensure_mcp_servers():
    status, existing = call("GET", "/v1/mcp/server")
    if status != 200 or not isinstance(existing, list):
        raise SystemExit("Could not list MCP servers.")
    by_id = {row.get("server_id"): row for row in existing}
    by_name = {row.get("server_name"): row for row in existing}
    for name, port, description in MCP_SERVERS:
        registry_name = name.replace("-", "_")
        url = "http://host.docker.internal:" + port + "/mcp"
        body = {
            "server_id": registry_name,
            "server_name": registry_name,
            "alias": registry_name,
            "description": description,
            "url": url,
            "transport": "http",
            "auth_type": "none",
        }
        found = by_id.get(registry_name) or by_name.get(registry_name)
        if found and found.get("url") == url and found.get("transport") == "http":
            print("mcp server " + registry_name)
            continue
        if found:
            body["server_id"] = found["server_id"]
            status, result = call("PUT", "/v1/mcp/server", body)
            ok = status in (200, 202)
        else:
            status, result = call("POST", "/v1/mcp/server", body)
            ok = status in (200, 201)
        if not ok:
            raise SystemExit(f"Could not register MCP server {registry_name}: {status} {result}")
        print("mcp server " + registry_name)


def ensure_mcp_toolsets():
    status, existing = call("GET", "/v1/mcp/toolset")
    if status != 200 or not isinstance(existing, list):
        raise SystemExit(f"Could not list MCP toolsets: {status} {existing}")
    by_name = {row.get("toolset_name"): row for row in existing}
    for name, _port, description in MCP_SERVERS:
        registry_name = name.replace("-", "_")
        tools = [
            {"server_id": registry_name, "tool_name": tool_name}
            for tool_name in MCP_TOOLS[name]
        ]
        wanted = {(item["server_id"], item["tool_name"]) for item in tools}
        found = by_name.get(registry_name)
        if found:
            current = {
                (item.get("server_id"), item.get("tool_name"))
                for item in found.get("tools") or []
            }
            if current == wanted and (found.get("description") or "") == description:
                print("mcp toolset " + registry_name)
                continue
            status, result = call("PUT", "/v1/mcp/toolset", {
                "toolset_id": found["toolset_id"],
                "toolset_name": registry_name,
                "description": description,
                "tools": tools,
            })
            ok = status == 200
        else:
            status, result = call("POST", "/v1/mcp/toolset", {
                "toolset_name": registry_name,
                "description": description,
                "tools": tools,
            })
            ok = status in (200, 201)
        if not ok:
            raise SystemExit(f"Could not register MCP toolset {registry_name}: {status} {result}")
        print("mcp toolset " + registry_name)


def ensure_skills():
    status, existing = call("GET", "/claude-code/plugins")
    if status != 200 or not isinstance(existing, dict):
        raise SystemExit(f"Could not list skills: {status} {existing}")
    rows = existing.get("plugins") or existing.get("data") or []
    by_name = {row.get("name"): row for row in rows}
    for name, namespace, description, keywords in SKILLS:
        body = {
            "name": name,
            "source": {
                "source": "git-subdir",
                "url": SKILL_REPO,
                "path": "Middleware/skills/" + name,
            },
            "version": "1.0.0",
            "description": description,
            "keywords": keywords,
            "category": "FOREX",
            "domain": "Trading Desk",
            "namespace": namespace,
        }
        found = by_name.get(name)
        if found and found.get("description") == description and found.get("version") == "1.0.0":
            print("skill " + name)
            continue
        if found:
            status, result = call("PUT", "/claude-code/plugins/" + name, {
                key: value for key, value in body.items() if key != "name"
            })
            ok = status == 200
        else:
            status, result = call("POST", "/claude-code/plugins", body)
            ok = status in (200, 201)
        if not ok:
            raise SystemExit(f"Could not register skill {name}: {status} {result}")
        print("skill " + name)


def ensure_guardrails():
    root = Path(sys.argv[1]).resolve().parent / "Middleware" / "guard-rails"
    status, existing = call("GET", "/v2/guardrails/list")
    if status != 200 or not isinstance(existing, dict):
        raise SystemExit(f"Could not list guardrails: {status} {existing}")
    by_name = {row.get("guardrail_name"): row for row in existing.get("guardrails") or []}
    for name, modes, description in GUARDRAILS:
        code = (root / name / "apply_guardrail.py").read_text()
        body = {
            "guardrail_name": name,
            "litellm_params": {
                "guardrail": "custom_code",
                "mode": modes,
                "custom_code": code,
                "default_on": True,
            },
            "guardrail_info": {"description": description},
        }
        found = by_name.get(name)
        current = (found or {}).get("litellm_params") or {}
        if found and current.get("custom_code") == code and current.get("mode") == modes:
            print("guardrail " + name)
            continue
        if found:
            status, result = call("PUT", "/guardrails/" + found["guardrail_id"], {"guardrail": body})
            ok = status == 200
        else:
            status, result = call("POST", "/guardrails", {"guardrail": body})
            ok = status in (200, 201)
        if not ok:
            raise SystemExit(f"Could not register guardrail {name}: {status} {result}")
        print("guardrail " + name)


def ensure_agents():
    status, existing = call("GET", "/v1/agents")
    if status != 200 or not isinstance(existing, list):
        raise SystemExit(f"Could not list agents: {status} {existing}")
    by_name = {row.get("agent_name"): row for row in existing}
    for name, port, _team, description in DESK_AGENTS:
        api_base = "http://host.docker.internal:" + port
        model = "langgraph/" + name
        body = {
            "agent_name": name,
            "enabled": True,
            "agent_card_params": {
                "protocolVersion": "1.0",
                "name": name,
                "description": description,
                "url": api_base,
                "version": "1.0.0",
                "capabilities": {"streaming": True},
                "defaultInputModes": ["text"],
                "defaultOutputModes": ["text"],
                "skills": [
                    {
                        "id": name,
                        "name": name,
                        "description": description,
                        "tags": ["forex", "trading-desk"],
                    }
                ],
            },
            "litellm_params": {
                "custom_llm_provider": "langgraph",
                "model": model,
                "api_base": api_base,
            },
        }
        found = by_name.get(name)
        params = (found or {}).get("litellm_params") or {}
        card = (found or {}).get("agent_card_params") or {}
        if (
            found
            and params.get("model") == model
            and params.get("api_base") == api_base
            and params.get("custom_llm_provider") == "langgraph"
            and card.get("description") == description
        ):
            print("agent " + name)
            continue
        if found:
            status, result = call("PUT", "/v1/agents/" + found["agent_id"], body)
            ok = status == 200
        else:
            status, result = call("POST", "/v1/agents", body)
            ok = status in (200, 201)
        if not ok:
            raise SystemExit(f"Could not register agent {name}: {status} {result}")
        print("agent " + name)


def ensure_agent_keys():
    status, existing = call("GET", "/v1/agents")
    if status != 200 or not isinstance(existing, list):
        raise SystemExit(f"Could not list agents: {status} {existing}")
    by_name = {row.get("agent_name"): row for row in existing}
    for name, _port, team_id, _description in DESK_AGENTS:
        found = by_name.get(name)
        if not found:
            raise SystemExit(f"Agent {name} is not registered.")
        agent_id = found["agent_id"]
        status, listed = call("GET", "/key/list?agent_id=" + agent_id + "&page=1&size=10")
        rows = []
        if isinstance(listed, dict):
            rows = listed.get("keys") or listed.get("data") or []
        elif isinstance(listed, list):
            rows = listed
        if status == 200 and rows:
            print("agent key " + name)
            continue
        status, result = call("POST", "/key/generate", {
            "key_alias": name,
            "agent_id": agent_id,
            "team_id": team_id,
            "models": ["all-proxy-models"],
        })
        if status != 200 or not isinstance(result, dict) or not result.get("key"):
            safe = result
            if isinstance(result, dict):
                safe = {key: value for key, value in result.items() if key not in ("key", "token")}
            raise SystemExit(f"Could not create the key for {name}: {status} {safe}")
        print("agent key " + name)


def ensure_app_users():
    for name in names:
        alias = "app-user-" + name
        email = alias + "@localhost"
        status, listing = call("GET", "/user/list?user_email=" + urllib.parse.quote(email))
        users = listing.get("users", []) if isinstance(listing, dict) else []
        found = next(
            (user for user in users if (user.get("user_email") or "").lower() == email.lower()),
            None,
        )
        if found:
            print("app user " + alias)
            continue
        status, result = call("POST", "/user/new", {
            "user_id": alias,
            "user_email": email,
            "user_alias": alias,
            "user_role": "internal_user_viewer",
            "teams": [{"team_id": name, "user_role": "user"}],
            "auto_create_key": True,
            "models": ["all-proxy-models"],
            "send_invite_email": False,
        })
        if status != 200:
            safe = result
            if isinstance(result, dict):
                safe = {key: value for key, value in result.items() if key not in ("key", "token")}
            raise SystemExit(f"Could not create app user {alias}: {status} {safe}")
        print("app user " + alias)


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
    ensure_mcp_servers()
    ensure_mcp_toolsets()
    ensure_skills()
    ensure_guardrails()
    ensure_agents()
    ensure_agent_keys()
    ensure_app_users()
    ensure_admin()


if __name__ == "__main__":
    main()
