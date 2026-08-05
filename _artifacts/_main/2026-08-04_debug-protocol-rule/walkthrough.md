---
IsArtifact: true
ArtifactMetadata:
  title: Debug protocol rule — reproduce-before-you-fix
  type: walkthrough
  date: 2026-08-04
---

# Walkthrough — `reproduce-before-you-fix` (the house debug loop)

- **Date:** 2026-08-04
- **Workspace:** home base (lobby)
- **Plan:** [`implementation_plan.md`](implementation_plan.md) — approved as written

---

## 1. What this was

Daniel asked for an enterprise-standard debugging rule and left the new-vs-update call open. Research
first, then the call.

**The industry spine** (four sources, in agreement): MIT 6.031 gives *reproduce → locate → fix and
verify* plus the **ten-minute rule**. Verraes gives the operational version — commit the failing test,
brainstorm hypotheses without debate, order by probability ÷ time-to-disprove, and **falsify rather than
confirm**. Delta debugging gives *minimize the repro* (the minimal case usually is the diagnosis).
TestRail / CircleCI / Black's contributing guide all state the same sentence: run it first to confirm it
fails, then fix, run again. Google SRE contributes blamelessness and the deliberate plural, *contributing
causes*.

**The measured gap.** Fragments already lived in five places — `karpathy-guidelines:20`,
`collaborative-debug-first`, `sudo-quick-dev:40`, `sudo-mobile-error-team` §4,
`sudo-live-testing-team:46`. But `grep -ri reproduc` across every rule and every command returned
**one hit**, in `sudo-close-workingtree.md`, about a disk path. Reproduction had **zero** coverage in the
agent system, and nothing anywhere put a stop condition on the guess-loop.

## 2. Why a new rule, not an edit

`collaborative-debug-first`'s trigger is specifically *you can't observe but Daniel can* — that is one
branch of one gate here, and widening it would destroy the trigger that makes it dispatchable.
`tests-must-gate-for-real` fires at test-writing time about test *validity*; this fires at bug-report
time about *process*. Merging either way yields a rule that loads wrongly in both directions.

The rule therefore **references and never restates**: red-must-fail-for-the-right-reason →
`tests-must-gate-for-real` #1; can't-observe → `collaborative-debug-first`; escalation → quick-dev's
EJECT tripwire. Nothing duplicated, so nothing to drift.

## 3. The five gates

| Gate | Requirement |
|---|---|
| **G1 REPRODUCE** | A **citable** repro someone else could run: exact command, URL + click path, Sentry event id, or a failing test. *"I read the code and can see the bug"* is a hypothesis. Two legitimate endings: can't-observe → `collaborative-debug-first`; genuinely non-reproducible → **add observability, say so, stop.** Never fix blind. |
| **G1.5 MINIMIZE** | Smallest input/path that still fails; one variable at a time. |
| **G2 PIN** | Test **before** the fix. Run it. **Paste the red.** Assertions verified against real source. Named after the bug id. **Commit the red.** |
| **G3 FALSIFY** | All hypotheses listed *before* testing any. Ordered by probability ÷ cost-to-disprove. Disprove, don't confirm. One change, one observation. |
| **G4 FIX** | Minimal, at the mechanism. Architectural cause → fix minimally, record as follow-up; never rewrite a design under a bug ticket. |
| **G5 PROVE** | **Revert only the fix hunk → watch the test go red → restore.** Then the whole surrounding module suite. |

**Stop conditions** (any one → stop editing, escalate): 10 min unsystematic · 3 hypotheses falsified with
no lead · 2 edits producing no new evidence. Labeled in-rule as house-set and tunable, so nobody mistakes
them for literature. Escalation hands over the repro, the minimized case, the red test, and **what is
ruled out** — framed as progress, because it is.

**G5 is the gate nobody does**, and it is the one that turns "the test passes" into "the test catches
this." A pinning test never seen failing *against this fix* may be passing coincidentally.

Plus **contributing causes, plural**: record the *mechanism*, the *reach* (what else shares it — then go
look), and **the miss** (why no existing test caught it). Karpathy's "why does the architecture allow
this?" becomes a written output.

## 4. Task Checklist

