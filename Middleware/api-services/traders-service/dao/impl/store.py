import json

from psycopg.errors import UniqueViolation
from psycopg.types.json import Json

from common.db import connect, ensure_status_table, read_status, read_statuses, set_status
from common.files import dataset_path, read_json
from dao.interfaces import TradersDao

DATASETS = [
    ("trader_books", "Trading Books", "trader_books"),
    ("traders", "Traders", "traders"),
    ("trader_book_mappings", "Trader and Trading Book mappings", "trader_book_mappings"),
]


class TradersDaoImpl(TradersDao):
    def __init__(self) -> None:
        self.ensure()

    def ensure(self) -> None:
        ensure_status_table(DATASETS)
        with connect() as conn:
            conn.execute("CREATE SCHEMA IF NOT EXISTS trader_books")
            conn.execute("CREATE SCHEMA IF NOT EXISTS traders")
            conn.execute("CREATE SCHEMA IF NOT EXISTS trader_book_mappings")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trader_books.books (
                    book_id text PRIMARY KEY,
                    name text NOT NULL,
                    base_currency text NOT NULL,
                    term_currency text NOT NULL,
                    products jsonb NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS traders.traders (
                    trader_id text PRIMARY KEY,
                    username text NOT NULL,
                    display_name text NOT NULL,
                    desk text NOT NULL,
                    customer_ids jsonb NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trader_book_mappings.mappings (
                    trader_id text NOT NULL,
                    book_id text NOT NULL,
                    PRIMARY KEY (trader_id, book_id)
                )
                """
            )
            conn.commit()

    def statuses(self) -> list[dict]:
        return read_statuses([item[0] for item in DATASETS])

    def status(self, dataset_key: str) -> dict | None:
        return read_status(dataset_key)

    def load_books(self) -> int:
        rows = read_json(dataset_path("TraderBooks", "trader-books.json"))
        set_status("trader_books", "ingesting", None, "")
        try:
            with connect() as conn:
                conn.execute("TRUNCATE trader_books.books")
                with conn.cursor() as cursor:
                    cursor.executemany(
                        """
                        INSERT INTO trader_books.books
                            (book_id, name, base_currency, term_currency, products)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        [
                            (row["book_id"], row["name"], row["base_currency"], row["term_currency"], Json(row["products"]))
                            for row in rows
                        ],
                    )
                conn.commit()
        except Exception as exc:
            set_status("trader_books", "failed", 0, str(exc))
            raise
        set_status("trader_books", "ingested", len(rows), "")
        return len(rows)

    def books(self) -> list[dict]:
        with connect() as conn:
            rows = conn.execute(
                "SELECT book_id, name, base_currency, term_currency, products FROM trader_books.books ORDER BY book_id"
            ).fetchall()
        return [
            {
                "book_id": row[0],
                "name": row[1],
                "base_currency": row[2],
                "term_currency": row[3],
                "products": row[4],
            }
            for row in rows
        ]

    def load_traders(self) -> list[dict]:
        rows = read_json(dataset_path("Traders", "traders.json"))
        set_status("traders", "ingesting", None, "")
        try:
            with connect() as conn:
                conn.execute("TRUNCATE traders.traders")
                with conn.cursor() as cursor:
                    cursor.executemany(
                        """
                        INSERT INTO traders.traders
                            (trader_id, username, display_name, desk, customer_ids)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        [
                            (row["trader_id"], row["username"], row["display_name"], row["desk"], Json(row["customer_ids"]))
                            for row in rows
                        ],
                    )
                conn.commit()
        except Exception as exc:
            set_status("traders", "failed", 0, str(exc))
            raise
        set_status("traders", "ingested", len(rows), "")
        return rows

    def traders(self) -> list[dict]:
        with connect() as conn:
            rows = conn.execute(
                """
                SELECT trader_id, username, display_name, desk, customer_ids
                FROM traders.traders
                ORDER BY trader_id
                """
            ).fetchall()
        return [_trader(row) for row in rows]

    def trader(self, trader_id: str) -> dict | None:
        with connect() as conn:
            row = conn.execute(
                """
                SELECT trader_id, username, display_name, desk, customer_ids
                FROM traders.traders
                WHERE trader_id = %s
                """,
                (trader_id,),
            ).fetchone()
        return _trader(row) if row else None

    def load_mappings(self) -> int:
        with connect() as conn:
            book_ids = {row[0] for row in conn.execute("SELECT book_id FROM trader_books.books").fetchall()}
            trader_ids = {row[0] for row in conn.execute("SELECT trader_id FROM traders.traders").fetchall()}
        if not book_ids or not trader_ids:
            raise RuntimeError("Ingest trading books and traders before the mappings.")
        rows = read_json(dataset_path("Trader-Books-Mappings", "trader-books-mappings.json"))
        for row in rows:
            if row["trader_id"] not in trader_ids or row["book_id"] not in book_ids:
                raise RuntimeError(f"Mapping {row['trader_id']} / {row['book_id']} does not match the ingested records.")
        set_status("trader_book_mappings", "ingesting", None, "")
        try:
            with connect() as conn:
                conn.execute("TRUNCATE trader_book_mappings.mappings")
                with conn.cursor() as cursor:
                    cursor.executemany(
                        "INSERT INTO trader_book_mappings.mappings (trader_id, book_id) VALUES (%s, %s)",
                        [(row["trader_id"], row["book_id"]) for row in rows],
                    )
                conn.commit()
        except Exception as exc:
            set_status("trader_book_mappings", "failed", 0, str(exc))
            raise
        set_status("trader_book_mappings", "ingested", len(rows), "")
        return len(rows)

    def mappings(self) -> list[dict]:
        with connect() as conn:
            rows = conn.execute(
                """
                SELECT trader_id, book_id
                FROM trader_book_mappings.mappings
                ORDER BY trader_id, book_id
                """
            ).fetchall()
        return [{"trader_id": row[0], "book_id": row[1]} for row in rows]

    def books_for(self, trader_id: str) -> list[dict]:
        wanted = {row["book_id"] for row in self.mappings() if row["trader_id"] == trader_id}
        return [book for book in self.books() if book["book_id"] in wanted]

    def add_book(self, row: dict) -> dict:
        try:
            with connect() as conn:
                conn.execute(
                    """
                    INSERT INTO trader_books.books
                        (book_id, name, base_currency, term_currency, products)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (row["book_id"], row["name"], row["base_currency"], row["term_currency"], Json(row["products"])),
                )
                conn.commit()
        except UniqueViolation as exc:
            raise RuntimeError("That trading book already exists.") from exc
        return row

    def add_trader(self, row: dict) -> dict:
        try:
            with connect() as conn:
                conn.execute(
                    """
                    INSERT INTO traders.traders
                        (trader_id, username, display_name, desk, customer_ids)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (row["trader_id"], row["username"], row["display_name"], row["desk"], Json(row["customer_ids"])),
                )
                conn.commit()
        except UniqueViolation as exc:
            raise RuntimeError("That trader already exists.") from exc
        return row

    def add_mapping(self, row: dict) -> dict:
        with connect() as conn:
            book = conn.execute("SELECT 1 FROM trader_books.books WHERE book_id = %s", (row["book_id"],)).fetchone()
            trader = conn.execute("SELECT 1 FROM traders.traders WHERE trader_id = %s", (row["trader_id"],)).fetchone()
        if book is None or trader is None:
            raise RuntimeError("The trader and the trading book both have to exist before they can be mapped.")
        try:
            with connect() as conn:
                conn.execute(
                    "INSERT INTO trader_book_mappings.mappings (trader_id, book_id) VALUES (%s, %s)",
                    (row["trader_id"], row["book_id"]),
                )
                conn.commit()
        except UniqueViolation as exc:
            raise RuntimeError("That trader is already mapped to that book.") from exc
        return row


def _trader(row: tuple) -> dict:
    customer_ids = row[4]
    if isinstance(customer_ids, str):
        customer_ids = json.loads(customer_ids)
    return {
        "trader_id": row[0],
        "username": row[1],
        "display_name": row[2],
        "desk": row[3],
        "customer_ids": customer_ids,
    }
