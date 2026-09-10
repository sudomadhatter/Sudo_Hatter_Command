# SCC-440 — TEA docs: the CI-gate sections brought up to the AVCH-149 gate

**Ticket:** [SCC-440](https://sudo-command.atlassian.net/browse/SCC-440) · subtask of the open rolling
ticket [SCC-428](https://sudo-command.atlassian.net/browse/SCC-428)
**Lane:** `chore/SCC-440-tea-docs-ci-gate` off `origin/main` @ `a79180c4`
**Qualified:** `lane_qualify.py` → **LIGHT** (2 paths, none deployable, none in the toolkit)
**Date:** 2026-09-10

---

## Why

AVCH-149 rebuilt AviationChat's PR gate and armed the `main` ruleset. The two TEA reference manuals
still described the Story 7.1 shape from the 2026-06-29 audit, and they were wrong in ways an agent
would **act on** — not merely out of date. A reader was told the gate has no coverage flag, that
Playwright runs "both e2e specs", and that the Firestore security-rules suite is out of the gate.

## What changed

**[tea_testing_guide.md](../../../docs/_scc_sops_prds/tea_testing_guide.md)**

- **New §6.0 — "The PR gate as it stands today"**, declared the current state of record for CI and
  placed above the 2026-06-29 analysis it supersedes. Covers the three-gates distinction (local
  review gate / CI PR gate / server ruleset) that PR #99 proved people conflate, the five jobs and
  what each runs, the routing table, the fail-toward-running rule, ruleset 21963341's contents, and
  a flowchart. States plainly that a job skipped by `if:` reports **Success**, because that single
  fact is what makes the design work and what makes it dangerous to get wrong.
- **Staleness note rewritten** to name AVCH-119 and AVCH-149 and to point at §6.0 first. Also
  removed a stray orphan `-->` on the line below it — no `<!--` opened it, so it was rendering as
  literal text; it sat inside the block being rewritten.
- **Anchor facts 2 and 3** annotated with what closed them, rather than left reading as present tense.
- **§1 scorecard P7 row** rewritten: stack-level selection landed, per-test selection did not.
- **§4 P2 step 5** ("wire `--cov` into CI") marked done, with the floor that actually shipped (54,
  not the 61 sketched) and the real command line.
- **§6 P7 "Covered?"** split into what was assessed in June, what changed since, and what is still
  genuinely open — plus one line arguing the remaining TIA saving may not be worth buying.
- **Two mermaid subgraph labels** corrected; the "TODAY" diagram was captioned as current.

**[tea_deep_reference.md](../../../docs/_scc_sops_prds/tea_deep_reference.md)**

- **§14 anchor index** — `firestore.rules.test.js` said "local-only, out of the PR gate". It has been
  in the gate since AVCH-119, inside `Backend E2E (Firestore emulator)`, which is a required context.
- **New §12 subsection** mapping each pyramid tier to the CI job that executes it and when, with a
  link into §6.0 of the guide.

## Evidence

| gate | result |
|---|---|
| `lane_qualify.py --paths <the 2 docs>` | `LIGHT` — 2 paths, none deployable, none in the toolkit |
| `workflow_lint.py --toolkit-only` | **0 errors, 0 warnings**, 8 info (pre-existing UTF-8 BOMs) |
| `tests/test_check_maps.py` | **37/37** — after adding this session's `_artifacts/_main/INDEX.md` row, which F2 correctly demanded |
| `tests/test_mutation_sweep.py` | **40/40** standalone |
| `tests/test_sops_prds_folder.py` | **61/61** |
| `tests/run_all.py` | re-run bare at commit; the two files that were red are now 37/37 and 61/61 |

> ⚠️ **`run_all.py` is not safe to run while writing into the worktree.** Its first pass here reported
> `test_mutation_sweep.py` red; that suite refuses a dirty tree, and the dirt was this walkthrough
> being written mid-run. It passes 40/40 standalone. Run the suite on an untouched tree or the
> failure it reports is about you, not the code.

## The T9 failure was mine, not a dependency

`test_sops_prds_folder.py` T9 failed on two references I wrote:

```
T9 every prose path reference resolves:
  tea_testing_guide.md -> .github/scripts/classify_changes.py (resolves nowhere)
  tea_testing_guide.md -> backend/tests/test_classify_changes.py (resolves nowhere)
```

I first read that as a landing-order dependency — the files are created by AVCH-149, so I concluded
the docs could not commit until PR #107 merged and the submodule advanced. **That was wrong, and it
held the operator's documents hostage to an unrelated merge.**

T9 was reporting a real defect in the writing. These are **AviationChat** files cited from a
**lobby** document as bare repo-relative paths. That form resolves nowhere for the checker and
nowhere for a human reader either — someone reading this manual in the lobby cannot open
`.github/scripts/classify_changes.py`, because the lobby has no such file and never will. The
correct form for a cross-repo citation from here is a repository link, which is what they are now:

```
[`classify_changes.py`](https://github.com/sudomadhatter/AGY_AVIATIONCHAT/blob/main/.github/scripts/classify_changes.py)
```

Five references rewritten (four to the classifier, one to its test suite). T9 is **61/61** and this
lane no longer depends on AVCH-149 landing.

⛔ **The lesson worth keeping:** a link checker that says "resolves nowhere" is describing the
reader's experience, not asking to be waited out. Reaching for "this will resolve after the merge"
was the expensive answer to a question whose cheap answer was "then write the reference correctly."

## Your Actions

- [ ] Merge this lane's PR. It is independent — nothing in it waits on AVCH-149 any more.

**Reading order once both are merged:** §6.0 of the guide is the state of record for CI. The rest of
that document is a 2026-06-29 audit kept for its walkthroughs, and it is now labelled as such at the
top rather than reading as present tense.
