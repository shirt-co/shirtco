#!/usr/bin/env python3
"""Shirt Co company brain CLI: index, search, serve, and answer from local docs."""

from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import lib
import ollama_client


def cmd_catalog(_: argparse.Namespace) -> int:
    path = lib.write_catalog()
    print(f"Wrote {path}")
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    chunks = lib.build_chunks(include_private=True)
    embeddings = {}
    if args.embed:
        if not ollama_client.available():
            print("Ollama is not running. Start it, then re-run with --embed.", file=sys.stderr)
            return 1
        print(f"Embedding {len(chunks)} chunks with {ollama_client.EMBED_MODEL}...")
        for chunk in chunks:
            embeddings[chunk["id"]] = ollama_client.embed(f"{chunk['title']}\n{chunk['heading']}\n{chunk['text']}")
    path = lib.save_index(chunks, embeddings)
    lib.write_catalog()
    print(f"Indexed {len(chunks)} chunks at {path}")
    if embeddings:
        print(f"Stored {len(embeddings)} embeddings.")
    else:
        print("Keyword index only. Pass --embed when Ollama is running for semantic search.")
    return 0


def _search(query: str, category: str | None, limit: int, include_private: bool) -> list[dict[str, Any]]:
    stored = lib.load_index()
    embeddings = (stored or {}).get("embeddings") or {}
    query_embedding = None
    if embeddings and ollama_client.available():
        try:
            query_embedding = ollama_client.embed(query)
        except ollama_client.OllamaError:
            query_embedding = None
    return lib.hybrid_search(
        query,
        embeddings=embeddings or None,
        query_embedding=query_embedding,
        category=category,
        limit=limit,
        include_private=include_private,
    )


def cmd_search(args: argparse.Namespace) -> int:
    hits = _search(args.query, args.category, args.limit, include_private=not args.public_only)
    print(json.dumps(hits, indent=2))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    docs = lib.load_documents(include_private=not args.public_only)
    payload = [
        {
            "id": doc["id"],
            "title": doc["title"],
            "category": doc["category"],
            "visibility": doc["visibility"],
            "path": doc["path"],
        }
        for doc in docs
    ]
    print(json.dumps(payload, indent=2))
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    docs = lib.load_documents(include_private=True)
    for doc in docs:
        if doc["id"] == args.doc_id:
            print(json.dumps({k: v for k, v in doc.items() if k != "abs_path"}, indent=2))
            return 0
    print(f"Document not found: {args.doc_id}", file=sys.stderr)
    return 1


def format_context(hits: list[dict[str, Any]]) -> str:
    blocks = []
    for hit in hits:
        blocks.append(
            f"### {hit['title']} — {hit['heading']}\nSource: {hit['path']}\n\n{hit['text']}"
        )
    return "\n\n".join(blocks)


def answer_question(question: str, include_private: bool = True) -> dict[str, Any]:
    hits = _search(question, None, 6, include_private=include_private)
    context = format_context(hits)
    if ollama_client.available():
        prompt = (
            f"Question: {question}\n\n"
            f"Shirt Co documents:\n{context}\n\n"
            "Answer using only those documents. If they are incomplete, say what is missing."
        )
        try:
            answer = ollama_client.chat(prompt)
            mode = "local-llm"
        except ollama_client.OllamaError as exc:
            answer = (
                f"Local model is not answering ({exc}). Retrieved Shirt Co passages instead:\n\n{context}"
            )
            mode = "retrieval-fallback"
    else:
        if not hits:
            answer = "No Shirt Co documents matched that question."
        else:
            top = hits[0]
            answer = (
                f"Ollama is not running, so this is retrieved Shirt Co text rather than a model answer.\n\n"
                f"From {top['title']} ({top['heading']}):\n\n{top['text']}"
            )
        mode = "retrieval"
    return {"answer": answer, "mode": mode, "sources": hits}


def cmd_answer(args: argparse.Namespace) -> int:
    print(json.dumps(answer_question(args.question, include_private=not args.public_only), indent=2))
    return 0


