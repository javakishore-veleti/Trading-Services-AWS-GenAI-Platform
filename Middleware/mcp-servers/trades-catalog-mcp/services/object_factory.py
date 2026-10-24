from services.interfaces import CatalogSvc


class ServiceObjectFactory:
    _svc: CatalogSvc | None = None

    @classmethod
    def catalog_svc(cls) -> CatalogSvc:
        if cls._svc is None:
            from services.impl.catalogsvc import CatalogSvcImpl

            cls._svc = CatalogSvcImpl()
        return cls._svc
