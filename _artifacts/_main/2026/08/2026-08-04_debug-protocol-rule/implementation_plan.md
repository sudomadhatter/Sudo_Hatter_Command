---
IsArtifact: true
ArtifactMetadata:
  title: Debug protocol rule (reproduce-before-you-fix)
  type: implementation_plan
  date: 2026-08-04
---

# Implementation Plan — Debug protocol rule (`reproduce-before-you-fix`)

**Status:** approved 2026-08-04.

**Goal:** one on-demand rule that gives the house a debug loop with gates, replacing five scattered
one-liners with a spine they can point at. Fill the reproduction gap (zero current coverage) and put a
stop condition on the guess-loop.

## Research — what the industry converges on

- **MIT 6.031** — reproduce reliably → locate the cause → fix and verify. Plus the **10-minute rule**:
  ten minutes of ad-hoc poking → stop, switch to the scientific method.
- **Verraes, *How to Fix a Bug: Tests, Hypotheses, Timeboxes*** — write the failing test and *commit it*;
  brainstorm hypotheses without debate; rank by probability ÷ time-to-disprove; **falsify**, don't
  confirm; timebox each.
- **Delta debugging** — minimize the reproduction; the minimal repro usually *is* the diagnosis.
- **Regression-test consensus** (TestRail, CircleCI, Black's contributing guide) — "run it first to
  confirm it fails, then fix, run again." A test never *seen* red proves nothing.
- **Google SRE postmortem culture** — blameless, and note the deliberate plural: *contributing causes*.

## The gap this fills

Fragments already exist in five places: `karpathy-guidelines.md:20`, `collaborative-debug-first.md`,
`sudo-quick-dev.md:40`, `sudo-mobile-error-team.md` §4, `sudo-live-testing-team.md:46`.

`reproduc*` across every rule and command returns **one hit** — a disk path in
`sudo-close-workingtree.md`, not a bug. Reproduction has zero coverage. Neither does hypothesis
discipline for the general case, nor a stop condition on the guess-loop, nor "prove the pinning test
actually catches this fix."

## Decisions

**D1 — New rule, `.agents/rules/reproduce-before-you-fix.md`.** House naming is descriptive-imperative
(`tests-must-gate-for-real`, `completion-not-illusion`, `artifacts-always-first`). The name states the gap.
Not an update to `collaborative-debug-first` (its trigger is specifically *you can't observe but Daniel
can* — one branch of one gate here), and not to `tests-must-gate-for-real` (fires at test-writing time
about test *validity*; this fires at bug-report time about *process*).

**D2 — Load class: on-demand, pulled by a floor pointer.** An on-demand rule only fires if something
reaches for it. `karpathy-guidelines.md:20` is floor and already says "investigate root cause before
proposing fixes" — a `[[reproduce-before-you-fix]]` pointer there makes the floor rule the dispatcher.

**D3 — It references, never restates.** Red-must-fail-for-the-right-reason → `tests-must-gate-for-real`
#1. Can't-observe → `collaborative-debug-first`. Escalation → quick-dev's EJECT tripwire. No duplicated
prose to drift.

**D4 — Numbers are house-set and labeled as such.** MIT's 10-minute rule is literature. "3 falsified
hypotheses" and "2 edits producing no new evidence" are an adaptation for an agent loop, marked tunable.

## The rule's five gates

| Gate | Requirement | Legitimate exit |
|---|---|---|
| **G1 REPRODUCE** | A *citable* repro: exact command, URL + click path, Sentry event id, or a failing test. "I read the code and can see the bug" is a hypothesis, not a repro. | Can't observe → `collaborative-debug-first`. Genuinely non-reproducible (heisenbug/prod-only/race) → **add observability, say so plainly, stop.** Never fix blind. |
| **G1.5 MINIMIZE** | Narrow to the smallest input/path that still fails. | — |
| **G2 PIN** | Write the test, **run it, paste the red.** Verify every asserted string/selector/endpoint against real source. Name it after the bug id. Commit the red. | Config/copy tweaks: say so explicitly. |
| **G3 FALSIFY** | List all hypotheses *before* testing any. Order by probability ÷ cost-to-disprove. Try to **disprove**. One change, one observation — never stack. | **Stop:** 10 min unsystematic, OR 3 falsified, OR 2 edits with no new evidence. |
| **G4 FIX** | Minimal change at the cause. No refactors, no drive-bys. Architectural cause → fix minimally, record as follow-up. | — |
| **G5 PROVE** | **Revert only the fix hunk → watch the test go red → restore.** Then run the whole surrounding module suite. Paste real output. Remove temp debug logs. | — |

G5 is the one nobody does. A pinning test written after the fix and never seen failing *against that
fix* may be passing coincidentally.

Plus **contributing causes, plural** (SRE) — record the *mechanism*, the *reach* (what else shares it —
go check), and **the miss** (why no existing test caught this; that gap is the real finding).

## Files touched

| File | Change |
|---|---|
| `.agents/rules/reproduce-before-you-fix.md` | **NEW** — frontmatter, When This Applies, 5 gates, contributing causes, escalation, anti-patterns, Why + sources |
| `.agents/rules/INDEX.md` | one row in The set |
| `.agents/rules/karpathy-guidelines.md:20` | append the `[[reproduce-before-you-fix]]` pointer (D2 — the dispatch) |
| `.agents/rules/collaborative-debug-first.md` | one line at top: this is G1's can't-observe branch |
| `.agents/commands/sudo-quick-dev.md` | add to "Rules in force"; line 40's "root cause first" points at it |
| `.agents/commands/sudo-mobile-error-team.md` | add to "Rules in force"; §4 points at it |

**Anti-patterns section** — only ones the house has paid for: fixing before reproducing · a test written
after the fix, never seen red · "I changed 3 things, try now" · **deleting the guard to prove a test
works** (kills both tests, isolates nothing — relocate/revert instead; AGY 21.8b) · symptom patch called
a fix · closing without asking why nothing caught it.

## Execution order

1. Write the rule (the only file with real content).
2. INDEX row → karpathy pointer → collaborative-debug-first pointer.
3. Two command headers.
4. `check_maps.py` — expect zero new drift.
5. Walkthrough + INDEX rows + active-context.

## Verification

`python .agents/scripts/check_maps.py` clean · frontmatter matches the INDEX row's trigger wording ·
every `[[link]]` resolves to a real file · rule ≤ ~7 KB (it is read in-session).

## Open questions (resolved at approval)

- **Q1 — command wiring scope.** Wired the two commands that *fix* bugs. `sudo-live-testing-team.md`
  only diagnoses; `sudo-dev-story-tests.md:103` is about suite failures, not reported bugs. Deferred.
- **Q2 — `living-template-sync.md`.** Propagation into `Fresh_Workspace_BMAD` is `/sync-agents`' job;
  a sync is already pending from the memory session. Out of scope here.
- **Q3 — the numbers.** 10 min / 3 hypotheses / 2 no-evidence edits, accepted as-is.

## Not in scope

No new command. No changes to `tests-must-gate-for-real` (rule 4 already carries relocate-don't-delete;
linked, not copied). No touching the pending memory-store or `adk-prompting` commits.
