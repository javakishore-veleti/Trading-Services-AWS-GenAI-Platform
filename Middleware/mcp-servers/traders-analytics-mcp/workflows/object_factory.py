from workflows.interfaces import ListGrainsWf, ReadAnalyticsWf, WfTask


class WorkflowObjectFactory:
    _list_grains: ListGrainsWf | None = None
    _read_analytics: ReadAnalyticsWf | None = None
    _read_grains_task: WfTask | None = None
    _validate_read_task: WfTask | None = None
    _read_rows_task: WfTask | None = None

    @classmethod
    def list_grains(cls) -> ListGrainsWf:
        if cls._list_grains is None:
            from workflows.impl.listgrainswf import ListGrainsWfImpl

            cls._list_grains = ListGrainsWfImpl()
        return cls._list_grains

    @classmethod
    def read_analytics(cls) -> ReadAnalyticsWf:
        if cls._read_analytics is None:
            from workflows.impl.readanalyticswf import ReadAnalyticsWfImpl

            cls._read_analytics = ReadAnalyticsWfImpl()
        return cls._read_analytics

    @classmethod
    def read_grains_task(cls) -> WfTask:
        if cls._read_grains_task is None:
            from workflows.impl.listgrainswf import ReadGrainsTask

            cls._read_grains_task = ReadGrainsTask()
        return cls._read_grains_task

    @classmethod
    def validate_read_task(cls) -> WfTask:
        if cls._validate_read_task is None:
            from workflows.impl.readanalyticswf import ValidateReadTask

            cls._validate_read_task = ValidateReadTask()
        return cls._validate_read_task

    @classmethod
    def read_rows_task(cls) -> WfTask:
        if cls._read_rows_task is None:
            from workflows.impl.readanalyticswf import ReadRowsTask

            cls._read_rows_task = ReadRowsTask()
        return cls._read_rows_task
