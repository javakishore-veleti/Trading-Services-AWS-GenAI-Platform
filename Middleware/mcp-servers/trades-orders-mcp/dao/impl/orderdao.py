from common.dtos.req_resp_dtos import CreateOrderRequest, GetOrderRequest, ListOrdersRequest, OrderDto, OrderRowDto, OrderRowsDto
from dao.interfaces import OrderDao


class OrderDaoImpl(OrderDao):
    _orders: list[OrderDto] = [
        OrderDto(order_id="ORD-1001", customer_id="CUS-1001", product_id="SPOT-EURUSD", pair="EUR/USD", side="buy", notional=1000000, all_in_rate=1.0864, channel="Web", desk_location="US-East", status="filled"),
        OrderDto(order_id="ORD-1002", customer_id="CUS-1003", product_id="FWD-USDJPY-3M", pair="USD/JPY", side="sell", notional=2500000, all_in_rate=151.05, channel="Advisor", desk_location="Japan", status="filled"),
        OrderDto(order_id="ORD-1003", customer_id="CUS-1007", product_id="NDF-USDKRW", pair="USD/KRW", side="buy", notional=500000, all_in_rate=1366.1, channel="Mobile", desk_location="Singapore", status="working"),
    ]
    _next_id: int = 1004

    def find_orders(self, request: ListOrdersRequest) -> OrderRowsDto:
        rows = OrderDaoImpl._orders
        if request.customer_id:
            rows = [row for row in rows if row.customer_id == request.customer_id]
        if request.status:
            rows = [row for row in rows if row.status == request.status]
        return OrderRowsDto(orders=rows)

    def find_order(self, request: GetOrderRequest) -> OrderRowDto:
        found = next((row for row in OrderDaoImpl._orders if row.order_id == request.order_id), None)
        return OrderRowDto(order=found)

    def insert_order(self, request: CreateOrderRequest) -> OrderDto:
        order = OrderDto(
            order_id=f"ORD-{OrderDaoImpl._next_id}",
            customer_id=request.customer_id,
            product_id=request.product_id,
            pair=request.pair,
            side=request.side,
            notional=request.notional,
            all_in_rate=request.all_in_rate,
            channel=request.channel,
            desk_location=request.desk_location,
            status="working",
        )
        OrderDaoImpl._next_id += 1
        OrderDaoImpl._orders.append(order)
        return order
