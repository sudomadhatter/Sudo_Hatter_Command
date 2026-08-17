---
description: Fast-track dev flow on bmad-quick-dev engine — clarify intent, implement, and run mandatory review gate.
platforms: [opencode, antigravity, claude, codex]
---

# /cicd-quick-dev — Fast-Track Development

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push
> - `.agents/rules/artifacts-always-first.md` — **§ When to Skip case 4 covers this lane: invoking this
>   command IS the "skip the plan" instruction.** The closing `walkthrough.md` is NOT skipped.
> - `.agents/rules/reproduce-before-you-fix.md` — **when the quick fix is a BUG fix**: the five gates
>   (reproduce → minimize → pin a test seen red → falsify one hypothesis at a time → minimal fix → prove
>   by reverting). Its G3 stop conditions fire the EJECT tripwire below.

Thin orchestrator for SMALL work — a fix, a docs/config change, a task that does not earn the full
development pipeline.

**Accuracy over speed.** What this lane drops is the *pipeline* — the ATDD red phase, the full suite, the
three-reviewer panel, the revert-and-re-derive loops. It does **not** drop the rigour: a worktree,
acceptance criteria fixed before the code, an eject tripwire, an independent adversarial review, an
objective machine floor, and a human gate at the end.

> Flow position: worktree → `bmad-quick-dev` (one-shot route) → review gate → [STOP for human review;
> close-out is the human's].

## Step 0 — Resolve the target project (FIRST — before any other step)
Bind the target per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
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

## Step 1 — Clarify, fix the ACs, and route
Invoke the **`bmad-quick-dev`** skill with `$ARGUMENTS`. Its `step-01-clarify-and-route` does the
intent check, story-key resolution, epic-context load, and the version-control sanity check.

**⊕ Before leaving Step 1, capture an explicit acceptance-criteria list** — 2–6 checkable statements,
echoed in the chat. This is the accuracy baseline: the one-shot route writes its spec *after* the code,
so without this there is nothing to audit the diff against. If the intent will not reduce to checkable
ACs, that is not a quick fix — eject.

**Do NOT create a story file on the ad-hoc lane.** A story id / epic story keeps BMAD's normal story
handling; an ad-hoc fix mints **no story file and no epic key** (`artifacts-always-first` §2 quick-fix
bucket) — hanging one off a finished epic silently reopens it.

## Step 1.5 — ⛔ EJECT TRIPWIRE (check here, and again as you go)
**STOP and hand off to the full lane (`/cicd-write-story-tests` ①) if any of these is true:**
- Step 1 routes to **plan-code-review** rather than one-shot. The skill judges blast radius; "this needs
  the planning route" IS the eject signal — it is a truer measure than counting files.
- The change touches a **protected surface** — auth/tenancy walls, payments, PII handling, DB schema or
  security rules, a cross-boundary API/SSE contract. Risk, not size, decides this one.
- The intent will not reduce to checkable ACs (Step 1), or a review finding in Step 3 is bigger than a
  trivial patch.

Report the one-line reason; keep the worktree and everything written, discard nothing.

## Step 2 — One-shot implementation
Let the skill's `step-oneshot.md` run: implement the clarified intent directly, then its own review and
spec trace. Commits happen **inside the worktree, explicit paths only** — never `git add -A` — and every
commit subject leads with the repo's Jira key from `.agents/jira.conf`, or the armed `commit-msg` hook
refuses it. Never push `main`.

## Step 3 — ⭐ Review gate (mandatory — never skipped, never "assumed clean")
Runs **after** the work, on the diff since the skill's `baseline_commit`. Tiered by what was touched:

**Every lane**
- **Independent adversarial reviewer** — `bmad-review-adversarial-general` in a subagent with **NO
  conversation context**, at the same model capability. Blind eyes are the point: an agent reviewing its
  own reasoning anchors on it.

**Code touched — add all three**
- **Acceptance auditor** — the diff against the **Step 1 ACs**. Each AC → where it is satisfied; anything
  in the diff beyond the ACs is drift: cut it or name why it stays.
- **`/cicd-clean-code-audit`** — the objective machine floor (ruff / eslint / pyrefly / tsc). This half can
  **FAIL**; the judgment half caps at CONCERNS.
- **Scoped tests** — the test file(s)/suite covering the touched module, and the **WHOLE** endpoint/module
  suite when a shared handler changed (a new read on a shared endpoint silently breaks sibling tests).
  Paste the **actual** output. Bug fixes add ONE pinning regression test.

**Docs / config only — no lint floor (there is nothing to lint)**
- Link + anchor check on every path and `#L` anchor touched.
- **SOP-currency check** — a usage-surface change (`.agents/commands/`, `.agents/rules/`,
  `.agents/scripts/`, git hooks, root `AGENTS.md`) must move
  `docs/_scc_sops_prds/workflows_testing_SOP.md` in the same commit, or the armed gate
  rejects the commit.

Classify findings **patch / defer / reject**; auto-fix patches NOW, in this lane; drop noise with a
one-line reason. **`defer` is not a parking lot** (operator rulings 2026-08-15): a finding may be
deferred ONLY against a named structural blocker — another live lane owns the file, the fix lives in
another repo, or it waits on a decision the operator has not taken — and the deferred-work entry names
that blocker; "pre-existing" or "bigger than this lane" is not one. A finding worth fixing with no
blocker is a patch, or it is the EJECT tripwire (Step 1.5) firing. **Anything bigger than a trivial
patch → HALT** (and see Step 1.5). Re-run the affected check after applying fixes and paste the output.

## Step 4 — Artifacts, then stop
- The **spec** the skill wrote is the working doc (it carries the Suggested Review Order).
- **Story lane only:** the skill syncs `sprint-status.yaml` and advances the story to **`review`** on its
  way out. That is the normal dev→review flip (`story-status-flip-contract`) — `done` stays yours. On the
  ad-hoc lane there is no story key, so the sync skips silently.
- Write a **thin `walkthrough.md`** in the owning `_artifacts/` store — story work →
  `epic_<E>/<story>/`; ad-hoc → `quick_fixes/quick-fix-<track>.<n>-<slug>/` (read that folder's
  `INDEX.md` for the next free number and append the row by hand; **create the folder + its `INDEX.md`
  if this is the repo's first quick fix** — the lobby has none yet, AviationChat does). It **links** the spec rather than
  restating it, and carries `## Task Checklist` → `## Evidence` (AC→evidence + pasted totals + SHA) →
  `## Code Review (<date>)` with the canonical **`Verdict: PASS|CONCERNS|FAIL|WAIVED @ <sha>`** line →
  `## Your Actions`. Post clickable Markdown links to every artifact in the chat.

## Step 4.5 — File the Dev Record on the ticket (AUTOMATIC, never ask)
This lane **closes its own branch**, and the ad-hoc chore lane never reaches
`/cicd-update-sprint-memory` at all — so this is the only place its knowledge gets recorded. Before
SCC-49 it died in the walkthrough. Runs AFTER Step 4 so the walkthrough it points at exists. The key is
already in hand: the story's `jira_key:` frontmatter on the story lane, or the `<JIRA-KEY>` in the
`chore/<JIRA-KEY>-<slug>` branch name on the ad-hoc lane.

```bash
python3 .agents/scripts/jira_feed.py devrecord --key <JIRA-KEY> --story <id-or-slug> \
       --project <PROJECT> --stage quick-dev --walkthrough <the Step 4 walkthrough> \
       --outcome "<what shipped, one line>" --verdict "<the Step 3 verdict>" \
       --decision "<a ruling made while fixing>" --pitfall "<what nearly bit>" \
       --followon "<only what Step 3 deferred against a NAMED blocker - never a pile>" --apply
```

**Exactly one Dev Record per ticket.** The script finds an existing record and UPDATES it in place, so
a story that later goes through `/cicd-update-sprint-memory` ends with one current record instead of
two partial ones — **never pass `--append-new` here.** It reads the ticket back and exits 2 if the
comment is not there; a non-zero exit means the record did NOT land, so report that rather than
success. No ticket key at all (a fix outside any ticket) → say so in the Done report and skip;
**never invent a key.** Full acli reference: `.agents/rules/jira.md`.

## Done
Stop here. Do **NOT** run `/cicd-update-sprint-memory`, never land on the epic branch (close-out's job),
never touch `main`. Display the spec path, the walkthrough link, the key changes, and the review-gate
output, then invite Daniel to review and run `/cicd-update-sprint-memory` himself when satisfied.
