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
- [ ] [Review][Fix] <title> [<file>:<line>] src=<lens> · repro <id>
```

**`repro <id>` is the finding's reproduction id**, and it is what the caller's `repro_receipt.py`
run is keyed on. A `Fix` box without one is a box whose finding never passed
step 3's gate and should not have been written.

**`src=` is the finding's originating lens (SCC-233)** — the column the SCC-124 trial recorded by
hand and the shipped engine then dropped. One lens by its short name (`edge`, `acceptance`, `test-adequacy`);
a finding two lenses reached independently joins them as `src=edge+test-adequacy` (dedupe happened
in step 3 on the shared anchor, so a joined src is measured corroboration, not a guess).

Every `fix` box above is the caller's to close **in this lane, before its verdict** — the record is
the worklist for the fixes that happen now, not a list of things somebody else will do.

**There is no `Escalate` box and no `Defer` box (SCC-447, operator ruling 2026-09-11).** Every
reproduced finding is a `Fix` box. What the caller cannot apply alone becomes `held` in the caller's
own record with its patch, and what is outside this lane's files becomes `out-of-lane` there — both
are the CALLER's dispositions, written at fix time, and this engine never writes either
(`code-standards.md` §6.5 owns them). Nothing is deferred anywhere: a ledger of reproduced defects
nobody is fixing is the queue this ticket closed, and a finding handed to the operator with a
recommendation is the review he asked to be designed out of.

Dropped findings are **not** written here — builders must never see dead boxes. They are counted
only, in the summary below. **But a finding that dies keeps its lens (SCC-233):** the per-lens
disposition counts below include the dropped ones, so which lens's findings fail to reproduce is
computable from the record. That is the calibration signal, and it is how a lens earns its place or
loses it by measurement rather than by argument.

## 2. What the engine hands back

```
review-runtime:  fan-out | inline
lens_isolation:  worktree | mixed — <lens>: <mode>, … | shared — <why, when the runtime could not isolate>
lenses_run:
- <lens> · ok | recovered-inline | dead — <why, when it is not `ok`>
- <one row per lens that was applicable — the ROSTER, not a summary of it>
lenses_counted:  <n>/<applicable>
lenses_na:       <lenses not applicable in this mode, or "none">
findings:        <f> fix   (<d> dropped — no reproduction · <r> recorded)
dispositions:    per-lens: <lens>=<reproduced>/<dropped>/<recorded> · … (a multi-lens finding counts once per contributing lens)
severity_floor:  none | CONCERNS | FAIL
notes:           <degradations, absent optional inputs, verify wave: retired (SCC-447)>
```

⛔ **Return these as PLAIN LINES — the fence above is illustration and must NOT be copied
(SCC-240).** The caller pastes your return verbatim into the walkthrough, and
`walkthrough_roster.py` strips code fences before it reads anything (SCC-154), so a roster
handed back inside a fence is a roster the close-out gate cannot see — and until this was
written, the refusal it produced said only that the roster was absent.

⛔ This block and SKILL.md's "What the engine returns" are the SAME contract — `lenses_run:` is a
BLOCK of per-lens rows (SCC-173), never the retired counted line, because the caller pastes it
verbatim into the walkthrough where `walkthrough_roster.py` reads it. Until this review wave the
two blocks disagreed: this one still showed `lenses_run: <n>/<applicable>`, the exact shape the
parser deliberately reads as NO roster.

⛔ **`severity_floor` is PROVISIONAL.** The caller resolves it at the stamp against the rows still
open then — see step 3 §5 and `code-standards.md` §7. Handing it back as though it were final is
what gave the old loop no way down.

Then stop. The caller composes its verdict line from this summary plus its own gates.

## 3. The boundary — what this engine never touches

The engine has no authority over anything outside the record above, and this is a hard edge, not a
default:

- **It never runs a command.** `SKILL.md` grants no Bash, deliberately. The lens ran its own
  reproduction in its own copy and the caller re-runs it on the real tree; this engine only ever
  checks that the claim is present.
- **It never advances a story's state and never writes a board file.** Only a human close-out
  moves work to done; a reviewer that promotes its own subject is not a reviewer.
- **It never issues the verdict line.** It supplies a provisional floor; the caller owns the verdict.
- **It never applies fixes on its own initiative.** The caller applies every `fix` in the same
  lane before its verdict — that obligation is the caller's contract (fix in thread), and the
  engine's job ends at handing the worklist back.
- **It never merges, pushes, or transitions a ticket.** Those are the operator's sign-off, reached
  through the close-out command and nowhere else.
- **It never pauses the caller's flow.** Findings are handed back written down; the engine does not
  wait on anything, and nothing it returns is a question for the operator.

An engine that quietly does any of these is indistinguishable from one that was asked to.
