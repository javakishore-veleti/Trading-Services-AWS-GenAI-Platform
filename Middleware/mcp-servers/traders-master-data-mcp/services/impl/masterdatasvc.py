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
from dao.object_factory import DaoObjectFactory
from services.interfaces import MasterDataSvc


class MasterDataSvcImpl(MasterDataSvc):
    def list_channels(self, request: EmptyRequest) -> ChannelsResponse:
        rows = DaoObjectFactory.master_data_dao().find_channels(request)
        return ChannelsResponse(channels=rows.channels)

    def list_countries(self, request: ListCountriesRequest) -> CountriesResponse:
        rows = DaoObjectFactory.master_data_dao().find_countries(request)
        return CountriesResponse(countries=rows.countries)

    def list_desks(self, request: EmptyRequest) -> DesksResponse:
        rows = DaoObjectFactory.master_data_dao().find_desks(request)
        return DesksResponse(desks=rows.desks)

    def list_installations(self, request: ListInstallationsRequest) -> InstallationsResponse:
        rows = DaoObjectFactory.master_data_dao().find_installations(request)
        return InstallationsResponse(installations=rows.installations)

    def list_books(self, request: EmptyRequest) -> BooksResponse:
        rows = DaoObjectFactory.master_data_dao().find_books(request)
        return BooksResponse(books=rows.books)

    def list_book_defaults(self, request: EmptyRequest) -> BookDefaultsResponse:
        rows = DaoObjectFactory.master_data_dao().find_book_defaults(request)
        return BookDefaultsResponse(defaults=rows.defaults)

    def list_book_channels(self, request: EmptyRequest) -> BookChannelsResponse:
        rows = DaoObjectFactory.master_data_dao().find_book_channels(request)
        return BookChannelsResponse(book_channels=rows.book_channels)

    def list_traders(self, request: ListTradersRequest) -> TradersResponse:
        rows = DaoObjectFactory.master_data_dao().find_traders(request)
        return TradersResponse(traders=rows.traders)
