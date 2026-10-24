---
name: trading-desk-offers
description: Build the FOREX all-in from the customer rating band, the product spread, and a fresh mid. AAA removes 8 basis points, BB removes 1, and the net never prints below 0.5. A missing mid, a due data release, or an unknown product is no quote.
---

# FOREX trading desk offers

This skill is the FOREX trading desk offer book. Use it when the desk needs a price for a customer. The desk owns the rating, the discount, and the all-in quote.

A quote needs a known customer, a catalog pair, a side, a notional, a mid, a rating, and a product type. If one of those is missing, there is no price. A headline is not a mid. A chart comment is not a mid. The mid is stale when a scheduled release for either currency is due and the desk has not taken a new mid after that release.

## Rating discounts

Discounts are in basis points.

- AAA: 8
- AA: 6
- A: 4
- BBB: 2.5
- BB: 1

## Product spreads

Spreads are in basis points, before the discount.

- Spot: 10
- Forward: 14
- Swap: 12
- NDF: 18
- Vanilla option: 22
- Barrier option: 26

The net spread is the product spread minus the rating discount, and it never goes below 0.5 basis points. One basis point is 0.0001. A buy all-in price is the mid multiplied by one plus the net spread. A sell all-in price subtracts it.

Say the three figures in the quote: the rating discount, the product spread, and the net. Also say the all-in on the mid as given, and the all-in if that same mid is 10 pips higher or 10 pips lower. The net does not change in that illustration. A wish to change the spread table is not a quote.

The notional on the quote is the largest notional an order may use. This book does not raise it.

An unknown customer, mid, or rating is not a price. An unknown product type is not a price.

## Tools

- list_customer_ratings
- list_rating_discounts
- quote_fx_offer
