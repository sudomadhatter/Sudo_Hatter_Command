---
IsArtifact: true
ArtifactMetadata:
  title: Test-certification contract — audit of the optimization research + upgraded plan
  type: implementation_plan
  date: 2026-08-02
---

# Implementation Plan (v2) — Test-certification contract for the ②③ dev flow

**Status:** AWAITING EXECUTION APPROVAL · **Scope:** lobby rules + commands, 3 project layers
**Supersedes:** the v1 transcription of [plan_optimize-sudo-dev-story-tests.md](../../../_my_resources/open_tasks/plan_optimize-sudo-dev-story-tests.md)
**Method:** audited the research against disk + the measured 21.8b evidence; 10 findings, 4 material

---

## Part 1 — Audit of the research plan

### The evidence the research was written from

Real numbers, read today from the 21.8b walkthrough
([story-21-8b .../walkthrough.md:82-85](../../../Projects/AGY_AVIATIONCHAT/.claude/worktrees/story-21-8b-demo-data-quarantine/_artifacts/epic_21/story-21-8b-demo-data-quarantine/walkthrough.md)):

```
Story contract set      57 passed  (46 at ②; ③ added 11)
Full backend suite      3023 passed, 35 skipped, 0 failed  (278s) @ 64098847   ← ③'s run
                        ②'s 3012P @ 7423eadf was the entry baseline
Emulator E2E FULL-TREE  39 passed  (re-proven at ③)
Blast radius            760 passed, 9 skipped (②)
```

**One full backend suite = 278 s = 4.63 min, serial.** That single number governs everything below.

### Findings

