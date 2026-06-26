# GitNexus — How to Use It (Daniel's Guide)

**What it is:** a *code knowledge graph* for your repos that Claude Code can query **live** while we work. It reads your source with a deterministic parser (tree‑sitter — no LLM guessing), builds a graph of every symbol and how they connect (calls, imports, inherits), and serves it to me through one MCP server. When you ask "what breaks if I change this?", I get a real answer from the graph instead of guessing from a few greps.

**Status:** adopted and live as of 2026‑06‑25. Indexed repos: **`AGY_AVIATIONCHAT`**, **`RAG_Pipeline_AC`** (the ingestion pipeline), and **`SUDO_COMMAND`** (the home‑base command center — added 2026‑06‑25). Validated in the spike at `_artifacts/_main/2026-06-24_gitnexus-adoption-spike/`.

> **`SUDO_COMMAND` = the command center itself.** It indexes ALL of `.agents/` — rules · workflows · commands · skills · scripts (~17k nodes; 14 top‑level rules, 3 top‑level workflows). This is "the one everything points to," NOT the pointer/adapter copies (`.claude/`/`.opencode/` mirrors are excluded by construction — only `.agents/` is indexed). GitNexus hard‑skips dot‑folders, so the index is **rooted directly at `.agents/`** (`--skip-git`), which bypasses the skip.
> - **Caveat 1:** `--skip-git` disables commit‑staleness tracking → **re‑index manually after you change any rule/workflow.**
> - **Caveat 2:** GitNexus extracts *headings*, not doc cross‑references, from markdown — so `impact`/`context`/`trace` give few edges *between* rule/workflow `.md` files. The graph is strong on the `.py`/`.ps1` scripts, thin on the prose wiring. For "what references what" in the toolkit, read/grep the files.
> - (An earlier thin "portfolio map" view — projects as nodes — was tried and **dropped** in favor of this single command‑center index named `SUDO_COMMAND`.)
>
> Full record: `_artifacts/_main/2026-06-25_home-base-maps-gitnexus-opentasks/`.

**The one rule to remember:** GitNexus is a **disposable accelerator, never a source of truth.** Your markdown maps, AGENTS.md, and the code itself are canonical. If GitNexus vanished tomorrow, nothing breaks — you'd just lose a fast lookup. (This is the "Tier‑2" idea below.)

---

## How you actually use it (this is the important part)

**You don't call any tools. You just talk to me.** The GitNexus tools are wired into *my* toolbox, not yours. You ask a question in plain English; I decide the graph is the right tool, call it, and bring back the answer. So "using GitNexus" = **asking me the right kind of question.**

Here's the translation table — say the thing on the left, I run the tool on the right:

| When you say something like… | I run | What you get back |
|---|---|---|
| "What breaks if I change `SpecialistChat`?" / "blast radius of this function" | `impact` | Everything upstream/downstream that depends on it, by depth + risk |
| "What calls this? What does it touch?" / "give me the full picture on `ReasonerAgent`" | `context` | 360° view: callers, callees, the flows it's part of, file:line |
| "How does `applyVerification` reach the database?" / "trace A to B" | `trace` | The exact call chain, hop by hop, with file:line |
| "How does verification work end to end?" / "where does X happen?" | `query` | Ranked execution flows for that concept, not just file matches |
| "What do my uncommitted changes affect?" / "review before I commit" | `detect_changes` | Maps your `git diff` to symbols → which flows are at risk |
| "What repos are indexed? Are they stale?" | `list_repos` | The registry + a staleness warning if the index is behind HEAD |
| "What contracts link the app and the pipeline?" | `group_list` / `group_sync` | HTTP provider/consumer contracts across the group (see limits) |

You can also just describe the *goal* ("I'm about to refactor the reasoner — what should I worry about?") and I'll pick the right combination. The tools chain naturally: I usually go `query` → `context` → `impact`.

---

## The two‑tier mental model (when to reach for it)

This is *why* it's safe to lean on. There are two layers of context, and GitNexus is only the second:

