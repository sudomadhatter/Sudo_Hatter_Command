# SCC-355 — why Zoo notifications are silent on the Mac (diagnosis, 2026-08-31)

**Investigated on the Mac, read-only. No repo file changed. Ticket SCC-355 is still `Review Required`,
so this is a follow-on inside its own lane — not a new story ([[followon-fixes-are-not-a-new-story]]).**

---

## G1 · Reproduction

Two live, citable artifacts on this machine at 12:22 on 2026-08-31.

**(a) Nothing is running the notifier.**

```
$ ps aux | grep zoo_notify | grep -v grep
NO zoo_notify PROCESS RUNNING
$ ls ~/Library/LaunchAgents/ | grep -i zoo
(nothing)
```

**(b) A Zoo approval has been sitting unanswered for 17 minutes and the classifier says "needs nothing".**

```
$ python3 .agents/scripts/zoo_notify.py --once --dry-run
zoo-notify: 01a0589d-7c03-702b-878b-6ec3846fb90d needs nothing

thread 01a057c4-27ef  tail written 12:05:14, still the tail at 12:22
  type=ask  ask=tool  partial=True  isAnswered=None  autoApprovalDecision=None
  text='{"tool":"newTask","mode":"debug","content":"QUEEN OF HEARTS — run ③ co…'
  classify() -> None
```

## The channels are NOT the problem — they are proven good

```
$ python3 .agents/scripts/zoo_notify.py --self-test
zoo-notify: self-test -> banner=sent push=sent
exit=0
```

`terminal-notifier` is at `/opt/homebrew/bin/terminal-notifier`; `NTFY_TOPIC=mac-sudo-command` is
exported in `~/.zshrc:114`. Both channels fired and exited 0. **Operator must confirm he SAW them** —
a Work Focus swallows the banner while the run still reports `sent`
([[claude-notifications-hook-schema-and-ntfy]]).

---

## Cause 1 — nothing starts the watcher (this alone explains 100% of the silence)

`zoo_notify.py --watch` is a **foreground blocking poll loop**. Zoo contributes no event hook
(SCC-355's own negative result, guide §6.1), so a process must be alive to poll. Ship shipped the
script and the SOP row — `"Start the watcher once per machine: python3 .agents/scripts/zoo_notify.py
--watch"` — and **no mechanism that starts it**. It was never started here, and even when started it
dies with the terminal or the chat session.

**Fix:** a `launchd` LaunchAgent on the Mac (`~/Library/LaunchAgents/com.sudohatter.zoo-notify.plist`,
`RunAtLoad` + `KeepAlive`) and a Startup-folder shortcut or Scheduled Task on the PC. Note
[[interactive-startup-files-are-invisible-to-automation]]: launchd does **not** source `~/.zshrc`, so `NTFY_TOPIC` must
move to `~/.zshenv` or be set in the plist's `EnvironmentVariables` (harmless today only because the
`.zshrc` value happens to equal the built-in default).

## Cause 2 — the `partial` guard drops the asks that matter most

[`zoo_notify.py:classify()`](../../../.agents/scripts/zoo_notify.py) returns `None` for any tail with
`partial is True`, *before* any other test, on the belief that "a stream in flight is not a decision
point." **That belief is false for `ask` messages.** Zoo clears `partial` when *it* handles an ask and
leaves `partial: true` standing when the *operator* must handle it.

Measured across all 7 live threads (1,455 messages) — asks where `autoApprovalDecision` is null,
i.e. the ones that genuinely want him:

| ask | dropped by the partial guard | would page |
|---|---:|---:|
| `tool` | **13** | 3 |
| `command` | 4 | 23 |
| `followup` | 2 | 3 |
| `mistake_limit_reached` | 0 | 8 |
| `resume_task` | 0 | 15 |
| **total** | **19** | **52** |

**81% of operator-needed `tool` asks are dropped** — and `tool` is the `newTask` subagent launch,
exactly the "Zoo sits blocked and nobody knows" case the script exists to end. The resting state is
provable: 10 asks on disk carry `partial=True` **and** `isAnswered=True` — Zoo stamped the answer on
top and never cleared `partial`.

**Fix (verified against the live store, changes no verdict that was already right):** apply the
partial guard to `say` only.

```python
def classify(messages):
    if not messages: return None
    last = messages[-1]
    kind = last.get("type")
    if kind == "ask":
        if last.get("ask") == "completion_result": return "turn_end"
        if last.get("isAnswered") is True: return None
        if last.get("autoApprovalDecision") is not None: return None
        return "ask"
    if last.get("partial") is True: return None      # a SAY still streaming is not a decision
    if kind == "say" and last.get("say") == "completion_result": return "turn_end"
    return None
```

Simulated over the 7 live threads: the two stuck `ask/tool partial=True` threads flip `None -> ask`;
every other verdict is unchanged, including `say/reasoning partial=True -> None`. Double-paging is
already prevented — `thread_signature()` keys on `(event, len(messages), tail.ts)`, and a partial ask
finalised in place keeps both its index and its `ts`, so the signature is identical and `watch()`
sends once. Proven:

```
sig partial : ('ask', 2, 2)
sig final   : ('ask', 2, 2)      same signature -> sends ONCE: True
```

## Cause 3 — the miss: the test suite pins the bug as intended behaviour

`test_partial_ask_never_fires()` (`test_zoo_notify.py:119`) asserts exactly the wrong thing, and both
fixtures are **hand-written 4–5 message stubs with `partial: False` tails** — real threads run 76–413
messages. The plan called for "a captured `ui_messages.json`"; what shipped was synthesised, so the
battery never saw the shape Zoo actually writes. This is [[stubbed-children-make-green-vacuous]] in
fixture form: 38 green tests, none of which touched reality.

**Fix:** replace the two fixtures with **redacted captures from the live store** (one tail
`ask/tool partial=True isAnswered=None`, one `say/completion_result`), invert
`test_partial_ask_never_fires` into `test_partial_ask_still_pages_because_zoo_never_clears_it`, and
add the pinning regression named for the ticket. Per [[reproduce-before-you-fix]] G2 the new test must
be **seen red against the shipped `classify()`** before the fix lands, and G5 proved by reverting.

## Cause 4 — a backlog already pending never pages, by design

`watch()`'s first sweep primes silently. The ask sitting open since 12:05 will therefore stay silent
even after the watcher starts. That is correct (it prevents a page per historical thread on every
restart), but it means "start the watcher and look" shows nothing — the proof needs a **fresh** ask.

---

## Handoff — what the fixing agent does, in order

1. Work under **SCC-355** on a `chore/SCC-355-*` branch off `main`. No new ticket.
2. Capture two real fixtures from `~/Library/Application Support/Code/User/globalStorage/zoocodeorganization.zoo-code/tasks/*/ui_messages.json`, redacted.
3. Write the pinning test, **see it red**, paste the red.
4. Apply the `classify()` fix above. Run `python3 .agents/scripts/tests/run_all.py` bare.
5. Revert the fix hunk, watch the test go red, restore (G5).
6. Add the LaunchAgent plist + the PC equivalent, and move `NTFY_TOPIC` to `~/.zshenv`.
7. Update the SOP row and guide §6.1/§11 — the install step is now "load the agent", not "run the command".
