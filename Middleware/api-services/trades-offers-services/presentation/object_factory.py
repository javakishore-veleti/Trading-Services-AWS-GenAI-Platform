from presentation.api import OffersApi


class PresentationObjectFactory:
    _api: OffersApi | None = None

    @classmethod
    def api(cls) -> OffersApi:
        if cls._api is None:
            cls._api = OffersApi()
        return cls._api
