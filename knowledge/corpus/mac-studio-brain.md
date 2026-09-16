---
id: mac-studio-brain
title: Mac Studio company brain
category: tools
audience: agents, ops
visibility: public
updated: 2026-09-16
summary: How the local model on Connor's Mac Studio holds Shirt Co knowledge for agents.
tags: [ollama, mcp, rag]
---

# Mac Studio company brain

The searchable source of truth for "how Shirt Co works" is markdown in this repo plus **private files that never leave the Mac Studio**.

## Layout

```text
knowledge/
  corpus/             Public-safe docs (this GitHub repo)
  private/            Local only — handbook, vendor list, customer cheat sheets
  catalog.json        Index of public docs for the hub UI
  server/             Search, HTTP API, MCP server (Python, no extra packages)
```

## Local model

On the Mac Studio, [Ollama](https://ollama.com) runs:

- **nomic-embed-text** — embeddings for semantic search
- A chat model (8B–32B depending on unified memory) — answers grounded in retrieved docs

Search still works **without** Ollama (keyword / BM25-style). Embeddings and spoken answers are the upgrade.

## How agents access it

| Agent | How |
| --- | --- |
| Cursor on the Mac Studio | MCP server `knowledge/server/mcp_server.py` — tools `search_shirtco`, `get_shirtco_doc`, `answer_shirtco` |
| Hub in a browser on the Mac | UI talks to `http://127.0.0.1:8787` when the brain is serving |
| Cloud agents / GitHub Pages | Public `corpus/` + `catalog.json` only. They cannot see `knowledge/private/` |
| Future remote agents | Point them at the Mac over Tailscale and bind the HTTP API to that interface |

## Commands

```bash
python3 knowledge/server/brain.py catalog
python3 knowledge/server/test_brain.py
python3 knowledge/server/brain.py search "blind ship packing slip"
python3 knowledge/server/brain.py serve          # http://127.0.0.1:8787
python3 knowledge/server/brain.py index --embed  # requires Ollama
```

Setup: `knowledge/scripts/setup-mac-studio.sh`.
