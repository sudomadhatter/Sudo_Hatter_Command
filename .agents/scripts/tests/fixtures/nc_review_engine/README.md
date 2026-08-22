# `nc_review_engine` — the review engine's negative control (SCC-129)

A seeded bad diff, a clean control diff, and the committed base they both apply to. Together they
answer one question about `.agents/skills/code-review-engine/`: **does the engine still catch what
it is supposed to catch, and still stay quiet on code that is fine?**

`_negative_control: true` with `NC_`-prefixed ids is this system's existing convention for
negative controls (the eval harness), followed here rather than reinvented.

## Two halves. Both are real, and neither substitutes for the other

| | Proves | Runs |
|---|---|---|
| **Mechanical** — `.agents/scripts/tests/test_review_fixture.py` | the control is still **armed** — nobody has quietly neutered it | every `run_all.py`, forever |
| **Live** — this document | the engine actually **rejects** `bad.diff` and **passes** `clean.diff` | by hand at a review gate; evidence pasted into that lane's walkthrough |

The split is forced, not a compromise. The engine is five markdown files executed by an LLM, and
the enforcement suite is stdlib-only and deterministic — so no test in `run_all.py` can assert an
engine verdict. What a test *can* do is guarantee the fixture is intact, which is what stops this
control from dying the way controls actually die: silently, in an unrelated edit, months later.

## The five seeded defects — one per lens

One each, deliberately, so a live run also proves **each lens is alive**. A lens that quietly
stopped working is invisible otherwise; "some findings came back" would not tell you.

| id | Lens | Seeded defect | Catchable by |
|---|---|---|---|
| `NC_BLIND` | Blind Hunter | `invoice_total` subtracts the tax its own docstring says is included | the diff text alone |
| `NC_EDGE` | Edge Case Hunter | `unit_price` divides by an unguarded `quantity` | the diff + repo |
| `NC_LITERAL` | Literal-Correctness | `helpers.parse(raw, strict=True)` — that argument does not exist | **only** by opening `codebase/helpers.py`, which `bad.diff` does not touch |
| `NC_ACCEPT` | Acceptance Auditor | `record_payment` clamps a negative amount | **only** against `spec.md` §2 |
| `NC_TESTADQ` | Test-Adequacy | three new deterministic functions plus a rewritten `invoice_total`, no test at any tier | the diff's file list vs `spec.md` §4 |

`manifest.json` is the authority for all of it — marker strings, expected severities, and why each
defect belongs to its lens.

## Running the live control

The engine never resolves its own inputs (`SKILL.md` § *The caller contract*), so **you are the
caller**. Invoke the `code-review-engine` skill twice — once per diff:

| Input | Bad-diff run | Clean-control run |
|---|---|---|
| `REPO` | repo root | repo root |
| `WORKTREE` | repo root (the fixture is committed, not a lane) | same |
| `DIFF` | `.agents/scripts/tests/fixtures/nc_review_engine/bad.diff` | `…/clean.diff` |
| `HEAD_SHA` | `git rev-parse HEAD` | same |
| `review_mode` | `full` | `full` |
| `STORY_FILE` | `…/spec.md` (line items + payments) | `…/spec-refunds.md` (refunds) |
| `lens_budget` | `standard` | `standard` |

⛔ **ONE SPEC PER CHANGE, and the two are not interchangeable.** Each diff is audited against the
spec for *that* change. Hand a reviewer the spec for the other one and it will correctly report
every unimplemented section as an acceptance gap — a finding about the pairing, not about the
code. The first live run proved it: with a single combined spec, `clean.diff` drew three
"missing implementation" findings and would have failed the clean control while the engine was
working perfectly.

⛔ **Tell every repo-access role not to open the answer key — the step-2 verifier included.**
`manifest.json`, this README, and both `.diff` files name the seeded defects outright *and state
the pass criterion*, and every role with repo access can read them. A lens that does is reciting,
not reviewing, and the control silently becomes a readback that passes no matter what the engine
does.

⚠ **This bit us on the first live run, in the place it matters most.** The step-2 Evidence
Verifier is the role whose revised severities *decide the clean arm's outcome* — and it read this
README, then said so unprompted: *"you should weigh that claim knowing I had the README in
context."* It had established both severities on the merits first, and its reasoning was checked
independently and held. But a verifier that knows the answer it is supposed to reach is not
independent, and the disclosure is the only reason anyone could tell. **The prohibition below
binds step-2 roles exactly as hard as step-1 lenses.** Append to those prompts:

> Do not open `manifest.json`, `README.md`, `bad.diff` or `clean.diff` under
> `.agents/scripts/tests/fixtures/nc_review_engine/`. Your subject is the diff you were handed and
> the definitions the changed lines depend on.

(On the first live run one lens declined the answer key unprompted and said why. That was its own
judgment, not a property of the fixture — which is exactly why it is written down here instead of
being left to recur by luck.)

**Pass criteria — both halves, always:**

- **`bad.diff`** — every defect in `manifest.json` is reported, and `severity_floor` comes back
  **`FAIL`** (step-03 §5: a surviving `critical` in `patch` or `decision_needed`).
- **`clean.diff`** — **no `critical` and no `important`** survives, and `severity_floor` is
  **`none`**.

⛔ **Run both.** A reviewer that flags everything is as broken as one that flags nothing, and the
bad-diff half alone cannot tell you which one you have.

**A miss is a result, not something to hide.** Record which lens missed which defect. The same
defect missed on two consecutive runs means it is not loud enough — redesign it, re-prove
intactness, re-run. That is the control doing its job on the engine, which is the whole point.

**Append one line per run to `live_runs.jsonl`** — date, sha, ticket, which diff, the returned
floor, and a verdict for each of the five defects. Full evidence still belongs in the running
lane's walkthrough; this file is the index into them, and it is what makes "two consecutive
runs" computable instead of a rule nobody can apply. The mechanical guard checks each entry is
COMPLETE — it deliberately does **not** require every defect to be a hit, because a check that
went red on a recorded miss would pressure the next person to leave the miss out, and a log of
successes only is not a log. It also makes the quiet failure visible: a control nobody has run
in eight lanes looks identical to a healthy one until you can see the last date.

## Changing the fixture

⛔ **The manifest and the diffs are ONE artifact.** Change a seeded defect and you change
`manifest.json` in the same commit; the mechanical guard fails otherwise, by design, and its
failure text says exactly that.

⛔ **Do not "fix" `codebase/helpers.py` to accept the argument `bad.diff` passes it.** That call
failing to bind *is* `NC_LITERAL`. Adding a `strict` parameter would disarm the defect while every
mechanical check stayed green — the marker would still be in the diff, and the call would simply
start working. The file says so at the top, for whoever arrives with a linter.

Neither diff is ever applied — the guard only runs `git apply --check`, which is the rot detector:
a diff that stopped applying is a control that quietly died.
