---
id: dtf-transfers
title: DTF transfers
category: dtf
audience: everyone
visibility: public
updated: 2026-09-16
summary: How Shirt Co sells and builds DTF work — shop garments, wholesale transfers, sizes, and pricing.
tags: [dtf, pricing, wholesale]
---

# DTF transfers

DTF is a **production method** at Shirt Co and a **wholesale product** for other shops. Consumer hobbyist DTF storefront (DTFs.co as its own brand) is being folded into Shirt.co. Do not treat Shirt Co as a side-hustle transfer e-comm shop.

## Two paths

1. **Shirt.co decorated garments** — DTF printed onto goods the shop is fulfilling. Quoted and produced through Printavo with DTF first-location / additional-location matrices.
2. **Wholesale transfer orders** — partners order film by size and quantity. Gang sheets are assembled in production. Hub tool: Transfer Orders (`/transfers/`).

## Wholesale transfer pricing (hub tool defaults)

Live per-square-inch tiers (editable in Transfer Orders → Settings):

| Total sq in | Rate | Label |
| --- | --- | --- |
| 0+ | $0.03 / sq in | Standard |
| 1,000+ | $0.025 / sq in | Volume |
| 5,000+ | $0.02 / sq in | Wholesale |

- Shipping default: **$8.50** flat, **free at $75** subtotal.
- Max film width: **30 inches**.
- Art is sized at **300 dpi**.
- Default fulfillment on partner orders: white-label / blind ship on.

Size presets used in the portal: Mini 2×2, Small 3×3, Pocket 4×4, Youth 6×6, Medium 8×8, Standard front 10×10, Adult front 11×11, Large front 11×14, Oversized 12×17, Jumbo 15×20.

Partners can paste a `dtfs.order.v1` JSON payload instead of forwarding Shopify emails. Shop inbox moves jobs **New → In print → Shipped**.

Artwork: URL (Shopify CDN, Dropbox, Drive) or a dropped PNG that auto-sizes at 300 dpi.

## Printavo DTF tickets

- Use the **DTF first-location** matrix for the first DTF imprint.
- Use the **DTF additional-location** matrix for extra locations.
- Enter style numbers and let SanMar / S&S populate garments when Shirt Co is decorating blanks.
- Nickname pattern still includes method + job + piece count.

## Art for DTF

Prefer real print-ready files, not screenshots. The Shirt.co DTF path uses a 300 dpi art check. Low-res uploads should be flagged, not silently printed.
