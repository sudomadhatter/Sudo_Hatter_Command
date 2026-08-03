---
IsArtifact: true
ArtifactMetadata:
  title: Test-certification contract — audit + implementation walkthrough
  type: walkthrough
  date: 2026-08-02
---

# Walkthrough — Test-certification contract for the ②③ dev flow

**What this was:** an audit of the `/sudo-dev-story-tests` optimization research, then implementation of the
upgraded design. Plan: [implementation_plan.md](implementation_plan.md).

---

## The problem, restated after audit

`/sudo-dev-story-tests` Step 3 ordered the full-suite certification run **before** Step 4
(`bmad-testarch-automate`) — the step whose job is adding tests. Follow the spec literally and the
walkthrough carries totals measured at a SHA that stops existing the moment expansion lands.

**What the audit corrected in the research's own framing** (10 findings, 4 material):

| | Research claimed | Ground truth |
|---|---|---|
| ③'s inheritance | "silently dead — 0% hit-rate" | 21.8b's walkthrough line 83 says ②'s pair *was* the entry baseline. ③ **did** inherit — because the agent noticed the staleness and paid a **second** full run in ② to make it valid. The defect costs one extra run; it does not void the contract. |
| Cost | "12.5 min → 6 min" | That is ②-only. One backend suite = **278 s serial**. Per story (②+③) the real figure is **~17 min → ~11 min**. |
| Biggest lever | xdist filed "out of scope" | Post-fix floor is 2 × 278 s. Fixing `-n auto` is worth ~5–6 min/story — **more than this whole plan**, and it compounds. Reordering is the *correctness* fix; xdist is the *efficiency* project. |
| Delivery | write the invariant into two command bodies | The failure being fixed **was an agent following prose.** Prose alone adds no enforcement, and copying it into two bodies is the same mechanism that caused the drift. |

## What changed, file by file

### 1. `.agents/rules/tests-must-gate-for-real.md` — **new Rule 4** (the single source)

The structural move. Instead of duplicating invariants across ② and ②_AP, they live once in the rule that
①②③ and every autopilot lane already read. Rule 4 carries:

- **Feedback ≠ certification** — scoped/blast-radius runs are feedback; the full suite is certification, and
  it has exactly one moment: the shipping SHA.
- **The (totals, SHA) pair is a contract** — any code/test change after the run voids it; artifact/doc-only
  changes are exempt.
- **Never certify before a step that adds tests.**
- **Only citable forms count** — emulator tiers run FULL-TREE; `-k`/single-file runs are debug-only.
- **Mutation proof** — prove a behavioral test non-vacuous by **RELOCATING** the guard, never deleting it
  (deletion kills both tests and isolates nothing); every scenario needs a positive control.

Plus a `## Why` entry recording the 21.8b evidence, so the next reader gets the receipts, not the assertion.

**3,853 B → 6,668 B**, byte-identical across the lobby + all three projects (verified).

### 2. `.agents/commands/sudo-dev-story-tests.md` (②)

- **Step 3** — full-suite mandate deleted. Scoped runs while iterating + one **blast-radius pass**, then an
  explicit *"Do NOT run the full suite in this step — Step 4.5 owns the one certification run."*
- **Step 4** — three lines: structural reds are wiring proofs; behavioral coverage is **owed** here; prove it
  by relocating the guard. Full contract → Rule 4.
- **Step 4.5 (new)** — machine floor once → commit → **ONE full-suite run per touched stack** → emit the
  certification handoff → finalize the automate summary. Red at the run → fix, re-commit, re-run; only the
  LAST run certifies.
- **Step 5** — checklist gains `## Suite Ledger` and the certification-JSON item.

### 3. `.agents/commands/sudo-code-review.md` (③) — heuristic → **mechanical check**

This is what converts the plan from better prose into an enforced contract. ③ previously asked an LLM to
eyeball *"totals are full-suite-shaped (count ≈ known suite size + this story's new tests)"* — a judgment
call on a number, inside a step whose own posture is "fail toward running, never toward trusting."

Now: read `certification-<story>.json`, compare its `sha` to `git rev-parse HEAD`.

- `sha` == HEAD and `failed: 0` → inherit, cite the file, do not re-run.
- File absent / SHA mismatched / a touched stack missing / any `failed` > 0 → run the full suite yourself.

③ also **refreshes the JSON to its own SHA** after its final run (it is then the certifying run), and appends
its rows to the story's Suite Ledger.

### 4. `.agents/commands/sudo-dev-story-tests_AP.md` (the twin)

Order was already correct (`sudo-commands-have-ap-twins-that-drift` — the interactive command was the one
that drifted). Ported the *content* only, as references: certify-last + full-tree + SHA-voiding in stage 4,
the mutation rule in stage 3, the Suite Ledger in stage 5. **No certification JSON here** — headless lanes
gate on the orchestrator's own independent run and consume no handoff, so emitting one would be ceremony.

### 5. `_bmad/custom/bmad-testarch-automate.toml` × 3 projects

Two new `persistent_facts` entries (MUTATION PROOF, CERTIFY LAST) so automate runs invoked **outside** the ②
wrapper carry the same contract. AGY + Fresh + NEXgen.

### 6. Not touched — and why

**`autopilot_mobile.workflow.js`.** Its `prompt3` inlines its own stage content and has no expand step at
all — but it never consumes the (totals, SHA) pair and its orchestrator gates the `review` flip on an
independent run, so it owes nothing here. Its missing automate step is a **separate drift**, filed below, not
fixed inside an optimization pass.

