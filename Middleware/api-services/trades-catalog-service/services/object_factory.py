from services.interfaces import CatalogService


class ServiceObjectFactory:
    _service: CatalogService | None = None

    @classmethod
    def catalog_service(cls) -> CatalogService:
        if cls._service is None:
            from dao.object_factory import DaoObjectFactory
            from services.impl.catalogsvc import CatalogServiceImpl

            cls._service = CatalogServiceImpl(DaoObjectFactory.catalog_dao())
        return cls._service
