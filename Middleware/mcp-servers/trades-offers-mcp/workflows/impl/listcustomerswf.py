from common.dtos.req_resp_dtos import ListCustomersContext, ListCustomersRequest, ListCustomersResponse
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ListCustomersWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ReadCustomersTask(WfTask):
    def execute(self, context: ListCustomersContext) -> ListCustomersContext:
        response = ServiceObjectFactory.offer_svc().list_customers(context.request)
        context.response = response
        context.error = response.error
        return context


class ListCustomersWfImpl(ListCustomersWf):
    def invoke(self, request: ListCustomersRequest) -> ListCustomersResponse:
        context = ListCustomersContext(request=request)
        context = WorkflowObjectFactory.read_customers_task().execute(context)
        return context.response
