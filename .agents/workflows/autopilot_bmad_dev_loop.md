# Autopilot BMAD Dev Loop — Reference

> A one-command, fully-autonomous **dev + QA team** that takes a single BMAD story from
> `ready-for-dev` to *planned → audited → implemented → reviewed → self-fixed*, then hands the
> finished-but-uncommitted work back to Daniel for close-out.
>
> **Engine:** [`scripts/autopilot-dev-story.ps1`](../../scripts/autopilot-dev-story.ps1) ·
> **Trigger:** `/autopilot_claude <story>` ([`.claude/commands/autopilot_claude.md`](../../.claude/commands/autopilot_claude.md)) ·
> **Status:** v2, hardened — anchored matcher, evidence-gated (no verdict tokens), dedicated `_AP`
> commands, independent test gate, auto story→`review`. Proven end-to-end on **Story 14.2** (full
> 4-stage run, $9.00, clean APPROVE, backend 1723 passed / frontend 270 passed).

---

## 1. The one-paragraph mental model

It is a **relay race between two AI teammates who each stay in one chat.** A plain PowerShell
script (no LLM "coordinator" — that would just be tax) fires four headless `claude -p` subprocesses
in sequence. The **Dev** (Amelia, Opus 4.8) plans the story, then *resumes the same session* to
implement it. The **QA** (Murat, Opus 4.8) audits the plan *before any code exists*, then *resumes
the same session* to review the finished code, apply fixes itself, and write Daniel a report. The
two teams hand off through **files in one folder**, never by talking directly. After its own
independent test gate goes green, the script flips the story to `review` — but it **never commits
and never marks the story `done`**; that last mile is always human.

---

## 2. Why it exists (the problem it solves)

A normal "dev a story" chat is one model doing everything in one pass: it plans, codes, and grades
its own homework with no independent check. The autopilot splits that into a **four-eyes pipeline**
where an **independent reviewer session** (a fresh QA chat, Murat) checks the Dev's work twice —
once on the plan (cheap, before code is written) and once on the diff. The independence comes from a
*separate session + a different persona*, not from a stronger model: both default to **Opus 4.8**,
and the reviewer can be pinned to a stronger or different model via `-AuditModel` when a story
warrants it. The pre-code audit is the highest-leverage part: catching a flawed test assertion or an
unmount-order a11y bug in the *plan* costs nothing, whereas catching it after implementation costs a
red CI run and a rewrite. And because no agent grades its *own* output as the final word, the
orchestrator runs an **independent test gate** of its own after Stage 4 (§6) — it re-runs the suites
itself rather than trusting any pasted "tests green."

---

## 3. The four-stage relay

```
Stage 1  Plan        Dev/Amelia 4.8  NEW dev     /sudo-dev-story-tests_AP plan       -> implementation_plan.md
Stage 2  Audit       QA /Murat  4.8  NEW qa      /sudo-self-audit_AP  -> self-audit-stress-test.md
Stage 3  Implement   Dev/Amelia 4.8  RESUME dev  /sudo-dev-story-tests_AP implement  -> code + walkthrough.md
Stage 4  Review+Fix  QA /Murat  4.8  RESUME qa   /sudo-code-review_AP          -> code-review.md + fixes
  then   TEST GATE   orchestrator (no LLM) re-runs pytest+vitest -> green: flip story to review -> Daniel
```

Each stage runs a dedicated headless **`_AP`** command (a lean, agent-to-agent variant of the
interactive BMAD skill, stripped of its "wait for a human" checkpoints). The orchestrator prompt is a
thin pointer: it names the `_AP` command + the shared folder + the story; the behaviour lives in the
command file.

