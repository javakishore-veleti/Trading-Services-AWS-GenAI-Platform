from services.interfaces import OrdersService


class ServiceObjectFactory:
    _service: OrdersService | None = None

    @classmethod
    def orders_service(cls) -> OrdersService:
        if cls._service is None:
            from dao.object_factory import DaoObjectFactory
            from services.impl.orderssvc import OrdersServiceImpl

            cls._service = OrdersServiceImpl(DaoObjectFactory.orders_dao())
        return cls._service
