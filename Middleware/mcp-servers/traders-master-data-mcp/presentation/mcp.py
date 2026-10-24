from fastmcp import FastMCP

from common.dtos.req_resp_dtos import (
    BookChannelsResponse,
    BookDefaultsResponse,
    BooksResponse,
    ChannelsResponse,
    CountriesResponse,
    DesksResponse,
    EmptyRequest,
    InstallationsResponse,
    ListCountriesRequest,
    ListInstallationsRequest,
    ListTradersRequest,
    TradersResponse,
)
from workflows.interfaces import (
    ListBookChannelsWf,
    ListBookDefaultsWf,
    ListBooksWf,
    ListChannelsWf,
    ListCountriesWf,
    ListDesksWf,
    ListInstallationsWf,
    ListTradersWf,
)
from workflows.object_factory import WorkflowObjectFactory


class MasterDataMcp:
    def __init__(self) -> None:
        self.server = FastMCP("traders-master-data-mcp")
        self.server.tool(self.list_omni_channels)
        self.server.tool(self.list_desk_countries)
        self.server.tool(self.list_trading_desks)
        self.server.tool(self.list_desk_installations)
        self.server.tool(self.list_trading_books)
        self.server.tool(self.list_book_defaults)
        self.server.tool(self.list_book_channels)
        self.server.tool(self.list_traders)

    def list_omni_channels(self, request: EmptyRequest) -> ChannelsResponse:
        """Omni channels a trading book or desk installation can offer."""
        workflow: ListChannelsWf = WorkflowObjectFactory.list_channels()
        return workflow.invoke(request)

    def list_desk_countries(self, request: ListCountriesRequest) -> CountriesResponse:
        """Countries and US regions where a trading desk can be installed."""
        workflow: ListCountriesWf = WorkflowObjectFactory.list_countries()
        return workflow.invoke(request)

    def list_trading_desks(self, request: EmptyRequest) -> DesksResponse:
        """List trading desks."""
        workflow: ListDesksWf = WorkflowObjectFactory.list_desks()
        return workflow.invoke(request)

    def list_desk_installations(self, request: ListInstallationsRequest) -> InstallationsResponse:
        """Each row is one desk installed in one location, with the channels at that site."""
        workflow: ListInstallationsWf = WorkflowObjectFactory.list_installations()
        return workflow.invoke(request)

    def list_trading_books(self, request: EmptyRequest) -> BooksResponse:
        """List trading books."""
        workflow: ListBooksWf = WorkflowObjectFactory.list_books()
        return workflow.invoke(request)

    def list_book_defaults(self, request: EmptyRequest) -> BookDefaultsResponse:
        """Default channel, tenor, notional, and pair for each trading book."""
        workflow: ListBookDefaultsWf = WorkflowObjectFactory.list_book_defaults()
        return workflow.invoke(request)

    def list_book_channels(self, request: EmptyRequest) -> BookChannelsResponse:
        """Omni channels enabled on each trading book."""
        workflow: ListBookChannelsWf = WorkflowObjectFactory.list_book_channels()
        return workflow.invoke(request)

    def list_traders(self, request: ListTradersRequest) -> TradersResponse:
        """List traders. Optionally filter by desk_id."""
        workflow: ListTradersWf = WorkflowObjectFactory.list_traders()
        return workflow.invoke(request)
