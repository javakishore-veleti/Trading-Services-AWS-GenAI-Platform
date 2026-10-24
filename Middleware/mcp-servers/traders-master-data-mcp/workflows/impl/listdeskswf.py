from common.dtos.req_resp_dtos import DesksContext, DesksResponse, EmptyRequest
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ListDesksWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ReadDesksTask(WfTask):
    def execute(self, context: DesksContext) -> DesksContext:
        response = ServiceObjectFactory.master_data_svc().list_desks(context.request)
        context.response = response
        context.error = response.error
        return context


class ListDesksWfImpl(ListDesksWf):
    def invoke(self, request: EmptyRequest) -> DesksResponse:
        context = DesksContext(request=request)
        context = WorkflowObjectFactory.read_desks_task().execute(context)
        return context.response
