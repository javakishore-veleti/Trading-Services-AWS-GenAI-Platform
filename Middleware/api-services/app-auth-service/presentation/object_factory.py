from presentation.api import AuthApi


class PresentationObjectFactory:
    _api: AuthApi | None = None

    @classmethod
    def api(cls) -> AuthApi:
        if cls._api is None:
            cls._api = AuthApi()
        return cls._api
