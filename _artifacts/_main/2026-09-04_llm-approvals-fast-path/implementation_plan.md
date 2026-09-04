# Implementation Plan — /smh-llm-approvals carries its own landing road (SCC-393)

**Date:** 2026-09-04 · **Lane:** `_artifacts/_main/2026-09-04_llm-approvals-fast-path/`
**Branch:** `chore/SCC-393-approvals-fast-path` (cut from `origin/main` @ `70154040`)
**Parent subject:** SCC-392 (the harvest that measured the cost)

## The problem, measured on the run that produced it

`/smh-llm-approvals` ran end to end on 2026-09-04 and routed 12 allow rows into the shared
source. Writing those 12 rows took minutes. Everything around them took the rest of the day.

The door is 281 lines and describes Steps 1-4 in detail, but **Step 4 is
`Report what changed … Then stop.`** — it names no road to `main`. So the agent is left holding
four modified tracked files (`families.json` plus its three renders) with no procedure, and
improvising next to `main` means the heaviest thing in reach: a plan, a worktree, an
assert-first cycle, a five-lens review, a PR, and a CI round trip.

Four more gaps compounded it, each one a sentence the door does not carry:

| Gap | What it cost, measured |
|---|---|
| The door never names `test_permission_parity.py` | All 17 picks were written, THEN the battery reported A3/A5/A6/B8 red. Five picks (`gh`, `env -u GITHUB_TOKEN gh`, `acli`, `chmod`, `npx`) had to be found and backed out by hand, one at a time |
| The door never says the applies need the Bash sandbox off | `antigravity_permissions_apply.py --apply` died `OSError: [Errno 30] Read-only file system` on `~/.gemini/`; the same class hit `.claude/settings.local.json` in Step 1, which the door DOES warn about |
| The door names NO road at all | `main` is protected, the direct push was rejected, and the road was re-derived live — twice. ⛔ The first cut of this fix wrote the *wrong* road into the door (local merge + minted token + `git push origin main`); `git-policy.md` bans all of it for every door in this repo, and the review caught it |
| `lane_qualify.py` answers `TASK` for any `.agents/permissions/` path | Correct for a hand edit, but it is the machine signal an agent reads when deciding how much ceremony to spend |

## The change — the door carries the road

### 1. `.agents/rules/artifacts-always-first.md` § "When to Skip"

`/smh-llm-approvals` becomes a **third named exemption**, in the same shape as the two already
there: *invoking the command IS the "skip the plan" instruction*, conditional on its own guards
staying intact.

⛔ **The exemption keys on the COMMAND, never on the path, and `lane_qualify.py` is deliberately
NOT changed.** The qualifier is a path classifier and it is right: a hand edit to
`families.json` outside this door has no operator pick, no forced render check and no forced
battery run, so it must keep the full lane. `/cicd-quick-dev` and `/smh-quick-fix` are both
command-named exemptions for exactly this reason. Widening the path rule would hand the same
pass to an edit that earned none of it.

The guards the exemption is conditional on, all four machine-checkable:

- the operator's live pick at the Step 2 gate — that IS the approval, already captured
- `permission_render.py --check` prints *in sync*
- `python3 .agents/scripts/tests/test_permission_parity.py` is green
- the diff is confined to `.agents/permissions/families.json`, `.agents/permissions/antigravity.json`,
  `.claude/settings.json`, `.vscode/settings.json` — anything else and the exemption is void

### 2. `.agents/commands/smh-llm-approvals.md` — Step 3 gains the fence check

Immediately after the render, before anything is reported: run the battery. A red row means the
pick damaged the fence — back **that** pick out, name the deny row that refused it, and tell the
operator which of his picks could not land and why. This is the step that would have cost minutes
instead of hours.

### 3. `.agents/commands/smh-llm-approvals.md` — a real Step 4, "Land it"

The road, explicit end to end: run the scope guard (not eyeball it), write a lean walkthrough
naming the picks and the operator's words verbatim, stamp it with `flight_recorder.py`, commit by
explicit path on a `chore/<KEY>-<slug>` branch, push it, `gh pr create`, **STOP**.

