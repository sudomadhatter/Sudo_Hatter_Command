# Implementation Plan — Home-base maps refresh · GitNexus on the lobby · open_tasks as "what's next" source

**Workspace:** `_home` (Sudo_Hatter_Command) — working FROM the home base.
**Date:** 2026-06-25
**Status:** ⏸️ AWAITING APPROVAL — no files outside `_artifacts/` touched yet.

Covers Daniel's three asks in one session:
1. Make sure all the home-base maps are up to date.
2. Add GitNexus to the **top-level** project (the lobby itself) — index the infra folders, **show every project folder but NOT the files inside them** (we cherry-pick which projects get full indexing separately, as aviationChat/ingestion already are).
3. Make `_my_resources/open_tasks/` the place the agent reads when Daniel asks "what do we need to do next" (his running todo + saved plans/PRPs).

---

## 0. What I already verified (read-only)

- **Maps have NO drift today.** `_docs/repo-map.md` regenerates byte-identical (dry-run spliced into a copy in scratchpad → no diff). The SessionStart drift checker prints nothing (clean). `router.md` already lists all 7 `Projects/` folders (aviationChat-AGY, clean-bmad-workspace, jetChat-AGY, B&L WorldWide, NEXGen Films, ingestion-Pipeline-AC, openCode). → **Task #1 is already clean; the only map edits needed are the ones Tasks #2 and #3 introduce.**
- **GitNexus state:** registry has 2 repos — `AGY_AVIATIONCHAT` (Projects/aviationChat-AGY) and `RAG_Pipeline_AC` (Projects/ingestion-Pipeline-AC) — plus group `ac-stack`. The **home base itself is not indexed.**
- **Lobby `.gitignore`** has `/Projects/` (whole tree ignored) and does **not** list `.gitnexus/`.
- **`_my_resources/README.md`** already says `open_tasks` is "features and things I am working on" + "always double-check against live project files." But the active memory `my-resources-personal-area-protected` + the repo-map PROTECTED row say *don't reference `_my_resources/` unless Daniel links it*. Task #3 = a **standing carve-out** for `open_tasks/` only.

---

## TASK 1 — Maps up to date

Almost a no-op on its own (no drift). Concretely:
- **1a.** Regenerate the `_docs/repo-map.md` AUTO body to be safe (`python .agents/scripts/generate_repo_map.py --output _docs/repo-map.md --mode content --ignore Projects,_my_resources`). Expected: no change.
- **1b.** Apply the curated-header edits that Tasks #2 and #3 require (see those sections). These are the *real* map updates.
- **1c.** Re-run the drift checker → expect exit 0, no nags.

---

## TASK 2 — GitNexus on the home base (infra in, project files out)

### Goal
Register the lobby as its own GitNexus repo so the graph covers home-base **infrastructure** (the `.agents/` toolkit, root contract files, `_docs/`, `_system/`, `_routing-canary/`), and so **every project shows up as a node** — but **none of the projects' source files** get pulled in.

### Approach (recommended: **A — marker-file index**)
Index the lobby with a `.gitnexusignore` that hides everything heavy/transient/personal and, for `Projects/`, keeps **only each project's top-level marker doc** (`AGENTS.md`/`CLAUDE.md`/`GEMINI.md`) so the project appears as a real node without graphing its files.

