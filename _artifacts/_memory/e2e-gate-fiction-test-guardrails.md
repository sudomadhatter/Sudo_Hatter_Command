---
name: e2e-gate-fiction-test-guardrails
description: AGY e2e CI gate was report-only forever hiding a fiction test + wrong-config CI; fixed the job to run the real journey harness and added a tests-must-gate-for-real rule + baked guards into ①②③. Propagation (sync + commit) still owed.
metadata: 
  node_type: memory
  type: project
  originSessionId: 6aaaddfd-6d07-4c62-9a38-782516e2742f
---

**2026-07-13.** AGY's `frontend-e2e` PR gate (`.github/workflows/pr-check.yml`) had failed every run
yet showed workflow "success" because `continue-on-error: true` (report-only). Three independent holes:
(1) `e2e/hanger-talk.spec.ts` asserted 4 UI strings that appear **0× in source**, on an auth-gated page
it called "public" — **fiction, never passed**; (2) CI ran bare `npx playwright test` = the plain
`playwright.config.ts` which `testIgnore`s `journeys/**`, so the REAL TEA-16 emulator harness never ran
on CI (it was **6/6 green locally** the whole time — `npm run test:e2e`); (3) report-only left open
indefinitely with no owner.

**Fixed (uncommitted on `main_debug`):** rewired the `frontend-e2e` job to run the real harness
(setup-java Temurin 17 + `npm ci` in `firebase/tests` + `npm run test:e2e`); **deleted** the fiction spec.
Kept `continue-on-error` for exactly ONE proving run — flip to hard gate (delete that line) after the
first green **ubuntu** run. The `deploy-frontend.yml` is only a build pre-check; frontend actually ships
via **Firebase App Hosting auto-deploy on merge to main**, so the gate blocks the PR merge, not the deploy.

**Process guard (the durable fix):** new rule `.agents/rules/tests-must-gate-for-real.md` (`.agents/rules/` + INDEX row)
— a red must fail for the RIGHT reason (grounded in real source), CI must run the REAL suite entrypoint,
and a soft/report-only gate is a one-run window with owner+expiry, never open-ended. Baked enforcement
into the command masters: ① `sudo-write-story-tests` Step 3 (ground every red vs real source),
② `sudo-dev-story-tests` Step 3 (a red that can't go green = fiction, fix/quarantine, never ship red or
delete-to-hide), ③ `sudo-code-review` Steps 3.1/3.4 + its `_AP` twin (CI-runs-real-entrypoint check;
fiction-red ≠ grandfathered legacy red; flag soft CI steps lacking owner+expiry). Skills are thin
launchers → command `.md` is single source.

**Propagated 2026-07-13** via `/sync-agents` × 3 (lobby + AGY + Fresh): guard now in all four surfaces —
opencode/antigravity global caches + the antigravity workflow mirror; the rule file vendored into AGY +
Fresh `.agents/rules/` (+ INDEX row). Codex reaches the 3 dev-flow commands via repo `.agents/skills`
launchers → commands (they're `platforms:[opencode,antigravity]`, so absent from `~/.codex/prompts` BY
DESIGN — a codex prompt would double the skill menu entry); codex reads the rule via native AGENTS.md.
Trimmed my ② `sudo-dev-story-tests` addition to fit the then-current Antigravity size limit. **That limit is gone (SCC-370)** — every door is a thin launcher now, so never trim a command to fit a surface.

**Still owed (git — Daniel's call per git-policy):** commit the master `.agents/` guard changes + the
vendored copies on the live epic branch (else a `chore/*` branch off `main` — the old `main_debug`
target retired 2026-08-07); commit the AGY CI fix + fiction-spec deletion; open the proving PR and
flip report-only→hard-gate after the first green ubuntu run.
Related: [[atdd-mock-shape-must-match-backend-contract]], [[agy-learner-e2e-harness]].
