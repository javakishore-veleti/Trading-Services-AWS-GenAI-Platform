#!/usr/bin/env python3
"""Create one database, one schema, and one vector store per team.

The same path works for a handful of teams or a thousand. Each team is a
Postgres database with its own login. The connector is one process and opens
only the database named in its catalog for that store id.
"""

import hashlib
import os
import re
import secrets
import subprocess
import sys
from pathlib import Path

CONTAINER = "trading-services-genai-pgvector-pgvector-1"
ADMIN_USER = os.environ.get("PGVECTOR_USER", "pgvector")
ADMIN_PASSWORD = os.environ.get("PGVECTOR_PASSWORD", "pgvector")
ADMIN_DB = os.environ.get("PGVECTOR_DB", "pgvector")
IDENT = re.compile(r"vs_[a-z0-9_]{1,60}")

SCHEMA = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS vector_stores (
    id text PRIMARY KEY,
    name text NOT NULL,
    file_counts jsonb,
    status text NOT NULL DEFAULT 'completed',
    usage_bytes integer DEFAULT 0,
    created_at timestamptz NOT NULL DEFAULT now(),
    expires_after jsonb,
    expires_at timestamptz,
    last_active_at timestamptz,
    metadata jsonb
);
CREATE TABLE IF NOT EXISTS embeddings (
    id text PRIMARY KEY,
    vector_store_id text NOT NULL REFERENCES vector_stores(id) ON DELETE CASCADE,
    content text NOT NULL,
    embedding vector(1536),
    metadata jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS embeddings_store_id ON embeddings (vector_store_id);
"""


def database_name(team_id: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", team_id.lower()).strip("_")
    name = f"vs_{slug}"
    if len(name) > 63:
        digest = hashlib.sha256(team_id.encode()).hexdigest()[:8]
        name = f"vs_{slug[:50]}_{digest}"
    if IDENT.fullmatch(name) is None:
        raise SystemExit(f"Cannot name a database for {team_id}.")
    return name


def psql(database: str, sql: str, user: str | None = None, password: str | None = None) -> str:
    env = [f"PGPASSWORD={password if password is not None else ADMIN_PASSWORD}"]
    result = subprocess.run(
        [
            "docker", "exec", "-i", "-e", env[0], CONTAINER,
            "psql", "-U", user or ADMIN_USER, "-d", database,
            "-v", "ON_ERROR_STOP=1", "-At", "-q",
        ],
        input=sql.encode(),
        capture_output=True,
    )
    if result.returncode != 0:
        message = result.stderr.decode().strip() or result.stdout.decode().strip()
        raise SystemExit(message)
    return result.stdout.decode()


def sql_literal(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise SystemExit("Refusing to place an unsafe value in SQL.")
    return "'" + value + "'"


def upsert_env(path: Path, key: str, value: str) -> None:
    lines = path.read_text().splitlines() if path.exists() else []
    replaced = False
    output = []
    for line in lines:
        if line.startswith(key + "="):
            output.append(f"{key}={value}")
            replaced = True
        else:
            output.append(line)
    if not replaced:
        if output and output[-1] != "":
            output.append("")
        output.append(f"{key}={value}")
    path.write_text("\n".join(output) + "\n")


def env_value(path: Path, key: str) -> str:
    if not path.exists():
        return ""
    for line in path.read_text().splitlines():
        if line.startswith(key + "="):
            value = line.split("=", 1)[1]
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            if value and value != "change-me":
                return value
    return ""


def ensure_router(env_path: Path) -> str:
    password = env_value(env_path, "PGVECTOR_ROUTER_PASSWORD") or secrets.token_hex(24)
    upsert_env(env_path, "PGVECTOR_ROUTER_PASSWORD", password)
    psql(ADMIN_DB, f"""
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'pgvector_router') THEN
        CREATE ROLE pgvector_router LOGIN PASSWORD {sql_literal(password)};
    ELSE
        ALTER ROLE pgvector_router PASSWORD {sql_literal(password)};
    END IF;
