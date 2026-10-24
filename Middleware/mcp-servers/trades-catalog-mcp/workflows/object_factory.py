from workflows.interfaces import GetProductWf, ListProductsWf, WfTask


class WorkflowObjectFactory:
    _list_products: ListProductsWf | None = None
    _get_product: GetProductWf | None = None
    _read_products_task: WfTask | None = None
    _validate_get_product_task: WfTask | None = None
    _read_product_task: WfTask | None = None

    @classmethod
    def list_products(cls) -> ListProductsWf:
        if cls._list_products is None:
            from workflows.impl.listproductswf import ListProductsWfImpl

            cls._list_products = ListProductsWfImpl()
        return cls._list_products

    @classmethod
    def get_product(cls) -> GetProductWf:
        if cls._get_product is None:
            from workflows.impl.getproductwf import GetProductWfImpl

            cls._get_product = GetProductWfImpl()
        return cls._get_product

    @classmethod
    def read_products_task(cls) -> WfTask:
        if cls._read_products_task is None:
            from workflows.impl.listproductswf import ReadProductsTask

            cls._read_products_task = ReadProductsTask()
        return cls._read_products_task

    @classmethod
    def validate_get_product_task(cls) -> WfTask:
        if cls._validate_get_product_task is None:
            from workflows.impl.getproductwf import ValidateGetProductTask

            cls._validate_get_product_task = ValidateGetProductTask()
        return cls._validate_get_product_task

    @classmethod
    def read_product_task(cls) -> WfTask:
        if cls._read_product_task is None:
            from workflows.impl.getproductwf import ReadProductTask

            cls._read_product_task = ReadProductTask()
        return cls._read_product_task