```mermaid
flowchart TD
    D(["Daniel: /autopilot_claude 14.2"]) --> M1["orchestrator mints dev UUID -> sessions.json"]
    M1 --> S1["Stage 1 PLAN — NEW dev session (Amelia, Opus 4.8)<br/>/sudo-dev-story-tests_AP plan"]
    S1 -->|"writes implementation_plan.md"| F[("shared run folder")]
    F --> M2["orchestrator mints qa UUID -> sessions.json"]
    M2 --> S2["Stage 2 AUDIT — NEW qa session (Murat, Opus 4.8)<br/>/sudo-self-audit_AP"]
    S2 -->|"reads plan -> writes self-audit-stress-test.md (findings + fixes)"| F
    F --> S3["Stage 3 IMPLEMENT — RESUME dev (plan still in context)<br/>/sudo-dev-story-tests_AP implement"]
    S3 -->|"reads audit -> writes source code + walkthrough.md"| F
    F --> S4["Stage 4 REVIEW+FIX — RESUME qa (audit still in context)<br/>/sudo-code-review_AP"]
    S4 -->|"reads diff -> re-runs tests, applies fixes, writes code-review.md + OUT-OF-SPEC + OPEN QUESTIONS"| F
    F --> G{"orchestrator TEST GATE<br/>independent pytest + vitest"}
    G -->|"RED"| RED["TESTS RED — exit 4<br/>(resume -ResumeFrom 4)"]
    G -->|"green"| RV["flip story -> review<br/>(story .md + sprint-status.yaml)"]
    RV --> DONE["PIPELINE COMPLETE<br/>not committed, not 'done'"]
    DONE --> D2(["Daniel: ratify decisions, commit, flip review -> done"])
```

**What each stage may and may not do:**

| Stage | Command invoked | May write | Must NOT |
|---|---|---|---|
| 1 Plan | `/sudo-dev-story-tests_AP plan` | `implementation_plan.md`, `decisions-log.md` | touch source code |
| 2 Audit | `/sudo-self-audit_AP` | `self-audit-stress-test.md`, `decisions-log.md` | hard-halt on findings (fixes flow to S3) |
| 3 Implement | `/sudo-dev-story-tests_AP implement` | source, tests, `walkthrough.md` | re-plan; commit; touch story status |
| 4 Review+Fix | `/sudo-code-review_AP` | `code-review.md`, fixes, walkthrough sections | commit; touch story status / `sprint-status.yaml` (the **orchestrator** owns the `review` flip) |

---

## 4. The two-session continuity (the v2 idea)

Each team does its **codebase deep-dive once**. v1 cold-started all five stages, so the QA reviewer
re-read the same files the QA auditor had already studied an hour earlier — pure re-derivation tax.
v2 keeps each team in **one persistent chat**:

```mermaid
flowchart LR
    subgraph dev["DEV session — one chat, id 6274..."]
        S1["Stage 1: PLAN<br/>cold deep-dive"] --> S3["Stage 3: IMPLEMENT<br/>RESUME — plan already in context"]
    end
    subgraph qa["QA session — one chat, id 0b9e..."]
        S2["Stage 2: AUDIT<br/>cold deep-dive"] --> S4["Stage 4: REVIEW+FIX<br/>RESUME — audit already in context"]
    end
    S1 -. "plan file" .-> S2
    S2 -. "audit file" .-> S3
    S3 -. "walkthrough + diff" .-> S4
```

**How it is wired:** the script owns the session ids. It mints a UUID for a team **at the moment
that team's first stage runs**, persists it to `_pipeline/sessions.json`, and passes
`--session-id <uuid> --name autopilot-<story>-<dev|qa>` on the first call, then `--resume <uuid>` on
the second. Because the ids are ours (not parsed out of the model's output), a crashed run is still
resumable — we just re-issue `--resume`.

> **Minting on-run, not up-front, is deliberate** (a collision fix — see §8). If both ids were
> generated once at startup, a forced redo (`-ResumeFrom 1`) would re-issue `--session-id` with an
> id that *already exists*, and the CLI's behaviour on a duplicate id is undocumented.

**The honest tradeoff (measured on 13.3):** resume buys *coherence and cache reuse*, not a
guaranteed per-stage cost drop. A resumed session re-sends its prior transcript as input on every
turn — billed, though at cheap cache-read rates. On 13.3 the Stage-4 resume read **676,763 tokens
from cache** against just 1,359 fresh input tokens: the continuity mechanism demonstrably worked,
but the resume *stages* were not individually cheaper than v1's cold stages (S3 was $2.41 vs a v1
cold implement ~$1.88). The win is quality + context fidelity; treat any cost savings as
story-dependent, not a law.

