from dao.interfaces import OfferDao


class DaoObjectFactory:
    _dao: OfferDao | None = None

    @classmethod
    def offer_dao(cls) -> OfferDao:
        if cls._dao is None:
            from dao.impl.offerdao import OfferDaoImpl

            cls._dao = OfferDaoImpl()
        return cls._dao
