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
- [ ] [Review][Escalate] <title> [<file>:<line>] src=<lens> · repro <id> · recommend: <one line>
- [ ] [Review][Defer] <title> [<file>:<line>] src=<lens> · repro <id> — <why it is worth fixing> · blocked by <other live lane <branch> | other repo <name> | operator ruling>
```

**`repro <id>` is the finding's reproduction id**, and it is what the caller's `repro_receipt.py`
run is keyed on. A `Fix`, `Escalate` or `Defer` box without one is a box whose finding never passed
step 3's gate and should not have been written.

**`src=` is the finding's originating lens (SCC-233)** — the column the SCC-124 trial recorded by
hand and the shipped engine then dropped. One lens by its short name (`edge`, `acceptance`, `test-adequacy`);
a finding two lenses reached independently joins them as `src=edge+test-adequacy` (dedupe happened
in step 3 on the shared anchor, so a joined src is measured corroboration, not a guess).

Every `fix` box above is the caller's to close **in this lane, before its verdict** — the record is
the worklist for the fixes that happen now, not a list of things somebody else will do.

Every `escalate` box is carried to the OPERATOR, in the same thread, with its receipt and its
one-line recommendation. **The caller does not fix it and does not open a ticket for it.** Its
default is that the lane ships as recorded; the operator's word is what changes that. This is the
bucket that keeps a real-but-not-urgent finding from becoming a new unreviewed edit at the end of a
lane, which is the loop SCC-447 closed.

Every `defer` also gets a bullet in `DEFERRED_WORK`, under a heading naming this review and its
date; when the caller supplied no such path, the same bullets come back in the summary instead.
Deferred work that lives only inside one review's record is deferred to nowhere. **And a `defer`
bullet is a JUDGED item, never a bare title** — it carries why it matters and the ONE structural
blocker step 3 allows (another live lane owns the file · another repo · an operator ruling), because
it reproduced and the only reason it is not fixed here is that it cannot be. The ledger is not a
ticket queue and not a proposal source (operator rulings 2026-08-15): nothing in it is owed, no
close-out mints a ticket from it as a pile, and no review proposes one from it either — an entry is
picked up by the lane its blocker names, or deleted when its reason dies.

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
findings:        <f> fix · <e> escalate · <w> defer   (<d> dropped — no reproduction · <r> recorded)
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
- **It never pauses the caller's flow.** An `escalate` finding is handed back written down, for the
  caller to put in front of the operator; the engine does not wait on the answer.

An engine that quietly does any of these is indistinguishable from one that was asked to.
