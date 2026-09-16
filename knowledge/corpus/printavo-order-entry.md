---
id: printavo-order-entry
title: Printavo order entry
category: printavo
audience: sales, agents
visibility: public
updated: 2026-09-16
summary: How Shirt Co writes quotes and invoices in Printavo, including grouping, imprints, and dates.
tags: [printavo, billy, quoting]
---

# Printavo order entry

This is the public-safe process. Customer examples, ticket numbers, and inbox IDs stay in private training notes on the Mac Studio.

## Intents

1. **Initial quote** — customer wants pricing. Create a reviewable Printavo quote. Sales reviews and sends.
2. **Confirmed-order update** — customer sent final details. Update the existing ticket. Do not duplicate it.

Keep the full lifecycle on **one ticket** whenever possible.

## Customer lookup first

1. Search Printavo by email, then phone, then name.
2. Confirm an **exact** match. Do not pick a similar result.
3. If the customer exists, open them and choose **New Quote**.
4. If they do not exist, create a customer only when company name, email, and phone are present. Shipping address is required when the order ships. Default fulfillment is **pickup from Shirt Co** if shipping is not specified.
5. If required fields are missing, stop and tell the human what to collect.

## Quote vs confirmed order

Initial quotes may proceed without final size breakdown, official garment colors, or final art if those are marked **TBD / assumption**.

Minimum to create a reviewable quote:

- Exact existing customer **or** enough data to create one
- Company / school / event / customer name
- Email and phone
- Estimated quantity
- Product/style/tier good enough to quote

Confirmed-order updates also need: existing ticket match, final qty, size breakdown, official colors/styles, decoration details, due date / pickup or ship instructions.

## Dates and ticket fields

Typical defaults when entering a ticket (unless the thread says otherwise):

- **Production date:** 4 days out
- **Customer due date:** 5 days out
- **Billing date:** same as production due date
- **Invoice owner:** the salesperson who owns the thread (do not steal ownership)
- **Priority:** `normal`, `rush`, or `firm`
- **Goods/product status:** leave blank. The Shirt Co team changes this when they push the order through.

**Order title / nickname:** customer/org + event/team + item.

**Quantity label:** decoration + title + total pieces. Example pattern: `DTF - Francis Howell football senior shirts - 500 pieces`.

**Line-item description:** garment only (example: `Gildan Softstyle T-Shirt. 64000`). Do not dump sizes, art notes, or AI metadata into the product description.

## Product entry

1. Enter category / product type.
2. For DTF and branded blanks, enter the style number and wait for SanMar / S&S matches.
3. Pick the product; let Printavo autofill.
4. Enter sizes in the actual size fields. Do not collapse a size breakdown into one total.
5. Split **adult vs youth** into separate style lines when the quote form prefills an adult style. Example: adult Gildan `64000` vs youth `64000B`.

## Grouping

Printavo prices by **product group quantity**.

Group garments together when they get the **same design**: same artwork, same artwork size, same locations, same ink/color requirements. Different garment colors can share a group if the design is the same.

Start a new group when artwork, size, location set, or decoration pricing would change.

Do not split groups just because colors differ — that can drop the quantity break and mis-price the job.

## Imprints and pricing

Product price alone is not enough. Add imprints under each group:

1. First imprint uses the **first-location** matrix for that decoration method.
2. Extra locations use the **additional-location** matrix.
3. Screen print: choose color count per location. Front 2-color + back 1-color is two imprint entries, not one 3-color blend.
4. Use `/PRINT`-style notes for location, ink, and print details.
5. Click **Refresh Pricing / Auto Price**. If a group does not price, stop and flag it. Do not guess a unit price.
6. Save the ticket. Notify the **sales rep**, not the customer.

Trained screen-print example when it is clearly a 1-color logo on tees: **Screen Printing**, **Screen Print - 1st Location**, **1-color (Min 24 pc)**. Ink can remain `VERIFY FROM ART`.

If screen print vs DTF is unclear, create the review quote and leave pricing TBD.

## Production notes (`/prod` shape)

```text
TICKET WRITER/SALES REP: TBD

ART: /EXISTING

ART DETAILS:
PRODUCT:
GARMENT COLOR:
PRINT METHOD:
LOCATION:
INK:
SIZES:
INCLUDE UNION BUG
CUSTOMER ART ATTACHED - VERIFY ART / WHITE BACKGROUND BEFORE PRODUCTION

STORE: N

APPROVAL NEEDED? y
```

Keep Missive/source/confidence metadata **out** of production notes. Put that in the internal review note.

Attach uploaded art to **Production Files** on the ticket even if the quote is unsent.

## Website forms

No-reply senders are not the customer. Parse **Order for:** name, email, phone, products, sizes from the body. Youth sizes on an adult-prefilled style become a separate youth line.
