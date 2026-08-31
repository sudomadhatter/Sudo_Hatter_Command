---
name: zoo-team-wonderland-roster
description: "Zoo Code team design — March Hare is the lead/orchestrator; emoji + regular-case name + ALL-CAPS role; FIVE seats (TESTER+QA merged into Queen of Hearts) override four built-in slugs + one custom; ask stays stock."
metadata: 
  node_type: memory
  type: project
  originSessionId: e6749d54-4e2f-4b6e-8a95-6db65f065496
  modified: 2026-08-30T01:17:57.523Z
---

Decided 2026-08-29 (brainstorm with the operator, pre-ticket — the roster lane is minted after PR
#103 / SCC-346 closes out). The operator is the MAD HATTER — the Steve Jobs idea person. The
**MARCH HARE** is his Wozniak AND the team lead: the orchestrator seat, invoked only when the
operator selects it, acts as autopilot driving the existing `/smh-*` and `/cicd-*` doors, ceiling =
merge-ready (PR opened; the operator lands).

Rules the operator set: agent names are **ALL CAPS with emojis**. Zoo's five built-in modes
(`orchestrator`, `architect`, `code`, `ask`, `debug`) cannot be deleted or hidden, but a custom mode
with the same slug replaces the built-in wholesale, name included (verified in Zoo v3.80.1 compiled
source — the merge swaps the whole mode object). FIVE seats = four overridden slugs + one new slug
(designer); the `ask` slug is deliberately unclaimed so stock Zoo Ask stays for plain Q&A
(amendment 3, 2026-08-29: "the tester and the QA need to really be one" — and she is still the
Queen of Hearts; "the self audit and the code review are the QA and the testing"). Seats teach "how to use our system" from `docs/_scc_sops_prds/workflows_testing_SOP.md`
+ AGENTS.md — never by baking project SOPs into modes (project law loads per-project via
`.agents/INDEX.md`, see [[thin-projects-center-owns-workflow-law]]). Routing law each seat carries:
cicd = dev system for real project work, smh = same system turned inward on the command center
([[sudo-commands-have-ap-twins-that-drift]]). All seats pin the Sudo_Hatter Zoo configuration
profile (API keys live there, never in git). Floor rules reach every seat via generated
`.roo/rules/` copies ([[zoo-code-replaces-roo-code]]).

Roster (operator confirmed 2026-08-29; NAME LAW per his correction: character name in regular
case, ROLE in ALL CAPS after the em-dash — "Use regular March Hare for the name then TEAM LEAD
for the title in caps"):
🫖🐰 March Hare — TEAM LEAD (orchestrator slug; delegates via Zoo's `new_task` tool to seat slugs,
`switch_mode` for handoffs — both confirmed in the v3.80.1 bundle; needs the per-machine
auto-approve tiles `alwaysAllowModeSwitch` + `alwaysAllowSubtasks`) · ⏰🐇 White Rabbit — PM
(architect slug; default daily seat) · 😼🔨 Cheshire Cat — ENGINEER (code slug; renamed from Carpenter, SCC-360) · 🦋 Caterpillar —
DESIGNER (new slug) · ♥️👑 Queen of Hearts — TESTER & QA (debug slug — suppresses stock law-free
Debug; the quality seat at BOTH ends: red-first traps + TEA/testarch doors AND the review/audit
doors, full pen so findings fix in-lane; the retired edit-strip/scoped-pen design was replaced by
a group CEILING — mcp is the TEAM LEAD's alone — plus a live charter-name pin, test B2b).
Ticket: SCC-350, lane chore/SCC-350-wonderland-team.
