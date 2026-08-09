---
IsArtifact: true
ArtifactMetadata:
  title: Artifacts rule hardening — read the local law, fix the dead lobby pointer, record the verdict home
  type: implementation_plan
  date: 2026-07-26
---

# Artifacts rule hardening

## Why

A verification pass over story 21.3's artifacts (asked for after a run of hand cleanup + re-indexing)
found the *placement* correct — `Projects/AGY_AVIATIONCHAT/_artifacts/epic_21/story-21-3-student-archive-never-delete/`
holds `implementation_plan.md` + `self-audit-stress-test.md` + `walkthrough.md`, matching its four siblings,
landed on `main_debug` at those paths, nothing loose at the `_artifacts/` root, nothing leaked to the lobby.

Three real defects sit underneath that, and they are why misplacement recurs.

### D1 — the rule never says to read the folder's own instructions

`.agents/rules/artifacts-always-first.md` §2's project-local branch names `active-context.md`/`INDEX.md`
and says "follow its rules" — but never instructs the agent to **open** `<project>/_artifacts/AGENTS.md`,
the file that actually is the local law. That file carries buckets the global rule does not contain at all:

| Work type | project local law | what the global rule alone produces |
|---|---|---|
| debugging / ad-hoc | `debugging/<YYYY-MM-DD>_<slug>/` | `_main/<YYYY-MM-DD>_<slug>/` ❌ |
| TEA / non-numeric story id | `tea/<story>/` | `<YYYY-MM-DD>_<slug>/` ❌ |
| structured debug epic | `epic_debug_<N>/<story>/` | not mentioned ❌ |

Story work survives only because `epic_<E>/<story>/` happens to appear in both. Every debugging and TEA
session written by a rule-only agent lands in the wrong bucket — which is the cleanup being done by hand.

### D2 — the code-review verdict has two competing homes

Rule §6 + a Hard Stop: every code review MUST be `code-review.md` in the session folder.
`.agents/commands/sudo-code-review.md:87`: write `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md`.
Epics 11–12 followed the rule; epic 15 onward follows the command (20+ files). 21.3 followed the command,
so its story folder has no `code-review.md`. Both are readable; a reader trusting the rule looks in the
wrong place.

### D3 — a dead pointer, repeated in three live files

`_artifacts/AGENTS.md:24`, `_artifacts/README.md:1,10`, `_artifacts/INDEX.md:5` all direct the reader to
the lobby bucket `_artifacts/aviationChat-AGY/`. That path does not exist — the Claude bucket is
`_artifacts/AGY_AVIATIONCHAT/`; `aviationChat-AGY` survives only as opencode's namespace
(`_artifacts/opencode/aviationChat-AGY/`) under a pre-rename folder name. An agent trusting the pointer
creates a second bucket. (`_archived/` + historical walkthrough hits are immutable history — untouched.)

## Explicitly NOT in scope — the INDEX-row append

An earlier draft proposed making "append a row to the project's `INDEX.md`" a per-session obligation.
**Dropped on the operator's call.** The ledger already has machinery: the SessionStart hook chain runs
`check_maps.py --depth3-only` ("Checking depth-3 _artifacts INDEX...") and `record_map_changes.py --nag`,
and `/update-maps-indexes` does the real reconcile — run deliberately, with cheaper agents. The rule
should point at that machinery, not duplicate it into every session. Placement is the per-session
obligation; the ledger is reconciled in batch.

## Files touched

| File | Change |
|---|---|
| [.agents/rules/artifacts-always-first.md](../../../../../.agents/rules/artifacts-always-first.md) | D1: read-the-local-law-first mandate (blockquote + §2 + a Hard Stop) · D2: §6 records the sudo-lane verdict path · the ledger note pointing at the hook + `/update-maps-indexes` |
| [Projects/AGY_AVIATIONCHAT/.agents/rules/artifacts-always-first.md](../../../Projects/AGY_AVIATIONCHAT/.agents/rules/artifacts-always-first.md) | hand-vendored copy — byte-identical to master today, re-copied after the edit |
| [Projects/Fresh_Workspace_BMAD/.agents/rules/artifacts-always-first.md](../../../Projects/Fresh_Workspace_BMAD/.agents/rules/artifacts-always-first.md) | same (living-template-sync) |
| [Projects/AGY_AVIATIONCHAT/_artifacts/AGENTS.md](../../../../../Projects/AGY_AVIATIONCHAT/_artifacts/AGENTS.md) | D3 line 24 |
| [Projects/AGY_AVIATIONCHAT/_artifacts/README.md](../../../../../Projects/AGY_AVIATIONCHAT/_artifacts/README.md) | D3 lines 1, 10 |
| [Projects/AGY_AVIATIONCHAT/_artifacts/INDEX.md](../../../../../Projects/AGY_AVIATIONCHAT/_artifacts/INDEX.md) | D3 line 5 · backfill the 5 missing `epic_21` rows |

`/sync-agents` copies commands + skills and **never rules** — the two project copies are hand-vendored.

## Order

1. Edit the lobby master rule (D1, D2, ledger note).
2. Copy it verbatim to AGY + Fresh.
3. Repair the three D3 pointers.
4. Backfill the five `epic_21` INDEX rows — kept in scope despite the batch machinery because the "What"
   column needs story knowledge a mechanical pass does not have.
5. Verify: `grep -rn "aviationChat-AGY"` shows zero live hits · `grep -c epic_21` on the INDEX shows 5 ·
   the three rule copies diff clean.
6. One commit per repo (lobby, AGY, Fresh) — never cross-commit.

## Open questions

None. Scope confirmed item-by-item by the operator; the INDEX-append item was withdrawn on their call.

## Verification plan

- `diff` the three rule copies → identical.
- `grep -rn "aviationChat-AGY" --include=*.md` over the three live files → zero.
- `grep -n "epic_21" Projects/AGY_AVIATIONCHAT/_artifacts/INDEX.md` → 5 rows.
- `git status` clean in all three repos after their commits.
