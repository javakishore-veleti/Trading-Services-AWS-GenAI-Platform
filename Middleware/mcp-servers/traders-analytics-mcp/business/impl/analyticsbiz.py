from business.interfaces import AnalyticsBiz
from common.dtos.req_resp_dtos import ErrorDto, ReadAnalyticsRequest, ValidationDto


class AnalyticsBizImpl(AnalyticsBiz):
    _grains = {"eod", "intraday", "hourly"}

    def validate_read(self, request: ReadAnalyticsRequest) -> ValidationDto:
        if request.grain not in AnalyticsBizImpl._grains:
            return ValidationDto(error=ErrorDto(code="invalid", message="grain must be eod, intraday, or hourly"))
        return ValidationDto()
