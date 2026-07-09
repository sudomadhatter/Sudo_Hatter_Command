---
IsArtifact: true
ArtifactMetadata:
  type: implementation_plan
  workspace: Fresh_Workspace_BMAD
  date: 2026-07-09
  slug: fresh-template-bootstrap
  status: approved
---

# Implementation Plan — Fresh_Workspace_BMAD as the clone-and-rename template

**Approval on record:** Daniel in-chat 2026-07-09 — *"the idea for Fresh Workspace is that it is a ready to go project with all the organization and tools i use ready to go so all I have to do is clone the project and rename it. The all the workflows and rules are already in place. Can you set it up this way?"* — plus his companion question on whether the custom-BMAD layer is worth adding for the ASDLC/BDD/autopilot (answered in the walkthrough; the useful parts are implemented here).

## Context

Fresh_Workspace_BMAD is the successor to the deleted `Projects/clean-bmad-workspace` skeleton (frontend
package name is still `clean-bmad-frontend`; `{{PROJECT_NAME}}` / `<PROJECT_NAME>` placeholders intact).
`/sync-agents` already vendors the full command/skill toolkit (incl. autopilot + `_AP` set, synced today),
and TDAD Phase-1 tooling is installed (`pytest-bdd>=7.0.0` pinned, venv Python 3.14 with pytest-bdd 8.1.0).
What a clone does NOT get today — the gaps the `testing_audit_BDD` audit (P2-9) and this session's
custom-BMAD recon identified:

1. **No BMAD guardrails** — `_bmad/custom/` is empty (no plan-first / artifact-insurance tomls) and
   `_bmad/scripts/resolve_customization.py` is missing, so the vendored skills' customization step
   (SKILL.md line 30 in every synced skill) has nothing to resolve. AGY's two guard tomls never propagate
   because `/sync-agents` excludes `_bmad/` by design.
2. **No `.agents/rules/000-PLAN-FIRST-GATE.md`** — the rule the guard tomls load is AGY-project-owned.
3. **Gate disarmed** — no `_bmad-output/sudo-tests.yaml` → `/sudo-code-review` auto-WAIVES forever.
4. **No CI** — `.github/workflows/` absent (and the audit's P0-1 lesson: gate `main_debug` too).
5. **BDD layer unproven** — zero `.feature` files; the TDAD layout (`backend/tests/features/` +
   `backend/tests/bdd/steps_*.py`) doesn't exist and nothing verifies pytest actually collects it.
6. **The TDAD dialect override** (audit note, testing_audit_BDD.md:214) — testarch skills speak
   Playwright/Cypress by default; nothing pins them to pytest-bdd. Both `bmad-testarch-atdd` and
   `bmad-testarch-automate` expose a `[workflow]` customize surface (persistent_facts append,
   on_complete override) — verified in their `customize.toml`.

## Changes

### Fresh_Workspace_BMAD (all new files except one edit)

| # | File | Action |
|---|------|--------|
| 1 | `_bmad/scripts/resolve_customization.py` | copy from AGY (stdlib-only; referenced by every synced skill) |
| 2 | `_bmad/scripts/resolve_config.py` | copy from AGY (referenced by 3 skills) |
| 3 | `_bmad/custom/.gitignore` | copy from AGY (`*.user.toml`) |
| 4 | `_bmad/custom/config.toml` | copy from AGY (commented team-override template) |
| 5 | `_bmad/custom/bmad-dev-story.toml` | copy from AGY verbatim — plan-first gate + artifact-protocol persistent facts + on_complete walkthrough insurance (battle-tested, 3 fix iterations May–Jun) |
| 6 | `_bmad/custom/bmad-quick-dev.toml` | copy from AGY verbatim — same guard for quick-dev |
| 7 | `.agents/rules/000-PLAN-FIRST-GATE.md` | copy from AGY verbatim (generic; Fresh has the `opencode.json` + `_artifacts/README.md` it references) |
| 8 | `_bmad/custom/bmad-testarch-atdd.toml` | NEW — pytest-bdd dialect pin (persistent_facts) |
| 9 | `_bmad/custom/bmad-testarch-automate.toml` | NEW — dialect pin + `on_complete` that persists `automation-summary-<story>.md` (the exact evidence today's ③-gate check looks for) |
| 10 | `_bmad-output/sudo-tests.yaml` | NEW — gate ARMED from day one: `required_tiers [L1, L2]`, `l1_coverage_min: 0.0` (ratchet anchor — only ever goes UP; AGY precedent 0.54), `agent_bearing: true` (stack ships ADK/LLM), `nfr: true`, `waive: false`, `baseline: at-opt-in`; tier_map/standards keys commented until a TEA-8-style story creates them |
| 11 | `.github/workflows/pr-check.yml` | NEW — `on: pull_request: branches: [main, main_debug]` (P0-1 lesson baked in); backend job = pip install + full pytest with branch coverage (`--cov-fail-under=0`, ratchet comment); frontend job = `npm ci` + lint + build (no test script exists yet — noted for the first UI story) |
| 12 | `backend/tests/features/template/workspace_smoke.feature` | NEW — sample Gherkin contract proving the Vision-Lock layer |
| 13 | `backend/tests/bdd/__init__.py` + `backend/tests/bdd/steps_template.py` | NEW — self-binding steps (`scenarios()`), house convention documented in the module docstring |
| 14 | `pyproject.toml` | EDIT — `python_files = ["test_*.py", "*_test.py", "steps_*.py"]` so self-binding steps modules are collected |

### AGY_AVIATIONCHAT (2 new files — the audit-remediation slice only)

| # | File | Action |
|---|------|--------|
| 15 | `_bmad/custom/bmad-testarch-atdd.toml` | same dialect toml (AGY layout is identical; wording allows Playwright ONLY for explicitly E2E-level journey stories — AGY legitimately has a Playwright pack) |
| 16 | `_bmad/custom/bmad-testarch-automate.toml` | same — skill-layer belt to today's command-layer suspenders on automate evidence |

### Out of scope (deliberately)

- No BMAD version upgrade for Fresh (`_bmad` core layout differs from AGY v6.9 but the *skills* are the
  synced v6.9-style set and only need the resolver script — verified).
- No frontend test runner (nothing to run; wiring vitest belongs to the first UI story).
- No changes to `new-project.ps1` / `.agents/templates/project-template` (a second, lighter scaffold
  mechanism — flagged to Daniel in the walkthrough; unifying them is his call).
- No deploy workflows (product-specific; the audit's P0-2 test-job lesson noted in pr-check.yml comments).

## Verification

1. `Projects/Fresh_Workspace_BMAD/.venv/Scripts/python -m pytest backend/tests -v` → BDD smoke scenario
   collected AND green (proves layout + `python_files` + pytest-bdd wiring end-to-end).
2. YAML-parse `pr-check.yml`; TOML-parse all four new/copied tomls via `tomllib`.
3. `resolve_customization.py --skill <fresh testarch-automate skill dir>` returns the merged override
   (proves the resolver + toml chain actually resolves in Fresh).
4. md5 compare every copied file vs its AGY source.

## Risks / notes

- `python_files` REPLACES the default list — including all three patterns keeps existing conventions.
- Gate armed with `l1_coverage_min: 0.0` + CI `--cov-fail-under=0` = teeth on traceability/regressions
  without an impossible day-one coverage bar; both are documented ratchets.
- Guard tomls bind to the interactive skills; autopilot's `_AP` commands carry their own equivalents
  (stage separation + walkthrough requirement), so no headless stall risk — the testarch tomls DO fire in
  autopilot's QA stage (sudo-code-review_AP invokes trace/nfr/test-review skills).
