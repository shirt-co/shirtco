(() => {
  const STOP = new Set("a an and are as at be by for from in is it of on or the to with".split(" "));
  const LOCAL_API = "http://127.0.0.1:8787";
  const state = {
    catalog: null,
    docs: new Map(),
    category: "all",
    local: false,
  };

  const $ = (id) => document.getElementById(id);

  function tokens(text) {
    return (String(text || "").toLowerCase().match(/[a-z0-9][a-z0-9+.#/-]*/g) || []).filter((t) => !STOP.has(t));
  }

  function renderMarkdown(src) {
    const escaped = src
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
    const lines = escaped.split("\n");
    const out = [];
    let inCode = false;
    let inTable = false;
    let listType = null;

    const closeList = () => {
      if (listType) {
        out.push(listType === "ol" ? "</ol>" : "</ul>");
        listType = null;
      }
    };

    const closeTable = () => {
      if (inTable) {
        out.push("</tbody></table>");
        inTable = false;
      }
    };

    const inline = (text) =>
      text
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

    for (const line of lines) {
      if (line.startsWith("```")) {
        closeList();
        closeTable();
        if (inCode) {
          out.push("</code></pre>");
          inCode = false;
        } else {
          out.push("<pre><code>");
          inCode = true;
        }
        continue;
      }
      if (inCode) {
        out.push(`${line}\n`);
        continue;
      }
      if (/^\|/.test(line)) {
        closeList();
        if (/---/.test(line)) {
          continue;
        }
        const cells = line.split("|").slice(1, -1).map((cell) => inline(cell.trim()));
        if (!inTable) {
          out.push("<table><tbody>");
          inTable = true;
          out.push(`<tr>${cells.map((cell) => `<th>${cell}</th>`).join("")}</tr>`);
        } else {
          out.push(`<tr>${cells.map((cell) => `<td>${cell}</td>`).join("")}</tr>`);
        }
        continue;
      }
      closeTable();
      if (!line.trim()) {
        closeList();
        continue;
      }
      if (/^### /.test(line)) {
        closeList();
        out.push(`<h3>${inline(line.slice(4))}</h3>`);
        continue;
      }
      if (/^## /.test(line)) {
        closeList();
        out.push(`<h2>${inline(line.slice(3))}</h2>`);
        continue;
      }
      if (/^# /.test(line)) {
        closeList();
        out.push(`<h1>${inline(line.slice(2))}</h1>`);
        continue;
      }
      const ul = line.match(/^[-*]\s+(.*)/);
      if (ul) {
        if (listType !== "ul") {
          closeList();
          out.push("<ul>");
          listType = "ul";
        }
        out.push(`<li>${inline(ul[1])}</li>`);
        continue;
      }
      const ol = line.match(/^\d+\.\s+(.*)/);
      if (ol) {
        if (listType !== "ol") {
          closeList();
          out.push("<ol>");
          listType = "ol";
        }
        out.push(`<li>${inline(ol[1])}</li>`);
        continue;
      }
      closeList();
      out.push(`<p>${inline(line)}</p>`);
    }
    closeList();
    closeTable();
    if (inCode) out.push("</code></pre>");
    return out.join("");
  }

  function stripFrontmatter(text) {
    if (!text.startsWith("---")) return { meta: {}, body: text };
    const end = text.indexOf("\n---", 3);
    if (end === -1) return { meta: {}, body: text };
    const raw = text.slice(4, end);
    const body = text.slice(end + 4).replace(/^\n/, "");
    const meta = {};
    raw.split("\n").forEach((line) => {
      const idx = line.indexOf(":");
      if (idx > 0) meta[line.slice(0, idx).trim()] = line.slice(idx + 1).trim().replace(/^"|"$/g, "");
    });
    return { meta, body };
  }

  function scoreDoc(queryToks, doc) {
    const hay = tokens(`${doc.title} ${doc.category} ${doc.summary} ${doc.body}`);
    const tf = new Map();
    hay.forEach((t) => tf.set(t, (tf.get(t) || 0) + 1));
    let score = 0;
    const titleToks = new Set(tokens(doc.title));
    queryToks.forEach((t) => {
      if (!tf.has(t)) return;
      score += tf.get(t);
      if (titleToks.has(t)) score += 4;
    });
    return score;
  }

  function snippet(body, queryToks) {
    const plain = body.replace(/[#*_`]/g, " ");
    const lower = plain.toLowerCase();
    for (const t of queryToks) {
      const at = lower.indexOf(t);
      if (at >= 0) {
        const start = Math.max(0, at - 80);
        return `${start ? "…" : ""}${plain.slice(start, start + 220).trim()}…`;
      }
    }
    return plain.trim().slice(0, 220) + "…";
  }

  async function loadDoc(entry) {
    if (state.docs.has(entry.id)) return state.docs.get(entry.id);
    const res = await fetch(entry.path);
    const raw = await res.text();
    const parsed = stripFrontmatter(raw);
    const doc = { ...entry, body: parsed.body };
    state.docs.set(entry.id, doc);
    return doc;
  }

  async function localSearch(query) {
    const res = await fetch(`${LOCAL_API}/search?q=${encodeURIComponent(query)}&limit=10`);
    if (!res.ok) throw new Error("local search failed");
    const data = await res.json();
    return data.results || [];
  }

  async function search(query) {
    const q = query.trim();
    const queryToks = tokens(q);
    const resultsEl = $("results");
    $("reader").hidden = true;
    resultsEl.hidden = false;
    if (!q) {
      resultsEl.innerHTML = `<p class="empty">Search how Shirt Co quotes, prints, ships, or uses Printavo.</p>`;
      return;
    }

    let hits = [];
    if (state.local) {
      try {
        hits = (await localSearch(q)).map((hit) => ({
          id: hit.doc_id,
          title: hit.title,
          category: hit.category,
          snippet: hit.snippet,
          heading: hit.heading,
          path: hit.path,
        }));
      } catch {
        state.local = false;
        setStatus();
      }
    }

    if (!hits.length) {
      const docs = [];
      for (const entry of state.catalog.docs) {
        if (state.category !== "all" && entry.category !== state.category) continue;
        docs.push(await loadDoc(entry));
      }
      hits = docs
        .map((doc) => ({ doc, score: scoreDoc(queryToks, doc) }))
        .filter((row) => row.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 10)
        .map(({ doc }) => ({
          id: doc.id,
          title: doc.title,
          category: doc.category,
          snippet: snippet(doc.body, queryToks),
          path: doc.path,
        }));
    } else if (state.category !== "all") {
      hits = hits.filter((hit) => hit.category === state.category);
    }

    if (!hits.length) {
      resultsEl.innerHTML = `<p class="empty">No matches for “${q}”. Try Printavo, DTF, blind ship, or Billy.</p>`;
      return;
    }

    resultsEl.innerHTML = hits
      .map(
        (hit) => `
        <button type="button" class="result-card" data-id="${hit.id}">
          <p class="meta">${hit.category}${hit.heading ? " · " + hit.heading : ""}</p>
          <h3>${hit.title}</h3>
          <p class="snippet">${hit.snippet || ""}</p>
        </button>`
      )
      .join("");
  }

  async function openDoc(id) {
    const entry = state.catalog.docs.find((doc) => doc.id === id);
    if (!entry) return;
    const doc = await loadDoc(entry);
    $("results").hidden = true;
    const reader = $("reader");
    reader.hidden = false;
    reader.innerHTML = `
      <div class="reader-head">
        <p class="meta">${doc.category} · ${doc.visibility || "public"}</p>
        <h2>${doc.title}</h2>
      </div>
      <div class="prose">${renderMarkdown(doc.body)}</div>`;
    document.querySelectorAll(".result-card").forEach((el) => {
      el.classList.toggle("active", el.dataset.id === id);
    });
  }

  function setStatus() {
    const el = $("status");
    if (state.local) {
      el.className = "brain-status live";
      el.textContent = "Mac Studio brain connected · private docs included";
    } else {
      el.className = "brain-status warn";
      el.textContent = "Public corpus · start the local brain on the Mac Studio for private docs";
    }
  }

  function renderCats() {
    const cats = ["all", ...Object.keys(state.catalog.categories || {}).sort()];
    $("cats").innerHTML = cats
      .map((cat) => `<button type="button" class="chip${cat === state.category ? " active" : ""}" data-cat="${cat}">${cat}</button>`)
      .join("");
  }

  function renderDocList() {
    $("docList").innerHTML = state.catalog.docs
      .map(
        (doc) => `
        <button type="button" class="doc-card" data-id="${doc.id}">
          <p class="meta">${doc.category}</p>
          <h3>${doc.title}</h3>
          <p>${doc.summary || ""}</p>
        </button>`
      )
      .join("");
  }

  async function checkLocal() {
    try {
      const res = await fetch(`${LOCAL_API}/health`);
      state.local = res.ok;
    } catch {
      state.local = false;
    }
    setStatus();
  }

  async function init() {
    const res = await fetch("catalog.json");
    state.catalog = await res.json();
    renderCats();
    renderDocList();
    $("results").innerHTML = `<p class="empty">${state.catalog.doc_count} public topics loaded. Search or pick a topic.</p>`;
    await checkLocal();

    $("searchBtn").addEventListener("click", () => search($("q").value));
    $("q").addEventListener("keydown", (event) => {
      if (event.key === "Enter") search($("q").value);
    });
    $("cats").addEventListener("click", (event) => {
      const btn = event.target.closest("[data-cat]");
      if (!btn) return;
      state.category = btn.dataset.cat;
      renderCats();
      if ($("q").value.trim()) search($("q").value);
    });
    $("results").addEventListener("click", (event) => {
      const btn = event.target.closest("[data-id]");
      if (btn) openDoc(btn.dataset.id);
    });
    $("docList").addEventListener("click", (event) => {
      const btn = event.target.closest("[data-id]");
      if (btn) openDoc(btn.dataset.id);
    });
  }

  init().catch((err) => {
    $("results").innerHTML = `<p class="empty">Could not load catalog.json (${err.message}).</p>`;
  });
})();
