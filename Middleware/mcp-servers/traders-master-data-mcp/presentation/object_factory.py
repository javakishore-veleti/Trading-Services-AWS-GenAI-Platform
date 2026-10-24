from presentation.api import MasterDataApi
from presentation.mcp import MasterDataMcp


class PresentationObjectFactory:
    _api: MasterDataApi | None = None
    _mcp: MasterDataMcp | None = None

    @classmethod
    def api(cls) -> MasterDataApi:
        if cls._api is None:
            cls._api = MasterDataApi()
        return cls._api

    @classmethod
    def mcp(cls) -> MasterDataMcp:
        if cls._mcp is None:
            cls._mcp = MasterDataMcp()
        return cls._mcp
