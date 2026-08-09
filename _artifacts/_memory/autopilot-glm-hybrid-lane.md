---
name: autopilot-glm-hybrid-lane
description: /autopilot_glm = the hybrid autopilot; same engine as /autopilot_claude but Dev lane (stages 1+3) runs GLM 5.2 to save Claude tokens.
metadata: 
  node_type: memory
  type: project
  originSessionId: 56204375-03db-4672-8b92-85ad32bbea51
---

`/autopilot_glm` is `/autopilot_claude` with the **Dev lane offloaded to GLM 5.2** so the token-heavy code-writing spends ZERO Claude subscription tokens. Built + proven on AGY 2026-07-03.

- **ONE shared engine** (`scripts/autopilot-dev-story.ps1`), NOT a fork — added opt-in flags `-DevBaseUrl`/`-DevModel`/`-DevAuthToken` + the `-Glm` sugar switch. Empty flags = byte-identical to the all-Claude run. Mechanism: `Invoke-Stage` scopes `ANTHROPIC_BASE_URL`/`AUTH_TOKEN` + the opus/sonnet/haiku model-slot env vars around ONLY the Dev-lane child `claude -p` call, so stages 1 (Plan) + 3 (Implement) hit Z.ai's Anthropic-compatible endpoint (`https://api.z.ai/api/anthropic`, model `glm-5.2`) while QA stages 2+4 stay native Anthropic.
- **Key resolution:** `-DevAuthToken` > process env (`Z_AI_API_KEY`/`GLM_API_KEY`/`ANTHROPIC_AUTH_TOKEN`) > a gitignored `.env` the engine walks UP to find (project root → …/Projects → command-center root), so one lobby `.env` serves all children and it survives the Windows "already-open shell doesn't see a new User env var" gap. Never echoed → never in any log. Missing key = fail-fast at $0 before any stage; `-DryRun` previews without a key. **LIVE on this laptop (2026-07-03):** Daniel's Z.ai key is set in the lobby `.env` (gitignored via `**/.env`) AND the Windows User env; endpoint validated (`claude -p --model glm-5.2` → served `glm-5.2`, PONG, ~$0.08). Z.ai key console: https://z.ai/manage-apikey/apikey-list (GLM Coding Plan at https://z.ai/model-api).
- **Cost tracking is Claude-only by design** — GLM spend is on the Z.ai plan (cheap, Daniel doesn't care to track it). `-MaxCost`/`-MaxStageCost` gate only the QA lane.
- **Command is a THIN wrapper** (drift-avoidance, see [[sudo-commands-have-ap-twins-that-drift]]): owns only the GLM delta (`-Glm` flag + `-glm` log suffix + `HYBRID` grep token + key prereq); defers ALL reporting/todo/debrief mechanics to `/autopilot_claude`. Lives in AGY `.claude/commands/` + `.agents/commands/`.
- **Propagation still owed** (per [[autopilot-engine-is-project-local]]): AGY-only right now. **Agent-executable runbook + canonical patch exist:** `_my_resources/migrations/propagate-autopilot-glm-hybrid.md` (+ `autopilot-glm-hybrid.patch`) — point a command-center agent at it to patch any project's local `autopilot-dev-story.ps1` (idempotency precheck, fast-copy path when un-diverged, surgical 9-edit path when drifted, verify). NOTE checked 2026-07-03: AGY (pre-edit) and Fresh_Workspace engines were BYTE-IDENTICAL, so the fast copy path is currently safe. Do the rollout AFTER a first green real GLM run confirms the endpoint behaves.
