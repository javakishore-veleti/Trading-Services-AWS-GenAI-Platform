from fastmcp import FastMCP

from common.dtos.req_resp_dtos import GetProductRequest, GetProductResponse, ListProductsRequest, ListProductsResponse
from workflows.interfaces import GetProductWf, ListProductsWf
from workflows.object_factory import WorkflowObjectFactory


class CatalogMcp:
    def __init__(self) -> None:
        self.server = FastMCP("trades-catalog-mcp")
        self.server.tool(self.list_fx_products)
        self.server.tool(self.get_fx_product)

    def list_fx_products(self, request: ListProductsRequest) -> ListProductsResponse:
        """List FX products a customer can trade. Filter by product type or customer segment."""
        workflow: ListProductsWf = WorkflowObjectFactory.list_products()
        return workflow.invoke(request)

    def get_fx_product(self, request: GetProductRequest) -> GetProductResponse:
        """Return one FX catalog product by id, such as SPOT-EURUSD."""
        workflow: GetProductWf = WorkflowObjectFactory.get_product()
        return workflow.invoke(request)
