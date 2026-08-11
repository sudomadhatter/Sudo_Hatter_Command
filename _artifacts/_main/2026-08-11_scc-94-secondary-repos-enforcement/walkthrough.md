# SCC-94 — walkthrough

**`secondary_repos` is now enforced.** `test_task_preflight` **48 → 75** (9 cases built here,
16 more added after the review found the parser had no floor — see the Code Review section, which
carries the authoritative findings). `run_all` 12/12 exit 0 · `workflow_lint --toolkit-only` 0/0
exit 0 · `sop_currency` exit 0.

⚠ The section below records the two bugs I caught **while building**. The review then found a
BLOCKER and four MAJORs I had not — most notably that this commit's own documentation taught an
edit which silently disabled the check. Read the Code Review section for the real defect list.

Verified end to end against the live **SCC-88** lane, not only fixtures:

```
[INFO ] secondary: Projects/AGY_AVIATIONCHAT: empty stub in this lane (submodules do not
        populate in a worktree) - verified in the shared checkout at …/Projects/AGY_AVIATIONCHAT
[INFO ] secondary: Projects/AGY_AVIATIONCHAT: AVCH-53 matches its jira.conf (AVCH)
-- 0 error(s), 1 warning(s), 107 info --   VERDICT: clear to close out and merge
```

## The two bugs I found in my own work

**1. `\s*` swallowed the line break.** `secondary_rows()` matched `^secondary_repos:\s*(.*)$`
under `re.MULTILINE`. `$` matches *before* a newline, but `\s` matches the newline **itself**, so
`\s*(.*)` ran past the line end and captured the next line. Every block-form manifest read as an
"inline form", and every declared repo went unverified behind a warning that looked like a
manifest style complaint. Caught because the positive control that had passed during RED started
*failing* after the implementation — more cases failing after writing the feature was the tell.
Fixed with `[^\S\n]*` (horizontal whitespace only).

**2. ⭐ It blocked every cross-repo close-out, in the one place close-outs happen.** The first
version resolved the secondary repo only under the lane. **Submodules do not populate in a
worktree** — `Projects/<name>/` is an empty stub in every lane — so the real SCC-88 lane got:

> `ERROR secondary: Projects/AGY_AVIATIONCHAT: declared as a secondary repo but not a git checkout here`

All nine fixtures were green when this was true. They built the secondary inside a plain repo, so
they never modelled the only environment that matters. Now it falls back to the main worktree's
checkout — which is not a workaround: submodule content is **shared**, so there is exactly one
checkout of that repo and one branch state to verify — and it says which checkout it used. Pinned
by a test that builds a **real linked worktree** with the secondary present only in the main
checkout.

That test also corrected a wrong assertion of mine: I asserted `code == 0`, but a live lane always
warns that its worktree is still checked out, which is exit 1. The property under test is that the
check does not **block** (exit 2), and it now says so.

## Design note kept in the code

The blocking/reporting split is the load-bearing decision and the comment above `check_secondary`
carries it: project-store defects cannot fail `run_all`, because a lobby gate that reds for a
defect nobody in the lobby may fix blocks every unrelated lane. At close-out that objection does
not hold — the lane declared the cross-repo work, so it can commit there.

`store_problems()` imports `check_store` from the gate rather than reimplementing it: a second
copy of "what makes a store valid" would drift from the one `run_all` enforces. In this repo
`.agents/scripts/tests/` **is** the enforcement layer, so the dependency is not a test/production
inversion. An import failure is reported as a warning, never swallowed — a check that quietly
becomes a no-op when its dependency moves is worse than no check, because the green still looks
earned. Both the "it read the store" and "a seeded defect fires" halves were verified directly
against AGY's real store rather than inferred from silence.

## Doors and docs

The command body crossed into a stale-mirror state: `.opencode/commands/smh-close-task-merge-tree.md`
is a **full 16.4 KB mirror**, not a stub, so editing the command left it out of date. Re-synced —
all four doors current, and the change is scoped to that one command plus the sync manifest.

Noted in passing, **not fixed here**: `workflow_lint --toolkit-only` reported 0 errors / 0 warnings
while that mirror was stale. A generated door can silently drift from its command and the lint does
not see it. That is its own ticket.

The SOP row for `/smh-close-task-merge-tree` never mentioned the manifest at all. `sop_currency`
passed anyway, so this was added rather than taken as permission to skip — a cross-repo close-out
can now be blocked by *another repo's* state, which is exactly the kind of thing an operator has to
learn before it happens, not during.

## Scope held

The AGY-side memory gate stays an AVCH ticket. Repo-local enforcement never centralises; this is
the half the command center actually owns.

---

## Code Review (2026-08-11)

