---
description: Autopilot Dev-Story Loop (HYBRID) - same 4-stage Dev/QA pipeline as /cicd-autopilot-claude, but the Dev lane (Stage 1 Plan + Stage 3 Implement) runs on DeepSeek V4 Flash 0731 via OpenRouter's Anthropic-compatible endpoint, so the token-heavy code-writing spends ZERO Claude subscription tokens. The QA lane stays on Claude - Stage 2 Audit on Opus 4.8, Stage 4 Review+Fix on Fable 5. Every lane runs at its model's top effort rung (Dev max, QA xhigh). CLAUDE-ONLY (drives the claude CLI). Requires an OpenRouter key.
platforms: [claude]
---

# /cicd-autopilot-deepseek4 - Hybrid Story Pipeline (DeepSeek V4 Flash Dev lane + Opus/Fable QA lane)

> **This is `/cicd-autopilot-claude` with ONE change: the Dev lane runs on DeepSeek V4 Flash instead of Opus.**
> The orchestrator is the *same* `scripts/autopilot-dev-story.ps1`; the only difference is the
> `-Deepseek4` flag, which routes Stages 1 (Plan) + 3 (Implement) at OpenRouter's Anthropic-compatible
> endpoint and runs every lane at its model's top effort rung. Those stages spend **zero Claude tokens**
> (billed to your OpenRouter key); Stages 2 + 4 stay on Claude (audit on Opus 4.8, review on Fable 5).
> Every guardrail is inherited unchanged, because it is the same script: the **story worktree**
> (`.claude/worktrees/<story-slug>/` on `claude/<JIRA-KEY>-<story-slug>`, cut from the epic branch),
> resumable stages, the per-story lock, the baseline-red gate, the story flip to `review`, the
> orchestrator's commit inside the tree, the ticket move to In Review — and never-pushes,
> never-touches-`main`, never-marks-`done`.
>
> *Replaced `/autopilot_glm` on 2026-07-20. Moved off V4 Pro to **V4 Flash 0731** on 2026-08-04 — DeepSeek's
> newest release, re-post-trained for coding/reasoning/agent work, at **~4.8x more output per dollar** than
> Pro. The generic `-DevBaseUrl`/`-DevModel`/`-DevAuthToken` flags still reach any Anthropic-compatible
> provider, including Pro or GLM, if you ever want one back.*

## The ladder this command runs

| Stage | Lane | Model | Effort | Billed to |
|---|---|---|---|---|
| 1 Plan | Dev | `deepseek/deepseek-v4-flash-0731` | **`max`** | OpenRouter |
| 2 Audit | QA | `claude-opus-4-8` | **`xhigh`** | Claude subscription |
| 3 Implement | Dev | `deepseek/deepseek-v4-flash-0731` | **`max`** | OpenRouter |
| 4 Review+Fix | QA | `claude-fable-5` | **`xhigh`** | Claude subscription |

Note this is a **deliberately different ladder from `/cicd-autopilot-claude`** (which runs Dev at `medium`).
The Dev lane here is cheap third-party inference, so there is no reason to hold it back; the QA lane
runs `xhigh` on both gates as the last check before the human. The QA gates inherit the engine's split
defaults — **Stage 2 audit on Opus 4.8, Stage 4 review on Fable 5** (Fable is 2x Opus per token, so the
pre-dev audit takes the cheaper model and only the final gate before the human pays for Fable).

