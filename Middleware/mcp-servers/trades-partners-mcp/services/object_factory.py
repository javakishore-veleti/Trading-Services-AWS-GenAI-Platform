from services.interfaces import PartnerSvc


class ServiceObjectFactory:
    _svc: PartnerSvc | None = None

    @classmethod
    def partner_svc(cls) -> PartnerSvc:
        if cls._svc is None:
            from services.impl.partnersvc import PartnerSvcImpl

            cls._svc = PartnerSvcImpl()
        return cls._svc
