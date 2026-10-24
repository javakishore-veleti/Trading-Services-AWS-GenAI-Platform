from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from common.dtos.req_resp_dtos import ErrorDto, GetPartnerRequest, GetPartnerResponse, ListPartnersRequest, ListPartnersResponse
from workflows.interfaces import GetPartnerWf, ListPartnersWf
from workflows.object_factory import WorkflowObjectFactory


class PartnerApi:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/partners", self.list_partners, methods=["GET"], response_model=ListPartnersResponse)
        self.router.add_api_route("/partners/{partner_id}", self.get_partner, methods=["GET"], response_model=GetPartnerResponse)

    def list_partners(self, request: Annotated[ListPartnersRequest, Depends()]) -> ListPartnersResponse:
        workflow: ListPartnersWf = WorkflowObjectFactory.list_partners()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def get_partner(self, partner_id: str) -> GetPartnerResponse:
        workflow: GetPartnerWf = WorkflowObjectFactory.get_partner()
        response = workflow.invoke(GetPartnerRequest(partner_id=partner_id))
        self._raise_for_error(response.error)
        return response

    def _raise_for_error(self, error: ErrorDto | None) -> None:
        if error is None:
            return
        status = 404 if error.code == "not_found" else 400
        raise HTTPException(status_code=status, detail=error.message)