Why marker-file over "empty folder shell": GitNexus builds nodes from indexed content; a folder with everything filtered out may not surface at all. Re-including one marker doc per project **guarantees all 7 projects show** and gives a useful node (each project's workspace map) — at zero cost of indexing their code.

**Alternatives (say the word and I switch):**
- **B — folder-shell only:** ignore `Projects/*/**` with no marker re-include. Lighter, but whether empty project folders surface as nodes is uncertain → projects may not show. Not recommended.
- **C — don't descend into Projects at all:** projects already appear as *text* in `router.md`/`repo-map.md` (which get indexed), so "all projects show" via those doc nodes. Simplest/zero-risk, but projects aren't first-class nodes. Fallback if A proves fiddly.

### Files created/edited
1. **NEW `c:\Sudo_Hatter_Command\.gitnexusignore`** (proposed contents):
   ```gitignore
   # GitNexus index scope for the Sudo_Hatter_Command home base (the LOBBY).
   # Goal: graph home-base INFRA; show each project folder but NOT its files.
   # Paired with GITNEXUS_NO_GITIGNORE=1 so the lobby .gitignore's /Projects/ rule
   # doesn't pre-exclude the whole tree (scope lives HERE instead).

   # Transient / mirror / personal — never graph these
   _artifacts/
   _my_resources/
   .claude/
   .opencode/
   .vscode/
   .gitnexus/
   **/node_modules/
   **/.venv/
   **/__pycache__/

   # Projects: show the folder + its top-level marker doc(s); hide everything else.
   Projects/*/**
   !Projects/*/AGENTS.md
   !Projects/*/CLAUDE.md
   !Projects/*/GEMINI.md
   ```
   **Decision points inside this file (flag any you want changed):**
   - `_artifacts/` **excluded** — it's transient memory (thousands of md files) and would bloat the graph. Recommend exclude.
   - `_my_resources/` **excluded** — PROTECTED area, must not be indexed.
   - `.claude/` + `.opencode/` **excluded** — they're synced mirrors of `.agents/`; indexing them double-counts the toolkit. Recommend exclude.
   - `.agents/`, `_docs/`, `_system/`, `_routing-canary/`, root `*.md`/`*.json` — **included** (this is the "all the other folders" the lobby owns).

2. **EDIT `c:\Sudo_Hatter_Command\.gitignore`** — add `.gitnexus/` (and keep `**/.gitnexus/` for safety) so the lobby's new index folder is never committed.

### The index command (run from lobby root)
```powershell
$env:GITNEXUS_NO_GITIGNORE = "1"; gitnexus analyze "c:\Sudo_Hatter_Command" --index-only --name HOME_BASE -f
```
- `--index-only` → **no** AGENTS.md/CLAUDE.md edits and **no** `.claude/skills/gitnexus/` injection (keeps the curated front door + the synced mirror clean). This is deliberately different from how the project repos were indexed.
- `--name HOME_BASE` → clean registry alias (matches the UPPER style of the other two; disambiguates from the project basenames). Open to `SUDO_HATTER_COMMAND` if you prefer.
- `GITNEXUS_NO_GITIGNORE=1` → so `.gitnexusignore` is the single source of scope.

### Verify (then adjust + re-run if needed — `analyze -f` is repeatable, `.gitnexus/` is disposable)
- `gitnexus list` shows `HOME_BASE` registered.
- A cypher/query confirms: **all 7 projects present** (via their marker docs), **zero** project *source* files indexed, and the `.agents/` infra IS indexed.
- If A doesn't surface a project, tune the `.gitnexusignore` negations and re-run; if it stays fiddly, fall back to Approach C.

### Who runs it
On approval I'll run `analyze` myself and report the verification. (It's a build step, not a git commit — fully reversible via `gitnexus remove HOME_BASE` / deleting `.gitnexus/`.) If you'd rather run it, the command above is copy-paste ready.

---

## TASK 3 — `_my_resources/open_tasks/` as the "what's next" source

A standing carve-out from the `_my_resources/` "do-not-reference" rule, scoped to `open_tasks/` only. Daniel saves his running todo + plans/PRPs there; when he asks "what do we need to do next," the agent should READ that folder (still **read-only** — never edit his notes; still cross-check against live project files per his README).

### Files edited
1. **EDIT `router.md`** — add a routing row so the established "what should I work on" path lands here:
   | If the work is about… | Go to | Read first | Status |
   |---|---|---|---|
   | "What do we do next" / open tasks / what's left / Daniel's plans & PRPs | `_my_resources/open_tasks/` | `todo_list.md` (+ any plan/PRP files there) | active · **read-only** (Daniel's notes — never edit; cross-check vs live project files) |

2. **EDIT `_docs/repo-map.md`** (curated header):
   - Amend the `_my_resources/` PROTECTED row to note the carve-out: *protected/do-not-edit, EXCEPT `_my_resources/open_tasks/` which the agent READS (read-only) when asked "what's next."*
   - Add a Knowledge-map row: `_my_resources/open_tasks/` → read when Daniel asks "what do we need to do next."

3. **EDIT memory `my-resources-personal-area-protected.md`** — record the standing exception (open_tasks is referenceable read-only for "what's next"), so the protection rule and its one carve-out stay consistent. Update its `MEMORY.md` pointer line.

4. **No edit to `_my_resources/README.md`** — it already frames `open_tasks` as work-context, and it's inside the protected area. I'll leave it; if you'd rather I make the carve-out explicit there too, say so.

### Optional AGENTS.md touch
§2 already routes "what should I work on" → `router.md`, so the chain works without an AGENTS.md edit. I'll add a one-liner only if you want it more discoverable.

---

## Cross-cutting notes
- **Your GitNexus guide** (`_my_resources/diagrams_guides/system/gitnexus-usage-guide.md`) says "Indexed repos: AGY_AVIATIONCHAT and RAG_Pipeline_AC" — that goes stale once HOME_BASE is added. It's in your protected area, so I **won't** edit it; flagging so you can update it (or tell me to).
- **Git:** I won't commit/push. The closing `walkthrough.md` will carry the exact explicit-path commit command for you (home base is on `main`).
- **License tripwire (unchanged):** indexing the lobby is fine — it's private local infra, never shipped. No project license status changes.

## Done = 
1. `_docs/repo-map.md` + `router.md` reflect GitNexus-on-lobby and the `open_tasks` carve-out; drift check exits 0.
2. `gitnexus list` shows `HOME_BASE`; all 7 projects present as nodes; no project source files indexed; `.agents/` infra indexed; `.gitnexus/` gitignored.
3. Asking "what do we need to do next" routes to `_my_resources/open_tasks/` (read-only); memory updated.

## Out of scope
- Full-indexing any additional project (cherry-picked later, per ask).
- Editing files in `_my_resources/` (read-only reference only).
- The on-hold `2026-06-25_gitnexus-audit-integration` plan (wiring GitNexus into the self-audit workflow) — separate effort.
