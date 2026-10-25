from services.interfaces import AuthService


class ServiceObjectFactory:
    _service: AuthService | None = None

    @classmethod
    def auth_service(cls) -> AuthService:
        if cls._service is None:
            from dao.object_factory import DaoObjectFactory
            from services.impl.authsvc import AuthServiceImpl

            cls._service = AuthServiceImpl(DaoObjectFactory.auth_dao())
        return cls._service