---

## 5. The tech stack

| Layer | What | Detail |
|---|---|---|
| **Orchestrator** | Windows PowerShell 5.1 | One script, no external deps. Plain control flow — the "coordinator" is `if`/`for`, not an LLM. |
| **Worker** | `claude` CLI (headless) | `claude -p <prompt> --model <id> --permission-mode bypassPermissions --output-format json` |
| **Continuity** | CLI session flags | `--session-id <uuid>` + `--name <label>` (first call) · `--resume <uuid>` (second call) |
| **Agents** | Dedicated headless **`_AP` commands** | Prompts invoke `/sudo-dev-story-tests_AP plan`, `/sudo-self-audit_AP`, `/sudo-dev-story-tests_AP implement`, `/sudo-code-review_AP` (agent-tuned variants of the interactive BMAD skills). |
| **Models** | Opus 4.8 (Dev) · Opus 4.8 (QA) | Both default to `claude-opus-4-8`; independence is the *separate session + persona*, not a stronger model. Pin asymmetrically via `-DevModel` / `-AuditModel`. |
| **Test gate** | `pytest` + `vitest`, run by the script | After Stage 4 the orchestrator re-runs the suites itself (`-TestScope auto` derives scope from the baseline diff: backend-only / frontend-only / both — and a shared-contract change (schemas / models / OpenAPI / generated types) forces both, so a cross-stack break can't slip through). It refuses to stamp COMPLETE on red. |
| **Handoff** | Artifact files | One canonical `_artifacts/<date>_autopilot-<story>/` folder; `_pipeline/` holds raw JSON + `sessions.json` + a self-contained `run.log` transcript. |
| **Telemetry** | Parsed from result JSON | `.total_cost_usd`, `.num_turns`, `.is_error`, cache token counts. |

**The exact call** (from `Invoke-Stage`):

```powershell
$cargs = @('-p', $Prompt, '--model', $Model,
           '--permission-mode', 'bypassPermissions', '--output-format', 'json')
if ($SessionMode -eq 'New') { $cargs += @('--session-id', $SessionId, '--name', $SessionName) }
else                        { $cargs += @('--resume', $SessionId) }
$raw = $null | & $Claude @cargs 2>$null | Out-String   # empty stdin; drop PS stderr-wrapping
```

### 5a. Engine vs. harness — what "model-agnostic" actually means here

The orchestrator is **not the model you are chatting with.** It is a PowerShell script that spawns its
**own** headless workers. So you can launch it from a Claude Code session, an **opencode** session, an
**Antigravity** session, or a bare terminal, and it **still runs Opus 4.8** — the worker model is the
script's `-DevModel` / `-AuditModel`, completely independent of whatever harness you triggered it from.

That splits "works for all LLMs" into two independent things:

- **Harness-agnostic (done):** the `_AP` commands and this doc live in the shared `.agents/` toolkit, so
  **any** LLM session can read, understand, and trigger the loop. The engine reaches past your harness
  to Anthropic regardless.
- **Worker-engine (deliberately NOT built):** swapping the worker binary off the `claude` CLI would only
  buy **non-Claude brains** — which is exactly what we don't want — and it costs more (API per-token vs
  the Claude-subscription CLI path). It also throws away the per-role **effort** lever below, which is
  Claude-native.

**Engine Adapter** — the seam a second engine would plug into is `Invoke-Stage` (the call above):

