from common.dtos.req_resp_dtos import ListRatingsContext, ListRatingsRequest, ListRatingsResponse
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ListRatingsWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ReadRatingsTask(WfTask):
    def execute(self, context: ListRatingsContext) -> ListRatingsContext:
        response = ServiceObjectFactory.offer_svc().list_ratings(context.request)
        context.response = response
        context.error = response.error
        return context


class ListRatingsWfImpl(ListRatingsWf):
    def invoke(self, request: ListRatingsRequest) -> ListRatingsResponse:
        context = ListRatingsContext(request=request)
        context = WorkflowObjectFactory.read_ratings_task().execute(context)
        return context.response
