# Implementation Plan — Harden `/sudo-dev-story-tests` test execution (accuracy + efficiency)

**Status:** PROPOSED — awaiting operator review, nothing edited yet
**Date:** 2026-08-02 · **Scope:** lobby toolkit (`.agents/commands/`) + one AGY custom layer
**Baseline evidence:** the story 21.8b ② run — 15 suite invocations, ~12.5 min test wall-clock, 2 full-suite runs, 1 stale-totals near-miss

---

## Why now — the retro found a spec bug, not just waste

The 21.8b retrospective measured **~55% of test wall-clock as redundant**, and nearly all of it
traces to one ordering flaw in the command spec:

> Step 3 mandates "ONE full-suite run per touched stack … paste totals + `git rev-parse HEAD`"
> **before** Step 4 (`bmad-testarch-automate`) — whose entire job is to add tests.

Follow the spec literally and the walkthrough carries totals **measured at a SHA that no longer
exists** the moment automate lands its expansion. That is an accuracy defect wearing an
efficiency costume, and it has a second, structural cost found during recon:

**③ (`sudo-code-review` Step 3) is already SHA-strict.** It inherits ②'s green *only when the
pasted SHA equals the HEAD under review* — "Missing, partial, or SHA-mismatched → run the full
suite up front yourself." Under the current ② ordering, the SHA can never match whenever
automate adds a test. So the ②→③ inheritance optimization the two commands built together is
**silently dead**: the full suite gets paid in ② (stale), again in ② if the agent notices (as
21.8b did), and again in ③ if it doesn't.

**The `_AP` twin already has the right order** (red → green → **expand** → **suite + SHA** →
walkthrough). The interactive command drifted from its own twin in exactly this spot —
`sudo-commands-have-ap-twins-that-drift`, demonstrated.

## Findings (from the measured 21.8b run)

| # | Finding | Class | Evidence |
|---|---|---|---|
| F1 | Full-suite run ordered before automate → stale totals + a voided ③ handshake | **Accuracy** + 4.7 min | 3008 @ `66069c99` was stale on arrival; re-run produced 3012 @ `7423eadf` |
| F2 | Hedge re-run of `services`+`routers` (116 s) after automate | Efficiency | Exists only because of F1; the final full run strictly contains it |
| F3 | Filtered emulator runs are ceremony — collection dominates | Efficiency | 11.8 s (`-k`, 3 tests) vs 12.7 s (full tree, 39 tests); only the full-tree form is citable anyway (sibling conftests global-mock the tree) |
| F4 | Mutation technique unencoded — delete-the-guard kills the structural test too, isolating nothing; only **relocate** proves the behavioral test adds value | Accuracy | First 21.8b mutation check was invalid; second (relocate) was the real proof |
| F5 | No per-run measurement — redundancy invisible until a manual retro | Meta | This plan required hand-archaeology of 15 invocations |

## Design principles

1. **Feedback ≠ certification.** Scoped runs and the blast-radius pass are *feedback* — early,
   cheap, at the point of maximum uncertainty. The full suite is *certification* — it has exactly
   one legitimate moment: the final code SHA. One run, at that moment, or it proves nothing.
2. **The (totals, SHA) pair is a contract with ③,** not decoration. Produce it where ③ can
   honor it, and its skip pays for this whole plan by itself.
3. **Single source of truth for totals.** The walkthrough's certification block is the one
   citable number; the automate summary references it, never carries a divergent copy.
4. **Only citable forms get run.** If a harness rule says only the full-tree result counts,
   the subset run is deleted, not "kept for comfort."
5. **The workflow measures itself.** A required Suite Ledger turns the next optimization pass
   into a diff, not an archaeology dig.

---

## Workstreams

### WS-A — Reorder: certify once, at the shipping SHA *(the core fix)*

**File:** `.agents/commands/sudo-dev-story-tests.md`

**A1 — Step 3 (Implement):** delete the full-suite mandate. Replace the sentence beginning
"then **finish with ONE full-suite run per touched stack**…" with:

