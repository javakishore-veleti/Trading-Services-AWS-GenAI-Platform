from dao.interfaces import OrdersDao


class OrdersDaoImpl(OrdersDao):
    def __init__(self) -> None:
        self._orders: list[dict] = []

    def add(self, order: dict) -> dict:
        self._orders.insert(0, order)
        return order

    def for_trader(self, trader_id: str) -> list[dict]:
        return [order for order in self._orders if order["trader_id"] == trader_id]
