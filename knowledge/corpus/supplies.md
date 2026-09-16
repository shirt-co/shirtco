---
id: supplies
title: Supply Kanban
category: supplies
audience: shop
visibility: public
updated: 2026-09-16
summary: QR-powered supply reordering for the shop floor.
tags: [kanban, qr, shop]
---

# Supply Kanban

Phone-scannable kanban for workplace supplies. Live at `/supplies/`.

1. Add supplies in **Catalog**.
2. Print QR labels for bins and shelf faces.
3. Scan with a phone and request a reorder.
4. Track **On shelf → Needs reorder → On order**, then mark received.

QR codes embed item details, so phones do not need a shared login. Board state currently lives in each browser's `localStorage`. Cross-device reorders travel by email until a shared backend exists.

Set the purchasing email under Settings. After a live change that edits item fields, reprint labels from the production `/supplies/` URL so the QR payload stays current.

The first load seeds sample supplies so the workflow can be tested. Reset from Settings.
