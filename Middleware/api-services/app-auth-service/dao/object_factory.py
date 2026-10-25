from dao.interfaces import AuthDao


class DaoObjectFactory:
    _dao: AuthDao | None = None

    @classmethod
    def auth_dao(cls) -> AuthDao:
        if cls._dao is None:
            from dao.impl.store import AuthDaoImpl

            cls._dao = AuthDaoImpl()
        return cls._dao
