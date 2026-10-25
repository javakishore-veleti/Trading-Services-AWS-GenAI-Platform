from services.interfaces import CustomerService


class ServiceObjectFactory:
    _service: CustomerService | None = None

    @classmethod
    def customer_service(cls) -> CustomerService:
        if cls._service is None:
            from dao.object_factory import DaoObjectFactory
            from services.impl.customersvc import CustomerServiceImpl

            cls._service = CustomerServiceImpl(DaoObjectFactory.customer_dao())
        return cls._service
