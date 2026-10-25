from presentation.api import CatalogApi


class PresentationObjectFactory:
    _api: CatalogApi | None = None

    @classmethod
    def api(cls) -> CatalogApi:
        if cls._api is None:
            cls._api = CatalogApi()
        return cls._api
