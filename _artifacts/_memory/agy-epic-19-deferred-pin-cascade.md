---
name: agy-epic-19-deferred-pin-cascade
description: "Epic 19 (ADK runtime upgrade) was DEFERRED 2026-07-20 and REOPENED 2026-08-08 as Jira AVCH-18 on branch epic/AVCH-18-adk-2x-runtime — re-scoped to a coordinated 4-family bump at adk 2.6.3/genai 2.17.0, with AVCH-45 folded in as story 19.5. The cascade is real; the blast radius was measured and is bounded. Does NOT merge to main until fully tested."
metadata:
  node_type: memory
  type: project
  originSessionId: d835c3ce-e2c6-4c32-b50c-20d47c58f588
  modified: 2026-08-08T22:02:50.568Z
---

**REOPENED 2026-08-08** (operator ruling) after a wholesale deferral on 2026-07-20. Jira epic
**AVCH-18**; all work on **`epic/AVCH-18-adk-2x-runtime`**, cut from `main`. Board: `epic-19:
in-progress`. Filename keeps the old "deferred" slug only because two memories link to it.

**Operator's framing, and the reason the risk is acceptable:** *"Worst case we just delete the branch
if we fail to get it to work, best case we fix a huge tech debt."* Nothing merges to `main` until he
is happy with it. Rebase the epic branch onto `main` at each story close-out.

**Why it was tractable this time — mostly MEASUREMENT, not a changed world.** July halted on a real
`ResolutionImpossible`, but never measured the four families. Measured 2026-08-08 in a clean scratch
venv: unpinning them resolves cleanly at **adk 2.6.3 / genai 2.17.0** → fastapi 0.129.0→0.141.1,
**starlette 0.52.1→1.5.0 (still a MAJOR)**, google-auth 2.48.0→2.56.3, OTel 1.38.0→1.42.1
(0.59b0→0.63b1); uvicorn + sse-starlette unchanged. Two findings shrank it: ADK 2.x **drops 46
transitive packages** (the `google-cloud-aiplatform` tree — bigquery, spanner, sqlalchemy, `mcp`) and
**zero are imported in `backend/`**; and the starlette major has a **3-line direct surface**
(`main.py:214`, `routers/internal.py:18`, one test). Introspected 2.6.3 directly: `Agent is LlmAgent`
True, `Gemini` has no `api_key` field but has `client_kwargs`, and `Runner`/`FunctionTool`/
`AgentEvaluator`/`BaseSessionService` all import — so the July API homework carries forward unchanged.

**Three traps baked into the old epic text — all now corrected in `epics.md`, but re-check if you meet
an older copy:**
1. **E19-FR2 named a file that no longer exists** (`agents/hr/sub_agents/ta/agent.py`, deleted by
   debug-1.5). There is exactly ONE ADK `Gemini(api_key=…)` site: `agents/greeting/agent.py:26`. The
   other **nine** `api_key=` hits are `genai.Client(api_key=…)` — raw genai SDK, **still valid**. A
   sweep that "fixes" them is the most likely way this epic breaks working code.
2. **The ship-gate could not fail.** E19-FR5 required "both ADK eval tests green" — but there are
   **zero `.evalset.json` files**, so both tests in `backend/tests/evals/` skip unconditionally, and
   the AC carried an "or skips are justified" escape hatch. Removed deliberately.
3. **`requirements.lock.txt` is stale** — generated 2026-05-30, last touched 2026-06-24, missing 8
   current direct deps. It has not been the source of truth for months; 19.1's regen fixes it.

**AVCH-45 folded in as story 19.5 and RUNS FIRST** despite its number: ADK evalsets must be recorded
against the **current 1.26.0** runtime or they only prove the new runtime agrees with itself. Order is
**19.5 → 19.1 → 19.2 → 19.3 → 19.4** (encoded as Jira `Blocks` links). 19.3's wipe keeps its double
gate. AVCH-33/34/35/36 are already TRUE CHILDREN of AVCH-18; only AVCH-45 is merely `Relates`-linked,
because **`acli` cannot re-parent an existing work item** (no `parent` field in its edit schema) —
that one is a manual UI action.

⚠️ **`acli jira workitem view` does NOT print the parent field.** Reading "no parent" out of its
output is how AVCH-49 got minted on 2026-08-08 as a duplicate Epic 19 epic while AVCH-18 already
existed and already owned the four story children. AVCH-18 was `Deferred`, so an `In Progress`-only
JQL search never surfaced it either. **Before minting any epic, search the project for the epic by
NAME across every status** — not by inspecting a child's parent.

**How to apply:** the old "never run ② on 19.x / Lane A is deliberately empty" instruction is VOID —
start at 19.5. The 5 `@EPIC_19_DEFERRED` skip marks in
`backend/tests/agents/test_story_19_1_runtime_pins_explicit_key_auth.py` come off during 19.1. Fresh
pin-propagation stays RETIRED (Fresh was retired 2026-08-07). Related:
[[agy-deferred-epic-not-deferred-v3]], [[sprint-dependency-map-recommends-stale-work]],
[[agy-story-files-canonical-dir]].
