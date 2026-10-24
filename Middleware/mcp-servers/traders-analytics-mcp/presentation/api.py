from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from common.dtos.req_resp_dtos import ErrorDto, ListGrainsRequest, ListGrainsResponse, ReadAnalyticsRequest, ReadAnalyticsResponse
from workflows.interfaces import ListGrainsWf, ReadAnalyticsWf
from workflows.object_factory import WorkflowObjectFactory


class AnalyticsApi:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/grains", self.list_grains, methods=["GET"], response_model=ListGrainsResponse)
        self.router.add_api_route("/analytics", self.read_analytics, methods=["GET"], response_model=ReadAnalyticsResponse)

    def list_grains(self, request: Annotated[ListGrainsRequest, Depends()]) -> ListGrainsResponse:
        workflow: ListGrainsWf = WorkflowObjectFactory.list_grains()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def read_analytics(self, request: Annotated[ReadAnalyticsRequest, Depends()]) -> ReadAnalyticsResponse:
        workflow: ReadAnalyticsWf = WorkflowObjectFactory.read_analytics()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def _raise_for_error(self, error: ErrorDto | None) -> None:
        if error is None:
            return
        status = 404 if error.code == "not_found" else 400
        raise HTTPException(status_code=status, detail=error.message)
