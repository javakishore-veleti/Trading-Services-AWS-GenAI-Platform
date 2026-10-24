from common.dtos.req_resp_dtos import BookDefaultsContext, BookDefaultsResponse, EmptyRequest
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ListBookDefaultsWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ReadBookDefaultsTask(WfTask):
    def execute(self, context: BookDefaultsContext) -> BookDefaultsContext:
        response = ServiceObjectFactory.master_data_svc().list_book_defaults(context.request)
        context.response = response
        context.error = response.error
        return context


class ListBookDefaultsWfImpl(ListBookDefaultsWf):
    def invoke(self, request: EmptyRequest) -> BookDefaultsResponse:
        context = BookDefaultsContext(request=request)
        context = WorkflowObjectFactory.read_book_defaults_task().execute(context)
        return context.response
