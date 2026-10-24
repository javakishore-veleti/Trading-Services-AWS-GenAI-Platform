"""One connector for every team database.

A search names a vector store id. The id is looked up in the catalog and the
query runs on that team's database, with that team's login. Another team's
rows are not in the connection.
"""

import os
from typing import Any

import httpx
import psycopg
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from psycopg.rows import dict_row

app = FastAPI(title="Team pgvector connector")

CATALOG_URL = os.environ["CATALOG_URL"]
EMBEDDING_MODEL = os.environ.get("EMBEDDING__MODEL", "text-embedding-3-small")
EMBEDDING_BASE_URL = os.environ.get("EMBEDDING__BASE_URL", "http://litellm:4000").rstrip("/")
EMBEDDING_API_KEY = os.environ["EMBEDDING__API_KEY"]
EMBEDDING_DIMENSIONS = int(os.environ.get("EMBEDDING__DIMENSIONS", "1536"))


class SearchRequest(BaseModel):
    query: str | list[str]
    limit: int | None = 20
    filters: dict[str, Any] | None = None


def catalog_row(store_id: str) -> dict[str, str] | None:
    with psycopg.connect(CATALOG_URL, row_factory=dict_row) as conn:
        row = conn.execute(
            """
            SELECT team_id, db_name, role_name, role_password, connector_key
            FROM team_vector_databases
            WHERE team_id = %s
            """,
            (store_id,),
        ).fetchone()
    return dict(row) if row else None


def authorize(store_id: str, authorization: str) -> dict[str, str]:
    presented = authorization.removeprefix("Bearer ").strip()
    row = catalog_row(store_id)
    if row is None or not presented or presented != row["connector_key"]:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return row


def team_url(row: dict[str, str]) -> str:
    return (
        f"postgresql://{row['role_name']}:{row['role_password']}"
        f"@pgvector:5432/{row['db_name']}"
    )


def embed(text: str) -> list[float]:
    try:
        response = httpx.post(
            f"{EMBEDDING_BASE_URL}/embeddings",
            headers={"Authorization": f"Bearer {EMBEDDING_API_KEY}"},
            json={"model": EMBEDDING_MODEL, "input": text},
            timeout=60,
        )
        response.raise_for_status()
        vector = response.json()["data"][0]["embedding"]
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Embedding model {EMBEDDING_MODEL} is not available on the proxy.",
        ) from exc
    if len(vector) != EMBEDDING_DIMENSIONS:
        raise HTTPException(
            status_code=503,
            detail=f"Embedding model returned {len(vector)} dimensions, expected {EMBEDDING_DIMENSIONS}.",
        )
    return vector


@app.get("/health")
def health() -> dict[str, str]:
    with psycopg.connect(CATALOG_URL) as conn:
        conn.execute("SELECT 1")
    return {"status": "healthy"}


@app.post("/v1/vector_stores/{vector_store_id}/search")
def search(
    vector_store_id: str,
    body: SearchRequest,
    authorization: str = Header(),
) -> dict[str, Any]:
    row = authorize(vector_store_id, authorization)
    query = body.query if isinstance(body.query, str) else " ".join(body.query)
    vector = embed(query)
    literal = "[" + ",".join(str(value) for value in vector) + "]"
    limit = min(max(body.limit or 20, 1), 100)
    sql = """
        SELECT id, content, metadata, (embedding <=> %s::vector) AS distance
        FROM embeddings
        WHERE vector_store_id = %s
    """
    params: list[Any] = [literal, vector_store_id]
    for key, value in (body.filters or {}).items():
        sql += " AND metadata->>%s = %s"
        params.extend([str(key), str(value)])
    sql += " ORDER BY distance ASC LIMIT %s"
    params.append(limit)
    with psycopg.connect(team_url(row), row_factory=dict_row, options="-c statement_timeout=15000") as conn:
        rows = conn.execute(sql, params).fetchall()
    data = []
    for found in rows:
        metadata = found["metadata"] or {}
        distance = float(found["distance"])
        data.append({
            "file_id": str(metadata.get("file_id") or found["id"]),
            "filename": str(metadata.get("filename") or "content"),
            "score": 1.0 - distance,
            "attributes": metadata,
            "content": [{"type": "text", "text": found["content"]}],
        })
    return {
        "object": "vector_store.search_results.page",
        "search_query": query,
        "data": data,
        "has_more": False,
        "next_page": None,
    }
