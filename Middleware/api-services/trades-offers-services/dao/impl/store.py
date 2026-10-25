from dao.interfaces import OffersDao

# Illustrative board. USD/INR uses the desk's indicative 96. History files do not override this.
BOARD = {
    "USD/INR": 96.0,
    "EUR/USD": 1.08,
    "GBP/USD": 1.27,
    "USD/JPY": 151.0,
    "AUD/USD": 0.66,
    "USD/CAD": 1.36,
    "USD/CHF": 0.88,
    "NZD/USD": 0.60,
    "EUR/GBP": 0.85,
    "EUR/JPY": 163.0,
    "GBP/JPY": 191.0,
    "EUR/INR": 90.0,
    "GBP/INR": 105.0,
    "USD/SGD": 1.34,
    "USD/HKD": 7.80,
    "USD/CNH": 7.25,
    "AUD/JPY": 99.0,
    "USD/ZAR": 18.2,
    "USD/MXN": 17.1,
    "USD/TRY": 34.0,
    "USD/SEK": 10.5,
    "USD/NOK": 10.7,
    "USD/DKK": 6.9,
    "USD/PLN": 4.0,
    "USD/CZK": 23.0,
    "USD/HUF": 365.0,
    "USD/THB": 34.5,
    "USD/MYR": 4.4,
    "USD/IDR": 15800.0,
    "USD/KRW": 1350.0,
    "USD/TWD": 32.0,
    "USD/AED": 3.67,
    "USD/SAR": 3.75,
    "USD/BRL": 5.4,
}


class OffersDaoImpl(OffersDao):
    def quote(self, base: str, term: str, direction: str) -> dict | None:
        pair = f"{base.upper()}/{term.upper()}"
        mid = BOARD.get(pair)
        if mid is None:
            return None
        outright = round(mid + (0.25 if pair == "USD/INR" else mid * 0.002), 4 if mid < 20 else 2)
        return {
            "quote_id": f"QUOTE-{pair.replace('/', '')}",
            "pair": pair,
            "direction": direction,
            "rate_basis": "offers-service",
            "indicative": mid,
            "spot": {
                "bid": round(mid - (0.10 if pair == "USD/INR" else mid * 0.0005), 4 if mid < 20 else 2),
                "ask": round(mid + (0.10 if pair == "USD/INR" else mid * 0.0005), 4 if mid < 20 else 2),
                "settlement": "two business days",
            },
            "window_forward": {
                "outright": outright,
                "forward_points": round(outright - mid, 4),
                "window_days": 30,
            },
            "currency_futures": {
                "price": round(mid + (0.50 if pair == "USD/INR" else mid * 0.004), 4 if mid < 20 else 2),
                "expiry": "2026-11-26",
                "margin_required": True,
            },
        }
