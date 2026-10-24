from fastmcp import FastMCP

from common.dtos.req_resp_dtos import (
    CreateOrderRequest,
    CreateOrderResponse,
    GetOrderRequest,
    GetOrderResponse,
    ListOrdersRequest,
    ListOrdersResponse,
)
from workflows.interfaces import CreateOrderWf, GetOrderWf, ListOrdersWf
from workflows.object_factory import WorkflowObjectFactory


class OrderMcp:
    def __init__(self) -> None:
        self.server = FastMCP("trades-orders-mcp")
        self.server.tool(self.list_fx_orders)
        self.server.tool(self.get_fx_order)
        self.server.tool(self.create_fx_order)

    def list_fx_orders(self, request: ListOrdersRequest) -> ListOrdersResponse:
        """List FX orders. Filter by customer_id or status."""
        workflow: ListOrdersWf = WorkflowObjectFactory.list_orders()
        return workflow.invoke(request)

    def get_fx_order(self, request: GetOrderRequest) -> GetOrderResponse:
        """Return one FX order by id, such as ORD-1001."""
        workflow: GetOrderWf = WorkflowObjectFactory.get_order()
        return workflow.invoke(request)

    def create_fx_order(self, request: CreateOrderRequest) -> CreateOrderResponse:
        """Create a working FX order."""
        workflow: CreateOrderWf = WorkflowObjectFactory.create_order()
        return workflow.invoke(request)