| Engine | Headless call | Session new / resume | Telemetry | Status |
|---|---|---|---|---|
| **Claude** (`claude` CLI) | `claude -p … --output-format json` | `--session-id`+`--name` / `--resume` | result JSON (`.total_cost_usd`, `.num_turns`, `.is_error`, `.modelUsage`) | **proven runtime** (`/autopilot_claude`, Fable-5 QA via subscription) |
| **opencode** (`opencode` CLI) | `opencode run … --auto --format json` | `--session <id>` (id **captured from the event stream** on the "new" stage, not pre-minted) | NDJSON event stream (parse adapter: `text` events -> result, `step_finish.part.cost` -> cost, `error` events -> is_error) | **second runtime** (`/autopilot_opencode`, Dev=selected default, QA=`openrouter/z-ai/glm-5.2` `--variant max`) |
| **Antigravity / Gemini** | — | — | — | IDE-bound, not headless-scriptable; **out of scope** |

> **TWO RUNTIMES NOW EXIST.** `/autopilot_claude` is the Claude-engine proven path (Fable-5 QA via
> the Claude subscription, `--max-budget-usd` per-stage cap, `.modelUsage` mismatch assertion).
> `/autopilot_opencode` is the opencode-engine sibling (GLM 5.2 at `--variant max` for QA, no API
> keys, no per-stage cap, mismatch assertion is a no-op — the opencode event stream carries no
> `model` field). Both share the same artifact contract, test gate, story->`review` flip, and
> resilience model; only the `Invoke-Stage` seam + the telemetry adapter differ.

> **CURRENT RUNTIME: the `claude` CLI on Opus 4.8 — and it should stay there.** The relay, file-handoff,
> test gate, and resilience model (the rest of this doc) are already vendor-neutral; only this one call is
> Claude-bound, by choice. (The opencode engine is the second runtime above — same vendor-neutral core,
> different `Invoke-Stage` seam.)

### 5b. Tuning lever — per-role EFFORT on one model, not per-role model

The asymmetry that matters is **effort, not model.** Both teams default to `claude-opus-4-8`; the script
dials *thinking effort per role via prompt keywords* — Dev-Plan says "think hard" (med), Dev-Implement has
no keyword (low), QA Audit/Review both say "think hard". We tried `-DevModel claude-sonnet-4-6` to save
cost and found **Opus-4.8-at-lower-effort is the same cost with better results** — so prefer dialing the
keyword down over downgrading the model. (`-DevModel`/`-AuditModel` still exist for pinning a *successor*
model when one ships, not for trading down.)

---

## 6. Resilience model

```mermaid
stateDiagram-v2
    [*] --> Running
    Running --> Retry: transient API error<br/>(idle timeout / 529 / 429 / overloaded)
    Retry --> Running: backoff 5s,15s,30s<br/>(<= MaxRetries)
    Retry --> CRASHED: retries exhausted
    Running --> PAUSED: stage emits PIPELINE_BLOCKER
    Running --> CRASHED: unparseable output / throw
    Running --> CostCeiling: spend over -MaxCost
    Running --> NextStage: artifact present<br/>(no verdict token — trust the file)
    NextStage --> Running: re-stamp cost + stage
    NextStage --> TestGate: all 4 stages done
    TestGate --> TestsRed: suite fails
    TestGate --> ReviewFlip: suites green -> flip story to review
    ReviewFlip --> COMPLETE: stamp PIPELINE COMPLETE
    COMPLETE --> [*]: exit 0 (human close-out required)
    PAUSED --> [*]: exit 2 (needs Daniel)
    CRASHED --> [*]: exit 3 (resume with -ResumeFrom)
    TestsRed --> [*]: exit 4 (resume -ResumeFrom 4)
    CostCeiling --> [*]: exit 5 (raise -MaxCost)
```

Seven guarantees, each earned by a real incident:

1. **Transient errors retry before failing.** A regex classifies idle-timeout / overload / 429 /
   503 / 529 / generic API errors as transient and retries with `5s,15s,30s` backoff
   (`-MaxRetries`, default 3). A *non-transient* error (e.g. a bad model id) fails fast — no
   pointless retry.
