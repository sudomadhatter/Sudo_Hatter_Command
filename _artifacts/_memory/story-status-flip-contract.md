---
name: story-status-flip-contract
description: "Who flips story status and when — dev/orchestrator set `review`, only the human close-out sets `done`. The recurring \"fighting\" skeleton was BMAD code-review auto-closing to done."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5421655a-fc6c-40ca-966a-d7eaa2b44a08
  modified: 2026-07-25T19:18:17.753Z
---

Story lifecycle: `ready-for-dev` → `in-progress` → `review` → `done`. The status-flip ownership contract (reconciled across all flows 2026-06-29 after it had been a recurring fight):

- **→ `review` (manual flow):** the **dev step** does it — `/sudo-dev-story-tests` invokes `bmad-dev-story`, whose Step 9 sets the story to `review`. We deliberately **let bmad do this** instead of forbidding it (don't fight bmad's own logic).
- **→ `review` (autopilot flow):** the **orchestrator script** (no LLM) flips to `review` on its OWN independent green gate. The headless agents (`sudo-dev-story-tests_AP`, `sudo-code-review_AP`, opencode `autopilot-reviewer`/`auditor`) **never touch status or sprint-status.yaml**. This is the key difference from the manual flow — don't tell an `_AP` agent to flip status; that's the orchestrator's job.
- **→ `done`:** ONLY the human close-out — `/sudo-update-sprint-memory` after Daniel's sign-off (see [[close-out-command-is-daniels-signoff]]). No agent, no autopilot, no code-review ever writes `done`. Only objectively-red tests block the human's flip. ⚠️ **The flip is a separate act from the landing** — a story can be merged to its epic branch with its branch pruned and still read `review`; see [[landing-is-not-closeout]].
- **code-review never flips status** (manual `/sudo-code-review` or AP) — it writes a verdict and leaves the story at `review`.

**The skeleton that kept resurfacing:** `.agents/rules/bmad_code_review_sudo_fix.md` (renamed 2026-06-29 from `bmad_code_review_fast_path`) used to auto-close the story to `done` ("no confirmation needed"), and BMAD's own `skills/bmad-code-review/steps/step-04-present.md` still defaults `{new_status}=done`. We do NOT edit the BMAD skill internals (its installer would wipe the edit — see [[sudo-commands-have-ap-twins-that-drift]] for the don't-fight-BMAD principle); instead the **`bmad_code_review_sudo_fix` RULE is the sanctioned override** that forces "stop at `review`". If code review ever starts auto-closing to `done` again, fix the rule, not the BMAD skill.

Master `.agents/` is canonical; edit there + `sync-agents.ps1` to each project (see [[toolkit-sync-covers-agents-not-docs]]).
