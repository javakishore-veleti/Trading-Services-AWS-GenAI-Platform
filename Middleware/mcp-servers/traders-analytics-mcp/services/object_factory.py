from services.interfaces import AnalyticsSvc


class ServiceObjectFactory:
    _svc: AnalyticsSvc | None = None

    @classmethod
    def analytics_svc(cls) -> AnalyticsSvc:
        if cls._svc is None:
            from services.impl.analyticssvc import AnalyticsSvcImpl

            cls._svc = AnalyticsSvcImpl()
        return cls._svc