2. **A crash is loud, never silent.** Any hard failure is caught and stamps
   `CRASHED - NOT FINISHED` into `_RUN-STATUS.md` (exit 3). The status file *never* lies "IN
   PROGRESS" after the process dies.
3. **Mid-run status is accurate.** After every stage *and before the test gate* the script re-stamps
   `_RUN-STATUS.md` with the running cost + which phase is next, so "ask status" mid-run is truthful —
   including during the ~100s gate (this was a bug — see §8).
4. **Runs are resumable.** A stage counts as done iff its artifact exists on disk; the orchestrator
   auto-detects the first incomplete stage and skips the rest, reusing the saved session ids.
   `-ResumeFrom N` forces a start stage; `-DryRun` prints the whole resume plan for $0.
5. **Only a genuine blocker stops the flow — and it PAUSES, it doesn't crash.** Findings never halt
   the run (audit fixes flow into the next stage). The *only* mid-run stop is a stage emitting a
   `PIPELINE_BLOCKER:` line — reserved for contradictory ACs, a missing dependency, or a product call
   only a human can make. It stamps a *graceful* `PAUSED - NEEDS DANIEL` (exit 2), not a red crash.
6. **Evidence over tokens.** A stage is "done" iff its handoff artifact lands on disk — there is **no
   verdict-token gate** (the old `Assert-Verdict` crashed complete, tests-green stages over a missing
   string; it was removed). A missing artifact is a *warning*, not a crash; the human reviews the
   folder. This is a human-in-the-loop pipeline: it trusts the artifacts, not a phrase.
7. **The pipeline verifies green itself.** After Stage 4 the orchestrator re-runs the suites
   independently (`pytest` + `vitest`, scoped by `-TestScope`) rather than trusting the agents' pasted
   "tests green." A red gate stamps `TESTS RED` (exit 4); only a green gate advances the story to
   `review` and stamps `COMPLETE`. (A missing runner stamps `TESTS UNVERIFIED` rather than a false green.)

**Per-stage runner logic:**

```mermaid
flowchart TD
    A["Invoke-Stage N"] --> B["claude -p ... (attempt)"]
    B --> C{"parsed JSON<br/>& not is_error?"}
    C -- yes --> D["add cost; return result text"]
    C -- no --> E{"transient<br/>& attempt < MaxRetries?"}
    E -- yes --> F["sleep backoff"] --> B
    E -- no --> G["throw -> CRASHED stamp"]
    D --> H{"result has<br/>PIPELINE_BLOCKER?"}
    H -- yes --> I["PAUSED stamp, exit 2<br/>(needs Daniel, not a crash)"]
    H -- no --> J{"handoff artifact<br/>on disk?"}
    J -- missing --> W["! WARNING (no crash)"] --> K
    J -- present --> K["Set-Progress; next stage"]
```

---

## 7. The artifact handoff folder

Everything for a run lives in one place; the resumed agents read these files instead of
re-deriving:

```
_artifacts/<date>_autopilot-<story>/
├── implementation_plan.md        (Stage 1 — Dev)
├── self-audit-stress-test.md     (Stage 2 — QA, findings + proposed fixes)
├── walkthrough.md                (Stage 3 — Dev; ends with ## Task Checklist + ## Your Actions; Stage 4 prepends QA CLOSE-OUT to the TOP)
├── code-review.md                (Stage 4 — QA, the formal review artifact)
├── decisions-log.md              (any stage — every story-silent call the team made)
├── _RUN-STATUS.md                (live status: IN PROGRESS / TEST GATE / COMPLETE / PAUSED / TESTS RED / CRASHED)
└── _pipeline/
    ├── sessions.json             ({"dev":"<uuid>","qa":"<uuid>"})
    ├── run.log                   (self-contained transcript — stage headers + each result + final banner)
    ├── stage{1..4}-*.json        (raw CLI result JSON per stage — cost, turns, etc.)
    └── gate-tests-*.txt          (independent test-gate output: backend / frontend)
```

