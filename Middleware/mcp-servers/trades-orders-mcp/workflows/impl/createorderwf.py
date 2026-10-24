from business.object_factory import BusinessObjectFactory
from common.dtos.req_resp_dtos import CreateOrderContext, CreateOrderRequest, CreateOrderResponse
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import CreateOrderWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ValidateCreateOrderTask(WfTask):
    def execute(self, context: CreateOrderContext) -> CreateOrderContext:
        result = BusinessObjectFactory.order_biz().validate_create(context.request)
        context.error = result.error
        return context


class InsertOrderTask(WfTask):
    def execute(self, context: CreateOrderContext) -> CreateOrderContext:
        response = ServiceObjectFactory.order_svc().create_order(context.request)
        context.response = response
        context.error = response.error
        return context


class CreateOrderWfImpl(CreateOrderWf):
    def invoke(self, request: CreateOrderRequest) -> CreateOrderResponse:
        context = CreateOrderContext(request=request)
        context = WorkflowObjectFactory.validate_create_order_task().execute(context)
        if context.error is None:
            context = WorkflowObjectFactory.insert_order_task().execute(context)
        if context.response is None:
            return CreateOrderResponse(error=context.error)
        return context.response
