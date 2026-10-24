from presentation.api import OrderApi
from presentation.mcp import OrderMcp


class PresentationObjectFactory:
    _api: OrderApi | None = None
    _mcp: OrderMcp | None = None

    @classmethod
    def api(cls) -> OrderApi:
        if cls._api is None:
            cls._api = OrderApi()
        return cls._api

    @classmethod
    def mcp(cls) -> OrderMcp:
        if cls._mcp is None:
            cls._mcp = OrderMcp()
        return cls._mcp
