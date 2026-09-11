---
name: code-review-engine
description: The house review engine — three adversarial lenses over a resolved diff, and the fan-out reproduces what they find before reporting it; triages the survivors into two buckets — fix or drop — records them, and returns a PROVISIONAL severity floor its caller resolves at the stamp. Invoked BY /cicd-code-review, /smh-code-review and /cicd-quick-dev; it is not a standalone command and never resolves its own inputs.
allowed-tools: Read, Write, Glob, Grep, Task
---

# Code Review Engine

**Goal:** take a diff the caller has already resolved, hunt it with three parallel lenses that each
reproduce what they report, triage what survives, record it — and hand back a provisional severity
floor. Nothing else.

**Your role:** you are the engine, not the reviewer command. The caller owns the story, the board,
the gate and the verdict line. You own findings and their severity.

## ⛔ FIRST — was this invoked with a caller contract?

Every platform that publishes skills makes this one visible as a menu entry, so a human can reach it
directly. **If `REPO`, `WORKTREE`, `DIFF`, `HEAD_SHA` and `review_mode` were not supplied by a
calling command, you were invoked from a menu.** Print the contract table below, say this engine
runs only as a step of `/cicd-code-review`, `/smh-code-review` or `/cicd-quick-dev`, and
**return without reading the step files.** Do not resolve the inputs yourself and do not proceed.

## The caller contract — these arrive resolved, and the engine never resolves them itself

| Input | What it is | Required |
|---|---|---|
| `REPO` | absolute path to the repository root | yes |
| `WORKTREE` | absolute path to the tree the diff came from (may equal `REPO`) | yes |
| `DIFF` | the diff text, or a path to it — already scoped by the caller | yes |
| `HEAD_SHA` | the sha the diff was taken at, for the record the caller writes | yes |
| `review_mode` | `full` (a spec exists) or `no-spec` (none) | yes |
| `review_runtime` | `fan-out` or `inline` — whether subagents are available, **probed by the caller, never assumed**; absent means the engine probes and reports what it found (step-01 defines the consequence) | optional |
| `STORY_FILE` | story or task acceptance source; present in `full` mode | optional |
| `FINDINGS_SINK` | file the findings are written to | optional |
| `ARTIFACT_DIR` | folder for lens prompt files when subagents are unavailable | optional |

⛔ **A missing required input is a stop, not a guess.** If the caller did not supply one, say which
and return — resolving it yourself is how a review ends up describing a different diff than the one
being gated. The mirror rule: never re-derive an input the caller already resolved.

**The optional inputs behave differently, and this is the rule for all of them:** when one is
absent the engine does **not** invent a path. It returns the content that would have gone there to
the caller, inside the summary, and names what it could not write. The caller has the folder; the
engine has the findings.

## What the engine does NOT do, ever

These belong to the caller and to the human close-out:

- **It never runs a command.** The `allowed-tools` line above grants no Bash, deliberately: a
  reviewer that can execute is one edit away from being an editor, and SCC-295 measured three of
  five lenses writing into the builder's tree mid-review. Reproduction therefore splits across three
  layers — the lens runs its command in its own copy, this engine checks the claim is *there*, and
  the CALLER re-runs it on the real tree and owns the receipt (step-03 §4).
- It never issues the `Verdict:` line.
- It never advances a story's state or writes a board file.
- It never runs the test or clean-code gates.
- It never merges, pushes, or transitions a ticket.
- It never stops the caller's flow to ask a question — step-04 hands findings back; it does not wait
  on them.
- **It never produces a ticket** — no residue ticket, no "proposed" or "decided" ticket, no
  ticket-ruling row. A finding that survives step-03's reproduction gate is **fixed** by the caller
  in the same lane before its verdict; a fix the caller may not apply alone is written as a patch
  and `held` for the operator's word, never proposed as a ticket (operator rulings 2026-08-15, both,
  and 2026-09-11: no escalate bucket, no defer bucket).

## Flow

1. `steps/step-01-review.md` — parallel lens fan-out over the diff
2. `steps/step-02-verify.md` — pass-through (the verify wave is retired, SCC-447)
3. `steps/step-03-triage.md` — the reproduction gate, then bucket and score
4. `steps/step-04-record.md` — write the findings, return the summary

Read each step file fully and follow it. Start with `steps/step-01-review.md`.

## What the engine returns to its caller

```
review-runtime:  fan-out | inline
lens_isolation:  worktree | mixed — <lens>: <mode>, … | shared — <why, when the runtime could not isolate>
lenses_run:
- <lens> · ok | recovered-inline | dead — <why, when it is not `ok`>
- <one row per lens that was applicable — the ROSTER, not a summary of it>
lenses_counted:  <n>/<applicable>
lenses_na:       <lenses not applicable in this mode, or "none">
findings:        <f> fix   (<d> dropped — no reproduction · <r> recorded)
dispositions:    per-lens: <lens>=<reproduced>/<dropped>/<recorded> · … (SCC-233; a multi-lens finding counts once per contributing lens)
severity_floor:  none | CONCERNS | FAIL
notes:           <degradations, absent optional inputs, verification state>
```

⛔ **Return these as PLAIN LINES — the fence above is illustration and must NOT be copied
(SCC-240).** The caller pastes your return verbatim into the walkthrough, and
`walkthrough_roster.py` strips code fences before it reads anything (SCC-154), so a roster
handed back inside a fence is a roster the close-out gate cannot see — and until this was
written, the refusal it produced said only that the roster was absent.

⛔ **`lenses_run:` is a BLOCK, and its rows are the evidence the review happened.** It was one
counted line until SCC-173: `lenses_run: 5/5` is the engine's *claim* about itself, in exactly the
way `Verdict: PASS` is the caller's — and a walkthrough carrying only a verdict merged clean with
zero lenses run, because nothing downstream could tell a review that ran from one that was narrated.
The caller copies these two fields into the walkthrough's `## Code Review` **verbatim**, where
`walkthrough_roster.py` reads them and both preflights block on what it finds. Keep the row shape
(`- <lens> · <state>`), keep the header spelling, and do not summarise the block away.

**The severity axis, stated once: severity order is `none` < `CONCERNS` < `FAIL`.** The floor this
engine returns is **provisional**, and the caller resolves it at the stamp. The caller may report
anything MORE severe — its own gates can add their own reasons. There are exactly TWO
ways a caller may come back LESS severe than the floor this engine returned. Both are
machine-checkable, and both are evidence, never
judgment: a receipt showing the command does **not** fail on the real tree, or a fix whose pin was
seen red and then green. Any other downgrade is the caller overruling the review, which it may not do.
When a caller's own law says a dead layer *"caps the verdict at CONCERNS"*, that phrase and this
floor mean the same thing: the verdict may not come back better than CONCERNS.

`<applicable>` excludes any lens that does not run in this `review_mode`; those are listed on
`lenses_na` instead. A spec-less review therefore reports `2/2`, never `2/3` — see step-01.