> Run scoped suites while you iterate (the story's files + touched modules), and finish with one
> targeted **blast-radius pass** over the suites your changed files share (fail-fast on
> collateral while context is hot). **Do NOT run the full suite in this step** — Step 4 adds
> tests, which stales any totals produced now; Step 4.5 owns the one certification run.
> If a test fails, find root cause before fixing.

**A2 — insert Step 4.5 (Certify at the shipping SHA)** between Automate and Close-out:

> 1. **Machine floor, ONCE, over the final changed-file set** — ruff + pyrefly on changed files
>    (both HARD gates lint whole files, so inherited debt in touched files is yours). If `--fix`
>    altered anything, re-run the story contract set.
> 2. **Commit** (explicit paths, never `git add -A`).
> 3. **ONE full-suite run per touched stack** (backend: `backend/.venv` pytest with the canonical
>    runner flags — the runner AIDEV-NOTE in `backend/requirements.txt` is the one source of
>    truth). E2E tier touched → the **FULL-TREE** emulator run (`-m emulator`); `-k`/single-file
>    emulator runs are **debug-only, never citable** — collection dominates their cost (measured:
>    11.8 s filtered vs 12.7 s full tree) and sibling conftests make isolated results
>    untrustworthy.
> 4. **Paste the actual totals + `git rev-parse HEAD` into the walkthrough.** INVARIANT: the
>    totals MUST come from a run at exactly the SHA the walkthrough names — any code or test
>    change after this run voids it (repeat step 3). Artifact-only commits after the run are
>    exempt; ③ Step 3 already honors that distinction. This (totals, SHA) pair is ③'s entry
>    baseline — produced at any earlier SHA, ③'s check fails and the full suite is paid twice.
> 5. **Finalize the automate summary's suite-result line NOW** so both artifacts carry the same
>    pair — never two documents with divergent totals.

**A3 — Step 3's "(totals, SHA) is ③'s entry baseline" paragraph** moves into Step 4.5 (it is
now true there, and only there).

**Acceptance:** the phrase "full-suite" appears in exactly one step (4.5); dry-run against the
21.8b transcript shows the stale path unreachable and the mandated full-suite count = 1 in both
automate branches (adds tests / skipped); ③'s inheritance precondition is satisfiable again.

### WS-B — Harden Step 4 (Automate): owed coverage + valid mutation proof

Append to Step 4's body (per `restate-alwayson-obligations-in-command-bodies` — agents follow
the literal step list):

> **Structural reds are wiring proofs, never behavior proofs.** If ① left structural-only
> guard/wiring reds (source-contains asserts), behavioral short-circuit coverage is **owed
> here**, not optional — a guard relocated below the write it protects passes a source-grep red
> identically (→ memory `source-grep-guards-cannot-see-order`). Prove the new behavioral test
> non-vacuous by **RELOCATING** the guard (structural reds stay green; only the new test fires),
> never by deleting it (kills both, isolates nothing). Give every scenario a **positive
> control** — the unguarded path must still write — or the test passes against a helper that
> writes nothing at all.

Also add the same fact to `Projects/AGY_AVIATIONCHAT/_bmad/custom/bmad-testarch-automate.toml`
`persistent_facts` (beside the TEST DIALECT entry), so automate runs reached *outside* the ②
wrapper carry it too. (Recon confirmed the facts live in that project layer — there is no
`.agents/skills/` master for this skill.)

### WS-C — Suite Ledger: make the workflow self-measuring

**Step 5 walkthrough spec** gains one required section:

> **`## Suite Ledger`** — one row per suite invocation this session:
> `scope · command · duration · result · why this run`. The certification run's row links the
> SHA. This is the workflow's own telemetry — it is how redundant runs get seen and cut, and it
> turns the next optimization pass into a diff against this table.

Cost: one small table whose data is already in hand when the suites run. It also makes hedging
visible — an unnecessary re-run now needs a written "why."

### WS-D — Twin + propagation

1. **`sudo-dev-story-tests_AP.md`:** order is already correct — port only the *content* deltas:
   the Step 4.5 invariant + emulator full-tree policy into its stage 4, the WS-B mutation rule
   into its stage 3, the Suite Ledger into its stage 5 walkthrough spec. Diff the twins after.
2. **Toolkit sync** via its standard entry point → all four platforms (claude / opencode /
   antigravity launchers / codex); verify `.sync-manifest.json` and mirrors carry the new body.
3. **Fresh template** (`fresh-workspace-living-template`): confirm whether it mirrors command
   bodies; if yes, propagate.
