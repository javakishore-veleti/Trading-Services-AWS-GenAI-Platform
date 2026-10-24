PLATFORM_TEAM = "BU1004-trading-desk-platforms"
BLOCKED_FIELDS = {
    "discount_bps": True,
    "spread_bps": True,
    "net_spread_bps": True,
    "all_in_rate": True,
    "all_in": True,
    "timing": True,
    "effective": True,
    "bill_through_date": True,
    "bill_through": True,
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


def parse_json(text):
    try:
        return json_parse(text)
    except Exception:
        return None


def collect_payloads(inputs):
    found = []
    texts = read_value(inputs, "texts") or []
    for text in texts:
        parsed = parse_json(as_text(text))
        if parsed is not None:
            found.append(parsed)
    calls = read_value(inputs, "tool_calls") or []
    for call in calls:
        function = read_value(call, "function") or {}
        arguments = read_value(function, "arguments")
        if arguments is None:
            arguments = read_value(call, "arguments")
        if isinstance(arguments, str):
            arguments = parse_json(arguments)
        if arguments is not None:
            found.append(arguments)
    return found


def find_blocked_field(value):
    if isinstance(value, dict):
        for key in value:
            if key in BLOCKED_FIELDS and value.get(key) not in (None, ""):
                return key
            found = find_blocked_field(value.get(key))
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = find_blocked_field(item)
            if found is not None:
                return found
    return None


def apply_guardrail(inputs, request_data, input_type):
    if input_type != "request":
        return allow()
    if read_value(request_data, "team_id") != PLATFORM_TEAM:
        return allow()
    for payload in collect_payloads(inputs):
        field = find_blocked_field(payload)
        if field is not None:
            return block("A selling platform can carry the customer, the product, and the requested change. It cannot set the price or the timing.")
    return allow()
