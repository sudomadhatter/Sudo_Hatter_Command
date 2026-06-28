# Implementation Plan — Autopilot concurrency-safe ("run as many stories as I want")

**Date:** 2026-06-27
**Author:** Claude (home base)
**Status:** AWAITING APPROVAL (plan-first gate — no files edited yet)
**Bucket:** `_artifacts/_main/` (cross-project toolkit + per-project script work)

---

## 0. Problem (from Daniel's root-cause writeup)

Two `/autopilot_claude` runs (stories 14-7 and 14-8) ran at once and collided. Two independent breaks:

- **RC#1 (cosmetic, monitoring):** every run streams its transcript to the SAME hardcoded global log
  `_artifacts/_autopilot-run.log`, so the live tail cross-wired 14-8's stages onto 14-7.
- **RC#2 (the run-killer):** two concurrent headless `claude -p` processes raced on the CLI's **shared
  internal global state** under `~/.claude`. 14-7's Stage 1 got a corrupted/truncated prompt, wrote no
  `implementation_plan.md`, and the orchestrator's **soft** artifact check (`! WARNING`, then continue)
  marched on to Stage 2 with nothing to audit — burning spend on garbage.

**Proven:** session ids were ALREADY unique per run (`autopilot-14-7-dev` ≠ `autopilot-14-8-dev`) and it
still corrupted → tagging *our* identifiers is necessary but NOT sufficient. The race is on the CLI's
private store at a fixed path we don't control.

## 1. Organizing principle — the story id is the one isolation key (Daniel's "tag by story")

The workflow always has a unique story, so the story id `<id>` (e.g. `14-7`) is the natural tag. We thread
it through ALL four surfaces — including the CLI's hidden state, which is the part session-id tagging
missed:

| Surface | Today | After | Fixes |
|---|---|---|---|
| Global live-tail log | `_artifacts/_autopilot-run.log` (shared) | `_artifacts/_autopilot-run-<id>.log` | RC#1 |
| Per-run lockfile | none | `<temp>/autopilot-cli-home/<id>` + `_pipeline/.run.lock` (PID) | double-run |
| **CLI config home** | global `~/.claude` (shared → races) | `CLAUDE_CONFIG_DIR=<temp>/autopilot-cli-home/<id>` | **RC#2** |
| Session ids | already `autopilot-<id>-dev/-qa` | unchanged (already tagged) | — |

Run folder, `_pipeline/run.log`, `_RUN-STATUS.md`, `sessions.json` are ALREADY per-run/isolated — no change.

## 2. Decision (approved direction)

Daniel chose Option 1 but deferred to my call for production quality. **Decision: target full per-run
`CLAUDE_CONFIG_DIR` isolation (Option 2), gated behind an empirical probe**, with Option 1's startup mutex
kept ONLY as a fallback if the probe is inconclusive. Rationale: a startup-only mutex fixes the *launch*
race but NOT a race on the CLI's shared session store *during* a run; per-run config home is the only
mechanism that isolates the whole lifecycle — required for true "N at once."

## 3. Scope — all three surfaces ("all 3 repos")

1. **Skill (master + synced copies):** `.agents/commands/autopilot_claude.md` → edit master, then
   `/sync-agents` propagates to `.claude/commands/` (home base) + both projects' `.agents/`+`.claude/`
   copies. This is the "main one" — the home base carries the **skill**, not a script (autopilot scripts
   live per-project).
2. **AGY script:** `Projects/AGY_AVIATIONCHAT/scripts/autopilot-dev-story.ps1` (1057 lines, current).
3. **Fresh script:** `Projects/Fresh_Workspace_BMAD/scripts/autopilot-dev-story.ps1` (809 lines, older
   variant; **lacks `Set-WorkspaceTrust`** — trust seeding adapted accordingly).
4. **Minor docs:** `*/autopilot_bmad_dev_loop.md` references to the global log path (cosmetic; update).

> The two scripts have DIVERGED. Concurrency-relevant pieces (`Assert-Artifact`, the `& $Claude` call,
> guid session minting, `Add-RunLog`) are structurally identical; edits map cleanly at different line
> numbers. **Flag (out of scope):** reconcile both to one canonical `.agents/scripts/` script later.

## 4. The fixes

### Step 0 — PROBE first (no production edits until this passes) [E]
Throwaway script in scratchpad. Confirm on THIS machine:
1. With `CLAUDE_CONFIG_DIR=<fresh seeded dir>`, `claude -p "reply OK" --output-format json` **authenticates**
   and returns (no login prompt). Seed = copy `~/.claude/.credentials.json` (+ `~/.claude.json`, `settings.json`).
