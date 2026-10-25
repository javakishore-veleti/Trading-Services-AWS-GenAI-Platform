from collections import Counter

from desk.findings import PRODUCT_NAMES


def rank_products(customer: dict, orders: list[dict], eligibility: list[dict], quote: dict) -> dict[str, int]:
    requirement = customer["settlement_requirement"]
    preferred = customer["preferences"]["preferred_product"]
    multi = len(requirement["dates"]) > 1
    available = bool(requirement["usd_available_now"])
    counts = Counter(order["order_header"]["product_id"] for order in orders)
    allowed = {row["product_id"] for row in eligibility if row["eligible"]}
    scores: dict[str, int] = {}
    for product in ("SPOT", "WINDOW_FORWARD", "CURRENCY_FUTURES"):
        if product not in allowed:
            continue
        score = 0
        if preferred == product:
            score += 2
        score += min(counts[product], 3)
        if product == "SPOT" and available and not multi:
            score += 4
        if product == "WINDOW_FORWARD" and not available and multi:
            score += 4
        if product == "CURRENCY_FUTURES" and multi:
            score -= 3
        if quote:
            score += 1
        scores[product] = score
    return scores


def choose(scores: dict[str, int]) -> str:
    return max(scores, key=lambda product: scores[product])


def why_not(product: str, customer: dict, quote: dict) -> str:
    requirement = customer["settlement_requirement"]
    dates = ", ".join(requirement["dates"])
    if product == "SPOT":
        if requirement["usd_available_now"] and len(requirement["dates"]) == 1:
            return "Spot matches one near-term conversion."
        return "Spot settles in two business days. The currency is still ahead, so spot does not lock the rate for the later dates."
    if product == "WINDOW_FORWARD":
        if not requirement["usd_available_now"] and len(requirement["dates"]) > 1:
            return f"Window Forward covers {dates} inside a {requirement['window_days']}-day window."
        return "One near-term date does not need a future settlement window."
    expiry = quote["currency_futures"]["expiry"]
    return (
        f"Currency Futures expire on {expiry} and require margin. "
        f"That fixed expiry does not follow the settlement dates {dates}."
    )


def recommendation(customer: dict, orders: list[dict], eligibility: list[dict], quote: dict, agent_findings: list[dict]) -> dict:
    scores = rank_products(customer, orders, eligibility, quote)
    if not scores:
        return {
            "product_id": "",
            "product_name": "",
            "amount": customer["settlement_requirement"]["amount"],
            "currency": customer["settlement_requirement"]["currency"],
            "rationale": "No eligible product was returned by the catalog.",
            "evidence": [],
            "alternatives": [],
            "risks": ["The trader still makes the decision."],
            "assumptions": [],
            "next_steps": ["Ask product control to confirm eligibility."],
            "trader_decides": True,
            "scores": {},
        }
    winner = choose(scores)
    requirement = customer["settlement_requirement"]
    pair = f"{requirement['base_currency']}/{requirement['term_currency']}"
    indicative = quote["indicative"]
    term_value = requirement["amount"] * indicative
    if winner == "WINDOW_FORWARD":
        rationale = (
            f"{customer['name']} expects to sell {requirement['amount']:,.0f} {requirement['currency']} "
            f"across {len(requirement['dates'])} dates inside {requirement['window_days']} days, and the currency is not available for spot. "
            f"Past multi-date orders used Window Forward. {pair} indicative {indicative} and the 30-day window outright "
            f"{quote['window_forward']['outright']} come from {quote['quote_id']}. "
            f"At the indicative rate the term amount is {term_value:,.2f} {requirement['term_currency']}."
        )
    elif winner == "SPOT":
        rationale = (
            f"{customer['name']} has {requirement['amount']:,.0f} {requirement['currency']} available "
            f"for one settlement on {requirement['dates'][0]}. "
            f"{pair} spot bid {quote['spot']['bid']} and ask {quote['spot']['ask']} come from {quote['quote_id']}."
        )
    else:
        rationale = (
            f"{customer['name']} ranks Currency Futures first on the loaded records. "
            f"The futures price is {quote['currency_futures']['price']} with expiry {quote['currency_futures']['expiry']}."
        )
    evidence = [item for agent in agent_findings for item in agent["evidence"]]
    alternatives = [
        {"product_id": product, "product_name": PRODUCT_NAMES[product], "reason": why_not(product, customer, quote)}
        for product in scores
        if product != winner
    ]
    risks = [
        "The quote is from the offers service and is not an executed ticket.",
        "Historical order rates are illustrative and were not used as today's price.",
        "The trader confirms the product. The agents do not book it.",
    ]
    if winner == "WINDOW_FORWARD":
        risks.insert(0, "Window Forward still needs the exposure documents before product control will accept it.")
    if winner == "CURRENCY_FUTURES":
        risks.insert(0, "Margin and the fixed expiry still have to be acceptable to the customer.")
    return {
        "product_id": winner,
        "product_name": PRODUCT_NAMES[winner],
        "amount": requirement["amount"],
        "currency": requirement["currency"],
        "pair": pair,
        "rationale": rationale,
        "evidence": evidence,
        "alternatives": alternatives,
        "risks": risks,
        "assumptions": [
            "Customer, history, settlement dates, eligibility, and the quote were read from the API services for this turn.",
        ],
        "next_steps": [
            "The trader reviews the evidence and the alternatives.",
            "The trader confirms before an order is recorded.",
        ],
        "trader_decides": True,
        "scores": scores,
    }
