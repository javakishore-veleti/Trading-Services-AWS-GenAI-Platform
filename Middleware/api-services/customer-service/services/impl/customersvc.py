from common.guard import require_admin
from common.paging import page_of
from dao.interfaces import CustomerDao
from services.interfaces import CustomerService


class CustomerError(Exception):
    def __init__(self, status: int, message: str) -> None:
        self.status = status
        self.message = message
        super().__init__(message)


class CustomerServiceImpl(CustomerService):
    def __init__(self, dao: CustomerDao) -> None:
        self._dao = dao

    def statuses(self) -> dict:
        return {"datasets": self._dao.statuses()}

    def status(self, dataset_key: str) -> dict:
        found = self._dao.status(dataset_key)
        if found is None:
            raise CustomerError(404, "That dataset is not tracked.")
        return found

    def populate_customers(self, authorization: str) -> dict:
        require_admin(authorization)
        return {"dataset": "Customers", "count": self._dao.load_customers()}

    def populate_orders(self, authorization: str) -> dict:
        require_admin(authorization)
        try:
            count = self._dao.load_orders()
        except RuntimeError as exc:
            raise CustomerError(409, str(exc)) from exc
        return {"dataset": "Customer-Trades-History", "count": count}

    def customers(self, page: int, page_size: int) -> dict:
        rows = [_summary(row) for row in self._dao.customers()]
        return page_of(rows, page, page_size)

    def customer(self, customer_id: str) -> dict:
        found = self._dao.customer(customer_id)
        if found is None:
            raise CustomerError(404, "That customer is not ingested. Ingest customers in the admin portal.")
        return found

    def orders_for(self, customer_id: str) -> dict:
        self.customer(customer_id)
        return {"customer_id": customer_id, "orders": self._dao.orders_for(customer_id)}

    def orders(self, page: int, page_size: int) -> dict:
        rows = [_order_summary(order) for order in self._dao.orders()]
        return page_of(rows, page, page_size)

    def many(self, customer_ids: list[str]) -> dict:
        rows = []
        for customer_id in customer_ids:
            found = self._dao.customer(customer_id)
            if found is not None:
                rows.append(_summary(found))
        return {"customers": rows}


    def add_customer(self, authorization: str, row: dict) -> dict:
        require_admin(authorization)
        customer_id = _text(row.get("customer_id"), "Customer id")
        preferred = _text(row.get("preferred_product"), "Preferred product")
        if preferred not in {"SPOT", "WINDOW_FORWARD", "CURRENCY_FUTURES"}:
            raise CustomerError(400, "Preferred product must be Spot, Window Forward, or Currency Futures.")
        dates = _words(row.get("dates"))
        amount = _number(row.get("amount"), "Amount")
        customer = {
            "customer_id": customer_id,
            "name": _text(row.get("name"), "Name"),
            "country": _text(row.get("country"), "Country").upper(),
            "resident": bool(row.get("resident")),
            "preferences": {
                "preferred_product": preferred,
                "typical_size": amount,
                "typical_currency": _text(row.get("currency"), "Currency").upper(),
                "hedging": "",
                "note": "Added from Desk Management.",
            },
            "settlement_requirement": {
                "requirement_id": f"SET-{customer_id}",
                "base_currency": _text(row.get("base_currency"), "Base currency").upper(),
                "term_currency": _text(row.get("term_currency"), "Term currency").upper(),
                "direction": "sell_base",
                "amount": amount,
                "currency": _text(row.get("currency"), "Currency").upper(),
                "usd_available_now": bool(row.get("usd_available_now")),
                "window_days": 30,
                "dates": dates,
                "purpose": "Added from Desk Management.",
            },
        }
        try:
            return self._dao.add_customer(customer)
        except RuntimeError as exc:
            raise CustomerError(409, str(exc)) from exc

    def add_order(self, authorization: str, row: dict) -> dict:
        require_admin(authorization)
        order_id = _text(row.get("order_id"), "Order id")
        product_id = _text(row.get("product_id"), "Product")
        if product_id not in {"SPOT", "WINDOW_FORWARD", "CURRENCY_FUTURES"}:
            raise CustomerError(400, "Product must be Spot, Window Forward, or Currency Futures.")
        amount = _number(row.get("amount"), "Amount")
        rate = _number(row.get("rate"), "Rate")
        base = _text(row.get("base_currency"), "Base currency").upper()
        term = _text(row.get("term_currency"), "Term currency").upper()
        currency = _text(row.get("currency"), "Currency").upper()
        value_date = _text(row.get("value_date"), "Value date")
        buy_amount = round(amount * rate, 2)
        head = {
            "order_id": order_id,
            "customer_id": _text(row.get("customer_id"), "Customer id"),
            "book_id": _text(row.get("book_id"), "Book id"),
            "product_id": product_id,
            "base_currency": base,
            "term_currency": term,
            "direction": "sell_base",
            "amount": amount,
            "currency": currency,
            "order_date": _text(row.get("order_date"), "Order date"),
            "settlement_pattern": "single settlement",
            "window_start": None,
            "window_end": None,
            "futures_expiry": None,
            "margin_required": product_id == "CURRENCY_FUTURES",
            "status": "open",
            "rate_basis": "illustrative",
        }
        lines = [
            _line(order_id, 1, "pay", value_date, base, amount, term, buy_amount, rate),
            _line(order_id, 2, "receive", value_date, base, amount, term, buy_amount, rate),
        ]
        try:
            saved = self._dao.add_order({"order_header": head, "order_lines": lines})
        except RuntimeError as exc:
            raise CustomerError(409, str(exc)) from exc
        return _order_summary(saved)


def _text(value: object, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise CustomerError(400, f"{label} is required.")
    return text


def _words(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in str(value or "").split(",") if part.strip()]


def _number(value: object, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise CustomerError(400, f"{label} must be a number.") from exc


def _line(order_id: str, number: int, line_type: str, value_date: str, sell: str, amount: float, buy: str, buy_amount: float, rate: float) -> dict:
    return {
        "line_id": f"{order_id}-{number}",
        "line_number": number,
        "line_type": line_type,
        "value_date": value_date,
        "sell_currency": sell,
        "sell_amount": amount,
        "buy_currency": buy,
        "buy_amount": buy_amount,
        "rate": rate,
        "rate_basis": "illustrative",
    }


def _summary(row: dict) -> dict:
    return {
        "customer_id": row["customer_id"],
        "name": row["name"],
        "country": row["country"],
        "preferred_product": row["preferences"]["preferred_product"],
        "settlement_dates": row["settlement_requirement"]["dates"],
    }


def _order_summary(order: dict) -> dict:
    head = order["order_header"]
    return {
        "order_id": head["order_id"],
        "customer_id": head["customer_id"],
        "product_id": head["product_id"],
        "amount": head["amount"],
        "currency": head["currency"],
        "base_currency": head["base_currency"],
        "term_currency": head["term_currency"],
        "settlement_pattern": head["settlement_pattern"],
        "line_count": len(order["order_lines"]),
    }
