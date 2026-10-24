from presentation.api import PartnerApi
from presentation.mcp import PartnerMcp


class PresentationObjectFactory:
    _api: PartnerApi | None = None
    _mcp: PartnerMcp | None = None

    @classmethod
    def api(cls) -> PartnerApi:
        if cls._api is None:
            cls._api = PartnerApi()
        return cls._api

    @classmethod
    def mcp(cls) -> PartnerMcp:
        if cls._mcp is None:
            cls._mcp = PartnerMcp()
        return cls._mcp
