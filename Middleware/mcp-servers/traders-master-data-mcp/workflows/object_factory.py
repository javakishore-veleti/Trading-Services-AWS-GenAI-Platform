from workflows.interfaces import (
    ListBookChannelsWf,
    ListBookDefaultsWf,
    ListBooksWf,
    ListChannelsWf,
    ListCountriesWf,
    ListDesksWf,
    ListInstallationsWf,
    ListTradersWf,
    WfTask,
)


class WorkflowObjectFactory:
    _list_channels: ListChannelsWf | None = None
    _list_countries: ListCountriesWf | None = None
    _list_desks: ListDesksWf | None = None
    _list_installations: ListInstallationsWf | None = None
    _list_books: ListBooksWf | None = None
    _list_book_defaults: ListBookDefaultsWf | None = None
    _list_book_channels: ListBookChannelsWf | None = None
    _list_traders: ListTradersWf | None = None
    _read_channels_task: WfTask | None = None
    _resolve_region_task: WfTask | None = None
    _read_countries_task: WfTask | None = None
    _read_desks_task: WfTask | None = None
    _read_installations_task: WfTask | None = None
    _read_books_task: WfTask | None = None
    _read_book_defaults_task: WfTask | None = None
    _read_book_channels_task: WfTask | None = None
    _read_traders_task: WfTask | None = None

    @classmethod
    def list_channels(cls) -> ListChannelsWf:
        if cls._list_channels is None:
            from workflows.impl.listchannelswf import ListChannelsWfImpl

            cls._list_channels = ListChannelsWfImpl()
        return cls._list_channels

    @classmethod
    def list_countries(cls) -> ListCountriesWf:
        if cls._list_countries is None:
            from workflows.impl.listcountrieswf import ListCountriesWfImpl

            cls._list_countries = ListCountriesWfImpl()
        return cls._list_countries

    @classmethod
    def list_desks(cls) -> ListDesksWf:
        if cls._list_desks is None:
            from workflows.impl.listdeskswf import ListDesksWfImpl

            cls._list_desks = ListDesksWfImpl()
        return cls._list_desks

    @classmethod
    def list_installations(cls) -> ListInstallationsWf:
        if cls._list_installations is None:
            from workflows.impl.listinstallationswf import ListInstallationsWfImpl

            cls._list_installations = ListInstallationsWfImpl()
        return cls._list_installations

    @classmethod
    def list_books(cls) -> ListBooksWf:
        if cls._list_books is None:
            from workflows.impl.listbookswf import ListBooksWfImpl

            cls._list_books = ListBooksWfImpl()
        return cls._list_books

    @classmethod
    def list_book_defaults(cls) -> ListBookDefaultsWf:
        if cls._list_book_defaults is None:
            from workflows.impl.listbookdefaultswf import ListBookDefaultsWfImpl

            cls._list_book_defaults = ListBookDefaultsWfImpl()
        return cls._list_book_defaults

    @classmethod
    def list_book_channels(cls) -> ListBookChannelsWf:
        if cls._list_book_channels is None:
            from workflows.impl.listbookchannelswf import ListBookChannelsWfImpl

            cls._list_book_channels = ListBookChannelsWfImpl()
        return cls._list_book_channels

    @classmethod
    def list_traders(cls) -> ListTradersWf:
        if cls._list_traders is None:
            from workflows.impl.listtraderswf import ListTradersWfImpl

            cls._list_traders = ListTradersWfImpl()
        return cls._list_traders

    @classmethod
    def read_channels_task(cls) -> WfTask:
        if cls._read_channels_task is None:
            from workflows.impl.listchannelswf import ReadChannelsTask

            cls._read_channels_task = ReadChannelsTask()
        return cls._read_channels_task

    @classmethod
    def resolve_region_task(cls) -> WfTask:
        if cls._resolve_region_task is None:
            from workflows.impl.listcountrieswf import ResolveRegionTask

            cls._resolve_region_task = ResolveRegionTask()
        return cls._resolve_region_task

    @classmethod
    def read_countries_task(cls) -> WfTask:
        if cls._read_countries_task is None:
            from workflows.impl.listcountrieswf import ReadCountriesTask

            cls._read_countries_task = ReadCountriesTask()
        return cls._read_countries_task

    @classmethod
    def read_desks_task(cls) -> WfTask:
        if cls._read_desks_task is None:
            from workflows.impl.listdeskswf import ReadDesksTask

            cls._read_desks_task = ReadDesksTask()
        return cls._read_desks_task

    @classmethod
    def read_installations_task(cls) -> WfTask:
        if cls._read_installations_task is None:
            from workflows.impl.listinstallationswf import ReadInstallationsTask

            cls._read_installations_task = ReadInstallationsTask()
        return cls._read_installations_task

    @classmethod
    def read_books_task(cls) -> WfTask:
        if cls._read_books_task is None:
            from workflows.impl.listbookswf import ReadBooksTask

            cls._read_books_task = ReadBooksTask()
        return cls._read_books_task

    @classmethod
    def read_book_defaults_task(cls) -> WfTask:
        if cls._read_book_defaults_task is None:
            from workflows.impl.listbookdefaultswf import ReadBookDefaultsTask

            cls._read_book_defaults_task = ReadBookDefaultsTask()
        return cls._read_book_defaults_task

    @classmethod
    def read_book_channels_task(cls) -> WfTask:
        if cls._read_book_channels_task is None:
            from workflows.impl.listbookchannelswf import ReadBookChannelsTask

            cls._read_book_channels_task = ReadBookChannelsTask()
        return cls._read_book_channels_task

    @classmethod
    def read_traders_task(cls) -> WfTask:
        if cls._read_traders_task is None:
            from workflows.impl.listtraderswf import ReadTradersTask

            cls._read_traders_task = ReadTradersTask()
        return cls._read_traders_task
