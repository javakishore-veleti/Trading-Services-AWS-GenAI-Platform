from presentation.api import CatalogApi
from presentation.mcp import CatalogMcp


class PresentationObjectFactory:
    _api: CatalogApi | None = None
    _mcp: CatalogMcp | None = None

    @classmethod
    def api(cls) -> CatalogApi:
        if cls._api is None:
            cls._api = CatalogApi()
        return cls._api

    @classmethod
    def mcp(cls) -> CatalogMcp:
        if cls._mcp is None:
            cls._mcp = CatalogMcp()
        return cls._mcp
