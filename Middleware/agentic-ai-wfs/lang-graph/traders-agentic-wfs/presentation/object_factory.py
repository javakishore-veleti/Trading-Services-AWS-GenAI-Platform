from presentation.api import DeskApi


class PresentationObjectFactory:
    _api: DeskApi | None = None

    @classmethod
    def api(cls) -> DeskApi:
        if cls._api is None:
            cls._api = DeskApi()
        return cls._api
