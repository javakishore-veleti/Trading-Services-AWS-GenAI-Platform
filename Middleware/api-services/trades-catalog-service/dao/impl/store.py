from dao.interfaces import CatalogDao

PRODUCTS = [
    {
        "product_id": "SPOT",
        "name": "Spot",
        "meaning": "Exchange one currency for another at an agreed current rate, normally settling within two business days.",
    },
    {
        "product_id": "WINDOW_FORWARD",
        "name": "Window Forward",
        "meaning": "Agree on an exchange rate today and exchange currencies on permitted dates within a specified future settlement window.",
    },
    {
        "product_id": "CURRENCY_FUTURES",
        "name": "Currency Futures",
        "meaning": "Use standardized exchange-traded contracts to protect against currency movements, with margin requirements and fixed contract expiries.",
    },
]

REFERENCES = [
    {
        "reference_id": "REF-AD-1",
        "source": "Bank product control",
        "title": "Authorised dealer product conditions",
        "summary": "Eligibility and documentation stay with the bank's compliance systems. The agent reads the result and does not authorize the trade.",
    },
    {
        "reference_id": "REF-WINDOW-1",
        "source": "Product terms",
        "title": "Window settlement conditions",
        "summary": "A window forward needs an underlying exposure and permitted settlement dates inside the contracted window.",
    },
    {
        "reference_id": "REF-FUT-1",
        "source": "Exchange terms",
        "title": "Futures margin and expiry",
        "summary": "A currency future has a fixed expiry and a margin requirement. Those terms have to fit the customer's dates.",
    },
]


class CatalogDaoImpl(CatalogDao):
    def products(self) -> list[dict]:
        return list(PRODUCTS)

    def product(self, product_id: str) -> dict | None:
        for row in PRODUCTS:
            if row["product_id"] == product_id:
                return row
        return None

    def eligibility(self, customer_id: str) -> list[dict]:
        notes = {
            "SPOT": "Eligible for near-term conversion. It does not lock a rate for later receipts.",
            "WINDOW_FORWARD": "Eligible when the exposure and the settlement dates are documented.",
            "CURRENCY_FUTURES": "Eligible where the customer can meet margin and a fixed expiry.",
        }
        return [
            {
                "customer_id": customer_id,
                "product_id": row["product_id"],
                "eligible": True,
                "note": notes[row["product_id"]],
            }
            for row in PRODUCTS
        ]

    def references(self) -> list[dict]:
        return list(REFERENCES)
