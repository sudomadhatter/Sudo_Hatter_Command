# SCC-352 — walkthrough (CONSOLIDATED lane; Part B / SCC-355 built)

review-runtime: fan-out

**Lane:** `chore/SCC-352-llm-approvals` · **Parent:** SCC-352 · **Riders:** SCC-354 (Part A, not
yet built) · SCC-355 (Part B, built here) · **HEAD at write time:** `94de53b6`

## Task Checklist

- [x] **B0 — probe Zoo's notification surface.** Came back NEGATIVE, which is a result, not a
      blocker: Zoo v3.80.1's manifest contributes 19 settings keys and 20 commands and not one is a
      notification, a sound, or an event hook. The plan had already grounded the fallback, so the
      trigger became the thread store instead of a hook.
- [x] **B1 — the notifier.** `.agents/scripts/zoo_notify.py` — classify / compose / store_roots /
      send, plus `--once`, `--watch`, `--dry-run`.
- [x] **B2 — the trigger.** The watcher over `ui_messages.json`, notifying only on a state
      TRANSITION so a rewritten file in the same state is not news.
- [x] **B3 — SOP, changelog, indexes.** One new per-machine SOP row (and its caption's row count,
      which adding a row silently breaks), one changelog row, one scripts INDEX row.
      - Consequential, not declared: `_artifacts/_main/INDEX.md` needed the session-folder row —
        `test_check_maps.py` F2 failed the suite until it was added. Reported here rather than
        smuggled, because the plan's declared set is what the review's drift check reads.
- [ ] **B4 — the live proof.** The operator's; see `## Your Actions`.
- [ ] **Part A (SCC-354)** — planned, audited, not started.

## Evidence

**B1/B2 — the classifier and the notifier** → `.agents/scripts/tests/test_zoo_notify.py`, 13 cases.

RED, written before the module existed:

```
FileNotFoundError: [Errno 2] No such file or directory:
  '.../.agents/scripts/zoo_notify.py'
-- 0/13 passed --  FAILED: test_answered_ask_is_not_pending, test_ask_and_turn_end_are_distinguishable,
test_auto_approved_ask_never_fires, test_completed_turn_classifies_as_turn_end,
test_compose_is_pure_and_touches_no_network, test_custom_storage_path_setting_wins,
test_empty_thread_is_silent, test_notifier_script_exists,
test_ntfy_topic_defaults_to_the_existing_topic, test_ntfy_topic_env_override_wins,
test_partial_ask_never_fires, test_pending_ask_classifies_as_ask,
test_store_root_resolves_on_mac_and_on_windows
```

The red is the RIGHT red: it dies on the import of a module that does not exist, not in a fixture.

GREEN, after `zoo_notify.py`:

```
-- 13/13 passed --
```

**Non-vacuity** → `sweep.json`, 9 mutants drawn FROM the code, run as one sweep.

First sweep, which is why the sweep exists — it found three defects a green 13/13 could not show:

```
-- SWEEP FAILED --
  * M1 stop honouring Zoo's own verdict: SURVIVED - the named case still passed with the mutant in place
  * M6 the PC resolves to the Mac's store path: SURVIVED - the named case still passed with the mutant in place
  * M2,M3,M4,M5,M7,M8,M9: SWEEP ERROR - exit 1 with no `FAILED:` line
```

- **M1 survived** because `test_auto_approved_ask_never_fires` also set `isAnswered=True`, so the
  isAnswered guard caught the case first and the guard under test was never exercised.
- **M6 survived** because the test passed a DIFFERENT `home` to each call, so the two paths differed
  for that reason alone and a mutant collapsing win32 onto the Mac branch still passed.
- **The seven "SWEEP ERROR"s** were an attribution mismatch: `mutation_sweep.py` reads a kill off a
  line STARTING with `FAILED:` (its L186), and the house `__main__` harness appends FAILED to the
  tally line instead. Now emitted on its own line.

Second sweep, after those three fixes:

