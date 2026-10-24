IO_TEAM = "BU1002-trading-desk-io"
COUNTRIES = {
    "south korea": True,
    "korea": True,
    "kr": True,
    "japan": True,
    "jp": True,
    "china": True,
    "cn": True,
    "australia": True,
    "au": True,
    "new zealand": True,
    "nz": True,
    "brazil": True,
    "br": True,
    "belgium": True,
    "be": True,
    "france": True,
    "fr": True,
}
COUNTRY_FIELDS = {"country": True, "home": True, "customer_country": True}


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


def check_countries(value):
    if isinstance(value, dict):
        for key in value:
            if key in COUNTRY_FIELDS:
                country = as_text(value.get(key)).strip().lower()
                if country != "" and country not in COUNTRIES:
                    return country
            blocked = check_countries(value.get(key))
            if blocked is not None:
                return blocked
    elif isinstance(value, list):
        for item in value:
            blocked = check_countries(item)
            if blocked is not None:
                return blocked
    return None


def apply_guardrail(inputs, request_data, input_type):
    if input_type != "request":
        return allow()
    if read_value(request_data, "team_id") != IO_TEAM:
        return allow()
    for payload in collect_payloads(inputs):
        blocked = check_countries(payload)
        if blocked is not None:
            return block("International operations covers South Korea, Japan, China, Australia, New Zealand, Brazil, Belgium, and France.")
    return allow()
