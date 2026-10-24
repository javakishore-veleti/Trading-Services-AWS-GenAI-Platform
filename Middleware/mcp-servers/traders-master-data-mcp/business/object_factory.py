from business.interfaces import MasterDataBiz


class BusinessObjectFactory:
    _biz: MasterDataBiz | None = None

    @classmethod
    def master_data_biz(cls) -> MasterDataBiz:
        if cls._biz is None:
            from business.impl.masterdatabiz import MasterDataBizImpl

            cls._biz = MasterDataBizImpl()
        return cls._biz