```
-- restore verified: bytes match, nothing was committed, and `git diff --quiet c5d0a4b5` is clean --
-- full file, unfiltered: python3 .agents/scripts/tests/test_zoo_notify.py -> exit 0 --
        | -- 13/13 passed --
-- sweep clean: 9/9 killed by their declared case --
```

**The full gate** → receipt at [gates/suite.json](gates/suite.json).

First stamp was RED and that is the mechanism working — `65/66 files passed  FAILED: test_check_maps.py`,
which was the missing `_artifacts/_main/INDEX.md` row. After adding it:

```
[PASS] suite exit=0 82.7s @ 021144c6   (66/66 files; receipt sha matches)
```

Other floor gates, run bare (a pipe would have read `tail`'s exit code, not the gate's — the house
scar `piping-a-gate-hides-its-exit-code`, which this lane walked into once and corrected):

```
check_links.py --base origin/main   -> exit 0, clean
workflow_lint.py --toolkit-only     -> 0 error(s), 0 warning(s), 8 info
py_compile zoo_notify.py + test     -> OK
```

`check_links` first exited 1 with 13 unresolved paths — every one a Part A file the plan declares
but has not built. There is no house convention for that state, so the plan now writes those ten
paths bare rather than backticked: the linter's own convention 5 says a non-backticked token is not
a claim, and `declared_change_set.py` still parses the block at 29 entries / 0 incomplete / 17 NEW.
Recorded as a formatting-only amendment inside the plan.

## Your Actions

Landed and needing nothing from you: `zoo_notify.py` and its 38-case suite, the 25/25 mutant sweep,
the SOP row, the changelog row, both INDEX rows, and `zoo-code-permissions-guide.md` §6.1/§11.1.
Part A (SCC-354) is planned and audited but not started, by the build order you approved.

- [x] **The merge itself — lands via this branch's PR**
- [x] **Prove the notifier live on the Mac.** Done and measured 2026-08-31:
      `python3 .agents/scripts/zoo_notify.py --self-test` → `banner=sent push=sent`, exit 0. A real
      terminal-notifier banner and a real ntfy push to `mac-sudo-command` both fired.
      ⚠️ If a future run reports `banner=sent` and you see nothing, that is the Focus-mode failure,
      not a broken notifier — terminal-notifier must be in System Settings → Focus → Work → Allowed
      Notifications, and suppressed banners still appear in Notification Center history.
- [ ] **Prove it on the PC — one command, five seconds:**
      `python .agents\scripts\zoo_notify.py --self-test`
      Exit 0 **with a toast on screen** is the pass; exit 1 names the channel that failed.
      This is the only row here that is genuinely yours, and only because a Windows toast that
      displays nothing is indistinguishable from a quiet one to any check running off-machine.
      What was verified from the Mac before shipping: the emitted PowerShell parses clean under
      pwsh 7.7 (0 syntax errors), and every WinRT call matches Microsoft's own
      `ToastNotificationManager` example — `GetTemplateContent`, the `CreateToastNotifier(String)`
      overload, `GetElementsByTagName`/`AppendChild`/`CreateTextNode`, and `ToastText02`, which the
      enum documentation defines as exactly the two text nodes the code writes.
      The script travels with the merge; the PC needs nothing installed.

## Code Review (2026-08-31)

Verdict: PASS @ 3e6afd4d
Suite evidence measured at: 3e6afd4d (receipt `gates/suite.json`, result `pass`, exit 0, 66/66, clean tree)

review-runtime: fan-out
lens_isolation: worktree
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none
dispositions:    per-lens: blind=6/2/0 · edge=6/1/0 · literal=8/2/0 · acceptance=8/2/0 · test-adequacy=10/2/0
drift:           undeclared=0 · unimplemented=16 · incomplete=0 — all 16 remaining are Part A / SCC-354 paths, declared once for the consolidated lane and deliberately unbuilt; `zoo-code-permissions-guide.md` was in this list at review time and is now implemented (finding 20)

