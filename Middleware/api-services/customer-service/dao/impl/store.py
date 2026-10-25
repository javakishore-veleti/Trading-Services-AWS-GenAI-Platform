import json

from psycopg.errors import UniqueViolation
from psycopg.types.json import Json

from common.db import connect, ensure_status_table, read_status, read_statuses, set_status
from common.files import dataset_path, read_json
from dao.interfaces import CustomerDao

DATASETS = [
    ("customers", "Customers", "customers"),
    ("customer_trades_history", "Customer trades history", "customer_trades"),
]


class CustomerDaoImpl(CustomerDao):
    def __init__(self) -> None:
        self.ensure()

    def ensure(self) -> None:
        ensure_status_table(DATASETS)
        with connect() as conn:
            conn.execute("CREATE SCHEMA IF NOT EXISTS customers")
            conn.execute("CREATE SCHEMA IF NOT EXISTS customer_trades")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS customers.customers (
                    customer_id text PRIMARY KEY,
                    name text NOT NULL,
                    country text NOT NULL,
                    resident boolean NOT NULL,
                    preferences jsonb NOT NULL,
                    settlement_requirement jsonb NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS customer_trades.order_headers (
                    order_id text PRIMARY KEY,
                    customer_id text NOT NULL,
                    book_id text,
                    product_id text NOT NULL,
                    base_currency text NOT NULL,
                    term_currency text NOT NULL,
                    direction text NOT NULL,
                    amount numeric NOT NULL,
                    currency text NOT NULL,
                    order_date date NOT NULL,
                    settlement_pattern text NOT NULL,
                    window_start date,
                    window_end date,
                    futures_expiry date,
                    margin_required boolean NOT NULL,
                    status text NOT NULL,
                    rate_basis text NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS customer_trades.order_lines (
                    line_id text PRIMARY KEY,
                    order_id text NOT NULL REFERENCES customer_trades.order_headers (order_id),
                    line_number integer NOT NULL,
                    line_type text NOT NULL,
                    value_date date NOT NULL,
                    sell_currency text NOT NULL,
                    sell_amount numeric NOT NULL,
                    buy_currency text NOT NULL,
                    buy_amount numeric NOT NULL,
                    rate numeric NOT NULL,
                    rate_basis text NOT NULL
                )
                """
            )
            conn.commit()

    def statuses(self) -> list[dict]:
        return read_statuses([item[0] for item in DATASETS])

    def status(self, dataset_key: str) -> dict | None:
        return read_status(dataset_key)

    def load_customers(self) -> int:
        rows = read_json(dataset_path("Customers", "customers.json"))
        set_status("customers", "ingesting", None, "")
        try:
            with connect() as conn:
                conn.execute("TRUNCATE customers.customers")
                with conn.cursor() as cursor:
                    cursor.executemany(
                        """
                        INSERT INTO customers.customers
                            (customer_id, name, country, resident, preferences, settlement_requirement)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        [
                            (
                                row["customer_id"],
                                row["name"],
                                row["country"],
                                row["resident"],
                                Json(row["preferences"]),
                                Json(row["settlement_requirement"]),
                            )
                            for row in rows
                        ],
                    )
                conn.commit()
        except Exception as exc:
            set_status("customers", "failed", 0, str(exc))
            raise
        set_status("customers", "ingested", len(rows), "")
        return len(rows)

    def customers(self) -> list[dict]:
        with connect() as conn:
            rows = conn.execute(
                """
                SELECT customer_id, name, country, resident, preferences, settlement_requirement
                FROM customers.customers
                ORDER BY customer_id
                """
            ).fetchall()
        return [_customer(row) for row in rows]

    def customer(self, customer_id: str) -> dict | None:
        with connect() as conn:
            row = conn.execute(
                """
                SELECT customer_id, name, country, resident, preferences, settlement_requirement
                FROM customers.customers
                WHERE customer_id = %s
                """,
                (customer_id,),
            ).fetchone()
        return _customer(row) if row else None

    def load_orders(self) -> int:
        with connect() as conn:
            known = {row[0] for row in conn.execute("SELECT customer_id FROM customers.customers").fetchall()}
        if not known:
            raise RuntimeError("Ingest customers before the trade history.")
        orders = read_json(dataset_path("Customer-Trades-History", "orders.json"))
        for order in orders:
            head = order["order_header"]
            if head["customer_id"] not in known:
                raise RuntimeError(f"Order {head['order_id']} names an unknown customer {head['customer_id']}.")
            if len(order.get("order_lines", [])) < 2:
                raise RuntimeError(f"Order {head['order_id']} needs a header and more than one line.")
        set_status("customer_trades_history", "ingesting", None, "")
        try:
            with connect() as conn:
                conn.execute("TRUNCATE customer_trades.order_lines, customer_trades.order_headers")
                with conn.cursor() as cursor:
                    cursor.executemany(
                        """
                        INSERT INTO customer_trades.order_headers (
                            order_id, customer_id, book_id, product_id, base_currency, term_currency,
                            direction, amount, currency, order_date, settlement_pattern,
                            window_start, window_end, futures_expiry, margin_required, status, rate_basis
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        [_header_values(order["order_header"]) for order in orders],
                    )
                    cursor.executemany(
                        """
                        INSERT INTO customer_trades.order_lines (
                            line_id, order_id, line_number, line_type, value_date,
                            sell_currency, sell_amount, buy_currency, buy_amount, rate, rate_basis
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        [
                            _line_values(order["order_header"]["order_id"], line)
                            for order in orders
                            for line in order["order_lines"]
                        ],
                    )
                conn.commit()
        except Exception as exc:
            set_status("customer_trades_history", "failed", 0, str(exc))
            raise
        set_status("customer_trades_history", "ingested", len(orders), "")
        return len(orders)

    def orders_for(self, customer_id: str) -> list[dict]:
        return [order for order in self.orders() if order["order_header"]["customer_id"] == customer_id]

    def orders(self) -> list[dict]:
        with connect() as conn:
            headers = conn.execute(
                """
                SELECT order_id, customer_id, book_id, product_id, base_currency, term_currency,
                       direction, amount, currency, order_date, settlement_pattern,
                       window_start, window_end, futures_expiry, margin_required, status, rate_basis
                FROM customer_trades.order_headers
                ORDER BY order_id
                """
            ).fetchall()
            lines = conn.execute(
                """
                SELECT line_id, order_id, line_number, line_type, value_date,
                       sell_currency, sell_amount, buy_currency, buy_amount, rate, rate_basis
                FROM customer_trades.order_lines
                ORDER BY order_id, line_number
                """
            ).fetchall()
        grouped: dict[str, list[dict]] = {}
        for line in lines:
            grouped.setdefault(line[1], []).append({
                "line_id": line[0],
                "line_number": line[2],
                "line_type": line[3],
                "value_date": _date(line[4]),
                "sell_currency": line[5],
                "sell_amount": float(line[6]),
                "buy_currency": line[7],
                "buy_amount": float(line[8]),
                "rate": float(line[9]),
                "rate_basis": line[10],
            })
        return [{"order_header": _header(row), "order_lines": grouped.get(row[0], [])} for row in headers]

    def add_customer(self, row: dict) -> dict:
        try:
            with connect() as conn:
                conn.execute(
                    """
                    INSERT INTO customers.customers
                        (customer_id, name, country, resident, preferences, settlement_requirement)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        row["customer_id"],
                        row["name"],
                        row["country"],
                        row["resident"],
                        Json(row["preferences"]),
                        Json(row["settlement_requirement"]),
                    ),
                )
                conn.commit()
        except UniqueViolation as exc:
            raise RuntimeError("That customer already exists.") from exc
        return row

    def add_order(self, order: dict) -> dict:
        head = order["order_header"]
        with connect() as conn:
            known = conn.execute(
                "SELECT 1 FROM customers.customers WHERE customer_id = %s",
                (head["customer_id"],),
            ).fetchone()
        if known is None:
            raise RuntimeError("That customer is not on the desk yet.")
        if len(order.get("order_lines", [])) < 2:
            raise RuntimeError("A trade needs a header and at least two lines.")
        try:
            with connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO customer_trades.order_headers (
                            order_id, customer_id, book_id, product_id, base_currency, term_currency,
                            direction, amount, currency, order_date, settlement_pattern,
                            window_start, window_end, futures_expiry, margin_required, status, rate_basis
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        _header_values(head),
                    )
                    cursor.executemany(
                        """
                        INSERT INTO customer_trades.order_lines (
                            line_id, order_id, line_number, line_type, value_date,
                            sell_currency, sell_amount, buy_currency, buy_amount, rate, rate_basis
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        [_line_values(head["order_id"], line) for line in order["order_lines"]],
                    )
                conn.commit()
        except UniqueViolation as exc:
            raise RuntimeError("That trade already exists.") from exc
        return order


def _customer(row: tuple) -> dict:
    return {
        "customer_id": row[0],
        "name": row[1],
        "country": row[2],
        "resident": row[3],
        "preferences": _json(row[4]),
        "settlement_requirement": _json(row[5]),
    }


def _header_values(head: dict) -> tuple:
    return (
        head["order_id"],
        head["customer_id"],
        head.get("book_id"),
        head["product_id"],
        head["base_currency"],
        head["term_currency"],
        head["direction"],
        head["amount"],
        head["currency"],
        head["order_date"],
        head["settlement_pattern"],
        head.get("window_start"),
        head.get("window_end"),
        head.get("futures_expiry"),
        head["margin_required"],
        head["status"],
        head["rate_basis"],
    )


def _line_values(order_id: str, line: dict) -> tuple:
    return (
        line["line_id"],
        order_id,
        line["line_number"],
        line["line_type"],
        line["value_date"],
        line["sell_currency"],
        line["sell_amount"],
        line["buy_currency"],
        line["buy_amount"],
        line["rate"],
        line["rate_basis"],
    )


def _header(row: tuple) -> dict:
    return {
        "order_id": row[0],
        "customer_id": row[1],
        "book_id": row[2],
        "product_id": row[3],
        "base_currency": row[4],
        "term_currency": row[5],
        "direction": row[6],
        "amount": float(row[7]),
        "currency": row[8],
        "order_date": _date(row[9]),
        "settlement_pattern": row[10],
        "window_start": _date(row[11]),
        "window_end": _date(row[12]),
        "futures_expiry": _date(row[13]),
        "margin_required": row[14],
        "status": row[15],
        "rate_basis": row[16],
    }


def _json(value):
    return json.loads(value) if isinstance(value, str) else value


def _date(value):
    return value.isoformat() if value is not None and hasattr(value, "isoformat") else value
