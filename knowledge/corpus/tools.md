---
id: tools
title: Tools Shirt Co uses
category: tools
audience: everyone
visibility: public
updated: 2026-09-16
summary: Printavo, Missive, garment vendors, and the internal hub tools.
tags: [printavo, missive, github, hub]
---

# Tools Shirt Co uses

## Printavo

Printavo is the system of record for quotes, invoices, customers, art/production files, and production status.

- Search customers by **email first**, then phone, then name. Exact match only.
- One ticket should cover the lifecycle: quote first, then update that same ticket when the order is confirmed.
- Pricing comes from Printavo imprint matrices and **Refresh Pricing**, not from an agent inventing a unit price.
- Production files belong on the ticket. Customer-facing notes are visible to the customer — keep them conservative.

## Missive

Shared inbox for sales and contract orders. Humans apply labels when they want Billy to draft a Printavo quote or update an invoice. Billy posts an **internal** review note back to the thread. Billy must never email the customer from Missive.

## Garment vendors

Printavo auto-prices blanks when linked vendors are available. Shirt Co's main linked vendors:

- SanMar
- S&S Activewear

Prefer keeping an invoice on one vendor instead of mixing unnecessarily. Enter the style number, wait for products to populate, then enter sizes in Printavo size fields.

## Internal hub (this repo)

Public GitHub Pages hub: `https://shirt-co.github.io/shirtco/`

| Tool | Status | What it does |
| --- | --- | --- |
| Transfer Orders | Live | Size-based DTF ordering, live $/sq in pricing, partner JSON |
| Supply Kanban | Live | QR labels, scan-to-reorder shop supplies |
| Company Brain | Live | Searchable company knowledge for people and agents |
| Quoting Tool | Planning | Faster quotes that match shop pricing |
| Art Tracker | Planning | Art request → approval → production handoff |

Shipping playbook for non-dev teammates: [SHIP.md](../../SHIP.md). Describe the change in plain English. A bot opens a PR. Connor (or a named Approver) merges. GitHub Pages publishes.

## Website / quotes

Customer bulk-order and quote forms on Shirt.co can arrive from a no-reply sender. Treat the **form body** as the customer source of truth, not the no-reply address.

## Text Blaze (Chrome)

Humans use Text Blaze shortcuts in Printavo:

- `/prod` fills the production-notes template
- `/PRINT` fills screen-print imprint notes

Agents should match those templates, not dump AI audit trails into production notes.
