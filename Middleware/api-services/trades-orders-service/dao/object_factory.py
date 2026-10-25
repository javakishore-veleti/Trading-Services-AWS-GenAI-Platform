from dao.interfaces import OrdersDao


class DaoObjectFactory:
    _dao: OrdersDao | None = None

    @classmethod
    def orders_dao(cls) -> OrdersDao:
        if cls._dao is None:
            from dao.impl.store import OrdersDaoImpl

            cls._dao = OrdersDaoImpl()
        return cls._dao
