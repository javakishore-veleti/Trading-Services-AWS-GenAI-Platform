---
name: trading-desk-bffs
description: Carry Advisor, Partner, Dealer, Mobile, Web, and Kiosk requests to the FOREX offer book and the order book, then show the all-in and the change those books returned. This backend does not compute a second price and does not pick immediate or bill-through.
---

# FOREX trading desk screens

This skill is the backend for the FOREX trading desk screens.

The screens are Advisor, Partner, Dealer, Mobile, Web, and Kiosk. A person working in one of those screens reaches the offer book and the order book through this backend.

The screen shows the quote the offer book returned and the change the order book accepted. It shows a stale mid as a stale mid. It does not replace that mid with a number from the screen. It does not invent a second all-in.

This team carries the screen request to the team that owns the decision and returns the answer to the screen. It does not set the rating discount. It does not choose whether an upgrade or a downgrade is immediate or bill-through. If the offer book has no price, the screen does not send an order.