- **Tier 1 — the MAP** (`repo-map.md` + `router.md`): cheap, always loaded, owned plain markdown. Answers *"where is X / what's the shape of this repo."* Unchanged by GitNexus.
- **Tier 2 — the GRAPH** (GitNexus): expensive, **on‑demand only**, derived and disposable. Answers *"what depends on X / blast radius / trace this path / how does this flow work."* Never auto‑loaded — I pull it only when a question needs it.

**Rule of thumb:** if a plain file search or the map answers it, that's enough. Reach for the graph when the question is about **relationships and consequences** — dependencies, blast radius, call chains, "what flows through here." That's where it beats grep, because grep finds *text* and the graph finds *connections*.

---

## What each tool gives you (with a real example from your repo)

### `impact` — blast radius ("what breaks if I touch this")
The headline tool. Give it a symbol; it walks the dependency edges and tells you everything affected, grouped by how many hops away, with a risk rating and a **confidence** per edge.

Real run against `VerificationEvent` (the class defined twice in your repo — once in `schemas/specialist.py`, once in `reasoner/agent.py`):
- The reasoner copy → **12 impacted, risk MEDIUM**, 6 direct importers (`specialist/agent.py`, `evals/drivers.py`, routers, `__init__.py`…).
- The schemas copy → **11 impacted, risk LOW.**
- Same name, **different blast radius** — which is exactly the dual‑definition smell worth cleaning up.

> **Disambiguation:** when a name exists twice, the tool hands me both candidates with a `uid`, and I re‑run against the exact one. You don't have to do anything — just know that's why I sometimes say "there are two of these."

> **Read the confidence column.** Code imports come back at confidence `1.0`. The graph also indexes your `_bmad/**/*.md` story files and infers "imports" from them at `0.8` — useful as breadcrumbs, but they're docs, not code. I'll separate them when it matters.

### `context` — 360° view of one symbol
Everything pointing *in* (callers, importers, subclasses) and *out* (callees, methods, properties), plus which execution flows the symbol participates in, all with file:line. This is the "tell me everything about `X`" tool — the deep dive after a search.

### `query` — find execution flows by concept
Natural‑language search that returns **ranked call chains**, not file hits. "How does SSE streaming work" returns the actual flow of functions, ranked. Use this to *orient* in unfamiliar code before zooming in with `context`.

### `trace` — shortest path between two symbols
"How does A reach B?" in one call. Returns the exact chain hop‑by‑hop with edge types and confidence, or — if there's no path — the furthest point it *could* reach, so you see where the chain breaks. Saves the 3–8 manual hops you'd otherwise do by hand.

### `detect_changes` — pre‑commit blast radius
Reads your **uncommitted `git diff`**, maps the changed lines to symbols, and tells you which flows your edit touches. Ask me this *right before committing* and I'll flag anything risky you didn't realize you were affecting. (Scopes: unstaged / staged / all / compare‑to‑a‑branch.)

### `list_repos` — the registry + staleness
Shows what's indexed and warns when an index is behind HEAD (right now both repos read **"1 commit behind — run analyze to update"**). That's your cue to re‑index (below).

### `group_*` — cross‑repo contracts (with a big caveat — see Limits)
`group_list` / `group_sync` build a contract registry across the `ac-stack` group by matching **HTTP** provider/consumer pairs.

---

## You run these yourself (in the terminal, not through me)

I drive the *query* tools above. **You** drive the *index lifecycle* from PowerShell:

```powershell
gitnexus list                 # what's indexed (same data I see via list_repos)
gitnexus analyze "<repo path>"  # (re)index a repo — run this when the index goes stale
gitnexus serve                # the visual graph at http://localhost:4747  ← your original "see my projects" want
gitnexus status               # quick health of the current repo's index
gitnexus doctor               # capabilities check (graph store, FTS, vector index)
```

**Re‑indexing (the one chore):** the graph is a snapshot. After you commit real code changes, `list_repos` starts showing "N commits behind." When the drift starts to matter, re‑run:

