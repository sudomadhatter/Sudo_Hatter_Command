# Todo List
<!-- Daniel's personal task notes for all projects. READ-ONLY for agents. Unless asked to update this file by me. -->

## New Tasks
<!-- Always cross-check against the live project files before trusting anything here. -->
1. We need to verify all the /test-automatic are run and the story test are actual indexed and running for the full test sweet I missed that step on some of them I think
   — ✅ **DONE 2026-07-09** (`testing_audit_BDD.md`, this folder): suspicion CONFIRMED — 13 of 14 Epic-8 ATDD stories skipped `/bmad-testarch-automate` — BUT no tests are orphaned (pr-check runs the FULL suite, so everything on disk runs in CI). Enforcement seam closed same day: ② must leave `automation-summary-<story>.md` evidence, ③ gate check 5 caps silent skips at CONCERNS. Risk-based backfill of the 13 = audit P1-4 (open).

2. Finish the back log on TEA Stories, use C:\\Sudo_Hatter_Command_my_resources\\open_tasks\\tea_testing_guide.md as reference to get up to speed quickly.
   — ✅ **DONE (verified 2026-07-09):** tea-12..18 all executed; the 2026-07-03 trace re-run = **gate PASS, P0 weighted 100%** (supersedes the guide's 7/02 CONCERNS header — header now fixed). Still open from the audit: P0-1..P0-3 CI holes (main_debug ungated, test-less deploy, journeys pack) + P1-5 NFR run.

3. Security Hardening:
   - Error reporting we have something already in place just verify how this works and how the agents can get access to it
   - CLI and MCP access to crashes
   - Review the \_artifacts to see how we built the crashed feature.
   — 🔄 **IN PROGRESS 2026-07-09:** verified = Sentry backend-only (org `aviationchat`, Sentry MCP live; frontend has NO Sentry yet). Epic 16 drafted (16.1 triage runbook · 16.2 GH-Actions pipeline · 16.3 frontend Sentry) — awaiting your "approved" to place the stories (`_artifacts/AGY_AVIATIONCHAT/2026-07-09_incident-response-story-draft/`).

4. Make Storys for debug findings:
   - C:\Sudo_Hatter_Command\Projects\AGY_AVIATIONCHAT\_my_resources\open_tasks\fix_list_admin_sudoadmin.md

## Sub-Projects Todo Lists
<!-- Read /open_tasks/todo_list.md for a quick view of what is going on in the sub projects listed below. -->
   1. C:\Sudo_Hatter_Command\Projects\AGY_AVIATIONCHAT\_my_resources\open_tasks\todo_list.md


## Open Tasks
<!-- Add plan/PRP notes as <slug>.md alongside this file. -->
<!-- open_tasks files — auto-listed by /1_update_maps -->
1. Tea Storys 
2. Live Testing
3. Tasks for Fable 
   - Complete New Task 1. and 2. 3. Security Hardening. — 1 ✅ · 2 ✅ · 3 🔄 (Epic 16 drafts await approval; see above)
   - Full TEA Audit with Fable — ✅ **DONE 2026-07-09**: `testing_audit_BDD.md` (this folder); remediation P1-6 + P2-9 shipped same day, P0-1..3/P1-4/P1-5 open
   - Verify the file folder system against this script: C:\Sudo_Hatter_Command\_my_resources\youtube_transcripts\implementation-plan_folder-as-workspace-routing-system.md — ✅ **DONE 2026-07-09** (system-docs-truth-sync session): R1–R8 met/exceeded, no structural change needed; doc drift fixed in place

<!-- CHECKPOINT id="ckpt_mrco535n_b16yyr" time="2026-07-08T22:47:55.451Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->

<!-- CHECKPOINT id="ckpt_mrcohy4b_7gq97k" time="2026-07-08T22:57:55.451Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->