> **The run is self-contained.** The global live-tail log lives at `_artifacts/_autopilot-run.log`
> (the stable path the `/autopilot_claude` skill tails), but the folder *also* keeps its own `_pipeline/run.log`
> copy — so opening just the run folder shows the whole story without hunting for the global log.

The artifact-presence map *is* the resume logic: `1=implementation_plan.md`,
`2=self-audit-stress-test.md`, `3=walkthrough.md`, `4=code-review.md`.

**QA owns the last mile.** Because Stage 4 is the final agent before the human, it writes two
spotlight sections at the **top** of `walkthrough.md`:

- `## OUT-OF-SPEC DECISIONS (QA judgment calls - your review)` — every call the team made that the
  story didn't cover, so Daniel can ratify or reverse.
- `## OPEN QUESTIONS FOR DANIEL` — anything the team genuinely couldn't resolve. The agent is
  explicitly *allowed to ask* here rather than forcing everything into a blocker.

---

## 8. Things we discovered building it (the war stories)

Each of these is a real bug or insight from the shakedown runs, now baked into the design:

- **A polished artifact is not a finished story.** A plan or a half-written walkthrough *reads* as
  done. The pipeline therefore makes incompleteness loud (`_RUN-STATUS.md` markers) and never relies
  on the *absence* of a signal to mean "not done." (See the project rule `completion-not-illusion`.)

- **TUNING-1 — stale mid-run status.** v1 only wrote `_RUN-STATUS.md` at start/halt/crash/end, so
  "ask status" mid-run showed `$0.00` and no current stage. Fix: re-stamp after every stage with the
  running cost. Confirmed live on 13.3 (`$1.26` after Stage 1).

- **Session-id collision (caught by a forced-failure test).** Generating both UUIDs up front meant a
  forced redo re-issued `--session-id` with an already-existing id. Fix: **mint on-run** — generate
  the id when its stage actually runs, persist then. A forced redo now gets a clean id.

- **The "exit -1 / stuck IN PROGRESS" red herring.** A crash test once looked like the script hung.
  Root cause was the *test harness*: piping the child through `Select-Object -First 1` closed its
  stdout early and killed it mid-`catch`. The script was fine; the *measurement* was wrong. Lesson:
  consume a child process's full output before judging it.

- **UTF-8 mojibake in captured stdout (TUNING-2).** PowerShell captured the CLI's UTF-8 as cp1252,
  turning em-dashes into `ΓÇö` in the saved JSON. Fix: set `[Console]::OutputEncoding = UTF8` before
  the calls. (Handoff was always safe — it goes through files the model writes, not the captured
  string — but the saved JSON now reads cleanly.)

- **PowerShell scripts must be pure ASCII.** PS 5.1 reads a UTF-8-no-BOM file as ANSI, so a smart
  quote or em-dash in the *script* breaks parsing. Every edit is gated on a 0-non-ASCII + 0-parse-
  error check.

