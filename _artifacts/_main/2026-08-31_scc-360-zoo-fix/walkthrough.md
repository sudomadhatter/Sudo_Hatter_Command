# Walkthrough — SCC-360: the Zoo fix (Cheshire Cat · The Gnat · the review gate · verdict receipts)

**Lane:** `chore/SCC-360-cheshire-cat-rename` (consolidated; riders SCC-361, SCC-362, SCC-363)
**Repo:** Sudo_Hatter_Command (lobby)

## What shipped, and why

The AVCH-101 / AVCH-106 audit found the Zoo team was not defying the rules — it was
**out-arguing the prose**. Every violation lived where a rule asked for judgment: the review level
was reasoned down to `quick`, the full suite was skipped by citing the operator's own
parallel-lane concern, ten test-adequacy findings died in one blanket dismissal, a fix was recorded
as applied that was never applied, and a self-run review stamped its own `Verdict: PASS` over a red
standing suite. A cheaper model does not break a refusal; it rationalizes through anything that is
not one. So every part of this lane replaces a sentence with a mechanism.

### Part 0 (SCC-360) — the ENGINEER seat is the Cheshire Cat

`Carpenter` → `😼🔨 Cheshire Cat — ENGINEER`, at every carrier: the seat master, the five sibling
masters that name it in their hand-off text, `zoo-team.md`, both INDEXes, the SOP page, the
twin-parity ledger key, `sync-agents.ps1`'s seat map, and the generated Zoo surfaces. The rename is
cosmetic; doing it across every carrier in one commit is not — a half-renamed seat is how a
generated surface silently resurrects a stock Zoo mode.

### SCC-361 — The Gnat claims the `ask` slug

`🦟🔍 The Gnat — LIBRARIAN`, groups exactly `[read]`. The stock Ask mode carried **no seat law at
all**, so any work routed through it was ungoverned by design — the leak the operator spotted first.
The seat is an unbiased lookup desk: it answers from project evidence and cites where it read, and
it **cannot** write a file or run a command, because the extension enforces mode groups. The
harmlessness is the mechanism, not the wording.

### SCC-362 — review left the seats and became the operator's model-switch gate

② runs to review-ready and stops. The operator switches the model and runs ③ himself
(`/cicd-code-review` / `/smh-code-review`), and ① (`/cicd-create-epic-sprint`,
`/cicd-write-story-tests`) runs on that same reviewing model. **No seat writes a `Verdict:` stamp
any more** — the refusal is in every master. The Queen of Hearts keeps the red phase and
review-readiness; she no longer judges her own team's finished work, which is the sentence that
authorized the self-stamped PASS.

### SCC-363 — a verdict needs a receipt

A new armed **commit-msg** gate (`verdict-receipt.sh` + `VERDICT-ENFORCE` + `verdict_receipt.py`).
A commit that adds `Verdict: PASS` or `Verdict: CONCERNS` to a walkthrough is **refused** unless the
lane carries a real `suite` receipt at the same tree. `FAIL` and `WAIVED` are never gated (recording
bad news must never be harder than recording good news); `[verdict-ok]` logs an auditable bypass;
deleting the flag drops it to warn-only. Registered in `hooks_armed.py` so an ARMED report cannot
omit it.

## Evidence

Suite, after absorbing origin/main (18 commits) into the lane:

```
python3 .agents/scripts/tests/run_all.py                       ->  68/68 files passed   (exit 0)
python3 .agents/scripts/workflow_lint.py --toolkit-only        ->  0 error(s), 0 warning(s) (exit 0)
python3 .agents/scripts/check_maps.py --depth3-only --strict   ->  exit 0
```

The generator agrees with the tree: `sync-agents.ps1 -GlobalsOnly` emitted **6 team seats** into
`.roomodes` and left the worktree **byte-clean**, proving the generated Zoo surfaces are what the
generator produces rather than hand-forged copies.

Conflict resolution on the absorb kept **both sides' facts** in the two ledger files
(`_artifacts/_main/INDEX.md` and the SOP changelog); `docs/doc-graph.md` is generated and was
regenerated rather than hand-picked.

## Your Actions

- [x] Approve the landing — given as the word `approved` (2026-08-31)

Superseded stamp (defused - written before ③ ran, and it named the merge commit): PASS @ 90ebb15e

review-runtime: fan-out

## Code Review (2026-08-31 — ③, on the operator's reviewing model)

Run through `/smh-code-review` at `review_level: standard`, derived from the Step 0.7 radius:
the diff touches gate, hook and rule surfaces (`.githooks/commit-msg`, `VERDICT-ENFORCE`,
`verdict-receipt.sh`, `zoo-team.md`) and 45 files, far past the ≤3-file quick threshold.

### Step 0.7 — blast radius re-derived against current `main`

- **What moved:** nothing this diff references. `origin/main` had not advanced past the
  merge-base after the absorb (`theirs = 0`), and `git merge-tree` returned a clean tree with
  no conflict messages. Every repo path and script the changed files load still resolves.
- **What it changes here:** nothing — true overlap against `main` is empty. The only overlap
  is with the LIVE sibling lane `chore/SCC-358-memory-and-sync` on `_artifacts/_memory/MEMORY.md`,
  a ledger append; whichever lane lands second absorbs `main` and keeps both rows, so there is
  no landing-order dependency in either direction.
- **What was re-measured:** the diff and `HEAD_SHA` were both re-taken AFTER the `origin/main`
  absorb (18 commits, three ledger conflicts resolved keeping both sides), so the lenses hunted
  the tree that will actually land rather than the pre-merge one. One sibling worktree is live;
  `risk_seam.py` reports `unclassified` here, which is the correct permanent answer for a repo
  with no code graph (SCC-289), so every judgement below came from reading the diff.

