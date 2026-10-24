from presentation.api import AnalyticsApi
from presentation.mcp import AnalyticsMcp


class PresentationObjectFactory:
    _api: AnalyticsApi | None = None
    _mcp: AnalyticsMcp | None = None

    @classmethod
    def api(cls) -> AnalyticsApi:
        if cls._api is None:
            cls._api = AnalyticsApi()
        return cls._api

    @classmethod
    def mcp(cls) -> AnalyticsMcp:
        if cls._mcp is None:
            cls._mcp = AnalyticsMcp()
        return cls._mcp
