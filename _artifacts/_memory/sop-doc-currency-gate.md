---
name: sop-doc-currency-gate
description: "Since 2026-08-08 an ARMED commit-msg gate rejects any change to a usage surface (.agents/commands|rules|scripts, git-hooks, .githooks, root AGENTS.md) that does not also stage docs/_scc_sops_prds/workflows_testing_SOP.md. `[sop-ok]` in the message is the logged opt-out."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ea1c7963-b655-4c4b-861f-0b832da17b1e
  modified: 2026-08-08T05:57:14.734Z
---

`docs/_scc_sops_prds/workflows_testing_SOP.md` is the **operator's PRD** — the one page
that answers "what do I type." (It lived under `_my_resources/_quick_reference/` at birth and
moved to `docs/_scc_sops_prds/`; the gate's path followed. The operator asked for it by name and
approved the gate.)

**The gate** (`.agents/scripts/sop_currency.py` ← `git-hooks/sop-currency.sh`, second in
`.githooks/commit-msg` after the Jira gate): a commit touching `.agents/commands/*.md`,
`.agents/rules/*.md`, `.agents/scripts/*.py|*.ps1`, `.agents/scripts/git-hooks/`, `.githooks/`, or
root `AGENTS.md` is **rejected** unless the SOP doc is staged with it. Exempt by design:
`INDEX.md` churn, `reference/`, `templates/`, `skills/`, `workflows/`, `_artifacts/`, its own tests.

- Opt out per commit with **`[sop-ok]`** (case-insensitive) — it stays in the git log as the record.
- Disarm to warn-only by deleting `.agents/scripts/git-hooks/SOP-ENFORCE`.
- No-ops in any repo lacking the doc, so project clones are unaffected.
- `.claude/`/`.opencode/` mirror churn is NOT a surface — sync commits pass untouched.

**Why:** it shipped ARMED against the usual warn-first advice because **hook output is invisible in
VS Code** ([[vscode-hides-git-hook-output]]) — a warn-only gate reads as clean success and enforces
nothing. Every gate here keeps a one-token exit instead, since a gate with no legitimate way out
gets `--no-verify`d permanently.

**How to apply:** when you edit any usage surface, edit the SOP doc **in the same commit** — don't
defer it and don't reach for `[sop-ok]` unless the change genuinely alters nothing the operator
does. The doc's voice: consequence before mechanism, every term explained, retire entries rather
than accreting "(retired)" notes, and **paste any command into a shell before writing it down**
([[windows-authored-code-hides-posix-bugs]] §7). Sibling rule: [[thin-projects-center-owns-workflow-law]]
governs WHERE a rule lives; `living-template-sync.md` keeps new projects from being born stale.

**Known open drift:** AGY's copy at `Projects/AGY_AVIATIONCHAT/_my_resources/_quick_reference/`
is behind the lobby's and still calls that project's `.agents/` "a synced copy" — false since
centralization. The gate cannot reach across repos.
