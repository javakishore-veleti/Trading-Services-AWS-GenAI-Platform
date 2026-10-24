from dao.interfaces import MasterDataDao


class DaoObjectFactory:
    _dao: MasterDataDao | None = None

    @classmethod
    def master_data_dao(cls) -> MasterDataDao:
        if cls._dao is None:
            from dao.impl.masterdatadao import MasterDataDaoImpl

            cls._dao = MasterDataDaoImpl()
        return cls._dao
