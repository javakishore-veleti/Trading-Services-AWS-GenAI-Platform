from business.object_factory import BusinessObjectFactory
from common.dtos.req_resp_dtos import GetPartnerContext, GetPartnerRequest, GetPartnerResponse
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import GetPartnerWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ValidateGetPartnerTask(WfTask):
    def execute(self, context: GetPartnerContext) -> GetPartnerContext:
        result = BusinessObjectFactory.partner_biz().validate_get(context.request)
        context.error = result.error
        return context


class ReadPartnerTask(WfTask):
    def execute(self, context: GetPartnerContext) -> GetPartnerContext:
        response = ServiceObjectFactory.partner_svc().get_partner(context.request)
        context.response = response
        context.error = response.error
        return context


class GetPartnerWfImpl(GetPartnerWf):
    def invoke(self, request: GetPartnerRequest) -> GetPartnerResponse:
        context = GetPartnerContext(request=request)
        context = WorkflowObjectFactory.validate_get_partner_task().execute(context)
        if context.error is None:
            context = WorkflowObjectFactory.read_partner_task().execute(context)
        if context.response is None:
            return GetPartnerResponse(error=context.error)
        return context.response
