from business.object_factory import BusinessObjectFactory
from common.dtos.req_resp_dtos import GetProductContext, GetProductRequest, GetProductResponse
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import GetProductWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ValidateGetProductTask(WfTask):
    def execute(self, context: GetProductContext) -> GetProductContext:
        result = BusinessObjectFactory.catalog_biz().validate_get(context.request)
        context.error = result.error
        return context


class ReadProductTask(WfTask):
    def execute(self, context: GetProductContext) -> GetProductContext:
        response = ServiceObjectFactory.catalog_svc().get_product(context.request)
        context.response = response
        context.error = response.error
        return context


class GetProductWfImpl(GetProductWf):
    def invoke(self, request: GetProductRequest) -> GetProductResponse:
        context = GetProductContext(request=request)
        context = WorkflowObjectFactory.validate_get_product_task().execute(context)
        if context.error is None:
            context = WorkflowObjectFactory.read_product_task().execute(context)
        if context.response is None:
            return GetProductResponse(error=context.error)
        return context.response
