from dao.interfaces import OffersDao


class DaoObjectFactory:
    _dao: OffersDao | None = None

    @classmethod
    def offers_dao(cls) -> OffersDao:
        if cls._dao is None:
            from dao.impl.store import OffersDaoImpl

            cls._dao = OffersDaoImpl()
        return cls._dao
