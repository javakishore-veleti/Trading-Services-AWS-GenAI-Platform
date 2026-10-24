TEAMS = {
    "BU1000-trading-desk-offers": ["trades_offers_mcp"],
    "BU1003-trading-desk-order": ["trades_orders_mcp"],
    "BU1002-trading-desk-io": ["trades_catalog_mcp", "trades_offers_mcp", "trades_orders_mcp"],
    "BU1001-trading-desk-bffs": ["trades_catalog_mcp", "trades_offers_mcp", "trades_orders_mcp"],
    "BU1004-trading-desk-platforms": ["trades_catalog_mcp", "trades_offers_mcp", "trades_orders_mcp"],
}


def read_value(obj, key):
    if isinstance(obj, dict):
        return obj.get(key)
    return None


def as_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def tool_names(inputs):
    names = []
    calls = read_value(inputs, "tool_calls") or []
    for call in calls:
        function = read_value(call, "function") or {}
        name = as_text(read_value(function, "name") or read_value(call, "name"))
        if name != "":
            names.append(name)
    return names


def apply_guardrail(inputs, request_data, input_type):
    if input_type != "request":
        return allow()
    team_id = as_text(read_value(request_data, "team_id"))
    allowed = TEAMS.get(team_id)
    if allowed is None:
        return allow()
    for name in tool_names(inputs):
        server = name.split("-")[0]
        if server not in allowed:
            return block("This team can call only the tools for its own business.")
    return allow()
