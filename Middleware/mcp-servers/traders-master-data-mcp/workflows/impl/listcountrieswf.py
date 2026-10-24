from business.object_factory import BusinessObjectFactory
from common.dtos.req_resp_dtos import CountriesContext, CountriesResponse, ListCountriesRequest
from services.object_factory import ServiceObjectFactory
from workflows.interfaces import ListCountriesWf, WfTask
from workflows.object_factory import WorkflowObjectFactory


class ResolveRegionTask(WfTask):
    def execute(self, context: CountriesContext) -> CountriesContext:
        result = BusinessObjectFactory.master_data_biz().resolve_region(context.request)
        context.request = result.request
        context.error = result.error
        return context


class ReadCountriesTask(WfTask):
    def execute(self, context: CountriesContext) -> CountriesContext:
        response = ServiceObjectFactory.master_data_svc().list_countries(context.request)
        context.response = response
        context.error = response.error
        return context


class ListCountriesWfImpl(ListCountriesWf):
    def invoke(self, request: ListCountriesRequest) -> CountriesResponse:
        context = CountriesContext(request=request)
        context = WorkflowObjectFactory.resolve_region_task().execute(context)
        if context.error is None:
            context = WorkflowObjectFactory.read_countries_task().execute(context)
        if context.response is None:
            return CountriesResponse(countries=[], error=context.error)
        return context.response
