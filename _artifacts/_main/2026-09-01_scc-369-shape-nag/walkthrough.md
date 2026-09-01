# SCC-369 — Nag the agent, don't rewrite the rule

**Lane:** `chore/SCC-369-shape-nag` · worktree `.claude/worktrees/scc369-shape-nag`
**Plan:** [implementation_plan.md](implementation_plan.md) · **Ticket:** SCC-369 (Task, one consolidated lane)
**Base:** `origin/main` @ `645ea5e7`, absorbed to `e54e0c37` mid-lane

---

## What this lane actually did

`command-shape.md` was a rule that reached every platform and changed nobody's behaviour. It is
summarized in `AGENTS.md` §6, restated in `zoo-team.md` for every Zoo seat, keyworded into
`rule-trigger.py`, and it fired twice as a prompt injection during the very session that measured
it — while that session broke it repeatedly. The measurement is the whole argument: over 25 Claude
sessions and 7,858 Bash calls, **1,933 violations of that one rule, 98.9% of every detectable
violation in the transcripts.** Five copies of the law, and near-total non-compliance.

So this lane stopped writing the rule down and started **nagging** — injecting the correction at
the instant of the mistake, citing the rule file by name so the agent is sent back to the law
rather than handed a sixth restatement of it. That is the operator's ruling of 2026-09-01, and it
is now written into the rule itself as §Nag, with its own limits attached so a future editor
cannot quietly turn a nag into a gate.

**The channel was established by probe, not by assumption.** Only one of four candidate channels
reaches the model: `PostToolUse` → `hookSpecificOutput.additionalContext`, verbatim. A hook's
`systemMessage`, its stderr, and a `PreToolUse` `allow` carrying a reason all go nowhere the model
can read. `PostToolUse` is also the right *safety* answer rather than a compromise — it runs after
the command, so it cannot block, wedge, or slow a headless run, and `permissionDecision: "ask"`
would have been worse than useless because it becomes an **auto-DENY in auto mode**.

**The front door was manufacturing the problem it complained about.** `AGENTS.md` §6 still carried
the pre-SCC-351 text telling agents to *"use `git -C`"* — the exact spelling Zoo's permission layer
auto-denies — and so did five places in the operator's SOP, including the row whose entire subject
is agents working on the wrong tree, which named `git -C` as its remedy. An agent obeying the front
door faithfully generated the approval stops. Of 1,247 `git -C` invocations measured, **521 named a
verb the allow list cannot pre-approve**; every one of those was a stop that would have been silent
in the `cd <abs> && git <verb>` shape the rule already mandated.

**What the nag is deliberately not.** It never blocks — asserted by test, because a mutant that
returns `ask` must fail the suite. It is not applied to destructive commands: a `PostToolUse` nag
speaks *after* the damage, so `git add -A` and `git worktree remove --force` stay `PreToolUse`
concerns and are named out of scope rather than silently skipped. And Zoo Code gets **no nag at
all**, because Zoo has no hook surface of any kind — that is why `zoo_notify.py` has to poll the
thread store. Zoo gets measurement and a correct fence instead, and the rule says so in the
negative so the next reader does not spend a day trying to write one.

## What closed, item by item

**1 · `AGENTS.md` §6 reconciled.** The gate now states the per-piece law — permission layers judge
a compound command **piece by piece**, so `cd <abs> && git status` is two matchable pieces while
`git -C <path> status` is one piece no verb rule can see — and pins the `cd <abs> && git` spelling.

**2 · The scan that should have caught it, widened.** `test_zoo_permissions.py`'s `git -C` sweep
reached `.agents/{commands,rules,skills}` only, so no test could see the root entry files where the
bad text actually lived. It now covers them. Both halves are proved: a live line rejects, and a
blockquoted teaching line still passes, so prose that *explains* the anti-pattern is not swept up.
The mutant confirms the scan is not pinned to one filename — re-inserting `git -C` into `CLAUDE.md`
goes red too.

**3 · `shape-guard.py`, the nag.** Registered through `run-hook.sh`, never a bare interpreter —
naming one platform's binary reproduces SCC-77, where the PC has `python` and no `python3` and the
hook exits **127 in silence**, which is indistinguishable from a hook with nothing to say. It fires
exactly one nag per broken rule, names the rule and the remedy, stays silent on a clean command, on
a `grep` *for* the string, and on a heredoc body, and fails open on malformed input.

