from business.interfaces import PartnerBiz


class BusinessObjectFactory:
    _biz: PartnerBiz | None = None

    @classmethod
    def partner_biz(cls) -> PartnerBiz:
        if cls._biz is None:
            from business.impl.partnerbiz import PartnerBizImpl

            cls._biz = PartnerBizImpl()
        return cls._biz
