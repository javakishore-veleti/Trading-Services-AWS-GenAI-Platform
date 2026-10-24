from dao.interfaces import PartnerDao


class DaoObjectFactory:
    _dao: PartnerDao | None = None

    @classmethod
    def partner_dao(cls) -> PartnerDao:
        if cls._dao is None:
            from dao.impl.partnerdao import PartnerDaoImpl

            cls._dao = PartnerDaoImpl()
        return cls._dao
