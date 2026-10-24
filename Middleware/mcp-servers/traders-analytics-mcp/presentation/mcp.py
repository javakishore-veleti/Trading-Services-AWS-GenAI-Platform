from fastmcp import FastMCP

from common.dtos.req_resp_dtos import ListGrainsRequest, ListGrainsResponse, ReadAnalyticsRequest, ReadAnalyticsResponse
from workflows.interfaces import ListGrainsWf, ReadAnalyticsWf
from workflows.object_factory import WorkflowObjectFactory


class AnalyticsMcp:
    def __init__(self) -> None:
        self.server = FastMCP("traders-analytics-mcp")
        self.server.tool(self.list_analytics_grains)
        self.server.tool(self.read_fx_analytics)

    def list_analytics_grains(self, request: ListGrainsRequest) -> ListGrainsResponse:
        """Warehouse grains available to read: end of day, intraday, and hourly."""
        workflow: ListGrainsWf = WorkflowObjectFactory.list_grains()
        return workflow.invoke(request)

    def read_fx_analytics(self, request: ReadAnalyticsRequest) -> ReadAnalyticsResponse:
        """Read warehouse analytics. This tool does not create or change figures."""
        workflow: ReadAnalyticsWf = WorkflowObjectFactory.read_analytics()
        return workflow.invoke(request)