Verdict: PASS @ 46622dc
Suite evidence measured at `46622dc` — the sha carrying every fix. The review opened at
`5dfe233` as **CONCERNS** (one BLOCKER, four MAJOR); all applied and re-measured here, so the
verdict is stated at the code that will land, not the code that was reviewed. Only this
doc-line changes after `46622dc`.
**The review found the feature had no floor.** The parser could not distinguish *"no secondary
repos"* from *"I could not read the secondary repos"*, so its green was only as trustworthy as the
manifest's whitespace. That is the same class of defect this ticket was written to close, one layer
down.

**Scope** — the 10-file diff of `chore/SCC-94-secondary-repos-enforcement` vs `main`.
**Method** — clean-room adversarial hunt in a subagent with no conversation context, acceptance
audit against A1–A8, command-centre gate, Step 0.7 re-derivation.

### Findings

| file:line | severity | failure scenario | disposition |
|---|---|---|---|
| `task_preflight.py:225,233` | **BLOCKER** | `secondary_rows()` returned `([], None)` — verified nothing, said nothing, exit 0 — for **four valid YAML spellings** of a declared block list, each carrying a ticket key the target repo *rejects*. Worst case was self-inflicted: this commit's own template shipped `secondary_repos: []` above a **commented** block, so uncommenting it (the edit the comment invites) left the `[]` to win `re.search`. The documentation taught an edit that silently disabled the check. | **applied** — every branch that finds the key now returns `unparsed` rather than an empty list; `unparsed` is an **ERROR**, not a warning. Handles two keys, zero-indent blocks, `secondary_repos :`, bare `-` items, and a mapping key before any item. The template no longer ships a commentable second key. |
| `task_preflight.py:233` | MAJOR | A column-0 comment mid-list read as a dedent and truncated the list: a second declared repo carrying a rejected key was dropped with **no output at all**. Partial parses read as coverage. | **applied** — comments and blanks are skipped at any indent, as YAML requires. |
| `task_preflight.py:323` | MAJOR | A secondary with no `jira.conf` fell through to the success branch and printed `matches its jira.conf ()` — a claimed verification whose own empty parens prove it never happened. `check_branch` already warns correctly for the primary. | **applied** — now warns, matching its sibling. |
| `task_preflight.py:264` | MAJOR | `check_store` reads with plain `read_text(encoding="utf-8")`; one cp1252 byte in a project's `MEMORY.md` raised `UnicodeDecodeError` **out of** `store_problems`, killing the run at **exit 1** — which this script grades as *warnings* — with no `VERDICT` line, and since this check runs first, the deployable-lane question the script exists to answer never ran. | **applied** — the call is guarded as well as the import; an unreadable store is reported, never raised. |
| `task_preflight.py:335` | MAJOR | Detached HEAD → `rev-parse --abbrev-ref` returns `HEAD`, and the code queried `origin/HEAD...HEAD`, blocking with "never pushed" or a bogus ahead/behind. **Detached is what `git submodule update --init` produces**, so every submodule on a fresh clone hit this. | **applied** — detached is detected and the SHA checked for remote containment instead. |
| `task_preflight.py:300` | MINOR | Only `Projects/<name>` resolved; the repo's own only non-empty manifest (SCC-62) writes bare names, giving a hard block whose printed remedy cannot succeed. | **applied** — both spellings resolve. Swept all 15 committed manifests: **0 newly block.** |
| `task_preflight.py:293` | MINOR | `landing:` was parsed and never read — `retain-on-epic`, documented as "must never be presented as merged to production", was treated identically to `independent-task`. The decorative-field failure this ticket indicts. | **applied** — an unrecognised `landing` errors, and `retain-on-epic` now suppresses the landed-check. |
| `task_preflight.py:323` | MINOR | `ticket: AVCH` (a project key, no number) passed and was reported as a match. | **applied** — rejected. |
| `task_preflight.py:243` | MINOR | `#` inside a value truncated it (`Projects/C#App` → `Projects/C`). YAML opens a comment only after whitespace. | **applied** — `_scalar()`. |
| `test_task_preflight.py` | MINOR | A5's two refusals were implemented and **completely untested**; no case for a missing `repo:` either. | **applied** — 16 new cases; every parser case mutation-proven to fail against the original. |
| `smh-close-task-merge-tree.md:141` | MINOR | The Step 1 reading guide gained no `secondary` row, so the new blocking check is documented everywhere except where the operator is told to look. | **deferred** — the command body and SOP both carry it; the Step 1 table is a separate edit better made where SCC-90's restructure lands. |
| `implementation_plan.md` | NIT | "6 of 8 failing … the three that should pass" — 6+3=9, not 8. | **applied** — corrected below. |

### Gates — actual output

- **Enforcement suite** — `python3 .agents/scripts/tests/run_all.py` → `12/12 files passed`, **exit 0**
- **Preflight suite** — `python3 .agents/scripts/tests/test_task_preflight.py` → `-- 75/75 passed --`, **exit 0** (48 pre-task → 59 → **75** after review). The many `N error(s)` lines inside are fixtures asserting the preflight *blocks* correctly.
- **Toolkit lint** — `--toolkit-only` → `-- 0 error(s), 0 warning(s), 8 info --`, **exit 0**
- **SOP currency** — **exit 0**
- **Door parity** — re-synced after the template edit; the `.opencode` full mirror updated, both launcher skills and the Antigravity stub current
- **A gate must reject AND allow** — both halves proven: 16 refusal cases, plus negative controls that an absent key, `[]`, and `[] # comment` stay silent, and that a correct declaration still exits 0