- **Continuity is a cost *tradeoff*, not a free win.** Resume re-sends the prior transcript as
  billed input. The payoff is coherence + cache-cheap context reuse (676K cache-read tokens on
  13.3's Stage 4), not necessarily a cheaper stage. State the win honestly.

- **Agents drop "boring" bookkeeping on a clean pass (the Stage-4 hard-gate bug).** On 13.3, QA did
  everything substantive right but, finding *no fixes needed*, folded its review into `walkthrough.md`
  and **skipped the standalone `code-review.md`** (plus the 4.8 commit attribution and the verdict
  line). The artifact gate correctly stamped `CRASHED`. Root cause: the prompt buried "write
  code-review.md" as one of eight numbered steps. **Fix:** restructure the Stage-4 prompt into
  *review WORK* + a loud **"REQUIRED OUTPUT FILES — this stage FAILS if any is missing"** block that
  demands `code-review.md` *even on a clean review*. General lesson: **separate the judgment work
  from the mechanical deliverables and make the deliverables un-collapsible.**

- **Don't tell a resumed agent "don't re-research."** Early drafts of the team preamble said "you
  already analyzed this, don't re-investigate." That's a quality threat — the agent can over-read it
  and skip *new* investigation it genuinely needs. Continuity is mechanical (the context is already
  there); the prompt only frames it as a *convenience, never a restriction*. (Memory:
  `continuity-prompts-no-research-suppression`.)

- **The audit pays for itself.** On 13.3 the pre-code audit caught (a) a coverage gap where tests
  asserted the callback but never the user-visible "WE'RE LIVE" + Sign-In that the AC names, and
  (b) an a11y live-region placed inside a component that *unmounts at the exact moment* it should
  announce. Both were fixed before a line of code existed.

- **The story-id matcher collided `14.1` with `14.10` (R1).** The unanchored `*14-1*` glob matched
  both `story-14-1-…` and `story-14-10-…`. Fix: dash-normalize *both* the id and each filename, then
  boundary-match `(^|-)<id>(-|$)`. The folder slug is now derived from the **resolved story id**, so it
  is always the clean `…_autopilot-14-2` (the old code slugified the whole *path* →
  `…_autopilot-bmad-bmm-stories-story-14-1-…-md`).

- **The verdict-token gate crashed complete, tests-green work (R1 — the reason §6 guarantee 6 exists).**
  The old `Assert-Verdict` demanded a literal `PIPELINE_*_OK` string; a stage that did everything right
  but phrased its verdict in natural language got stamped CRASHED. Removed entirely — a stage is done
  iff its artifact is on disk. The first principle: **trust the artifacts, not a token.**

- **The orchestrator was too rigid about form when it already had the substance (R1).** The fix above
  generalised: the run no longer hard-fails on a missing handoff artifact either (it *warns*), because
  this is human-in-the-loop — Daniel reviews the folder. The only stop is a genuine `PIPELINE_BLOCKER`,
  and even that PAUSES gracefully rather than crashing.

- **The folder-vs-log split sent the human to the wrong directory (R2).** The live transcript lived
  OUTSIDE the run folder; mid-run, a *parallel team's* folder changed and read as the autopilot's
  output. Fix: mirror the transcript into `_pipeline/run.log` so the run folder is self-contained.

- **The ~100s "silent gap" at the test gate (R2).** Between Stage 4 and COMPLETE the gate runs both
  suites with almost no output — it looked hung, and `_RUN-STATUS.md` read a stage stale. Fix: a
  pre-gate `IN PROGRESS - TEST GATE` re-stamp + the monitor now streams the `>>> TEST GATE` heartbeat.
  (Bonus: a bare `WARNING` monitor token false-fired on pytest's `_GENERIC_LOAD_METHOD_WARNING`;
  anchored it to the script's own `! WARNING` prefix.)

- **The pipeline left the story at `ready-for-dev` — the human had to flip it (R2).** On the 14.2 run,
  close-out meant manually setting the story to `review`. That *is* the BMAD "Dev finishes → review"
  step, so the orchestrator now does it on a green gate: flips the story to `review` in BOTH the `.md`
  and `sprint-status.yaml` — idempotent (only `ready-for-dev`/`in-progress` advance), **never `done`**
  (the human owns `review → done`), best-effort (a flip hiccup warns, never crashes a finished run).

- **The full pipeline is proven end-to-end (Story 14.2, 2026-06-24).** All four stages + the
  independent gate ran clean: **$9.00**, verdict APPROVE, backend **1723 passed** / frontend **270
  passed**. The team caught a **stale story premise** (an AC claimed a prior story had removed the last
  V1 dossier caller — it hadn't; the Admin Socratic-grader still wrote it) and adjudicated
  *delete-not-migrate*, logging it to `decisions-log.md`. That is the four-eyes value in one run:
  the plan questioned a wrong premise instead of blindly executing it.

---

## 9. How to run it

```powershell
# Full run
.\scripts\autopilot-dev-story.ps1 -Story 13.4

# See the resume plan + session ids, spend nothing
.\scripts\autopilot-dev-story.ps1 -Story 13.4 -DryRun

# Cheap trial: plan + audit only (stop after Stage 2)
.\scripts\autopilot-dev-story.ps1 -Story 13.4 -MaxStage 2

# Re-run only the review+fix leg (resumes the qa session)
.\scripts\autopilot-dev-story.ps1 -Story 13.4 -ResumeFrom 4
```

Or trigger via the slash command: **`/autopilot_claude 13.4`**.

| Parameter | Default | Purpose |
|---|---|---|
| `-Story` | (required) | `"14.2"` or a path to the story `.md` |
| `-DevModel` | `claude-opus-4-8` | model for Stages 1 & 3 (Dev) |
| `-AuditModel` | `claude-opus-4-8` | model for Stages 2 & 4 (QA) |
| `-MaxStage` | `4` | stop after this stage (1–4) |
| `-ResumeFrom` | `0` (auto) | force a start stage (1–4) |
| `-MaxRetries` | `3` | transient-error attempts per stage |
| `-MaxCost` | `30` | $ ceiling; halts if spend crosses it (`0` disables) |
| `-TestScope` | `auto` | independent gate: `auto` (scope from baseline diff: backend-only / frontend-only / both; a shared-contract change forces both) / `backend` / `frontend` / `both` / `none` |
| `-DryRun` | off | print the plan + sessions, no spend |

**Exit codes:** `0` complete · `2` paused on a blocker · `3` crashed (resume with `-ResumeFrom`) ·
`4` test gate red (resume `-ResumeFrom 4`) · `5` cost ceiling hit (raise `-MaxCost`).

---

## 10. The human close-out (always required)

The pipeline stops at "developed + reviewed + fixed, gate-verified green, story advanced to
`review`." On a green gate it **does** flip the story to `review` (both the story `.md` and
`sprint-status.yaml`). But it deliberately does **not**:

- run `git commit` / `git push`,
- mark the story `done`, or
- make the judgment calls on the team's out-of-spec decisions.

Daniel's close-out: read the **QA CLOSE-OUT** + **OUT-OF-SPEC DECISIONS** + **OPEN QUESTIONS FOR
DANIEL** at the top of `walkthrough.md`, ratify (or reverse) the team's story-silent calls, run the
git command from the walkthrough's "Your Actions," and flip `review → done`. That last mile is the
point — the autopilot does the labor and parks the story at `review`; the human owns the judgment,
the `done` flip, and the commit.

---

## 11. What is NOT yet proven

- **The retry *loop* firing live.** The backoff path is verified by code inspection + a regex
  classification test, but no real transient failure has been forced on demand (a bad model id is
  correctly *non-transient*, so it never enters the loop).
- **The story→`review` auto-flip firing on a real green gate (R2).** Verified at $0 — clean parse, and
  the two flip regexes unit-tested against the real `sprint-status.yaml` line format (idempotent,
  comment-preserving, no `14-2`/`14-20` prefix collision). It is deterministic PowerShell (not headless
  command expansion), so risk is low; the next real run exercises it and prints
  `>>> STORY STATUS - … flipped to review`.

**Now proven (previously open):** the full four-stage relay **and** the independent test gate ran
end-to-end on **Story 14.2** — including the Stage-4 "required `code-review.md` even on a clean review"
gate (Stage 4 produced `code-review.md` on a clean APPROVE and stamped `PIPELINE COMPLETE`), the `_AP`
headless command expansion, and the anchored matcher / clean folder slug.

---

*Source of truth is always the script + `.claude/commands/autopilot_claude.md`. This doc is the map, not
the territory — if they disagree, the script wins.*