class BrainHandler(BaseHTTPRequestHandler):
    server_version = "ShirtCoBrain/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))

    def _send(self, status: int, payload: Any, origin: str | None = None) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        allow_origin = origin if self._origin_ok(origin) else "*"
        self.send_header("Access-Control-Allow-Origin", allow_origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _origin_ok(self, origin: str | None) -> bool:
        if not origin:
            return False
        return (
            origin.startswith("http://localhost")
            or origin.startswith("http://127.0.0.1")
            or "github.io" in origin
            or origin.endswith("shirt.co")
        )

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send(204, {})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        origin = self.headers.get("Origin")
        if parsed.path in ("/health", "/"):
            self._send(
                200,
                {
                    "ok": True,
                    "name": "Shirt Co Company Brain",
                    "ollama": ollama_client.available(),
                    "embed_model": ollama_client.EMBED_MODEL,
                    "chat_model": ollama_client.CHAT_MODEL,
                    "docs": len(lib.load_documents(include_private=True)),
                },
                origin,
            )
            return
        if parsed.path == "/search":
            q = (query.get("q") or [""])[0]
            category = (query.get("category") or [None])[0]
            limit = int((query.get("limit") or ["8"])[0])
            hits = _search(q, category, limit, include_private=True)
            self._send(200, {"query": q, "results": hits}, origin)
            return
        if parsed.path == "/docs":
            docs = lib.load_documents(include_private=True)
            self._send(
                200,
                [
                    {
                        "id": doc["id"],
                        "title": doc["title"],
                        "category": doc["category"],
                        "visibility": doc["visibility"],
                        "summary": doc["summary"] or lib.first_sentence(doc["body"]),
                        "path": doc["path"],
                    }
                    for doc in docs
                ],
                origin,
            )
            return
        if parsed.path.startswith("/docs/"):
            doc_id = parsed.path.split("/docs/", 1)[1]
            for doc in lib.load_documents(include_private=True):
                if doc["id"] == doc_id:
                    self._send(200, {k: v for k, v in doc.items() if k != "abs_path"}, origin)
                    return
            self._send(404, {"error": "not found"}, origin)
            return
        self._send(404, {"error": "not found"}, origin)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        origin = self.headers.get("Origin")
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send(400, {"error": "invalid json"}, origin)
            return
        if parsed.path == "/answer":
            question = str(payload.get("question") or payload.get("q") or "").strip()
            if not question:
                self._send(400, {"error": "question is required"}, origin)
                return
            self._send(200, answer_question(question, include_private=True), origin)
            return
        if parsed.path == "/search":
            hits = _search(
                str(payload.get("query") or ""),
                payload.get("category"),
                int(payload.get("limit") or 8),
                include_private=True,
            )
            self._send(200, {"results": hits}, origin)
            return
        self._send(404, {"error": "not found"}, origin)


def cmd_serve(args: argparse.Namespace) -> int:
    host = args.host
    port = args.port
    server = ThreadingHTTPServer((host, port), BrainHandler)
    print(f"Shirt Co brain listening on http://{host}:{port}")
    print("Agents: search GET /search?q=...  answer POST /answer")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Shirt Co company brain")
    sub = parser.add_subparsers(dest="command", required=True)

    catalog = sub.add_parser("catalog", help="Write public catalog.json for the hub UI")
    catalog.set_defaults(func=cmd_catalog)

    index = sub.add_parser("index", help="Build the local search index")
    index.add_argument("--embed", action="store_true", help="Create Ollama embeddings")
    index.set_defaults(func=cmd_index)

    search = sub.add_parser("search", help="Search Shirt Co knowledge")
    search.add_argument("query")
    search.add_argument("--category")
    search.add_argument("--limit", type=int, default=8)
    search.add_argument("--public-only", action="store_true")
    search.set_defaults(func=cmd_search)

    listing = sub.add_parser("list", help="List documents")
    listing.add_argument("--public-only", action="store_true")
    listing.set_defaults(func=cmd_list)

    get_doc = sub.add_parser("get", help="Print one document")
    get_doc.add_argument("doc_id")
    get_doc.set_defaults(func=cmd_get)

    answer = sub.add_parser("answer", help="Retrieve (and optionally ask the local model)")
    answer.add_argument("question")
    answer.add_argument("--public-only", action="store_true")
    answer.set_defaults(func=cmd_answer)

    serve = sub.add_parser("serve", help="HTTP API for the hub UI and local agents")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8787)
    serve.set_defaults(func=cmd_serve)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
