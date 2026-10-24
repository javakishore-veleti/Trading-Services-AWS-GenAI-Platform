CHANGES = {"new": True, "cancel": True, "upgrade": True, "downgrade": True}
TIMED = {"upgrade": True, "downgrade": True}
TIMINGS = {"immediate": True, "bill-through": True, "bill_through": True}


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


def call_payloads(inputs):
    found = []
    calls = read_value(inputs, "tool_calls") or []
    for call in calls:
        function = read_value(call, "function") or {}
        name = as_text(read_value(function, "name") or read_value(call, "name"))
        arguments = read_value(function, "arguments")
        if arguments is None:
            arguments = read_value(call, "arguments")
        if isinstance(arguments, str):
            arguments = parse_json(arguments)
        if not isinstance(arguments, dict):
            arguments = {}
        found.append({"name": name, "payload": arguments})
    return found


def nested_dicts(value, found):
    if isinstance(value, dict):
        found.append(value)
        for key in value:
            nested_dicts(value.get(key), found)
    elif isinstance(value, list):
        for item in value:
            nested_dicts(item, found)


def apply_guardrail(inputs, request_data, input_type):
    if input_type != "request":
        return allow()
    for call in call_payloads(inputs):
        payloads = []
        nested_dicts(call.get("payload"), payloads)
        for payload in payloads:
            change = read_value(payload, "change") or read_value(payload, "action") or read_value(payload, "order_change")
            if change is None:
                continue
            change = str(change).lower()
            if change not in CHANGES:
                return block("An order change must be new, cancel, upgrade, or downgrade.")
            if change not in TIMED:
                continue
            timing = read_value(payload, "timing") or read_value(payload, "effective")
            bill_through = read_value(payload, "bill_through_date") or read_value(payload, "bill_through")
            if bill_through not in (None, ""):
                continue
            if timing is None or str(timing).lower() not in TIMINGS:
                return block("An upgrade or downgrade must be immediate or bill-through.")
    return allow()
