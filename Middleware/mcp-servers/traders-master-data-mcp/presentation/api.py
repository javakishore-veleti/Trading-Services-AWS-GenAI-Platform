from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from common.dtos.req_resp_dtos import (
    BookChannelsResponse,
    BookDefaultsResponse,
    BooksResponse,
    ChannelsResponse,
    CountriesResponse,
    DesksResponse,
    EmptyRequest,
    ErrorDto,
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


class MasterDataApi:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/channels", self.list_channels, methods=["GET"], response_model=ChannelsResponse)
        self.router.add_api_route("/countries", self.list_countries, methods=["GET"], response_model=CountriesResponse)
        self.router.add_api_route("/desks", self.list_desks, methods=["GET"], response_model=DesksResponse)
        self.router.add_api_route("/installations", self.list_installations, methods=["GET"], response_model=InstallationsResponse)
        self.router.add_api_route("/books", self.list_books, methods=["GET"], response_model=BooksResponse)
        self.router.add_api_route("/book-defaults", self.list_book_defaults, methods=["GET"], response_model=BookDefaultsResponse)
        self.router.add_api_route("/book-channels", self.list_book_channels, methods=["GET"], response_model=BookChannelsResponse)
        self.router.add_api_route("/traders", self.list_traders, methods=["GET"], response_model=TradersResponse)

    def list_channels(self, request: Annotated[EmptyRequest, Depends()]) -> ChannelsResponse:
        workflow: ListChannelsWf = WorkflowObjectFactory.list_channels()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def list_countries(self, request: Annotated[ListCountriesRequest, Depends()]) -> CountriesResponse:
        workflow: ListCountriesWf = WorkflowObjectFactory.list_countries()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def list_desks(self, request: Annotated[EmptyRequest, Depends()]) -> DesksResponse:
        workflow: ListDesksWf = WorkflowObjectFactory.list_desks()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def list_installations(self, request: Annotated[ListInstallationsRequest, Depends()]) -> InstallationsResponse:
        workflow: ListInstallationsWf = WorkflowObjectFactory.list_installations()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def list_books(self, request: Annotated[EmptyRequest, Depends()]) -> BooksResponse:
        workflow: ListBooksWf = WorkflowObjectFactory.list_books()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def list_book_defaults(self, request: Annotated[EmptyRequest, Depends()]) -> BookDefaultsResponse:
        workflow: ListBookDefaultsWf = WorkflowObjectFactory.list_book_defaults()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def list_book_channels(self, request: Annotated[EmptyRequest, Depends()]) -> BookChannelsResponse:
        workflow: ListBookChannelsWf = WorkflowObjectFactory.list_book_channels()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def list_traders(self, request: Annotated[ListTradersRequest, Depends()]) -> TradersResponse:
        workflow: ListTradersWf = WorkflowObjectFactory.list_traders()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def _raise_for_error(self, error: ErrorDto | None) -> None:
        if error is None:
            return
        status = 404 if error.code == "not_found" else 400
        raise HTTPException(status_code=status, detail=error.message)
