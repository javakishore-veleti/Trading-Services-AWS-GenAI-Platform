from workflows.interfaces import CreateOrderWf, GetOrderWf, ListOrdersWf, WfTask


class WorkflowObjectFactory:
    _list_orders: ListOrdersWf | None = None
    _get_order: GetOrderWf | None = None
    _create_order: CreateOrderWf | None = None
    _read_orders_task: WfTask | None = None
    _validate_get_order_task: WfTask | None = None
    _read_order_task: WfTask | None = None
    _validate_create_order_task: WfTask | None = None
    _insert_order_task: WfTask | None = None

    @classmethod
    def list_orders(cls) -> ListOrdersWf:
        if cls._list_orders is None:
            from workflows.impl.listorderswf import ListOrdersWfImpl

            cls._list_orders = ListOrdersWfImpl()
        return cls._list_orders

    @classmethod
    def get_order(cls) -> GetOrderWf:
        if cls._get_order is None:
            from workflows.impl.getorderwf import GetOrderWfImpl

            cls._get_order = GetOrderWfImpl()
        return cls._get_order

    @classmethod
    def create_order(cls) -> CreateOrderWf:
        if cls._create_order is None:
            from workflows.impl.createorderwf import CreateOrderWfImpl

            cls._create_order = CreateOrderWfImpl()
        return cls._create_order

    @classmethod
    def read_orders_task(cls) -> WfTask:
        if cls._read_orders_task is None:
            from workflows.impl.listorderswf import ReadOrdersTask

            cls._read_orders_task = ReadOrdersTask()
        return cls._read_orders_task

    @classmethod
    def validate_get_order_task(cls) -> WfTask:
        if cls._validate_get_order_task is None:
            from workflows.impl.getorderwf import ValidateGetOrderTask

            cls._validate_get_order_task = ValidateGetOrderTask()
        return cls._validate_get_order_task

    @classmethod
    def read_order_task(cls) -> WfTask:
        if cls._read_order_task is None:
            from workflows.impl.getorderwf import ReadOrderTask

            cls._read_order_task = ReadOrderTask()
        return cls._read_order_task

    @classmethod
    def validate_create_order_task(cls) -> WfTask:
        if cls._validate_create_order_task is None:
            from workflows.impl.createorderwf import ValidateCreateOrderTask

            cls._validate_create_order_task = ValidateCreateOrderTask()
        return cls._validate_create_order_task

    @classmethod
    def insert_order_task(cls) -> WfTask:
        if cls._insert_order_task is None:
            from workflows.impl.createorderwf import InsertOrderTask

            cls._insert_order_task = InsertOrderTask()
        return cls._insert_order_task
