---
name: active-context-pointer-budget
description: "active-context.md is a POINTER FILE with a CONTEXT budget (≤20 KB ≈ 5k tokens, bytes÷4); prune = TRIAGE where deletion is a normal outcome — stale/superseded/already-recorded text is DELETED outright, archive is only for text with no other home."
metadata:
  type: feedback
  originSessionId: d1bc5de1-b28b-40c0-a47b-3d0e4c6de41a
  modified: 2026-07-27T04:31:53.924Z
---

**Operator rulings (2026-07-25, supersedes the old line-cap AND the old "compact, don't delete" preference —
this memory was renamed from `compact-dont-delete-on-closeout` because that name taught the wrong rule):**
`active-context.md` had grown to **~31k tokens** of narrative duplicating `sprint-status.yaml` + walkthroughs.
His words: *"it should just point to information that can be found, not rewrite the whole thing"*; *"lines is
not the issue anyway, it's context size"*; and — correcting my "never delete" overcorrection — *"we do need
to prune and delete."* If upkeep can't be handled, *"this becomes a bug, not a helpful thing to have."*

**The contract (baked into `/sudo-update-sprint-memory` Steps 4–5; AGY restructured 07-25, 31k → ~1.9k):**
- **Budget, not lines: ≤ 20 KB ≈ 5,000 tokens** (bytes ÷ 4). Report `~X / 5,000 tokens` every close-out.
  Over → prune in the SAME pass, one-in-one-out.
- **Entries are BORN as pointers** — ≤3 lines: outcome · STILL-OWED · pointer. Narrative goes to
  `sprint-status.yaml` + the walkthrough, NEVER active-context.
- **Prune = compact or DELETE — deletion is the normal outcome:** still-live → ≤3-line pointer; everything
  else → **delete**, git is the undo. Read before cutting — never let a STILL-OWED obligation die (the
  2026-07-13 OIDC-env loss is the cautionary case), and a standing ruling must live in memory/specs first.
- **`_archive/` is unmaintained COLD STORAGE, not a routing home** (his ruling, correcting my
  archive-everything overcorrection: *"I would prefer to just have a memory of relevant information"*):
  append-only dumps like a restructure snapshot, ZERO upkeep, nothing reads it routinely, never a mandatory
  copy step. Live docs reference it only as "if struggling with something that feels previously solved,
  grep `_archive/` + git history before re-deriving a fix."
- **The map** — one home per kind of information; point at it: sprint-status = ledger · walkthrough =
  narrative · `sudo-code-review-<story>.md` = findings · component-specs / project-context = rules ·
  `known-pitfalls.md` = pitfall long-tail (**grep-scoped, never bulk-loaded**; prune-on-touch moves entries
  into component specs) · Claude memory = cross-session.

**A second way obligations die — a backwards merge, with NO conflict marker to warn you (2026-07-27).**
Reconciling `main` → `main_debug` hit a conflict in `active-context.md`. Both sides were legitimate prunes
authored on different branches; `main_debug`'s was newer, so newest-wins is the right call **for the
narrative**. It is the wrong call for **OWED**: main's older side still carried *"seed live LLM rates
(`seed_pricing_config.py`, 11.9)"*, which `main_debug`'s newer file had already dropped and which survived
only inside an epic-11 retro. Taking `--ours` wholesale would have deleted it permanently, and git would
have reported a clean resolution. Two other main-only OWED lines were checked and correctly dropped (PITR
already enabled; the 11.18 attorney sign-off lives in `component-specs/legal-pages.md`), and one —
*"Bug 7 (21.7) — school code validation bypass"* — corroborated nowhere and was treated as mis-transcribed
rather than invented onto the board.

**The rule: resolve the narrative by newest-wins, but diff the OWED lists item by item.** Because this file
is pruned aggressively and independently on parallel branches (today: story worktrees landing on the epic
branch — the file is edited there, never in the shared `main` checkout), a merge in *either* direction can
drop an obligation with no marker. For each OWED line only one side has, ask: discharged, re-homed, or about to
die? Only the third needs recovering, and grep the repo to tell them apart.

**How to apply:** never write a narrative paragraph into active-context; the budget check is as mandatory
as the status flip; delete confidently once the STILL-OWED check is done. Same triage applies to stale
memory files and pitfalls. AGY is restructured; other projects get the same treatment when next touched.
Related: [[settled-decisions-are-not-gaps]], [[landing-is-not-closeout]].
