#!/usr/bin/env python3
"""Shirt Co knowledge corpus: load, chunk, and search markdown files."""

from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"
CORPUS_DIR = KNOWLEDGE_ROOT / "corpus"
PRIVATE_DIR = KNOWLEDGE_ROOT / "private"
INDEX_DIR = KNOWLEDGE_ROOT / ".index"
CATALOG_PATH = KNOWLEDGE_ROOT / "catalog.json"

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+.#/-]*", re.I)
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.M)
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text or "") if token.lower() not in STOPWORDS]


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_RE.match(text.strip() + ("\n" if not text.endswith("\n") else ""))
    if not match:
        return {}, text
    meta: dict[str, Any] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed = value.strip().strip('"').strip("'")
        if parsed.startswith("[") and parsed.endswith("]"):
            inner = parsed[1:-1].strip()
            meta[key.strip()] = [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]
        else:
            meta[key.strip()] = parsed
    return meta, match.group(2).lstrip("\n")


def slug_from_path(path: Path, root: Path) -> str:
    relative = path.relative_to(root).with_suffix("")
    return str(relative).replace(os.sep, "/")


def iter_markdown(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*.md") if path.name != "README.md" or root != PRIVATE_DIR)


def load_documents(include_private: bool = True) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    sources = [(CORPUS_DIR, "public")]
    if include_private:
        sources.append((PRIVATE_DIR, "private"))

    for root, default_visibility in sources:
        for path in iter_markdown(root):
            if root == PRIVATE_DIR and path.name == "README.md":
                continue
            text = path.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(text)
            visibility = str(meta.get("visibility") or default_visibility)
            doc_id = str(meta.get("id") or slug_from_path(path, root))
            rel = path.relative_to(KNOWLEDGE_ROOT).as_posix()
            docs.append(
                {
                    "id": doc_id,
                    "path": rel,
                    "abs_path": str(path),
                    "title": str(meta.get("title") or path.stem.replace("-", " ").title()),
                    "category": str(meta.get("category") or "general"),
                    "audience": str(meta.get("audience") or "everyone"),
                    "visibility": visibility,
                    "updated": str(meta.get("updated") or ""),
                    "summary": str(meta.get("summary") or ""),
                    "tags": meta.get("tags") if isinstance(meta.get("tags"), list) else [],
                    "body": body,
                    "text": f"{meta.get('title', '')}\n{body}",
                }
            )
    docs.sort(key=lambda doc: (doc["category"], doc["title"]))
    return docs


def chunk_document(doc: dict[str, Any], max_chars: int = 1400) -> list[dict[str, Any]]:
    body = doc["body"]
    headings = list(HEADING_RE.finditer(body))
    sections: list[tuple[str, str]] = []
    if not headings:
        sections.append((doc["title"], body))
    else:
        if headings[0].start() > 0:
            preamble = body[: headings[0].start()].strip()
            if preamble:
                sections.append((doc["title"], preamble))
        for index, heading in enumerate(headings):
            end = headings[index + 1].start() if index + 1 < len(headings) else len(body)
            title = heading.group(2).strip()
            content = body[heading.end() : end].strip()
            sections.append((title, f"{heading.group(0)}\n{content}".strip()))

    chunks: list[dict[str, Any]] = []
    for heading, content in sections:
        if not content.strip():
            continue
        if len(content) <= max_chars:
            pieces = [content]
        else:
            pieces = []
            paragraphs = re.split(r"\n\s*\n", content)
            current = ""
            for paragraph in paragraphs:
                candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
                if len(candidate) > max_chars and current:
                    pieces.append(current)
                    current = paragraph
                else:
                    current = candidate
            if current:
                pieces.append(current)
        for offset, piece in enumerate(pieces):
            chunks.append(
                {
                    "id": f"{doc['id']}#{len(chunks)}",
                    "doc_id": doc["id"],
                    "title": doc["title"],
                    "heading": heading,
                    "category": doc["category"],
                    "visibility": doc["visibility"],
                    "path": doc["path"],
                    "text": piece,
                }
            )
    return chunks


def build_chunks(docs: list[dict[str, Any]] | None = None, include_private: bool = True) -> list[dict[str, Any]]:
    documents = docs if docs is not None else load_documents(include_private=include_private)
    chunks: list[dict[str, Any]] = []
    for doc in documents:
        chunks.extend(chunk_document(doc))
    return chunks


def _idf(df: int, n_docs: int) -> float:
    return math.log((n_docs - df + 0.5) / (df + 0.5) + 1)


def search_chunks(
    query: str,
    chunks: list[dict[str, Any]] | None = None,
    category: str | None = None,
    limit: int = 8,
    include_private: bool = True,
) -> list[dict[str, Any]]:
    haystack = chunks if chunks is not None else build_chunks(include_private=include_private)
    if category:
        haystack = [chunk for chunk in haystack if chunk["category"] == category]
    query_tokens = tokenize(query)
    if not query_tokens or not haystack:
        return []

    df: dict[str, int] = {}
    tokenized = []
    for chunk in haystack:
        tokens = tokenize(f"{chunk['title']} {chunk['heading']} {chunk['text']}")
        tokenized.append(tokens)
        seen = set(tokens)
        for token in seen:
            df[token] = df.get(token, 0) + 1

    n_docs = len(haystack)
    scored: list[tuple[float, int]] = []
    for index, tokens in enumerate(tokenized):
        tf: dict[str, int] = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        score = 0.0
        heading_tokens = set(tokenize(haystack[index]["heading"] + " " + haystack[index]["title"]))
        for token in query_tokens:
            if token not in tf:
                continue
            freq = tf[token]
            denom = freq + 1.2 * (0.25 + 0.75)
            bm25 = _idf(df.get(token, 0), n_docs) * (freq * 2.2) / denom
            if token in heading_tokens:
                bm25 *= 1.8
            score += bm25
        matched = sum(1 for token in query_tokens if token in tf)
        if matched:
            score *= 0.55 + (0.9 * matched / len(query_tokens))
        if score > 0:
            scored.append((score, index))

    scored.sort(key=lambda item: item[0], reverse=True)
    results = []
    for score, index in scored[: max(1, limit)]:
        chunk = dict(haystack[index])
        snippet = re.sub(r"\s+", " ", chunk["text"]).strip()
        chunk["score"] = round(score, 4)
        chunk["snippet"] = snippet[:420]
        results.append(chunk)
    return results


def cosine(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    norm_l = math.sqrt(sum(a * a for a in left))
    norm_r = math.sqrt(sum(b * b for b in right))
    if norm_l == 0 or norm_r == 0:
        return 0.0
    return dot / (norm_l * norm_r)


def hybrid_search(
    query: str,
    embeddings: dict[str, list[float]] | None = None,
    query_embedding: list[float] | None = None,
    category: str | None = None,
    limit: int = 8,
    include_private: bool = True,
) -> list[dict[str, Any]]:
    chunks = build_chunks(include_private=include_private)
    lexical = {item["id"]: item for item in search_chunks(query, chunks, category=category, limit=24)}
    if not embeddings or not query_embedding:
        return sorted(lexical.values(), key=lambda item: item["score"], reverse=True)[:limit]

    scored = []
    for chunk in chunks:
        if category and chunk["category"] != category:
            continue
        vector = embeddings.get(chunk["id"])
        if not vector:
            continue
        vector_score = cosine(query_embedding, vector)
        lex_score = lexical.get(chunk["id"], {}).get("score", 0.0)
        combined = (0.62 * vector_score) + (0.38 * (lex_score / 10.0))
        if chunk["id"] in lexical:
            combined += 0.08
        if combined <= 0:
            continue
        item = dict(chunk)
        item["score"] = round(combined, 4)
        item["snippet"] = re.sub(r"\s+", " ", chunk["text"]).strip()[:420]
        scored.append(item)
    scored.sort(key=lambda item: item["score"], reverse=True)
    if scored:
        return scored[:limit]
    return list(lexical.values())[:limit]


def catalog_payload(docs: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    documents = docs if docs is not None else load_documents(include_private=False)
    categories: dict[str, int] = {}
    entries = []
    for doc in documents:
        categories[doc["category"]] = categories.get(doc["category"], 0) + 1
        entries.append(
            {
                "id": doc["id"],
                "title": doc["title"],
                "category": doc["category"],
                "audience": doc["audience"],
                "visibility": doc["visibility"],
                "updated": doc["updated"],
                "summary": doc["summary"] or first_sentence(doc["body"]),
                "tags": doc["tags"],
                "path": doc["path"],
            }
        )
    return {
        "name": "Shirt Co Company Brain",
        "visibility": "public-safe corpus; private docs stay on the Mac Studio",
        "doc_count": len(entries),
        "categories": categories,
        "docs": entries,
    }


def first_sentence(body: str) -> str:
    plain = re.sub(r"[#*_`>]", "", body).strip()
    plain = re.sub(r"\s+", " ", plain)
    match = re.split(r"(?<=[.!?])\s+", plain, maxsplit=1)
    return (match[0] if match else plain)[:220]


def write_catalog(path: Path | None = None) -> Path:
    target = path or CATALOG_PATH
    payload = catalog_payload()
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return target


def save_index(chunks: list[dict[str, Any]], embeddings: dict[str, list[float]] | None = None) -> Path:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"chunks": chunks, "embeddings": embeddings or {}}
    target = INDEX_DIR / "index.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


def load_index() -> dict[str, Any] | None:
    target = INDEX_DIR / "index.json"
    if not target.exists():
        return None
    return json.loads(target.read_text(encoding="utf-8"))