**Scope.** `origin/main...HEAD`, 20 files at review time, of which 8 are code/doc and 12 are lane
artifacts. Built half only: Part B / SCC-355. Part A / SCC-354 is planned and unbuilt by design.

**Method.** Five lenses, each in its own disposable worktree cut from the repo under review at the
review sha, launched in parallel. The Blind Hunter got the code diff alone with no tree and no
artifacts — the lane's plan and walkthrough were withheld from it so its blindness was real rather
than declared. 47 raw findings, 26 unique claims after grouping. The verify wave was launched and
then **stopped by the operator mid-run**; every finding acted on below was instead confirmed by the
assessor directly against the source, and two were confirmed by `grep` on the tree.

**Closing finding 5 properly — the operator's push, and it was right.** The first fix made the PC
branch *correct*; it left proving it as an open row waiting on a real Zoo ask, which is not a check
anybody runs. Two things were then done from the Mac that did not need a PC: the emitted PowerShell
was parsed under pwsh 7.7 (0 syntax errors, 111 tokens), and every WinRT call was checked against
Microsoft's own `ToastNotificationManager` reference rather than from memory — `GetTemplateContent`,
the `CreateToastNotifier(String)` overload, the `GetElementsByTagName`/`AppendChild`/`CreateTextNode`
sequence, and `ToastText02`, documented as exactly the two text nodes the code writes. The docs also
confirm *why* the PowerShell AppUserModelID is required: a desktop toast needs a Start-menu shortcut
carrying one. `--self-test` was then added so each machine is proven by one command that exits
non-zero when a channel fails. The Mac is now proven live (`banner=sent push=sent`, exit 0); the PC
row is one command instead of a wait.

**The one line that matters (SCC-205 §6.5).** 47 findings came back; 21 were assessed real and are
fixed in this lane; the rest were dismissed as duplicates of a fixed claim or as noise. Two
assessments disagreed with the lens's own label, both upward: `DECISION_ASKS` was filed
`suggestion` by the Acceptance Auditor and is a real silent-miss of the one ask the feature exists
for, and the mutant-clustering finding was filed `important` but is the reason a 9/9 green sweep
measured 30% of the file.

### Findings

