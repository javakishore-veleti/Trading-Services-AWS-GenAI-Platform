from business.interfaces import DeskAgentBiz

CATALOG_FIELDS = {
    "product_id",
    "name",
    "product_type",
    "pair",
    "base",
    "quote",
    "tenor",
    "settlement",
    "min_notional_usd",
    "max_notional_usd",
    "customer_segments",
    "segment",
    "products",
    "product",
    "error",
}

OFFER_FIELDS = CATALOG_FIELDS | {
    "customer_id",
    "customer_name",
    "rating",
    "home",
    "side",
    "notional",
    "mid",
    "spread_bps",
    "discount_bps",
    "net_spread_bps",
    "all_in_rate",
    "total_quote_amount",
    "customers",
    "ratings",
    "description",
}

ORDER_FIELDS = {
    "customer_id",
    "product_id",
    "pair",
    "side",
    "notional",
    "all_in_rate",
    "channel",
    "desk_location",
    "order_id",
    "status",
    "change",
    "action",
    "order_change",
    "timing",
    "bill_through",
    "bill_through_date",
    "orders",
    "order",
    "error",
}

SCREEN_BLOCKED = {
    "discount_bps",
    "spread_bps",
    "net_spread_bps",
    "timing",
    "effective",
    "bill_through",
    "bill_through_date",
}

PLATFORM_BLOCKED = SCREEN_BLOCKED | {"all_in_rate", "all_in", "total_quote_amount"}

SLICE_FIELDS = {
    "catalog": CATALOG_FIELDS,
    "offer-book": OFFER_FIELDS,
    "order-book": ORDER_FIELDS,
}

TOOL_INPUTS = {
    'list_fx_products': {'product_type', 'segment'},
    'get_fx_product': {'product_id'},
    'list_customer_ratings': set(),
    'list_rating_discounts': set(),
    'quote_fx_offer': {'customer_id', 'notional', 'pair', 'product_type', 'side'},
    'list_fx_orders': {'customer_id', 'status'},
    'get_fx_order': {'order_id'},
    'create_fx_order': {'all_in_rate', 'channel', 'customer_id', 'desk_location', 'notional', 'pair', 'product_id', 'side'},
}

TOOL_SERVER = {
    'list_fx_products': ('catalog', 'trades-catalog-mcp'),
    'get_fx_product': ('catalog', 'trades-catalog-mcp'),
    'list_customer_ratings': ('offer-book', 'trades-offers-mcp'),
    'list_rating_discounts': ('offer-book', 'trades-offers-mcp'),
    'quote_fx_offer': ('offer-book', 'trades-offers-mcp'),
    'list_fx_orders': ('order-book', 'trades-orders-mcp'),
    'get_fx_order': ('order-book', 'trades-orders-mcp'),
    'create_fx_order': ('order-book', 'trades-orders-mcp'),
}


class FieldCompressor:
    def keep(self, payload: dict, allowed: set[str], blocked: set[str]) -> dict:
        return self._walk(payload, allowed, blocked)

    def _walk(self, value: object, allowed: set[str], blocked: set[str]) -> dict:
        if not isinstance(value, dict):
            return {}
        kept: dict = {}
        for key, item in value.items():
            if key in blocked or key not in allowed:
                continue
            if isinstance(item, dict):
                nested = self._walk(item, allowed, blocked)
                if nested:
                    kept[key] = nested
            elif isinstance(item, list):
                kept[key] = [
                    self._walk(row, allowed, blocked) if isinstance(row, dict) else row for row in item
                ]
            else:
                kept[key] = item
        return kept


class _AgentPolicy(DeskAgentBiz):
    agent_name = ""
    sub_agents: tuple[str, ...] = ()
    tools: set[str] = set()
    blocked: set[str] = set()
    _compressor = FieldCompressor()

    def sub_agent(self, tool: str) -> str | None:
        found = TOOL_SERVER.get(tool)
        if found is None or tool not in self.tools:
            return None
        name = found[0]
        if name not in self.sub_agents:
            return None
        return name

    def server_for(self, tool: str) -> str | None:
        found = TOOL_SERVER.get(tool)
        if found is None or tool not in self.tools:
            return None
        return found[1]

    def reject(self, tool: str) -> str | None:
        if tool not in self.tools:
            return f"{self.agent_name} cannot call {tool}."
        return None

    def select(self, tool: str, payload: dict) -> dict:
        allowed = TOOL_INPUTS.get(tool, set())
        if not allowed:
            return {}
        return self._compressor.keep(payload, allowed, self.blocked)

    def compress(self, sub_agent: str, payload: dict) -> tuple[str, dict]:
        allowed = SLICE_FIELDS.get(sub_agent, set())
        body = self._compressor.keep(payload, allowed, self.blocked)
        summary_parts: list[str] = []
        compacted: dict = {}
        for key, value in body.items():
            if isinstance(value, list):
                names = []
                for row in value:
                    if isinstance(row, dict):
                        names.append(
                            row.get("product_id")
                            or row.get("order_id")
                            or row.get("customer_id")
                            or row.get("rating")
                        )
                summary_parts.append(f"{key} {len(value)}")
                compacted[key] = {"count": len(value), "ids": [name for name in names if name][:8]}
            else:
                compacted[key] = value
        summary = ", ".join(summary_parts) if summary_parts else sub_agent
        return summary, compacted


class PlatformsAgentBiz(_AgentPolicy):
    """Carries a Salesforce or Shopify request to the offer book and the order book and writes the result back."""

    agent_name = "trading-desk-platforms"
    sub_agents = ('catalog', 'offer-book', 'order-book',)
    tools = {'create_fx_order', 'get_fx_order', 'get_fx_product', 'list_customer_ratings', 'list_fx_orders', 'list_fx_products', 'list_rating_discounts', 'quote_fx_offer'}
    blocked = PLATFORM_BLOCKED

    def reject(self, tool: str) -> str | None:
        if tool == "create_fx_order":
            return "A selling platform cannot set the price or the timing."
        return super().reject(tool)
