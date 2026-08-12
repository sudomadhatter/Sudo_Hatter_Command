---
name: code-review-engine
description: The house review engine — runs the adversarial lens fan-out over a resolved diff, verifies findings, triages them into four buckets and records them, returning a severity summary its caller turns into a verdict. Invoked BY /cicd-code-review, /smh-code-review and /cicd-code-review-AP; it is not a standalone command and never resolves its own inputs.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Code Review Engine

**Goal:** take a diff the caller has already resolved, hunt it with parallel lenses, verify what
they find, triage it, record it — and hand back a severity summary. Nothing else.

**Your role:** you are the engine, not the reviewer command. The caller owns the story, the board,
the gate and the verdict line. You own findings and their severity.

---

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
| `FINDINGS_SINK` | where step-04 writes; defaults to the caller's walkthrough | optional |

⛔ **A missing required input is a stop, not a guess.** If the caller did not supply one, say which
and return — resolving it yourself is how a review ends up describing a different diff than the one
being gated. The mirror rule: never re-derive an input the caller already resolved.

**What the engine does NOT do, ever** — these belong to the caller and to the human close-out:
issue the `Verdict:` line · advance any story's board state or write any board file · run the test
or clean-code gates · merge, push, or transition a ticket · stop the caller's flow to ask a
question (step-04 hands decisions back as findings; it does not wait on them).

## Flow

1. `steps/step-01-review.md` — parallel lens fan-out over the diff
2. `steps/step-02-verify.md` — verification pass over what the lenses found
3. `steps/step-03-triage.md` — normalize, dedupe, bucket, and score severity
4. `steps/step-04-record.md` — write the findings, return the summary

Read each step file fully and follow it. Start with `steps/step-01-review.md`.

## What the engine returns to its caller

```
lenses_run:      <n>/<total>   (with per-lens status: ok | recovered-inline | dead | n/a (mode))
findings:        <d> decision · <p> patch · <w> defer   (<r> dismissed)
severity_floor:  none | CONCERNS | FAIL
notes:           <degradations, extractor failures, anything the caller must record>
```

`severity_floor` is the engine's whole contribution to the verdict: the caller may land ON it or
BELOW it (a caller's own gate can add its reasons), never above it.
