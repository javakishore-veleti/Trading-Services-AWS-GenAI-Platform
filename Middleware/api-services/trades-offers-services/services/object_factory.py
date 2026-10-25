from services.interfaces import OffersService


class ServiceObjectFactory:
    _service: OffersService | None = None

    @classmethod
    def offers_service(cls) -> OffersService:
        if cls._service is None:
            from dao.object_factory import DaoObjectFactory
            from services.impl.offerssvc import OffersServiceImpl

            cls._service = OffersServiceImpl(DaoObjectFactory.offers_dao())
        return cls._service
