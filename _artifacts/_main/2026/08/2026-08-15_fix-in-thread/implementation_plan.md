# SCC-160 follow-on — survivors are fixed in thread; a review never produces a ticket

**Branch:** `chore/SCC-160-fix-in-thread` · **Base:** `0b46c62` (main) · **Ticket:** SCC-160 (open, `Review Required`)

## The ruling (operator, 2026-08-15, verbatim — the second one, after the first landing merged)

> "160 was not a fix. we will give you the updates once 38 finishes. the notes will be done then.
> but no it did not fix the problem. we need the fixes made in thread not a ticket made every story
> thats an endless loop that never finishes." · "we are not saying true or false — just that its not
> the full fix." · "we can start on this in parallel. we know the problem lets fix it"

**Plan-gate ruling:** the literal `approved` was not typed; "we can start on this in parallel. we
know the problem lets fix it" is recorded VERBATIM as the go, the same override shape the first
SCC-160 lane recorded. Recorded on the ticket (SCC-160 comment, 2026-08-15) — the operator develops
from Jira, not from memory.

## The flaw, located

The first landing built the relevance gate (what is NOT worth doing dies in triage) and retired the
residue ticket — but its survivor path still read: *"fixed in this lane, or ledgered, or — rarely —
proposed to the operator as a decided chore ticket."* That third leg is a ticket the operator has to
rule on, every story: SCC-160's own walkthrough ended in a `Rule on Ticket A and Ticket B` action
row, which is what holds it on `Review Required` today. Same loop, new adjective.

## What changes

| # | File | Change | Proving assertion |
|---|---|---|---|
| 1 | `code-review-engine/steps/step-03-triage.md` | Survivor path = **fix in this lane, before the verdict**. `defer` narrows to a STRUCTURAL blocker only (file owned by another live lane / another repo needing its own key / waits on an open `decision_needed`); "pre-existing" alone is no longer a defer reason. New load-bearing sentence: ⛔ **A review never produces a ticket.** — no residue, no "proposed", no "decided", no ticket-ruling row. | `test_review_engine.py` self-falsifying pins: existing 3 kept; NEW pin "a review never produces a ticket" rejects the counter-example "proposed to the operator as one decided chore ticket"; NEW pin "defer names a structural blocker" rejects "pre-existing and not caused by this change" as the defer definition |
| 2 | `code-review-engine/steps/step-04-record.md` | `[Review][Defer]` bullet carries the blocker, not a "lane class it rides"; boundary paragraph: the caller applies every `patch` in the same lane before its verdict (the engine still never patches on its own initiative). Ledger sentence: not a ticket queue **and not a proposal source**. | pin table (existing `[Review][Patch]` open-box pin) + `run_all` |
| 3 | `code-review-engine/SKILL.md` | contract mirror: survivor disposition line | `run_all` (SKILL/step parity pins) |
| 4 | `smh-code-review.md` · `cicd-code-review.md` | Step 1 gains an explicit **"Fix in thread"** obligation: every `patch` applied in this lane now, `decision_needed` walked with the operator now, before Step 3's gates; findings-table disposition wording (`deferred — <blocker>`); Step 5 ⛔ widened: ANY ticket born from review findings — residue, proposed, decided — is the retired defect. AP twin: diff header re-stamped (law lives in the shared engine; check whether Step-1 fix-in-thread text must port). | `workflow_lint --toolkit-only` (ap_reconciled + door mirrors) |
| 5 | `.agents/rules/jira.md` §Who mints · `artifacts-always-first.md` disposition mirror · SOP ⓘ aside | Same recut, each surface's phrasing; SOP tells the operator what they should never see again: a ticket-ruling row born from a review. | `run_all` link/anchor + SOP currency hook |
| 6 | `_artifacts/_main/deferred-work.md` | Header recut (blocker-only ledger; not a proposal source); the three entries re-judged under the new bucket — each either fixed in this lane or dropped with its reason. | walkthrough table |
| 7 | `_artifacts/_main/2026-08-15_triage-owns-relevance/walkthrough.md` | The `Rule on Ticket A and Ticket B` row REPLACED under the new law: each of the 8 survivors is fixed in this lane or dropped with a one-line reason — no ticket, no ruling row. Verdict line untouched. | `jira_feed check` sees no open operator box → SCC-160 can reach Done at close-out |
| 8 | `_artifacts/_memory/review-findings-are-not-a-work-queue.md` + `MEMORY.md` | Pointer memory (edited pre-lane, carried in): the law lives on the ticket. | `test_memory_store.py` |

**Acceptance (checkable):**
- [ ] A1 — grep of `.agents/` for `proposed .* decided (chore )?ticket|decided ticket the triage proposes|residue ticket` returns only ban/history sentences, never a permitted path.
- [ ] A2 — `test_review_engine.py` carries the two NEW self-falsifying pins and each rejects its counter-example (run the framework's own falsification).
- [ ] A3 — `run_all.py` exit 0 · `workflow_lint --toolkit-only` exit 0 · `check_maps --depth3-only --strict` exit 0, all bare.
- [ ] A4 — the SCC-160 walkthrough has zero unchecked operator boxes born from review findings; `jira_feed check SCC-160` (or the equivalent readback) reports no hold.
- [ ] A5 — every one of the 8 Ticket A/B items + 3 ledger entries has a disposition in this lane's walkthrough: `fixed @ <sha>` or `dropped — <reason>`.

**Out of scope:** the SCC-38 run and its notes (the operator's live test; those notes may re-cut this
again — that is expected, not a defect of this lane).
