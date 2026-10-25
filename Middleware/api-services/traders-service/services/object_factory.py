from services.interfaces import TradersService


class ServiceObjectFactory:
    _service: TradersService | None = None

    @classmethod
    def traders_service(cls) -> TradersService:
        if cls._service is None:
            from dao.object_factory import DaoObjectFactory
            from services.impl.traderssvc import TradersServiceImpl

            cls._service = TradersServiceImpl(DaoObjectFactory.traders_dao())
        return cls._service
