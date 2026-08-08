---
description: Fast-track dev flow — story, direct dev (no ATDD red phase, no planning stop, no adversarial review), scoped tests, clean-code audit, stop for human review. Carries an EJECT tripwire back to the full ①②③ lane the moment the change turns out not to be small.
platforms: [opencode, antigravity, claude, codex]
---

# /sudo-quick-dev — Fast-Track Development (fast lane, guarded)

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push
> - `.agents/rules/reproduce-before-you-fix.md` — **when the quick fix is a BUG fix**: the five gates
>   (reproduce → minimize → pin a test seen red → falsify one hypothesis at a time → minimal fix → prove
>   by reverting). Its G3 stop conditions fire the EJECT tripwire below.

Thin orchestrator for SMALL fixes. It keeps the speed — bypasses red-phase test writing
(`sudo-write-story-tests`), planning approval gates, and the adversarial review (`sudo-code-review`) —
and keeps the safety through four cheap guards: a worktree, an eject tripwire, scoped verification,
and the clean-code audit. The human review at the end is the gate.

> Flow position: `bmad-create-story` → worktree → `bmad-dev-story` (direct, continuous) → scoped
> tests → `/clean-code-audit` → [STOP for human review; close-out is the human's].

## Step 0 — Resolve the target project (FIRST — before any other step)
Bind the target per `.agents/rules/sudo-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override → `.agents/active-project.txt` → else **STOP and ask** — never guess, never operate on the
lobby. Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>` before any work; every path and
child tool call resolves under `PROJECT_ROOT`.

## Step 0.5 — Worktree (before the first edit)
Per `worktree-per-story`: run `git worktree list` under `PROJECT_ROOT`; reuse an existing
`claude/<JIRA-KEY>-<slug>` tree for this fix, else open one off the story's EPIC branch (`epic/<JIRA-KEY>-<slug>`).
No epic applies — a truly ad-hoc fix outside any sprint — then mirror `git-policy.md`'s chore lane
instead: a short-lived `chore/<JIRA-KEY>-<slug>` branch off `main`, no worktree, merged back to `main` in the same
session with Daniel's sign-off. Echo the case. Quick fixes are NOT exempt — this is what keeps them
tangle-free, rollbackable, and landable through the normal close-out.

## Step 1 — Create the story
Invoke the **`bmad-create-story`** skill for the story in `$ARGUMENTS` (e.g., a story ID like `12.3`, or a new descriptive name). This creates the story file in `_bmad/bmm/stories/` with its ACs.

## Step 2 — Direct Implementation (Continuous)
Invoke the **`bmad-dev-story`** skill on the created story.
* **Bypass Planning Gate:** the developer agent is explicitly permitted to bypass "wait for approval"
  planning gates (such as the planning_mode halt after writing the implementation plan). Plan,
  implement, and write the walkthrough in one continuous execution.
* **Skip ATDD:** skip the strict red-phase acceptance-test-first cycle; implement the minimal code
  directly to satisfy the story.
* **Root cause first:** for a bug fix, find the root cause before touching code — no symptom patches.
  Work `reproduce-before-you-fix` in order: **no edit before a citable reproduction (G1)**, and the
  pinning test of Step 2b is written and **seen red (G2) BEFORE the fix**, not after it.
* **⛔ EJECT TRIPWIRE (the safety core — check as you go, not just at the end):** if the emerging
  change exceeds **~3 files / ~150 changed lines**, or touches a **protected surface** — auth/tenancy
  walls, payments, PII handling, DB schema or security rules, a cross-boundary API/SSE contract —
  **STOP. This is not a quick fix.** Report the one-line reason and hand off to the full lane
  (`/sudo-write-story-tests` ①); keep the worktree and the story file, discard nothing.

## Step 2b — Scoped verification (never the full suite)
Run the test file(s)/suite covering the touched module — the WHOLE endpoint/module suite when a
shared handler changed (a new read on a shared endpoint silently breaks sibling tests) — and paste
the **actual** output.
* **Bug fixes add ONE pinning regression test** (a fix without a test regresses silently).
* Config/copy tweaks need no new test — say so explicitly.
* The full suite is deliberately NOT run here — that is ③'s job in the full lane; anything shipping
  to `main` still passes PR CI + `/sudo-e2e`.

## Step 3 — Clean-code audit (post-dev conformance)
Invoke the **`/clean-code-audit`** skill on the fix's diff (full two-half pass — machine floor +
judgment — since no adversarial review runs in this lane), bound to the Step 0.5 worktree. Then add a
one-line **AC-trace confirmation** to the report: each AC → where it's implemented; anything in the
diff beyond the ACs is drift — cut it or name why it stays. Apply safe fixes, re-run the affected
check, paste output.

## Step 3.5 — File the Dev Record on the ticket (AUTOMATIC, never ask)
This lane **closes its own branch**, and the ad-hoc chore lane never reaches
`/sudo-update-sprint-memory` at all — so this is the only place its knowledge gets recorded. Before
SCC-49 it died in the walkthrough. The key is already in hand: the story's `jira_key:` frontmatter on
the story lane, or the `<JIRA-KEY>` in the `chore/<JIRA-KEY>-<slug>` branch name on the ad-hoc lane.

```bash
python3 .agents/scripts/jira_feed.py devrecord --key <JIRA-KEY> --story <id-or-slug> \
       --project <PROJECT> --stage quick-dev [--walkthrough <path>] \
       --outcome "<what shipped, one line>" --verdict "<the Step 3 verdict>" \
       --decision "<a ruling made while fixing>" --pitfall "<what nearly bit>" \
       --followon "<anything Step 3 deferred>" --apply
```

**Exactly one Dev Record per ticket.** The script finds an existing record and UPDATES it in place, so
a story that later goes through `/sudo-update-sprint-memory` ends with one current record instead of
two partial ones — **never pass `--append-new` here.** It reads the ticket back and exits 2 if the
comment is not there; a non-zero exit means the record did NOT land, so report that rather than
success. No ticket key at all (a fix outside any ticket) → say so in the Done report and skip;
**never invent a key.** Full acli reference: `.agents/rules/jira.md`.

## Done
Stop here. Do **NOT** run `/sudo-update-sprint-memory`. Commit inside the worktree (explicit paths —
never `git add -A`); never land on the epic branch (close-out's job), never touch `main`. Display the
story path, the key changes, the test +
audit output, and invite the human (Daniel) to review and run `/sudo-update-sprint-memory` himself
when satisfied.
