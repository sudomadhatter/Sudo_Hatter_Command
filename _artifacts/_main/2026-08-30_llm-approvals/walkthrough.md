# SCC-352 — walkthrough (CONSOLIDATED lane; Part B / SCC-355 built)

review-runtime: fan-out

**Lane:** `chore/SCC-352-llm-approvals` · **Parent:** SCC-352 · **Riders:** SCC-354 (Part A, not
yet built) · SCC-355 (Part B, built here) · **HEAD at write time:** `94de53b6`

## Task Checklist

- [x] **B0 — probe Zoo's notification surface.** Came back NEGATIVE, which is a result, not a
      blocker: Zoo v3.80.1's manifest contributes 19 settings keys and 20 commands and not one is a
      notification, a sound, or an event hook. The plan had already grounded the fallback, so the
      trigger became the thread store instead of a hook.
- [x] **B1 — the notifier.** `.agents/scripts/zoo_notify.py` — classify / compose / store_root /
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
[PASS] suite exit=0 82.7s @ 94de53b6
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

Landed and needing nothing from you: `zoo_notify.py` and its 13-case suite, the 9/9 mutant sweep,
the SOP row, the changelog row, and both INDEX rows. Part A (SCC-354) is planned and audited but not
started, by the build order you approved.

- [ ] **Prove the notifier live on the Mac.** Run `python3 .agents/scripts/zoo_notify.py --watch`,
      then in Zoo trigger one command that stops for approval and let one turn finish. Confirm you
      get a banner AND a phone push for each. ⚠️ If the phone push lands but no banner appears, that
      is the Focus-mode failure, not a broken notifier — terminal-notifier must be in System Settings
      → Focus → Work → Allowed Notifications, and suppressed banners still show in Notification
      Center history.
- [ ] **Prove it on the PC.** Same, with `python` instead of `python3`. The PC has never had
      `notify.sh` either, so this is the first notification either tool has sent from that machine.
