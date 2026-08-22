# SCC-279 — root `GEMINI.md` folds back to a one-line adapter

**Ticket:** SCC-279 (Subtask, Part C of SCC-262) · **Lane:** `chore/SCC-279-gemini-adapter-fold`
**Base:** `origin/main @ 6273c82` · **Lane type:** lightweight (doc-only, operator-directed) + one gate test
**Date:** 2026-08-22

---

## The operator's ruling — recorded verbatim (Acceptance C1)

The ticket named two doors and said the choice was not an agent's to make. Asked which, the operator
chose:

> **A — FOLD (Recommended)** — *"Shrink `GEMINI.md` to a one-line adapter. Rule 1 is deleted (the
> `-Maintained` flag it names is retired and errors); rules 2 and 3 cite `worktree-per-story.md` and
> `git-policy.md`, which already cover them. All three law docs then agree."*

Door B (codify a Gemini carve-out in the standard) was not taken. Scope followed the ruling: `GEMINI.md`,
the standard, `AGENTS.md` §8 — **not both doors**.

---

## What was actually wrong

Root `GEMINI.md` was 9 lines carrying a `## GEMINI SPECIFIC HARD RULES:` block. Three documents say it
should be 5 lines of redirect: the routing plan's **R8**, `docs/workspace-standard.md` **Part 1 Layer 1**,
and root `AGENTS.md` **§8**.

⭐ **The shape is worse than untidy, in two specific ways.**

1. **Law that binds everyone, written where one model reads it.** None of the three rules was
   Gemini-specific in substance. A Claude or Codex session never opens that file, so the rules were
   invisible to three of four platforms while reading as mandatory to the fourth.
2. **A shared entry file rots unwatched.** Rule 1 told Gemini to run
   `sync-agents.ps1 -Maintained`. That flag was **retired 2026-08-07** and now `Write-Error`s and
   `exit 1` (`sync-agents.ps1:98-104`). It also named `Fresh_Workspace_BMAD` as a "top maintained
   project" — de-listed the same day (SCC-25). An adapter is the file nobody re-reads, so a **dead
   instruction sat in the workspace entry point** and was still the first thing one platform loaded
   every session.

---

## Acceptance C3 — nothing was LOST in the move

Each rule, and where it already lives for **all four** platforms:

| GEMINI.md rule | Already law at | Load class | Evidence |
|---|---|---|---|
| 3 · EXPLICIT GIT COMMITS ONLY (no `git add -A/./-u`; verify `--cached`) | `.agents/rules/git-policy.md:295-299` | **protocol** (always-load tier 2) | near-verbatim, including the `git diff --cached --stat` check |
| 2 · WORKTREE BEFORE CODE EDITS | `.agents/rules/worktree-per-story.md` | **protocol** | trigger is "ANY lane that will produce commits, BEFORE the first edit" (SCC-62) |
| 1 · SYNC MAINTAINED PROJECTS ONLY | `.agents/rules/project-law.md` §Hard stops | on-demand **+ mechanical** | *"`/smh-sync-agents` targets the command center and the machine-global caches only"* — and `sync-agents.ps1` refuses `-Maintained` outright |

⚠ Rule 2 was also **subtly wrong as written**: it said branch from the epic branch, which is true only for
story lanes. Task/ad-hoc work takes `chore/*` off `main` — the very lane this ticket ran on.
`worktree-per-story.md`'s table carries both cases; the GEMINI copy carried one.

So the fold **removes one dead instruction and two stale duplicates of live law**. Nothing moved into a
new home because nothing needed one.

---

## ⭐ The finding this lane added: the existing check could not see it

`check_maps.py` already reads adapters — and it asks whether the redirect is **present**
(`ADAPTER_PHRASE in text`, check 8). Two reasons that never fired:

- **check 8 covers `TIER2_DIRS` only** (`_artifacts`, `_my_resources`, `docs`). At the **root** it calls
  `need("GEMINI.md", "adapter")` — **existence only**, never content.
- Even where it does read content, *"contains the redirect"* and *"is the redirect"* are different
  claims, and only the second is what the three documents promise.

That is the same class as SCC-164 A–K and SCC-179: **a written rule with nothing checking it.** So the
fold ships with its guard.

**`.agents/scripts/tests/test_entry_adapters.py`** — auto-discovered by `run_all.py`, so it is **fatal**,
unlike check 8's non-fatal hint. It reads every **tracked** `CLAUDE.md` / `GEMINI.md` (tracked, not
globbed — a worktree carries untracked copies of anything, and a gate that reads whatever is on disk
reports a different answer per lane) and fails on any line that is not the title, the redirect, or the
house footnote. `ADAPTER_PHRASE` is **imported from `check_maps`**, never re-typed: two spellings of one
house sentence is how the check and the file drift apart.

