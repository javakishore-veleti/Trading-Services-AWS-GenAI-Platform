from business.object_factory import BusinessObjectFactory
from common.dtos.req_resp_dtos import ReadAnalyticsContext, ReadAnalyticsRequest, ReadAnalyticsResponse
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ReadAnalyticsWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ValidateReadTask(WfTask):
    def execute(self, context: ReadAnalyticsContext) -> ReadAnalyticsContext:
        result = BusinessObjectFactory.analytics_biz().validate_read(context.request)
        context.error = result.error
        return context


class ReadRowsTask(WfTask):
    def execute(self, context: ReadAnalyticsContext) -> ReadAnalyticsContext:
        response = ServiceObjectFactory.analytics_svc().read_analytics(context.request)
        context.response = response
        context.error = response.error
        return context


class ReadAnalyticsWfImpl(ReadAnalyticsWf):
    def invoke(self, request: ReadAnalyticsRequest) -> ReadAnalyticsResponse:
        context = ReadAnalyticsContext(request=request)
        context = WorkflowObjectFactory.validate_read_task().execute(context)
        if context.error is None:
            context = WorkflowObjectFactory.read_rows_task().execute(context)
        if context.response is None:
            return ReadAnalyticsResponse(rows=[], error=context.error)
        return context.response
