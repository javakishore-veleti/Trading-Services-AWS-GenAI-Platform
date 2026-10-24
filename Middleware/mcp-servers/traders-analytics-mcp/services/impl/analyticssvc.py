from common.dtos.req_resp_dtos import ListGrainsRequest, ListGrainsResponse, ReadAnalyticsRequest, ReadAnalyticsResponse
from dao.object_factory import DaoObjectFactory
from services.interfaces import AnalyticsSvc


class AnalyticsSvcImpl(AnalyticsSvc):
    def list_grains(self, request: ListGrainsRequest) -> ListGrainsResponse:
        rows = DaoObjectFactory.analytics_dao().find_grains(request)
        return ListGrainsResponse(grains=rows.grains)

    def read_analytics(self, request: ReadAnalyticsRequest) -> ReadAnalyticsResponse:
        rows = DaoObjectFactory.analytics_dao().find_rows(request)
        return ReadAnalyticsResponse(rows=rows.rows)
