---
IsArtifact: true
ArtifactMetadata:
  title: Close-out RECONCILES the operator's task list before it asks finish to close
  type: walkthrough
  date: 2026-08-23
  ticket: SCC-298
  parent: SCC-293
  lane: chore/SCC-298-reconcile-actions
---

review-runtime: fan-out

# SCC-298 — the close-out verifies the task list instead of reading it

**What shipped.** `jira_feed.py reconcile-actions`, and a mandatory step in front of every door
that closes a ticket. `finish` decided `Done` from what `## Your Actions` **claimed**; nothing had
ever checked whether a row's claim was still true. SCC-288 sat at `Review Required` for a day over
one box whose API token already existed, authenticated, and had attached the file.

> **Operator, 2026-08-23:** *"agents are terrible at checking off those task lists, especially when
> its a user task, even if I tell them."* And the ruling on how a row gets ticked: **evidence where
> a machine check exists; where none does, ask and tick on their word — recorded either way.**

**The precedent was already in the file.** SCC-175 stopped reading the *merge* row off a tick and
started **computing** it from the repo — *"a tick is a CLAIM, and `finish --apply` is what writes
`Done` to Jira on the strength of it."* That covered one row. This is that ruling for every other
row, with the difference that most rows have no `merge-base` to ask, so the check is derived per
row and its **answer** is written into the file beside it.

## Task Checklist

- [x] **Step 0 — repo, ticket, runtime probe.** `Sudo_Hatter_Command`; SCC-298 (Subtask under
      SCC-293); `review-runtime: fan-out` recorded here before the review it describes.
- [x] **Step 0.5 — worktree, upstream unset, ticket to In Progress.**
      `chore/SCC-298-reconcile-actions`; `jira_feed.py start` exit 0.
  - ⚠️ `git worktree add … origin/main` **auto-tracked `origin/main`**. `branch --unset-upstream`
    ran immediately — an unnoticed `git push` on that branch targets `main`.
- [x] **Step 1 — six checkable acceptance rows** (A7 added by the audit → seven).
- [x] **Step 1.5 — plan written, self-audited, `approved` received.** Audit verdict **GO** with
      four anchored findings, all baked into the plan before the stop.
  - ⚠️ **F1 (high)** — *"byte-identical in both doors"* had **no check behind it**.
  - ⚠️ **F2 (high)** — it is **four** doors that call `finish --apply`, not two.
  - ⚠️ **F3 (medium)** — `.agents/scripts/INDEX.md:22` enumerates the verbs; it was not declared.
  - ⚠️ **F4 (medium)** — Scope Ledger: `sweep.json` created with no acceptance row behind it.
- [x] **Step 1.6 — no subtasks.** Nothing earns its own branch, and a `Subtask` cannot have
      children (`hierarchyLevel -1` is the floor).
- [x] **Step 2 — RED, and the RED caught its own vacuity.** 15/27 → tightened → **6/27**.
- [x] **Step 3 — GREEN.** Block **41/41**; `test_jira_feed.py` **456/456**;
      `test_command_surfaces.py` **208/208**.
  - ⚠️ **The suite caught an assumption I had not checked**: `.opencode/commands/*` are FULL
    copies of the brain, not thin launchers. Four went stale; `/smh-sync-agents -NoGlobals` fixed
    them. `.agents/workflows/` and the launcher skills *are* thin — git saw no change in either.
  - ⚠️ **The sweep found a real defect**: mutant **M2** survived. The contentless deny-set was
    **35/37 unreachable**, and the case meant to cover it was exercising the floor instead.
- [x] **Step 3 — sweep.** **16/16 killed**, restore verified byte-identical, both closing
      full-file runs green.
- [x] **Step 3.5 — eject tripwire clear.** No deployable path in the diff, no story shape, no
      NO-GO. Every acceptance row reduced to a command.
- [ ] **Step 4 — review gate** (`/smh-code-review`) — appends `## Code Review` and the verdict.

## Evidence

**HEAD `854d350`.** Four commits on `chore/SCC-298-reconcile-actions`:

| sha | what |
|---|---|
| `f2093fa` | the verb, the four door passages, the rule clause, the SOP, both INDEX rows |
| `645837d` | the opencode mirrors the suite caught going stale |
| `ed52202` | the three cases the mutant table found missing, and the table |
| `854d350` | the deny-set the sweep proved was 35/37 unreachable |

### RED — and reading *which line raised*, which is the whole point

First run of the block against a `jira_feed.py` that had never heard of the verb:

```
[FAIL] A1 an open section EXITS 3 - the same HELD code `finish` uses: exit=2: usage: jira_feed.py [-h]
jira_feed.py: error: argument verb: invalid choice: 'reconcile-actions' (choose from 'outline', …)
…
[PASS] A3a a line that is already ticked is not an open row: exit=2: … invalid choice: 'reconcile-actions'
[PASS] A3a … - and NOTHING was written: the file changed on a refusal
-- 15/27 passed --
```

⛔ **Twelve of those fifteen passes were fiction.** Every refusal case asserted `code == 2` — and
**argparse exits 2 on an unknown verb.** Nothing ran, so nothing was written either. A case that is
green *before* the feature exists cannot fail when the feature breaks
(`red-test-can-die-before-its-assertion`). The same shape sank A1's two negative rows (*"the string
is absent"* is trivially true of empty output) and A2's *"the original text survives"* (the
**untouched** row also contains that text).

