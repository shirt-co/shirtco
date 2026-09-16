---
id: shipping
title: Shipping, pickup, and packing identity
category: shipping
audience: everyone
visibility: public
updated: 2026-09-16
summary: Pickup vs ship, blind ship, white-label packing slips, and when address is required.
tags: [shipping, pickup, blind-ship]
---

# Shipping, pickup, and packing identity

## Default

If a quote thread does not specify shipping, default to **pickup from Shirt Co**. A shipping address is required only when the order is actually shipping.

## Blind ship / white label

Used when Shirt Co should not appear as the decorator to the end customer.

- Packing slip name = the brand the partner/contract customer wants shown.
- Transfer Orders partner jobs default white-label and blind ship **on**.
- Contract decorate-only jobs ship as the contract customer, not Shirt Co.

Do not guess ship-to when the PO could mean the end customer **or** the contract customer's warehouse. Flag it.

## Wholesale DTF shipping (hub defaults)

- Flat shipping $8.50
- Free shipping at $75 subtotal
- Rush and union-print are fulfillment flags on the transfer order, not silent promises

## Production vs customer due dates

On Printavo tickets, production date and customer due date are different fields. Typical entry defaults (4 days / 5 days out) are **not** a promised in-hands date. Agents must not promise a timeline.
