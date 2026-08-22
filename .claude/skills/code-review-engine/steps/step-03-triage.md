# Step 3 — Normalize, dedupe, bucket, score

Be precise. When uncertain between two categories, take the more conservative one.

## 1. Normalize into one shape

Every lens emits a different format — adversarial prose, edge-case JSON with `location` /
`trigger_condition` / `guard_snippet` / `potential_consequence`, auditor lists with an acceptance
reference. Best-effort parse anything that does not match its expected shape, and note the parsing
problem rather than dropping the finding.

Each finding becomes:

| field | meaning |
|---|---|
| `id` | sequential integer |
| `source` | `blind` · `edge` · `literal` · `acceptance` · `test-adequacy` · `compound`, or merged (`blind+edge`) |
| `title` | one line |
| `detail` | the full description, plus any evidence |
| `location` | `file:line` when available |
| `severity` | normalized per §2 |

## 2. Severity — normalize the aliases FIRST

Reviewer models emit whatever vocabulary they like, in whatever case. Fold every one of them into
the four house levels before anything downstream looks at severity:

| House level | Accepts |
|---|---|
| `critical` | critical, high, blocker |
| `important` | important, medium, major |
| `suggestion` | suggestion, minor, low — **and anything unrecognized** |
| `nitpick` | nitpick, info, trivia, trivial |

Case-insensitive. The unrecognized-falls-to-`suggestion` rule is deliberate: an unknown word must
never be *promoted* into something that gates a merge.

**A revised severity outranks the hunter's.** When step 2 has supplied a `revised_severity` for a
finding — evidence in hand — that value replaces the hunter's assertion outright. Hunters assert;
verification is what makes a severity load-bearing.

⚠ **A finding with no revised severity keeps the hunter's** — step 2's self-gate skipped the wave,
or its verifier died. The table in §5 is applied to that severity anyway, deliberately, because an
unverified finding is not a softer finding: this engine
gates exactly as hard as the path it replaces, no harder and no softer.

## 3. Deduplicate

Two findings describing the same issue merge into one: keep the most specific as the base (prefer
the one carrying a `location`), fold every unique detail and reference from the others into its
`detail`, and set `source` to the merged sources. Do not merge two findings that share a file but
describe different failures — that hides one of them.

## 4. Bucket — exactly one per finding

- **decision_needed** — an ambiguous choice needing human input; the code cannot be correctly
  patched without knowing intent. Walked with the operator in-thread by the caller (see the
  decision leg under `defer`); in `no-spec` mode it exists too — the operator is the spec.
- **patch** — a real issue whose correct fix is unambiguous — and worth making (the gate below).
  **The caller applies it in this lane, before its verdict.** Pre-existing is not an exemption: a
  survivor found in a file this lane touched is fixed where it was found.
- **defer** — real, worth fixing, **and this lane structurally cannot hold the fix** — one of
  exactly three blockers, named in the bullet: the file is owned by another LIVE lane (the fix
  lands there; name it), the fix lives in another repo (which needs its own ticket key — `jira.md`
  §The map: each repo declares its own key), or it waits on a `decision_needed` the operator has
  not taken. "Pre-existing and not caused by this change" is NOT a defer reason (operator ruling
  2026-08-15, second): that reading turned the ledger into a parking lot. No blocker → it is
  `patch`. **The decision leg, precisely:** the caller walks every `decision_needed` with the
  operator in-thread and it becomes a patch or a dismiss on their word; one the operator does not
  take in-thread (or a headless run, which has no operator) stays an open DECISION row in the
  walkthrough's `## Your Actions` — a decision is theirs and may hold the ticket; it is not a
  ticket — and the `defer` bullet points at that row as its blocker.
- **dismiss** — noise, false positive, already handled elsewhere — **or true but not worth
  implementing.** That last class is a judgment this step OWNS, and it is recorded in one line,
  never hidden.

In `review_mode: no-spec`, a finding that would be `decision_needed` becomes `patch` if the fix is
unambiguous; otherwise it is STILL `decision_needed` — there is no spec to resolve the ambiguity
against, but there is an operator, and the caller walks it with them in-thread like any other
(headless: an open decision row). What it never becomes is a `defer` with no blocker.

### The relevance gate — TRUE is not the same as WORTH DOING (operator ruling 2026-08-15)

