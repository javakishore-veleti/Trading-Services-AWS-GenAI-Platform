from services.interfaces import MasterDataSvc


class ServiceObjectFactory:
    _svc: MasterDataSvc | None = None

    @classmethod
    def master_data_svc(cls) -> MasterDataSvc:
        if cls._svc is None:
            from services.impl.masterdatasvc import MasterDataSvcImpl

            cls._svc = MasterDataSvcImpl()
        return cls._svc
