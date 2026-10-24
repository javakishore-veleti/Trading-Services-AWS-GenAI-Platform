from business.interfaces import AnalyticsBiz


class BusinessObjectFactory:
    _biz: AnalyticsBiz | None = None

    @classmethod
    def analytics_biz(cls) -> AnalyticsBiz:
        if cls._biz is None:
            from business.impl.analyticsbiz import AnalyticsBizImpl

            cls._biz = AnalyticsBizImpl()
        return cls._biz
