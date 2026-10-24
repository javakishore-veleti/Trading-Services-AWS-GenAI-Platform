READS = {"list_analytics_grains": True, "read_fx_analytics": True}


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
    tools = read_value(inputs, "tools") or []
    for tool in tools:
        function = read_value(tool, "function") or {}
        name = as_text(read_value(function, "name") or read_value(tool, "name"))
        if name != "":
            names.append(name)
    return names


def apply_guardrail(inputs, request_data, input_type):
    if input_type != "request":
        return allow()
    for name in tool_names(inputs):
        if "traders_analytics_mcp" not in name and name not in READS:
            continue
        short = name.split("-")[-1]
        if short not in READS:
            return block("Analytics is read-only.")
    return allow()