`_routing-canary/`'s two adapters are exempt **BY NAME with a reason** — they point at `agent.md` by
design, and holding them to the house sentence would stop the canary testing what it exists to test. An
unexplained exemption is how the next block of hard rules gets parked where nothing looks.

---

## Evidence

### RED first — captured against the pre-fix tree

The test was written and run **before** `GEMINI.md` was touched. Exit **1**, and it named the one file:

```
[PASS] the house adapter is clean
[PASS] title + redirect alone is clean (the footnote is optional)
[PASS] model-specific hard rules are caught even though the redirect is present: 4 flagged: ...
[PASS] a file with the footnote but NO redirect is caught
[PASS] the canary's `agent.md` redirect does NOT pass as the house adapter
[PASS] the tree actually has adapters to check (a silent empty sweep is not a pass): 10 tracked adapters
[FAIL] every tracked CLAUDE.md / GEMINI.md is the redirect and nothing more: GEMINI.md: no redirect
       line — expected `Read `AGENTS.md` in this same folder ...`; L3: **CRITICAL MANDATE:** ...;
       L5: ## GEMINI SPECIFIC HARD RULES:; L6: 1. **SYNC MAINTAINED PROJECTS ONLY**: ...;
       L7: 2. **WORKTREE ENFORCEMENT BEFORE CODE EDITS**: ...; L8: 3. **EXPLICIT GIT COMMITS ONLY**: ...
-- 6/7 passed --
```

⭐ Note the first violation: **"no redirect line."** The old file's mandate said *"read and strictly
follow … `AGENTS.md` located in this exact folder"* — its own wording, not the house sentence. So root
`GEMINI.md` would have failed `check_maps`' phrase test too, had that test ever looked at the root.

The fixture cases prove the detector is alive **both ways** before its silence means anything: the house
adapter is clean, a redirect-only file is clean, the broken shape is caught with all four offending lines
named, a footnote-without-redirect is caught, and the canary shape is flagged (which is exactly why it is
exempted by name rather than quietly passing).

### GREEN after the fold

```
-- 7/7 passed --
[COVERAGE] adapters read this run: 10 (.agents/CLAUDE.md, .agents/GEMINI.md, CLAUDE.md, GEMINI.md,
           _artifacts/CLAUDE.md, _artifacts/GEMINI.md, _my_resources/CLAUDE.md, _my_resources/GEMINI.md,
           docs/CLAUDE.md, docs/GEMINI.md)
[SKIP] _routing-canary/CLAUDE.md — routing canary — adapters point at `agent.md` by design
[SKIP] _routing-canary/GEMINI.md — routing canary — adapters point at `agent.md` by design
```

Root `GEMINI.md` is now byte-identical to root `CLAUDE.md` apart from the platform name — verified by
`diff` with both names normalised, not by eye.

### Gates — run **bare** at the lane sha

A pipe hands back `tail`'s exit code, so a red gate reads as green. Each was run bare with its output
redirected and `$?` read immediately.

