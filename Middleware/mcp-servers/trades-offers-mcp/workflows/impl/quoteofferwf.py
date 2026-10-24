from business.object_factory import BusinessObjectFactory
from common.dtos.req_resp_dtos import PriceOfferRequest, PriceOfferResponse, QuoteContext
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import QuoteOfferWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ValidateQuoteTask(WfTask):
    def execute(self, context: QuoteContext) -> QuoteContext:
        result = BusinessObjectFactory.offer_biz().validate(context.request)
        context.error = result.error
        return context


class LoadQuoteTask(WfTask):
    def execute(self, context: QuoteContext) -> QuoteContext:
        facts = ServiceObjectFactory.offer_svc().load_quote(context.request)
        context.facts = facts
        context.error = facts.error
        return context


class PriceQuoteTask(WfTask):
    def execute(self, context: QuoteContext) -> QuoteContext:
        response = BusinessObjectFactory.offer_biz().price(context.facts)
        context.response = response
        context.error = response.error
        return context


class QuoteOfferWfImpl(QuoteOfferWf):
    def invoke(self, request: PriceOfferRequest) -> PriceOfferResponse:
        context = QuoteContext(request=request)
        context = WorkflowObjectFactory.validate_quote_task().execute(context)
        if context.error is None:
            context = WorkflowObjectFactory.load_quote_task().execute(context)
        if context.error is None:
            context = WorkflowObjectFactory.price_quote_task().execute(context)
        if context.response is None:
            return PriceOfferResponse(error=context.error)
        return context.response
