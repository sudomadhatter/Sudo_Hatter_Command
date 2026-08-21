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

**The count is the RAW step-1 count, before dedupe.** Two lenses reporting the same issue counts as
two, because dedupe belongs to step 3 and doing it here would undo the independence the fan-out just
paid for. The cost of the boundary case is a compound role that reads a finding beside its own
duplicate and correctly returns an empty list, which is the cheapest outcome this role has.

⛔ **A skipped wave is recorded, never silent.** Add `verify wave: skipped (0 findings)` — or
`compound: skipped (<2 findings)` — to the engine's returned `notes`. A review that verified nothing
and a review whose findings were all confirmed are different evidence, and a reader who
cannot tell them apart has been handed the wrong one.

⚠ **Zero findings has two causes and the note must say which.** A clean diff and a fan-out where
every lens died both arrive here as zero. When any lens is `dead`, write
`verify wave: skipped (0 findings — but <n> lens(es) dead)`; step 3 raises the floor for the dead
lens either way, and step 1 already says the review may simply not have looked where the problem
is. The bare note is for a review that genuinely found nothing.

## The evidence dossier — this part is code, not a lens

Both roles work from the same programmatically-extracted dossier: `evidence_extract.py` reads the
repository and prints facts, and nothing in it is anybody's judgment.

**The engine's tool grant excludes Bash on purpose, so the orchestrator never runs the extractor
itself.** You can WRITE the inputs and you cannot RUN anything, so the work splits in two:

- **You prepare the inputs.** ⭐ **Group first, then serialise — the grouping is YOURS and this
  is when it happens:** apply the claim-grouping rule below **AFTER the self-gate has read the raw
  count and BEFORE you
  serialise**. Then serialize the step-1 findings as a JSON list, **in step-1 order**,
  one object per finding, carrying the keys the extractor reads: `title` · `file_path` ·
  `line_start` · `body` · `evidence`. The JSON always carries
  **one object per finding — grouping never collapses it**; what grouping changes is the
  PROMPT, which names which indices share a single question. The diff is `DIFF`, as the caller
  resolved it.
- **Each role runs the extractor itself**, as its own first action, because a role is a subagent
  with its own shell. That instruction lives in the dossier block below and is appended to both
  prompts. It is not decoration: a role merely *told* a dossier exists, and never told to build
  one, reviews cold while the record says it did not.

⛔ **Substitute every placeholder before you send a prompt.** The block below carries
`<WORKTREE>`, `<FINDINGS_JSON>` and `<DIFF>`; replace each with the real absolute path or the real
content. A subagent inherits none of your shell variables, so a literal `$REPO` arrives undefined
and the extractor exits 2 — a plumbing failure that would then be recorded as a cold review.

⛔ **The extractor reads `WORKTREE`, never `REPO`, wherever the two differ.** The caller contract
keeps them apart precisely because a lane's diff comes from a worktree. Point the extractor at the
repository root instead and it reads `main`'s copy of every file at the lane's line numbers — so
the verifier would truthfully refute correct findings about code it was never shown.

⭐ **The join is BY INDEX, never by title.** The extractor returns exactly one package per input
finding, in input order — and titles are NOT unique, because a multi-lens fan-out over one diff
produces duplicate titles as the expected case. Reconcile every result to its finding by position.

⭐ **Verify each CLAIM once, not each duplicate (SCC-156) — fan the query in, fan the results back
out.** Where two or more findings name the **same `file:line`** *and* assert the **same behavior**,
ask about it **once**: the code's behavior at one location does not change per duplicate, and a
findings-heavy lane otherwise pays a full verification round trip for the same question three times.
⛔ **This is the rule the dossier bullet above sends you to, not a second one — the orchestrator
does the grouping, at the point that bullet names, and the roles receive groups and never form
them.** Read as an instruction to the verifier, it becomes "send everything and let the role sort
it out", which is how SCC-210 sent 46 findings where there were 29 unique claims.

