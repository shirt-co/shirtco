#!/usr/bin/env python3
"""MCP server so Cursor agents on the Mac Studio can query Shirt Co knowledge."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import brain
import lib

PROTOCOL = "2024-11-05"
TOOLS = [
    {
        "name": "search_shirtco",
        "description": (
            "Search Shirt Co company knowledge (how the shop works, tools, Printavo, "
            "DTF, contract decoration, shipping, agent rules). Use before answering "
            "Shirt Co process questions."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language search query"},
                "category": {
                    "type": "string",
                    "description": "Optional category filter such as printavo, dtf, agents, shipping",
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 8},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_shirtco_doc",
        "description": "Load one Shirt Co knowledge document by id.",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "required": ["id"],
        },
    },
    {
        "name": "list_shirtco_docs",
        "description": "List Shirt Co knowledge documents and categories.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "answer_shirtco",
        "description": (
            "Answer a Shirt Co question from company docs. Uses the Mac Studio local "
            "model when Ollama is running; otherwise returns retrieved passages."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"question": {"type": "string"}},
            "required": ["question"],
        },
    },
]


def _text(payload: Any) -> dict[str, Any]:
    text = payload if isinstance(payload, str) else json.dumps(payload, indent=2)
    return {"content": [{"type": "text", "text": text}]}


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "search_shirtco":
        hits = brain._search(
            str(arguments.get("query") or ""),
            arguments.get("category"),
            int(arguments.get("limit") or 8),
            include_private=True,
        )
        return _text(hits)
    if name == "get_shirtco_doc":
        doc_id = str(arguments.get("id") or "")
        for doc in lib.load_documents(include_private=True):
            if doc["id"] == doc_id:
                return _text({k: v for k, v in doc.items() if k != "abs_path"})
        return {"isError": True, "content": [{"type": "text", "text": f"Document not found: {doc_id}"}]}
    if name == "list_shirtco_docs":
        return _text(lib.catalog_payload(lib.load_documents(include_private=True)))
    if name == "answer_shirtco":
        return _text(brain.answer_question(str(arguments.get("question") or ""), include_private=True))
    return {"isError": True, "content": [{"type": "text", "text": f"Unknown tool: {name}"}]}


def handle(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    msg_id = message.get("id")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": PROTOCOL,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "shirtco-knowledge", "version": "1.0.0"},
            },
        }
    if method == "notifications/initialized" or method == "initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = message.get("params") or {}
        result = call_tool(str(params.get("name") or ""), params.get("arguments") or {})
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
    if msg_id is None:
        return None
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        reply = handle(message)
        if reply is not None:
            sys.stdout.write(json.dumps(reply) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
