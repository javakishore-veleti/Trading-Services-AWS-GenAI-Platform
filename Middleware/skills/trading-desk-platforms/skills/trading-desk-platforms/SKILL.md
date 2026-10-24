---
name: trading-desk-platforms
description: Pass a Salesforce CRM or Shopify request that names a FOREX customer, pair, and change to the offer book and the order book, then store their result on the platform. The platform supplies no discount, no all-in, and no timing.
---

# FOREX trading desk platforms

This skill connects the FOREX trading desk to an external platform. Salesforce CRM and Shopify are the platforms this team owns. Another platform of the same kind is handled the same way.

A platform record, such as a CRM opportunity or a Shopify checkout, is not itself a FOREX quote or a FOREX order. Before it is carried across, it needs a customer, a pair, a side, a notional, and the requested change. A record missing one of those stays on the platform.

This team carries the customer, the product, and the requested change to the offer book and the order book, then writes the quote and the order result back to the platform.

This team does not set the rating discount. It does not choose immediate or bill-through timing. Those decisions stay with the offer book and the order book.