**4 · `shape_scan.py`, the measurement.** Its load-bearing design decision is that it does **not
re-implement the three rules** — it calls the hook's own `violations()` and reads the rule number
out of the nag text. The measurement therefore cannot drift from what the nag actually catches, and
`test_shape_scan.py` fails if a private copy of the detector ever creeps back in. The negative
battery is the point of the tests, not decoration: the first cut of this scanner counted a `grep`
*for* `"git -C"` as a use of it, and counted heredoc bodies as commands.

**5 · The ruling promoted to law.** `command-shape.md` now carries §Nag with the operator's words,
the measurement that justifies it, the mechanism, and three numbered limits — a nag may never
block, a nag cannot protect against a destructive command, and only `PostToolUse`
`additionalContext` reaches the model. Six new checks in `test_rule_frontmatter.py` went red first.

**6 · The Zoo fence corrected.** Eight commands that repeatedly stopped and waited for approval,
and that no deny row protects, were promoted: `npx vitest`, `npm run`, `test -`, `sleep`, `ps aux`,
`ln -s`, and the two-machine venv twin (`backend/.venv/bin/` and `backend/.venv/Scripts/`, because
the same repo resolves to a different directory on the Mac than on the PC). All eight were checked
against the deny list first; none collides. The tracked file reads **120 allow / 105 deny**.

The store itself is being **reset rather than merged**, and the guide now records why. 143 entries
exist only in one Mac's globalState and never existed on the PC; `zoo_permissions_apply.py` has no
surgical remove, so keeping them would mean committing debris like `do`, `done` and `giast` into
repo policy. Of the 143, **101 are already covered by tracked prefixes and only 42 newly prompt** —
every one of those debris, a typo, or a bare-token superset whose trailing-space form is already
tracked. The reset also closes the `rm -f` hole with no deny-list change at all.

## Evidence

Whole gate, run bare, after the review fixes:

python3 .agents/scripts/tests/run_all.py — EXIT_CODE_WAS=0 — 70/70 files passed

python3 .agents/scripts/workflow_lint.py --toolkit-only — 0 error(s), 0 warning(s), 8 info

python3 .agents/scripts/check_links.py --base origin/main — 13 markdown file(s), 234 path claim(s) checked — clean

Per-file, after the review:

python3 .agents/scripts/tests/test_shape_guard.py — 17/17 passed (was 13/13)

python3 .agents/scripts/tests/test_shape_scan.py — 11/11 passed (was 8/8)

python3 .agents/scripts/tests/test_zoo_permissions.py — 20/20 passed (was 17/17)

python3 .agents/scripts/tests/test_rule_frontmatter.py — 18/18 passed (was 17/17)

python3 .agents/scripts/shape_scan.py --self-test — NEGATIVE CONTROLS: PASS (all nine score zero) · POSITIVE CONTROLS: PASS (all five fire with the right rule)

⛔ **The published baseline changed, because the review proved the detector wrong in BOTH
directions.** The figures below are the corrected measurement and are what every document in this
lane now carries. The originals are recorded here rather than quietly replaced, because the
correction is the most important thing this review produced:

| rule | shipped | corrected | why it moved |
|---|---|---|---|
| 3 · piped gate | 9.49 % | **6.88 %** | `GATE` matched a gate's FILENAME anywhere in a pipe piece, so `sed … test_x.py \| head` — reading a file — counted as running one. Three lenses measured the same class independently, at 15.4 / 15.9 / 21.8 % of rule-3 hits. Now matched in COMMAND POSITION. |
| 2 · exit-echo tail | 9.36 % | **11.92 %** | the regex required `;` or `&&` before the `echo`, so every multi-line call whose second LINE was the echo scored zero — 225 of them, under-reported. A newline is a separator too. |
| 1 · `git -C` | 5.79 % | **5.65 %** | quote handling was two regex passes, so an apostrophe inside a double-quoted string paired with a later one and swallowed real violations. One left-to-right pass now. |

Corrected totals over the same window: **1,946 of 8,355 Bash calls — 23.3% of every call — break
this one rule**, across 25 sessions. The old headline (*"98.9% of every detectable violation"*) is
gone: it was a share of a denominator nothing in this lane measured, and 23.3% of every Bash call
is both larger in force and actually derivable from the instrument that ships here.

