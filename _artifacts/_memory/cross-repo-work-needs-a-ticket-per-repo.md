---
name: cross-repo-work-needs-a-ticket-per-repo
description: "One piece of work spanning the lobby and a project needs TWO tickets — each repo's armed commit-msg gate answers only to its own Jira project, and widening jira.conf is ruled out in writing."
metadata: 
  node_type: memory
  type: project
  originSessionId: f3e01c24-9b74-4562-ba18-4cc66697fffd
  modified: 2026-08-09T08:51:33.222Z
---

A change that spans the lobby and a project **cannot ride one ticket**. Each repo's `.agents/jira.conf`
binds it to one project (lobby → `SCC`, AGY → `AVCH`) behind an **armed** `commit-msg` hook, so an
`SCC-41` subject is rejected outright inside AGY.

**The escape hatch is already closed, on purpose.** AGY's own `.agents/INDEX.md` lists `jira.conf` under
"stays here permanently — never centralize" with the reason spelled out:

> "One shared copy would make the gate reject AviationChat's own work items and accept the lobby's."

So do not add `SCC` to a project's `JIRA_KEYS`. Mint a second ticket in that repo's project and split the
work on the **repo boundary** — e.g. SCC-41 carried the autopilot command docs + loop spec + SOP page in
the lobby, AVCH-50 carried the two engine `.ps1` files in AGY (2026-08-09). Cross-reference them in both
Dev Records; the split is also the honest description of the change.

**Related, same investigation: the Jira key is not derivable from anything BMAD.** The BMAD epic number
and the Jira epic key do **not** track each other — BMAD epic 19 lives on `epic/AVCH-18-adk-2x-runtime`
(`AVCH-18 fix(epic-19): repoint the epic to AVCH-18, not the duplicate AVCH-49`), and story files carry
no key in frontmatter. The only reliable sources are: the **branch name** (`epic/<KEY>-<slug>` →
the key), or a board search for a ticket whose summary's first token is the exact BMAD id — the same
dedupe rule `jira_feed.py mint` uses. Anything that needs a key and has neither must ask or refuse,
never compute one.

**How to apply:** before starting work that touches more than one repo, read each repo's `jira.conf`
first and mint per repo. When a script needs a key, derive it from the checked-out `epic/*` branch and
fail loudly if HEAD is not one — a guessed key produces commits Jira silently never links.

Related: [[jira-integration-live]] · [[thin-projects-center-owns-workflow-law]] ·
[[repo-local-enforcement-never-centralizes]] · [[agy-epic-keys-rot-silently]]
