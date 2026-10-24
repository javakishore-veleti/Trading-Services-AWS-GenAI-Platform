---
name: trading-desk-order
description: Book a FOREX new order, cancel, upgrade, or downgrade. An upgrade or downgrade is an immediate cancel of the current order or a bill-through date, never an edit in place. New risk waits when the book has stopped for the day, and the notional cannot exceed the quote.
---

# FOREX trading desk orders

This skill owns a change to a FOREX trading desk order. There are four changes. Each change names the quote that supplied the all-in. An order with no quote is not booked. An order whose only reason is to win back the last loss is not booked until the offer book prices it on its own.

## New

Place the order at the quoted notional and all-in. The notional cannot be larger than the notional on that quote.

## Cancel

End the order. A cancel is accepted even when the book has stopped taking new FOREX risk for the day.

## Upgrade

Move the customer to a higher order. Pick one timing.

- Immediate: cancel the existing order now, then start the upgraded order.
- Bill-through: keep billing the existing order until the bill-through date, then start the upgraded order.

## Downgrade

Move the customer to a lower order. Use the same two timings as an upgrade. A downgrade that reduces notional is still accepted when the book has stopped taking new risk.

When the book has stopped taking new FOREX risk for the day, do not place a new order and do not place an upgrade. Say that the book is closed for new risk and stop there.

An upgrade or a downgrade is not an edit of the existing order in place. Write down the change, the timing, and the quote that justified the all-in.
