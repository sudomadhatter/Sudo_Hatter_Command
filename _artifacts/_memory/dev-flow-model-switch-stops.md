---
name: dev-flow-model-switch-stops
description: "② Step-2 gate triggers (formalized 2026-07-20): 'continue' = audit here, no second stop; 'changed' = operator switched the model — audit, then STOP AGAIN to switch back; a pasted file path = another team's blind audit. Agent can never switch models and must never offer to."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d57e9da6-d3b3-4b3d-93ef-2bcf512c4037
  modified: 2026-07-26T19:13:20.895Z
---

The agent can NEVER change the main session's model — only the operator can, via their surface's
switcher (`/model` etc.). **Never offer model choices or subagent model-override lanes at the ② gate** —
the old "name a model / spawn the audit as a subagent" option was REMOVED from
`/sudo-dev-story-tests` on 2026-07-20 (operator: "you can't change models, don't offer").

**The Step-2 gate contract (baked into the command 2026-07-20, all surfaces synced):** post a SHORT
message that ALWAYS carries the clickable `implementation_plan.md` link, listing exactly:
1. `continue` — or switch model first, then say `changed`; 2. handoff to another team (they paste the
audit file path). The operator's reply IS the trigger:
- **`continue`** → audit runs here on the current model; fold + persist; NO second stop.
- **`changed`** → operator already switched the model; run the audit on it, persist + fold, then
  **STOP AGAIN** ("Audit done — switch back, then say `continue`") before Step 2.5/3. Never implement
  on the audit-switched model. This switch-back gate exists ONLY after `changed`.
- **pasted file path** → another team ran the audit blind (often a different LLM); copy it into
  `ARTIFACT_DIR` as `self-audit-stress-test.md` if elsewhere, fold, proceed — no further stops.

**Why:** 2026-07-20, story debug-1.5 — Daniel switched to Fable for the audit lane; the flow would have
rolled into implementation on Fable ("I need you to stop again so I can switch it back"). Formalized
same day during story 19.1 ② ("quick and efficient, works across all LLMs").

**How to apply:** the contract lives in `.agents/commands/sudo-dev-story-tests.md` Step 2 — follow it
literally; keep gate messages short; always hyperlink the plan. The `_AP` twin is headless (no gate) and
deliberately unchanged — [[sudo-commands-have-ap-twins-that-drift]]. Ceiling note RESOLVED 2026-07-26:
the Step-0 ladder moved into `.agents/rules/sudo-target-resolution.md`, the file is ~10.4 KB with real
headroom, and its Antigravity mirror is verbatim again — the Step-2 gate text itself stays untouchable.
Related: [[operator-chairs-the-board]], [[wrapper-flows-collapse-nested-menus]].
