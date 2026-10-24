from dao.interfaces import OrderDao


class DaoObjectFactory:
    _dao: OrderDao | None = None

    @classmethod
    def order_dao(cls) -> OrderDao:
        if cls._dao is None:
            from dao.impl.orderdao import OrderDaoImpl

            cls._dao = OrderDaoImpl()
        return cls._dao
