# SCC-411 — cycle 11 run as ONE lane

**Ticket:** SCC-411 (the 2026-09 rolling ticket, cycle 11)
**Lane:** `chore/SCC-411-bugs-cycle-11`, cut from `origin/main` at `aa408738`
**Date:** 2026-09-06
**PR:** [#181](https://github.com/sudomadhatter/Sudo_Hatter_Command/pull/181)

## What this was

SCC-411 was closed Done on 2026-09-06 carrying ten collected INDEX rows, nine of which had never
been turned into work. Closing it that way did not resolve those rows; it buried them, because a
Done ticket is not a place anybody looks. The operator reopened it with a ruling that settles how
this cycle ends: the pile closes **under the ticket that collected it**. It is not carried into
cycle 12, and it is not split into new tickets. SCC-419 stays clean and holds the baton, so the
board shows exactly one running cycle and one successor.

Before writing anything, every row was re-measured against this repo at `aa408738`, using the
repo's own matchers over the rendered permission lists rather than reasoning about them. Eight rows
were real and still open. One had already been fixed on `main` and is struck with the evidence
instead of being worked. One had shipped as SCC-417. Two of the eight turned out to be **wider than
the ticket said**, which is the main reason this lane is bigger than its row count suggests.

## The headline: a branch delete is judged by its target list

`git branch -d` takes a **list** of branches, and every permission grammar in this house matches a
command from the **left** — Zoo by literal lowercased prefix, Antigravity by a per-token regex over
the leading tokens, Claude by `Bash(<prefix>:*)`. So the first target satisfies the rule and every
target after it rides free, with no shell metacharacter for any splitter to notice. Verified against
real git 2.43 in a throwaway repo:

```
$ git branch -d worktree-agent-x main
Deleted branch worktree-agent-x (was 9dd7d8f).
Deleted branch main (was 9dd7d8f).
```

The ticket filed this as a known limit with the remedy named: it needs a hook that parses the branch
list, because no permission row can say *"exactly one argument, and it starts with `chore/`"*. The
re-measurement then found the family was larger than filed. These all read **allow** at `aa408738`:

| spelling | zoo | claude | antigravity |
| --- | --- | --- | --- |
| `git branch -d chore/SCC-1-x main` | allow | allow | allow |
| `git branch -r -d origin/main` | allow | allow | allow |
| `git branch -r --delete origin/main` | allow | allow | allow |
| `git branch -v -d main` | allow | allow | allow |
| `git branch -vv -d main` | allow | allow | allow |
| `git branch --delete main` | allow | ask | allow |
| `git branch -f -d main` | allow | ask | allow |
| `git branch -rd origin/main` | allow | ask | deny |

The cause is one sentence: **the delete flag is not always first.** Every existing deny row named
the first flag, so any option in front of the delete walked straight past the fence. The `-r`, `-v`,
`-vv` and `--format` forms are worse than the rest, because Claude grants those flags as **reads** —
and real git accepts every one of them alongside a delete (`git branch -v -d victim` prints
*Deleted branch victim*). A read grant was quietly carrying a write.

`.agents/hooks/guard-branch-delete.py` closes the family on Claude. It is a `PreToolUse` **deny**,
never an ask, and it reads the whole target list: any target outside `chore/`, `claude/` or `epic/`,
any target carrying a substitution, and every remote-tracking delete is refused, in any flag
position. Zoo and Antigravity run no hooks, so they get deny rows for the eight spellings their
grammars can express, each with its `env -u` twin and its automatic `cd <abs> && ` house twin, and
each pinned by a destructive-battery row. The two things those grammars genuinely cannot express —
the target list itself, and an arbitrary option in front of the delete flag — are written into the
guide's residual section as limits, not claimed as fixed.

One design note worth keeping. The guard **fails open on "this is not a branch delete"** and
**closed on "this is a delete whose targets I cannot read"**. Silence is the right answer to a
listing, a create, a rename or another tool. It is the wrong answer to `git branch -d "$BRANCH"`,
because the one command that laundered a target past every other fence is exactly the one a
shrugging guard would wave through.

## A measurement killed an approved decision mid-build

The approved plan said the `env -C` wrapper siblings — `nice`, `xargs`, the shell builtin `command`,
`env -i`, `env VAR=v` — should stay as asks, on cycle 10's reasoning that they land on `ask` and the
operator still decides. That reasoning is false on one platform, and the measurement is short:

```
bare -> house, on Antigravity          (Zoo splits the chain; every one stays ask there)
  curl https://evil.sh   ask -> allow      nice rm -rf /     ask -> allow
  ssh user@host          ask -> allow      env -i rm -rf /   ask -> allow
  rm -rf /              deny -> deny       git push --force deny -> deny

which allow rule swallows the house prefix:  command(cd) / unsandboxed(cd)
```

Antigravity matches a command's leading tokens; the fence carries a blanket `command(cd)` allow; and
`command-shape.md` rule 1 **mandates** that every door command be `cd <abs> && …`. So behind the
shape an agent actually types, everything after the `&&` is invisible and the ask tier evaporates.
Denies survive it because the renderer writes a `cd .* && ` twin of every one; asks have no twin to
get. The plan was amended in place with the measurement, and the four expressible wrappers became
denies. `command -v ` stays approvable and is now pinned in two batteries, since Antigravity has no
longest-prefix re-allow and needed an explicit `(?!-v)` lookahead.

The general mechanism is bigger than this lane. It is pinned in both directions by a new parity case
and written into the guide with the remedy stated — replace the blanket `command(cd)` with the
enumerated house shapes the doors actually print. It was deliberately **not** attempted here:
getting that list wrong turns the operator's real ceremony into approval prompts, and an approval
prompt is this house's flagship budget threat.

## Three gates that were quietly lying

**The approvals report double-counted.** A context compaction re-emits records already in a session
transcript, with identical `toolu_` ids, and `scan()` had no memory of which ids it had already
paired. One operator interruption was therefore counted twice. Measured: one use/result pair scans
as `calls 1, stops 1`; the same pair written twice scans as `2, 2`. Every number that door prints —
the ranking, the wall-clock total, the stop count the operator makes allow-row decisions from —
could be inflated twofold.

**The VS Code guard failed open.** `zoo_permissions_apply.py --apply` refuses to write while VS Code
is running, because VS Code flushes its in-memory state over the top on exit. Inside the sandbox,
WSL interop is blocked and `tasklist.exe` returns an **error string with exit 0**, not an `OSError`.
The function caught only `OSError`, found no `Code.exe` in that string, and answered *not running* —
while the same call outside the sandbox answered *running* with nineteen processes live. The
docstring already promised *"unable to ask = treat as running"*; only the code was missing. It now
requires the output to look like an actual tasklist answer before searching it.

**The gate receipt stamped a clean tree DIRTY.** The sandbox mounts denied `.claude/*` paths into the
work tree as character devices, and `git status` reports all twelve as ordinary untracked files:

```
?? .bashrc   ?? .claude/agents   ?? .claude/loop.md   ?? .gitconfig   (+8 more)
$ stat -c '%F %n' .bashrc .claude/agents
character special file .bashrc
character special file .claude/agents
```

A DIRTY receipt is not adoptable by the review's Step 3 or by `task_preflight`, so the suite got
re-run sandbox-off purely to earn a clean stamp — **the same double gate run SCC-418 removed,
arriving through a different door.** That is why it was finished here rather than filed again. The
filter is exactly "untracked and a character device", asked of the filesystem via `lstat` rather than
of the name, with a control case proving a real untracked file beside the mounts is still dirt.

Proved live in this lane. `git status --porcelain` returned nine entries; the receipt recorded one:

```
porcelain paths: ['.claude/hooks', '.claude/launch.json', '.claude/loop.md', '.claude/output-styles',
                  '.claude/routines', '.claude/scheduled_tasks.json', '.claude/workflows',
                  '_artifacts/.../gates/', '_artifacts/.../walkthrough.md']
  .claude/hooks              CHAR DEVICE   is_char_device=True      (x7)
  .../walkthrough.md         regular file  is_char_device=False
_measure_dirt -> ['_artifacts/_main/2026-09-06_scc-411-bugs-cycle-11/walkthrough.md']
```

⚠️ **One trap for whoever reads this next: `stat(1)` and `os.lstat` disagree here.** Run from the
shell, `stat -c '%F' .claude/hooks` printed *regular empty file* for the same seven paths that
`os.lstat` — called from the Python process that actually runs the check — reported as character
devices, seconds apart. The sandbox does not present the mount identically to every process. The
predicate uses `os.lstat` inside the checking process, which is the view that decides; do not
falsify this from a shell `stat` and conclude the filter is dead.

## The row nothing was holding

Nothing in this repo asserted where the lane re-allow prefixes end. Measured by mutation: widening
`git branch -d chore/` all the way down to `git branch -d c` — and the `claude/` and `epic/` twins
with it — flipped **zero** rows of any battery, while `git branch -d canything-at-all` became
auto-approve. Four near-miss rows now bound them, each one character from a live re-allow.

## Evidence

| What | Result |
| --- | --- |
| RED, all five test files, before any fix | guard 1/9 · parity 99/102 · zoo 24/27 · stops 25/26 · receipt AttributeError |
| `run_all.py` from the lane, in-sandbox, ONE run | **80/80 files passed** |
| Mutants | **15/15 killed**, every restore byte-identical |
| `sop_currency.py` · `workflow_lint --toolkit-only` · `check_maps --depth3-only --strict` · `permission_render --check` | exit 0 |
| `merge-tree` against `origin/main` | clean, tree `d56e4901`, zero conflicts |

Nine of the fifteen mutants change behaviour without deleting anything — five narrow a live rule,
two widen what is accepted, two flip a decision. Pass 1 was **14/15**: the survivor showed that the
guard's unreadable-target check was unfalsifiable, because every case testing it also failed the
namespace test. The real hole it pointed at is a lane-shaped target with a substituted suffix —
`git branch -d chore/$BRANCH` with `BRANCH="x main"` word-splits into two targets, the second being
`main`. Three cases were added; no production code changed. That is the sweep doing its job: a
surviving mutant said *nothing proves this code matters*, and the answer was a missing test.

## Dispositions — every one of the ten rows

| # | Row | Disposition |
| --- | --- | --- |
| 1 | `env -C` sibling wrappers are ASK, not DENY | **Fixed** — four denied with twins; `env VAR=` is an Antigravity-only deny and a documented Zoo residual |
| 2 | `approval_stops.py` has no `.agents/scripts/INDEX.md` row | **Fixed** — row added |
| 3 | `vscode_running()` fails open in a sandboxed shell | **Fixed** — fails closed on a non-answer, with a control that keeps it usable |
| 4 | Zoo auto-approves `git branch -rd origin/REF` | **Fixed, wider than filed** — every remote-delete spelling denied; the guard refuses them all on Claude |
| 5 | The `-d` family's multi-argument and long-form escapes | **Fixed on Claude** by the guard; deny rows for what Zoo and Antigravity can express; the list escape documented as a residual |
| 6 | `zoo_pieces()` does not score a backtick body | **Pinned + fixed on Claude** — a behaviour row records Zoo's model unchanged (deliberately); the guard refuses any substituted target |
| 7 | No assertion bounds any lane re-allow prefix | **Fixed** — four near-miss rows, proved by the mutation that used to pass |
| 8 | `approval_stops.py` double-counts across a compaction | **Fixed** — dedupe on `tool_use` id, with a control for two distinct calls |
| 9 | The `/smh-llm-approvals` fast path is unreachable for a Zoo harvest | **Struck, already closed on `main`** — Step 4 now lists `terminal-permissions-guide.md` as the fifth permitted path, with the SCC-412 measurement under it. No code. |
| 10 | SCC-417 banned-row gate | **Shipped** (PRs #178, #179) |
| + | SCC-418's leftover: the receipt reads bind mounts as dirt | **Fixed** — the same double gate run, closed at its second door |

## Your Actions

- [x] The merge itself — lands via [PR #181](https://github.com/sudomadhatter/Sudo_Hatter_Command/pull/181)
- [ ] After the merge, once per machine: `python3 .agents/scripts/zoo_permissions_apply.py --apply`
      and `python3 .agents/scripts/antigravity_permissions_apply.py --apply`, to push the new deny
      rows into the live stores. Nothing here writes a live store. Hooks are read at session start,
      so `guard-branch-delete.py` is live in the next session, not the running one.

## Code Review (2026-09-06)

Five lenses ran over the lane's own diff, and the headline fence did not survive first contact. The
guard this ticket exists to build was **open on the family it fences**: `_VALUE_FLAGS` declared that
every option in it consumes the next token, and on real git 2.43 three of them (`--color`, `-t`,
`--track`) take an *optional* argument and consume nothing — so the hook swallowed the delete flag
as their value and said nothing while git deleted the branch. Two lenses reached that independently,
and it reads *allow* on all three platforms. That is a fence with a sign on it, and it is the one
class of finding that cannot ship, so it was fixed rather than recorded.

Three more holes came with it: an empty target list passed in silence (the exact shrug the file's
own design law forbids), a `\`+newline continuation split the verb from its delete flag, and
`git --work-tree <path> branch -d` escaped the invocation match. And one hole pointing the other
way, which mattered because this repo is full of the literals: the guard matched its own strings
anywhere in a command, so `grep -rn "git branch -d main"` and the commit message describing the
fence were both refused. Every one was reproduced against the real `classify()` before and after.

The second real finding was that the sandbox-mask filter shipped in **one** of four "is this tree
clean?" gates while the changelog claimed all of them — and the gate it missed is the one that
closes this lane out. Measured here: `task_preflight` reported nine uncommitted changes, seven of
them bind mounts. The predicate also knew only one of the two shapes a mask takes; a lens measured
the second in its own worktree while I measured the first in mine, and both are real.

Two tests were proven vacuous by mutation and are now real gates. `_is_char_device` could be
replaced with `return False` — restoring the exact pre-SCC-411 bug — with the receipt file still
green, because the only cases holding it stubbed it away. And the case named "the refusal names the
offending target" asserted `"main" in text` against prose containing "main" three times.

Everything else was assessed and dismissed under `code-standards.md` §6.5: the duplicated
`tokenize` cannot be extracted without changing a sibling fence outside this diff, so the drift
— the actual risk — is now pinned by a test instead; three over-length lines match 42 pre-existing
rows in the same table and no house gate enforces length; two stale hook counts in the SOP were
already stale at `origin/main`.

review-runtime: fan-out
lens_isolation:  worktree
lenses_run:
- blind-hunter · ok
- gate-and-test-integrity · ok
- parity-and-blast-radius · ok
- acceptance-and-record · ok
- clean-code · ok
lenses_counted: 5/5
lenses_na: none
findings: 31 returned across five lenses · 22 assessed REAL and fixed in-lane · 9 dismissed under §6.5 (structure, naming, or pre-existing debt outside this diff)
dispositions: per-lens: blind-hunter=4/0/0 · gate-and-test-integrity=5/1/0 · parity-and-blast-radius=4/1/0 · acceptance-and-record=8/4/0 · clean-code=1/3/0
drift: none — the Declared Change Set still matches `git diff origin/main...HEAD`, widened by the six files this review's fixes touched
severity_floor: none

### Step 0.7 — blast radius re-derived

1. `origin/main` has not moved since the merge-base (`aa408738`), so true overlap with landed work is EMPTY.
2. `git merge-tree --write-tree` against `origin/main` is clean, zero conflict messages.
3. The only live sibling worktree is the lobby on `main`, so there is no landing-order dependency.

| # | Finding | Lens | Assessment | Disposition |
| --- | --- | --- | --- | --- |
| 1 | `_VALUE_FLAGS` swallows the delete flag — `git branch -v --color -d main` deletes, guard silent, allow ×3 | blind, gate | REAL · BEHAVIOUR · in-diff | **Fixed** — three optional-argument flags removed, and the skip now refuses any value starting with `-` (git's own parse-options rule). Two independent fixes, each with a row only it can satisfy |
| 2 | A delete whose target list is EMPTY passes in silence | blind | REAL · BEHAVIOUR · in-diff | **Fixed** — now a refusal; a delete always names a branch |
| 3 | `\`+newline splits the verb from the delete flag | blind | REAL · BEHAVIOUR · in-diff | **Fixed** — rejoined before splitting, as the shell does |
| 4 | `git --work-tree <path> branch -d` escapes the match | blind | REAL · BEHAVIOUR · in-diff | **Fixed** — separate-value pre-subcommand options added |
| 5 | The guard refuses a `grep` for its own literals, and its own commit message | blind | REAL · BEHAVIOUR (a refusal of something legitimate) · in-diff | **Fixed** — quoted spans masked before the search, `#` comments stripped, shell `-c` bodies exempted so `bash -c "git branch -d main"` is still denied |
| 6 | The mask predicate knows one of the two shapes a sandbox mask takes | parity | REAL · BEHAVIOUR · in-diff | **Fixed** — covers a character device and a zero-byte read-only file; both arms driven against real filesystem objects |
| 7 | The mask filter shipped in one of four tree gates; the changelog claimed all four, and the missing one blocks this lane's close-out | parity | REAL · BEHAVIOUR · in-diff | **Fixed** — `strip_sandbox_masks` shared by all four; masks are named, never silently dropped |
| 8 | `_is_char_device` could `return False` with the receipt file still green | gate | REAL · BEHAVIOUR (a gate that cannot fail) · in-diff | **Fixed** — four cases now drive the real predicate, including `/dev/null` and a symlink to it |
| 9 | "the refusal names the offending target" cannot fail — the prose contains `main` | gate | REAL · BEHAVIOUR · in-diff | **Fixed** — asserts on `zzz-victim`, which appears in no reason string |
| 10 | Nothing bounded the chain splitter; `--` end-of-flags had no case; battery lengths unpinned | gate | REAL · in-diff | **Fixed** — three rows and two length pins |
| 11 | Two install guides instruct `git branch -D tmp/gate-check`, which the new guard refuses | parity | REAL · BEHAVIOUR · in-diff (this diff created the conflict) | **Fixed** — renamed `chore/gate-check` in both |
| 12 | `mutants.json` M14 credits a case that cannot kill it; the nine/five tally miscounts twice; `sweep_runs` says 2 for three passes | acceptance | REAL · in-diff | **Fixed** — all three corrected; the sweep was stronger than its own summary claimed |
| 13 | Plan acceptance row D asserts ASK for four wrappers that shipped DENY; row I and step 7 name a signature that did not ship; self-audit counts 21 EDIT paths for 18 | acceptance | REAL · in-diff | **Fixed** — the §2 amendment had superseded the decision row but never the acceptance row |
| 14 | Walkthrough cites `check_maps --strict`, which cannot exit 0; ticket `## Files` omits two paths | acceptance | REAL · in-diff | **Fixed** |
| 15 | `tokenize` is byte-identical to `allow-readonly-chain.py`'s | clean-code | REAL · **not** BEHAVIOUR (§6.5 q2) | **Risk fenced, copy kept** — the two use different quote sets, so extracting it would change a fence outside this diff. A test now pins them in sync and goes red naming both. `_GIT_OPTS` stopped being a copy when finding 4 was fixed |
| 16 | Three lines over 120 chars · single-caller helpers · a pre-existing type annotation · two stale hook counts in the SOP · hoisting `seen_ids` | clean-code, gate, parity | not BEHAVIOUR, or not in this diff | **Dismissed** under §6.5 — recorded, not fixed |

Gates at the shipping SHA:

| Gate | Result |
| --- | --- |
| `run_all.py` | **80/80 files** in ONE sandboxed run @ `a5027c40` |
| Review mutation sweep | **8/8 killed**, restores byte-identical; pass 1 was 7/8 |
| Build mutation sweep | 15/15 killed (23/23 across both sweeps) |
| `gate_receipt` | `[PASS] suite exit=0 28.8s @ a5027c40`, `dirty_paths` = the walkthrough only — the seven `.claude/*` mounts exempted live |
| `sop_currency` · `workflow_lint --toolkit-only` · `check_maps --depth3-only --strict` · `permission_render --check` | exit 0 |

The review sweep's pass 1 is worth one line, because it repeated the build sweep's lesson exactly.
M17 survived: the row written to falsify the flag-list correction put the flag *before* `-d`, where
the independent skip-refusal already covers it. Only a flag sitting *between* the delete flag and
the target can eat the target. The row moved; no production code changed. A mutant that survives
because two fixes overlap is not a hole — it is a test that cannot tell them apart.

Clean-Code Gate: **PASS** — `py_compile` green on every changed file, no §2 banned pattern shipped,
no secret. The one §2 duplication finding is fenced by a test rather than removed, for the reason in
row 15.

Verdict: PASS @ a5027c40
