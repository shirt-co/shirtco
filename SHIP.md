# How we ship a Shirt Co hub tool (non-dev playbook)

One page. No git required for Audrey, Steve, or anyone else.

## What this is

All internal tools live in one public GitHub repo and publish automatically:

- Hub: https://shirt-co.github.io/shirtco/
- Company Brain: https://shirt-co.github.io/shirtco/knowledge/
- Repo: https://github.com/shirt-co/shirtco

Cursor / Grok Bot builds the code. GitHub Pages publishes it when `main` updates. You never need Terminal.

## Who does what

| Role | Does |
|------|------|
| Anyone on the team | Describes the change in plain English |
| Cursor cloud agent or Grok Bot | Builds it on a branch and opens a Pull Request (PR) |
| Connor (or a named Approver) | Clicks **Merge** after a quick look |
| GitHub Pages | Goes live in a few minutes. No extra deploy button |

## Ship a change (everyday)

1. Message Connor’s Wiffle chat, or open Cursor on the `shirt-co/shirtco` repo and say what you want.
   Example: “On Supply Kanban, add a column for On hold and show it on phone.”
2. Wait for a PR link. Open it. Click the preview if there is one, or open the live tool folder after merge.
3. If it looks right, reply “merge” (or click **Merge pull request** yourself if you have access).
4. Refresh the hub URL in about 1–2 minutes. Done.

## Ship a brand-new tool

1. Name it in one sentence (who uses it, what it replaces).
2. Ask the bot to create a new folder (`toolname/`) with `index.html`, wire a card on the hub home, and open a PR.
3. Review + merge same as above.
4. Share the new URL with the shop: `https://shirt-co.github.io/shirtco/toolname/`

## Test without breaking live

- Prefer a PR. Do not edit `main` by hand in the GitHub website unless it is a one-line typo and Connor says ok.
- Transfer pricing: bot can run `node transfers/pricing.test.js` before merge.
- Company Brain: bot can run `python3 knowledge/server/test_brain.py` before merge.
- Supply QR labels: after a live change that edits item fields, reprint labels from the production `/supplies/` URL.

## Rules (keep it simple)

- No passwords, API keys, customer lists, handbook text, or Printavo logins in the repo. It is **public**. Company Brain private files stay in `knowledge/private/` on the Mac Studio.
- One tool per folder. Do not rewrite another team’s tool without pinging them.
- Prefer small changes. One PR = one idea.
- If something breaks live, say so in the Wiffle chat. Rollback = revert the PR (bot can do that).

## Access for Audrey, Steve, and others

**Default (easiest):** no GitHub login. Ask Wiffle / Cursor → PR → Connor merges.

**Optional (faster):** Join org `shirt-co` team `hub-publishers` (**Write**) and connect Cursor to that GitHub account. Cursor opens `shirt-co/shirtco`. Then you can merge your own PRs after a self-check. Still no Terminal.

## One-line ask templates

- Fix: “Bug on Transfer Orders: [what happens] when [action]. Want [correct behavior].”
- Change: “On [tool], change [X] to [Y]. Keep [Z] the same.”
- New: “New hub tool: [name]. For [who]. Should do [3 bullets]. Put a Planning card on the hub until it’s live.”