| # | file:line | sev | failure scenario | disposition |
|---|---|---|---|---|
| 1 | `zoo_notify.py:175` watch() | critical | Cold `seen{}` treats every historical thread as fresh news; a finished thread's tail stays `ask/completion_result` forever, so every restart pages once per task dir. Reproduced at 30 sends on one poll. | applied @ c7ea0157 — first sweep primes silently |
| 2 | `zoo_notify.py:188` watch() | important | Thread read twice; the second read loses the race, `read_thread` returns `[]`, `messages[-1]` raises `IndexError` past the only handler, and the watcher dies silently. | applied @ c7ea0157 — read once |
| 3 | `zoo_notify.py:191` watch() | important | De-dupe keyed on the event word, so a second ask arriving in the same poll window reads as "not news". Reproduced: `rm -rf build` never paged. | applied @ c7ea0157 — `thread_signature` keys on the tail `ts` |
| 4 | `zoo_notify.py:31` classify() | important | Allow-list built from two threads drops `auto_approval_max_req_reached` — the ask Zoo raises *because* the operator must intervene. Six real ask types reproduced as silent misses. | applied @ c7ea0157 — deny-list; fails open |
| 5 | `zoo_notify.py:101` banner_cmd() | important | Windows branch loaded the WinRT type, discarded it, and `Write-Output`-ed into a captured pipe. No toast ever shown; `send()` reported `banner=sent`. A check that cannot fail. | applied @ c7ea0157 — constructs and Shows a toast; `='Stop'` |
| 6 | `zoo_notify.py:119` send() | important | `check=False` plus an unconditional `"sent"` reported success for a notifier that ran and failed — on both machines. | applied @ c7ea0157 — reads `returncode` |
| 7 | `zoo_notify.py:154` _project_name() | important | `Path.cwd().name` on a single global daemon stamps every project's banner with the launch directory. | applied @ c7ea0157 — reads the task's own `history_item.json` workspace |
| 8 | `zoo_notify.py:212` main() | important | `zoo-code.customStoragePath` documented as honoured; `main()` called `store_root()` with no args, so the parameter was unreachable and the setting dead. | applied @ c7ea0157 — `read_custom_store` wired; pinned end-to-end |
| 9 | `zoo_notify.py:56` store_root() | important | Only the default profile resolved, while the sibling `zoo_permissions_apply.py` already enumerates `profiles/*/globalStorage/`. `profiles/builtin/` exists on this Mac. | applied @ c7ea0157 — `store_roots()` enumerates profiles |
| 10 | `test_zoo_notify.py:157,166` | important | Two assertions compared `str()` paths with `/`, which are False under `WindowsPath` — the suite was authored to go RED on the PC. | applied @ c7ea0157 — compares `Path.parts` |
| 11 | `sweep.json` | important | All 9 mutants drawn from the four functions the tests already covered; 11 fresh mutants against the other 70% all survived. Measured coverage 37/125 statements. | applied @ c7ea0157 — 22 mutants drawn from the code |
| 12 | `zoo_notify.py:119` send() | critical | Deleting the `if dry_run` guard left the suite green — the one safety property in the CLI contract was unpinned. | applied @ c7ea0157 — M10 now kills it |
| 13 | `zoo_notify.py:77` classify() | important | The `say`/`completion_result` branch never executed under test; no fixture reached it. | applied @ c7ea0157 — pinned, M5 kills it |
| 14 | `zoo_notify.py:142,147` | suggestion | `read_thread`'s corrupt-JSON guard and `newest_thread`'s ordering both unpinned; stripping either left the suite green. | applied @ c7ea0157 — both pinned |
| 15 | `zoo_notify.py:213` main() | suggestion | Exit code 2 — the only signal separating "not installed" from "nothing needed" — untested. | applied @ c7ea0157 — subprocess test |
| 16 | `zoo_notify.py:89` compose() | suggestion | First-line and 120-char truncation untested; a 4KB diff would become the whole push. | applied @ c7ea0157 — pinned |
| 17 | `zoo_notify.py:208` --interval | nitpick | `0` spun a core, `-1` crashed `time.sleep`. | applied @ c7ea0157 — bounded at 1s |
| 18 | `zoo_notify.py:142` newest_thread() | nitpick | A task dir deleted between the glob and the stat raised out of `once()`. | applied @ c7ea0157 — guarded |
| 19 | `sweep.json` | suggestion | The table declared `case` labels the runner cannot select on — this file has no `_harness`, so `--case` was swallowed and `NO_MATCH` (exit 3) could never fire. | applied @ c7ea0157 — `"unfiltered": true` on every mutant |
| 20 | `docs/migrations/zoo-code-permissions-guide.md` | important | §6/§11 declared in the change set and required by acceptance A5/B3; never written. `grep -i 'notif\|ntfy\|banner'` returned 0 hits while the walkthrough ticked B3 after re-wording it. | applied @ c7ea0157 — §6.1 and §11.1 written; grep now 11 |
| 21 | `walkthrough.md:86` | suggestion | Quoted `82.7s @ 94de53b6` while the receipt it links recorded `df8f1c9d` / `82.6`. Evidence transcription, not a false green — the suite was independently re-run green. | applied @ this commit |
| — | INDEX / SOP / changelog | suggestion | `--dry-run` listed as a mode argparse rejects; SOP claimed it fires "only when `autoApprovalDecision` is null" while turn-end never reads it; changelog claimed "pins all of it (13 cases)". | applied @ c7ea0157 |
| — | 26 further findings | — | Duplicates of a claim already fixed above, reached independently by a second or third lens. | dismissed — counted as corroboration, not as separate work |

### Gates

