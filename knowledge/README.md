# Shirt Co Company Brain

Local-first knowledge base for training people and grounding AI agents in how Shirt Co actually works.

## Two layers

1. **Public corpus** (`corpus/`) — process, tools, agent rules. Published on the hub. Safe for a public GitHub repo.
2. **Private corpus** (`private/`, gitignored) — handbook, vendor list, customer cheat sheets. Lives on Connor's Mac Studio. Local Ollama embeddings make it searchable for agents on that machine.

Printavo remains the **order** database. This brain is the **how we operate** database.

## For employees

Open [Company Brain](https://shirt-co.github.io/shirtco/knowledge/) and search. Works on phones. No login.

## For the Mac Studio

```bash
./knowledge/scripts/setup-mac-studio.sh
python3 knowledge/server/brain.py serve
```

That installs/uses [Ollama](https://ollama.com), builds a local index, and prints a Cursor MCP snippet. Cursor on that Mac gets tools:

- `search_shirtco`
- `get_shirtco_doc`
- `list_shirtco_docs`
- `answer_shirtco`

Cloud agents only see the public corpus unless you later expose `127.0.0.1:8787` over Tailscale.

## Commands

```bash
python3 knowledge/server/test_brain.py
python3 knowledge/server/brain.py search "never change Printavo status"
python3 knowledge/server/brain.py answer "How do we price wholesale DTF transfers?"
```

Add private files, then `python3 knowledge/server/brain.py index --embed`. Drive sources are listed in `sources.json`.
