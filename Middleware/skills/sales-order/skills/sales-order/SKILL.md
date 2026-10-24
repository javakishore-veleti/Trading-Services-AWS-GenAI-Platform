---
name: sales-order
description: Place, cancel, upgrade, or downgrade an order. An upgrade or downgrade is immediate or bill-through.
---

# Sales orders

This skill owns a change to a commercial order. There are four changes.

## New

Place the order.

## Cancel

End the order.

## Upgrade

Move the customer to a higher order. Pick one timing.

- Immediate: cancel the existing order now, then start the upgraded order.
- Bill-through: keep billing the existing order until the bill-through date, then start the upgraded order.

## Downgrade

Move the customer to a lower order. Use the same two timings as an upgrade.

An upgrade or a downgrade is not an edit of the existing order in place.
