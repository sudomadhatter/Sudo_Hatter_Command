---
description: Autopilot Dev-Story Loop (HYBRID) - same 4-stage Dev/QA pipeline as /autopilot_claude, but the Dev lane (Stage 1 Plan + Stage 3 Implement) runs on DeepSeek V4 Pro via OpenRouter's Anthropic-compatible endpoint, so the token-heavy code-writing spends ZERO Claude subscription tokens. The QA lane stays on Claude - Stage 2 Audit on Opus 4.8, Stage 4 Review+Fix on Fable 5. Whole board runs at xhigh effort. CLAUDE-ONLY (drives the claude CLI). Requires an OpenRouter key.
platforms: [claude]
---

# /autopilot_deepseek4 - Hybrid Story Pipeline (DeepSeek V4 Pro Dev lane + Opus/Fable QA lane)

> **This is `/autopilot_claude` with ONE change: the Dev lane runs on DeepSeek V4 Pro instead of Opus.**
> The orchestrator is the *same* `scripts/autopilot-dev-story.ps1`; the only difference is the
> `-Deepseek4` flag, which routes Stages 1 (Plan) + 3 (Implement) at OpenRouter's Anthropic-compatible
> endpoint and raises the whole board to `xhigh` effort. Those stages spend **zero Claude tokens**
> (billed to your OpenRouter key); Stages 2 + 4 stay on Claude (audit on Opus 4.8, review on Fable 5).
> Every guardrail (resumable,
> per-story lock, baseline-red gate, story-flip-to-review, never-commits, never-marks-done) is
> inherited unchanged.
>
> *Replaced `/autopilot_glm` on 2026-07-20 — same lane, cheaper + stronger model. The generic
> `-DevBaseUrl`/`-DevModel`/`-DevAuthToken` flags still reach any Anthropic-compatible provider,
> including GLM, if you ever want it back.*

## The ladder this command runs

| Stage | Lane | Model | Effort | Billed to |
|---|---|---|---|---|
| 1 Plan | Dev | `deepseek/deepseek-v4-pro` | **`xhigh`** | OpenRouter |
| 2 Audit | QA | `claude-opus-4-8` | **`xhigh`** | Claude subscription |
| 3 Implement | Dev | `deepseek/deepseek-v4-pro` | **`xhigh`** | OpenRouter |
| 4 Review+Fix | QA | `claude-fable-5` | **`xhigh`** | Claude subscription |

Note this is a **deliberately different ladder from `/autopilot_claude`** (which runs Dev at `medium`).
The Dev lane here is cheap third-party inference, so there is no reason to hold it back; the QA lane
runs `xhigh` on both gates as the last check before the human. The QA gates inherit the engine's split
defaults — **Stage 2 audit on Opus 4.8, Stage 4 review on Fable 5** (Fable is 2x Opus per token, so the
pre-dev audit takes the cheaper model and only the final gate before the human pays for Fable).

## Prerequisites

**Engine support.** The hybrid lane lives in `scripts/autopilot-dev-story.ps1` and is currently present
**only in `AGY_AVIATIONCHAT`**. Other projects' engines have no `-DevBaseUrl`/`-Deepseek4` and will
reject the flag — port the lane first (see `.agents/reference/autopilot_bmad_dev_loop.md` §5b).

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

Follow **`/autopilot_claude` exactly** — Step 0 (resolve the target project), the story check, the
live TodoWrite pipeline list, the per-notification todo advancement, and the final debrief are all
**identical**. There are only THREE deltas, all in the Monitor launch (Step 3):

1. Append **`-Deepseek4`** to the PowerShell invocation.
2. Use a **`-ds4` log suffix** so a hybrid run never cross-wires the live stream of a plain
   `/autopilot_claude` run of the same story (the run FOLDER is still shared per story, by design —
   pick ONE lane per story).
3. Add `HYBRID` to the grep filter so the hybrid banner streams into the chat.

### Step 3 (Monitor) — use this command instead

Substitute `<PROJECT_ROOT>` and `<STORY>` from Step 0 (when `PROJECT_ROOT` is `.` the paths reduce to
the in-project form), then call **Monitor** with `persistent: true`:

