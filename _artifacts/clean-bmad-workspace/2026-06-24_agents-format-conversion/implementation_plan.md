---
IsArtifact: true
ArtifactMetadata:
  title: clean-bmad-workspace → .agents format conversion (+ model-agnostic autopilot)
  type: implementation_plan
  date: 2026-06-24
---

# Conversion Plan — clean-bmad-workspace to the `.agents` format

> **STATUS: PLAN UPDATED (rev 3) — still AWAITING "approved" before any project file is touched.**
> Target: `Projects/clean-bmad-workspace/` — the **generic reusable template** (placeholders, not real
> aviationChat values) and the test case before the 6 queued projects in `router.md`.
> **Validation path you chose:** after I execute, you drive an **opencode session** in the converted
> repo to prove the new `.agents/` routing is model-agnostic.
>
> **Decisions locked:**
> - Autopilot = **doc + shared placement** (engine stays Claude/Opus-4.8, harness-independent).
> - Conversion = **manual now, capture playbook**.
> - **Git = agents NEVER commit/push. Print the command; Daniel pushes himself.** (No
>   `git-closeout-commits.md` in the template.)
> - **Keep clean-bmad GENERIC** — it's the template; do not bake in concrete aviationChat values.
> - **BMAD owns some files** (`_bmad/`, `.agents/bmad/`, `bmad-*` skills/commands) and regenerates them
>   on update — our customizations live ONLY in non-BMAD files (`AGENTS.md`, adapters, `opencode.json`,
>   our own rules). Never hand-edit a BMAD-managed file.

## Goal

Move `clean-bmad-workspace` from the **old format** (`.agent/` singular source + `.claude/rules/`
mirror + fat `CLAUDE.md`/`AGENTS.md` with `{{PLACEHOLDERS}}` and dead slash commands) to the
**home-base new format**: `.agents/` (plural) = single vendored toolkit, `AGENTS.md` = the brain,
`CLAUDE.md`/`GEMINI.md` = one-line adapters. Then make the autopilot loop model-agnostic at the
doc/placement level, and capture the steps as a reusable playbook — all while keeping the template
generic and keeping our edits out of BMAD-owned files.

## Definition of done

1. Root has thin-adapter `CLAUDE.md` + `GEMINI.md` ("Read AGENTS.md") and a real, **generic** Layer-2
   `AGENTS.md` map — zero `{{PLACEHOLDERS}}` left dangling, zero dead `/dev /pm /sm` commands, and an
   authoritative **GIT = never commit/push** line in ALWAYS-LOAD.
2. `.agents/` (plural) is the single source: 12 master generic rules (vendored, **minus**
   `git-closeout-commits.md`) + the 6 project rules.
3. `.agent/` (singular), `.claude/rules/`, and stale duplicates are gone; nothing references `.agent/`.
4. `.claude/` = `commands/` + `skills/` (+ kept `settings*.json`); `.opencode/` = `commands/` + `agent/`.
5. **`opencode.json` rewritten to `.agents/` paths** so the opencode test-run boots.
6. Autopilot: `autopilot-dev-story.ps1` in master `.agents/scripts/`; loop doc rewritten model-agnostic
   (Engine-Adapter + effort-tuning rationale) in master `.agents/workflows/`.
7. `conversion-playbook.md` captures the ordered steps + the BMAD-owned-vs-ours map, ready to become
   `/convert-project`.
8. Verifies: structural checks pass + **you run an opencode session in clean-bmad and it routes**.

---

## Part A — Convert clean-bmad-workspace

### A1. Build the real `.agents/` (plural) source
Keep these **project-specific** rules (not in the master) in `.agents/rules/`:
`adk_file_formating.md`, `credential-resolution.md`, `prompt-tdd.md`, `pyrefly-paths.md`,
`useEffect-dep-array-stability.md`, `voice-agent-architecture.md`. Review `.agent/gemini.md`; drop it
unless it holds a real project hard-stop (default: drop — the only project hard-stop we need, git, goes
in `AGENTS.md`).

### A2. Vendor the master toolkit
`/sync-agents -Target Projects/clean-bmad-workspace` → vendors master `.agents/` (additive `robocopy
/E`, so the 6 project rules survive) and populates `.claude/{commands,skills}` + `.opencode/{commands,
agent}`. Master wins for generic rules — **except** `git-closeout-commits.md`, which A5 removes.

### A3. Rewrite the three root files (kept GENERIC — this is the template)
- `AGENTS.md` → Layer-2 map from the project template: MAP/MISSION/SUPPORT, **ALWAYS-LOAD**
  (`.agents/rules/constitution.md` + `karpathy-guidelines.md` **+ the authoritative one-liner: "GIT
  (workspace hard rule, overrides any base-constitution close-out language): agents never run `git
  commit`/`git push` — always print the exact command; Daniel pushes himself"**), a real ROUTING TABLE,
  PERSISTENCE → `../../_artifacts/clean-bmad-workspace/`. All rule refs become `.agents/…`. Keep the
  app-shape description generic/templated, not aviationChat-specific.
- `CLAUDE.md` → thin adapter.
- `GEMINI.md` → thin adapter at **project root** (replaces `.gemini/GEMINI.md`).

### A4. Rewrite `opencode.json` to the new paths  *(critical for your opencode test)*
Mirror the home-base file: `instructions` → `["AGENTS.md", ".agents/rules/constitution.md",
".agents/rules/karpathy-guidelines.md"]` (slim least-context set; the long `.agent/rules/...`
enumeration is dropped — those load on demand via the routing table); `skills.paths` →
`[".agents/skills"]`. **Preserve** clean-bmad's richer `permission` block (taskkill / npm / gcloud /
external_directory) — only the paths + instructions change.

