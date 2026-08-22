---
name: rule-org-single-source-audit
description: "Cross-project rule-org audit (2026-07-06). Lobby+AGY+Fresh clean & on single-source model, karpathy §5 added to all 3. AGY_JETCHAT + RAG_Pipeline_AC are the real rules-in-.claude offenders (still unfixed)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fc8bbc7d-1589-4ba3-ab1c-aa8a1f4b77e3
---

Rule-organization audit across the lobby + `Projects/`, 2026-07-06.

**⚠️ SUPERSEDED 2026-08-07 (SCC-31).** The project `.agents/` vendor described below no longer exists:
projects carry only their OWN rules + skills + `INDEX.md`, and shared rules are read in place from the
lobby ([[thin-projects-center-owns-workflow-law]]). The single-source principle survived — it just has
one home now instead of N synced copies. RAG_Pipeline_AC's "no `.agents/rules/`" offense below was
resolved in that conversion. Kept as history:

**The model (corrects the recurring "rules ended up in `.claude`" worry):** behavioral rules are single-sourced in `.agents/rules/` and read **in-place** via `CLAUDE.md`/`GEMINI.md` → `AGENTS.md` → `.agents/rules/`. There should be **no** `<proj>/.claude/rules/`. `/sync-agents` copies only commands+skills+hooks into `.claude`/`.opencode`/antigravity — **never rules**; the project `.agents/` vendor is additive `robocopy /E` (overwrites shared rules from master, preserves project-only rules like `constitution.project.md`, never purges). So a lobby rule edit is live with no sync; a project rule needs a re-vendor OR a matching edit. [[toolkit-sync-covers-agents-not-docs]]

**DONE (clean / on-model):**
- **Lobby, AGY_AVIATIONCHAT, Fresh_Workspace_BMAD**: root trio correct (AGENTS brain + thin CLAUDE/GEMINI adapters), rules single-sourced, **karpathy §5 "Read the Docs, Don't Guess" added** (don't guess an MCP/CLI/API/library interface — web-search the vendor's first-party docs; verify version). Deleted the stale `.agents/{CLAUDE,AGENTS}.md` gitnexus fossils (identical `SUDO_COMMAND/17230-symbol` vendored junk, md5 f7f6b45e…) in all three.
- **BRKN_Tattoos**: also clean/on-model (trio + single-sourced rules), but still carries the `.agents/{CLAUDE,AGENTS}.md` fossil (not swept — out of scope + repo already dirty at session start).

**REAL offenders (the actual "rules in `.claude`" cases — NOT yet fixed):**
- **AGY_JETCHAT**: root trio BROKEN — has `CLAUDE.md` but **no `AGENTS.md`** (the file CLAUDE.md points to!) and no `GEMINI.md`; AND a **stray `.claude/rules/` (15 files)**, several not in its `.agents/rules/` → rules split across both. Needs: restore AGENTS.md+GEMINI.md, reconcile `.claude/rules` → `.agents/rules`, delete the stray, sweep fossils.
- **RAG_Pipeline_AC**: worst — **no `.agents/rules/` at all**, rules live ONLY in a **stray `.claude/rules/` (14 files)**, no `GEMINI.md`. Not on the single-source model; needs a full migration to `.agents/rules/` + thin front doors.
- Empty/unscaffolded stubs (ignore): B-L-WorldWide, NEXGen-Films, OpenChat-Openrouter.

**Method to apply per project:** (1) rules only in `.agents/rules/`, no stray `.claude/rules/`; (2) root trio = `AGENTS.md` brain + thin `CLAUDE.md`/`GEMINI.md` (a project's own accurate gitnexus block on CLAUDE.md is fine — leave it); (3) sweep stale `.agents/{CLAUDE,AGENTS}.md` fossils; (4) propagate karpathy §5. [[gitnexus-index-not-actually-live]]
