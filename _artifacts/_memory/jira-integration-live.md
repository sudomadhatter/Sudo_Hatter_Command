---
name: jira-integration-live
description: "Jira is LIVE for both repos as of 2026-08-07 — SCC (lobby) and AVCH (AviationChat). Every branch and commit carries a key; the commit-msg hook is ARMED (ENFORCE), so a keyless or wrong-project commit is rejected outright."
metadata:
  probe: 'test -d ~/.config/acli' 
  node_type: memory
  type: project
  originSessionId: 8bc78088-0a6e-4b75-b4eb-edc817c5fe79
  modified: 2026-08-08T04:47:43.953Z
---

Set up 2026-08-07 at `https://sudo-command.atlassian.net`. Two **team-managed** projects, one board
each (team-managed allows only one board per project; extra boards need a saved filter from **global**
nav, not from inside the project):

| Project | Key | Repo | Board | Sprints |
|---|---|---|---|---|
| Sudo Command Center | `SCC` | `Sudo_Hatter_Command` (lobby) | 2 | on — Sprint 1 active, runs to the Sep 1 soft launch |
| Aviation Chat | `AVCH` | `AGY_AVIATIONCHAT` | 3 | on |

**The join is a literal string.** Atlassian's *GitHub for Atlassian* app links a commit/branch/PR to a
work item by finding `KEY-number` verbatim — there is no other mechanism. It reads the **branch name**
too, so a correctly-named branch covers every commit on it even if one message forgets the key. See
[[git-branch-model-standard]].

**The gate is ARMED, in both repos.** `.agents/scripts/git-hooks/commit-msg-jira.sh` via a
`.githooks/commit-msg` shim; mode flag `.agents/scripts/git-hooks/JIRA-ENFORCE` is **tracked on
purpose** — untracked it would be armed on one machine and silent on every other clone. A commit with
no valid key for that repo is **refused**, and a rejected commit is a no-op (staged set untouched).
Each repo declares its project in `.agents/jira.conf`; an `SCC` key inside AviationChat is rejected by
design.

Exempt: merge/revert/fixup/squash subjects and in-progress rebases. Kill switch:
`.agents/scripts/git-hooks/DISABLE`. Bypass once: `--no-verify`.

**Deliberately NOT checked: whether the ticket exists.** A live lookup would put a network round-trip
on every commit and fail closed offline. A well-formed but wrong key is caught downstream — it simply
never appears on any ticket's Development panel.

**`acli` is the tool, not MCP.** `acli` 1.3.22, authenticated as `sudomadhatter@gmail.com`, token in
the credential store that side has - `acli`'s own mode-600 `~/.config/acli/` inside Ubuntu. One binary any model can shell out to — MCP would be per-tool config drifting
across all four platforms. Flag traps: `view` takes the key **positionally** (`--key` is only on
`transition`); `project list` needs one of `--recent/--limit/--paginate`; it's `board search` and
`board list-sprints --id N`, not `board list`; `comment create` needs `--key`; `transition` wants
`--yes` to skip its interactive confirm.

**This is now a platform-neutral rule (2026-08-08): `.agents/rules/jira.md`** in lobby AND AGY —
born because Gemini, knowing only the policy rules, claimed "I have no Jira integration" when the
authenticated CLI was sitting right there. The rule carries the cheat-sheet, flag traps, ticket↔file
join, and guardrails; pointed to from rules/INDEX.md, git-policy.md, push-e2e Step 6.5,
update-sprint-memory Step 4.5, the human guide's cheat-sheet section, and — after a fresh Gemini
session STILL missed it (its funnel never consults rules/INDEX.md for a status question) — named
directly in **AGENTS.md §3** of both repos: the one file every discovery path passes through.