| Gate | Result | Exit |
|---|---|---|
| `python3 .agents/scripts/tests/run_all.py` | **49/49 files passed** (48 + this lane's new file) | **0** |
| `python3 .agents/scripts/workflow_lint.py --toolkit-only` | 0 error(s), 0 warning(s), 8 info | **0** |
| `python3 .agents/scripts/check_maps.py --depth3-only --strict` | silent | **0** |

### SOP currency

`sop_currency.py`'s surface list is `.agents/commands/*.md`, `.agents/rules/*.md`, the hook dirs, and
`.agents/scripts/*.py|.ps1` — with `.agents/scripts/tests/` **explicitly exempt** (`_EXEMPT_PREFIXES`).
This lane touches none of them, so **no `[sop-ok]` was used and none was needed**. The SOP was updated
anyway, on merit: a new fatal suite member belongs in the suite table, and the delta line belongs in the
changelog (`sop-currency.md` §Writing the update, habit 4).

---

## Files changed

| File | Change |
|---|---|
| `GEMINI.md` | 9 lines → the 5-line house adapter, identical to `CLAUDE.md` bar the platform name |
| `docs/workspace-standard.md` | §0.5 **R8** row: open exception → **CLOSED**, ruling + where each rule already lives + the guard · Part 1 Layer 1: the promise gets its enforcement named beside it · conversion checklist row and the Tier-2 row now distinguish the non-fatal presence hint from the fatal body check |
| `AGENTS.md` | §8: *"asserted, not assumed"* + the test, with the one-line reason |
| `.agents/scripts/tests/test_entry_adapters.py` | **new** — the guard, RED first |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | suite-table row for the new test |
| `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` | one delta line |
| `_artifacts/_main/INDEX.md` + this folder | the session record |

---

## Acceptance C — line by line

| # | Requirement | Status |
|---|---|---|
| C1 | Operator's ruling recorded verbatim in the walkthrough | ✅ top of this file |
| C2 | `GEMINI.md` and the three law documents AGREE | ✅ file is the house adapter; R8 row, Layer 1 and §8 all updated to match |
| C3 | Door A: no rule LOST — each covered by an existing rule (cited) or given a named home | ✅ the table above; two cited in protocol-tier rules, one in `project-law.md` **and** enforced by the script |
| C4 | The §0.5 R8 row updated to match the outcome | ✅ open exception → CLOSED, with the ruling |
| C5 | Enforcement suite green | ✅ 49/49 · 0/0/8 · exit 0, all bare |

---

## ⚠ Scope note — one thing added beyond the ticket, and why

The ticket's acceptance did not ask for a test. I added one because this lane's whole finding is that a
promise made in three documents went unchecked for an unknown length of time, and Door A without a guard
leaves the identical hole open for the next edit. It is a **test-only** addition — no new script, no
command change, no gate surface — so the lane stays inside its risk class. If that is unwanted, deleting
`test_entry_adapters.py` reverts it with no other change.

---

## Findings ledger

| # | Finding | Disposition |
|---|---|---|
| 1 | Root `GEMINI.md` carries three model-specific hard rules against R8 / Layer 1 / §8 | **FIXED** — folded on the operator's Door A ruling |
| 2 | Rule 1 names `sync-agents.ps1 -Maintained`, retired 2026-08-07, now `exit 1` — a **live dead instruction** in the entry point | **FIXED** — deleted; correct scope already in `project-law.md` and enforced by the script |
| 3 | Rule 1 names `Fresh_Workspace_BMAD` as a top maintained project; de-listed 2026-08-07 (SCC-25) | **FIXED** — deleted with rule 1 |
| 4 | Rule 2 states the story-lane base only; Task lanes cut `chore/*` off `main` | **FIXED** — deleted; `worktree-per-story.md` carries both cases |
| 5 | `check_maps` check 8 asks only whether the redirect is PRESENT, and never reads a **root** adapter's body — so the broken file passed | **FIXED** — `test_entry_adapters.py`, fatal in `run_all` |
| 6 | Root `GEMINI.md`'s mandate was not even the house sentence, so the phrase test would have failed it too — if it had ever run at the root | **NOTED** — the same test now covers it |

---

## Preflight receipt + the flight event that could not be written

`task_preflight.py --fetch --repo <lane> --branch chore/SCC-279-gemini-adapter-fold --expect-key SCC-279`:

```
LANE: LOCAL
GATES: ARMED
VERDICT: clear to close out and merge
-- 0 error(s), 1 warning(s), 17 info --
```

The one warning is the lane's own worktree still being checked out — Step 5 prunes it. `preflight-receipt.json`
is committed here because `main-write-gate --mode pr` requires it.

⚠ `flight_recorder.py record` exited **2**: *"walkthrough.md carries no canonical `Verdict: ... @ <sha>` line
(fences stripped) — the event is keyed on that sha."* Correct refusal, and **the fourth lane in a row** to hit
it (SCC-267, SCC-269, SCC-271, this one). No LLM review runs on a quick-fix or lightweight lane, so no lane of
that class can ever produce the line the recorder keys on. A `record` failure never blocks a merge, and a
verdict line was **not** fabricated to satisfy it. The recorder is structurally blind to an entire lane class;
that is the recorder's contract to change, not this ticket's scope.

## Your Actions

- [x] The ruling — given, recorded verbatim, and followed (Door A, no Door B changes).
- [x] The fold, the three law documents, the SOP and its changelog — done and evidenced above.
- [x] The guard — written RED first, green after, in the armed suite.
- [x] The merge itself — lands via this branch's PR.

Nothing is owed. **SCC-262 (the parent) stays open** — it is the rolling home for the cycle, and closing
Part C does not close it. The **`_routing-canary` re-run** is still outstanding from SCC-269's change to
`router.md`; it is that ticket's cadence trigger, not this one's work.
