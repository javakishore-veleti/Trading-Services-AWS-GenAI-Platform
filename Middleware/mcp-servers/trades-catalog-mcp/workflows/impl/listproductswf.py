from common.dtos.req_resp_dtos import ListProductsContext, ListProductsRequest, ListProductsResponse
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ListProductsWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ReadProductsTask(WfTask):
    def execute(self, context: ListProductsContext) -> ListProductsContext:
        response = ServiceObjectFactory.catalog_svc().list_products(context.request)
        context.response = response
        context.error = response.error
        return context


class ListProductsWfImpl(ListProductsWf):
    def invoke(self, request: ListProductsRequest) -> ListProductsResponse:
        context = ListProductsContext(request=request)
        context = WorkflowObjectFactory.read_products_task().execute(context)
        return context.response
