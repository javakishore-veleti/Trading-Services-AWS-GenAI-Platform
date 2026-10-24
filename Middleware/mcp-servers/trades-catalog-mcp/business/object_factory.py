from business.interfaces import CatalogBiz


class BusinessObjectFactory:
    _biz: CatalogBiz | None = None

    @classmethod
    def catalog_biz(cls) -> CatalogBiz:
        if cls._biz is None:
            from business.impl.catalogbiz import CatalogBizImpl

            cls._biz = CatalogBizImpl()
        return cls._biz
