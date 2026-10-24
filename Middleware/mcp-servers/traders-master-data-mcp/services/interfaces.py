from abc import ABC, abstractmethod

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


class MasterDataSvc(ABC):
    @abstractmethod
    def list_channels(self, request: EmptyRequest) -> ChannelsResponse:
        raise NotImplementedError

    @abstractmethod
    def list_countries(self, request: ListCountriesRequest) -> CountriesResponse:
        raise NotImplementedError

    @abstractmethod
    def list_desks(self, request: EmptyRequest) -> DesksResponse:
        raise NotImplementedError

    @abstractmethod
    def list_installations(self, request: ListInstallationsRequest) -> InstallationsResponse:
        raise NotImplementedError

    @abstractmethod
    def list_books(self, request: EmptyRequest) -> BooksResponse:
        raise NotImplementedError

    @abstractmethod
    def list_book_defaults(self, request: EmptyRequest) -> BookDefaultsResponse:
        raise NotImplementedError

    @abstractmethod
    def list_book_channels(self, request: EmptyRequest) -> BookChannelsResponse:
        raise NotImplementedError

    @abstractmethod
    def list_traders(self, request: ListTradersRequest) -> TradersResponse:
        raise NotImplementedError
