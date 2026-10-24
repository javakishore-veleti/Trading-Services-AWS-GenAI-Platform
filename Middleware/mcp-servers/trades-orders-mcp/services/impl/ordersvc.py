from common.dtos.req_resp_dtos import (
    CreateOrderRequest,
    CreateOrderResponse,
    ErrorDto,
    GetOrderRequest,
    GetOrderResponse,
    ListOrdersRequest,
    ListOrdersResponse,
)
from dao.object_factory import DaoObjectFactory
from services.interfaces import OrderSvc


class OrderSvcImpl(OrderSvc):
    def list_orders(self, request: ListOrdersRequest) -> ListOrdersResponse:
        rows = DaoObjectFactory.order_dao().find_orders(request)
        return ListOrdersResponse(orders=rows.orders)

    def get_order(self, request: GetOrderRequest) -> GetOrderResponse:
        row = DaoObjectFactory.order_dao().find_order(request)
        if row.order is None:
            return GetOrderResponse(error=ErrorDto(code="not_found", message=f"Unknown order {request.order_id}"))
        return GetOrderResponse(order=row.order)

    def create_order(self, request: CreateOrderRequest) -> CreateOrderResponse:
        order = DaoObjectFactory.order_dao().insert_order(request)
        return CreateOrderResponse(order=order)
