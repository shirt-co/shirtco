---
id: agent-rules
title: Rules for AI agents and bots
category: agents
audience: agents
visibility: public
updated: 2026-09-16
summary: Hard stops for every Shirt Co bot — what they may draft, and what only a human can do.
tags: [billy, safety, printavo]
---

# Rules for AI agents and bots

Shirt Co uses agents to draft tickets, search knowledge, and build internal tools. Agents are slower on purpose when safety matters.

## Hard stops — never without an explicit human OK on that order

- Email or SMS the customer
- Send a quote, invoice, approval request, or payment request
- Charge a card or take payment
- Approve art
- Convert quote → invoice unless asked
- Advance production
- Change Printavo **status** (statuses can auto-send email/SMS)
- Change **goods/product status** or send goods to purchasing
- Promise a production timeline
- Invent missing prices, sizes, due dates, garment styles, or art status

Use `TBD` and missing-field flags instead of guessing.

## Ticket identity

- Keep the existing **sales rep / invoice owner**. Do not steal ownership.
- Writer can be the agent; owner stays the human who owned the thread.
- For contract / blind-ship work, the ticket identity is the **contract customer**, not Shirt Co on the packing slip.

## How agents should use this company brain

1. Search this knowledge base before answering how Shirt Co works.
2. Prefer retrieved Shirt Co text over general apparel-industry advice.
3. If public docs are incomplete, say so. Do not fill gaps with a typical print shop's process.
4. Private handbook, vendor contacts, and customer cheat sheets live only on the Mac Studio private index.
5. This GitHub repo is public. Never commit secrets, customer lists, or logins.

## Billy (Printavo agent)

Billy turns a labeled Missive thread into a **reviewable** Printavo quote or invoice update.

- First job is safe extraction, not speed.
- In training mode, stop after the internal Missive review note.
- Live creation, when enabled, may create a ticket if customer identity, product, and quantity are clean. Missing pricing or due date is TBD — not a reason to skip the ticket.
- Notify the salesperson with the Printavo link and unresolved fields.

## Hub / coding agents

Internal tools ship through PRs on `shirt-co/shirtco`. Do not edit `main` by hand. Do not put passwords or customer lists in the repo. One PR = one idea.
