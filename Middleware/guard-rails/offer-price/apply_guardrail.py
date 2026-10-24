DISCOUNTS = {"AAA": 8.0, "AA": 6.0, "A": 4.0, "BBB": 2.5, "BB": 1.0}
SPREADS = {
    "spot": 10.0,
    "forward": 14.0,
    "swap": 12.0,
    "ndf": 18.0,
    "vanilla-option": 22.0,
    "barrier-option": 26.0,
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


def collect_quotes(value, found):
    if isinstance(value, dict):
        if "net_spread_bps" in value:
            found.append(value)
        for key in value:
            collect_quotes(value.get(key), found)
    elif isinstance(value, list):
        for item in value:
            collect_quotes(item, found)


def apply_guardrail(inputs, request_data, input_type):
    if input_type != "response":
        return allow()
    quotes = []
    for payload in collect_payloads(inputs):
        collect_quotes(payload, quotes)
    for quote in quotes:
        net = read_value(quote, "net_spread_bps")
        if net is None:
            continue
        net = float(net)
        if net < 0.5:
            return block("Offer net spread is below 0.5 basis points.")
        spread = read_value(quote, "spread_bps")
        discount = read_value(quote, "discount_bps")
        if spread is not None and discount is not None:
            expected = float(spread) - float(discount)
            if expected < 0.5:
                expected = 0.5
            if abs(net - expected) > 0.01:
                return block("Offer net spread does not follow the rating discount and the product spread.")
        rating = read_value(quote, "rating")
        if rating is not None and discount is not None and str(rating) in DISCOUNTS:
            if abs(float(discount) - DISCOUNTS.get(str(rating))) > 0.01:
                return block("Offer discount does not match the customer rating.")
        product = read_value(quote, "product_type")
        if product is not None and spread is not None and str(product) in SPREADS:
            if abs(float(spread) - SPREADS.get(str(product))) > 0.01:
                return block("Offer spread does not match the product.")
    return allow()
