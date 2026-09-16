# Private Shirt Co knowledge

This folder is gitignored except for this README.

Put the real company database here on the **Mac Studio**:

- Employee handbook
- Vendor list and account numbers
- Printavo SOPs that include customer examples
- Sales cheat sheets
- Meeting notes you do not want public
- Anything with emails, phones, prices that are not already on the public hub

## Frontmatter (optional but useful)

```md
---
id: handbook-2026
title: Employee Handbook January 2026
category: policies
audience: everyone
visibility: private
updated: 2026-01-01
---
```

Then from the repo root:

```bash
python3 knowledge/server/brain.py index --embed
python3 knowledge/server/brain.py search "who do I call for HR"
```

See `knowledge/sources.json` for Drive files Connor already has.
