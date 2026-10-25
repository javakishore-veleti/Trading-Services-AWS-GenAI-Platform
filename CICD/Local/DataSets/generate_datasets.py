#!/usr/bin/env python3
"""Write the local FX datasets. Rates are illustrative. Re-run from the repo root."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CURRENCIES = [
    "USD", "INR", "GBP", "JPY",
    "EUR", "AUD", "CAD", "CHF", "NZD", "SGD", "HKD", "CNH", "ZAR", "MXN", "TRY",
    "SEK", "NOK", "DKK", "PLN", "CZK", "HUF", "THB", "MYR", "IDR", "KRW", "TWD", "AED", "SAR", "BRL",
]

BOOKS = [
    ("BOOK-01", "USD/INR", "USD", "INR"),
    ("BOOK-02", "EUR/USD", "EUR", "USD"),
    ("BOOK-03", "GBP/USD", "GBP", "USD"),
    ("BOOK-04", "USD/JPY", "USD", "JPY"),
    ("BOOK-05", "AUD/USD", "AUD", "USD"),
    ("BOOK-06", "USD/CAD", "USD", "CAD"),
    ("BOOK-07", "USD/CHF", "USD", "CHF"),
    ("BOOK-08", "NZD/USD", "NZD", "USD"),
    ("BOOK-09", "EUR/GBP", "EUR", "GBP"),
    ("BOOK-10", "EUR/JPY", "EUR", "JPY"),
    ("BOOK-11", "GBP/JPY", "GBP", "JPY"),
    ("BOOK-12", "EUR/INR", "EUR", "INR"),
    ("BOOK-13", "GBP/INR", "GBP", "INR"),
    ("BOOK-14", "USD/SGD", "USD", "SGD"),
    ("BOOK-15", "USD/HKD", "USD", "HKD"),
    ("BOOK-16", "USD/CNH", "USD", "CNH"),
    ("BOOK-17", "AUD/JPY", "AUD", "JPY"),
    ("BOOK-18", "USD/ZAR", "USD", "ZAR"),
    ("BOOK-19", "USD/MXN", "USD", "MXN"),
    ("BOOK-20", "USD/TRY", "USD", "TRY"),
]

EXTRA_PAIRS = [
    ("USD", "SEK"), ("USD", "NOK"), ("USD", "DKK"), ("USD", "PLN"), ("USD", "CZK"),
    ("USD", "HUF"), ("USD", "THB"), ("USD", "MYR"), ("USD", "IDR"), ("USD", "KRW"),
    ("USD", "TWD"), ("USD", "AED"), ("USD", "SAR"), ("USD", "BRL"),
]

# Illustrative history rates. The offers service owns today's USD/INR quote of 96.
RATES = {
    "USD/INR": 83.0, "EUR/USD": 1.08, "GBP/USD": 1.27, "USD/JPY": 151.0,
    "AUD/USD": 0.66, "USD/CAD": 1.36, "USD/CHF": 0.88, "NZD/USD": 0.60,
    "EUR/GBP": 0.85, "EUR/JPY": 163.0, "GBP/JPY": 191.0, "EUR/INR": 90.0,
    "GBP/INR": 105.0, "USD/SGD": 1.34, "USD/HKD": 7.80, "USD/CNH": 7.25,
    "AUD/JPY": 99.0, "USD/ZAR": 18.2, "USD/MXN": 17.1, "USD/TRY": 34.0,
    "USD/SEK": 10.5, "USD/NOK": 10.7, "USD/DKK": 6.9, "USD/PLN": 4.0,
    "USD/CZK": 23.0, "USD/HUF": 365.0, "USD/THB": 34.5, "USD/MYR": 4.4,
    "USD/IDR": 15800.0, "USD/KRW": 1350.0, "USD/TWD": 32.0, "USD/AED": 3.67,
    "USD/SAR": 3.75, "USD/BRL": 5.4,
}

ZERO_DECIMALS = {"JPY", "KRW", "IDR", "HUF"}
PRODUCTS = ("SPOT", "WINDOW_FORWARD", "CURRENCY_FUTURES")


def add_business_days(start: str, days: int) -> str:
    cursor = date.fromisoformat(start)
    left = days
    while left:
        cursor += timedelta(days=1)
        if cursor.weekday() < 5:
            left -= 1
    return cursor.isoformat()


def money(amount: float, currency: str) -> float:
    if currency in ZERO_DECIMALS:
        return float(round(amount))
    return round(amount, 2)


def split_amount(total: int, parts: int) -> list[int]:
    base = total // parts
    lines = [base] * parts
    lines[-1] = total - base * (parts - 1)
    return lines


def book_id_for(base: str, term: str) -> str | None:
    pair = f"{base}/{term}"
    for book_id, name, _base, _term in BOOKS:
        if name == pair:
            return book_id
    return None


def legs(order_id: str, value_date: str, sell_ccy: str, sell_amount: float, buy_ccy: str, rate: float, line_type: str, start: int) -> list[dict]:
    buy_amount = money(sell_amount * rate, buy_ccy)
    return [
        {
            "line_id": f"{order_id}-{start}",
            "line_number": start,
            "line_type": line_type,
            "value_date": value_date,
            "sell_currency": sell_ccy,
            "sell_amount": sell_amount,
            "buy_currency": buy_ccy,
            "buy_amount": buy_amount,
            "rate": rate,
            "rate_basis": "illustrative",
        }
    ]


def header(order_id: str, customer_id: str, product: str, base: str, term: str, amount: int, order_date: str, pattern: str, window: tuple[str, str] | None, expiry: str | None, margin: bool) -> dict:
    return {
        "order_id": order_id,
        "customer_id": customer_id,
        "book_id": book_id_for(base, term),
        "product_id": product,
        "base_currency": base,
        "term_currency": term,
        "direction": "sell_base",
        "amount": amount,
        "currency": base,
        "order_date": order_date,
        "settlement_pattern": pattern,
        "window_start": window[0] if window else None,
        "window_end": window[1] if window else None,
        "futures_expiry": expiry,
        "margin_required": margin,
        "status": "settled",
        "rate_basis": "illustrative",
    }


def spot_order(order_id: str, customer_id: str, base: str, term: str, amount: int, order_date: str) -> dict:
    rate = RATES[f"{base}/{term}"]
    value_date = add_business_days(order_date, 2)
    body = header(order_id, customer_id, "SPOT", base, term, amount, order_date, "single settlement", None, None, False)
    pay, = legs(order_id, value_date, base, amount, term, rate, "pay", 1)
    receive = dict(pay)
    receive["line_id"] = f"{order_id}-2"
    receive["line_number"] = 2
    receive["line_type"] = "receive"
    return {"order_header": body, "order_lines": [pay, receive]}


def window_order(order_id: str, customer_id: str, base: str, term: str, amount: int, order_date: str, window: tuple[str, str], value_dates: list[str], pattern: str) -> dict:
    rate = RATES[f"{base}/{term}"]
    parts = split_amount(amount, len(value_dates))
    body = header(order_id, customer_id, "WINDOW_FORWARD", base, term, amount, order_date, pattern, window, None, False)
    lines: list[dict] = []
    for index, (value_date, part) in enumerate(zip(value_dates, parts), start=1):
        lines.extend(legs(order_id, value_date, base, part, term, rate, "settlement", index))
    return {"order_header": body, "order_lines": lines}


def futures_order(order_id: str, customer_id: str, base: str, term: str, amount: int, order_date: str, expiry: str) -> dict:
    rate = RATES[f"{base}/{term}"]
    margin = money(max(amount * 0.05, 1000), base)
    body = header(
        order_id, customer_id, "CURRENCY_FUTURES", base, term, amount, order_date,
        "fixed contract expiry", None, expiry, True,
    )
    lines = legs(order_id, expiry, base, amount, term, rate, "contract", 1)
    lines.extend(legs(order_id, order_date, base, margin, base, 1.0, "margin", 2))
    return {"order_header": body, "order_lines": lines}


def customers() -> list[dict]:
    rows = []
    specials = {
        1: ("Northwind Exports", "IN", True),
        2: ("Harbor Retail", "IN", True),
    }
    for number in range(1, 101):
        customer_id = f"CUST-{number:03d}"
        name, country, resident = specials.get(number, (f"Customer {number:03d}", "IN" if number % 2 == 0 else "US", True))
        window_customer = number == 1 or (number > 2 and number % 2 == 0)
        if number == 2:
            window_customer = False
        if window_customer:
            preferences = {
                "preferred_product": "WINDOW_FORWARD",
                "typical_size": 1000000 if number == 1 else 400000 + number * 1000,
                "typical_currency": "USD",
                "hedging": "rate certainty with flexible settlement dates",
                "note": "Frequently uses Window Forwards when receiving currency across multiple dates.",
            }
            requirement = {
                "requirement_id": f"SET-{number:03d}",
                "base_currency": "USD",
                "term_currency": "INR",
                "direction": "sell_base",
                "amount": 1000000 if number == 1 else 500000,
                "currency": "USD",
                "usd_available_now": False,
                "window_days": 30,
                "dates": ["2026-11-10", "2026-11-18", "2026-11-27"],
                "purpose": "Expected receivables. The term currency is needed on more than one date.",
            }
        else:
            preferences = {
                "preferred_product": "SPOT",
                "typical_size": 250000 if number == 2 else 200000 + number * 1000,
                "typical_currency": "USD",
                "hedging": "immediate conversion",
                "note": "Usually converts currency that is already available.",
            }
            requirement = {
                "requirement_id": f"SET-{number:03d}",
                "base_currency": "USD",
                "term_currency": "INR",
                "direction": "sell_base",
                "amount": 250000 if number == 2 else 200000,
                "currency": "USD",
                "usd_available_now": True,
                "window_days": 2,
                "dates": ["2026-10-28"],
                "purpose": "Currency is available for near-term conversion.",
            }
        rows.append({
            "customer_id": customer_id,
            "name": name,
            "country": country,
            "resident": resident,
            "preferences": preferences,
            "settlement_requirement": requirement,
        })
    return rows


def traders() -> list[dict]:
    rows = []
    for number in range(1, 101):
        customer_numbers = {number, ((number + 19) % 100) + 1, ((number + 39) % 100) + 1}
        if number == 1:
            customer_numbers.update({1, 2})
        rows.append({
            "trader_id": f"TRADER-{number:03d}",
            "username": f"trader{number:03d}",
            "display_name": f"Trader {number:03d}",
            "desk": "FX Trading Desk",
            "customer_ids": [f"CUST-{item:03d}" for item in sorted(customer_numbers)],
        })
    return rows


def books() -> list[dict]:
    return [
        {
            "book_id": book_id,
            "name": name,
            "base_currency": base,
            "term_currency": term,
            "products": list(PRODUCTS),
        }
        for book_id, name, base, term in BOOKS
    ]


def mappings() -> list[dict]:
    rows = []
    for number in range(1, 101):
        first = ((number - 1) % 20) + 1
        second = ((number + 6) % 20) + 1
        for book_number in (first, second):
            rows.append({
                "trader_id": f"TRADER-{number:03d}",
                "book_id": f"BOOK-{book_number:02d}",
            })
    return rows


def orders() -> list[dict]:
    rows = [
        spot_order("ORD-000001", "CUST-001", "USD", "INR", 750000, "2026-03-02"),
        window_order(
            "ORD-000002", "CUST-001", "USD", "INR", 1200000, "2026-04-01",
            ("2026-04-06", "2026-04-24"),
            ["2026-04-08", "2026-04-15", "2026-04-22"],
            "three partial settlements",
        ),
        spot_order("ORD-000003", "CUST-001", "USD", "INR", 900000, "2026-05-04"),
        window_order(
            "ORD-000004", "CUST-001", "USD", "INR", 1500000, "2026-07-01",
            ("2026-07-06", "2026-07-27"),
            ["2026-07-06", "2026-07-13", "2026-07-20", "2026-07-27"],
            "multiple settlements over 20 days",
        ),
        spot_order("ORD-000005", "CUST-002", "USD", "INR", 180000, "2026-02-02"),
        spot_order("ORD-000006", "CUST-002", "USD", "INR", 250000, "2026-06-01"),
    ]
    sequence = 7
    pairs = [(base, term) for _book, _name, base, term in BOOKS] + EXTRA_PAIRS
    for number in range(3, 101):
        customer_id = f"CUST-{number:03d}"
        base, term = pairs[(number - 3) % len(pairs)]
        amount = 100000 + number * 1000
        product = PRODUCTS[(number - 3) % 3]
        order_id = f"ORD-{sequence:06d}"
        sequence += 1
        if product == "SPOT":
            rows.append(spot_order(order_id, customer_id, base, term, amount, "2026-03-02"))
        elif product == "WINDOW_FORWARD":
            rows.append(window_order(
                order_id, customer_id, base, term, amount, "2026-04-01",
                ("2026-04-06", "2026-04-24"),
                ["2026-04-08", "2026-04-15", "2026-04-22"],
                "three partial settlements",
            ))
        else:
            rows.append(futures_order(order_id, customer_id, base, term, amount, "2026-05-04", "2026-11-26"))
        if (number - 3) < len(EXTRA_PAIRS) and product != "SPOT":
            extra_base, extra_term = EXTRA_PAIRS[number - 3]
            extra_id = f"ORD-{sequence:06d}"
            sequence += 1
            rows.append(spot_order(extra_id, customer_id, extra_base, extra_term, 150000, "2026-08-03"))
    return rows


def write(folder: str, filename: str, payload: object) -> None:
    destination = ROOT / folder
    destination.mkdir(parents=True, exist_ok=True)
    (destination / filename).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def currencies_used(order_rows: list[dict]) -> set[str]:
    found: set[str] = set()
    for order in order_rows:
        for line in order["order_lines"]:
            found.add(line["sell_currency"])
            found.add(line["buy_currency"])
    return found


def check(customer_rows: list[dict], trader_rows: list[dict], book_rows: list[dict], mapping_rows: list[dict], order_rows: list[dict]) -> None:
    assert len(customer_rows) == 100
    assert len(trader_rows) == 100
    assert len(book_rows) == 20
    assert len(mapping_rows) == 200
    assert customer_rows[0]["name"] == "Northwind Exports"
    assert customer_rows[1]["name"] == "Harbor Retail"
    trader_one = trader_rows[0]
    assert "CUST-001" in trader_one["customer_ids"] and "CUST-002" in trader_one["customer_ids"]
    assert {"trader_id": "TRADER-001", "book_id": "BOOK-01"} in mapping_rows
    northwind = [order for order in order_rows if order["order_header"]["customer_id"] == "CUST-001"]
    assert [order["order_header"]["amount"] for order in northwind] == [750000, 1200000, 900000, 1500000]
    assert [order["order_header"]["settlement_pattern"] for order in northwind] == [
        "single settlement",
        "three partial settlements",
        "single settlement",
        "multiple settlements over 20 days",
    ]
    for order in order_rows:
        lines = order["order_lines"]
        assert len(lines) >= 2
        head = order["order_header"]
        if head["product_id"] == "SPOT":
            assert lines[0]["value_date"] == add_business_days(head["order_date"], 2)
        if head["product_id"] == "WINDOW_FORWARD":
            assert sum(line["sell_amount"] for line in lines) == head["amount"]
            for line in lines:
                assert head["window_start"] <= line["value_date"] <= head["window_end"]
        if head["product_id"] == "CURRENCY_FUTURES":
            assert head["margin_required"] is True
            assert head["futures_expiry"]
            assert any(line["line_type"] == "margin" for line in lines)
    assert currencies_used(order_rows) == set(CURRENCIES)
    assert {order["order_header"]["product_id"] for order in order_rows} == set(PRODUCTS)
    blob = json.dumps({"customers": customer_rows, "traders": trader_rows, "orders": order_rows})
    assert "password" not in blob


def main() -> None:
    customer_rows = customers()
    trader_rows = traders()
    book_rows = books()
    mapping_rows = mappings()
    order_rows = orders()
    check(customer_rows, trader_rows, book_rows, mapping_rows, order_rows)
    write("Customers", "customers.json", customer_rows)
    write("TraderBooks", "trader-books.json", book_rows)
    write("Traders", "traders.json", trader_rows)
    write("Trader-Books-Mappings", "trader-books-mappings.json", mapping_rows)
    write("Customer-Trades-History", "orders.json", order_rows)
    print(f"customers {len(customer_rows)}")
    print(f"books {len(book_rows)}")
    print(f"traders {len(trader_rows)}")
    print(f"mappings {len(mapping_rows)}")
    print(f"orders {len(order_rows)}")


if __name__ == "__main__":
    main()
