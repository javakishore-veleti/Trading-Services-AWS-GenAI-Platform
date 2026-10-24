from business.interfaces import OrderBiz


class BusinessObjectFactory:
    _biz: OrderBiz | None = None

    @classmethod
    def order_biz(cls) -> OrderBiz:
        if cls._biz is None:
            from business.impl.orderbiz import OrderBizImpl

            cls._biz = OrderBizImpl()
        return cls._biz
