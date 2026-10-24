from common.dtos.req_resp_dtos import ChannelsContext, ChannelsResponse, EmptyRequest
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ListChannelsWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ReadChannelsTask(WfTask):
    def execute(self, context: ChannelsContext) -> ChannelsContext:
        response = ServiceObjectFactory.master_data_svc().list_channels(context.request)
        context.response = response
        context.error = response.error
        return context


class ListChannelsWfImpl(ListChannelsWf):
    def invoke(self, request: EmptyRequest) -> ChannelsResponse:
        context = ChannelsContext(request=request)
        context = WorkflowObjectFactory.read_channels_task().execute(context)
        return context.response
