---
IsArtifact: true
ArtifactMetadata:
  title: "SCC-416 — Decide the epic's mode at kickoff; freeze main for a live epic's scope"
  type: walkthrough
  date: 2026-09-05
---

# Walkthrough — SCC-416

**Ticket:** [SCC-416](https://sudo-command.atlassian.net/browse/SCC-416) · **Lane:** `chore/SCC-416-in-flight-epic-freezes-main` off `origin/main` @ `f0dcb423` · **Shipping SHA:** `5d5d7f41` · **Plan:** [implementation_plan.md](implementation_plan.md) (v3, the operator's design, trimmed on his instruction) · **Door:** `/smh-close-task-merge-tree`

**What this is.** On 2026-09-05 Epic 24 work reached live production mid-epic: `chore/AVCH-80-rolling-bugs`, cut off `main`, shared three runtime files with the live `epic/AVCH-100-epic-24-agent-quality`, and both preflights judged it by its own diff against `PRODUCT_DIRS` — "chore touching backend → light gate → clear to ship" — never once listing `origin/epic/*`. `/cicd-push-e2e` opened PR #72, it merged at `4afaa667`, and Cloud Run revision `00076-boh` took 100% of traffic at 19:13:59 UTC. The operator's ruling forbidding exactly this (2026-09-03) sits in the Epic 24 banner of `sprint-status.yaml` **on the epic branch**, unreadable from a main-bound lane; that plan's lobby-side guard — "Lane 2" — was never started. This lane is Lane 2, plus the operator's own design on top of it: the epic's mode is decided once, at kickoff, and carried in the branch name.

## Task Checklist

- [x] Reproduce: the six-file overlap measured (`comm -12` of the two `git diff --name-only` lists), the two preflight code paths read, the ruling located on the epic branch
- [x] `task_preflight.live_epic_branches()` + `epic_freeze()` — product-file intersection of a lane's diff with each live epic's `base...ref` diff; a clean run says it checked
- [x] `check_scope` (Task door) calls it BEFORE the deployable handoff — epic work is never named for `/cicd-push-e2e`
- [x] `check_lane` (production door) calls it BEFORE the light-gate return
- [x] Tests RED first, then GREEN, then the five-mutant revert-proof
  - the Task twin's *"does NOT hand epic work to the production door"* failing on the unfixed tree IS the incident, reproduced as a test
  - M1 was a SWEEP ERROR on the first pass, not a survivor: dropping the ship door's `return` is not un-refusing — `rep.err` alone already blocks — so only the ORDER case died (M5's kill). Re-aimed at the decision that carries the refusal (`rep.err → rep.info`); 5/5 on the second sweep
- [x] The incident replayed against the fixed gate, read-only, in a scratch clone frozen at the pre-merge state — BLOCKED, naming the epic and the three files
  - the first two replays read 0 files: the preflight fetches, and a fetch from the real repo reset the clone's `origin/main` to the post-merge tip, so the merged lane correctly diffed to nothing. The fixture now fetches from a bare origin I froze at `7c973b99`
- [x] `cicd-create-epic-sprint.md` — the kickoff question and the `-quickdev` name it produces
- [x] `cicd-close-story-merge-tree.md` Step 3 — two arms keyed on the name: direct push (quick-dev) or PR into the epic + four checks + merge (extension of main)
  - measured while writing it: the door's existing direct push is refused on Epic 24 today by the AVCH-119 ruleset; the PR arm is what makes Epic 24's story landings work again
- [x] `git-policy.md` — one subsection: the two modes, the switch, the freeze
- [x] `cicd-push-e2e.md` Step 1 — one sentence: the diff decides the GATE, not the DESTINATION
- [x] SOP §7 chore admission, the kickoff paragraph, the two §5 refusal rows; changelog row — same commit, sop-currency gate passed without an opt-out
- [x] `run_all.py` 77/79 → 79/79: the two reds were this lane's own bookkeeping (three `.opencode/` mirrors of the edited doors, and the ledger row), closed in `5d5d7f41`
- [ ] Operator: the merge — see `## Your Actions`

