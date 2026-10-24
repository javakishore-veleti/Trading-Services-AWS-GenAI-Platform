from common.dtos.req_resp_dtos import BookChannelsContext, BookChannelsResponse, EmptyRequest
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ListBookChannelsWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ReadBookChannelsTask(WfTask):
    def execute(self, context: BookChannelsContext) -> BookChannelsContext:
        response = ServiceObjectFactory.master_data_svc().list_book_channels(context.request)
        context.response = response
        context.error = response.error
        return context


class ListBookChannelsWfImpl(ListBookChannelsWf):
    def invoke(self, request: EmptyRequest) -> BookChannelsResponse:
        context = BookChannelsContext(request=request)
        context = WorkflowObjectFactory.read_book_channels_task().execute(context)
        return context.response
