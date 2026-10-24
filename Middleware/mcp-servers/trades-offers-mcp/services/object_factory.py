from services.interfaces import OfferSvc


class ServiceObjectFactory:
    _svc: OfferSvc | None = None

    @classmethod
    def offer_svc(cls) -> OfferSvc:
        if cls._svc is None:
            from services.impl.offersvc import OfferSvcImpl

            cls._svc = OfferSvcImpl()
        return cls._svc
