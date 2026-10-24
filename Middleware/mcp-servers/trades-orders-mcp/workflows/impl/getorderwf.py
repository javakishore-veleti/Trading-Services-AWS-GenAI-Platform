from business.object_factory import BusinessObjectFactory
from common.dtos.req_resp_dtos import GetOrderContext, GetOrderRequest, GetOrderResponse
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import GetOrderWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ValidateGetOrderTask(WfTask):
    def execute(self, context: GetOrderContext) -> GetOrderContext:
        result = BusinessObjectFactory.order_biz().validate_get(context.request)
        context.error = result.error
        return context


class ReadOrderTask(WfTask):
    def execute(self, context: GetOrderContext) -> GetOrderContext:
        response = ServiceObjectFactory.order_svc().get_order(context.request)
        context.response = response
        context.error = response.error
        return context


class GetOrderWfImpl(GetOrderWf):
    def invoke(self, request: GetOrderRequest) -> GetOrderResponse:
        context = GetOrderContext(request=request)
        context = WorkflowObjectFactory.validate_get_order_task().execute(context)
        if context.error is None:
            context = WorkflowObjectFactory.read_order_task().execute(context)
        if context.response is None:
            return GetOrderResponse(error=context.error)
        return context.response
