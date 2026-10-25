import os

import psycopg


def connect() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        port=os.environ.get("POSTGRES_PORT", "5432"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
        dbname=os.environ.get("POSTGRES_DB", "postgres"),
    )


def ensure_status_table(datasets: list[tuple[str, str, str]]) -> None:
    with connect() as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS trading_desk_admin")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trading_desk_admin.ingestion_status (
                dataset_key text PRIMARY KEY,
                title text NOT NULL,
                schema_name text NOT NULL,
                status text NOT NULL,
                record_count integer NOT NULL DEFAULT 0,
                message text NOT NULL DEFAULT '',
                updated_at timestamptz NOT NULL DEFAULT now(),
                ingested_at timestamptz
            )
            """
        )
        conn.execute(
            """
            ALTER TABLE trading_desk_admin.ingestion_status
            ADD COLUMN IF NOT EXISTS ingested_at timestamptz
            """
        )
        for dataset_key, title, schema_name in datasets:
            conn.execute(
                """
                INSERT INTO trading_desk_admin.ingestion_status
                    (dataset_key, title, schema_name, status)
                VALUES (%s, %s, %s, 'pending')
                ON CONFLICT (dataset_key) DO NOTHING
                """,
                (dataset_key, title, schema_name),
            )
        conn.commit()


def set_status(dataset_key: str, status: str, record_count: int | None, message: str) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE trading_desk_admin.ingestion_status
            SET status = %s,
                record_count = COALESCE(%s, record_count),
                message = %s,
                updated_at = now(),
                ingested_at = CASE WHEN %s = 'ingested' THEN now() ELSE ingested_at END
            WHERE dataset_key = %s
            """,
            (status, record_count, message, status, dataset_key),
        )
        conn.commit()


def read_status(dataset_key: str) -> dict | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT dataset_key, title, schema_name, status, record_count, message, updated_at, ingested_at
            FROM trading_desk_admin.ingestion_status
            WHERE dataset_key = %s
            """,
            (dataset_key,),
        ).fetchone()
    return _status_row(row) if row else None


def read_statuses(dataset_keys: list[str]) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT dataset_key, title, schema_name, status, record_count, message, updated_at, ingested_at
            FROM trading_desk_admin.ingestion_status
            WHERE dataset_key = ANY(%s)
            ORDER BY dataset_key
            """,
            (dataset_keys,),
        ).fetchall()
    return [_status_row(row) for row in rows]


def _status_row(row: tuple) -> dict:
    return {
        "dataset_key": row[0],
        "title": row[1],
        "schema_name": row[2],
        "status": row[3],
        "record_count": row[4],
        "message": row[5],
        "updated_at": row[6].isoformat(),
        "ingested_at": row[7].isoformat() if row[7] else None,
    }