**Statuses:** `To Do` · `In Progress` · `In Review` · `Done` · `Deferred`. `Deferred` sits in the
**`To Do` category** on purpose — a Done-category status would auto-resolve and make descoped work read
as *shipped*. Descoped work goes to `Deferred` + the `descoped` label (the two were merged; team-managed
can't customise Resolution). Saved filters are GENERIC, cross-project (re-cut 2026-08-07 late):
`Deferred` (10003), `Quick-Dev` (10005), `Parallel-OK` (10006), `Blocked` (10007), `Descoped` (10009);
the per-project `SCC Deferred` (10004) is retired-pending-UI-delete. Agents never use saved filters
(raw JQL only) — they are operator sugar. TWO UI traps that bit here: (1) "Save filter" stores the last
search that RAN — press Enter on the JQL before saving, or the filter silently captures the default
query (3 of 4 hand-made filters shipped broken this way; fixed via `acli jira filter update --id`).
(2) The setup-era filters each BACKED a user kanban board ("AVCH Deferred" board 4, "SCC Deferred"
board 5) — Jira refuses to delete a board-backed filter; delete the board first (boards directory →
row ⋯ → Delete), then the filter.

**Free-tier limits shape the design.** Jira Free caps automation at 100 runs/month, so the design leans
on **Smart Commits** (`#comment` `#time` `#transition`), which cost zero quota. GitHub Free cannot put
rulesets on private repos (verified `403`), so there is **no server-side block on `main`** — an alarm,
not a lock. Daniel committed to GitHub Pro 2026-08-07; once active, `main` becomes unpushable except
through a passing PR and the docs' "alarm not lock" sections need updating.

**Docs:** `docs/_scc_sops_prds/jira_integration_guide.md` (the why) and
`docs/_scc_sops_prds/jira_manual.md` (the by-hand how-to; relocated there by the operator 2026-08-07). Both carry a live-vs-not-built ledger — keep it honest.

**The AVCH board is populated (2026-08-07 evening, SCC-29):** AVCH-13 = Epic 12 (In Progress) with
AVCH-14/15/16 = 12.3 umbrella + 12.3.4/12.3.7 (In Review); AVCH-17..20 = Epics 18/19/20/22 (Deferred).
Open story files carry `jira_key:` frontmatter and sprint-status.yaml's header is `project_key: AVCH`
— done epics were deliberately NOT resurrected as tickets. Pairing: Jira summary carries the BMAD
number (`Epic 12 — …`, `12.3.4 — …`); the YAML row keys never change.

**Full-pipeline backfill (2026-08-07 late, operator-directed):** the deferred epics' CHILD stories are
now tickets too — AVCH-24..32 = 18.1–18.9, AVCH-33..36 = 19.1–19.4, AVCH-37 = 20.1, AVCH-38..40 =
22.1–22.3; all `Deferred`, parented to their epic ticket, created UNASSIGNED (omitting `--assignee`
creates bare — this is the fix for "why is everything assigned to me"). The board now mirrors every
non-done YAML row 1:1. Deferred stories have NO story files (files mint at kickoff), so no `jira_key:`
frontmatter exists for them — the join is the BMAD number in the summary + the "Board row:" slug in the
description. Done work stays off the board (bare-state ruling) — do NOT backfill epics 1–17/21/debug/TEA.

**Command wiring live (SCC-27/28, AVCH-11/12):** `/sudo-push-e2e` Step 6.5 comments evidence +
transitions the EPIC ticket at merge; `/sudo-update-sprint-memory` Step 4.5 moves the story ticket at
close-out; every branch template toolkit-wide reads `epic|claude|chore/<JIRA-KEY>-<slug>`.

**Minting seams live (SCC-44/AVCH-41, 2026-08-07 late — operator released the human-mint rule):**
agents may mint tickets, at exactly two wired seams. `/sudo-create-epic-sprint` Step 1.5 mints the
EPIC ticket at kickoff (no more STOP-and-ask); `/sudo-write-story-tests` ① Step 1.6 mints the STORY
ticket at pickup — child of the epic ticket, bare, `jira_key:` stamped into frontmatter — and rules
three classifications as LABELS (labels stack, statuses don't — a story can be quick-dev AND blocked):
`quick-dev` (may ship via /sudo-quick-dev), `parallel-ok` (no file overlap with sibling lanes),
`blocked` (+ a `Blocks` link naming the blocker: `link create --out <blocker> --in <story> --type
Blocks`). A `Blocked` STATUS is wired as optional — the operator owes the one-time UI add per board
(acli cannot create statuses or saved filters); until then the label alone carries it. Speculative
minting stays banned — a ticket asserts a decided piece of work.

Still genuinely open on SCC: GitHub Pro / branch protection (SCC-19) and the Windows stale-stamp hook
removal (SCC-23). Docs refresh shipped as SCC-30 / AVCH-22; AGY's AGENTS.md went tier-2 as AVCH-23.
(acli quirk worth knowing: tickets create as the authenticated account — the site has one human
account, so everything shows "assigned to Daniel" unless created bare.)

**How to apply:** never invent a Jira number — read it from the ticket. Branch and commit with the key
for the repo you are standing in. See [[vscode-hides-git-hook-output]] for why a warning-only gate was
not enough.

<!-- CHECKPOINT id="ckpt_msjnn6ub_ve7no2" time="2026-08-08T00:48:05.987Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->
