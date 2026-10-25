PRODUCT_NAMES = {
    "SPOT": "Spot",
    "WINDOW_FORWARD": "Window Forward",
    "CURRENCY_FUTURES": "Currency Futures",
}

MODELS = {
    "behavior": "Qwen3-8B",
    "history": "Qwen3-14B",
    "settlement": "GPT-5 mini",
    "market": "Gemini 2.5 Flash",
    "hedging": "Claude Opus 4.5",
    "regulatory": "Claude Sonnet 4.5",
}


def finding(agent: str, model: str, summary: str, evidence: list[dict]) -> dict:
    return {
        "agent": agent,
        "model": model,
        "model_called": False,
        "summary": summary,
        "evidence": evidence,
    }


def behavior_finding(customer: dict) -> dict:
    preferences = customer["preferences"]
    name = PRODUCT_NAMES[preferences["preferred_product"]]
    return finding(
        "Customer Behavior",
        MODELS["behavior"],
        f"{customer['name']} usually chooses {name}. {preferences['note']}",
        [{
            "source": "customer-service",
            "record_id": customer["customer_id"],
            "detail": preferences["note"],
        }],
    )


def history_finding(customer: dict, orders: list[dict]) -> dict:
    counts = {"SPOT": 0, "WINDOW_FORWARD": 0, "CURRENCY_FUTURES": 0}
    evidence = []
    for order in orders:
        head = order["order_header"]
        counts[head["product_id"]] = counts.get(head["product_id"], 0) + 1
        evidence.append({
            "source": "customer-trades-history",
            "record_id": head["order_id"],
            "detail": f"{head['currency']} {head['amount']:,.0f} {PRODUCT_NAMES[head['product_id']]}: {head['settlement_pattern']}",
        })
    summary = (
        f"{counts['SPOT']} spot orders use a single settlement. "
        f"{counts['WINDOW_FORWARD']} window forwards split settlement across dates. "
        f"{counts['CURRENCY_FUTURES']} futures use a fixed expiry. "
        "History rates are illustrative and are not today's quote."
    )
    if not evidence:
        summary = f"{customer['name']} has no loaded orders. Populate customer trades history before relying on past trades."
    return finding("Historical Transaction", MODELS["history"], summary, evidence)


def settlement_finding(customer: dict) -> dict:
    requirement = customer["settlement_requirement"]
    dates = ", ".join(requirement["dates"])
    if requirement["usd_available_now"]:
        summary = (
            f"{requirement['currency']} {requirement['amount']:,.0f} is available for one settlement on {dates}. "
            "Spot can convert it in two business days."
        )
    else:
        summary = (
            f"{requirement['currency']} {requirement['amount']:,.0f} is expected across {len(requirement['dates'])} dates "
            f"({dates}) inside {requirement['window_days']} days. A window can hold those dates. "
            "A futures expiry may not."
        )
    return finding(
        "Settlement Requirements",
        MODELS["settlement"],
        summary,
        [{
            "source": "customer-service",
            "record_id": requirement["requirement_id"],
            "detail": requirement["purpose"],
        }],
    )


def market_finding(quote: dict) -> dict:
    window = quote["window_forward"]
    futures = quote["currency_futures"]
    summary = (
        f"{quote['pair']} indicative {quote['indicative']} from {quote['quote_id']}. "
        f"Spot bid {quote['spot']['bid']} / ask {quote['spot']['ask']}. "
        f"Window outright {window['outright']} for {window['window_days']} days. "
        f"Futures {futures['price']} expiring {futures['expiry']}, margin required."
    )
    return finding(
        "Market Intelligence",
        MODELS["market"],
        summary,
        [{
            "source": "trades-offers-services",
            "record_id": quote["quote_id"],
            "detail": f"indicative {quote['indicative']}",
        }],
    )


def regulatory_finding(eligibility: list[dict], references: list[dict]) -> dict:
    permitted = [PRODUCT_NAMES[row["product_id"]] for row in eligibility if row["eligible"]]
    summary = (
        "Permitted products: " + ", ".join(permitted) + ". "
        "The bank's controls still confirm eligibility and documents. This agent does not authorize the trade."
    )
    evidence = [
        {"source": "trades-catalog-service", "record_id": row["reference_id"], "detail": row["title"]}
        for row in references
    ]
    return finding("Regulatory Analysis", MODELS["regulatory"], summary, evidence)


def hedging_finding(customer: dict, winner: str) -> dict:
    name = PRODUCT_NAMES[winner]
    requirement = customer["settlement_requirement"]
    if winner == "WINDOW_FORWARD":
        summary = (
            f"Window Forward is the leading fit. {customer['name']} needs {requirement['currency']} sold across "
            f"{len(requirement['dates'])} future dates, which matches past window use more than spot or a fixed futures expiry."
        )
    elif winner == "SPOT":
        summary = (
            f"Spot is the leading fit. {customer['name']} has the currency available for one near-term settlement."
        )
    else:
        summary = f"Currency Futures is the leading fit for {customer['name']} on the loaded records."
    return finding(
        "Hedging Strategy",
        MODELS["hedging"],
        summary,
        [{"source": "decision-inputs", "record_id": customer["customer_id"], "detail": name}],
    )
