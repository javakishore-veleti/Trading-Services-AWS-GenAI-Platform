from presentation.api import LangGraphApi


class PresentationObjectFactory:
    _api: LangGraphApi | None = None

    @classmethod
    def api(cls) -> LangGraphApi:
        if cls._api is None:
            cls._api = LangGraphApi()
        return cls._api
