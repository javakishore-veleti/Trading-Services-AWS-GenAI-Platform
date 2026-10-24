from presentation.api import OfferApi
from presentation.mcp import OfferMcp


class PresentationObjectFactory:
    _api: OfferApi | None = None
    _mcp: OfferMcp | None = None

    @classmethod
    def api(cls) -> OfferApi:
        if cls._api is None:
            cls._api = OfferApi()
        return cls._api

    @classmethod
    def mcp(cls) -> OfferMcp:
        if cls._mcp is None:
            cls._mcp = OfferMcp()
        return cls._mcp
