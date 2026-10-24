from common.dtos.req_resp_dtos import ListOrdersContext, ListOrdersRequest, ListOrdersResponse
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ListOrdersWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ReadOrdersTask(WfTask):
    def execute(self, context: ListOrdersContext) -> ListOrdersContext:
        response = ServiceObjectFactory.order_svc().list_orders(context.request)
        context.response = response
        context.error = response.error
        return context


class ListOrdersWfImpl(ListOrdersWf):
    def invoke(self, request: ListOrdersRequest) -> ListOrdersResponse:
        context = ListOrdersContext(request=request)
        context = WorkflowObjectFactory.read_orders_task().execute(context)
        return context.response