### A5. Retire the old format  *(deletions — the only irreversible step; git-recoverable in the clone)*
Delete `.agent/` (singular, after A1 keepers move); delete `.claude/rules/` (new model has none);
delete stale/superseded rules (`mandatory-session-artifacts.md`, `000-PLAN-FIRST-GATE.md`). **Remove
`git-closeout-commits.md`** from the vendored set (it permits close-out commits — contradicts the
locked git policy). Ensure no remaining rule tells the agent it may commit; the `AGENTS.md` line is
authoritative regardless. Collapse `.gemini/` (GEMINI.md → root in A3; keep `.gemini/notes.md` as-is);
`.antigravity/mcp.json` stays.

---

## Part B — Model-agnostic autopilot (doc + shared placement)

**The framing:** the autopilot is not the model you're chatting with — it's a PowerShell orchestrator
that spawns its **own** headless `claude -p` workers. Launch it from opencode / Antigravity / a bare
terminal and it **still runs Opus 4.8** (`-DevModel`/`-AuditModel`, independent of your harness). So
"works for all LLMs" = share the `_AP` commands + doc via `.agents/` so any session can trigger it; the
engine stays Claude. We do NOT build a non-Claude worker engine (it would only buy non-Claude brains —
not wanted — and cost more: API per-token vs the Claude-subscription CLI path).

### B1. Promote the engine to the master toolkit
Move `autopilot-dev-story.ps1` → master `.agents/scripts/` (vendored by sync). Runtime unchanged.

### B2. Rewrite the loop doc — master `.agents/workflows/autopilot_bmad_dev_loop.md`
- **Engine Adapter** table: per vendor → headless call / session-new / session-resume / telemetry.
  Claude = filled & proven. opencode = optional future seam (*point at the Anthropic provider, NOT
  OpenRouter*; needs a session + JSON adapter; **not built**). Antigravity = IDE-bound, not headless.
- "CURRENT RUNTIME: Claude/Opus-4.8; the 2nd-engine seam is `Invoke-Stage`."
- **Effort lesson (your finding):** the better cost/quality axis is **per-role effort on the same Opus
  4.8**, not per-role model — already steered by *prompt keywords* (Dev-Plan "think hard"=med,
  Dev-Implement none=low, QA "think hard"). Opus-4.8-at-lower-effort beats dropping Dev to Sonnet 4.6
  (same cost, better results). Effort is Claude-native — another reason the engine stays on Claude.
- Point `_01_My/Agentic_Loops/autopilot_bmad_dev_loop.md` (your open file) at the master copy.

---

## Part C — Capture + verify

### C1. Playbook
`conversion-playbook.md` (this folder): ordered A1–A5 + the rule-reconciliation table (keep /
from-master / retire) + the `opencode.json` rewrite + the **BMAD-owned-vs-ours map** (regenerated:
`_bmad/`, `.agents/bmad/`, `bmad-*` skills/commands — never hand-edit; ours: `AGENTS.md`, adapters,
`opencode.json`, non-bmad rules) + the sync command + verification. Structured to become
`/convert-project <name>` for the 6 queued projects.

### C2. Verify
- Structural (me): tool dirs populated; every path in the new `AGENTS.md` resolves; `grep` finds no
  remaining `.agent/` (singular), `{{PLACEHOLDER}}`, or commit-permitting git language.
- **Routing test (you):** open an opencode session in `Projects/clean-bmad-workspace/` — confirm it
  boots `AGENTS.md` + `.agents/rules/constitution.md` + `karpathy`, resolves a `.agents/skills` skill,
  and sees the synced `.opencode/commands`.
- Optional canary: the `_experiment` cold-agent run.

---

## Open questions — all resolved
1. **Loop doc home:** `.agents/workflows/` ✅ (you delegated; chosen).
2. **Project hard-stops file:** no separate `constitution.project.md` — the one override we need (git)
   lives as a line in `AGENTS.md` ✅ (keeps it clean, BMAD-update-proof).
3. **`.gemini/notes.md` + 7KB `README.md`:** leave as-is ✅.

## Follow-up (flagged, NOT in this conversion)
- You said "**always** have me push, not the agents" — globally. The home-base **master** constitution/
  artifacts still carry close-out-commit language. Recommend later reconciling the master so never-commit
  is the global default and close-out-commit becomes an **aviationChat-only** override (matches the memory
  noting that rule assumes aviationChat's multi-team `main_debug` repo). Out of scope here; clean-bmad gets
  the clean stance now via its `AGENTS.md`.
- Retire the stale parts of the `clean-bmad-workspace-is-template` memory (the "mirror from aviationChat /
  `.agent/workflows/update_workflow_template_match.md`" procedure) once this new-format flow is proven.

## Risk / blast radius
All edits confined to `Projects/clean-bmad-workspace/` (throwaway clone, own git repo) plus two
**additive** moves into the home-base master `.agents/{scripts,workflows}/`. No edits to
`aviationChat-AGY`, the home-base master rules, or any other project. A5 deletions are the only
irreversible step, git-recoverable.

## Execution order (once approved)
A1 → A2 (sync) → A3 → A4 (opencode.json) → A5 (deletions) → B1 → B2 → C1 → structural verify →
hand to you for the **opencode test-run**.