| # | Finding | Severity |
|---|---|---|
| **A1** | **The plan's headline metric is contradicted by its own baseline story.** It claims ③'s inheritance is "silently dead — 0% hit-rate, SHA mismatch guaranteed." But 21.8b's walkthrough says ②'s pair *was* the entry baseline — ③ **did** inherit. The handshake wasn't dead; the agent noticed the staleness and paid a second full run in ② to make it valid. The defect costs **one extra full-suite run**, it does not void the ②→③ contract. | **Material — the fix is right, the justification is wrong** |
| **A2** | **The cost model is stated ②-only and never at system level.** "12.5 min → 6 min" is ② alone; ③ costs another 4.63 min on top. Per story the real figure is **≈17 min → ≈11 min**. And because ③ re-runs the full suite whenever it changes anything (in 21.8b it added 11 tests), **WS-A can never take a story below ~9.3 min of full-suite time.** That wall is not addressable by reordering. | **Material — budget the wrong number and the next optimization aims wrong** |
| **A3** | **WS-F defers the only lever larger than the entire plan.** Post-fix floor = 2 × 278 s serial. The `agy-xdist-tail-hang` follow-up is worth ~5–6 min/story if `-n auto` works — **more than WS-A saves, and it compounds.** The research bills the correctness fix as the efficiency project and files the efficiency project as out of scope. | **Material — inverted priorities** |
| **A4** | **F3 (delete the filtered emulator run) is billed as efficiency; it is worth 11.8 s.** Filtered 11.8 s vs full-tree 12.7 s — the "savings" is one second. It is a real *correctness* rule (only full-tree is citable, sibling conftests global-mock the tree). Keep it; stop counting it. | Minor — framing |
| **A5** | **The fix is prose in a command body, and the failure it fixes was an agent following prose.** Nothing makes a stale pair *detectable*. ③'s current check asks an LLM to eyeball *"totals are full-suite-shaped (count ≈ known suite size + this story's new tests)"* — a heuristic judgment on a number, in a step whose stated posture is "fail toward running, never toward trusting." A typed handoff makes it deterministic. | **Material — no enforcement layer** |
| **A6** | **WS-D propagates by copying — the same mechanism that produced the drift being fixed.** Three copies of one invariant (②, ②_AP, prose in ③) guarantee the next drift. The system already has a rules layer: [tests-must-gate-for-real.md](../../../.agents/rules/tests-must-gate-for-real.md) is **byte-identical (3,853 B) across the lobby and all three projects.** One rule, referenced three times, beats three copies. | **Material — structural** |
| **A7** | **Body growth is real but self-solving, and A6 sidesteps it.** `sudo-dev-story-tests.md` = 10,942 B; [sync-agents.ps1:385](../../../.agents/scripts/sync-agents.ps1#L385) emits a thin launcher above 11,500 B. v1's +1.8 KB crosses it (harmless — `update-maps-indexes` is 39 KB and works). Under A6 the command grows ~4 lines and stays under. | Minor — resolved by A6 |
| **A8** | **The Suite Ledger is self-reported telemetry authored by the agent whose waste it measures.** An agent that hedge-ran writes its own "why this run" column. Keep it — cheap, and the discipline of writing a why does deter hedging — but do not treat it as measurement, and scope it per **story** (②+③), not per command. | Minor — scope it honestly |
| **A9** | **The mobile lane owes nothing.** `prompt3` in `autopilot_mobile.workflow.js` never consumes the (totals, SHA) pair, and the orchestrator gates the `review` flip on its own independent run. Its missing automate step is a real drift — but a *separate* one, and adding it would grow the pipeline, not optimize it. Correctly dropped. | Confirms the operator's call |
| **A10** | **One unstated invariant.** After the certification run, **only artifact/doc files may change.** v1 implies it twice; ③ already encodes it. State it once, in the rule. | Minor |

### What survives the audit

The core fix is **correct and worth doing** — Step 3's full-suite mandate genuinely precedes the step that
adds tests, the `_AP` twin genuinely has the right order, and following the spec literally genuinely
produces a stale pair. What changes is the *justification* (A1), the *accounting* (A2), the *priority
order* (A3), and the *delivery mechanism* (A5, A6).

---

## Part 2 — The upgraded plan

### Design change vs v1, in one line

> v1 wrote the invariant into two command bodies and hoped agents follow it.
> **v2 writes it once into the rules layer, and makes ③'s check mechanical instead of a judgment call.**

### R1 — `tests-must-gate-for-real.md` gains **Rule 4: certification is measured at the shipping SHA**

The single source. One file, already byte-identical across the lobby + AGY + Fresh + NEXgen, already read
by ①, ②, ③, and the autopilot lanes. New Rule 4 carries:

- **Feedback ≠ certification.** Scoped + blast-radius runs are feedback (cheap, early, at maximum
  uncertainty). The full suite is certification — exactly one legitimate moment: the final code SHA.
- **The (totals, SHA) pair is a contract, not decoration.** Totals MUST come from a run at exactly the SHA
  named. Any code or test change after that run voids it. **Artifact/doc-only changes are exempt** (A10).
- **Only citable forms count.** E2E tier → the FULL-TREE emulator run; `-k`/single-file runs are debug-only,
  never citable (sibling conftests global-mock the tree).
- **Mutation proof:** a structural red is a wiring proof, never a behavior proof. Prove a new behavioral
  test non-vacuous by **RELOCATING** the guard (structural reds stay green; only the new test fires), never
  by deleting it (kills both, isolates nothing). Every scenario needs a **positive control**.

Cost: ~18 lines in one file. Replaces ~35 lines that v1 would have spread across two command bodies.

### WS-A — Reorder ② *(the core fix, unchanged in substance)*

**File:** [.agents/commands/sudo-dev-story-tests.md](../../../.agents/commands/sudo-dev-story-tests.md)

- **A1 — Step 3 (Implement):** delete the full-suite mandate. Scoped suites while iterating + one targeted
  **blast-radius pass** over the suites the changed files share. Explicit: *"Do NOT run the full suite here —
  Step 4 adds tests, which stales any totals produced now. Step 4.5 owns the one certification run."*
- **A2 — new Step 4.5 (Certify at the shipping SHA)**, between Automate and Close-out:
  1. Machine floor once over the final changed-file set (ruff + pyrefly — both HARD gates lint whole files,
     so inherited debt in touched files is yours). `--fix` altered something → re-run the story contract set.
  2. Commit (explicit paths, never `git add -A`).
  3. **ONE full-suite run per touched stack**, per **Rule 4**.
  4. Emit the certification block (WS-G) + paste the real output.
  5. Finalize the automate summary's suite-result line so both artifacts carry the same pair.
  - Red at step 3 → fix, re-commit, re-run. The loop is expected; only the *last* run is the certification.
- **A3 —** the "(totals, SHA) is ③'s entry baseline" paragraph moves from Step 3 into Step 4.5.

Net body change: **≈ +10 lines** (v1 was ≈ +25), because the invariants live in Rule 4 and Step 4.5
references them.

### WS-G — **NEW: typed certification handoff** *(the enterprise layer — answers A5)*

Today ③ decides whether to trust ②'s green by eyeballing prose. Replace it with a machine check.

② Step 4.5 writes `_bmad-output/test-artifacts/certification-<story>.json`:

```json
{ "story": "21.8b", "sha": "7423eadf…", "utc": "…",
  "stacks": { "backend": { "cmd": "…", "passed": 3012, "skipped": 35, "failed": 0, "seconds": 278 },
              "emulator": { "cmd": "… -m emulator", "passed": 39, "failed": 0, "seconds": 13 } } }
```

③ Step 3's inheritance test becomes deterministic — **read the file, compare `sha` to
`git rev-parse HEAD`.** Match → inherit. Absent or mismatched → run the full suite. No heuristic on
"full-suite-shaped totals," no prose parsing, and the artifact is greppable by a future hook.

**Tier-1 fallback if the JSON reads as machinery:** a fixed-format fenced `CERTIFICATION` block in the
walkthrough with the same fields. Deterministic to grep, zero new file types. Weaker (a hook can't validate
it as easily) but ~80% of the value at ~20% of the cost.

### WS-B′ — automate custom layer (all three projects, per your call)

One `persistent_facts` entry — the mutation-proof rule, pointing at Rule 4 — appended to
`_bmad/custom/bmad-testarch-automate.toml` in **AGY_AVIATIONCHAT, Fresh_Workspace_BMAD, NEXgen-VR-Director**,
so automate runs *outside* the ② wrapper carry it too. ~4 lines each.

### WS-C′ — Suite Ledger, honestly scoped (A8)

A `## Suite Ledger` section in the walkthrough — `scope · command · duration · result · why this run` — kept
**per story across ② and ③**, not per command. ③ appends its rows to ②'s table. Framed as a discipline
device (a hedge run needs a written why), **not** as measurement.

### WS-D′ — propagation, shrunk (A6, A9)

1. `sudo-dev-story-tests_AP.md` — order already correct; add **one line** referencing Rule 4 in its stage 4
   + the Suite Ledger in its stage 5. (v1 wanted three content blocks ported.)
2. `sudo-code-review.md` Step 3 — replace the "full-suite-shaped totals" heuristic with the WS-G check.
3. Rule 4 propagated to all three projects' `.agents/rules/` (they are byte-identical today — keep them so).
4. `/sync-agents` → four platforms; verify `.sync-manifest.json`; confirm the old Step-3 phrasing greps to
   zero across masters + mirrors.
5. **Mobile lane: no edits** (A9). Its missing automate step is filed as a separate follow-on, not fixed here.

### WS-E′ — corrected targets (A1, A2)

| Metric | 21.8b actual | After WS-A+G | Note |
|---|---|---|---|
| Full-suite runs in ② | 2 | **1** | the actual fix |
| Full-suite runs per story (②+③) | 3 | **2** | ③'s exit run is mandatory whenever ③ changes anything |
| ② test wall-clock | ~12.5 min | **~6 min** | v1's target — correct, and correctly labeled ②-only |
| **Per-story test wall-clock (②+③)** | **~17 min** | **~11 min** | the number to budget — v1 never stated it |
| ③ entry-run skip | worked, at the cost of a hedge run in ② | works by construction | A1: this was never 0% |
| Stale-totals walkthrough | reachable by following the spec | structurally unreachable | |
| Coverage | — | **unchanged** | every cut is a duplicate or a stale-order artifact |

**Decision rule (v1 had none):** >1 mandated full-suite run in ② on the next story is a **defect against the
command**, filed as such — not a note in a retro.

### WS-F′ — **promoted: xdist is the efficiency project** (A3)

After this plan the floor is 2 × 278 s serial ≈ 9.3 min/story of pure certification. `agy-xdist-tail-hang`
(~8 tests hang only under `-n auto`) is worth **~5–6 min/story** — more than this entire plan — and it
compounds with it. Recommendation: **this plan is the correctness fix; the xdist hang is the next
optimization, and it should be scheduled, not just tracked.**

---

## Files touched

| File | Change | Repo |
|---|---|---|
| [.agents/rules/tests-must-gate-for-real.md](../../../.agents/rules/tests-must-gate-for-real.md) | +Rule 4 (~18 lines) | lobby → all 3 projects |
| [.agents/commands/sudo-dev-story-tests.md](../../../.agents/commands/sudo-dev-story-tests.md) | Step 3 rewrite, +Step 4.5, +Ledger (~+10 lines) | lobby |
| [.agents/commands/sudo-dev-story-tests_AP.md](../../../.agents/commands/sudo-dev-story-tests_AP.md) | 2 reference lines | lobby |
| [.agents/commands/sudo-code-review.md](../../../.agents/commands/sudo-code-review.md) | heuristic → WS-G check | lobby |
| `Projects/{AGY,Fresh,NEXgen}/_bmad/custom/bmad-testarch-automate.toml` | +1 `persistent_facts` entry | 3 project repos |
| all mirrors | via `/sync-agents` | — |

**Not touched:** `autopilot_mobile.workflow.js` (A9), any product code, any story file.

## Execution order

1. **R1** — Rule 4 into `tests-must-gate-for-real.md` (lobby master).
2. **WS-A + WS-C′** — one edit pass on `sudo-dev-story-tests.md`.
3. **WS-G** — certification block/JSON spec into ② Step 4.5 **and** ③ Step 3 (both sides in the same pass —
   a one-sided handoff is worse than none).
4. **WS-D′** — twin reference lines; propagate Rule 4 to the three projects; `/sync-agents`; verify.
5. **WS-B′** — the three toml one-liners.
6. Commit per repo (lobby + 3 projects, separately). Ad-hoc non-story work → `main_debug` directly, no
   worktree (`worktree-per-story`). AGY has a live 21.8b lane — touch only the named files, never sweep.

## Verification

- `grep -c "full-suite"` in ② → confined to Step 4.5.
- Dry-run Step 3→4→4.5 against the 21.8b transcript: stale path unreachable; mandated full-suite count = 1
  in both automate branches (adds tests / skipped).
- **WS-G round-trip:** hand ③ a certification block whose SHA ≠ HEAD → it must run the full suite. SHA ==
  HEAD → it must inherit. Both directions, or the handoff is decorative.
- Twin diff clean on shared content; Rule 4 byte-identical in all four locations.
- Post-sync: new body present in `.claude/`, `.opencode/`, `.agents/workflows/`, Antigravity + Codex caches;
  `sudo-dev-story-tests.md` still **under 11,500 B** (verify — if it crosses, the launcher takes over and
  that is fine, just confirm the launcher generated).
- Old Step-3 phrasing greps to zero repo-wide (worktrees excepted — frozen copies, pruned at close-out).

## Risks

| Risk | Mitigation |
|---|---|
| Collateral surfaces later (full suite moved after automate) | Blast-radius pass stays in Step 3 — in 21.8b it ran 760 tests in 43 s and caught everything the full run later confirmed, at the point of maximum uncertainty. Certification was never the fast-feedback tool. |
| WS-G lands one-sided (② emits, ③ ignores) | Step 3 of execution does both in one pass; the round-trip verification tests both directions. |
| Rule 4 drifts across the four copies | They are byte-identical today; `/sync-agents` + the living-template rule keep them so. A diff check is in verification. |
| Agents hedge-re-run anyway | Explicit "do NOT re-run what the certification run subsumes" + a Ledger row that needs a written why. |
| Per-story cost still ~11 min | Acknowledged, not hidden (A2). WS-F′ names xdist as the owner of the remaining floor. |

**Rollback:** `git revert` per repo + re-sync. No product code touched; per-story behavior reverts with the
rule + command bodies.

## Open question

**WS-G tier** — the JSON file (deterministic, hook-checkable, one new artifact type) or the fenced
`CERTIFICATION` block in the walkthrough (no new file, ~80% of the value)? Recommend **JSON**: it is the
piece that converts this from "better prose" into an enforced contract, and it is ~15 lines of spec, not code.
