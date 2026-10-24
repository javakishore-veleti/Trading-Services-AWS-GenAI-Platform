from fastmcp import FastMCP

from common.dtos.req_resp_dtos import GetPartnerRequest, GetPartnerResponse, ListPartnersRequest, ListPartnersResponse
from workflows.interfaces import GetPartnerWf, ListPartnersWf
from workflows.object_factory import WorkflowObjectFactory


class PartnerMcp:
    def __init__(self) -> None:
        self.server = FastMCP("trades-partners-mcp")
        self.server.tool(self.list_fx_partners)
        self.server.tool(self.get_fx_partner)

    def list_fx_partners(self, request: ListPartnersRequest) -> ListPartnersResponse:
        """List banks on FX integrations. role is prime-broker, correspondent, or clearer."""
        workflow: ListPartnersWf = WorkflowObjectFactory.list_partners()
        return workflow.invoke(request)

    def get_fx_partner(self, request: GetPartnerRequest) -> GetPartnerResponse:
        """Return one partner bank by id, such as BNK-JPM."""
        workflow: GetPartnerWf = WorkflowObjectFactory.get_partner()
        return workflow.invoke(request)
