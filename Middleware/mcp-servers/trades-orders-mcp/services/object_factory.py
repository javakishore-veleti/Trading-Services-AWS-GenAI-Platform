from services.interfaces import OrderSvc


class ServiceObjectFactory:
    _svc: OrderSvc | None = None

    @classmethod
    def order_svc(cls) -> OrderSvc:
        if cls._svc is None:
            from services.impl.ordersvc import OrderSvcImpl

            cls._svc = OrderSvcImpl()
        return cls._svc