**Why the Dev lane says `max` and not `xhigh`:** effort rungs are per-model, and V4 Flash publishes
`[max, high, low]` — it has **no `xhigh` rung** (V4 Pro's were `[xhigh, high]`). `max` is Flash's top
rung, so this is the same "run the cheap lane at full depth" intent, spelled with a rung the model
actually has. The QA lanes stay `xhigh` because Opus and Fable do have it.

## Prerequisites

**Engine support.** The hybrid lane lives in `scripts/autopilot-dev-story.ps1` and is present in
**`AGY_AVIATIONCHAT` and `NEXgen-VR-Director`** (verified byte-identical in the `-Deepseek4` block,
2026-08-04; `Fresh_Workspace_BMAD` carried it too and left git on 2026-09-04, SCC-403). Any *other* project's engine has no `-DevBaseUrl`/`-Deepseek4` and
will reject the flag — port the lane first (see `docs/_scc_sops_prds/autopilot_bmad_dev_loop.md` §5b).

> The engine is **project-local and hand-ported** — `/smh-sync-agents` propagates `.agents/` commands, *not*
> `scripts/`. When you re-pin the Dev model, change it in **all three** engines or the lanes drift.

**An OpenRouter key** must be reachable as `OPENROUTER_API_KEY` (the engine reads it from the env so it
never lands in a log). Get one at https://openrouter.ai/keys.

The engine resolves the key in this order: `-DevAuthToken` flag > process env
(`OPENROUTER_API_KEY` → `DEEPSEEK_API_KEY` → `ANTHROPIC_AUTH_TOKEN`) > a gitignored **`.env`**
(searched from the project root up to the command-center root). So any ONE of:
- persist it once: `[Environment]::SetEnvironmentVariable('OPENROUTER_API_KEY','<key>','User')`, or
- drop `OPENROUTER_API_KEY=<key>` into a gitignored `.env` at the project **or** command-center root
  (recommended — survives the Windows "already-open shell doesn't see a new User var" gap), or
- export it in the current shell: `$env:OPENROUTER_API_KEY = "<key>"`.

If none is found the run stops immediately with a clear message (a `-DryRun` preview is still allowed
without a key, so you can sanity-check config first).

## What to do

Follow **`/cicd-autopilot-claude` exactly** — Step 0 (resolve the target project), **Step 0.5 (the epic
branch must be checked out — it is the worktree's base and the source of the Jira key)**, the story check, the
live TodoWrite pipeline list, the per-notification todo advancement, and the final debrief are all
**identical**. There are only THREE deltas, all in the Monitor launch (Step 3):

1. Append **`-Deepseek4`** to the PowerShell invocation.
2. Use a **`-ds4` log suffix** so a hybrid run never cross-wires the live stream of a plain
   `/cicd-autopilot-claude` run of the same story (the run FOLDER is still shared per story, by design —
   pick ONE lane per story).
3. Add `HYBRID` to the grep filter so the hybrid banner streams into the chat.

### Step 3 (Monitor) — use this command instead

Substitute `<PROJECT_ROOT>` and `<STORY>` from Step 0 (when `PROJECT_ROOT` is `.` the paths reduce to
the in-project form), then call **Monitor** with `persistent: true`:

- **command:** `LOG_SLUG=$(printf '%s' "<STORY>" | tr -c 'A-Za-z0-9' '-' | sed 's/--*/-/g; s/^-//; s/-$//'); LOG="<PROJECT_ROOT>/_artifacts/_autopilot-run-$LOG_SLUG-ds4.log"; powershell.exe -NoProfile -File "<PROJECT_ROOT>/scripts/autopilot-dev-story.ps1" -Story "<STORY>" -Deepseek4 > "$LOG" 2>&1 & APID=$!; tail --pid=$APID -f -n +1 "$LOG" | grep --line-buffered -E ">>> STAGE|TEST GATE|STORY STATUS|HYBRID|done in|PAUSED|AUTOPILOT|Total cost|CRASHED|retrying|MODEL MISMATCH|! WARNING|TESTS|COST CEILING|REVIEW INCOMPLETE"`
- **description:** `autopilot-ds4 <STORY> - hybrid stage progress (DeepSeek V4 Flash Dev lane; log <PROJECT_ROOT>/_artifacts/_autopilot-run-<story>-ds4.log)`
- **persistent:** `true`

Everything downstream — advancing the todo list on each `>>> STAGE N/4` notification, the `>>> TEST GATE`
heartbeats, the `PAUSED` / `CRASHED` handling, and the close-out debrief (total cost, OUT-OF-SPEC
DECISIONS + OPEN QUESTIONS FOR DANIEL, story auto-advanced to `review`) — is **byte-identical to
`/cicd-autopilot-claude`**; read that command for the full behavior and follow it verbatim from Step 4 on.

## Flags (beyond /cicd-autopilot-claude's)

`-Deepseek4` is sugar that fills in five values; **any flag you pass explicitly wins over it**
(the engine tests `$PSBoundParameters`, so `-Deepseek4 -AuditEffort max` really does hold that stage
at `max`):

| `-Deepseek4` sets | to |
|---|---|
| `-DevBaseUrl` | `https://openrouter.ai/api` |
| `-DevModel` | `deepseek/deepseek-v4-flash-0731` |
| `-DevEffort` | `max` (Flash's top rung — it has no `xhigh`) |
| `-AuditEffort` / `-ReviewEffort` | `xhigh` |

Granular overrides: `-DevBaseUrl <url>` / `-DevModel <id>` / `-DevAuthToken <key>` point the Dev lane at
any *other* Anthropic-compatible provider or model tier. To fall back to the old lane for one run:
`-DevModel deepseek/deepseek-v4-pro -DevEffort xhigh`.

## Notes

- **Cost:** the run's `Total cost` line reflects the **Claude (QA) lane only** — DeepSeek Dev-lane spend
  is billed on your OpenRouter account and is intentionally not tracked here (`-MaxCost` / `-MaxStageCost`
  gate the Claude spend). At V4 Flash 0731's rates (**$0.09/M in, $0.18/M out, $0.018/M cached read** —
  roughly **5.6M output tokens per dollar**) the Dev lane is cheap enough that this is a non-issue by
  design. That is **~4.8× cheaper per output token than V4 Pro** ($0.435/$0.87), which is the whole reason
  for the swap.
- **Peak/off-peak pricing.** DeepSeek introduced time-of-day API pricing with the V4 GA: **2× the
  off-peak rate during 09:00–12:00 and 14:00–18:00**. Long autopilot runs straddling those windows cost
  more than a flat-rate estimate suggests. Nothing in the engine accounts for this — it is a scheduling
  consideration, not a guardrail.
- **`deepseek/deepseek-v4-flash-0731` is DeepSeek's newest release** (2026-07-31), a re-post-trained
  revision of V4 Flash explicitly targeted at *coding, reasoning, and agent workflows* — which is exactly
  this lane. Architecturally it is the **smaller** MoE of the two (284B total / 13B active, vs Pro's
  1.6T / 49B); it wins on speed and price, and DeepSeek's claim is that the re-post-train closes the gap
  on agentic coding. Treat "better than Pro" as **true for this workload, not universally** — if a story
  comes back thin, `-DevModel deepseek/deepseek-v4-pro -DevEffort xhigh` puts you straight back.
- **Pin the dated id, never `~deepseek/deepseek-v4-flash-latest`.** That floating alias resolves
  server-side to the dated model, so `modelUsage` would echo `…-0731` against a requested `…-latest` and
  **false-fire the engine's MODEL MISMATCH assertion** — and a sprint's model could change under you
  mid-epic. Pinning is deliberate; re-pin by hand when DeepSeek ships the next revision.
- **Flash caps completions at 65,536 tokens** (Pro allowed 384,000). That is a *per-turn* ceiling in an
  agentic loop, not a per-stage one, so it is normally invisible — but at `max` reasoning the ceiling is
  shared with the thinking budget. If a Dev turn ever truncates mid-file, drop to `-DevEffort high`
  (Flash's own default rung) before suspecting anything else.
- **The engine clears `ANTHROPIC_API_KEY` for the Dev stages.** If a native Anthropic key is present the
  CLI prefers it over `ANTHROPIC_AUTH_TOKEN`, which would silently bill your Claude subscription while
  *appearing* to run on the cheap lane. The var is cleared for the child call and restored afterward, so
  the QA lane is unaffected.
- **Effort rungs are per-model — check before you override.** `--effort` is a Claude-CLI flag that
  OpenRouter maps onto the provider's own `reasoning_effort`. V4 Flash publishes `[max, high, low]`;
  V4 Pro published `[xhigh, high]`; Opus/Fable take all five. Passing a rung the model does not publish
  is either a 400 or a silent clamp, so name one it has. Verify with:
  `curl -s https://openrouter.ai/api/v1/models | jq '.data[] | select(.id=="<model>") | .reasoning'`.
- **Claude-lane token discipline (Stage 4).** The Fable review is the priciest single call in the run, so
  `/cicd-code-review-AP` binds it to a **one-ingest contract**: it pulls the diff, the changed files, their
  direct callers, and the covering tests **once**, then asks its three review lenses (blind diff / edge
  cases / acceptance) of that single context — no full-repo sweep, no re-traversal per lens. Targeted
  top-ups are allowed only on a *named* lead. Stage 4 also never re-runs the full suite: the orchestrator
  runs the authoritative pytest/vitest gate itself afterward. This is efficiency by **not re-reading**,
  never by reviewing less — the gate's depth is unchanged.
- **Same story, two lanes:** the run folder + session store + lockfile are keyed by story id, shared
  with `/cicd-autopilot-claude`. The per-story lock prevents concurrent double-runs; just don't mix lanes on
  one story's artifacts — pick one lane per story.
- **Preview cost/config for $0:** `... -Deepseek4 -DryRun` prints the resume plan, the full model/effort
  ladder for both lanes, the resolved Dev-lane endpoint, and whether the key is present — spending nothing.
