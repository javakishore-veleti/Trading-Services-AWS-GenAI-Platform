from presentation.api import CustomerApi


class PresentationObjectFactory:
    _api: CustomerApi | None = None

    @classmethod
    def api(cls) -> CustomerApi:
        if cls._api is None:
            cls._api = CustomerApi()
        return cls._api
