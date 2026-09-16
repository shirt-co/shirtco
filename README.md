# Shirt Co Projects

One repository and GitHub Pages site for Shirt Co's internal software.

## How the team ships changes

You do not need git or Terminal. The full playbook is in [SHIP.md](SHIP.md).

- Describe the change in plain English (Wiffle chat or Cursor).
- A bot opens a Pull Request; Connor (or a named Approver) merges after a quick look.
- GitHub Pages publishes the hub in a few minutes. No extra deploy button.
- Rules, new-tool steps, and ask templates live in the ship playbook.

## Project structure

```text
shirtco/
├── index.html         # Project hub
├── hub.css            # Shared hub/planning-page styles
├── SHIP.md            # Non-dev ship playbook
├── transfers/         # Live DTF transfer order portal
├── supplies/          # Live QR supply kanban
├── quotes/            # Quoting tool planning space
├── art/               # Art tracker planning space
└── knowledge/         # Company brain (search + Mac Studio local model)
```

Production URLs:

- Hub: `https://shirt-co.github.io/shirtco/`
- Transfer Orders: `https://shirt-co.github.io/shirtco/transfers/`
- Supply Kanban: `https://shirt-co.github.io/shirtco/supplies/`
- Quoting Tool: `https://shirt-co.github.io/shirtco/quotes/`
- Art Tracker: `https://shirt-co.github.io/shirtco/art/`
- Company Brain: `https://shirt-co.github.io/shirtco/knowledge/`

Each tool owns its folder and can evolve independently. Add another tool by creating a new folder with an `index.html`, then add its card to the root hub.

## Transfer Orders

Partner and customer DTF ordering without the email back-and-forth:

1. Build an order by transfer size and quantity (gang sheets are assembled in production).
2. Live wholesale pricing at $0.03 / $0.025 / $0.02 per square inch, with free shipping at $75.
3. White-label / blind-ship flags and a packing-slip brand name.
4. Artwork as a URL (Shopify CDN, Dropbox, Drive) or a dropped PNG that auto-sizes at 300 dpi.
5. Shop inbox moves jobs New → In print → Shipped.
6. Partners paste or import a `dtfs.order.v1` JSON payload instead of forwarding Shopify emails.

Rates and the shop notify email are editable under Settings. Pricing math lives in `transfers/pricing.js` and can be checked with `node transfers/pricing.test.js`.

## Supply Kanban

The supply app is a phone-scannable kanban for workplace supplies:

1. Add supplies in **Catalog**.
2. Print QR labels for bins and shelf faces.
3. Scan with a phone and request a reorder.
4. Track **On shelf → Needs reorder → On order**, then mark received.

QR codes embed item details, so phones do not need a shared login. Board state currently lives in each browser's `localStorage`; cross-device reorders travel by email until a shared backend is added.

## Company Brain

Searchable Shirt Co knowledge for employees and AI agents.

- Public process docs live in `knowledge/corpus/` and search from the hub with no login.
- Private files (handbook, vendor list, customer cheat sheets) stay in gitignored `knowledge/private/` on the Mac Studio.
- On the Studio, `knowledge/scripts/setup-mac-studio.sh` wires Ollama + a Cursor MCP server so agents can `search_shirtco` when they need it.

Check retrieval with `python3 knowledge/server/test_brain.py`.

## Run locally

No build step. Serve the repository root:

```bash
python3 -m http.server 8080
```

Visit `http://localhost:8080`. Transfer Orders is at `http://localhost:8080/transfers/`. The Kanban is at `http://localhost:8080/supplies/`.

## Deploy

Works with Netlify Drop, GitHub Pages, or Vercel (static). Config files `netlify.toml` and `vercel.json` are included.

After deploy, open the Supply Kanban, set the purchasing email under Settings, and print fresh labels. QR labels must be printed from the production `/supplies/` URL.

The Kanban's first load seeds sample supplies so the workflow can be tested immediately. Reset anytime from Settings; re-print labels after editing an item so the embedded QR payload stays current.