**Lens isolation.** The Agent tool's `isolation: "worktree"` clones the SESSION repo at `main`,
not this branch — the same class of trap `lens-worktrees-collide-across-reviews` records. Four
real worktrees were cut at the reviewed sha instead and probed: each named its own copy at
`a727c350`.

review-runtime: fan-out
lens_isolation: worktree
lenses_run:
- Blind Hunter · ok
- Edge Case Hunter · ok
- Literal-Correctness Hunter · ok — truncated to 20 of 45 files by the standing cap; the 25 withheld paths were named to it
- Acceptance Auditor · ok
- Test-Adequacy Auditor · ok
lenses_counted: 5/5
lenses_na: none
findings: 0 decision · 20 patch · 1 defer (7 noise-dismissed · 0 relevance kills)
drift: undeclared=15 · unimplemented=0 · incomplete=0 - dispositions in the findings table above. The undeclared set IS the review's own fix commit (b6edbd36): the plan declared the four parts, and every file beyond them was touched to close a finding this review raised. Nothing the plan declared is unbuilt.
dispositions: per-lens: Blind=9/0/0 · Edge=7/0/0 · Literal=8/0/0 · Acceptance=7/0/0 · TestAdequacy=4/0/0
severity_floor: none
notes: every survivor fixed in-lane before this verdict; one defer (cross-repo port) has a named structural blocker

### What the review actually found

**The gate this lane ships could be walked past four different ways, and every one was
reproduced with a real commit.** The parser demanded git's `b/` path prefix, which is a default
rather than a guarantee — `diff.noprefix=true` in a personal gitconfig made it match nothing and
a forged stamp committed in total silence. The receipt was read from the working tree, so the
house-standard `git add <walkthrough> && git commit` left it untracked and landed a verdict the
commit's own tree cannot evidence. The gate refused exactly one spelling of the stamp while every
other reader in the house accepts six case-insensitively, so **bolding the line recommitted the
precise AVCH-106 forgery this gate exists for**. And `git commit -v` appends the staged diff to
the message file, where `[verdict-ok]` appears as a literal in this repo's own sources — handing
any such commit a silent bypass whose token never reached the git log, falsifying the docstring's
"logged forever, auditable" claim on exactly that path.

**The tests were resting on the unproven claim the gate exists to refuse.** `main()` was never
executed, so `return 1 → return 0`, a silently renamed marker, and deleting the wrapper's `exec`
line all left the full suite at 68/68. `D1` grepped the raw hook file, which its own header
comment satisfies — the entire dispatch block could be deleted and stay green. And `B4b` greped
for a token without seeing polarity: rewriting a seat's refusal into *"You MAY run a ③ door and
write a `Verdict:` stamp"* passed 32/32, handing a seat written permission to self-certify.

**One finding was pure law rather than code, and it was the sharpest.** The rule sent seats
through `/smh-quick-dev` and `/cicd-quick-dev`, whose review step is marked *"mandatory — never
skipped"* and issues the very stamp the seats are forbidden to write. A seat reading both would
either deadlock or follow the door's explicit imperative over the rule's prose — reinstating the
regression SCC-362 removes. The stop point is now named in the rule.

### Mutation sweep — 11 applied, 11 killed

| Mutant | Baseline | Under mutant |
|---|---|---|
| `return 1` → `return 0` (the refusal itself) | 25/25 | 22/25 |
| `armed = MARKER.is_file()` → `False` | 25/25 | 22/25 |
| MARKER renamed (gate goes warn-only forever) | 25/25 | 22/25 |
| receipt read from disk again | 25/25 | 22/25 |
| `b/`-only regex + config pins dropped | 25/25 | 23/25 |
| drop `re.IGNORECASE` | 40/40 | 39/40 |
| narrow the stamp class to line-start-only | 40/40 | 32/40 |
| opt-out reads the raw message again | 40/40 | 38/40 |
| drop the non-dict receipt guard | 44/44 | 40/44 |
| wrapper `exec` → `exit 0` | 51/51 | 48/51 |
| subject carve-out widened to `*)` | 51/51 | 48/51 |
| re-add the `'Merge '*` text escape | 51/51 | 50/51 |
| seat refusal inverted into a permission | 33/33 | 32/33 |

**Recorded honestly:** reverting *only* the diff config pins still passes, because the tolerant
regex is the primary fix and the pins are defence-in-depth. That is a redundant defence, not a
missing test.

### Gates

```
python3 .agents/scripts/tests/run_all.py                      ->  68/68 files passed  (exit 0)
python3 .agents/scripts/tests/test_verdict_receipt.py         ->  51/51 passed        (exit 0)
python3 .agents/scripts/tests/test_zoo_team.py                ->  33/33 passed        (exit 0)
python3 .agents/scripts/workflow_lint.py --toolkit-only       ->  0 errors 0 warnings (exit 0)
python3 .agents/scripts/check_maps.py --depth3-only --strict  ->  exit 0
```

### Deferred — one item, with its structural blocker

`verdict_receipt.py` cites AVCH-106, but git hooks are repo-local and `sync-agents.ps1` does not
ship `git-hooks/`, so **AGY_AVIATIONCHAT has no verdict stage of its own** and the next AVCH stamp
over a red suite commits exactly as before. Blocker: **another repo** — cross-repo work takes a
ticket per repo. The scope is now stated in the script's own docstring so no reader mistakes it
for coverage. Remedy: an AVCH ticket to port the gate.

Verdict: PASS @ b6edbd36
