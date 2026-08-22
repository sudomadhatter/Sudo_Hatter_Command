---
name: story-status-flip-contract
description: "Who flips story status and when — dev/orchestrator set `review`, only the human close-out sets `done`. The recurring \"fighting\" skeleton was BMAD code-review auto-closing to done."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5421655a-fc6c-40ca-966a-d7eaa2b44a08
  modified: 2026-08-15T02:45:04.554Z
---

⛔ **READ THIS CONTRACT AS *WHEN*, NEVER *WHO* (operator ruling 2026-08-14).** "Only the human
close-out sets `done`" means: `done` is written only **inside the close-out ceremony the operator
invoked** — and the AGENT running that ceremony types the write. It has never meant the operator
edits Jira by hand; **no flow in any lane may leave the operator a manual ticket edit** — a flow
that does is broken by definition. The WHO-misreading is not hypothetical: on 2026-08-14 an agent
imported this sentence into the SCC lane, refused to flip a finished rider subtask (SCC-159) to
Done, and handed the operator exactly the data entry this rule was never asking for. The rule's
real target is agent SELF-certification (BMAD's vendor review step auto-closing stories — see
below), not agent typing. Universal law: [[review-status-means-needs-operator]].

Story lifecycle: `ready-for-dev` → `in-progress` → `review` → `done`. The status-flip ownership contract (reconciled across all flows 2026-06-29 after it had been a recurring fight):

- **→ `review` (manual flow):** the **dev step** does it — `/sudo-dev-story-tests` invokes `bmad-dev-story`, whose Step 9 sets the story to `review`. We deliberately **let bmad do this** instead of forbidding it (don't fight bmad's own logic).
- **→ `review` (autopilot flow):** the **orchestrator script** (no LLM) flips to `review` on its OWN independent green gate. The headless agents (`sudo-dev-story-tests_AP`, `sudo-code-review_AP`, opencode `autopilot-reviewer`/`auditor`) **never touch status or sprint-status.yaml**. This is the key difference from the manual flow — don't tell an `_AP` agent to flip status; that's the orchestrator's job.
- **→ `done`:** ONLY inside the operator-invoked close-out — `/sudo-update-sprint-memory` after the operator's sign-off (see [[close-out-command-is-daniels-signoff]]); **the agent executing that command performs the write**. No agent, no autopilot, no code-review ever writes `done` *outside that ceremony* — and the operator never writes it by hand. Only objectively-red tests block the human's flip. ⚠️ **The flip is a separate act from the landing** — a story can be merged to its epic branch with its branch pruned and still read `review`; see [[landing-is-not-closeout]].
- **code-review never flips status** (manual `/sudo-code-review` or AP) — it writes a verdict and leaves the story at `review`.

**The skeleton that kept resurfacing:** the historical `bmad_code_review_sudo_fix` rule (retired under SCC-128 with the house code-review engine) previously overrode vendor BMAD defaults (`{new_status}=done` in `skills/bmad-code-review/steps/step-04-present.md`). Today the house review engine handles reviews directly; if code review ever starts auto-closing to `done` again, ensure the review engine keeps the verdict separate from the `done` flip.

Master `.agents/` is canonical; edit there + `sync-agents.ps1` to each project (see [[toolkit-sync-covers-agents-not-docs]]).
