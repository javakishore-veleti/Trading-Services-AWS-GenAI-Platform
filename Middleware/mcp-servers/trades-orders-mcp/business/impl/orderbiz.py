from business.interfaces import OrderBiz
from common.dtos.req_resp_dtos import CreateOrderRequest, ErrorDto, GetOrderRequest, ValidationDto


class OrderBizImpl(OrderBiz):
    def validate_get(self, request: GetOrderRequest) -> ValidationDto:
        if not request.order_id.strip():
            return ValidationDto(error=ErrorDto(code="invalid", message="order_id is required"))
        return ValidationDto()

    def validate_create(self, request: CreateOrderRequest) -> ValidationDto:
        if request.side not in ("buy", "sell"):
            return ValidationDto(error=ErrorDto(code="invalid", message="side must be buy or sell"))
        if request.notional <= 0 or request.all_in_rate <= 0:
            return ValidationDto(error=ErrorDto(code="invalid", message="notional and all_in_rate must be positive"))
        return ValidationDto()
