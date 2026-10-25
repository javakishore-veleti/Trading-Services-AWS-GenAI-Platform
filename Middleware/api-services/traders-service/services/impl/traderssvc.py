from common.guard import register_traders, require_admin
from common.paging import page_of
from dao.interfaces import TradersDao
from services.interfaces import TradersService


class TradersError(Exception):
    def __init__(self, status: int, message: str) -> None:
        self.status = status
        self.message = message
        super().__init__(message)


class TradersServiceImpl(TradersService):
    def __init__(self, dao: TradersDao) -> None:
        self._dao = dao

    def statuses(self) -> dict:
        return {"datasets": self._dao.statuses()}

    def status(self, dataset_key: str) -> dict:
        found = self._dao.status(dataset_key)
        if found is None:
            raise TradersError(404, "That dataset is not tracked.")
        return found

    def populate_books(self, authorization: str) -> dict:
        require_admin(authorization)
        count = self._dao.load_books()
        return {"dataset": "TraderBooks", "count": count}

    def populate_traders(self, authorization: str) -> dict:
        require_admin(authorization)
        rows = self._dao.load_traders()
        register_traders(authorization, rows)
        return {"dataset": "Traders", "count": len(rows), "logins_registered": len(rows)}

    def populate_mappings(self, authorization: str) -> dict:
        require_admin(authorization)
        try:
            count = self._dao.load_mappings()
        except RuntimeError as exc:
            raise TradersError(409, str(exc)) from exc
        return {"dataset": "Trader-Books-Mappings", "count": count}

    def books(self, page: int, page_size: int) -> dict:
        return page_of(self._dao.books(), page, page_size)

    def traders(self, page: int, page_size: int) -> dict:
        rows = [
            {
                "trader_id": row["trader_id"],
                "username": row["username"],
                "display_name": row["display_name"],
                "desk": row["desk"],
                "customer_ids": row["customer_ids"],
            }
            for row in self._dao.traders()
        ]
        return page_of(rows, page, page_size)

    def mappings(self, page: int, page_size: int) -> dict:
        return page_of(self._dao.mappings(), page, page_size)

    def trader(self, trader_id: str) -> dict:
        found = self._dao.trader(trader_id)
        if found is None:
            raise TradersError(404, "That trader is not ingested. Ingest traders in the admin portal.")
        return found

    def customers_for(self, trader_id: str) -> dict:
        found = self.trader(trader_id)
        return {"trader_id": trader_id, "customer_ids": found["customer_ids"]}

    def books_for(self, trader_id: str) -> dict:
        self.trader(trader_id)
        return {"trader_id": trader_id, "books": self._dao.books_for(trader_id)}

    def add_book(self, authorization: str, row: dict) -> dict:
        require_admin(authorization)
        book = {
            "book_id": _text(row.get("book_id"), "Book id"),
            "name": _text(row.get("name"), "Name"),
            "base_currency": _text(row.get("base_currency"), "Base currency").upper(),
            "term_currency": _text(row.get("term_currency"), "Term currency").upper(),
            "products": _words(row.get("products"), "Products"),
        }
        try:
            return self._dao.add_book(book)
        except RuntimeError as exc:
            raise TradersError(409, str(exc)) from exc

    def add_trader(self, authorization: str, row: dict) -> dict:
        require_admin(authorization)
        trader = {
            "trader_id": _text(row.get("trader_id"), "Trader id"),
            "username": _text(row.get("username"), "Username"),
            "display_name": _text(row.get("display_name"), "Display name"),
            "desk": _text(row.get("desk"), "Desk"),
            "customer_ids": _words(row.get("customer_ids"), "Customers", required=False),
        }
        try:
            saved = self._dao.add_trader(trader)
        except RuntimeError as exc:
            raise TradersError(409, str(exc)) from exc
        register_traders(authorization, [saved])
        return saved

    def add_mapping(self, authorization: str, row: dict) -> dict:
        require_admin(authorization)
        mapping = {
            "trader_id": _text(row.get("trader_id"), "Trader id"),
            "book_id": _text(row.get("book_id"), "Book id"),
        }
        try:
            return self._dao.add_mapping(mapping)
        except RuntimeError as exc:
            raise TradersError(409, str(exc)) from exc


def _text(value: object, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise TradersError(400, f"{label} is required.")
    return text


def _words(value: object, label: str, required: bool = True) -> list[str]:
    if isinstance(value, list):
        words = [str(item).strip() for item in value if str(item).strip()]
    else:
        words = [part.strip() for part in str(value or "").split(",") if part.strip()]
    if required and not words:
        raise TradersError(400, f"{label} is required.")
    return words
