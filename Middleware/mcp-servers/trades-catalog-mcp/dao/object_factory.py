from dao.interfaces import CatalogDao


class DaoObjectFactory:
    _dao: CatalogDao | None = None

    @classmethod
    def catalog_dao(cls) -> CatalogDao:
        if cls._dao is None:
            from dao.impl.catalogdao import CatalogDaoImpl

            cls._dao = CatalogDaoImpl()
        return cls._dao