- **Zoo Code** — 19.03 / 4.45 / 3.64 % over 247 commands in 19 threads, reproduced exactly to two decimals when taken. ⛔ **No longer re-derivable:** Zoo's task directory came back **empty** after the VS Code restart on 2026-09-01, and no `ui_messages.json` survives anywhere under `globalStorage`. The scan reports *"no commands found — nothing to measure"* rather than a fabricated 0 %, which is correct, and is now asserted by `test_ingest_actually_reads_a_fixture_store` so an empty read can never again be mistaken for compliance. Nothing in this lane touched Zoo's task store.

## Acceptance

| | Statement | Result |
|---|---|---|
| A | `AGENTS.md` §6 states the per-piece law and the `cd <abs> &&` pin; no `git -C` outside a blockquote in any root entry file | **MET, both halves** — the negative half by `test_root_entry_files_carry_no_git_dash_c` + its `CLAUDE.md` mutant; the affirmative half was UNGUARDED at review time (deleting the whole §6 bullet left the gate 70/70) and is now `test_root_entry_files_STATE_the_law_they_were_corrected_to_carry` |
| B | A piped gate, an exit-echo tail and a `git -C` each produce exactly one nag naming their rule | **MET** — `test_shape_guard.py`, now also across all nine gate spellings and with a remedy assertion on every rule, not only rule 1 |
| C | A clean command, a `grep` for the string, and a heredoc body produce no nag | **MET, and widened** — the battery grew from six controls to nine: reading a test file through a pipe and searching for the exit-tail literal were the two false positives it was missing |
| D | The hook returns `allow` on every path, and a mutant returning `ask` fails the suite | **MET, and strengthened** — `test_never_blocks` now also rejects `continue`/`stopReason` (the hardest stop lever, which it missed) and whitelists the emitted key set, so the next blocking key added to the contract fails without anyone remembering to name it |
| E | `shape_scan.py` reproduces the baselines | **MET on the CORRECTED figures** — 6.88 / 11.92 / 5.65 %, which every document in the lane now carries. Row E previously named a third triple that nothing reproduced; see the table above. The Zoo half is proved by its capture, not a re-run, because the store has since been emptied |
| F | `command-shape.md` carries §Nag and `rules/INDEX.md` its row | **MET** — `test_rule_frontmatter.py` 18/18; the six §Nag checks now read the §Nag SECTION rather than the whole file, so gutting the section fails them |
| G | `zoo_permissions_apply.py --status` reads *in sync* on both lists | **PENDING the operator's hands** — see Your Actions |
| H | Whole gate green | **MET** — 70/70, exit 0 |

## Your Actions

⛔ **Checkbox rows, not a table.** `jira_feed.py reconcile-actions` and `finish` read `- [ ]`
lines; the table this section used to be was invisible to both, so `finish` would have closed the
ticket `Done` while row G below was provably still open. Found by this lane's own close-out.

- [ ] **Quit VS Code fully (Cmd+Q, not just close the window), then run the Zoo permissions apply in
      Terminal.app — not VS Code's integrated terminal — and read its closing `--status`.**
      Run it from the main checkout after the merge:
      `cd /Users/sudohatter/Sudo_Hatter_Command && python3 .agents/scripts/zoo_permissions_apply.py --apply && python3 .agents/scripts/zoo_permissions_apply.py --status`
      Both lists must close reading **in sync with tracked file** — that line IS acceptance row G.
      Measured at close-out and still open: `allowedCommands: 255 (DRIFT: 7 tracked entries missing
      from store, 142 store-only entries)`. It reads 142 and 7 rather than 143 and 8 because one of
      the eight promotions (`ln -s `) already existed in the store.
      **Why it is yours and not mine:** the apply writes into VS Code's globalState SQLite, and VS
      Code flushes its own in-memory copy on exit — so a write made while it runs is silently
      undone. `zoo_permissions_apply.py` refuses while it detects VS Code running, by design. This
      agent session lives *inside* VS Code, so it cannot be the thing that waits for VS Code to be
      gone.

- [x] The merge itself — lands via this branch's PR

## Out of scope, named not dropped

- **A nag for `git add -A` and `worktree remove --force`.** Destructive — a `PostToolUse` nag speaks after the damage. At 4 and 18 hits in 7,858 calls they are a risk problem, not a time problem, and they belong in a `PreToolUse` guard.
- **Any nag for Zoo seats.** Zoo has no hook surface. Measurement and a correct fence are what it can have.

---

