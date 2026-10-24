from business.interfaces import OfferBiz
from common.dtos.req_resp_dtos import ErrorDto, PriceOfferRequest, PriceOfferResponse, QuoteFactsDto, ValidationDto


class OfferBizImpl(OfferBiz):
    def validate(self, request: PriceOfferRequest) -> ValidationDto:
        if request.side not in ("buy", "sell"):
            return ValidationDto(error=ErrorDto(code="invalid", message="side must be buy or sell of the base currency"))
        if request.notional <= 0:
            return ValidationDto(error=ErrorDto(code="invalid", message="notional must be positive"))
        return ValidationDto()

    def price(self, facts: QuoteFactsDto) -> PriceOfferResponse:
        if facts.customer is None or facts.rating is None or facts.mid is None or facts.spread_bps is None:
            return PriceOfferResponse(error=ErrorDto(code="invalid", message="Quote facts are incomplete"))
        request = facts.request
        net_bps = max(facts.spread_bps - facts.rating.discount_bps, 0.5)
        sign = 1 if request.side == "buy" else -1
        all_in = round(facts.mid * (1 + sign * net_bps / 10000), 6)
        return PriceOfferResponse(
            customer_id=facts.customer.customer_id,
            customer_name=facts.customer.name,
            rating=facts.customer.rating,
            pair=request.pair,
            product_type=request.product_type,
            side=request.side,
            notional=request.notional,
            mid=facts.mid,
            spread_bps=facts.spread_bps,
            discount_bps=facts.rating.discount_bps,
            net_spread_bps=net_bps,
            all_in_rate=all_in,
            total_quote_amount=round(request.notional * all_in, 2),
        )
