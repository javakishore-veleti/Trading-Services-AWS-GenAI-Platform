from abc import ABC, abstractmethod

from pydantic import BaseModel

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


class WfTask(ABC):
    @abstractmethod
    def execute(self, context: BaseModel) -> BaseModel:
        raise NotImplementedError


class ListChannelsWf(ABC):
    @abstractmethod
    def invoke(self, request: EmptyRequest) -> ChannelsResponse:
        raise NotImplementedError


class ListCountriesWf(ABC):
    @abstractmethod
    def invoke(self, request: ListCountriesRequest) -> CountriesResponse:
        raise NotImplementedError


class ListDesksWf(ABC):
    @abstractmethod
    def invoke(self, request: EmptyRequest) -> DesksResponse:
        raise NotImplementedError


class ListInstallationsWf(ABC):
    @abstractmethod
    def invoke(self, request: ListInstallationsRequest) -> InstallationsResponse:
        raise NotImplementedError


class ListBooksWf(ABC):
    @abstractmethod
    def invoke(self, request: EmptyRequest) -> BooksResponse:
        raise NotImplementedError


class ListBookDefaultsWf(ABC):
    @abstractmethod
    def invoke(self, request: EmptyRequest) -> BookDefaultsResponse:
        raise NotImplementedError


class ListBookChannelsWf(ABC):
    @abstractmethod
    def invoke(self, request: EmptyRequest) -> BookChannelsResponse:
        raise NotImplementedError


class ListTradersWf(ABC):
    @abstractmethod
    def invoke(self, request: ListTradersRequest) -> TradersResponse:
        raise NotImplementedError