review-runtime: fan-out
lens_isolation:  worktree

## Code Review (2026-09-01)

Verdict: PASS @ e1cfe613
Suite evidence measured at e1cfe613 — `run_all.py` 70/70, exit 0, on a clean tree.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok — truncated by the 20-file cap: 13 of 24 files handed over, the 11 withheld named in its report; it declared the truncation on its first line and did not spend its top-up
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

dispositions:    per-lens: blind-hunter=3/2/0 · edge-case-hunter=2/0/2 · literal-correctness-hunter=3/3/1 · acceptance-auditor=8/1/2 · test-adequacy-auditor=8/2/0 (a multi-lens finding counts once per contributing lens)
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — reconciled with `--no-renames` against `origin/main...HEAD`; two review-fix files (`guard-cwd-escape.py`, `new_machine-migration-guide.md`) were added to the Declared Change Set when the review created the need for them

**Scope.** The `origin/main...HEAD` diff, 24 files, re-taken after Step 0.7 absorbed `origin/main`.
**Method.** Five lenses in parallel, each in its own clean context; the four repo-reading lenses in
their own disposable worktrees cut at `01636abb` and probed to confirm each named itself. The Blind
Hunter got the diff and no tree. The builder's tree was fingerprinted before the fan-out and was
byte-identical after it — no lens wrote to the subject.

### Step 0.7 — re-derivation

1. **Nothing this diff references moved, was renamed, or was deleted on `main`.** `origin/main` is
   a full ancestor of `HEAD` after the absorb; zero files landed between the merge base and
   `origin/main`. The three surviving mentions of `/smh-slash-command-updating` (which SCC-367
   deleted) are all narrative — SCC-367's own ledger row, its own SOP paragraph, and a plan line
   describing its change — none instructs an agent to open the deleted file. `check_links.py
   --base origin/main` is clean across 234 path claims.
2. **True overlap is empty and the merge does not conflict.** `git merge-tree --write-tree HEAD
   origin/main` produced tree `365699d6` with no conflict messages. The earlier absorb had three
   conflicts — the artifact ledger (both rows kept) and the two generated `doc-graph` files
   (regenerated, never hand-merged).
3. **One sibling lane is live and it does not block this one.** `chore/SCC-370-ag-thin-launchers`
   sits at `e54e0c37`, level with `main`, carrying no commits of its own, so there is no landing
   order to respect in either direction.

### Findings

Twenty-nine findings came back across five lenses. **Sixteen were assessed real and fixed in this
lane; thirteen were dismissed** under `code-standards` §6.5 — the assessor decides, not the label.
Two dismissals disagreed with their lens's severity and are named below, per the calibration rule.

