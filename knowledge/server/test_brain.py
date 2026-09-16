#!/usr/bin/env python3
"""Tests for Shirt Co knowledge search — no Ollama required."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import lib
import mcp_server


class CorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.docs = lib.load_documents(include_private=False)
        self.ids = {doc["id"] for doc in self.docs}

    def test_public_corpus_has_core_topics(self) -> None:
        expected = {
            "company",
            "tools",
            "printavo-order-entry",
            "dtf-transfers",
            "contract-decoration",
            "agent-rules",
            "shipping",
            "glossary",
        }
        missing = expected - self.ids
        self.assertFalse(missing, f"Missing public docs: {missing}")

    def test_no_private_customer_examples_in_public_corpus(self) -> None:
        joined = "\n".join(doc["body"] for doc in self.docs).lower()
        banned = ["jharper@", "phillyward25", "lakeprinting", "679783", "7273771"]
        for token in banned:
            self.assertNotIn(token, joined)

    def test_catalog_matches_public_docs(self) -> None:
        catalog = lib.catalog_payload(self.docs)
        self.assertEqual(catalog["doc_count"], len(self.docs))
        self.assertTrue(catalog["categories"])


class SearchTests(unittest.TestCase):
    def test_dtf_pricing_search(self) -> None:
        hits = lib.search_chunks("DTF transfer pricing per square inch", include_private=False)
        self.assertTrue(hits)
        self.assertTrue(any("dtf" in hit["doc_id"] or "dtf" in hit["path"] for hit in hits[:3]))
        blob = " ".join(hit["text"].lower() for hit in hits[:3])
        self.assertTrue("0.03" in blob or "square inch" in blob)

    def test_printavo_guardrails_search(self) -> None:
        hits = lib.search_chunks("Billy must never email the customer or charge a card", include_private=False)
        self.assertTrue(hits)
        blob = " ".join(hit["text"].lower() for hit in hits[:4])
        self.assertTrue("email" in blob or "charge" in blob)
        self.assertTrue(any("printavo" in hit["doc_id"] or "agent" in hit["doc_id"] for hit in hits[:4]))

    def test_status_change_guardrail_ranks_agent_rules(self) -> None:
        hits = lib.search_chunks("never change Printavo status", include_private=False)
        self.assertTrue(hits)
        top = " ".join(hit["text"].lower() for hit in hits[:2])
        self.assertTrue("status" in top)
        self.assertTrue(any(hit["doc_id"] in {"agent-rules", "printavo-order-entry", "contract-decoration"} for hit in hits[:2]))

    def test_blind_ship_search(self) -> None:
        hits = lib.search_chunks("blind ship packing slip contract customer", include_private=False)
        self.assertTrue(hits)
        self.assertTrue(any("contract" in hit["doc_id"] or "shipping" in hit["doc_id"] for hit in hits[:3]))

    def test_category_filter(self) -> None:
        hits = lib.search_chunks("pricing", category="dtf", include_private=False)
        self.assertTrue(hits)
        self.assertTrue(all(hit["category"] == "dtf" for hit in hits))

    def test_chunks_split_on_headings(self) -> None:
        docs = [doc for doc in lib.load_documents(include_private=False) if doc["id"] == "printavo-order-entry"]
        self.assertTrue(docs)
        chunks = lib.chunk_document(docs[0])
        headings = {chunk["heading"] for chunk in chunks}
        self.assertGreater(len(chunks), 3)
        self.assertTrue(any("guardrail" in heading.lower() or "never" in heading.lower() for heading in headings) or len(headings) > 2)

    def test_chunk_ids_are_unique(self) -> None:
        chunks = lib.build_chunks(include_private=False)
        ids = [chunk["id"] for chunk in chunks]
        self.assertEqual(len(ids), len(set(ids)))


class McpTests(unittest.TestCase):
    def test_initialize_and_tools(self) -> None:
        init = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        self.assertEqual(init["result"]["serverInfo"]["name"], "shirtco-knowledge")
        listed = mcp_server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        names = {tool["name"] for tool in listed["result"]["tools"]}
        self.assertEqual(names, {"search_shirtco", "get_shirtco_doc", "list_shirtco_docs", "answer_shirtco"})

    def test_search_tool(self) -> None:
        reply = mcp_server.handle(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "search_shirtco", "arguments": {"query": "supply kanban QR reorder"}},
            }
        )
        text = reply["result"]["content"][0]["text"]
        hits = json.loads(text)
        self.assertTrue(hits)
        self.assertTrue(any("supply" in hit["doc_id"] or "tool" in hit["doc_id"] for hit in hits[:3]))


if __name__ == "__main__":
    unittest.main()