## Evidence

| Row (plan §3) | Check | Proof |
|---|---|---|
| A | `ship_preflight` on a `chore/*` sharing a product file with a live epic → exit 2, `VERDICT: BLOCKED`, names the epic, the files, the story door | SP-Q.1 — 7 checks, RED then GREEN |
| B | `task_preflight` same lane → exit 2 `HANDOFF` naming the story door, never `/cicd-push-e2e` | task twin — 5 checks |
| C1 | live epic, no overlap → unchanged, says `1 live epic branch(es) checked, no product-file overlap` | SP-Q.2 + twin control |
| C2 | no live epic → unchanged, `0 live epic branch(es) checked` | SP-Q.3 |
| C3 | the epic branch itself → full gate, untouched by a sibling epic on the same file | SP-Q.3b |
| D | a remote-only epic counts | SP-Q.4; mutant M3 kills on it |
| E | overlap only on a non-product path → not refused | SP-Q.5 |
| G | a merged-but-unpruned epic → no false hit | SP-Q.6 |
| H | the incident replayed on the real repo's history, read-only | below |
| I | revert-proof | Suite Ledger — 5/5 killed, restore verified |
| J | `run_all.py` green; sop-currency gate passed | `79/79 files passed` @ `5d5d7f41`; commit `d7c4122e` landed without `[sop-ok]` |
| K | the two doors read the mode from the name and nothing else | `cicd-create-epic-sprint.md` cut block; `cicd-close-story-merge-tree.md` Step 3, two arms keyed on `*-quickdev` |

### Row H — the incident, replayed against the fixed gate

Scratch clone of `Projects/AGY_AVIATIONCHAT` with its origin re-pointed at a bare copy frozen at the pre-merge state (`origin/main` = `7c973b99`, `origin/chore/AVCH-80-rolling-bugs` = `ecc3fc09`, `origin/epic/AVCH-100-epic-24-agent-quality` = `7db01108`). Nothing in the real repo was written. The fixed `ship_preflight.py`, invoked exactly as `/cicd-push-e2e` Step 1.5 invokes it:

```
== ship preflight - chore/AVCH-80-rolling-bugs ==
[INFO ] branch: chore/AVCH-80-rolling-bugs -> AVCH-80 (chore lane)
[INFO ] intent: AVCH-80 matches the branch key
[INFO ] sync: chore/AVCH-80-rolling-bugs: on origin, not checked out here - Step 2's checkout creates the local ref from origin, so there is nothing unpushed
[ERROR] lane: EPIC WORK: 3 file(s) this lane changes are ALSO changed on the live epic epic/AVCH-100-epic-24-agent-quality: backend/agents/admin/agent.py, backend/agents/specialist/agent.py, backend/tools/librarian.py. While that epic is in flight, main is FROZEN for its scope. STOP. Cut claude/<KEY>-<slug> off origin/epic/AVCH-100-epic-24-agent-quality and land it with /cicd-close-story-merge-tree - never /cicd-push-e2e, never this door.
-- 1 error(s), 0 warning(s), 7 info --
VERDICT: BLOCKED - nothing may be gated, merged or pushed until these are fixed
```

That is the sentence the morning's run needed. The same lane, the same door, the same files — refused before the gate ran.

### What was NOT built, said plainly

A brand-new file in the epic's subsystem that the epic has not touched is not caught by file-level overlap; the kickoff decision and the story-door arm are the answer to that, not more machinery. No constitution clause, no branch-cut nudges in the three quick doors, no "CI green is not tested" paragraph in the rule, no `hotfix:` carve-out, no push-time hook — all cut on the operator's instruction to keep what is real to the system. Nothing in `Projects/` was written.

## Suite Ledger

