from business.interfaces import MasterDataBiz
from common.dtos.req_resp_dtos import ErrorDto, ListCountriesRequest, RegionResolutionDto


class MasterDataBizImpl(MasterDataBiz):
    _regions = {"us": "US", "europe": "Europe", "asia": "Asia"}

    def resolve_region(self, request: ListCountriesRequest) -> RegionResolutionDto:
        if request.region is None or not request.region.strip():
            return RegionResolutionDto(request=ListCountriesRequest())
        canonical = MasterDataBizImpl._regions.get(request.region.strip().lower())
        if canonical is None:
            return RegionResolutionDto(
                request=request,
                error=ErrorDto(code="invalid", message="region must be US, Europe, or Asia"),
            )
        return RegionResolutionDto(request=ListCountriesRequest(region=canonical))