Step 2 settles whether a finding is true. This gate settles whether it is worth implementing —
different questions, and conflating them is the flaw the ruling closed:

> "the agents who review this have the goals of finding things, this doesnt mean they are all
> actually relivant to impliment" — the operator, retiring the residue-ticket practice.

The hunters are pointed at finding; volume is their success metric. A triage that treats every
verified finding as owed work converts that metric into a work queue. So before a true finding
may enter `decision_needed`, `patch`, or `defer`, it must pass at least ONE of:

1. **A realistic path fires today** — from this defect to a wrong merge, false evidence, lost
   work, or a blocked real flow. Realistic means you can name the actor and the moment; a chain
   of hypotheticals ("if someone hand-edits X during Y while Z is down") fails this leg.
2. **It undermines evidence the house already cites as proof** — gate verdicts, receipts,
   mutation-kill attribution, suite totals. Evidence integrity is bought at full price.
3. **The operator asked for it** — an acceptance item, a standing ruling, a named request.

Fails all three → `dismiss`, one line: title + which leg it failed and why. Severity does not
bypass the gate — an `important` with no realistic path is still dead, and §5 reads only the
findings that survive here. Classes that default to dead: doc symmetry, coverage added for
symmetry rather than for a suspected hole, style preference, and pins on prose — the last is
vacuous by the house's own measurement (SCC-125).

⛔ **The residue class is RETIRED.** No pile of unfixed findings is ever "owed to a follow-on
ticket" — that phrase and its variants are banned from walkthroughs. **A finding that survives
this gate is fixed in this lane, in this thread, before the verdict — full stop.** The only
other place it may go is a `defer` bullet naming one of the three structural blockers above.

⛔ **A review never produces a ticket.** Not a residue ticket, not a "proposed" ticket, not a
"decided" ticket the operator is asked to rule on, not a ticket-ruling row in `## Your Actions`.
The first cut of this rule (SCC-160, 2026-08-15) allowed "rarely — proposed to the operator as a
decided chore ticket" and its own close-out ended in a `Rule on Ticket A and Ticket B` row; the
operator ruled that the same loop under a new name: "we need the fixes made in thread not a
ticket made every story thats an endless loop that never finishes." A ticket asserts a decision
already made (`jira.md` §Who mints tickets); a review is where the work gets done, not where the
next ticket gets born.

**`dismiss` is counted — and a relevance kill is counted AND named.** Pure noise (false
positive, misparse, duplicate of handled work) leaves the record as a number in the summary. A
relevance kill — true, but not worth implementing — leaves ONE line in the walkthrough findings
table: `dismissed — <failed leg + reason>`. A deferred finding is written down in full by
step 4, blocker named. The count is never omitted — a review that silently drops what it rejected is a summary
of its own conclusion.

## 5. Score the severity floor — the one place severity becomes a verdict

This table is the single definition; every caller reads it rather than inventing its own:

| Surviving finding | Effect on `severity_floor` |
|---|---|
| `critical`, in `decision_needed` or `patch` | **FAIL** |
| `important`, in `decision_needed` or `patch` | **CONCERNS** |
| `suggestion` or `nitpick`, any bucket | **never gate** — recorded, never raising the floor |
| anything in `defer` | **never gate** — this lane structurally cannot hold the fix (its blocker is named), and a gate cannot block a lane on work it cannot do |
| a lens still `dead` after retry AND inline rerun | **CONCERNS** |
| a step-2 role still `dead` after retry AND inline rerun | **CONCERNS** |

The floor is the **most severe** applicable row, on the axis `none` < `CONCERNS` < `FAIL`. A lens
recorded `recovered-inline` is not a dead lens and does not appear here at all, and neither does a
step-2 role that recovered inline — including one recorded `cold (no dossier)`, which is a lost head
start, not a lost surface. A role the step-2 self-gate never launched is likewise not dead.

⛔ **A `dismiss` never gates and a `defer` never gates** — but a `defer` is still written into the
record. Suppressing a finding from the record because it did not gate is how a review becomes a
summary of its own conclusion.

## 6. Nothing left

If zero findings survive: report a clean review. If zero survive **and** a lens is `dead`, report
the degradation instead — the review may simply not have looked where the problem is.

## NEXT

Read fully and follow `./step-04-record.md`.