END
$$;
CREATE TABLE IF NOT EXISTS team_vector_databases (
    team_id text PRIMARY KEY,
    db_name text NOT NULL UNIQUE,
    role_name text NOT NULL UNIQUE,
    role_password text NOT NULL,
    connector_key text NOT NULL
);
REVOKE ALL ON team_vector_databases FROM PUBLIC;
GRANT SELECT ON team_vector_databases TO pgvector_router;
REVOKE CONNECT ON DATABASE {ADMIN_DB} FROM PUBLIC;
GRANT CONNECT ON DATABASE {ADMIN_DB} TO {ADMIN_USER};
GRANT CONNECT ON DATABASE {ADMIN_DB} TO pgvector_router;
""")
    return password


def catalog_row(team_id: str) -> dict[str, str] | None:
    raw = psql(
        ADMIN_DB,
        "SELECT db_name || '|' || role_name || '|' || role_password || '|' || connector_key "
        f"FROM team_vector_databases WHERE team_id = {sql_literal(team_id)};",
    ).strip()
    if not raw:
        return None
    db_name, role_name, role_password, connector_key = raw.split("|", 3)
    return {
        "db_name": db_name,
        "role_name": role_name,
        "role_password": role_password,
        "connector_key": connector_key,
    }


def ensure_team(team_id: str) -> str:
    db_name = database_name(team_id)
    existing = catalog_row(team_id)
    role_password = existing["role_password"] if existing else secrets.token_hex(24)
    connector_key = existing["connector_key"] if existing else secrets.token_hex(24)
    psql(ADMIN_DB, f"""
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = {sql_literal(db_name)}) THEN
        CREATE ROLE {db_name} LOGIN PASSWORD {sql_literal(role_password)};
    ELSE
        ALTER ROLE {db_name} PASSWORD {sql_literal(role_password)};
    END IF;
END
$$;
""")
    found = psql(ADMIN_DB, f"SELECT 1 FROM pg_database WHERE datname = {sql_literal(db_name)};").strip()
    if found != "1":
        psql(ADMIN_DB, f"CREATE DATABASE {db_name} OWNER {db_name};")
    psql(ADMIN_DB, f"""
REVOKE CONNECT ON DATABASE {db_name} FROM PUBLIC;
GRANT CONNECT ON DATABASE {db_name} TO {db_name};
""")
    psql(db_name, SCHEMA)
    psql(db_name, f"""
ALTER TABLE vector_stores OWNER TO {db_name};
ALTER TABLE embeddings OWNER TO {db_name};
INSERT INTO vector_stores (id, name, file_counts, status, usage_bytes, metadata)
VALUES (
    {sql_literal(team_id)},
    {sql_literal(team_id)},
    '{{"in_progress":0,"completed":0,"failed":0,"cancelled":0,"total":0}}'::jsonb,
    'completed',
    0,
    '{{}}'::jsonb
)
ON CONFLICT (id) DO NOTHING;
""")
    index = subprocess.run(
        [
            "docker", "exec", "-i", "-e", f"PGPASSWORD={ADMIN_PASSWORD}", CONTAINER,
            "psql", "-U", ADMIN_USER, "-d", db_name, "-v", "ON_ERROR_STOP=1", "-q",
        ],
        input=b"CREATE INDEX IF NOT EXISTS embeddings_embedding_hnsw ON embeddings USING hnsw (embedding vector_cosine_ops);\n",
        capture_output=True,
    )
    if index.returncode != 0:
        raise SystemExit(index.stderr.decode().strip())
    psql(ADMIN_DB, f"""
INSERT INTO team_vector_databases (team_id, db_name, role_name, role_password, connector_key)
VALUES (
    {sql_literal(team_id)},
    {sql_literal(db_name)},
    {sql_literal(db_name)},
    {sql_literal(role_password)},
    {sql_literal(connector_key)}
)
ON CONFLICT (team_id) DO UPDATE
SET db_name = EXCLUDED.db_name,
    role_name = EXCLUDED.role_name,
    role_password = EXCLUDED.role_password,
    connector_key = EXCLUDED.connector_key;
""")
    print(f"vector database {db_name}")
    return db_name


def assert_isolated(teams: list[str]) -> None:
    if len(teams) < 2:
        return
    first = catalog_row(teams[0])
    second = catalog_row(teams[1])
    if first is None or second is None:
        raise SystemExit("Team catalog is incomplete.")
    denied = subprocess.run(
        [
            "docker", "exec", "-e", f"PGPASSWORD={first['role_password']}", CONTAINER,
            "psql", "-U", first["role_name"], "-d", second["db_name"], "-c", "SELECT 1",
        ],
        capture_output=True,
    )
    if denied.returncode == 0:
        raise SystemExit("A team login connected to another team's database.")
    print("team login cannot open another team's database")


def main() -> None:
    env_path = Path(sys.argv[1])
    teams = [line for line in os.environ.get("LOCAL_TEAM_NAMES", "").splitlines() if line]
    if not teams:
        raise SystemExit("LOCAL_TEAM_NAMES is empty.")
    ensure_router(env_path)
    for team_id in teams:
        ensure_team(team_id)
    assert_isolated(teams)


if __name__ == "__main__":
    main()
