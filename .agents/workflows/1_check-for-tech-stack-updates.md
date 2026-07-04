---
description: Audit and update the core tech stack (Antigravity, BMAD, ADK, MCPs) to ensure everything is on the latest version
---

# /1_check-for-tech-stack-updates — Tech Stack Drift Audit

Execute the workflow defined in @.agents/workflows/1_check-for-tech-stack-updates.md.

**opencode execution notes:**
- Read-only audit. Do not install or upgrade anything yourself — per @.agents/rules/constitution.md "⚠️ Ask First: Before installing or upgrading dependencies."
- Produce a report listing: package → current version → latest version → severity of drift (patch/minor/major).
- Output the report into `_artifacts/<chat-slug>/walkthrough.md` (or `tech-stack-audit.md` in the same folder if you prefer a dedicated file).
- For each major-version drift, flag breaking-change risks Don should review before approving an upgrade.
- Do NOT include `_bmad/` directory updates in the audit unless Don asks — that's a separate BMAD installer concern.

Optional additional input: $ARGUMENTS