| # | file:line | severity | failure scenario | disposition |
|---|---|---|---|---|
| 1 | `.agents/hooks/shape-guard.py:46` | important ×3 lenses | `GATE` matched a gate's filename anywhere in a pipe piece, so `sed -n '1,80p' tests/test_x.py \| head` was nagged for "piping a gate". Measured at 15.4 / 15.9 / 21.8 % of rule-3 hits by three lenses independently; it also inflated the published rule-3 rate from 6.88 % to 9.49 % | applied @ e1cfe613 — `command_prefix()` matches in command position; killed by mutant M3 |
| 2 | `.agents/scripts/tests/test_shape_scan.py:70` | critical | `test_detector_is_the_hooks_own` was a source-grep satisfied by the file's own docstring. A full private detector copy, then diverged from the hook, left the file 8/8 green | applied @ e1cfe613 — asserts module identity + a differential over nine gate spellings; the same mutant now kills 7 tests |
| 3 | `.agents/hooks/guard-cwd-escape.py:270` | important ×2 lenses | its remedy 2 told the model *"Use `git -C /abs/path ...`"*, so an agent obeying the PreToolUse guard was immediately nagged by the new PostToolUse one | applied @ e1cfe613 — remedy rewritten; `test_hooks_never_recommend_the_denied_spelling` sweeps `.agents/hooks/`, narrowed to recommendation with both halves proved |
| 4 | `.agents/scripts/shape_scan.py:98-186` | important | the entire ingest was untested: renaming the `Bash` filter, breaking the Zoo filter, or an empty `HOME` each reported 0.00 % and stayed green — indistinguishable from perfect compliance | applied @ e1cfe613 — fixture seams + known-answer assertions; killed by M8 and M9 |
| 5 | `.agents/hooks/shape-guard.py:89` | important | rule 2 required `;`/`&&` before the echo, so 225 multi-line calls whose second LINE was the echo scored zero — under-reporting rule 2 by 2.6 points | applied @ e1cfe613 — a newline is a separator too |
| 6 | `.agents/scripts/tests/test_shape_guard.py:154` | important | `test_never_blocks` missed `continue: false`, which halts the session outright and outranks `decision` | applied @ e1cfe613 — whitelists the emitted key set; killed by M2 |
| 7 | `.agents/scripts/tests/test_shape_guard.py:179` | important | the registration test pinned strings: a matcher of `Write`, or a one-character path typo, each left it 13/13 green with the hook a permanent no-op | applied @ e1cfe613 — asserts the matcher, resolves the path, and RUNS the registered command; killed by M5 and M6 |
| 8 | `.agents/scripts/tests/test_shape_guard.py:67` | important | `assert "command-shape" in text` was matched by the hook's own preamble, so `RULE` could point at a file that does not exist | applied @ e1cfe613 — pins the path and asserts it exists; killed by M1 |
| 9 | `AGENTS.md` §6 | important | acceptance row A's affirmative half was unguarded — deleting the entire §6 bullet left the gate 70/70 green | applied @ e1cfe613 — `test_root_entry_files_STATE_the_law_they_were_corrected_to_carry` |
| 10 | `.agents/hooks/shape-guard.py:139` | important | the rule-1 nag claimed the call *"stops and waits"* — false on 404 of 470 firings, because thirteen `git -C * <verb>` allow rules exist. A false fact is the one thing an agent can rationalize past | applied @ e1cfe613 — the text now says what is true on each platform |
| 11 | `.agents/hooks/shape-guard.py:66` | suggestion | `strip_quoted` ran two regex passes, so an apostrophe inside a double-quoted string paired with a later one and swallowed a real `git -C` between them — 2 hidden in the live corpus | applied @ e1cfe613 — one left-to-right pass, shared with the rule-2 span check |
| 12 | `.agents/scripts/shape_scan.py:213` | suggestion | `--sessions -1` is a SLICE, not a count: it silently widened the window from 1 session to 110 and 41,853 commands | applied @ e1cfe613 — refused at the boundary; killed by M10 |
| 13 | `.agents/scripts/tests/test_shape_guard.py:62` | suggestion | only one of the nine gate spellings was exercised — the coverage hole the diverged-copy mutant rode through | applied @ e1cfe613 — one case per spelling |
| 14 | `.agents/scripts/tests/test_shape_guard.py:71` | suggestion | rules 2 and 3 asserted the citation but not the REMEDY; truncating rule 3's remedy left it 13/13 green | applied @ e1cfe613 — a nag that names a fault without its fix is the shape the house bans |
| 15 | `.agents/scripts/tests/test_rule_frontmatter.py:163` | nitpick ×2 lenses | the six §Nag checks read the whole rule file, so *"§Nag names `shape-guard.py`"* really asserted *"the file mentions it somewhere"*; and line 183's `or` branch was unreachable (`"may never block"` contains `"never block"`) | applied @ e1cfe613 — scoped to the §Nag section, dead branch removed |
| 16 | plan row E · `command-shape.md` · SOP · walkthrough · `_artifacts/_main/INDEX.md` | suggestion ×3 lenses | four different Claude baselines shipped in one diff, and row E's own triple appeared in no assertion. Findings 1, 5 and 11 then made all of them wrong | applied @ e1cfe613 — re-measured and corrected in every document; the before/after table is in `## Evidence` |
| — | `.agents/hooks/INDEX.md:83` | nitpick ×3 lenses | the new row was inserted one slot out of alphabetical order in a block labelled auto-generated | applied @ e1cfe613 — dismissed on the first two reports as self-healing; three independent lenses is signal, and the move is one line |
| — | `docs/migrations/install_guides/new_machine-migration-guide.md:171-174` | suggestion | three RUNNABLE `git -C … status --short` lines survived in a bash fence while the changelog claimed the guidance was now the same everywhere | applied @ e1cfe613 |
| — | `docs/migrations/zoo-code-permissions-guide.md` | nitpick ×2 lenses | three counts for one set — 143 store-only, 142, and "those 139 rows" | applied @ e1cfe613 — reconciled, and the 142/7 arithmetic after the eight promotions is now explained rather than left to look like a fourth number |
| — | thirteen further findings | — | dismissed under `code-standards` §6.5: pre-existing debt outside this diff, findings the lens itself scored below its own reachability bar, and taste | dismissed |

