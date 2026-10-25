from presentation.api import OrdersApi


class PresentationObjectFactory:
    _api: OrdersApi | None = None

    @classmethod
    def api(cls) -> OrdersApi:
        if cls._api is None:
            cls._api = OrdersApi()
        return cls._api