⛔ **The first cut of this step wrote the WRONG road** — `git checkout main && git merge --no-ff`,
`mint-push-token.sh`, `git push origin main`. `.agents/rules/git-policy.md` bans every one of those
for every door in this repo (*"No agent merges to `main`… no eligibility test, no 'small enough'
class, no self-merge"*, and *"No command may change which branch a checkout is on"*), and it
laundered a permission pick into merge permission — the SCC-37 substitution that rule names. The
review caught it; `test_door_preflight_order.py` now names this door so the suite catches it next
time.

Plus the one operational fact nothing stated: the applies need the Bash sandbox off, and the two
scripts **fail differently** — Antigravity raises `OSError: [Errno 30] Read-only file system` from
`write_text`, Zoo raises `sqlite3.OperationalError: attempt to write a readonly database`. (The
window reload was already in the door and is left alone; an earlier draft of this plan wrongly
claimed it as new.)

### 4. `.opencode/commands/smh-llm-approvals.md`

Byte-identical mirror, refreshed in the same commit. Pinned by the existing E4 check.

### 5. `docs/_scc_sops_prds/workflows_testing_SOP.md` (+ changelog)

A usage surface changed, so the armed `sop_currency` commit-msg hook rejects the commit that
leaves the SOP behind. The `/smh-llm-approvals` prose gains the landing half.

## Declared Change Set

- EDIT `.agents/rules/artifacts-always-first.md` — the third exemption + its four guards → 1
- EDIT `.agents/commands/smh-llm-approvals.md` — Step 3 fence check, new Step 4 landing road → 2, 3
- EDIT `.opencode/commands/smh-llm-approvals.md` — byte-identical mirror (E4) → 4
- EDIT `.agents/scripts/tests/test_permission_parity.py` — the H block, and A16/A16b for the `read_file` grant kind the command corpus cannot see → the assert-first section
- EDIT `.agents/scripts/tests/test_door_preflight_order.py` — add this door to `DOORS`, so the no-self-merge invariant is ENFORCED on it rather than merely true by omission → 3
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the landing half of the door's prose → 5
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one line → 5
- EDIT `.agents/commands/INDEX.md` — the door's row now names a landing step → 2
- NEW `_artifacts/_main/2026-09-04_llm-approvals-fast-path/walkthrough.md` — evidence, review, actions → the definition of done
- NEW `_artifacts/_main/2026-09-04_llm-approvals-fast-path/tickets/SCC-393.md` — the ticket outline → the definition of done
- EDIT `_artifacts/_main/INDEX.md` — this lane's row → the definition of done
- EDIT `docs/doc-graph.json` — REGENERATED by the armed `refresh-maps` commit hook, never hand-edited; it stages itself on every commit that touches `docs/`, so it is declared here rather than left to read as drift → 5
- EDIT `docs/doc-graph.md` — the same hook, the same reason → 5

⛔ **Not declared, and deliberately not touched:** `.agents/scripts/lane_qualify.py` and its test
(see the ⛔ in §1), the three rendered permission files, `permission_render.py`, and the two
machine-local Claude files.

## Assert first — what proves it, before it is written

A new **H block** in `.agents/scripts/tests/test_permission_parity.py`, against the real files:

- H1 the door body carries a landing step that names `gate/` — not a `Then stop.` ending
- H2 Step 3 names `test_permission_parity.py`, so the fence check cannot be skipped
- H3 the door states the applies need the sandbox off
- H4 the door states the VS Code window reload after the Antigravity apply
- H5 the rule's "When to Skip" names `/smh-llm-approvals` AND all four of its guards
- H6 the rule still tells a hand edit to use the full lane — the exemption did not widen to paths
- H7 `.opencode/` mirror is byte-identical to the master

Then the full suite: `python3 .agents/scripts/tests/run_all.py`.

## Definition of done

`run_all.py` green · `permission_render.py --check` in sync · the door reads end to end to
someone who was not in this session and leaves them holding no unanswered question about how the
change lands · review verdict recorded, then the landing.