**Calibration — the two assessments that disagreed with their label.** The Test-Adequacy Auditor
labelled the vacuous `test_detector_is_the_hooks_own` **critical** and it was right to: a private
copy of the detector defeats the one structural property this lane sells, and its mutant proved it.
In the other direction, the Acceptance Auditor's recommendation to **drop thirteen
`Bash(git -C * <verb>)` allow rules** from `.claude/settings.json` was assessed real in its premise
and wrong in its remedy — dropping them would make 404 previously-silent calls stop and wait for a
human, which adds the friction this lane exists to remove. The honest fix was the nag's sentence,
not the operator's permission surface, and that is what shipped.

### Gates

| Gate | Result |
|---|---|
| Enforcement suite | `python3 .agents/scripts/tests/run_all.py` — **70/70 files passed, exit 0** |
| Toolkit lint | `workflow_lint.py --toolkit-only` — **0 error(s), 0 warning(s), 8 info** (pre-existing BOM notes on vendor `testarch-*` files) |
| Assertion evidence | `test_shape_guard.py` 17/17 · `test_shape_scan.py` 11/11 · `test_zoo_permissions.py` 20/20 · `test_rule_frontmatter.py` 18/18 — and **ten mutants run, ten killed**, each attributable to the right named test |
| SOP currency | `sop_currency.py --paths <24 changed> --message "…"` — silent, exit 0 |
| Link + anchor | `check_links.py --base origin/main` — 13 files, 234 path claims, **clean** |
| Door parity | **n/a** — no command was added, renamed or deleted |
| Declared set | `undeclared=0 · unimplemented=0 · incomplete=0` |

### Clean-Code Gate

Machine floor imported from the Gates table above rather than re-run (`/smh-clean-code-audit`
nested, SCC-146). `py_compile` clean on all four changed Python files. Comment contract (§2A): every
new block carries its *why* and its SCC-369 provenance, and each review fix names the mutation that
proved it — the anchors are traps, not narration. Convention table (§2C): stdlib only, no new
dependency, `sys.executable` carried into every subprocess so neither machine's interpreter is
named, no hardcoded paths. Drift and bloat findings imported from Step 1 rather than re-hunted; no
new abstraction has a single caller — `quoted_spans()` has two (rule 2's position test and
`strip_quoted`), and `command_prefix()` is called from the rule-3 loop and asserted directly by
tests.

**Changes applied: sixteen, all listed above.** The implementation was not correct as-is.

## Close-out (2026-09-01)

The close-out's own gates caught four things the review had not, and all four are fixed on this
branch before the PR.

**Three in the migration guide.** This lane's `git -C` rewrite of a PowerShell verification block
was itself broken: a bare `cd A` followed by a bare `cd B` resolves B *relative to* A, so the second
repo check ran in the wrong place and left the shell parked inside a project. `Push-Location` /
`Pop-Location` is the native PowerShell idiom that pins the target and comes back, so it satisfies
`command-shape.md` rule 1 without inventing a chain that cannot run. Two pre-existing unresolved
path claims came into scope with the file and were fixed with it — AGY's quick-fix walkthrough was
written bare so it resolved to nothing from the lobby root, and the phantom-agent aside spelled out
a file whose whole point is that it must **not** exist.

**One in this walkthrough.** `## Your Actions` was a Markdown table. `reconcile-actions` and
`finish` both read `- [ ]` rows, so both reported *nothing is owed* while acceptance row G was
measurably still open — `finish` would have written `Done` over it. It is checkbox rows now, and
`reconcile-actions` exits 3 on the one that is genuinely outstanding.

**Landing gate, re-run at the landing sha** because the doc fix moved code outside `_artifacts/`
and correctly revoked the suite SKIP: `run_all.py` **70/70 files passed, exit 0** ·
`workflow_lint.py --toolkit-only` **0 errors, 0 warnings, 8 info** · `check_maps.py --depth3-only
--strict` **silent, exit 0** · `check_links.py --base origin/main` **14 files, 247 path claims,
clean** · SOP currency enforced per commit by the armed `commit-msg` hook, with no `--no-verify`
and no `[sop-ok]` on any code commit in the lane.