| When | What | SHA | Result |
|---|---|---|---|
| RED | `test_ship_preflight.py --case SP-Q` on the unfixed tree | `da5a0d8c` | **4/16** — the passes are the controls that already hold; SP-Q.1 fails on `light gate … clear`, exit 0 |
| RED | `test_task_preflight.py --case SCC-416` on the unfixed tree | `da5a0d8c` | **3/7** — *"does NOT hand epic work to the production door"* FAILS: today it does |
| GREEN | the same two filtered runs | working tree → `d7c4122e` | **16/16** · **7/7** |
| full | `test_ship_preflight.py`, unfiltered | `d7c4122e` | **118/118** |
| full | `test_task_preflight.py`, unfiltered | `d7c4122e` | **116/116** |
| sweep 1 | `mutation_sweep.py` — 5 declared mutants | `d7c4122e` | 4 KILLED; M1 **SWEEP ERROR** (died by the wrong case — see checklist); restore verified |
| sweep 2 | the table with M1 re-aimed (`rep.err → rep.info`) | `d7c4122e` | **5/5 KILLED by their named case** — M1 by `SP-Q.1 … -> exit 2`, M2 by `does NOT hand epic work to the production door`, M3 by `SP-Q.4 remote-only`, M4 by `SP-Q.2 … SAYS it checked`, M5 by `SP-Q.1 … BEFORE the surface decision`; restore verified bytes + `git diff --quiet`; closing full runs 118/118 · 116/116 |
| enforcement | `run_all.py` | `d7c4122e` | 77/79 — `test_command_surfaces` (3 stale `.opencode/` mirrors of the edited doors) and `test_check_maps` (no ledger row for this folder) |
| enforcement | `run_all.py` after the sync + ledger row | `5d5d7f41` | **79/79 files passed** · `test_command_surfaces` 317/317 · `test_check_maps` green |
| replay | `ship_preflight.py` on the frozen AGY clone, `--branch chore/AVCH-80-rolling-bugs` | code `d7c4122e` | **BLOCKED — EPIC WORK, 3 files, epic named** |

### Mutation table (record)

| Mutant | File | Decision mutated | Named case | Outcome |
|---|---|---|---|---|
| M1 | `task_preflight.py` | INVERT the refusal: `rep.err` → `rep.info` in `epic_freeze` | `SP-Q.1 overlap with a live epic -> exit 2` | KILLED |
| M2 | `task_preflight.py` | INVERT the Task door's short-circuit (drop `return "HANDOFF"`) | `...and it does NOT hand epic work to the production door` | KILLED |
| M3 | `task_preflight.py` | NARROW: remote-only epics dropped (`if not remote and …`) | `SP-Q.4 a remote-only live epic still refuses` | KILLED |
| M4 | `task_preflight.py` | DELETE the "N live epic branch(es) checked" line | `SP-Q.2 ...and it SAYS it checked the live epic` | KILLED |
| M5 | `ship_preflight.py` | RELOCATE the guard below the light-gate line | `SP-Q.1 ...and the refusal came BEFORE the surface decision` | KILLED |

## Your Actions

- [ ] **The merge itself — lands via this branch's PR.** Lobby only; no deploy surface. The guard is live in every door the moment it merges.
- [ ] **AviationChat, after recovery, on your call — its own AVCH tickets, none of it touched here:** (1) the decision on `4afaa667` — revert on `main`, and re-land the AVCH-80 fixes on the epic as a story; (2) the AVCH-119 ruleset gains `exclude: refs/heads/epic/*-quickdev` (one API call) so quick-dev epics pay nothing; (3) `pr-check-skip.yml` lands on `main` — today it lives only on `epic/AVCH-100`, so a fresh epic's docs-only story PR is unmergeable; (4) a throwaway probe of `git push -u origin epic/…` under the ruleset's enforce-on-create, because the only live epic predates it; (5) **AVCH-80's ticket, riders AVCH-120/121/122, the `avch-80-rolling-bugs` worktree and the branch** — their right state depends on (1), which is why they are not moved here.
