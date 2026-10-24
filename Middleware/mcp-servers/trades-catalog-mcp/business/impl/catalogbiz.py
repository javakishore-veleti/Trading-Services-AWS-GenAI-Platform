from common.dtos.req_resp_dtos import ErrorDto, GetProductRequest, ValidationDto
from business.interfaces import CatalogBiz


class CatalogBizImpl(CatalogBiz):
    def validate_get(self, request: GetProductRequest) -> ValidationDto:
        if not request.product_id.strip():
            return ValidationDto(error=ErrorDto(code="invalid", message="product_id is required"))
        return ValidationDto()
