# SCC-456 — the teaching edition you share is generated, and its generator had never reached `main`

**Lane:** `chore/SCC-456-teaching-edition-export` · worktree `.claude/worktrees/SCC-456-export` ·
cut from `origin/main` @ `5f9062a9`
**Plan:** [implementation_plan.md](implementation_plan.md) · Audit verdict GO · approval recorded at `a52016e1`
**Published PR:** [sudo-command-center#1](https://github.com/sudomadhatter/sudo-command-center/pull/1)

---

## What this was, and why the ticket's own scope was the wrong fix

The ticket said four doors in `Projects/sudo-command-center` had drifted and should be reconciled by
hand. Measurement said that was the wrong fix, and the reason matters more than the drift.

**That repo is generated.** It is a sanitized export of this lobby, produced by
`export-teaching-edition.ps1` from `lobby.manifest.json`, and nothing ever flows back. Hand-editing
four door bodies would have been deleted by the next export — and, far worse, a hand edit never
passes the **leak scan**, which is the only thing standing between this workspace and a public
repo. The four drifted doors were a third of one fact: **the export had not run**, because its
engine lived on `origin/claude/teaching-edition`, a branch `main` had never seen, 396 commits stale.

A second and worse defect surfaced on the way: **the publish step could not delete.** The exporter
refuses a non-empty target, so publishing was "export to a folder and copy it over the repo" — and
a copy adds and overwrites but never removes. Every command retired upstream was still in every
reader's clone.

---

## What landed

**Part A — the engine on `main`.** Five paths ported from `origin/claude/teaching-edition` @
`8739a892` and nothing else: the exporter, the manifest, `replacements/`, the validator and its
test. The branch's edits to four tests, `jira.md` and three INDEX files were 396 commits stale and
were deliberately not carried. Five drifted manifest anchors repaired against `5f9062a9`; three dead
`exclude` rows pruned and two kept that only look dead.

**Part B — the overlay.** A new `overlay` block ships `/smh-tour`, `/smh-training`, the training-mode
rule and the `.training-mode` sentinel into the published edition without putting two unused doors in
this lobby. Four pinned properties: a missing source fails, an undeclared file under `overlay/` fails,
a collision with the copy pass fails, and **overlays run before substitutions and before the leak
scan**. That ordering is the safety property — copy-last is the natural implementation and it is a
hole straight through the only guard this export has.

**Part C — provenance, the publish door, the staleness line.** The export stamps
`.teaching-edition-source` with a source sha and two dates and nothing else, written after
substitutions and before the leak scan, failing closed if the sha cannot be read.
`/smh-publish-teaching-edition` lands on five surfaces and is the door that makes deletion real.
`teaching_edition_staleness.py` runs at SessionStart from `.agents/hooks/session-start-context.sh`
and reports when the published copy is more than 14 days behind `main`.

**Part D — the publish.** Export, clear the tracked tree, copy, review, PR. 69 added, **86 deleted**,
286 modified.

---

## The corrections — things I asserted that were wrong, and what measurement said instead

### The planned RED was fiction

The plan asserted that `pwsh … -WhatIf` would throw on the first drifted manifest anchor. **It does
not.** `-WhatIf` skips the substitution and line-prune passes entirely, so it exits 0 against a
manifest that cannot run. The real red came from a real export, at `export-teaching-edition.ps1:336`
— it named the index of the workflow surface SCC-394 had retired, which no longer exists.

This is exactly what red-first exists to catch, and it is recorded here rather than quietly fixed:
the plan keeps its approved text, and the correction lives in this record and in the commit that
landed Part A.

### The leak scan does not catch what the plan said it catches

The plan called *"a planted `dlohneiss` makes the export fail"* **the one assertion that matters
most**, because that scan is what guards a public repo. Run against the real manifest, twice:

| Probe | Result |
|---|---|
| needle in a file's **content** | `TEACHING EDITION VALID` — **not caught by the scan** |
| needle in a file's **name** | `LEAK SCAN FAILED`, 4 hits |

The content needle was rewritten to `your-user` by the substitution pass, which runs *before* the
scan — so the needle never reached the scanner and never reached the shipped file either. **The leak
did not ship, but substitution is what stopped it, not the scan.** Filenames are never substituted,
so there the scan is the only guard and it is the one that fires.

All 13 content needles also have substitution rules, so the content half of the scan can essentially
never go red on a *known* needle. That is defence in depth rather than a hole — the two lists cover
each other, and a needle with no substitution rule still reaches the scanner — but **a green leak
scan proves less than the plan assumed**, and that sentence is worth having written down.

### Two wrong diagnoses before the right one

A suite failure looked like a wall-clock flake in the RUNALL concurrency case, then like load
contention from this lane's heavy exports. Both readings were artifacts of grepping `^-- [0-9]+/`
over the output, which matches the per-block tallies and hid the `FAILED:` line under them. Running
the file and reading its tail named the real cause immediately: my `pwsh` guard called `c.check`
outside a `c.block`, which breaks the `--case` filter contract.

---

## Defects this lane found and fixed

1. **The exported shell's own commit gate refused a fresh clone's FIRST commit.** The tutor doors
   ship but the SOP never named them. The SOP rows are injected at export time by the same
   `lineTransforms` mechanism that prunes the sentry rows, so this lobby gains nothing it does not use.
2. **`/smh-new-project` could report success on a project whose first commit FAILED**, leaving a repo
   with no `HEAD`: `| Out-Null` swallows git's output and PowerShell does not stop on a non-zero
   native exit code. `init`, `add` and `commit` are all checked now. It also accepted a name that
   traverses out of `Projects/` or names a Windows device, and it set `JIRA_KEYS` without
   `JIRA_SITE` — a key prefix is half an address, so the CLI validated against whatever board the
   machine happened to be logged into.
3. **The SOP linked to files the export excludes**, which the shipped validator caught by name
   ("live SOP contains dead local link"). A reader's copy would have had dead links on the page they
   are told to read.
4. **My own arming guard was vacuous.** The case proving the staleness reporter is armed searched the
   whole hook file, and the block's own comment names `test_teaching_edition_staleness.py`, which
   contains `teaching_edition_staleness.py` as a substring — so it was satisfied by the comment
   explaining the guard and would have stayed green with the arming line deleted. Found by *designing*
   the mutant table, not by running it. Comments are stripped now.
5. **The publish door would have pushed straight to `main` of a public repo.** Found on the door's
   first live run. The published repo is checked out on `main`, so `git push origin HEAD` lands the
   whole refresh on `main` with no PR — and `gh pr create --head main` cannot open one either, so the
   door could not have completed. Step 4 cuts `chore/publish-<short-sha>` first; cases F7 and F8 pin it.

---

## Evidence

| Gate | Result |
|---|---|
| `run_all.py` | **95/95 files** @ `a74f3d9c` (94 before; this lane adds one file) |
| `test_teaching_edition.py` | 63/63 (47 at the start of Part C) |
| `test_teaching_edition_staleness.py` | 18/18, arming rows seen RED before the hook was armed |
| `test_command_surfaces.py` | 345/345 |
| `test_twin_parity.py` | 76/76 |
| Export | `TEACHING EDITION VALID` |
| Leak scan | clean — 42 needles, 0 hits (contents AND paths) |
| Independent needle grep over the published tree | 0 for every needle; `sudomadhatter` appears only in GitHub clone URLs readers need |
| `workflow_lint --toolkit-only` | 0 errors, 0 warnings |
| `check_maps --depth3-only --strict` | clean |
| Residual, lobby masters vs export | 40 doors / 3,530 lines → **0 and 0** |

### Mutation sweep — one table, 4/4 killed, restore verified byte-identical @ `c660f61b`

| Mutant | Killed by |
|---|---|
| M1 the door's clear stops deleting but still matches the extractor | `F2 · a tracked file the export no longer carries is GONE` |
| M2r the whole provenance pass stops running | `E4 · an unstampable source FAILS the export` |
| M3 the stamp gains a fourth key (the source PATH) | `E3 · it carries ONLY a sha and two dates` |
| M5 the stamp is written after the leak scan | `E5 · the stamp is written BEFORE the leak scan` |

**M2 as first aimed SURVIVED** — it disabled one of two guards and the second caught it, so it
removed no behaviour. Re-aimed at the whole pass, it killed.

**M4 (WIDTH: narrow the 40-char sha check to any hex run) SURVIVED and is DEFECTIVE, not a coverage
gap.** `git rev-parse HEAD` cannot return a short sha, so the narrowing admits nothing. Dropped
rather than answered with a test for a hole that does not exist; E5 covers the property it was
reaching for.

---

## Your Actions

- **Merge [sudo-command-center#1](https://github.com/sudomadhatter/sudo-command-center/pull/1)** —
  the public repo. 69 added, **86 deleted**, 286 modified. The deletions are the payload: 42
  retired workflow files, 33 consolidated design skills, the v2 autopilot lane, `/smh-quick-fix` and
  its mirrors. Leak scan clean, 0 hits on 42 needles, contents and paths.
- **Then bump the submodule pointer.** After you merge, in the lobby:
  `cd Projects/sudo-command-center && git switch main && git pull`, then
  `git add Projects/sudo-command-center` and commit. The submodule is currently checked out on
  `chore/publish-a74f3d9c`; the lane deliberately does not stage the pointer, because until you
  merge it would name a commit that is not on the published `main`.
- **Merge the lobby PR for this lane** the usual way.

## Still open, named once with its remedy

`sudo-project-skeleton` is the *other* living template and it still has **no drift detector** — the
same engine away, a second manifest sourced from a real project. `living-template-sync.md` now states
which of the two is detected and which is not. Its own ticket, after this one.

---

## Code Review

Pending — `/smh-code-review` runs next in this lane.
