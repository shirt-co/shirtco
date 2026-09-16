#!/usr/bin/env bash
# Install the Shirt Co company brain on a Mac Studio (Apple Silicon).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BRAIN="$ROOT/knowledge/server/brain.py"
MCP="$ROOT/knowledge/server/mcp_server.py"

echo "Shirt Co company brain"
echo "Repo: $ROOT"

if ! command -v python3 >/dev/null; then
  echo "Install Python 3 first (it ships with macOS)." >&2
  exit 1
fi

python3 "$BRAIN" catalog
python3 "$ROOT/knowledge/server/test_brain.py"

if ! command -v ollama >/dev/null; then
  echo
  echo "Ollama is not installed."
  echo "Install from https://ollama.com then re-run this script."
  echo "Keyword search already works without it."
else
  echo "Pulling embedding model nomic-embed-text..."
  ollama pull nomic-embed-text

  mem_gb="$(sysctl -n hw.memsize 2>/dev/null || echo 0)"
  mem_gb="$((mem_gb / 1024 / 1024 / 1024))"
  if (( mem_gb >= 64 )); then
    chat_model="${SHIRTCO_CHAT_MODEL:-qwen2.5:32b}"
  elif (( mem_gb >= 36 )); then
    chat_model="${SHIRTCO_CHAT_MODEL:-qwen2.5:14b}"
  else
    chat_model="${SHIRTCO_CHAT_MODEL:-llama3.1:8b}"
  fi
  echo "Pulling chat model $chat_model (detected ~${mem_gb}GB unified memory)..."
  ollama pull "$chat_model"
  export SHIRTCO_CHAT_MODEL="$chat_model"
  python3 "$BRAIN" index --embed
fi

cursor_mcp="$HOME/.cursor/mcp.json"
echo
echo "Add this to $cursor_mcp (merge with any existing mcpServers):"
python3 - <<PY
import json
print(json.dumps({
  "mcpServers": {
    "shirtco-knowledge": {
      "command": "python3",
      "args": ["$MCP"]
    }
  }
}, indent=2))
PY

echo
echo "Start the local API (leave this running for the hub UI on this Mac):"
echo "  python3 \"$BRAIN\" serve"
echo
echo "Then open:"
echo "  https://shirt-co.github.io/shirtco/knowledge/"
echo "  or python3 -m http.server 8080  →  http://localhost:8080/knowledge/"
echo
echo "Drop private files into knowledge/private/ and re-run:"
echo "  python3 \"$BRAIN\" index --embed"
