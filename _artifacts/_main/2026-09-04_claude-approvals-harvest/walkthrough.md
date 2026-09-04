# Walkthrough — harvest the machine-local Claude allow list (SCC-392)

**Date:** 2026-09-04 · **Lane:** `chore/SCC-392-claude-approvals-harvest` · **Cut from:** `main` @ `78f47333`
**Ticket:** [SCC-392](https://sudo-command.atlassian.net/browse/SCC-392) · **Plan:** [implementation_plan.md](implementation_plan.md)

## What was wrong

`/smh-llm-approvals` treated the three agents asymmetrically, and only one of the three was treated
correctly.

For **Antigravity** it diffs the live machine store against the tracked render and shows what exists
only on this machine. That diff is the whole mechanism by which a click-written grant becomes
something that travels: the door sees it, the operator names it, it lands in the one source, and the
renderer puts it on both machines.

For **Claude Code** it read chat transcripts, pairing an `is_error` refusal back to the Bash
`tool_use` that earned it. That finds commands which **stopped**. It cannot find the ones that
stopped *asking*, because an approval granted from a terminal chat is written to no transcript — it
is written to one of two machine-local files:

| List | Rows | Travels? |
|---|---|---|
| `<repo>/.claude/settings.json` — rendered from `families.json` | 140 | yes, it is tracked |
| `~/.claude/settings.json` — user scope | 82 | **no**, it is outside the repo |
| `<repo>/.claude/settings.local.json` — project scope | absent here | **no**, gitignored at `.gitignore:58` |

Measured on the WSL box 2026-09-04: 65 of the 82 user-scope rows were already covered by the tracked
list, and **17 were not**. Those 17 decide on this machine and nowhere else — the Mac goes on asking
for every one of them — and nothing in the door, the renderer or any gate could see that number
short of running the set difference by hand.

```
Bash(acli:*)   Bash(bash:*)   Bash(chmod:*)   Bash(gh:*)    Bash(jq:*)     Bash(mv:*)
Bash(node:*)   Bash(npm:*)    Bash(npx:*)     Bash(pytest:*) Bash(python:*) Bash(python3:*)
Bash(rsync:*)  Bash(sed:*)    Bash(sh:*)      Bash(touch:*)  Bash(env -u GITHUB_TOKEN gh:*)
```

## One thing checked before the diff was trusted

The tracked list and the user list do not have to use the same rule spelling, and a set difference
over two grammars would over-report every row as machine-local. Measured before building anything:
the tracked list is 75 colon-form rows (`Bash(cd:*)`), 9 space-form (`Bash(git checkout *)`) and 56
literals; the user list is 66 / 6 / 10 in the same three shapes, and the forms that appear in both
files match exactly. `Bash(git checkout *)` is present in the tracked list in that spelling, not a
colon variant. So a plain set difference is honest here, and the 17 are genuinely absent rules rather
than the same intent written another way.

## The change

### `.agents/scripts/claude_permissions_status.py` — new, read-only

Shaped like `antigravity_permissions_apply.py --status` in vocabulary and argument surface, minus the
apply. It resolves all three paths from `Path.home()` and the repo root, so it is correct on the Mac
and the PC without a hardcoded path, reads `permissions.allow` from each, and prints one status line
plus the rows the tracked list does not carry. On this machine:

```
status  : MACHINE-LOCAL allow rows: 17 (user=17) - they decide on this machine only
```

Three properties are load-bearing rather than incidental.

**There is no apply, and there must never be one.** Antigravity's store is a separate file the
extension reads at startup, so a rendered fence has to be pushed into it; Claude reads
`<repo>/.claude/settings.json` directly, so a rendered row is in force the moment the file is saved.
There is nothing to push into and nothing that can be replaced or lost. That absence is pinned by a
test rather than left to a comment (G8): the module exposes no `apply`, and the code — the WHOLE
file, docstrings excluded — contains no write call and no `--apply` flag. G8 shipped vacuous and the
review caught it; the story is under *Code Review* below, and G8a now pins the scan window itself so
it cannot narrow again.

**It reports `allow` only.** The door's standing law is that it never reads or writes any deny list.
A status report that surfaced deny rows would invite exactly the edit that law forbids, so the
reader never sees one (G4).

**Absent is empty, EMPTY is empty, and unreadable names itself.** `settings.local.json` does not
exist on this machine and normally does not exist anywhere — the same status an empty Zoo store
already has in this door, and it must not read like a failure (G3). A file that is *there* and holds
nothing declares no rows, which is also not damage (G3b). A file that is there, holds something, and
cannot be parsed — or cannot be read at all — is a different thing: it names itself and exits 2
(G9, G9b, G9d). It refuses rather than guessing, because treating an unreadable list as empty would
under-report the very rows this step exists to find, which is the silent under-report SCC-355 already
cost this door once.

Three smaller reading hazards are handled because a lens reproduced each: a Windows-authored file
carries a BOM (read as `utf-8-sig`), `{"permissions": null}` is legal JSON on which a `.get` default
never fires, and the headline counts DISTINCT rules — Claude offers the same grant at user and
project scope, so one rule granted twice is still one rule that does not travel (G5c, G5d).

### `.agents/commands/smh-llm-approvals.md` — three edits

**Step 1** gains the Claude store diff beside the transcript read, naming both machine-local files and
the script that diffs them, and stating plainly that a rule living only there reaches no other
machine.

**Step 2** gains a fourth output group under its own heading. Harvested rows are not commands that
stopped; they are rules that already stopped asking, and the question about them is not *may I run
this* but *should this travel*. Folded into the list above they lose that distinction.

**Step 3** gains the one caveat this particular source needs. The existing narrowness law reads *a
rule is only ever as wide as the command it came from* — but a row lifted out of
`~/.claude/settings.json` did not come from a command, so that law has nothing to measure it against.
Two rows on the live list, `Bash(bash:*)` and `Bash(sh:*)`, permit any command at all. Locally that is
the operator's call on a machine he is watching; promoting one into the source is a different act,
because it then renders to both machines. The door shows the row for what it is and takes his word out
loud — and does not narrow it for him, because this door does not compute prefixes (SCC-354).

And one warning is explicitly **barred**: the Antigravity apply REPLACES both arrays, which is why
that path carries a data-loss caveat. Claude's path has none. The door says so in the negative, so the
caveat is not cargo-culted across later by someone reading the two paragraphs side by side.

The "what this command does NOT do" list gains the read-only law: the two machine-local files are
read and never edited. Deleting a now-redundant row from `~/.claude/settings.json` is the operator's
own edit to ask for by name.

### `.opencode/commands/smh-llm-approvals.md`

Refreshed byte-identical, as E4 requires.

### `docs/_scc_sops_prds/workflows_testing_SOP.md` (+ changelog)

Usage surfaces changed, so the SOP moves in the same commit or the armed `sop_currency` gate rejects
it. §13 *What does NOT travel between the machines* gains a **Claude Code's approval lists** row
beside Zoo's and Antigravity's — that section is literally about this problem, and it was the one
agent missing from it. The `/smh-llm-approvals` prose gains a paragraph on the second half of Claude
and a paragraph on the blank-cheque stop; the existing Antigravity data-loss caveat is now scoped to
Antigravity in the operator's own page as well as in the door. The quick-reference row and the command
table row both gain the Claude half. One changelog line.

## Assert first — what was pinned, and what proves the pins bite

Sixteen rows for the script and three for the door, on synthetic inputs in a tempdir so nothing
depends on this machine's live files.

| Row | What it refuses to let happen |
|---|---|
| G1 / G2 | A local-only row silently dropped from the report, or a shared row reported as local |
| G3 / G3b | An absent — or empty — `settings.local.json` raising instead of counting as empty |
| G4 | A deny row reaching the operator's eyes, against the door's standing law |
| G5 / G6 | A `status()` hard-wired to one answer — it is seen saying both (the lesson C6 records for the sibling) |
| G5b | The headline counting FILES instead of rows — the fixture now separates the two |
| G5c | One rule granted at both scopes counted as two |
| G5d | A `"permissions": null` block, or a Windows BOM, raising instead of being read |
| G7 | A missing tracked list passing silently instead of exiting 2 |
| G7b | The row listing — this script's only product — vanishing while the run still exits 0 |
| G7c | The three default paths drifting from what the docstring advertises |
| G8 | An apply growing here later, which could only destroy |
| G8a | The G8 scan window narrowing back to a slice that contains no function body |
| G9 / G9b / G9d | An unreadable or unparseable file dying in a traceback, or an error that does not say WHICH file |
| E6 / E7 / E8 | The door losing the store names, the no-apply statement, the never-edits law, or the blank-cheque caveat |

⭐ **A pinned row is a claim until a mutant kills it.** `sweep.json` declares **ten** mutants and
`mutation_sweep.py` killed **all ten**, restore verified byte-for-byte against `55382345`:

```
KILLED  M1  an --apply that overwrites the tracked list, grown inside main()      -> G8
KILLED  M2  the no-apply scan narrowed back to the vacuous 454-char slice         -> G8a
KILLED  M3  the parse error stops naming the file it could not read               -> G9b
KILLED  M4  the headline counts FILES instead of distinct rules                   -> G5b
KILLED  M5  the same rule at both scopes counted twice                            -> G5c
KILLED  M6  an explicit null permissions block stops being tolerated              -> G5d
KILLED  M7  the row-listing loop deleted - the header prints, the rows do not     -> G7b
KILLED  M8  the repo root resolved one level too shallow                          -> G7c
KILLED  M9  the never-edits law deleted from the door body                        -> E7
KILLED  M10 the OSError half of the read guard removed                            -> G9d
-- restore verified: bytes match, nothing was committed, `git diff --quiet 55382345` is clean --
```

An eleventh mutant was written and then withdrawn: the first M3 tore out the guard and the
`utf-8-sig` read together, killed three rows at once, and the sweep **refused to attribute** the kill
to the case it declared. That is the attribution clause working, not a false alarm; M3 was split into
two mutants that each remove exactly one property.

## Evidence

```
python3 .agents/scripts/tests/run_all.py                       73/73 files passed        @ 55382345
python3 .agents/scripts/tests/test_permission_parity.py        -- 84/84 passed --
python3 .agents/scripts/mutation_sweep.py --table .../sweep.json   10/10 KILLED, restore verified
python3 .agents/scripts/workflow_lint.py --toolkit-only         0 error(s), 0 warning(s), 8 info
python3 .agents/scripts/check_links.py --base origin/main       12 files, 197 path claims, clean
python3 .agents/scripts/permission_render.py --check            in sync (zoo, claude, antigravity)
python3 .agents/scripts/declared_change_set.py diff ...         undeclared=0 unimplemented=0 incomplete=0
python3 .agents/scripts/claude_permissions_status.py            MACHINE-LOCAL allow rows: 17 (user=17)
```

The 8 `info` rows are pre-existing UTF-8 BOMs on eight `testarch-*.md` files this lane never touched.

**The suite reached 73/73; two rows were red on the FIRST run and both cleared.** `test_check_maps.py`
F2 wanted this lane's own row in `_artifacts/_main/INDEX.md` — added, and the gate was doing its job.
`test_sops_prds_folder.py` T9 cited `docs/.maps-journal.jsonl`, which is gitignored (`.gitignore:23`)
and so does not exist in a freshly cut worktree at all; it is written by the post-commit maps
recorder, which had not yet run here. Proved rather than assumed twice over: the same test passed
61/61 in the main checkout under `--on-main` while it was failing here, and it went green in this
worktree the moment the lane's first commit ran the recorder. Environmental and self-clearing.

**One measurement needs its condition stated.** Run under the Bash sandbox, the script exits 2 naming
`.claude/settings.local.json` — under that sandbox the path is a character-device mount artifact, not
a settings file, and reading it raises `PermissionError`. That is the new guard behaving correctly,
and the door now says so. Outside the sandbox the path is simply absent and the run is the clean
17-row report above.

## What is live now

The script and the door are live in this lane. Nothing was pushed into any machine store, because
Claude has none — the tracked `.claude/settings.json` is unchanged by this lane, since no row was
harvested yet. The harvest itself is the operator's next `/smh-llm-approvals` run, where the 17 rows
will appear as their own group and he picks which ones travel.

review-runtime: fan-out

## Code Review (2026-09-04)

Verdict: PASS @ 55382345
Suite evidence measured on the same sha: `run_all.py` 73/73, receipt `result: pass` exit 0 @ `55382345`.
The lenses ran on `5a774384` (the absorb of `origin/main`); every finding below was fixed after that
sha and re-proved by the ten-mutant sweep at `55382345`.

lens_isolation:  worktree
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none
findings:        0 decision · 25 patch · 0 defer   (0 noise-dismissed · 1 relevance kill)
dispositions:    per-lens: blind-hunter=4/0/0 · edge-case-hunter=4/0/1 · literal-correctness-hunter=4/0/0 · acceptance-auditor=7/0/0 · test-adequacy-auditor=6/0/0
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — the plan carried NO `## Declared Change Set` block at review start (one important finding, fixed in the lane); it now reconciles clean

**Scope:** the 11-file `origin/main...HEAD` diff, re-taken after Step 0.7 absorbed `origin/main`.
**Method:** five lenses fanned out in parallel, each in its own context; the four repo-reading lenses
each in their own disposable worktree copy of this repo (they reported their `agent-*` toplevels; the
Blind Hunter got no tree, by design). Every finding below was assessed against the three questions —
is it real, does it change behaviour, is it in this lane's diff — and fixed in this lane. Nothing was
deferred and no ticket was minted.

**The headline: the one check this lane advertised as load-bearing was inert, and four of five lenses
proved it independently.** Each of them wrote an `--apply` into `main()` that overwrote the tracked
settings file, ran the suite, and watched it stay green.

### Findings

| # | file:line | sev | Failure scenario | Disposition |
|---|---|---|---|---|
| 1 | `.agents/scripts/tests/test_permission_parity.py` G8 | critical | `split('"""')[2]` scanned 454 of 4,886 chars — the slice between the module docstring and the first function docstring, containing no function body. `main()` was in segment 8, never scanned. An `--apply` that rewrites `.claude/settings.json` passed. | applied @ `8b1a3219` — joins the even segments; **G8a** pins the window; M1 + M2 kill it |
| 2 | `.agents/scripts/claude_permissions_status.py` `_allow` | critical | A file that exists and cannot be parsed, or cannot be read, raised out of `main()` — exit 1 and a traceback, against a docstring and a door that both promise exit 0 or a named exit 2. Reproduced live: the door's own advertised command died on the sandbox mount artifact. | applied @ `8b1a3219` — named exit 2; G9/G9b/G9d; M3 + M10 |
| 3 | same, `_allow` | important | A 0-byte `settings.local.json` raised instead of counting as empty | applied @ `8b1a3219` — G3b |
| 4 | same, `_allow` | important | `{"permissions": null}` is legal JSON and a `.get` default never fires for an explicit null → `AttributeError` | applied @ `8b1a3219` — G5d; M6 |
| 5 | same, `_allow` | important | A Windows-authored file's BOM made a valid list unreadable | applied @ `8b1a3219` — `utf-8-sig`; G5d |
| 6 | same, `status` | suggestion | The headline counted (file, row) PAIRS, so one rule granted at both user and project scope read as two — and that headline is the number the door quotes | applied @ `8b1a3219` — distinct rules; G5c; M5 |
| 7 | same, `status` | nitpick | The per-file split was labelled by `Path.name`, which for `settings.json` is the **tracked** file's own name — the one line whose job is to separate tracked from machine-local | applied @ `8b1a3219` — role labels (`user=` / `project=`); G5b; M4 |
| 8 | `test_permission_parity.py` G5 | important | Its fixture held one row in one file, so row-count and file-count were indistinguishable; a `status()` counting files shipped green | applied @ `8b1a3219` — G5b, keyed exact-string assertion |
| 9 | `claude_permissions_status.py` `main` | important | The printed list is this script's only product and nothing read it: deleting the whole listing loop and returning 1 shipped green | applied @ `8b1a3219` — G7b captures stdout; M7 |
| 10 | same, module constants | suggestion | `REPO_ROOT`/`RENDERED`/`USER`/`PROJECT` were never pinned; `parents[1]` shipped green | applied @ `8b1a3219` — G7c; M8 |
| 11 | `_artifacts/.../gates/` | important | No mutation receipt, though `mutation_sweep.py` is the house instrument for exactly "can this check fail" | applied @ `55382345` — `sweep.json`, 10/10 killed |
| 12 | `.agents/commands/INDEX.md:65` | important | Still enumerated three sources and "one list" — the pre-SCC-392 door, in a file `E5` exists to keep current | applied @ `8b1a3219` |
| 13 | door frontmatter + 2 generated launchers | suggestion | The description an agent reads before invoking the door still said it writes "Claude Code's and Zoo Code's allow lists" — false since SCC-378, and now silent about the harvest | applied @ `8b1a3219` — first 130 chars unchanged, so the two shortened menu mirrors stay byte-valid |
| 14 | `test_permission_parity.py` E7 | suggestion | The plan promised E7 pin "no apply **and that nothing is deleted**"; only the first half was asserted, so the never-edits law could be deleted silently | applied @ `8b1a3219` — M9 |
| 15 | `tickets/SCC-392.md` §Done | important | Recorded a red `70/72` that the walkthrough and the gate receipt both contradict, and called this lane's own missing INDEX row "pre-existing" | applied @ `8b1a3219` |
| 16 | `workflows_testing_SOP.md:2921` | nitpick | "The rule underneath all eight" closed a table that now holds ten rows — already stale at nine, worse by two | applied @ `8b1a3219` |
| 17 | `implementation_plan.md` | nitpick | Named "§5's script inventory" (§5 is *Which lane am I in?* and has none) and called the new tests a "C-series" (C is the Antigravity-apply block) | applied @ `8b1a3219` |
| 18 | `claude_permissions_status.py` docstring | suggestion | The claim "the two files" is categorical; `~/.claude.json` carries a legacy `projects[*].allowedTools` array | applied @ `8b1a3219` — measured EMPTY on all three project entries, recorded in the docstring so nobody re-derives it |
| 19 | `.agents/scripts/INDEX.md` | nitpick | The new script had no inventory row, the convention its siblings follow | applied @ `09087e3a` (found in the review step, before the fan-out) |
| 20 | `implementation_plan.md` | important | No `## Declared Change Set` block, so there was nothing to reconcile the diff against | applied @ `09087e3a` |
| — | `claude_permissions_status.py:43` | suggestion | *Dismissed (relevance).* `PROJECT` anchors to the script's own tree rather than cwd, so a worktree session could read the lobby's file. The script **prints all three resolved paths on every run** — which is the remedy the lens itself proposed — `--project` overrides, and the anchor is the identical idiom all three sibling scripts use. Nothing to change. |

**Two of my own fixes were weak, and mutation caught them before the verdict.** G8a first rested on a
`len(code) > len(src)//2` size ratio, which fired on an unrelated four-line edit — a false red is a
broken check too; it now pins the property (`main()` is inside the window). G9 first checked only the
exit code, which passes with the guard removed, because `json.JSONDecodeError` already subclasses
`ValueError`; G9b now pins the file name in the message. Both are in the sweep table.

**Findings tail, in one line:** 26 raw findings across five lenses, deduplicating to 20 distinct
issues; 20 assessed real and fixed in this lane, 1 dismissed under the relevance gate with its reason
above, 0 deferred, 0 noise-dismissed. The calibration signal worth carrying forward: the single
highest-value finding was labelled `important` by three lenses and `critical` by one — the assessment
raised it, because a gate that cannot fail is the one defect class this house treats as a hard stop.

### Step 0.7 — re-derivation

1. **Nothing this diff references moved.** SCC-386 landed on `origin/main` after the lane was cut
   (merge-base `78f47333`, `origin/main` `1b88b487`), touching `.agents/rules/constitution.md`,
   `AGENTS.md`, `.agents/rules/INDEX.md` and a new rule plus its test. This diff references none of
   them; every path it names — `families.json`, `permission_render.py`,
   `antigravity_permissions_apply.py`, `zoo_notify.py`, `.gitignore:58`, `.gitignore:23` — still
   resolves, and `check_links` confirms it across 197 claims.
2. **True overlap: 3 files, 2 conflicts, both resolved on this branch.** The overlap is
   `_artifacts/_main/INDEX.md`, `docs/_scc_sops_prds/workflows_testing_SOP.md` and
   `workflows_testing_SOP_changelog.md`. `merge-tree` predicted content conflicts in the INDEX and
   the changelog — both pure newest-first row insertions at the same anchor — and the SOP auto-merged.
   Absorbed into this branch at `5a774384`, keeping both sides' rows in both files.
3. **No landing-order dependency.** The only other live worktree is the main checkout; the four
   `agent-*` trees were this review's own lens copies and are disposable. SCC-386 has already landed,
   so nothing is waiting on this lane and this lane is waiting on nothing.

### Clean-Code Gate

Machine floor imported from the Evidence block above rather than re-run (`run_all`, `workflow_lint`,
`sop_currency`, `check_links` all green at `55382345`). Run here and not there:

| Check | Result |
|---|---|
| `py_compile` on the new script | clean — it is imported and executed by 16 test rows and by the live run |
| Comment contract (§2A) | every non-obvious choice carries its *why*: the `[0::2]` join, the `or {}` / `or []`, `utf-8-sig`, the distinct count, the role labels and the empty-is-empty branch each name the defect they close |
| Convention table (§2C) | matches the sibling `antigravity_permissions_apply.py` — stdlib only, plain-ASCII output for Windows consoles, `Path.home()`/`parents[2]` resolution, `--`-prefixed test overrides, one-line status vocabulary |
| Drift / bloat | imported from Step 1; the one over-build (G8a's size ratio) was cut on its own mutant |

**Changes applied:** 20 findings, all in-lane, across `8b1a3219`, `55382345`, `09087e3a`.

## Your Actions

- [ ] **Which of the 17 machine-local rows should travel?** That is the harvest itself, and it is your
      call, not this lane's — run `/smh-llm-approvals` and name them. Two of them, `Bash(bash:*)` and
      `Bash(sh:*)`, permit any command at all; the door will stop and ask you out loud before either
      renders to both machines.
