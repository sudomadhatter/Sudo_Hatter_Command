# Step 4 — Record, and hand back

Write what was found. Then return. This step's entire scope is the record and the summary.

## 1. Where the findings go

Write to `FINDINGS_SINK` if the caller supplied one. If it did not, **return the findings block in
the summary and say it was not written** — do not pick a file. If `STORY_FILE` is set and carries a
tasks/subtasks section, append a `### Review Findings` subsection there as well; the builder reads
the story, and a finding they never see is a finding nobody fixes.

Order matters — unresolved work first, settled work last, and **nothing that is still open is
written as a completed box**:

```
- [ ] [Review][Decision] <title> — <detail> src=<lens>
- [ ] [Review][Patch] <title> [<file>:<line>] src=<lens>
- [ ] [Review][Defer] <title> [<file>:<line>] src=<lens> — <why it is worth fixing> · blocked by <other live lane <branch> | other repo <name> | open decision <title>>
```

**`src=` is the finding's originating lens (SCC-233)** — the column the SCC-124 trial recorded by
hand and the shipped engine then dropped. One lens by its short name (`blind`, `edge`, `literal`,
`acceptance`, `test-adequacy`); a finding two lenses reached independently joins them as
`src=blind+edge` (dedupe happened in step 3 on the shared anchor, so a joined src is measured
corroboration, not a guess).

Every `patch` box above is the caller's to close **in this lane, before its verdict** — the
record is the worklist for the fixes that happen now, not a list of things somebody else will
do. Every `defer` also gets a bullet in `DEFERRED_WORK`, under a heading naming this review and
its date; when the caller supplied no such path, the same bullets come back in the summary
instead. Deferred work that lives only inside one review's record is deferred to nowhere. **And a
`defer` bullet is a JUDGED item, never a bare title** — it carries why it matters and the ONE
structural blocker step 3 allows (another live lane owns the file · another repo · an open
decision), because it already passed the relevance gate and the only reason it is not fixed
here is that it cannot be. The ledger is not a ticket queue and not a proposal source (operator
rulings 2026-08-15): nothing in it is owed, no close-out mints a ticket from it as a pile, and
no review proposes one from it either — an entry is picked up by the lane its blocker names,
or deleted when its reason dies.

Dismissed findings are **not** written here — builders must never see dead boxes. Noise kills are
counted only, in the summary below; a relevance kill (true but not worth implementing) gets its
ONE line in the walkthrough findings table per step 3, and nowhere else. **But a finding that dies
keeps its lens (SCC-233):** the per-lens disposition counts below include dismissed and
relevance-killed attribution, so which lens's findings die at triage is computable from the record
— the enabler for the open Blind Hunter question (its SCC-129 clean-arm case rests on n=1, and
cutting a lens on n=1 is the unanchored move the parent ruling bans). After N runs the question is
answerable from data; N is not fixed here — fixing it would be a hard-coded cap.

## 2. What the engine hands back

```
lenses_run:      <n>/<applicable>   (per-lens: ok | recovered-inline | dead)
lenses_na:       <lenses not applicable in this mode, or "none">
findings:        <d> decision · <p> patch · <w> defer   (<n> noise-dismissed · <k> relevance kills)
dispositions:    per-lens: <lens>=<survived>/<dismissed>/<relevance-killed> · … (a multi-lens finding counts once per contributing lens)
severity_floor:  none | CONCERNS | FAIL
notes:           <degradations, absent optional inputs, verification state>
```

Then stop. The caller composes its verdict line from this summary plus its own gates.

## 3. The boundary — what this engine never touches

The engine has no authority over anything outside the record above, and this is a hard edge, not a
default:

- **It never advances a story's state and never writes a board file.** Only a human close-out
  moves work to done; a reviewer that promotes its own subject is not a reviewer.
- **It never issues the verdict line.** It supplies a floor; the caller owns the verdict.
- **It never applies fixes on its own initiative.** The caller applies every `patch` in the same
  lane before its verdict — that obligation is the caller's contract (fix in thread), and the
  engine's job ends at handing the worklist back.
- **It never merges, pushes, or transitions a ticket.** Those are the operator's sign-off, reached
  through the close-out command and nowhere else.
- **It never pauses the caller's flow for a decision.** `decision_needed` findings are handed back
  written down, for the caller to walk with the operator.

An engine that quietly does any of these is indistinguishable from one that was asked to.
