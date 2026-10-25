from dao.interfaces import CustomerDao


class DaoObjectFactory:
    _dao: CustomerDao | None = None

    @classmethod
    def customer_dao(cls) -> CustomerDao:
        if cls._dao is None:
            from dao.impl.store import CustomerDaoImpl

            cls._dao = CustomerDaoImpl()
        return cls._dao
