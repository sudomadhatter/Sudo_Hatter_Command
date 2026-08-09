# SCC-58 — Verifying workflow components

**Lane:** `chore/SCC-58-verify-workflow-components` (worktree — SCC-61 is live in the shared checkout)
**Date:** 2026-08-09
**Type:** verification Task; fixes are the natural completion of what the verification found.

---

## What the ticket asked

1. Verify `/self-assess` is actually using GitNexus for looking at edges, and audit its effectiveness.
2. Verify the new skeleton project has the file/folder guide set up in it and uses it.

---

## Finding 1 — the GitNexus gate is dead (the headline)

`/self-assess` is `/sudo-self-audit`. Phase 1 does instruct graph-first edge analysis, but behind this gate:

> If this repo is GitNexus-indexed (its `AGENTS.md`/`CLAUDE.md` carries a
> "GitNexus — Code Intelligence" section) and the MCP tools are present…

The heading is real. **The file is wrong.** `# GitNexus — Code Intelligence` is the H1 of
`docs/gitnexus.md` in all three repos — never a section of `AGENTS.md`/`CLAUDE.md`, which carry only a
one-line pointer to it (`AGENTS.md:177` in AGY, lowercase and hyphenated: `**GitNexus** —
code-intelligence (…)`).

An agent following the literal condition checks `AGENTS.md`, finds no such section, concludes
"not indexed", and falls through to grep — **every time, in the repo where the graph is worth the most.**

A title-match alone would not fix it either: the skeleton's `docs/gitnexus.md` is titled
`# GitNexus — Code Intelligence (project skeleton — NOT indexed yet)`. Matching the heading there
returns a **false positive** on a repo that has no index at all. The doc-string proxy is the wrong
predicate in both directions.

**Fix:** detect from the tool, not from prose. `list_repos` is ground truth and is one cheap call.

## Finding 2 — effectiveness gaps (the graph works; the instructions around it don't)

Measured, not assumed. `impact(get_db, upstream, summaryOnly)` on AGY returns **286 impacted / 141
direct / 72 processes / 12 modules / `epistemic: "exact"` / risk CRITICAL**. Grep returns a flat file
list with no depth, flow, or risk structure. The tool earns its place. Three gaps in how it is driven:

| # | Gap | Consequence |
|---|---|---|
| 2a | Calls the graph "authoritative" with **no freshness gate** | `Sudo_Hatter_Command`'s index is 4 commits behind HEAD; AGY's is pinned to `epic/AVCH-18`. A stale index yields a confidently wrong blast radius — a false-clean audit. |
| 2b | `repo:` is **conditional** ("when more than one repo is indexed") | Three repos are indexed. Conditional wording invites an unscoped call that silently answers about the wrong repo. |
| 2c | Names dynamic/string refs as the grep cross-check, but **not attribute dispatch** | `impact()` returns 0/LOW for `self.<attr>.<method>()`. A `0` reads as "safe to change" — the most dangerous possible way to be wrong. |

## Finding 3 — the skeleton guide exists and is routed, but contradicts the project's own law

`docs/file_structure_rules/README.md` is present, and `AGENTS.md` §6 routes to it. So the ticket's
question answers **yes** on both counts. Its *content* is what fails, verified against disk:

| Line | Claim | Ground truth |
|---|---|---|
| 60 | `.agents/` is "the **vendored master toolkit** — `rules/ skills/ commands/ workflows/ scripts/ templates/`" | The skeleton's `.agents/` holds only `rules/`, `skills/`, `scripts/` (index-only). No `commands/`, `workflows/`, or `templates/`. Contradicts its own `AGENTS.md` §3 ("nothing here duplicates it") **and** its own §5 ("reads it at the center — never vendors a copy"). |
| 82 | "Git — **never commit/push yourself**. Hand the operator the exact command." | `AGENTS.md` §8: commits **and pushes** on `claude/*` are FREE and ungated. A gate conflict, not a wording nit. |
| 100, 113, 144 | mandates `task-list.md` | `AGENTS.md` §5: "**no separate `task-list.md`**". Retired artifact, mandated 3×. |
| 131 | `_system/` (workspace builder) at the center | Does not exist. (`_routing-canary/` does.) |
| 81 | "GO BACK to `../../router.md`" | From `docs/file_structure_rules/`, `../../` is the skeleton root — no `router.md` there. The center's is 4 levels up. |

Plus, in the skeleton's own `AGENTS.md` §5: `self-audit-stress-test.md` is still listed, though
`/sudo-self-audit` retired it 2026-08-02.

---

## Plan

### A. Center repo (this lane, under SCC-58)
Rewrite the `/sudo-self-audit` Phase 1 graph-first block in all **three** mirrors — kept byte-identical:
- `.agents/commands/sudo-self-audit.md`
- `.agents/workflows/sudo-self-audit.md`
- `.opencode/commands/sudo-self-audit.md`

Changes: detection via `list_repos` (not a doc heading) · `repo:` unconditional · freshness gate
(`lastCommit` vs `HEAD`, stale ⇒ say so and cross-check) · 0/LOW must be grep-verified before it is
believed.

`.agents/skills/sudo-self-audit/SKILL.md` is a 15-line launcher and needs no change.
`sudo-self-audit_AP.md` delegates by `@`-reference and inherits the fix — no edit, verified.

### B. Skeleton repo (separate repo, separate commit)
`Projects/sudo-project-skeleton` is its own git repo with **no armed `jira.conf`** (only
`jira.conf.example`), so its commits carry no key by design and must not ride SCC-58's. Fix the six
rows in Finding 3 there, committed separately.

### C. Deliberately NOT in this lane
The parallel-worktree rules change (operator-requested this session) touches
`worktree-per-story.md`, `close-task-merge-tree.md`, `sudo-merge-epic-workingtrees.md`,
`sudo-close-workingtree.md`, `sudo-park.md`, `sudo-resume.md` — **all six are open and uncommitted in
SCC-61's lane right now.** Split to its own ticket, to start once SCC-61 merges. Operator decision,
2026-08-09.

Design carried forward to that ticket, including the gitignored-asset answer:

| Asset | Mac | PC | Why |
|---|---|---|---|
| `node_modules/` | symlink | **junction** | directory; junction needs no admin on Windows |
| `auth_keys/` | symlink | junction | directory, read-only in practice |
| `.env` | symlink | **copy** | Windows file-symlinks need admin/Developer Mode — the reason today's rule says "copy" |

Caveats to carry: a symlinked `.env` is **shared state** across lanes (good for rotation, one new
collision surface); shared `node_modules` is fine for dev but the E2E tier keeps its own `npm ci`.

## Verification
- `tests/run_all.py` green.
- The dead gate literal no longer appears in any command surface.
- The three mirrors are byte-identical.
