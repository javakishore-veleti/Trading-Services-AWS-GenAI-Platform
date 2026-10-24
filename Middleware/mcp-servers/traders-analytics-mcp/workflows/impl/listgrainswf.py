from common.dtos.req_resp_dtos import ListGrainsContext, ListGrainsRequest, ListGrainsResponse
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ListGrainsWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ReadGrainsTask(WfTask):
    def execute(self, context: ListGrainsContext) -> ListGrainsContext:
        response = ServiceObjectFactory.analytics_svc().list_grains(context.request)
        context.response = response
        context.error = response.error
        return context


class ListGrainsWfImpl(ListGrainsWf):
    def invoke(self, request: ListGrainsRequest) -> ListGrainsResponse:
        context = ListGrainsContext(request=request)
        context = WorkflowObjectFactory.read_grains_task().execute(context)
        return context.response
