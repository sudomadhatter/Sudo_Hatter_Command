---
IsArtifact: true
ArtifactMetadata:
  title: "Walkthrough — always-on clickable-link rule across all three workspaces"
  type: walkthrough
  date: 2026-06-28
---

# Walkthrough — Clickable links, never bare paths (always-on rule)

## What you asked for
Every artifact/file/path an agent hands you in chat must be a **clickable hyperlink** — across the lobby
(Sudo_Hatter_Command), AGY_AVIATIONCHAT, and Fresh_Workspace_BMAD. You confirmed the broad reading: **any
file path**, not just the formal artifact set. (Antigravity already renders these natively, so the rule is
a no-op it already satisfies; the real gap was the Claude/opencode surfaces.)

## What changed & why
A narrower version of this already lived in `artifacts-always-first.md`, but it (a) only covered the 5
formal artifact types and (b) only loaded on file-modifying work sessions. To make it truly *always* and
*everything*, I put the general rule in the **always-load floor** and generalized the existing callout so
the two agree.

**Edit 1 — `.agents/rules/constitution.md`** (the always-load floor; read every session, every model).
Added one bullet to `## ✅ Always`:
> Always hand Daniel **clickable links, never bare paths** — any file, artifact, or path you name or
> deliver in chat must be a Markdown link `[label](relative/path)` he can click to open. Applies to every
> session, including read-only / investigatory answers.

This is the durable home: the constitution loads even on read-only sessions, so a "where is X?" answer that
names a file is now covered too — not just work sessions.

**Edit 2 — `.agents/rules/artifacts-always-first.md`** (consistency, 2 spots).
Generalized the existing "🔗 Link every artifact in the chat" callout → **"Link every artifact — and every
file — in the chat, always,"** specified a **Markdown link `[label](path)`**, and pointed it at the
constitution rule as the single source. Updated the matching Hard Stop the same way.

**Kept model-agnostic on purpose:** no "Antigravity already does this" wording went into the shared rule —
the shared files must stay model-neutral (one brain, three surfaces), so the rule reads as a universal
preference that Antigravity simply already meets.

## Propagation
- **Lobby (Sudo_Hatter_Command)** reads master `.agents/` directly → live the moment the master was edited;
  no vendor step needed.
- **AGY_AVIATIONCHAT** and **Fresh_Workspace_BMAD** re-vendored via
  `& ".agents/scripts/sync-agents.ps1" -Target "<project>"`. The only sync-induced diff in each was the two
  rule files (every other vendored file was already current).

## Verification (pasted, not fabricated)

New lines present in all three copies of each rule:
```
===== CONSTITUTION: clickable-links bullet =====
  1  <- .agents/rules/constitution.md
  1  <- Projects/AGY_AVIATIONCHAT/.agents/rules/constitution.md
  1  <- Projects/Fresh_Workspace_BMAD/.agents/rules/constitution.md
===== ARTIFACTS-FIRST: 'and every file' callout =====
  2  <- .agents/rules/artifacts-always-first.md          (callout + hard stop)
  2  <- Projects/AGY_AVIATIONCHAT/.agents/rules/artifacts-always-first.md
  2  <- Projects/Fresh_Workspace_BMAD/.agents/rules/artifacts-always-first.md
```

Byte-identical across all three workspaces (md5):
```
-- constitution.md --          7d0383aeb0cb2616dbcf20324f3586d9  (x3, identical)
-- artifacts-always-first.md -- 074090bee1bc9636743d3fb7e2590a4f  (x3, identical)
```

No deviations from the approved plan.

## Task Checklist
- [x] Investigate where the rule should live (always-load floor) — confirmed `constitution.md`
- [x] Write `implementation_plan.md`, log INDEX row, stop for approval — approved
- [x] Edit master `constitution.md` — added always-on clickable-link bullet
- [x] Generalize the `artifacts-always-first.md` callout + hard stop for consistency
- [x] Re-vendor into AGY_AVIATIONCHAT and Fresh_Workspace_BMAD via `/sync-agents`
- [x] Verify all three copies byte-identical (md5 match x3 for both files)
- [ ] Commit — handed to you below (3 separate repos; I do not commit/push)

## Your Actions
Three separate git repos, all on `main_debug`. **Scoped paths only** — each repo has unrelated uncommitted
work that must NOT be swept in (AGY has frontend/bmad changes; the lobby has two unrelated untracked
folders). Run from the lobby root:

**1. Lobby — Sudo_Hatter_Command** (rule edits + this session's artifacts; excludes the unrelated
`testing-strategy-tea-gate/` folder and `testing_strategy_e2e.md`):
```bash
git add .agents/rules/constitution.md .agents/rules/artifacts-always-first.md _artifacts/INDEX.md "_artifacts/_main/2026-06-28_clickable-artifact-links-rule/"
git commit -m "feat(rules): always-on 'clickable links, never bare paths' in chat

Add to constitution.md (always-load floor) so any file/artifact/path handed in
chat must be a clickable Markdown link, every session incl. read-only. Generalize
the artifacts-always-first callout + hard stop to match.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

**2. AGY_AVIATIONCHAT** (re-vendored rules ONLY — leaves the frontend/bmad work untouched):
```bash
git -C Projects/AGY_AVIATIONCHAT add .agents/rules/constitution.md .agents/rules/artifacts-always-first.md
git -C Projects/AGY_AVIATIONCHAT commit -m "chore(rules): vendor always-on clickable-link rule from master

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

**3. Fresh_Workspace_BMAD** (re-vendored rules ONLY):
```bash
git -C Projects/Fresh_Workspace_BMAD add .agents/rules/constitution.md .agents/rules/artifacts-always-first.md
git -C Projects/Fresh_Workspace_BMAD commit -m "chore(rules): vendor always-on clickable-link rule from master

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
