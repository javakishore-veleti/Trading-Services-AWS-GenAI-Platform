from fastmcp import FastMCP

from common.dtos.req_resp_dtos import (
    ListCustomersRequest,
    ListCustomersResponse,
    ListRatingsRequest,
    ListRatingsResponse,
    PriceOfferRequest,
    PriceOfferResponse,
)
from workflows.interfaces import ListCustomersWf, ListRatingsWf, QuoteOfferWf
from workflows.object_factory import WorkflowObjectFactory


class OfferMcp:
    def __init__(self) -> None:
        self.server = FastMCP("trades-offers-mcp")
        self.server.tool(self.list_customer_ratings)
        self.server.tool(self.list_rating_discounts)
        self.server.tool(self.quote_fx_offer)

    def list_customer_ratings(self, request: ListCustomersRequest) -> ListCustomersResponse:
        """List customers and the rating that drives their FX discount."""
        workflow: ListCustomersWf = WorkflowObjectFactory.list_customers()
        return workflow.invoke(request)

    def list_rating_discounts(self, request: ListRatingsRequest) -> ListRatingsResponse:
        """Return the discount in basis points for each customer rating."""
        workflow: ListRatingsWf = WorkflowObjectFactory.list_ratings()
        return workflow.invoke(request)

    def quote_fx_offer(self, request: PriceOfferRequest) -> PriceOfferResponse:
        """Price an FX offer. side is buy or sell of the base currency."""
        workflow: QuoteOfferWf = WorkflowObjectFactory.quote_offer()
        return workflow.invoke(request)