2. Workspace **trust** is honored (no "workspace not trusted" gate) for the project cwd.
3. `--session-id` then `--resume` works **within** the dir.
4. Sessions land under `<dir>/projects/...`, NOT `~/.claude/projects/...` (proves real isolation).
- **If 1–4 pass →** implement Section 4.B as written.
- **If `.claude.json`/trust does NOT relocate →** drop trust-seeding (global trust suffices), keep the rest.
- **If credentials do NOT relocate / auth breaks →** FALL BACK to Option 1: global startup mutex around
  each `& $Claude` spawn + lock-only, and skip config-dir isolation.

### A — Per-story global log (skill) [RC#1]
In the Monitor command, derive a filesystem-safe slug from `$ARGUMENTS` at bash runtime and use it:
```
S=$(printf '%s' "$ARGUMENTS" | tr -c 'A-Za-z0-9' '-' | sed 's/--*/-/g; s/^-//; s/-$//')
LOG="_artifacts/_autopilot-run-$S.log"; powershell.exe -NoProfile -File scripts/autopilot-dev-story.ps1 -Story "$ARGUMENTS" > "$LOG" 2>&1 & APID=$! ; tail --pid=$APID -f -n +1 "$LOG" | grep ...
```
Update the `description:` line and every prose mention of `_artifacts/_autopilot-run.log` in the skill
(and the two `autopilot_bmad_dev_loop.md` docs) to the per-story form.

### B — Per-run `CLAUDE_CONFIG_DIR` isolation (both scripts) [RC#2 core]
At startup (after `$RepoRoot`/`$storyId` resolve, before any `claude` call):
- `$CliHome = Join-Path $env:TEMP ("autopilot-cli-home\" + $storyId)` — **OS temp, NOT under `_artifacts/`**
  (which is git-TRACKED; we must never risk committing the copied OAuth token). Per-story → isolated
  between stories; stable across resume of the same story → sessions persist.
- Seed once (idempotent): copy `~/.claude/.credentials.json`, `~/.claude.json`, `~/.claude/settings.json`
  into `$CliHome` if present. Then ensure the project key is trusted in `$CliHome/.claude.json` (reuse the
  `Set-WorkspaceTrust` splice, retargeted to `$CliHome`; ADD that helper to the Fresh script which lacks it).
- `$env:CLAUDE_CONFIG_DIR = $CliHome` for the orchestrator process → all `& $Claude` children inherit it.
- The existing `Set-WorkspaceTrust -ProjectPath $RepoRoot` against `~/.claude.json` stays (harmless; covers
  the fallback path).

### C — Hard-fail on a missing handoff artifact (both scripts) [RC#2 defense-in-depth]
Change `Assert-Artifact` (stages 1–3) from a `! WARNING` + continue into a **hard `throw`**, so a missing
`implementation_plan.md` / `self-audit-stress-test.md` / `walkthrough.md` lands in the existing CRASHED
catch (stamps `_RUN-STATUS.md` CRASHED, exits 3, **resumable** — finished stages auto-skip). Keep the
helpful "landed under another name? rename it" hint in the throw text. Stage 4's `code-review.md` keeps its
existing dedicated REVIEW-INCOMPLETE handling (exit 6). This alone would have stopped 14-7 at Stage 1.

### D — Per-story lock (both scripts) [stopgap + double-run guard]
On real-run startup: write `$Folder/_pipeline/.run.lock` = this `$PID`. If it exists AND its PID is a live
process AND ≠ ours → another run for THIS story is active → **refuse** with a clear message (new exit code,
e.g. 7). Stale PID (dead) → reclaim. Remove the lock in the `finally`/on normal exit. Prevents the same
story double-running; different stories are isolated by Section 4.B and run freely in parallel.
- (Conditional) Global startup mutex around `& $Claude` — added ONLY on the probe's fallback branch.

### E — Verification (post-edit)
Launch two stories concurrently `-MaxStage 1` (a real cheap story + a second). Assert: each
`_pipeline/run.log` contains ONLY its own story id; each `_artifacts/_autopilot-run-<id>.log` is separate;
each Stage 1 wrote a real `implementation_plan.md`; sessions landed in separate `$CliHome/projects/...`
dirs. Capture as a short note (optionally a committed smoke check).