## Test story

No product code changed, so there is no suite to run. Verification was structural, and the checks below all
passed:

| Check | Result |
|---|---|
| Old Step-3 phrasing (`finish with ONE full-suite run per touched stack`) across masters + all mirrors, worktrees excluded | **0 occurrences** (was 10 after the first lobby sync — the project fan-out cleared them) |
| `full-suite` in ② confined to the certification step | ✅ Step 4.5 only (Step 3's mentions are the explicit prohibition) |
| Step 4.5 + certification JSON + Suite Ledger present in all 3 project master copies | ✅ `Step4.5=1 cert.json=2 Ledger=3` each |
| ③ mechanical check + JSON reference in all 3 projects | ✅ `③mech=1 ③cert=2` |
| Twin carries certify-last + ledger + mutation rule in all 3 | ✅ `AP_certify=1 AP_ledger=1 AP_mutation=1` |
| Rule 4 byte-identical, lobby + 3 projects | ✅ 6,668 B, `diff` clean ×3 |
| automate toml facts in all 3 | ✅ `mutation=1 certify-last=1` |
| **WS-G round-trip** — emit side and consume side name the same path, same schema, same field names; match → inherit, miss → run; default is fail-toward-running | ✅ read both sides side by side |
| Antigravity launcher generated for the grown body | ✅ `THIN LAUNCHER` present in all 3 projects + lobby |

## One deviation from the plan

**The plan said the command would stay under the 11,500 B launcher threshold. It did not** — 10,942 → 14,061,
trimmed to **13,741 B**. So `/sync-agents` now emits a thin launcher for it instead of a verbatim Antigravity
mirror.

This is a non-issue, and the disk proves it: `sudo-code-review`, `sudo-close-workingtree`,
`sudo-update-scrum-board`, and `sudo-update-sprint-memory` were **already** over the threshold and already
shipping as launchers. The mechanism exists precisely so command bodies can grow rather than be byte-golfed
(`antigravity-uses-workflows-not-commands`). Verified the launcher generates correctly.

Worth noting the counterfactual: **without** the Rule-4 move, this edit would have been ~+3 KB larger again,
duplicated into the twin.

## Expected effect

| Metric | 21.8b baseline | After |
|---|---|---|
| Full-suite runs in ② | 2 | **1** |
| Full-suite runs per story (②+③) | 3 | **2** |
| ② test wall-clock | ~12.5 min | ~6 min |
| Per-story test wall-clock (②+③) | ~17 min | **~11 min** |
| ③ entry-run skip | worked, at the cost of a hedge run | works by construction |
| Stale-totals walkthrough | reachable by following the spec | structurally unreachable |
| Coverage | — | **unchanged** |

**Decision rule:** more than one mandated full-suite run in ② on the next story is a **defect against the
command**, filed as such — not a retro note.

## Suite Ledger

| Scope | Command | Duration | Result | Why this run |
|---|---|---|---|---|
| — | — | — | — | No product code changed; structural verification only (table above). This section exists because the new spec requires it, and an empty one with a reason is the honest form. |

## Task Checklist

- [x] R1 — Rule 4 into `tests-must-gate-for-real.md`
- [x] WS-A + WS-C′ — ② Step 3 rewrite, Step 4.5, Suite Ledger in Step 5
- [x] WS-G — certification JSON in ② **and** ③, one pass, round-trip verified
- [x] WS-D′ — twin reference lines; Rule 4 propagated to AGY / Fresh / NEXgen
- [x] WS-B′ — `persistent_facts` in three `bmad-testarch-automate.toml`
- [x] `/sync-agents` lobby + `-Maintained` fan-out; verification sweep
- [x] Commit + push per repo; walkthrough

## Your Actions

**Landed (all four repos on `main_debug`, pushed, `0 0`, clean):**

| Repo | Commit |
|---|---|
| AGY_AVIATIONCHAT | `da9df7c4` (on your `7e4cae11`) |
| Fresh_Workspace_BMAD | `45c88e5` (on your `54c92ed`) |
| NEXgen-VR-Director | `fdd70d5` (on your `2b71e64`) |
| Lobby | this commit, incl. the NEXgen gitlink bump → `fdd70d5` |

You committed the first pass yourself mid-session (lobby `a5113ea` at 21:20, plus the three project repos);
these commits carry the trim pass and the sync fan-out on top.

**Left alone deliberately:** `_artifacts/_main/2026-08-02_story-artifact-token-optimization/` is untracked and
is not this session's work — another lane's. Not swept (`worktree-per-story`: never touch work you didn't do).

**Still on you:**

1. **Burn-in.** The next ② story runs under the new spec — check its Suite Ledger against the table above.
   More than one mandated full-suite run in ② is a defect to file.
2. **Schedule the xdist tail-hang** (`agy-xdist-tail-hang-followup`). It is worth ~5–6 min/story — more than
   this entire change — and it is the only lever left on the remaining ~9.3 min floor. This is the
   recommendation the audit is most confident about.
3. **Mobile's missing automate step** — `autopilot_mobile.workflow.js` `prompt3` has no expand stage in any
   of the three projects. Real drift, deliberately out of scope here. Worth a follow-on.
4. **GitNexus index is stale** (hook flagged it during this session) — `gitnexus analyze` when convenient.
