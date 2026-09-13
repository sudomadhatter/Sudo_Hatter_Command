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
| `run_all.py` | **95/95 files** @ `e9d34b7a`, receipt at [gates/suite.json](gates/suite.json) (94 before; this lane adds one file) |
| `test_teaching_edition.py` | 72/72 (47 at the start of Part C; block G and F9-F13 came from the review) |
| `test_teaching_edition_staleness.py` | 19/19, arming rows seen RED before the hook was armed |
| `test_command_surfaces.py` | 345/345 |
| `test_twin_parity.py` | 76/76 |
| Export | `TEACHING EDITION VALID` |
| Leak scan | clean — 42 needles (13 declared + 29 from `.env`), 0 hits (contents AND paths) |
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

review-runtime: fan-out

## Code Review (2026-09-12)

### Step 0.7 — blast radius re-derived against current `main`

`main` was absorbed into this lane at `21922b71` (merge of `origin/main` `c53ee511`), so the
re-derivation runs against the tree that will actually exist.

1. **Did anything this diff references move on `main`?** No. `git diff --name-only <base>..origin/main`
   ∩ this lane's changed set is **empty** after the absorb. Every repo path the diff names was
   re-resolved by `check_links.py --base origin/main`: 2 unresolved, both inside the approved plan
   text, which names `.agents/workflows/INDEX.md` and `.agents/project-own.txt` as files that **no
   longer exist** — that is the sentence's point, and the plan cannot be edited after its approval
   stamp without breaking the approval gate.
2. **True overlap and merge state.** Six files overlapped before the absorb — `.sync-manifest.json`,
   `_artifacts/_main/INDEX.md`, the SOP, its changelog, and both doc-graph files. Five conflicted.
   The three **generated** ones were resolved by regenerating (`sync-agents.ps1`, `refresh_maps.py
   --repair`), never hand-merged; the two **row lists** kept both sides' rows, because SCC-456's
   rows and SCC-448's row are both true and there is no winner to pick. `git merge-tree` against
   `origin/main` now returns a clean tree with no conflict messages.
3. **Sibling lanes.** One live worktree, `chore/SCC-186-standing-push`; its remote branch has already
   landed (0 files vs `origin/main`), so there is no landing-order dependency in either direction.

`risk_seam.py classify` returns `unclassified` with empty tiers — the permanent, correct answer for
the command centre, which carries no code graph (SCC-289). Every judgement below comes from reading
the diff.

### The roster

