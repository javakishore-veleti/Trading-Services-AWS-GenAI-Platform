from business.interfaces import OfferBiz


class BusinessObjectFactory:
    _biz: OfferBiz | None = None

    @classmethod
    def offer_biz(cls) -> OfferBiz:
        if cls._biz is None:
            from business.impl.offerbiz import OfferBizImpl

            cls._biz = OfferBizImpl()
        return cls._biz
