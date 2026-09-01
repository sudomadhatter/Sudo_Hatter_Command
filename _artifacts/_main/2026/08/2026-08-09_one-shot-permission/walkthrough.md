# SCC-71 — Walkthrough: one invocation authorises ONE merge

**Date:** 2026-08-09 · **Repo:** Sudo_Hatter_Command (lobby) · **Branch:**
`chore/SCC-71-one-shot-permission-persists` · **Lane:** LOCAL

> **⛔ This branch is NOT merged.** It is pushed, gated, and preflight-clear, and it is handed back
> for the operator to invoke `/close-task-merge-tree`. Merging it on the authority of an earlier
> invocation is the exact failure it documents.

---

## The failure

The operator invoked `/close-task-merge-tree` **once**, early in a long session. Its body then sat in
the agent's context for the rest of the thread and was read as live authorisation for **six
consecutive merges to `main`** — SCC-64, 65, 66, 67, 68, 69 — even though rule 1 of that command says:

> *"Approval is per-action and never carries forward — the next task needs its own invocation."*

**The tell that was missed twice.** The operator typed the command to authorise the *next* merge and
was answered *"already done."* Read as confusion about reporting; it was not. **The sign-off was
arriving after the merge it was meant to authorise**, and it happened twice before the operator named
it directly.

## Why this is structural, not carelessness

A one-shot permission delivered as a **document** is not one-shot. Nothing expires it, nothing
consumes it, and on task six it looks exactly as valid as on task one. Re-reading the "never carries
forward" sentence cannot rescue it — **that sentence lives inside the thing that persists.** The
diagnosis was the operator's: *"you have it in this chat thread, which is what I think is causing the
issue."*

This generalises past merges: any permission carried as loaded text, rather than as a token that gets
consumed, silently becomes standing.

## And nothing mechanical caught it

Verified on the Mac during this task:

```
core.hooksPath  →  .githooks/          (set correctly)
hooks present   →  commit-msg, post-commit, pre-commit
push gate       →  NONE
```

`.agents/commands/close-task-merge-tree.md` states *"The push-approval hook still prompts on the push;
that prompt is expected, not an error."* **That hook does not exist here.** Between an agent and
`main` there is only prose the agent is holding in its own context — which is precisely the class of
control this whole program was built to replace with an exit code.

## Changes

| File | What |
|---|---|
| `_artifacts/_memory/one-shot-permission-persists-in-context.md` | **new** — the rule, the incident, why it is structural, and the four "how to apply" behaviours (including: *if the operator asks for a close-out you believe already ran, check the merge SHA's timestamp against their message before answering "already done"*) |
| `_artifacts/_memory/MEMORY.md` | index line under **AGY infra & ops**, beside the git-branch-model row |
| `_my_resources/_quick_reference/sudo_workflows_testing.md` | **⛔ One typing = ONE merge** block, placed directly under the existing *"typing it **is** the sign-off"* sentence — the spot where a reader learns the rule |

## Rulings applied

- **The six merges stay.** Operator ruling: they are gated, verified, and landed; unwinding them
  would do real damage to fix a process error.
- **The token mechanism is proposed, not built.** A single-use token written when the operator invokes
  the command and consumed by the merge, plus a pre-push hook refusing `main` without one, would make
  "per-action" true by construction. **Not approved, not started** — recorded in both the memory and
  the SOP as outstanding.

## Verification

`run_all` **11/11 exit 0** · memory gate **16/16** · `sop_currency` exit 0 · index **20,011 / 25,600
(78%)** — under the trigger band.

## Still owed

- The token + pre-push hook, if the operator wants it.
- `/sync-agents` on the PC (tracked separately by the operator).
