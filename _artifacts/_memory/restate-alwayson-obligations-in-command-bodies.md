---
name: restate-alwayson-obligations-in-command-bodies
description: Human sudo-* command bodies must restate Always-On rule obligations inline; agents follow literal steps and skip standing rules.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6fc84b3c-1b22-4acd-bdae-5abbf001b059
---

A `/sudo-dev-story-tests` run produced a plan + chat report but no `walkthrough.md`, no standalone `self-audit-stress-test.md`, and missing artifact frontmatter — because the command body listed Plan→Self-audit→Implement→Automate→Done but never restated those obligations. They lived only in the Always-On `artifacts-always-first` rule. The agent followed the command's literal steps and the standing rule lost.

**Why:** Agents execute the named steps in a command/skill body; an Always-On constitutional rule does NOT reliably override a step list that omits it. The `_AP` twin spelled the artifacts out, so the human lane silently drifted.

**How to apply:** When a sudo-* (or any) command must satisfy an Always-On rule, bake the obligation into the command body as an explicit step — don't rely on the standing rule. Fixed by adding "Step 5 — Close-out artifacts (MANDATORY)" to `.agents/commands/sudo-dev-story-tests.md` listing the three required files (implementation_plan/self-audit-stress-test/walkthrough) with their frontmatter `type:`. Closing artifacts: keep self-audit + plan as standalone files, but task-checklist + Your-Actions + git commit command all live as sections INSIDE walkthrough.md. Note `.agents/workflows/` is auto-regenerated from `.agents/commands/` by sync-agents, so the command is the true master. Related: [[sudo-commands-have-ap-twins-that-drift]], [[toolkit-sync-covers-agents-not-docs]].
