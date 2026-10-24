from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import (
    BookChannelRowsDto,
    BookDefaultRowsDto,
    BookRowsDto,
    ChannelRowsDto,
    CountryRowsDto,
    DeskRowsDto,
    EmptyRequest,
    InstallationRowsDto,
    ListCountriesRequest,
    ListInstallationsRequest,
    ListTradersRequest,
    TraderRowsDto,
)


class MasterDataDao(ABC):
    @abstractmethod
    def find_channels(self, request: EmptyRequest) -> ChannelRowsDto:
        raise NotImplementedError

    @abstractmethod
    def find_countries(self, request: ListCountriesRequest) -> CountryRowsDto:
        raise NotImplementedError

    @abstractmethod
    def find_desks(self, request: EmptyRequest) -> DeskRowsDto:
        raise NotImplementedError

    @abstractmethod
    def find_installations(self, request: ListInstallationsRequest) -> InstallationRowsDto:
        raise NotImplementedError

    @abstractmethod
    def find_books(self, request: EmptyRequest) -> BookRowsDto:
        raise NotImplementedError

    @abstractmethod
    def find_book_defaults(self, request: EmptyRequest) -> BookDefaultRowsDto:
        raise NotImplementedError

    @abstractmethod
    def find_book_channels(self, request: EmptyRequest) -> BookChannelRowsDto:
        raise NotImplementedError

    @abstractmethod
    def find_traders(self, request: ListTradersRequest) -> TraderRowsDto:
        raise NotImplementedError
