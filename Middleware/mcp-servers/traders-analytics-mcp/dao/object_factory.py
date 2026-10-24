from dao.interfaces import AnalyticsDao


class DaoObjectFactory:
    _dao: AnalyticsDao | None = None

    @classmethod
    def analytics_dao(cls) -> AnalyticsDao:
        if cls._dao is None:
            from dao.impl.analyticsdao import AnalyticsDaoImpl

            cls._dao = AnalyticsDaoImpl()
        return cls._dao
