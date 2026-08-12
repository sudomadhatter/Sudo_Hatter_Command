# Step 1 — The lens fan-out

Launch every lens **in parallel, each in its own clean context.** They do not see this
conversation, they do not see each other, and none of them sees the builder's reasoning — that
independence is the entire value of the fan-out. Wall-clock is the slowest lens, not their sum.

## The lenses

| Lens | Gets | Runs when | How |
|---|---|---|---|
| **Blind Hunter** | `DIFF` only — no spec, no repo access, no context docs | always | the `bmad-review-adversarial-general` skill |
| **Edge Case Hunter** | `DIFF` + read access to `REPO` | always | the `bmad-review-edge-case-hunter` skill |
| **Acceptance Auditor** | `DIFF` + `STORY_FILE` + any context docs | `review_mode: full` only | prompt below |
| **Test-Adequacy Auditor** | `DIFF` + read access to `REPO` | always | prompt below |

**Acceptance Auditor prompt:**
> You are an Acceptance Auditor. Review this diff against the spec and context docs. Check for:
> violations of acceptance criteria, deviations from spec intent, missing implementation of
> specified behavior, contradictions between spec constraints and actual code. Output findings as a
> Markdown list. Each finding: one-line title, which acceptance item or constraint it violates, and
> evidence from the diff.

**Test-Adequacy Auditor prompt:**
> You are a Test-Adequacy Auditor. Review this diff for TEST coverage adequacy by tier — not for
> bugs. Check: (1) does new deterministic logic (routing, state, DB/telemetry writes, parsing) have
> fast mocked unit tests? (2) is any generative / LLM output validated with soft assertions — JSON
> schema, semantic similarity, or an LLM-as-judge rubric — rather than brittle exact string
> matches? (3) does new agent/prompt behavior have at least one judge-style behavioral test? Output
> findings as a Markdown list. Each finding: one-line title, the file/area, which test tier is
> missing or mis-applied, and a one-line suggested test.

**If `EVIDENCE_PACK` was supplied**, prime every lens with it — and tell each one, in its own
prompt, that **the pack is a starting point, not the search space**: live files in `REPO` are the
authority, and a lens that only reads the pack will find only what the pack anticipated.

**If subagents are unavailable in this runtime**, write one prompt file per lens into the caller's
artifact folder, tell the caller they must be run externally and pasted back, and return. Do not
simulate a lens by imagining its output.

## When a lens fails — a dead lens is a finding, never a silent skip

Applied to any lens that errors, times out, or comes back empty:

1. **Retry it once.** Transient tool and API failures are the common case.
2. **Still failing → run that lens INLINE yourself, here, in this context.** A lens is a prompt,
   not a privileged tool; losing the parallelism costs time, not coverage. Record it as
   `recovered-inline`.
3. **Record the degradation** in the returned summary — name the lens, the failure, the recovery.
   "4 lenses ran" and "3 ran plus 1 rerun inline" are different evidence and must read differently.
4. **A lens that never ran at all sets `severity_floor: CONCERNS`.** Not clean. An unexamined
   surface is an unknown, and an unknown is never a pass.

## Skipped-by-mode is not the same as dead — and the difference is load-bearing

The Acceptance Auditor **does not run** in `review_mode: no-spec`, because there is nothing for it
to audit against. That is the mode working correctly, not a lens dying.

- Record it as **`n/a (mode)`** — not as a failure, and not inside the `<n>/<total>` ran count.
- It **does not cap the verdict.** `n/a (mode)` never raises `severity_floor`; only a lens that
  died after both recovery attempts does that.

Conflating the two is how a correctly-configured spec-less review gets reported as degraded
forever, and how a real dead lens gets waved through as "just the mode".

## Collect

Gather the raw output of every lens that produced one, tagged with which lens said it. Do not
normalize, dedupe, or judge anything here — that is step 3's job, and doing it early loses the
independence the fan-out just paid for.

## NEXT

Read fully and follow `./step-02-verify.md`.
