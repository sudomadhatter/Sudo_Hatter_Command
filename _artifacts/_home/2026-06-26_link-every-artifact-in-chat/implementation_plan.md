---
IsArtifact: true
ArtifactMetadata:
  title: Link every artifact in the chat — adopt aviationChat rule at home base + clean-bmad
  type: implementation_plan
  date: 2026-06-26
---

# Plan — "Link every artifact in the chat" rule

## Goal
Adopt, at the **home base** and in the **clean-bmad-workspace template**, the rule Daniel wants from
aviationChat: **always post a clickable link to an artifact in the chat** whenever one is written —
broadened from the current *plan-only* phrasing to **every artifact** (plan, walkthrough, task-list,
bug-list, code-review, self-audit).

## Background (what I found)
- The existing guidance in aviationChat is **plan-scoped only**: "Present the plan's key points inline in
  the chat AND link the artifact" — in [artifacts-always-first.md:90](../../../Projects/aviationChat-AGY/.agents/rules/artifacts-always-first.md#L90)
  and [000-PLAN-FIRST-GATE.md:46](../../../Projects/aviationChat-AGY/.agents/rules/000-PLAN-FIRST-GATE.md#L46).
- The home base rule [.agents/rules/artifacts-always-first.md:94](../../../.agents/rules/artifacts-always-first.md#L94)
  has the same plan-only line. The clean-bmad template's copy is identical in structure (plan line at L90).
- Daniel's confirmed intent: **link EVERY artifact in chat**, not just the plan.

## Scope — 2 files, 2 identical edits each
The anchor text is identical in both files, so the same two edits apply verbatim.

1. **[.agents/rules/artifacts-always-first.md](../../../.agents/rules/artifacts-always-first.md)** (home-base master)
2. **[Projects/clean-bmad-workspace/.agents/rules/artifacts-always-first.md](../../../Projects/clean-bmad-workspace/.agents/rules/artifacts-always-first.md)** (template)

### Edit 1 — new callout (insert right after the "Do NOT create …" block, before `## The Rule`)

```markdown
> **🔗 Link every artifact in the chat — always.** The moment you write or update ANY artifact (plan,
> walkthrough, task-list, bug-list, code-review, self-audit), post a **clickable link to it in the chat**
> that same turn, with a one-line note of what it is. Daniel reviews from the conversation — an artifact he
> can't open from chat may as well not exist. This generalizes the plan-link rule below to the whole set.
```

### Edit 2 — new Hard Stop bullet (add under `## Hard Stops`, after the "NEVER skip the artifact folder" line)

```markdown
- NEVER write or update an artifact without posting a clickable link to it in the chat that same turn
  (see the "Link every artifact in the chat" rule above).
```

## Why these two edits (and not more)
- The callout sits with the artifact set so it governs all of them; the Hard Stop makes it enforceable
  alongside the other "inline-only is not sufficient" stops. Minimal, high-signal, no restructuring.
- I'm **not** touching `AGENTS.md` (the rule file is the full protocol it points to) or the per-section
  text — the one callout covers every section.

## Out of scope (flag for your call)
- **aviationChat-AGY**: still has only the plan-only line. The rule "came from" there but in narrower form.
  I can backport the same two edits to its copy + `000-PLAN-FIRST-GATE.md` if you want parity — say so and
  I'll add it. Not doing it unless you confirm (separate repo, its own commit).
- No `.claude`/`.opencode` synced `rules/` copies exist at the home base, so nothing to re-sync there.

## Verification
- `grep -n "Link every artifact" ` in both files returns the callout + the hard-stop reference.
- Re-read both Hard Stops sections to confirm the bullet landed and formatting is intact.

## Open questions
1. Backport to aviationChat-AGY too? (default: **no**, unless you say yes)

## Git
Home base + clean-bmad are separate repos → two separate commits. I'll hand you the exact commands in the
walkthrough's "Your Actions"; I won't commit/push myself.