This is a **query** economy, and it changes nothing else about the step:

- **The raw count still governs the self-gate above.** Group AFTER the table has read the count. Two
  lenses reporting one issue still counts as two, because that is what the fan-out paid for.
- **The 1:1 result contract is unchanged.** A group of N findings sends one query and expands its
  verdict back to **N indexed results**, in input order, exactly as if each had been asked
  separately. Downstream reads no differently, and the by-index join above still holds.
- **Dedupe still belongs to step 3.** Grouping here decides who shares a question; it never merges,
  drops, or rewrites a finding, and step 3's merge rule runs on the full set as before.
- ⛔ **Same location is not enough.** Two findings on one line describing *different* failures are
  different claims and get their own queries — grouping them would hide one behind the other's
  verdict, which is exactly what step 3 is forbidden from doing at merge time.

### The dossier block — appended to BOTH role prompts

> **Before you review anything, build your evidence dossier.** Write the findings JSON below to
> `findings.json`, and the diff below to `diff.patch`, in a scratch directory you own. Then run:
>
> ```bash
> python3 <WORKTREE>/.agents/scripts/evidence_extract.py --repo <WORKTREE> --findings findings.json --diff diff.patch
> ```
>
> On Windows that interpreter is `python`, not `python3` — this system runs on two machines and
> only one of them has `python3`. The result is a JSON list holding exactly one package per
> finding, in the order you sent them, so **join it to the findings by INDEX, never by title.**
>
> **If that command fails for any reason, carry on COLD:** work from the repository alone and say
> in your output that you had no dossier. Do not stop, do not retry it more than once, and never
> report the extractor's failure as if it were a finding about the code.
>
> FINDINGS JSON:
> `<FINDINGS_JSON>`
>
> DIFF:
> `<DIFF>`

**If the extractor fails, that role runs COLD** — repo access only, no dossier — and the engine's
notes carry `evidence extractor unavailable: <role> ran cold`. This applies to **both** roles, and
naming the role in the note is what keeps one cold role distinguishable from two.

⛔ **A cold role does NOT cap the verdict.** The extractor is code, not a lens: the failure
contract at the end of this file covers roles that die, and a dead script is not a dead role.
Gating a merge on it would be gating on a convenience.

## Evidence Verifier

Assemble as: **the prompt below, then the dossier block**, and launch it with read access to
`WORKTREE`. Both parts, every time — the prompt without the block is a role that believes it has
evidence it was never given.

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

Assemble the same way — **the prompt below, then the dossier block** — and launch it **at the same
time as the verifier, not after it.** The two roles do not read each other, and triage reconciles
them.

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

⚠ **A compound finding can FAIL a merge on less evidence than any other finding, and that is a
decision, not an oversight.** It passed neither step 1's three hunter gates nor this step's
verifier, so its `critical` rests on one unverified role — while step 3 says plainly that
verification is what makes a severity load-bearing. It is left able to gate anyway, for the reason
the no-noise-filter law gives: this reviewer applies the fixes it finds, so a compound finding
raised wrongly costs one triage decision, and a real escalation path missed because the only role
looking for it was pre-emptively discounted ships. The named parents are what make it cheap to
check. **Revisit this the moment a compound re-verify pass exists** — that pass, deferred from this
epic, is exactly what would earn the severity rather than assume it.

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

⚠ **A role you rerun inline is COLD by construction, and must be recorded that way.** Step 2 runs
inline in *your* context, and you have no Bash — so no dossier can be built for it, ever. Record
`<role> rerun inline: cold (no dossier)`. It is still `recovered-inline` and still does not raise
the floor: what was lost is the head start, not the coverage, and you have the same repo access the
dossier was summarizing. Recording it as an ordinary recovery would claim evidence that could not
have existed.

## NEXT

Read fully and follow `./step-03-triage.md`.