### Acceptance

| item | proving assertion |
|---|---|
| A1 resolves incl. from a worktree | real-linked-worktree fixture; verified live on the SCC-88 lane |
| A2 key matches the target's `jira.conf` | mismatch blocks; **missing conf now warns** (was a false match) |
| A3 clean + `0/0` | dirty and unpushed fixtures block; **detached handled** |
| A4 store passes `check_store()` | seeded-orphan fixture blocks; unreadable store reported not raised |
| A5 no silent pass | 6 spellings + inline form + missing `ticket:`/`repo:`, all mutation-proven against the original parser |
| A6 negative controls | correct declaration exits 0; no store yet is not a failure; `[]` unchanged |
| A7 doors + SOP | re-synced, pasted above |
| A8 gates | pasted above |

### Clean-Code Gate

Machine floor green. Step 1's drift/bloat pass imported per Step 3.5: no over-engineering or dead
code found; the reviewer independently cleared CRLF handling, tabs, quoted values, ahead/behind
ordering, `worktree_main_root` across plain/nested/bare/submodule cases, and import side effects
(16 ms, no I/O). `except Exception` scope was flagged as too broad on the import and is now
deliberate on both import and call, each with the reason written at the line.

### Step 0.7 — re-derivation against current `main`

1. **Nothing moved under this diff.** `origin/main` = `main` = merge-base = `50e357b`; **0 files
   landed** since branching.
2. **True overlap with `main`: none;** `merge-tree` clean.
3. **Landing order.** `_artifacts/_main/INDEX.md` conflicts with SCC-88, SCC-83 and SCC-90 —
   mechanical, keep every row. ⚠ **`docs/_scc_sops_prds/workflows_testing_SOP.md` conflicts with
   SCC-90**, which rewrites that file wholesale (1,294 insertions / 695 deletions) and **no longer
   contains the paragraph this diff edits** — so the resolution is not mechanical: the enforcement
   note must be re-placed in the new structure whichever order they land. `.gitignore` conflicts
   against SCC-77 are not from this diff: SCC-77 is **31 behind main** and independently re-fixes
   what SCC-73 already landed there.

## Merge Reconciliation (2026-08-11) — landing #3

Verdict: PASS @ (this commit) — re-measured after absorbing `main`; supersedes `PASS @ 46622dc`,
which was measured before SCC-90 and SCC-89 landed.

**Why a re-measure was required, not optional.** The original verdict was true about a `main` that
no longer exists. Two lanes landed underneath this one:

| Landed | sha | What it did to this lane |
|---|---|---|
| SCC-90 | `0b380d4` | rewrote `workflows_testing_SOP.md` end to end |
| SCC-89 | `238e0ec` | relocated the migrations kit; added 2 ledger rows |

**Conflicts, and how each was resolved:**

| File | Shape | Resolution |
|---|---|---|
| `_artifacts/_main/INDEX.md` | ledger — 1 row ours, 3 rows theirs, no deletions either side | **kept all 4.** SCC-94's row on top, because this lane lands last and the table is newest-first. Never picked a winner. |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | ⚠ **not mechanical** — SCC-90 rewrote the file and the paragraph this lane edited no longer exists in that form | took `main`'s file whole, then **re-authored** the `secondary_repos` content into the new structure. |

**The SOP content was re-placed, not pasted.** SCC-94's original edit was one 900-word table cell —
the shape the old flat reference page used. The rewrite has two reading levels, so the content was
split to match: a **spine** paragraph plus a copyable `task.yaml` block in
§7's `/smh-close-task-merge-tree` section (what you do), and a `ⓘ` **aside** carrying the three
"why"s (unreadable-is-an-error, why the clean/pushed check has no substitute, and why the ordering
warning is load-bearing). The §17 reference row gained one sentence pointing back at §7. Pasting the
old cell into the new file would have produced a page that contradicts its own stated format — which
is the failure mode a rewrite-versus-edit conflict always has, and why git cannot resolve it.

### Gates after the reconcile (bare)

```
python3 .agents/scripts/tests/run_all.py                  -> exit 0   12/12 files passed
python3 .agents/scripts/workflow_lint.py --toolkit-only   -> exit 0   0 errors, 0 warnings, 8 info
python3 .agents/scripts/tests/test_sops_prds_folder.py    -> exit 0   16/16 passed
python3 .agents/scripts/tests/test_task_preflight.py      -> exit 0   75/75 passed
SOP link + anchor sweep                                   -> 77 links, 0 dead
```

`test_task_preflight.py` 75/75 is the one that matters: this lane's own assertions still gate after
absorbing a rewrite of the document they describe.
