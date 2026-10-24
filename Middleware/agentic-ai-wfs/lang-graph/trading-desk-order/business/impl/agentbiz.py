from business.interfaces import DeskAgentBiz

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

SLICE_FIELDS = {
    "order-book": ORDER_FIELDS,
}

TOOL_INPUTS = {
    'list_fx_orders': {'customer_id', 'status'},
    'get_fx_order': {'order_id'},
    'create_fx_order': {'all_in_rate', 'channel', 'customer_id', 'desk_location', 'notional', 'pair', 'product_id', 'side'},
}

TOOL_SERVER = {
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


class OrderAgentBiz(_AgentPolicy):
    """Books a new order, cancel, upgrade, or downgrade. An upgrade or downgrade is immediate or bill-through."""

    agent_name = "trading-desk-order"
    sub_agents = ('order-book',)
    tools = {'create_fx_order', 'get_fx_order', 'list_fx_orders'}
    blocked = set()
