# SCC-355 — Zoo notifications actually reach the operator (walkthrough)

review-runtime: inline (blocked: the operator's standing budget constraint, verbatim: "You maxed out my subscription weekly limit with this one fix, stay in task and fix this" — this lane was accepted on the stated basis "I'm running this entirely inline. No subagents, no fan-out, nothing spawns.")

**Lane:** `chore/SCC-355-zoo-notify-fix` · cut from `origin/main` @ `8a1b3cbf` · `origin/main` absorbed at `8ed61678` · HEAD `a136927e`
**Plan:** [implementation_plan.md](implementation_plan.md) (with the Self-Audit, verdict GO)
**Diagnosis it acts on:** [diagnosis.md](diagnosis.md)

---

## What was wrong, in one paragraph

Zoo notifications had never fired once, and two separate defects were responsible. The bigger one
was **delivery**: `zoo_notify.py --watch` is a foreground poll loop, Zoo contributes no event hook,
so a live process is the only possible trigger — and what shipped was the script plus an SOP line
telling the operator to run it. Nothing ran it. No process, no LaunchAgent, silent from the day it
landed. The second was the **classifier**: it discarded any thread whose tail carried `partial:
true`, believing that meant a stream still arriving. True of Zoo's narration, false of its asks —
Zoo clears that flag when its own matcher auto-approves and leaves it standing when the operator
must answer, so the guard threw away 81% of the `tool` asks that wanted him.

---

## Task Checklist

- [x] **Reproduce** — no watcher process, no LaunchAgent; a live ask sitting unanswered 17 minutes classified as "needs nothing"
- [x] **Prove the channels are innocent** — `--self-test` fired, the push was read back off the ntfy topic, the operator confirmed his phone
- [x] **RED first** — real fixtures captured, 9 pinning cases red against the shipped code
- [x] **GREEN** — the `partial` guard applies to `say` only; 46/46
- [x] **The delivery gap** — `zoo_notify_install.py`, launchd + Startup `.cmd`; 24/24
  - ⚠️ *found while installing:* `--apply` from this worktree would bake a path close-out prunes → guard added
  - ⚠️ *found while installing:* the agent's log was EMPTY (Python buffers a non-TTY) → `PYTHONUNBUFFERED`
- [x] **The reach check** — the same filter was in `/smh-llm-approvals`; fixed in the brain and both mirrors
- [x] **G5 revert proof** — the fix removed takes the suite from 46/46 to 37/46
- [x] **Mutation sweeps** — 16/16 killed by their declared case
  - ⚠️ *the sweep found two of my own assertions passing for the wrong reason* → both strengthened
- [x] **Docs** — SOP row, changelog, guide §6.1 + new §11.1, both script INDEX rows
- [x] **Live install on this Mac** — running under launchd, PID confirmed, log confirmed

---

## Evidence

### A1 — an operator-facing ask flagged `partial` pages

**RED**, against the shipped `classify()`, after replacing the stub fixtures with real captures:

```
  File ".../test_zoo_notify.py", line 84, in test_pending_ask_classifies_as_ask
    assert m.classify(_load("zoo_ui_messages_ask.json")) == "ask"
AssertionError
  File ".../test_zoo_notify.py", line 134, in test_partial_ask_still_pages_because_zoo_never_clears_it
AssertionError
  File ".../test_zoo_notify.py", line 195, in test_ask_outside_the_measured_sample_still_pages
AssertionError: auto_approval_max_req_reached must page the operator, not vanish
  File ".../test_zoo_notify.py", line 202, in test_completion_result_is_the_only_ask_that_is_not_a_decision
AssertionError
  File ".../test_zoo_notify.py", line 162, in test_finalising_a_partial_ask_in_place_does_not_double_page
AssertionError
AssertionError: zoo-notify: 01a05116 needs nothing     (test_main_actually_honours_custom_storage_path_end_to_end)
TypeError: watch() got an unexpected keyword argument 'fresh'
AssertionError: exactly the fresh pending ask pages; got 0: []
AssertionError: a rewritten file in the SAME state is not news; it must not re-page
-- 36/45 passed --
```

Nine reds, every one raising at its own assertion line — none died in setup. One defect reached
through five different doors, which is stronger evidence than a single case.

**GREEN**, after moving the guard so it applies to `say` only: `-- 46/46 passed --`

**The measurement behind it** (live store, 7 threads, 1,455 messages) — operator-needed asks, i.e.
`autoApprovalDecision` null, split by whether the shipped guard dropped them:

| ask | dropped | would page |
|---|---:|---:|
| `tool` | **13** | 3 |
| `command` | 4 | 23 |
| `followup` | 2 | 3 |
| `mistake_limit_reached` | 0 | 8 |
| `resume_task` | 0 | 15 |

Ten asks on disk carry `partial=True` **and** `isAnswered=True` together — Zoo stamped the answer
on top and never cleared the flag, which is the proof that `partial` is a resting state on an
operator-facing ask rather than a transient one.

### A2 — nothing that was already right changed

The full existing battery stayed green, unmodified. The four verdicts that must not move are
asserted explicitly: a streaming `say` stays silent, an auto-approved ask stays silent, an answered
ask stays silent, `completion_result` still means turn-end. Double-paging needed no new code —
`thread_signature()` keys on `(event, len(messages), tail.ts)` and finalising a partial ask rewrites
it in place, so the signature is identical:

```
sig partial : ('ask', 2, 2)
sig final   : ('ask', 2, 2)      same signature -> sends ONCE: True
```

### A3 — the fixtures are real

```
zoo_ui_messages_ask.json:     76 msgs, 10930 bytes  tail -> ask/tool partial=True isAnswered=None
zoo_ui_messages_turnend.json: 70 msgs, 10076 bytes  tail -> say/completion_result partial=False
redaction audit: 0 leak(s) in both  (/Users/…, C:\Users, sk-…, ghp_… all absent)
```

Pinned by `test_fixtures_are_real_captures_not_hand_written_stubs`, which asserts >50 messages, a
`partial: True` tail, the presence of auto-approved asks, and no leaked path.

### A4 / A5 — the watcher starts itself, and it is running now

```
$ python3 .agents/scripts/zoo_notify_install.py --apply --repo /Users/sudohatter/Sudo_Hatter_Command
zoo-notify-install: wrote /Users/sudohatter/Library/LaunchAgents/com.sudohatter.zoo-notify.plist
  runs: /Users/sudohatter/Sudo_Hatter_Command/.agents/scripts/zoo_notify.py
  launchctl: started

$ launchctl list | grep zoo-notify
26163	0	com.sudohatter.zoo-notify

$ tail -2 ~/Library/Logs/zoo-notify.log
zoo-notify: watching 1 store(s) every 5s (ctrl-c to stop)
zoo-notify: primed on 10 existing thread(s) - watching for new
```

⭐ It is deliberately pointed at the **main checkout**, not this worktree — a login agent outlives
the lane, and close-out prunes the lane. The installer now refuses a worktree path outright.

`NTFY_TOPIC` and a Homebrew-bearing `PATH` ride in `EnvironmentVariables` because launchd sources
no shell profile and its default `PATH` cannot see `terminal-notifier`. Without the latter the
banner half dies while the push half keeps working — harder to diagnose than total silence.

### A6 — a restart while Zoo is blocked still pages

Priming is silent except for an unanswered ask newer than the freshness window (300 s default,
`--prime-window 0` restores total silence). Pinned by two cases: three threads through one priming
sweep — fresh ask, stale ask, fresh turn-end — producing exactly one page, and that page named as
the fresh one.

### A7 — the PC branch

Both platform branches are unit-tested with the platform forced: the Startup `.cmd` uses `pythonw`
(a console window would sit on the desktop and killing it kills the watcher), sets the topic and
`PYTHONUNBUFFERED`, and uses CRLF because `cmd.exe` mis-parses LF-only batch files. **The live PC
run is the operator's, below** — this Mac cannot execute it, and asserting otherwise is the exact
class of claim [[mac-authored-code-hides-windows-bugs]] exists to prevent.

### A8 — the docs

The SOP's Zoo row now says *install it once per machine*, and the old *start the watcher* line — the
instruction that produced this bug report — is gone. Guide §6.1 records the `partial` rule beside
the `autoApprovalDecision` rule; new §11.1 carries the install, the status check, and the two
environment traps. Both scripts have `INDEX.md` rows; the changelog carries one line. The armed
`sop_currency` gate accepted the feature commit with the SOP staged (no `[sop-ok]`); the three
follow-up commits used `[sop-ok]` because the command the operator types did not change.

### A9 — the reach check, and its guard proven

`/smh-llm-approvals` carried the identical filter in prose. Measured on the live store, it listed
23 stopped commands and dropped 4. Fixed in the command brain and both generated mirrors.

⛔ The obvious assertion — grep the repo for the phrase — is **vacuous**, because the fix adds a
warning paragraph that quotes the old filter, so the grep matches the very text proving it was
fixed. The guard reads the *requirement sentence* instead, and it was proven to gate by reverting:

```
(doors reverted)   -- 45/46 passed --  FAILED: test_no_door_tells_an_agent_to_skip_a_partial_ask
(doors restored)   -- 46/46 passed --
```

### G5 — the fix reverted, the tests go red

```
(zoo_notify.py reverted to shipped)   -- 37/46 passed --   [the 9 pinning cases]
(fix restored)                        -- 46/46 passed --
```

### Mutation sweeps — 16/16 killed

Two tables, declared before mutating, every mutant drawn from a decision in the source.

| # | Mutant | Killed by |
|---|---|---|
| M1 | reinstate the bug: `partial` guard back above the `ask` branch | `test_partial_ask_still_pages_because_zoo_never_clears_it` |
| M2 | invert the answered guard | `test_answered_ask_is_not_pending` |
| M3 | invert Zoo's own-decision guard | `test_auto_approved_ask_never_fires` |
| M4 | `completion_result` becomes a decision | `test_completion_result_is_the_only_ask_that_is_not_a_decision` |
| M5 | drop the say-streaming guard | `test_partial_say_still_never_fires` |
| M6 | invert the freshness comparison | `test_priming_pages_a_FRESH_pending_ask_but_never_the_stale_backlog` |
| M7 | **width:** priming exception stops being ask-only | same |
| M8 | **width:** freshness window defaults to zero | same |
| M9 | agent stops starting at login (`RunAtLoad`) | `test_mac_plist_runs_at_load_and_keeps_alive` |
| M10 | one crash becomes permanent silence (`KeepAlive`) | same |
| M11 | **width:** `PATH` loses Homebrew | `test_mac_plist_path_reaches_homebrew_because_terminal_notifier_lives_there` |
| M12 | the log goes back to empty | `test_mac_plist_forces_unbuffered_output_or_the_log_stays_empty` |
| M13 | the worktree guard stops guarding | `test_apply_refuses_a_git_worktree_path_because_the_lane_gets_pruned` |
| M14 | status stops checking the path exists | `test_status_catches_a_plist_whose_script_path_no_longer_exists` |
| M15 | the PC gets a console window | `test_windows_command_starts_minimised_with_pythonw_and_sets_the_topic` |
| M16 | **width:** the `.cmd` loses CRLF | same |

```
-- sweep clean: 8/8 killed by their declared case --   (notifier,  @ ef4dc3f2)
-- sweep clean: 8/8 killed by their declared case --   (installer, @ 25e6a2ff)
-- restore verified: bytes match, nothing was committed, `git diff --quiet` is clean --
```

⭐ **The first sweep FAILED, and that is the whole reason it is run.** Two of my own new assertions
passed with the mutant in place:

- `test_partial_say_still_never_fires` tailed on `say: "reasoning"` — which classifies as `None`
  down the fall-through path whether the guard exists or not. It never tested the guard. Re-aimed at
  `say: "completion_result"` with `partial: True`, the only tail where the guard decides anything,
  plus a positive control that the finished one *does* page.
- `test_priming_pages_a_FRESH…` asserted only the **count**. Inverting the comparison pages the
  stale thread and silences the fresh one — still exactly one page, still an ask, still the same
  title. It now asserts *which* thread paged.

Both were [[prose-pinning-guards-are-vacuous]] in miniature, inside brand-new tests written this
session, and only the sweep could see them.

### The gate

```
[PASS] suite exit=0 91.4s @ 25e6a2ff        receipt: gates/suite.json
       result: pass · dirty_tree: false · dirty_paths: []
```

---

## The contributing causes

**Mechanism.** Two, and they are independent. (1) A feature whose delivery is an instruction to a
human is not delivered; `--watch` needed a process and got a sentence in a document. (2) A field
that looks like a transport detail (`partial`) was read as one, when it is actually Zoo's record of
*who is expected to answer*.

**Reach.** Asked and answered by going to look: the `partial` misreading had already been copied
into `/smh-llm-approvals`, where it hid 4 of 27 stopped commands. Fixed here. The delivery
mechanism has no second instance — `zoo_permissions_apply.py` is the only sibling and it is a
one-shot apply, not a daemon.

**The miss.** `test_partial_ask_never_fires` pinned the bug *as intended behaviour*, and both
fixtures were hand-written 4–5 message stubs with `partial: false` tails while real threads run
76–413 messages. Thirty-eight green tests, none of which had ever seen the shape Zoo writes. A
fixture that cannot express the bug makes every test above it decorative. That is the lesson worth
keeping, and it is why A3 is now a machine-checked acceptance row rather than a habit.

---

## Your Actions

Everything below is done and landed except two things only you can do.

- [x] The merge itself — lands via this branch's PR

- [ ] **Look at the Mac and tell me the banner appeared.** The self-test reported `banner=sent` and
      exited 0, and your phone got the push — but a Work Focus swallows the on-screen banner while
      everything still reports success, so this is the one claim I cannot verify from here. If no
      banner appeared, check Focus first, then System Settings → Notifications → terminal-notifier.
- [ ] **Install it on the PC**, next time you are on that machine:
      `python .agents\scripts\zoo_notify_install.py --apply` — then `python .agents\scripts\zoo_notify.py --self-test`
      to prove both channels there. The Windows branch is unit-tested but has never been run on real
      hardware, and I will not claim otherwise.

---

## Code Review (2026-08-31)

review-runtime: inline (blocked: the operator's standing budget constraint, verbatim: "You maxed out my subscription weekly limit with this one fix, stay in task and fix this" — this lane was accepted on the stated basis "I'm running this entirely inline. No subagents, no fan-out, nothing spawns.")

lens_isolation: none (single context)

lenses_run:
- edge-case · recovered-inline
- literal-correctness · recovered-inline
- acceptance · recovered-inline
- test-adequacy · recovered-inline

lenses_na: blind · n/a - context contaminated (this context wrote the plan, the code and the walkthrough, so a blind hunt cannot be faked)

The Blind Hunter is **dropped, not claimed**. Its entire value is a context that has not read the
builder's reasoning, and this context wrote it — under `inline` the engine drops it rather than
faking it, because a roster may not claim a review was more independent than it was.

dispositions: 5 findings surfaced, 4 assessed real and fixed in-thread, 1 dismissed under the three-question test, 0 left as future work

drift: 0 undeclared / 0 unimplemented / 0 incomplete

⛔ **This is a less independent review than a fan-out, and the roster says so rather than hiding
it.** The Blind Hunter's whole value is a context that has not read the builder's reasoning, and
this context wrote it. What partially replaces it here is that the **mutation sweeps are not
subject to that bias** — a mutant either dies or it does not — and they found two defects this
context had already convinced itself were fine.

### Step 0.7 — blast radius, re-derived against current `main`

1. **Did anything this diff references move?** No. `origin/main` advanced by 44 files (SCC-347's
   `cicd` PR door landed mid-lane). Every path, script and rule this diff names re-resolved;
   `check_links.py --base origin/main` is **clean**.
2. **True overlap and merge result.** Exactly the three ledgers the pre-work audit predicted:
   `_artifacts/_main/INDEX.md`, `workflows_testing_SOP.md`, `workflows_testing_SOP_changelog.md`.
   `merge-tree` predicted one conflict, in `INDEX.md`. **`main` was absorbed at `8ed61678` before
   the verdict**, resolved by keeping BOTH rows — it is an append-shaped ledger, not a rewrite —
   and every changelog row present on `main` was verified still present afterwards, by exact-line
   match, because a silently dropped ledger row was the audit's own pre-mortem narrative for F2.
3. **Live sibling lanes.** None remaining; `chore/SCC-347-*` landed. No landing-order dependency
   is left open.

`review_level`: **standard** — derived, not chosen: the radius touches a script others import, a
door surface and the SOP, and the diff carries more than three source files.

`risk_seam.py classify --repo <this tree>` → `unclassified`, the permanent and correct answer in
the command centre (SCC-289: a code graph parses code, this repo is markdown). Run for the shape;
every judgement below comes from reading the diff.

### Findings

| # | Finding | Anchor | Disposition |
|---|---|---|---|
| 1 | An unused parameter — `startup_path(home, platform)` never reads `platform` | `.agents/scripts/zoo_notify_install.py:68` | **FIXED** — `code-standards` §2 names unused params outright, and this is fresh code, not inherited debt |
| 2 | A conditional expression used as a statement for its side effect (`… .mkdir(…) if platform == "darwin" else None`) | `.agents/scripts/zoo_notify_install.py:202` | **FIXED** — rewritten as a real `if` |
| 3 | An `ask` whose `ask` is `completion_result` and which is still `partial` classifies `turn_end`, so a turn-end could page while the message is still streaming | `.agents/scripts/zoo_notify.py::classify` | **DISMISSED** — assessed REAL? **no**. Zero occurrences of `ask=completion_result` in the entire live store (7 threads, 1,455 messages); and were it to occur, `thread_signature` keys on the tail's own `ts`, which an in-place finalisation does not change, so it pages once rather than twice. Erring early on a turn-end is also the direction this module fails by doctrine |

**Findings raised in-thread and fixed before this gate** (they are recorded here because they are
the substance of the review, not because they are open): the installer would have baked a
**worktree path** into a login agent that outlives the lane close-out prunes → guard added and
pinned; the agent's **log was empty** on the first live install because Python buffers a non-TTY →
`PYTHONUNBUFFERED` in both platform branches; and the first mutation sweep failed, exposing **two
of this session's own new assertions passing for the wrong reason** → both re-aimed, with a
positive control added to one.

**Disposition tail (§6.5):** 5 findings surfaced, 4 assessed real and fixed in-thread, 1 dismissed
under the three-question test. No finding leaves this lane as future work; `deferred-work.md` is
untouched.

### Acceptance audit

| # | Statement | Where the diff satisfies it | The assertion that proves it |
|---|---|---|---|
| A1 | an operator-facing `partial` ask pages | `zoo_notify.py::classify` | `test_partial_ask_still_pages_because_zoo_never_clears_it` — RED against shipped, GREEN after; mutant M1 killed |
| A2 | no verdict that was already right changed | same | the unmodified battery + `test_a_finalised_ask_pages_exactly_as_a_partial_one_does`; mutants M2–M5 killed |
| A3 | fixtures are real captures | both fixture files | `test_fixtures_are_real_captures_not_hand_written_stubs` (>50 msgs, `partial: True` tail, auto-approved asks present, no leaked path) |
| A4 | the watcher starts itself and is restarted | `zoo_notify_install.py` | `launchctl list` → `26163 0 com.sudohatter.zoo-notify`; mutants M9, M10 killed |
| A5 | a launchd watcher resolves the right topic | `build_plist` | `test_mac_plist_carries_the_ntfy_topic_…`; M11 (PATH width) killed |
| A6 | a pending ask at startup still pages | `zoo_notify.py::watch` | two priming cases; mutants M6, M7, M8 killed |
| A7 | the PC has a shipped artifact and a documented step | `build_cmd`, guide §11.1 | `test_windows_command_starts_minimised_with_pythonw_…`; M15, M16 killed. **Never executed on Windows — operator checkbox** |
| A8 | the docs say install, not run | SOP, guide, both INDEXes, changelog | `check_links` clean; `sop_currency` accepted the feature commit with the SOP staged |
| A9 | no door tells an agent to skip a `partial` ask | the brain + both mirrors | `test_no_door_tells_an_agent_to_skip_a_partial_ask`, proven to gate by reverting the doors (45/46 → 46/46) |

**Drift, both directions.** Nothing in the diff is outside the list. The declared change set
reconciles exactly:

```
{"present": true, "incomplete": [], "undeclared": [], "unimplemented": []}
```

### The command-centre gate

| Check | Result |
|---|---|
| enforcement suite (`run_all.py`, through the receipt writer) | **PASS** exit=0, 88.7 s @ `a136927e`, `dirty_tree: false` |
| `check_links.py --base origin/main` | clean |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info (pre-existing BOMs) |
| `hooks_armed.py` | ARMED — `core.hooksPath=.githooks` |
| `declared_change_set.py diff` | 0 undeclared / 0 unimplemented / 0 incomplete |
| door parity (brain vs 2 generated mirrors) | opencode byte-identical; workflow differs only in its truncated `description:` |
| mutation sweeps | 16/16 killed by their declared case; restores byte-verified |
| `py_compile` on both new/changed scripts | clean |

### Clean-code gate (`/smh-clean-code-audit`, judgment half)

Comment contract: every non-obvious block carries its *why* and its ticket. No commented-out code,
no unowned TODO, no bare `except:` (the one broad catch is in `send()` and re-reports the failure
rather than swallowing it, which is its documented job — a push failure must not kill the banner).
No new abstraction with a single caller: `zoo_notify_install.py` is an entry point in the same
shape as its sibling `zoo_permissions_apply.py`. Both machines respected — no bare `python`, no
`C:/` literal, no `;` separator, and every path assertion compares `Path` parts rather than strings.

Verdict: CONCERNS @ a136927e

**Why CONCERNS and not PASS.** Every gate above is green and every finding is fixed. The cap is
for two claims that assert **machine state this Mac cannot reach**, following the SCC-332
precedent: the Windows Startup branch has never executed on Windows, and the Mac banner's
appearance **on screen** is unconfirmed — `--self-test` reported `banner=sent` and exited 0, and
the ntfy push was verified end to end (server read-back plus the operator's own confirmation), but
a Focus mode swallows the banner while everything still reports success. Both are already
`## Your Actions` rows. Neither blocks the merge; both are honestly open.
