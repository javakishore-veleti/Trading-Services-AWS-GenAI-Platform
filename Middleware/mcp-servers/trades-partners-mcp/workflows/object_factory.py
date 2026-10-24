from workflows.interfaces import GetPartnerWf, ListPartnersWf, WfTask


class WorkflowObjectFactory:
    _list_partners: ListPartnersWf | None = None
    _get_partner: GetPartnerWf | None = None
    _read_partners_task: WfTask | None = None
    _validate_get_partner_task: WfTask | None = None
    _read_partner_task: WfTask | None = None

    @classmethod
    def list_partners(cls) -> ListPartnersWf:
        if cls._list_partners is None:
            from workflows.impl.listpartnerswf import ListPartnersWfImpl

            cls._list_partners = ListPartnersWfImpl()
        return cls._list_partners

    @classmethod
    def get_partner(cls) -> GetPartnerWf:
        if cls._get_partner is None:
            from workflows.impl.getpartnerwf import GetPartnerWfImpl

            cls._get_partner = GetPartnerWfImpl()
        return cls._get_partner

    @classmethod
    def read_partners_task(cls) -> WfTask:
        if cls._read_partners_task is None:
            from workflows.impl.listpartnerswf import ReadPartnersTask

            cls._read_partners_task = ReadPartnersTask()
        return cls._read_partners_task

    @classmethod
    def validate_get_partner_task(cls) -> WfTask:
        if cls._validate_get_partner_task is None:
            from workflows.impl.getpartnerwf import ValidateGetPartnerTask

            cls._validate_get_partner_task = ValidateGetPartnerTask()
        return cls._validate_get_partner_task

    @classmethod
    def read_partner_task(cls) -> WfTask:
        if cls._read_partner_task is None:
            from workflows.impl.getpartnerwf import ReadPartnerTask

            cls._read_partner_task = ReadPartnerTask()
        return cls._read_partner_task
