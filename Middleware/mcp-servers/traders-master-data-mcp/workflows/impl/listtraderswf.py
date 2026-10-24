from common.dtos.req_resp_dtos import ListTradersRequest, TradersContext, TradersResponse
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ListTradersWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ReadTradersTask(WfTask):
    def execute(self, context: TradersContext) -> TradersContext:
        response = ServiceObjectFactory.master_data_svc().list_traders(context.request)
        context.response = response
        context.error = response.error
        return context


class ListTradersWfImpl(ListTradersWf):
    def invoke(self, request: ListTradersRequest) -> TradersResponse:
        context = TradersContext(request=request)
        context = WorkflowObjectFactory.read_traders_task().execute(context)
        return context.response
