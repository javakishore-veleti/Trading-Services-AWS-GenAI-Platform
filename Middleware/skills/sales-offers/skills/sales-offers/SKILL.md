---
name: sales-offers
description: Price an FX trade from the customer rating, the rating discount, and the all-in quote.
---

# Sales offers

This skill is the FX offer desk. Use it when a seller needs a price for a customer. The desk owns the rating, the discount, and the all-in quote.

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

An unknown customer, mid, or rating is not a price. An unknown product type is not a price.

## Tools

- list_customer_ratings
- list_rating_discounts
- quote_fx_offer