## 5. Risks
- **Undocumented `CLAUDE_CONFIG_DIR`** — mitigated by Step 0 probe + explicit fallback to Option 1.
- **OAuth token copied to temp** — confined to OS temp (never `_artifacts/`, which is tracked); acceptable,
  it's the user's own credential on their own machine.
- **Script divergence (AGY vs Fresh)** — edits adapted per file; Fresh needs `Set-WorkspaceTrust` added.
- **Hard-fail (C) changes behavior** — runs that previously limped on a mis-named artifact now CRASH
  (resumable). This is the intended, safer behavior.

## 6. Out of scope (flagged for later)
- Reconciling the two divergent project scripts into one canonical `.agents/scripts/` source.
- Any change to the BMAD `_AP` stage commands themselves.

## 7. Order of work (on approval)
1. Step 0 probe → confirm/branch. 2. Skill (A) + `/sync-agents`. 3. AGY script (B, C, D).
4. Fresh script (B, C, D + add `Set-WorkspaceTrust`). 5. Verification (E). 6. Hand back to Daniel
   (no commit — pipeline + Daniel's git policy own that).

---

## 8. VERIFICATION RESULTS + CORRECTED ROOT CAUSE (2026-06-27, post-implementation)

**What shipped (all 3 repos, on disk + auto-committed by an automation during the session):**
- A per-story log, B per-run `CLAUDE_CONFIG_DIR`, C hard-fail-on-missing-artifact, D per-story lock
  (hardened to PID+start-time to defeat PID reuse), plus a self-heal for the stage-log write.

**Probe (Step 0): PASSED** — seeded per-story `CLAUDE_CONFIG_DIR` authenticates, is trusted, isolates
sessions to TEMP (`~/.claude/projects` stayed at 145), and resumes. So B works as designed.

**Concurrent pipeline test (14-7 + 14-9, both real Stage 1): exposed the TRUE root cause.**
- 14-7's Stage-1 `claude` call **succeeded** (`is_error=false`, 10 turns, $0.59) but wrote **no plan**.
  The persisted session transcript shows the delivered prompt was **truncated to 1204 chars, ending
  mid-word at "A soft I"** — the *exact* cut point named in the original incident. The agent received
  only a partial team-preamble (no `/bmad-dev-story_AP plan`, no "You are Amelia", no story id) and
  wandered off "getting oriented with the run state" instead of planning.
- **RC#2 is PROMPT TRUNCATION under concurrent `claude -p`, NOT shared `~/.claude` state.** The config
  dirs were fully isolated and it STILL truncated → the original spec's RC#2 hypothesis was incomplete.
- **C (hard-fail) caught it cleanly** → CRASHED + resumable, no march-forward, no wasted downstream
  spend. This is the practical win: concurrency is now **SAFE**.
- A cheap haiku probe could NOT reproduce the truncation (intermittent race; only surfaced under two
  heavy concurrent Opus runs), so `-p`-arg vs stdin was **inconclusive**.

**Net status:** concurrent autopilot runs are now **SAFE** (no silent garbage, clean crash + cheap
resume) but not yet 100% **RELIABLE** — a concurrent stage can still occasionally get a truncated prompt
and need a re-run.

## 9. PHASE 2 — make it reliable (proposed, needs go-ahead + a little test spend)
1. **Auto-retry on no-artifact (in our control, recommended).** In `Invoke-Stage`, if the `claude` call
   returns success but the stage's expected artifact is absent, treat it like a transient error and
   RETRY within the existing `-MaxRetries` loop (re-mint the session id for new-session stages 1/2 to
   avoid `--session-id` collision). Turns an intermittent truncation into a transparent retry that
   almost always lands on the next attempt. Pairs with C (C becomes the last-resort stop after retries).
2. **stdin prompt delivery (likely the actual cure).** Pass the prompt via a per-process STDIN pipe
   (`$prompt | & $Claude -p ...`) instead of a giant `-p <arg>`; a per-process pipe has no shared path
   to truncate. Architecturally sound; needs a concurrent repro to confirm.
3. Verify either/both with a 2–3× concurrent `-MaxStage 1` repro.

## 10. Heads-up (not a fix)
- An automation committed these edits to `main_debug` in the AGY + home-base + Fresh repos mid-session
  (commits authored "Daniel Lohn", ~20:29, e.g. AGY `ba87cf6`, home-base `6b6323a`). My edits are
  committed cleanly + consistently (working trees match HEAD), but flag whether that auto-commit/push
  to `main_debug` is intended.
- Test API spend: ~$1.5–2 (probe + two concurrent Stage-1 runs).