review-runtime:  fan-out
lens_isolation:  shared — three lenses in their own clean contexts over one committed diff
lenses_run:
- correctness · ok
- gate-integrity · ok
- acceptance-auditor · ok
lenses_counted:  3/3
lenses_na:       none
findings:        11 fix (0 dropped — no reproduction · 4 recorded)
dispositions:    per-lens: correctness=4/0/0 · gate-integrity=3/0/4 · acceptance=4/0/0
drift:           3 undeclared groups, all judged legitimate — check_links.py + its test (the overlay's published-root links), test_twin_parity.py NOT_PAIRED (the new lobby-only door), and the generated mirrors (skills INDEX, .claude rules, doc-graph); plus new-project.ps1 and its door, which are real drift the operator authorised by name
severity_floor:  none
notes:           every critical and important reproduced; both test lenses proved their claims with mutants and restored byte-for-byte. No finding was dropped for want of a reproduction.

### What the review found — 1 critical, 10 important, every one mine

**The publish door's own destructive step could have deleted this workspace.** `critical`. Step 2
re-used `$LOBBY` and `$SCRATCH` from an earlier fenced block, with no `set -e` and no chaining. In a
fresh shell — every new terminal, every copy-paste, most tool calls — `PUB` computes to
`/Projects/sudo-command-center`, the `cd` fails, and `git ls-files -z | xargs -0 rm -f` then runs in
whatever directory the shell is standing in. The lens measured it deleting the lobby's tracked tree.
With `$SCRATCH` unset the copy source also becomes `/.`, the filesystem root, aimed into a public
repo. Both destructive blocks now re-derive their own paths, run under `set -euo pipefail`, and
refuse unless the scratch holds a real export, the target is a git repo, and its path ends in
`Projects/sudo-command-center`.

**A failed export's bytes were still copied into the public repo.** `important`. Nothing mechanical
sat between the exporter's exit code and the wipe-and-copy — the guard was a sentence telling the
reader to check the log. The lens planted a needle, watched the export exit non-zero on the leak
hit, and watched the needle land in the published tree anyway.

**An overlay could pull any file on the disk into a public export.** `important`. `from` was joined
to the manifest folder with no containment test, so `"from": "../../../.env"` shipped — and the leak
scan does not save you there, because it matches a fixed needle list, not "content that should not
be here". The copy pass has enforced exactly this containment since it was written; the overlay was a
second door into the same tree missing the same lock.

**An absent `.env` silently removed two thirds of the leak scan.** `important`. 13 declared literals,
42 needles at scan time — the other 29 are the live `.env`'s values, loaded behind a bare
`Test-Path`. A fresh clone, a CI runner or a worktree without the symlink has no `.env`, and the scan
then prints `clean` having checked a third of what it normally checks. Not an error: a quieter pass.
The manifest declares `leakScan.requireEnv`, the export stops without it, and the count now prints
its provenance.

**Three of my own new cases were vacuous, each proven with a mutant.** `important` ×3. `F7` said
"cuts a branch BEFORE it commits" and asserted only that the string existed somewhere — a
source-contains assert, which cannot see order. `F2`/`F3`, the rows proving the staleness reporter is
armed, grepped the whole hook file, and the script's name also appears in the `TE=` path assignment,
so repointing the hook's call at a different script left both green while the reporter never ran.
`K3`, the control proving the link-checker convention narrows, proved nothing: its citing path was 41
characters shorter than the real staging root, so the re-based path escaped above it and was
discarded for an unrelated reason.

**The overlay's refusals were unpinned while two records claimed they were pinned.** `important`. The
manifest's own comment said "Four properties, each pinned by a case in `test_teaching_edition.py`";
the plan baked the same claim. There were zero overlay assertions anywhere.

**A declared edit was 3/4 kept.** `important`. `teaching_edition_staleness.py` was in no index.

**Undeclared change to `/smh-new-project`.** `important` → `ruled`. Real drift against the Declared
Change Set, and authorised: the operator's *"yes just fix it"* covered the validator findings, which
included this file and its door by name. Recorded here rather than silently absorbed.

### Recorded, not fixed (4)

`F6`'s ban can be evaded by writing a destructive instruction as prose with an inline code span — no
cheap fix exists, because the door's own warnings use the same spellings. `E4` is not a genuinely
separate arm from `E3`. `E3` checks key names, so a leak appended to an existing line would pass it
(mitigated by `E5` and the scan). `F8`'s ban is spelled literally. Two more observations: the
`.agents/scripts/INDEX.md` explainer ships while naming the two pruned scripts, and the tracked-only
clear leaves empty directories in a local checkout — harmless, since `git clone` creates none.

### Mutation sweeps — three tables, 12 of 13 killed, every restore verified

| Sweep | Result |
|---|---|
| Part C guards (M1, M2r, M3, M5) | 4/4 killed |
| Review fixes (R1–R5) | 5/5 killed |
| Earlier Part C pass | M2 survived → re-aimed; M4 **defective**, dropped |

Three mutants had to be re-aimed before they meant anything, and each re-aim taught something. `M2`
disabled one of two guards and the second caught it. `R4` first removed two lines, so the wrong case
died — and once re-aimed it **survived**, exposing that `F9` counted `LOBBY=` occurrences across the
whole door, which has three, so deleting the one that mattered left the count at two. `F9`–`F12` now
locate the fenced block containing `git ls-files -z` and assert on that block alone.

Verdict: PASS @ e9d34b7aabbb0319be3e72714f472db627761b50
