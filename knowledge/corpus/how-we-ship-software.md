---
id: how-we-ship-software
title: How Shirt Co ships internal software
category: tools
audience: everyone
visibility: public
updated: 2026-09-16
summary: Non-dev playbook for changing hub tools without git.
tags: [github, hub, ship]
---

# How Shirt Co ships internal software

All internal tools live in one public GitHub repo: `shirt-co/shirtco`. GitHub Pages publishes when `main` updates.

## Who does what

| Role | Does |
| --- | --- |
| Anyone on the team | Describes the change in plain English |
| Cursor cloud agent or Grok Bot | Builds it on a branch and opens a Pull Request |
| Connor (or a named Approver) | Clicks Merge after a quick look |
| GitHub Pages | Goes live in a few minutes |

## Everyday change

1. Message Connor's Wiffle chat, or open Cursor on `shirt-co/shirtco` and say what you want.
2. Wait for a PR link. Preview it.
3. If it looks right, reply "merge" or merge it yourself if you have access.
4. Refresh the hub URL in about 1–2 minutes.

## Rules

- No passwords, API keys, customer lists, or Printavo logins in the repo. It is **public**.
- One tool per folder. Do not rewrite another team's tool without pinging them.
- Prefer small changes. One PR = one idea.
- If something breaks live, say so. Rollback = revert the PR.

Full playbook: `SHIP.md` in the repo root.