Tightened: every refusal must carry a `jira-feed: REFUSED` marker the verb owns, and every negative
row is bound to the exit code that proves the verb ran. **The honest red:**

```
-- 6/27 passed --
FAILED: A1 an open section EXITS 3 …, A1 …line number, A1 …SETTLED row is not listed, A1 …AGENT's
own checklist rows are invisible, A1 a section with nothing open EXITS 0, A2 the tick exits 0, A2
EXACTLY ONE line changed…, A2 the row is now ticked, A2 …original text survives, A2 …SOURCE is
recorded…, A2 …evidence itself is in the file, A3a…, A3b…, A3c…, A3d…, A3e…, A3f…, A3 (control)…,
A5 the only open row reconciles, A5 …`open_actions` is now CLEAR, A5 …so the list exits 0
```

### GREEN, per acceptance row

| Row | Assertion | Result |
|---|---|---|
| **A1** | open section exits 3, every open row named `L<n>`, settled rows and the agent's own `## Task Checklist` invisible; empty section exits 0 | **PASS** — and `A1c` pins the fail-closed direction: **no section at all is a refusal**, listing *and* ticking |
| **A2** | exactly one line changes, it is the one asked for, it is now `- [x]`, the source and the evidence are both in it | **PASS** — `len(before) == len(after) and diff == [L_C0 - 1]` |
| **A3** | five refusals, each exit 2 **with the `REFUSED` marker** and `read_bytes()` unchanged | **PASS** — plus `A3g` (floor alone), `A3h` (companion flags), `A3i` (the deny-set polices itself), and the **control** that a real operator row with real words is ACCEPTED |
| **A4** | the `<!-- reconcile-law -->` block extracted from all four doors is non-empty, >200 chars, and byte-equal | **PASS** — `CS-17`, 2/9 → **9/9**; all four blocks measure **1743** chars |
| **A5** | tick the only open row → `open_actions()` returns `[]`, so `finish` would close | **PASS** |
| **A6** | rule carries the law; all four doors cite it | **PASS** — `CS-17 F` × 4 |
| **A7** | every mutant killed by a NAMED case | **PASS** — **16/16** |

### The gates, at `854d350`

| Gate | Result |
|---|---|
| `run_all.py` **through the receipt writer** | **PASS exit 0, 92.3 s @ `854d3501`**, `dirty_tree: false` — receipt at `gates/suite.json` |
| `test_jira_feed.py` | **456/456** |
| `test_command_surfaces.py` | **208/208** (was 207/208 — the stale-mirror catch) |
| `mutation_sweep.py --table sweep.json` | **16/16 killed**; *"restore verified: bytes match, nothing was committed"*; both closing unfiltered full-file runs exit 0 |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info (pre-existing BOM notes) |
| maps ratchet on every commit | passed from a **worktree**, with **no `[maps-ok]`** — SCC-288's R9 fix holding |

### The two defects this lane found in its own work

**1. The RED lied, and the count was what hid it.** 15/27 looked like a healthy red. Twelve of the
passes were argparse's exit code being mistaken for the verb's. Reading *which line raised* — the
instruction the command gives and the one that is easiest to skip — is what surfaced it.

**2. `_GENERIC_EVIDENCE` was 35/37 unreachable, and only a mutant could see it.** M2 gutted the set
to `()` and the suite stayed green, because the length/word floor beneath it already refuses
anything under 16 characters or 3 words — so `done`, `ok`, `verified`, `n/a` never reached the set
at all. The case meant to cover it (`A3d`, ticking with `"done"`) was **exercising the floor**. Two
guards, one tested, and the untested one was almost entirely dead code wearing a guard's clothes.

Fixed in three places rather than by re-aiming the test alone: the set is now **19 long contentless
phrases**, every one ≥16 chars and ≥3 words — the one shape a floor structurally cannot see; `A3i`
asserts that property so the set **polices itself**; `A3d` was re-aimed at `"confirmed by operator"`
(21 chars, 3 words), which only the set can refuse. ⛔ Kept **exact-match** deliberately: a fuzzy
content test would refuse real operator quotes, and **a false refusal HOLDS a ticket** — the exact
failure this feature exists to end.

### Two decisions taken beyond the ticket, recorded so they are decisions

- **The verb refuses the MERGE row** (SCC-175). Not in the ticket's plan. Without it, this verb
  hands back the affordance SCC-175 spent a lane removing: `finish` computes that row from the
  repo, and a hand tick is the self-certification that fix closed. One `if`.
- **`/smh-sync-agents` ran with `-NoGlobals`.** The unswitched sync also publishes to the machine
  caches, and this lane has not landed — publishing an unmerged branch would put a door on the
  operator's menu that no `main` contains.

### Honest about the three cases written green

`A3g`, `A1c` and `A3h` were written **green, not red**: designing the mutant table asked whether
anything could see three behaviours, and nothing could, but the behaviour was already implemented
when the question was asked. A characterization check written green is honest; a green check
presented as a red is not. The sweep (M3, M11, M13) is what proves they bite.

## Your Actions

- [ ] **The merge itself** — lands via this branch's PR against `main`.
- [ ] **Decide when your opencode and Antigravity menus should pick up the changed doors.** This
      lane synced only the in-repo mirrors (`-NoGlobals`), deliberately, because it had not landed.
      The machine-global caches still carry the pre-SCC-298 text, and opencode needs a restart to
      rebuild its catalog either way.
