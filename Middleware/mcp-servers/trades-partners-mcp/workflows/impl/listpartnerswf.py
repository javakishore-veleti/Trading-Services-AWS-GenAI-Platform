from common.dtos.req_resp_dtos import ListPartnersContext, ListPartnersRequest, ListPartnersResponse
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ListPartnersWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ReadPartnersTask(WfTask):
    def execute(self, context: ListPartnersContext) -> ListPartnersContext:
        response = ServiceObjectFactory.partner_svc().list_partners(context.request)
        context.response = response
        context.error = response.error
        return context


class ListPartnersWfImpl(ListPartnersWf):
    def invoke(self, request: ListPartnersRequest) -> ListPartnersResponse:
        context = ListPartnersContext(request=request)
        context = WorkflowObjectFactory.read_partners_task().execute(context)
        return context.response