4. **Autopilot lanes** (verified on disk 2026-08-02 — four launchers, three engines):

   | Launcher | Engine | Reaches the fix how |
   |---|---|---|
   | `/autopilot_claude` | `scripts/autopilot-dev-story.ps1` (canonical) | Invokes `sudo-dev-story-tests_AP` by name → **covered by the twin patch** |
   | `/autopilot_deepseek4` | the SAME ps1, `-Deepseek4` flag (Dev lane on DeepSeek V4 Pro, QA stays Claude) | Same stage commands via the shared ps1 → **covered by the twin patch** |
   | `/autopilot_opencode` | opencode-native pipeline | References the `_AP` stage commands → **covered by the twin patch** |
   | `/autopilot_mobile` | Workflow-engine port (web/mobile; no ps1) | **Does NOT reference the `_AP` commands** — its stage subagent prompts inline their own copy of the stage content (`autopilot-mobile-mirrors-claude`: a known drifting port). **Port the Step-4.5 ordering/invariant + mutation rule into its Dev-stage prompt explicitly.** |

   Also verified: `sudo-code-review_AP.md` carries **no SHA-inheritance clause — by design.** The
   autopilot orchestrator gates the `review` flip on its own independent green run (unattended
   lanes verify, they don't trust). No inheritance edit is owed there; the interactive ③ is the
   only consumer of the (totals, SHA) pair, and Step 4.5 is what makes it valid for it.

**Acceptance:** twins diff clean on the shared content; sync manifest updated; the old Step-3
phrasing greps to zero across masters + mirrors.

### WS-E — Burn-in measurement

The next ② story runs under the new spec and its Suite Ledger is compared against the 21.8b
baseline. Targets:

| Metric | Baseline (21.8b) | Target |
|---|---|---|
| Suite invocations per story | 15 | ≤ 8 |
| Test wall-clock per story | ~12.5 min | ≤ 6 min |
| Full-suite runs in ② | 2 | **exactly 1** |
| ③ inheritance hit-rate (clean entry) | 0% — SHA mismatch guaranteed when automate adds tests | ~100% |
| Stale-totals walkthrough | reachable by following the spec | structurally unreachable |
| Coverage | — | **unchanged — every cut is a duplicate or a stale-order artifact** |

### WS-F — Out of scope, noted so effort lands right next

The remaining floor after this plan is dominated by the one serial full-suite run (~4.7 min).
The tracked `agy-xdist-tail-hang` follow-up (~8 tests hang only under `-n auto`) is the single
biggest lever left — closing it roughly halves the floor. Project-side work, separately tracked;
not this plan.

---

## Rollout

1. One edit pass: WS-A + WS-B + WS-C in `sudo-dev-story-tests.md` (same file, net ≈ +12 lines
   after deleting superseded text — antigravity's 12k body limit is launcher-solved, but verify
   post-sync).
2. WS-D: twin port → sync → mirror/Fresh/engine verification.
3. WS-B's AGY custom-layer fact (one-line toml edit, AGY repo).
4. WS-E burn-in on the next ② story; review the ledger vs baseline.

**Rollback:** git revert of the toolkit commit(s) + re-sync. No project code is touched;
per-story behavior reverts with the command body.

## Risks

| Risk | Mitigation |
|---|---|
| Collateral surfaces later (full suite moved after automate) | Blast-radius pass stays in Step 3 — in the baseline it caught everything the full run later confirmed, for 43 s at the point of maximum uncertainty. Certification was never the fast-feedback tool. |
| Agents hedge-re-run anyway | Explicit "do NOT re-run what the certification run subsumes" + the Ledger makes a hedge a visible row needing a why |
| Twin drift recurs | This plan is itself the evidence the twin-diff memory is load-bearing; WS-D makes the port + diff an explicit step |
| ③ incompatibility | None — ③ already implements the SHA-strict inheritance and the artifact-only-commit exemption; this plan makes ② produce what ③ already expects |
| Command body growth vs antigravity limit | Net growth is small; launchers already solved the 12k limit (`antigravity-uses-workflows-not-commands`); verify at sync |

## Effort

Single session: ~1–2 h including sync + verification. Burn-in is passive (next story pays
nothing extra — the Ledger is data already in hand).
