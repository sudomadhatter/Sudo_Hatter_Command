---
IsArtifact: true
ArtifactMetadata:
  title: "Rule change — always hand artifacts as clickable links in chat"
  type: implementation_plan
  date: 2026-06-28
---

# Plan — Always deliver artifacts/files as clickable links in chat

## Goal
Make it a standing rule across all agents that **any artifact, file, or path handed to Daniel in
chat is a clickable Markdown link** (`[label](relative/path)`) he can open — never a bare path.
Must apply on **this lobby (Sudo_Hatter_Command)** plus **AGY_AVIATIONCHAT** and **Fresh_Workspace_BMAD**.

## What's already there (so we don't duplicate)
- [artifacts-always-first.md:48-51](../../../.agents/rules/artifacts-always-first.md#L48-L51) already has
  a "🔗 Link every artifact in the chat" callout — but it is **scoped to the 5 formal artifact types**
  (plan, walkthrough, bug-list, code-review, self-audit) and only loads on **work sessions** (it's the
  "protocol" tier, not the always-load floor).
- The gap vs. your request: you want it **always** (even a read-only "where is X?" answer that names a
  file) and for **any** file/path, not only the formal artifact set.

## Approach (recommended)
Put the general rule in the **always-load floor** so it fires every session and on every model surface
(Claude / opencode / Antigravity), then re-vendor to the named projects.

### Edit 1 — `.agents/rules/constitution.md` (always-on floor) — add one bullet to "✅ Always"
> - Always hand Daniel **clickable links, never bare paths**: any file, artifact, or path you name or
>   deliver in chat must be a Markdown link `[label](relative/path)` he can click to open — every session,
>   including read-only/investigatory answers.

This is the durable home: `constitution.md` is loaded on *every* session (not just file-modifying ones),
so the rule also covers investigatory replies.

### Edit 2 — `.agents/rules/artifacts-always-first.md` (consistency, small) — generalize the existing callout
Broaden the line 48-51 callout from "ANY artifact (plan, walkthrough, …)" to "ANY artifact, file, or path
you hand over," state it's a **Markdown hyperlink `[label](path)`**, and note it's the always-on rule from
the constitution. Keeps the artifact protocol and the floor rule consistent (no contradictory wording).

### Propagation (covers the 3 named workspaces)
- **Lobby (Sudo_Hatter_Command)** — reads master `.agents/` directly, so Edits 1–2 apply immediately; no
  vendor step needed for the lobby's own rules.
- **AGY_AVIATIONCHAT** — `/sync-agents Projects/AGY_AVIATIONCHAT` re-vendors the updated rules into
  `Projects/AGY_AVIATIONCHAT/.agents/rules/`.
- **Fresh_Workspace_BMAD** — `/sync-agents Projects/Fresh_Workspace_BMAD` does the same.

## Files touched
| File | Change |
|---|---|
| `.agents/rules/constitution.md` | + 1 "✅ Always" bullet (the general always-on rule) |
| `.agents/rules/artifacts-always-first.md` | generalize the existing "🔗 Link every artifact" callout for consistency |
| `Projects/AGY_AVIATIONCHAT/.agents/rules/*` | re-vendored via `/sync-agents` (no hand-editing) |
| `Projects/Fresh_Workspace_BMAD/.agents/rules/*` | re-vendored via `/sync-agents` (no hand-editing) |

## Verification
- `diff` master vs. each vendored `constitution.md` + `artifacts-always-first.md` → confirm the new lines
  landed in both projects.
- Report the per-surface counts `/sync-agents` prints.

## Decisions baked in (correct me at approval if any is wrong)
1. **Scope = shared master, not project-local.** Editing master + sync applies to **all** conformant
   projects (a superset of the 3 you named). This is your universal preference, so shared is right; the 3
   you named are guaranteed covered. *(If you truly want it limited to only those 3, that's a different,
   project-local approach — say so.)*
2. **Model scope = all three surfaces.** Shared `.agents/rules/` is model-agnostic, so this binds Claude
   **and** opencode **and** Antigravity — a superset of "all the claude agents." Assumed desirable.
3. **"Artifact" read broadly** = any file/path you hand me in chat, not just the 5 formal `_artifacts/`
   types. If you meant only the formal deliverables, the change shrinks to just Edit 2.
4. **Git** = I'll hand you the commit command at the end; I won't commit/push myself.

## Open questions
- None blocking — approve as-is, or redirect on any of the 4 decisions above.
