---
type: walkthrough
story: SCC-53
date: 2026-08-09
branch: chore/SCC-53-bug-raised-by-audit
---

# SCC-53 — `Bug` is agent-raised, and restores to Story **or** Task

SCC-49 built `Bug` around the wrong actor and the wrong return path. The docs said *the operator
raises it and nothing else may touch it*; the code restored it to `Story` and only `Story`. Both are
now corrected against the operating model the operator actually wants: **an audit finds a live bug,
traces it back to the ticket that introduced it, and flags that ticket — the operator keeps a manual
door too — and close-out puts it back to whatever the ticket really is.**

The mechanism is not a half-built version of the target. It ran **operator → agent**; the target runs
**agent → operator**. Only the clearing half was reusable, and it was broken.

## Task Checklist

- [x] **The stranding bug — the one that mattered.** `devrecord --closing` restored a `Bug` to
      `Story` and warned-and-quit on anything else. A **Task** flagged `Bug` therefore hit
      *"does not look like BMAD sprint work"* and **stayed a `Bug` forever**, because nothing else in
      the system is allowed to clear one. It now restores whatever `work_type()` computes.
- [x] **`/close-task-merge-tree` now passes `--closing`.** It explicitly refused it, on my assumption
      that `Bug` was Story-only. Task work breaks as easily as story work, so the Task lane has to
      clear it too — and it is a silent no-op on a non-`Bug` ticket, so it is always safe to pass.
- [x] **`.agents/rules/jira.md` — the model rewritten.** Two doors in (audit, operator), one door out
      (close-out). The `Bug` row now says *Story **or** Task*. The ⛔ block keeps what was still true
      (nothing else may retype one, because "correcting" it erases the only signal the work is
      broken) and drops what was not (that the operator alone may set it). A second ⛔ pins the
      restore-to-Story-or-Task rule with the failure it prevents.
- [x] **The contradiction that started this, killed.** The AVCH worked example filed `debug-4.1` as a
      `Bug` under the **grouping** epic — wrong twice over against the type table 40 lines above it:
      a debug story is a `Story`, and it lives under its own **BMAD** epic. Removed, with a note
      saying why, so it does not get "restored" later. **`Bug` is a flag on a broken ticket, not a
      category of work** — that sentence is what the example was missing.
- [x] **`audit` still never retypes a `Bug`** — unchanged, and now says why in its own output: a bulk
      pass cannot tell *still broken* from *fixed*. Only close-out can.
- [x] **Docs swept** — `sudo-update-sprint-memory` Step 4.5, `close-task-merge-tree` Step 4,
      SOP §5 + §11, `scripts/INDEX.md`. `/sync-agents` re-mirrored all four platforms.

## Evidence

| Claim | Proof |
|---|---|
| Full enforcement suite green | `python3 .agents/scripts/tests/run_all.py` → **8/8 files, 238 cases** |
| `jira_feed` cases | **79/79** (was 78 — one inverted, two added) |
| The stranding is pinned red-first in intent | the old case asserted *"a Bug that is NOT BMAD sprint work is left for the operator"* — i.e. it **tested the defect**. Replaced by *"a fixed Bug on TASK work goes back to Task, not stranded"* |
| `audit` safety unchanged, both shapes | a `Bug` over story work **and** a `Bug` over task work are both left alone, each with its own case |
| No stale phrasing left | grep for `operator sets it` / `operator's Bug` / `back to Story` → only the three corrected strings |

`Verdict: PASS @ HEAD` — machine floor is the suite; no deployable surface touched.

## Your Actions

**Deferred by your ruling, filed as [SCC-54]:** the audit-raises-it trigger. The return path is built
and tested; the raise path needs an entry point that does not exist yet — there is no "audit the
site" command to hang it off (`/sudo-live-testing-team` files bug docs but writes no board state, and
the Epic-16 incident pipeline is a different lane). Noted there: **the hard part is the trace, not
the flip.** "Which ticket introduced this bug" is a blame-to-ticket join, and a wrong answer pulls an
innocent ticket out of `Done` — so it should propose the link and stop, not write it silently.
