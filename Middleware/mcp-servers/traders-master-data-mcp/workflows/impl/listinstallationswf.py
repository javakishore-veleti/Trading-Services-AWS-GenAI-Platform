from common.dtos.req_resp_dtos import InstallationsContext, InstallationsResponse, ListInstallationsRequest
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ListInstallationsWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ReadInstallationsTask(WfTask):
    def execute(self, context: InstallationsContext) -> InstallationsContext:
        response = ServiceObjectFactory.master_data_svc().list_installations(context.request)
        context.response = response
        context.error = response.error
        return context


class ListInstallationsWfImpl(ListInstallationsWf):
    def invoke(self, request: ListInstallationsRequest) -> InstallationsResponse:
        context = InstallationsContext(request=request)
        context = WorkflowObjectFactory.read_installations_task().execute(context)
        return context.response