- **command:** `LOG_SLUG=$(printf '%s' "<STORY>" | tr -c 'A-Za-z0-9' '-' | sed 's/--*/-/g; s/^-//; s/-$//'); LOG="<PROJECT_ROOT>/_artifacts/_autopilot-run-$LOG_SLUG-ds4.log"; powershell.exe -NoProfile -File "<PROJECT_ROOT>/scripts/autopilot-dev-story.ps1" -Story "<STORY>" -Deepseek4 > "$LOG" 2>&1 & APID=$!; tail --pid=$APID -f -n +1 "$LOG" | grep --line-buffered -E ">>> STAGE|TEST GATE|STORY STATUS|HYBRID|done in|PAUSED|AUTOPILOT|Total cost|CRASHED|retrying|MODEL MISMATCH|! WARNING|TESTS|COST CEILING|REVIEW INCOMPLETE"`
- **description:** `autopilot-ds4 <STORY> - hybrid stage progress (DeepSeek V4 Pro Dev lane; log <PROJECT_ROOT>/_artifacts/_autopilot-run-<story>-ds4.log)`
- **persistent:** `true`

Everything downstream — advancing the todo list on each `>>> STAGE N/4` notification, the `>>> TEST GATE`
heartbeats, the `PAUSED` / `CRASHED` handling, and the close-out debrief (total cost, OUT-OF-SPEC
DECISIONS + OPEN QUESTIONS FOR DANIEL, story auto-advanced to `review`) — is **byte-identical to
`/autopilot_claude`**; read that command for the full behavior and follow it verbatim from Step 4 on.

## Flags (beyond /autopilot_claude's)

`-Deepseek4` is sugar that fills in five values; **any flag you pass explicitly wins over it**
(the engine tests `$PSBoundParameters`, so `-Deepseek4 -AuditEffort max` really does hold that stage
at `max`):

| `-Deepseek4` sets | to |
|---|---|
| `-DevBaseUrl` | `https://openrouter.ai/api` |
| `-DevModel` | `deepseek/deepseek-v4-pro` |
| `-DevEffort` / `-AuditEffort` / `-ReviewEffort` | `xhigh` |

Granular overrides: `-DevBaseUrl <url>` / `-DevModel <id>` / `-DevAuthToken <key>` point the Dev lane at
any *other* Anthropic-compatible provider or model tier.

## Notes

- **Cost:** the run's `Total cost` line reflects the **Claude (QA) lane only** — DeepSeek Dev-lane spend
  is billed on your OpenRouter account and is intentionally not tracked here (`-MaxCost` / `-MaxStageCost`
  gate the Claude spend). At DeepSeek V4 Pro's rates (~$0.435/M in, ~$0.87/M out — roughly 1.15M output
  tokens per dollar) the Dev lane is cheap enough that this is a non-issue by design.
- **Peak/off-peak pricing.** DeepSeek introduced time-of-day API pricing with the V4 GA: **2× the
  off-peak rate during 09:00–12:00 and 14:00–18:00**. Long autopilot runs straddling those windows cost
  more than a flat-rate estimate suggests. Nothing in the engine accounts for this — it is a scheduling
  consideration, not a guardrail.
- **`deepseek/deepseek-v4-pro` is DeepSeek's newest model** as of 2026-07-20 (shipped 2026-04-24 as a
  preview; the mid-July release was its GA upgrade under the *same* model id, so this config picks it up
  automatically). There is no V5. If you want the model that rivals Fable 5, that is **Kimi K3**
  (`moonshotai/kimi-k3`, Moonshot AI, 2026-07-17) — reachable today via `-DevModel moonshotai/kimi-k3`,
  at roughly 17× V4 Pro's output cost.
- **The engine clears `ANTHROPIC_API_KEY` for the Dev stages.** If a native Anthropic key is present the
  CLI prefers it over `ANTHROPIC_AUTH_TOKEN`, which would silently bill your Claude subscription while
  *appearing* to run on the cheap lane. The var is cleared for the child call and restored afterward, so
  the QA lane is unaffected.
- **Effort passthrough is unverified on this provider.** `--effort xhigh` is a Claude-CLI flag; whether
  OpenRouter/DeepSeek honors it or silently ignores it has not been confirmed. If Dev-stage output quality
  looks flat, that is the first thing to suspect — the run will not error either way.
- **Same story, two lanes:** the run folder + session store + lockfile are keyed by story id, shared
  with `/autopilot_claude`. The per-story lock prevents concurrent double-runs; just don't mix lanes on
  one story's artifacts — pick one lane per story.
- **Preview cost/config for $0:** `... -Deepseek4 -DryRun` prints the resume plan, the full model/effort
  ladder for both lanes, the resolved Dev-lane endpoint, and whether the key is present — spending nothing.