- [x] Researched 4 industry sources; measured the actual gap by grep rather than assuming one
- [x] `.agents/rules/reproduce-before-you-fix.md` — new rule, 5 gates + contributing causes + anti-patterns + sourced Why
- [x] `.agents/rules/INDEX.md` — new row, and `collaborative-debug-first`'s row now names it as the G1 branch
- [x] `.agents/rules/karpathy-guidelines.md:20` — floor pointer (this is the dispatch that makes an on-demand rule actually fire)
- [x] `.agents/rules/collaborative-debug-first.md` — "Where this sits" header block
- [x] `.agents/commands/sudo-quick-dev.md` — Rules-in-force entry + Step 2 now says the pinning test is seen red **before** the fix
- [x] `.agents/commands/sudo-mobile-error-team.md` — Rules-in-force entry + §4 now requires "fails on broken code" be **observed**
- [x] `check_maps.py` — zero new drift

## 5. Evidence

```
=== check_maps (lobby) ===
[maps]                       [ok] clean
[INDEX.md paths]             [ok] clean
[level-2 INDEX presence]     [ok] clean
[structure conformance]      [ok] clean
[depth-3 _artifacts INDEX]   [x] missing row for 2026-08-04_debug-protocol-rule/   <- this session; row added below

=== wiring spot-check (citations of the new rule per file) ===
  2  .agents/rules/INDEX.md
  1  .agents/rules/karpathy-guidelines.md
  1  .agents/rules/collaborative-debug-first.md
  2  .agents/commands/sudo-quick-dev.md
  2  .agents/commands/sudo-mobile-error-team.md

=== all 5 cited rule/command names resolve on disk ===
  ok collaborative-debug-first · tests-must-gate-for-real · karpathy-guidelines
  ok sudo-mobile-error-team · sudo-quick-dev

=== reproduc* coverage: 1 file before (a disk path) -> 7 files now ===
```

**One criterion missed, stated plainly.** The plan's verification line said the rule should be ≤ ~7 KB;
it is **8526 B**. I trimmed once (9077 → 8526) and stopped. That 7 KB was a number I invented, and
against the actual folder it sits mid-pack — `tests-must-gate-for-real` is 6.7 KB, `code-standards` 7.5
KB, `worktree-per-story` 10.6 KB, `artifacts-always-first` 21.3 KB. Cutting further would have cost the
sourced *Why*, which is what stops the rule being read as arbitrary. Flagging rather than quietly moving
the goalpost.

## 6. Your Actions

**Nothing committed.** Working tree, explicit paths:

```powershell
git add .agents/rules/reproduce-before-you-fix.md .agents/rules/INDEX.md .agents/rules/karpathy-guidelines.md .agents/rules/collaborative-debug-first.md .agents/commands/sudo-quick-dev.md .agents/commands/sudo-mobile-error-team.md _artifacts/_main/2026-08-04_debug-protocol-rule _artifacts/_main/INDEX.md _artifacts/INDEX.md _artifacts/_main/active-context.md
git commit -m "feat(rules): reproduce-before-you-fix - the house debug loop as five gates

Debug guidance existed as five one-liners across rules and commands, but a
grep for reproduc* over the whole .agents tree returned ONE hit, about a disk
path. Reproduction had zero coverage, and nothing put a stop condition on the
guess-loop. New on-demand rule dispatched from the karpathy floor rule:
reproduce (citable, or say it does not) -> minimize -> pin a test SEEN red ->
falsify one hypothesis at a time -> minimal fix at the cause -> prove it by
reverting the fix hunk. Sources: MIT 6.031, Verraes, delta debugging, Google SRE."
```

⚠️ This commit is **separate from** the pending memory-store commit — that one is still uncommitted too,
with its own command in [`../2026-08-04_portable-memory-store/walkthrough.md`](../2026-08-04_portable-memory-store/walkthrough.md#6-your-actions).
Land them in either order, but don't merge the messages.

**Then `/sync-agents`** — this touched two command files and the shared rule set, so lobby → projects
propagation is owed. `living-template-sync` also wants it reaching `Fresh_Workspace_BMAD`.

**Deferred by agreement (Q1):** `sudo-live-testing-team.md` only diagnoses and reports, and
`sudo-dev-story-tests.md:103` is about suite failures rather than reported bugs — neither wired. Say the
word if you want them.

⚠️ Still outstanding from earlier sessions: three project repos hold staged `adk-prompting` deletions
awaiting commit, and **B-L-WorldWide is on `main`** (owner-only).
