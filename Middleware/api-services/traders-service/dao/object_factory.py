from dao.interfaces import TradersDao


class DaoObjectFactory:
    _dao: TradersDao | None = None

    @classmethod
    def traders_dao(cls) -> TradersDao:
        if cls._dao is None:
            from dao.impl.store import TradersDaoImpl

            cls._dao = TradersDaoImpl()
        return cls._dao
