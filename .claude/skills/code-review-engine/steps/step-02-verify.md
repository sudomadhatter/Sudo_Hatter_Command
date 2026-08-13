# Step 2 — Verify

A hunter asserts. This step is where an assertion becomes evidence, or dies.

Two roles run here, **concurrently, in ONE wave**: an Evidence Verifier that checks every finding
against what the code actually does, and a Compound Synthesis role that asks what the findings mean
*together*. Wall-clock is the slower of the two, never their sum.

## Self-gating — this step costs nothing on a clean diff

Count the findings step 1 collected, and gate on that count before anything else happens:

| Findings from step 1 | Evidence Verifier | Compound Synthesis |
|---|---|---|
| 0 | **does not run** | **does not run** |
| 1 | runs | **does not run** |
| 2 or more | runs | runs |

- **0 findings → skip this entire step.** No extractor run, no role launched, no tokens spent and
  no wall-clock added, so a clean diff costs exactly what it cost before this wave existed.
- **Fewer than 2 findings → no compound pass.** Compound synthesis exists to find what emerges from
  findings *interacting*; with one finding there is nothing to interact with.

⛔ **A skipped wave is recorded, never silent.** Add `verify wave: skipped (0 findings)` — or
`compound: skipped (<2 findings)` — to the engine's returned `notes`. A review that verified nothing
and a review whose findings were all confirmed are different evidence, and a reader who
cannot tell them apart has been handed the wrong one.

## The evidence dossier — this part is code, not a lens

Both roles work from the same programmatically-extracted dossier: `evidence_extract.py` reads the
repository and prints facts, and nothing in it is anybody's judgment.

**The engine's tool grant excludes Bash on purpose, so the orchestrator never runs the extractor
itself.** Each role runs it as its own first action, in its own context:

```bash
python3 .agents/scripts/evidence_extract.py --repo "$REPO" --findings findings.json --diff diff.patch
```

`python` on the PC — this system runs on two machines and only one of them has `python3`.

Hand each role the step-1 findings as a JSON list, **in step-1 order**, one object per finding,
carrying the keys the extractor reads: `title` · `file_path` · `line_start` · `body` · `evidence`.
Hand it the diff as well, or every `diff_hunk` comes back empty.

⭐ **The join is BY INDEX, never by title.** The extractor returns exactly one package per input
finding, in input order — and titles are NOT unique, because a multi-lens fan-out over one diff
produces duplicate titles as the expected case. Reconcile every result to its finding by position.

**If the extractor cannot run, or dies: the verifier runs COLD** — repo access only, no dossier —
and the run carries the note `evidence extractor unavailable: verifier ran cold`.

⛔ **A cold verifier does NOT cap the verdict.** The extractor is code, not a lens: the failure
contract at the end of this file covers roles that die, and a dead script is not a dead role.
Gating a merge on it would be gating on a convenience.

## Evidence Verifier

Launch it with the dossier, the findings, and read access to `REPO`. Its prompt:

> You are not the original reviewer, and you are not the adversary. You are an independent
> investigator. Your job is to determine what the code ACTUALLY does at each finding location, and
> whether the reviewer's claim about the code's behavior is factually accurate.
>
> You have two sources of truth: the extracted code, pulled programmatically, which is what the
> code really says; and read access to the whole repository, for tracing what the extraction does
> not cover. Where the two disagree, open the file.
>
> Answer these four questions for EVERY finding you were given.
>
> 1. **Does the code actually behave as the reviewer claims?** Compare the claim against the
>    extracted code, line by line. A reviewer who reports "uses string comparison" about code that
>    calls `errors.Is()` has made a factual error, and saying so IS your job.
> 2. **Is the described scenario actually reachable?** Check the callers. Are there upstream
>    guards, validators or type constraints that stop the bad state ever arriving?
> 3. **What does the broader context reveal?** A finding can look valid in isolation and be
>    prevented by another module — or look minor and be amplified by how it is used elsewhere.
> 4. **Is the severity proportionate** to what you just established? Say so either way.
>
> Return one result per finding, **in the order you were given them**, each carrying exactly these
> fields:
>
> ```
> title:               the finding's title, copied exactly
> verified:            true | false
> actual_behavior:     what the code actually does at that location
> revised_severity:    critical | important | suggestion | nitpick
> revised_confidence:  0.0–1.0
> verification_notes:  what you checked, and what settled it
> ```
>
> `verified: false` is a full result, not a failure — say what the code does instead. And never
> drop a finding you could not settle: return it `verified: false` with notes saying what blocked
> you, so the next reader knows it was looked at.

## Compound Synthesis

Launch it with the same dossier and the same findings — **at the same time as the verifier, not
after it.** The two roles do not read each other, and triage reconciles them. Its prompt:

> You are given every finding from an independent review of one change, and the extracted code each
> one refers to. Whether any single finding is correct is not your question — another investigator
> is answering that one. Your question is what these findings mean TOGETHER.
>
> Investigate:
>
> - Does one finding create a precondition that enables another?
> - Do separately minor issues combine into an escalation path?
> - Does a safety mechanism exist in one place and sit disconnected in another?
> - Can fixing one of these issues worsen the behavior another one exposes?
> - Do repeated patterns across findings indicate a systemic control gap?
>
> **Emit NEW findings only. Never restate, re-rank or summarize the originals** — the reviewer
> already has those, and a compound finding that is two originals stapled together is noise.
>
> Every compound finding MUST carry `contributing_findings`: the exact titles of the findings it is
> built from. One whose parents cannot be named is not a synthesis, it is a fresh assertion, and it
> has not been through the gates a hunter's finding goes through.
>
> **Emit only at confidence 0.6 or above, and only with concrete evidence. An EMPTY LIST is a
> valid and expected answer** — most changes compound into nothing at all.

## What step 3 receives

1. **Every step-1 finding, carried forward** — annotated with its verifier result: `verified`,
   `actual_behavior`, `revised_severity`, `revised_confidence`, `verification_notes`. A finding no
   verifier saw — the wave was gate-skipped, or the role died — is marked `verification: none` and
   keeps its hunter-asserted severity.
2. **Every compound finding, appended as a new finding** with `source: compound`, its
   `contributing_findings` preserved into `detail`, and its own severity. Compound findings are not
   re-verified in this pass; they reach triage on their own evidence.

⛔ **This step drops NOTHING.** A refuted finding travels to triage annotated `verified: false`
with the verifier's reasoning behind it; triage owns the `dismiss` bucket and decides with that
evidence in hand. Deleting it here would erase the disagreement that makes the record worth reading,
and step 1's no-noise-filter law binds at this layer exactly as hard.

⛔ **Never mark a finding verified that no role verified.** A fabricated verification is worse than
none at all: it is indistinguishable in the record from the real thing, and the severity table in
step 3 will act on it.

## When a role fails

Inherited from step 1 unchanged, because a role is a subagent exactly as a lens is:

1. **Retry it once.**
2. **Still failing → run that role INLINE yourself, here, in this context.**
3. **Record the degradation** in the returned summary — name the role, the failure, the recovery.
4. **Only a role that is still dead after BOTH the retry and the inline rerun raises the floor** to
   CONCERNS.

A role the self-gate skipped is **not** a dead role and never raises the floor — the same
distinction step 1 draws between a lens skipped by mode and a lens that died.

## NEXT

Read fully and follow `./step-03-triage.md`.
