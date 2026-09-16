---
id: sources-to-ingest
title: Private sources to ingest on the Mac Studio
category: tools
audience: ops
visibility: public
updated: 2026-09-16
summary: Drive documents that belong in private knowledge — listed by name, not copied here.
tags: [ingest, drive]
---

# Private sources to ingest on the Mac Studio

Copy these into `knowledge/private/` (or export text next to this list) and run `python3 knowledge/server/brain.py index --embed`.

Do **not** commit the files. The public repo only stores this shopping list.

## Highest value

| Title | Why |
| --- | --- |
| Handbook - Updated January 2026.pdf | Employee policy source of truth |
| Billy Printavo Order Entry SOP | Living SOP with training examples (contains customer PII — private) |
| Vendor List | Purchasing contacts |
| DTFS Pricing and Printavo Matrix | DTF matrix details beyond public hub defaults |
| Shirt.Co DTF vs Screen Production Study | When to choose DTF vs screen |
| Shirt.Co Contact Cheat Sheets | Sales outreach coaching — customer PII, keep private |
| Monthly Meeting Agenda - Running Doc | Current ops decisions |
| Company Meeting notes | Recent shop-wide context |

Google Drive already holds these on Connor's account. Dropbox can be added the same way after MCP/auth is connected.

## How to ingest

1. Export or download as markdown, text, or PDF into `knowledge/private/<folder>/`.
2. Add YAML frontmatter if you want category/tags (`visibility: private`).
3. `python3 knowledge/server/brain.py index --embed`
4. Search: `python3 knowledge/server/brain.py search "PTO after one year"` (handbook) or `"contract screen fee"`.

A starter map with Drive file ids lives in `knowledge/sources.json`.
