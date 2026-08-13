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
| `source` | `blind` · `edge` · `acceptance` · `test-adequacy` · `compound`, or merged (`blind+edge`) |
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
  patched without knowing intent. Only possible when `review_mode: full`.
- **patch** — a real issue whose correct fix is unambiguous.
- **defer** — real, but pre-existing and not caused by this change.
- **dismiss** — noise, false positive, or already handled elsewhere.

In `review_mode: no-spec`, a finding that would be `decision_needed` becomes `patch` if the fix is
unambiguous, otherwise `defer`. There is no spec to resolve the ambiguity against, so parking it as
a decision nobody can take is worse than either.

**`dismiss` is counted, `defer` is recorded.** A dismissed finding leaves the record as a number in
the summary; a deferred one is written down in full by step 4. The count is never omitted — a
review that silently drops what it rejected is a summary of its own conclusion.

## 5. Score the severity floor — the one place severity becomes a verdict

This table is the single definition; every caller reads it rather than inventing its own:

| Surviving finding | Effect on `severity_floor` |
|---|---|
| `critical`, in `decision_needed` or `patch` | **FAIL** |
| `important`, in `decision_needed` or `patch` | **CONCERNS** |
| `suggestion` or `nitpick`, any bucket | **never gate** — recorded, never raising the floor |
| anything in `defer` | **never gate** — it is not this change's defect |
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