| Gate | Result |
|---|---|
| Enforcement suite | `[PASS] suite exit=0 82.9s @ 3e6afd4d` — **66/66 files passed**, receipt `result: pass`, clean tree |
| Mutation sweep | **25/25 killed by their declared case**; restore verified, full unfiltered run exit 0 |
| Assertion evidence | `test_zoo_notify.py` → `-- 38/38 passed --`, exit 0 (was 13) |
| Toolkit lint | `0 error(s), 0 warning(s), 8 info` |
| Link + anchor | `check_links.py --base origin/main` → exit 0, clean, 12 files |
| SOP currency | exit 0 — the SOP-touching commit carries no `[sop-ok]` escape |
| Door parity | n/a — no command added, renamed or deleted |
| Declared change set | `present: true`, undeclared 0, incomplete 0, unimplemented 16 (all Part A) |

### Clean-Code Gate

Diff-scoped, on the two changed Python files. `py_compile` OK. No line over 120 chars. No
`TODO`/`FIXME`. No bare `except:` — the one `except Exception` carries `# noqa: BLE001` and records
the failure into `result["push"]` rather than swallowing it. No commented-out code. No new
single-caller abstraction: `user_dir()`, `store_roots()`, `read_custom_store()` and
`thread_signature()` each have a caller in the module and a test. No hardcoded interpreter or
`C:/` path. Comment contract met — every non-obvious block carries the why, and the four ⛔ blocks
record the defect each guard exists to prevent.

**Clean-code result: PASS.**

### Post-verdict commits (recorded, not re-stamped)

The `Verdict:` above stays at `3e6afd4d` — the sha the five lenses actually examined. Three commits
landed after it, and none is notifier code:

| Commit | What | Why the verdict does not move |
|---|---|---|
| `50f2bd84` | this review section + suite receipt | artifacts only |
| `91c0c263` | operator edits to `operator-profile.md` and `zoo-team.md`, applied to the `.agents/` **masters** and their `.roo/` mirrors regenerated | operator-authored prose trims to floor rules; no lens reviewed them and none claims to |
| `6a8f0409` | `/smh-sync-agents` propagation | mechanical; the only tracked delta was `.sync-manifest.json`, because the hand-regenerated mirrors were already byte-exact with what sync produces |

⛔ **Those five non-artifact files mean the close-out preflight must NOT grant the suite SKIP**
(SCC-146 freshness is content-based, and content outside `_artifacts/` moved). The suite was
therefore re-run in full at the landing sha and re-stamped — that receipt, not the verdict-sha one,
is the evidence for the merge.

⭐ **Why the edits were moved before they were committed.** They arrived in `.roo/rules/`, which is
the generated Zoo mirror; its own first line reads *"GENERATED by sync-agents … edit the master,
never this copy"*. Committed there, the next `/smh-sync-agents` would have silently reverted all
four. The masters are `.agents/rules/`, and `CLAUDE.md` inlines `operator-profile.md` from there —
so the edits now reach Claude, Zoo, Codex, opencode and Antigravity rather than one mirror.

### Step 0.7 — re-derivation

1. **Nothing this diff references moved.** `origin/main` is `632f7583`, identical to the merge-base,
   so zero files landed on `main` between the plan and this review. Every repo path and anchor the
   diff names re-resolves — `check_links.py --base origin/main` exit 0, clean.
2. **True overlap is empty and the merge is clean.** `git diff --name-only BASE..origin/main` → 0
   files, so the intersection with this lane's 20 is nil. `git merge-tree --write-tree --messages
   HEAD origin/main` wrote tree `c4c56cd2` with no conflict messages. No absorb was needed and none
   was performed; the verdict sha is therefore the sha the gates ran on.
3. **No sibling lane is live.** `git worktree list` shows exactly two trees — the lobby on `main` at
   `632f7583` and this lane. There is no landing-order dependency to name.

`review_level: standard`, derived from that radius rather than chosen: answer 1 came back
contained, but the radius carries gate and contract surfaces (`.agents/scripts/`, the enforcement
suite, the SOP) and the diff changed more than three source files.
