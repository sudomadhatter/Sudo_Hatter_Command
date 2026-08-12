---
name: code-review-engine
description: The house review engine — runs the adversarial lens fan-out over a resolved diff, verifies findings, triages them into four buckets and records them, returning a severity summary its caller turns into a verdict. Invoked BY /cicd-code-review, /smh-code-review and /cicd-code-review-AP; it is not a standalone command and never resolves its own inputs.
allowed-tools: Read, Write, Glob, Grep, Task
---

# Code Review Engine

**Goal:** take a diff the caller has already resolved, hunt it with parallel lenses, verify what
they find, triage it, record it — and hand back a severity summary. Nothing else.

**Your role:** you are the engine, not the reviewer command. The caller owns the story, the board,
the gate and the verdict line. You own findings and their severity.

## ⛔ FIRST — was this invoked with a caller contract?

Every platform that publishes skills makes this one visible as a menu entry, so a human can reach it
directly. **If `REPO`, `WORKTREE`, `DIFF`, `HEAD_SHA` and `review_mode` were not supplied by a
calling command, you were invoked from a menu.** Print the contract table below, say this engine
runs only as a step of `/cicd-code-review`, `/smh-code-review` or `/cicd-code-review-AP`, and
**return without reading the step files.** Do not resolve the inputs yourself and do not proceed.

## The caller contract — these arrive resolved, and the engine never resolves them itself

| Input | What it is | Required |
|---|---|---|
| `REPO` | absolute path to the repository root | yes |
| `WORKTREE` | absolute path to the tree the diff came from (may equal `REPO`) | yes |
| `DIFF` | the diff text, or a path to it — already scoped by the caller | yes |
| `HEAD_SHA` | the sha the diff was taken at, for the record the caller writes | yes |
| `review_mode` | `full` (a spec exists) or `no-spec` (none) | yes |
| `STORY_FILE` | story or task acceptance source; present in `full` mode | optional |
| `EVIDENCE_PACK` | pre-extracted evidence dossier; absent is normal today | optional |
| `FINDINGS_SINK` | file the findings are written to | optional |
| `ARTIFACT_DIR` | folder for lens prompt files when subagents are unavailable | optional |
| `DEFERRED_WORK` | the caller's `deferred-work.md` | optional |

⛔ **A missing required input is a stop, not a guess.** If the caller did not supply one, say which
and return — resolving it yourself is how a review ends up describing a different diff than the one
being gated. The mirror rule: never re-derive an input the caller already resolved.

**The four optional inputs behave differently, and this is the rule for all of them:** when one is
absent the engine does **not** invent a path. It returns the content that would have gone there to
the caller, inside the summary, and names what it could not write. The caller has the folder; the
engine has the findings.

**What the engine does NOT do, ever** — these belong to the caller and to the human close-out:
issue the `Verdict:` line · advance any story's state or write any board file · run the test or
clean-code gates · merge, push, or transition a ticket · stop the caller's flow to ask a question
(step-04 hands decisions back as findings; it does not wait on them).

## Flow

1. `steps/step-01-review.md` — parallel lens fan-out over the diff
2. `steps/step-02-verify.md` — verification pass over what the lenses found
3. `steps/step-03-triage.md` — normalize, dedupe, bucket, and score severity
4. `steps/step-04-record.md` — write the findings, return the summary

Read each step file fully and follow it. Start with `steps/step-01-review.md`.

## What the engine returns to its caller

```
lenses_run:      <n>/<applicable>   (per-lens: ok | recovered-inline | dead)
lenses_na:       <lenses not applicable in this mode, or "none">
findings:        <d> decision · <p> patch · <w> defer   (<r> dismissed)
severity_floor:  none | CONCERNS | FAIL
notes:           <degradations, absent optional inputs, verification state>
```

**The severity axis, stated once: severity order is `none` < `CONCERNS` < `FAIL`.** The caller may
report the floor or anything MORE severe — its own gates can add their own reasons — and never
anything less severe. When a caller's own law says a dead layer *"caps the verdict at CONCERNS"*,
that phrase and this floor mean the same thing: the verdict may not come back better than CONCERNS.

`<applicable>` excludes any lens that does not run in this `review_mode`; those are listed on
`lenses_na` instead. A spec-less review therefore reports `3/3`, never `3/4` — see step-01.