```powershell
gitnexus analyze "c:\Sudo_Hatter_Command\Projects\aviationChat-AGY"
gitnexus analyze "c:\Sudo_Hatter_Command\Projects\ingestion-Pipeline-AC"
# The command center (SUDO_COMMAND = .agents/ rules+workflows) — rooted AT .agents/ to beat the dot-folder skip; re-run after you edit any rule/workflow:
$env:GITNEXUS_NO_GITIGNORE="1"; gitnexus analyze "c:\Sudo_Hatter_Command\.agents" --skip-git --index-only --name SUDO_COMMAND -f
```

> **⚠️ `analyze` is NOT read‑only.** Running it **appends a "GitNexus — Code Intelligence" section to that repo's `CLAUDE.md`** and drops a `.claude/skills/gitnexus/` folder in. It *appends* (doesn't overwrite your front door), and we decided to **keep** it — that section is what makes me auto‑reach for these tools. Just don't be surprised by the `git status` noise. It also writes a `.gitnexus/` index folder — add that line to each repo's `.gitignore` before you ever commit those repos so it doesn't get swept in.

---

## Limits — what it does NOT do (so you don't trust it wrong)

1. **No cross‑repo edges between the app and the pipeline.** GitNexus links repos only through **HTTP** provider/consumer contracts. AviationChat ↔ ingestion couple through a **shared data store**, not HTTP calls — so the graph draws **zero edges between them**. The "one unified portfolio graph across all my projects" vision is real only for HTTP/microservice topologies. For your stack it's **two deep per‑repo graphs in one registry**, not a connected pair. Don't ask me for "blast radius across both repos" and trust a clean answer — there's no bridge there.
2. **Snapshot, not live.** It reflects the last `analyze`, not your current working tree (except `detect_changes`, which reads the live diff). Stale index → stale answers. Watch the staleness hint.
3. **Windows: semantic search is degraded.** The vector index is disabled on Windows, so concept search falls back to a slower exact scan. Structural tools (`impact`/`context`/`trace`) are unaffected and are the real value. We **skipped embeddings** for this reason.
4. **`explain` (security taint analysis) is unavailable** — it needs an index built with `gitnexus analyze --pdg`, which we didn't build. If you ever want source→sink taint findings, we'd re‑index with `--pdg` first. (Note: AviationChat security/pentest work lives on the separate **Shannon** track, not here.)
5. **Doc files inflate results.** Your `_bmad` stories get indexed and show up as low‑confidence "imports." Breadcrumbs, not ground truth.

---

## License tripwire (don't skip this)

GitNexus is **PolyForm Noncommercial**. Your call (2026‑06‑24): index AviationChat **while it's pre‑revenue / non‑profit**, because it's a private local dev tool that never ships in production.

**Hard stop:** the day AviationChat starts charging / goes for‑profit → **stop indexing it, delete its `.gitnexus/`,** and either get a commercial quote from akonlabs or swap Tier‑2 to a permissive/MIT engine. The two‑tier design is engine‑swappable for exactly this reason — your maps survive the swap.

**Never index:** `jetChat` (already commercial). (`clean-bmad-workspace` is **not** off‑limits and **not** another team's — it's Daniel's own clean‑shell template for cloning new projects, a near‑empty skeleton with no real code to graph, so there's simply nothing worth indexing there.)

---

## 30‑second cheat sheet

- **It's a question‑answering layer, not a thing you operate.** Ask me about *relationships and consequences*; I run the graph.
- **Best questions:** "what breaks if I change X", "trace A to B", "what does my diff affect", "how does this flow work."
- **Re‑index** with `gitnexus analyze "<path>"` when `list_repos` says it's behind. That edits the repo's `CLAUDE.md` (kept on purpose).
- **Visual** = `gitnexus serve` → http://localhost:4747.
- **It can't** connect the app and the pipeline (no HTTP between them), it's a snapshot, and semantic search is weak on Windows.
- **Trust the code and the maps over the graph, always.**

---
*Source of truth for the adoption decision, evidence, and findings: `_artifacts/_main/2026-06-24_gitnexus-adoption-spike/` (implementation_plan.md + walkthrough.md). Memory: `tooling-gitnexus-shannon-tracks`.*
