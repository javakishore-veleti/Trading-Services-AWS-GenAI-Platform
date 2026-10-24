from common.dtos.req_resp_dtos import BooksContext, BooksResponse, EmptyRequest
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ListBooksWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ReadBooksTask(WfTask):
    def execute(self, context: BooksContext) -> BooksContext:
        response = ServiceObjectFactory.master_data_svc().list_books(context.request)
        context.response = response
        context.error = response.error
        return context


class ListBooksWfImpl(ListBooksWf):
    def invoke(self, request: EmptyRequest) -> BooksResponse:
        context = BooksContext(request=request)
        context = WorkflowObjectFactory.read_books_task().execute(context)
        return context.response
