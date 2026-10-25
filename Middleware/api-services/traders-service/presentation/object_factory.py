from presentation.api import TradersApi


class PresentationObjectFactory:
    _api: TradersApi | None = None

    @classmethod
    def api(cls) -> TradersApi:
        if cls._api is None:
            cls._api = TradersApi()
        return cls._api
