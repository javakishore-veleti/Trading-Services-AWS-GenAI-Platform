from workflows.interfaces import ListCustomersWf, ListRatingsWf, QuoteOfferWf, WfTask


class WorkflowObjectFactory:
    _list_customers: ListCustomersWf | None = None
    _list_ratings: ListRatingsWf | None = None
    _quote_offer: QuoteOfferWf | None = None
    _read_customers_task: WfTask | None = None
    _read_ratings_task: WfTask | None = None
    _validate_quote_task: WfTask | None = None
    _load_quote_task: WfTask | None = None
    _price_quote_task: WfTask | None = None

    @classmethod
    def list_customers(cls) -> ListCustomersWf:
        if cls._list_customers is None:
            from workflows.impl.listcustomerswf import ListCustomersWfImpl

            cls._list_customers = ListCustomersWfImpl()
        return cls._list_customers

    @classmethod
    def list_ratings(cls) -> ListRatingsWf:
        if cls._list_ratings is None:
            from workflows.impl.listratingswf import ListRatingsWfImpl

            cls._list_ratings = ListRatingsWfImpl()
        return cls._list_ratings

    @classmethod
    def quote_offer(cls) -> QuoteOfferWf:
        if cls._quote_offer is None:
            from workflows.impl.quoteofferwf import QuoteOfferWfImpl

            cls._quote_offer = QuoteOfferWfImpl()
        return cls._quote_offer

    @classmethod
    def read_customers_task(cls) -> WfTask:
        if cls._read_customers_task is None:
            from workflows.impl.listcustomerswf import ReadCustomersTask

            cls._read_customers_task = ReadCustomersTask()
        return cls._read_customers_task

    @classmethod
    def read_ratings_task(cls) -> WfTask:
        if cls._read_ratings_task is None:
            from workflows.impl.listratingswf import ReadRatingsTask

            cls._read_ratings_task = ReadRatingsTask()
        return cls._read_ratings_task

    @classmethod
    def validate_quote_task(cls) -> WfTask:
        if cls._validate_quote_task is None:
            from workflows.impl.quoteofferwf import ValidateQuoteTask

            cls._validate_quote_task = ValidateQuoteTask()
        return cls._validate_quote_task

    @classmethod
    def load_quote_task(cls) -> WfTask:
        if cls._load_quote_task is None:
            from workflows.impl.quoteofferwf import LoadQuoteTask

            cls._load_quote_task = LoadQuoteTask()
        return cls._load_quote_task

    @classmethod
    def price_quote_task(cls) -> WfTask:
        if cls._price_quote_task is None:
            from workflows.impl.quoteofferwf import PriceQuoteTask

            cls._price_quote_task = PriceQuoteTask()
        return cls._price_quote_task
