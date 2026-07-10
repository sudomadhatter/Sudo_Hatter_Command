---
IsArtifact: true
ArtifactMetadata:
  title: "Epic 16 Automated Incident Response — design session walkthrough"
  type: walkthrough
  date: 2026-07-09
---

# Walkthrough — Epic 16: Automated Incident Response (design + registration session)

## What happened, in order

**Round 1 — research + first draft.** Daniel asked for "a story for error tracking… an agent
always ready with a report." Ground-truthing found: the error reporter is **Sentry, backend-only**
(Story 7.9, wired live by 11.5 → fatal→email); **no Firebase Cloud Functions** — backend logs are
Cloud Run → Google Cloud Logging; the **frontend has NO Sentry** (`ErrorBoundary.tsx:61-63` TODO);
Sentry MCP verified live (org `aviationchat`, project `python-fastapi`). First draft framed a
`/sudo-incident-response` command — **wrong shape**.

**Round 2 — the pivot (md-feedback memos).** Daniel: NOT a `/` command; always-live,
hook-triggered, PC-independent; epic 16 = yes; frontend = "for sure". Brainstormed three
architectures (claude-code-guide agent verified capabilities): GitHub Actions pipeline, **Claude
Code Routines** (first-party webhook→cloud-session, beta), Agent SDK on Cloud Run. Written up in
[always-live-trigger-brainstorm.md](always-live-trigger-brainstorm.md).

**Round 3 — decisions (chips).** Webhook from day one (no cron phase) · **Routines = primary**
("I trust the beta") with the GH-Actions lane built dormant as a **drilled rollback** (relay
`TARGET` flip) · **Level 2 from day one** (fix pre-built + tests + PR; accept = merge) ·
GitHub-issue-only notifications · build-history lookup **conditional** (only when struggling).
The relay design solves the beta's logs gap: it pre-fetches the Cloud Run log excerpt (GCP-native)
so no GCP credentials ever reach the beta.

**Round 4 — the branch correction + "approved".** Daniel: "**main is live** and will be the one
that needs to be monitored and pushed to; debug is where we build." Folded in: triage anchors at
the event's release SHA on `main`; incident PRs target **`main`** (deliberate owner carve-out of
"never PR to main" for this lane — the merge stays his button); hotfix **back-merge to
`main_debug`** flagged in every PR footer. Then the approved placement ran (below). Mid-turn,
Daniel also requested a visual overview doc → written to his diagrams library (his explicit
direction authorizes the `_my_resources` write).

**Round 5 — BDD/ATDD binding (approved via chip).** Daniel: "we need to follow our procedures
for bdd and atdd." The sudo dev flow already imposes them (Vision Lock = Step 2 of
`/sudo-write-story-tests`, vendored in the project; `pytest-bdd>=7.0.0` pinned at
`backend/requirements.txt:54`), but the story text now binds them for every lane:
**16.2 = the BDD pilot (testing-audit P2-8)** — new AC-8 (relay behaviors locked as a pytest-bdd
`.feature` contract via the Vision Lock, ATDD red→green; signature-reject / dedupe-drop /
`TARGET`-routing / kill-switch scenarios; `pr-check` collects it zero-config) + AC-9
(`/testarch-test-review` verdict before review→done) + Task 6. **16.3** — new AC-7 (vitest
tests-first from the ACs: DSN no-op + ErrorBoundary zone-tag capture with mocked
`@sentry/nextjs`; FE Gherkin = Playwright, explicit-E2E-only → the crash→phone journey stays in
the epic close-out) + Task 6. **16.1** — documented BDD **waiver** (no product code — runbook +
thin drill command; the forced-failure drill IS the acceptance evidence; waiver recorded in
Completion Notes). Sprint-status header + all three row comments tagged to match. Plan record:
[implementation_plan.md → Amendment 2](implementation_plan.md).

**Round 6 — Epic 16 test design (approved via chip).** Daniel asked to "run /testarch-test-review
to set up the categories… are they P0?" — tool mismatch caught: test-review audits *existing*
tests (Epic 16 has none yet; it stays the end-of-story gate we bound in Round 5). The right tool
is **`bmad-testarch-test-design`**, run faithfully in epic-level mode (steps 01–05, knowledge
fragments loaded, draft validated against the workflow checklist — which required trimming P0 to
strict criteria and flattening the execution strategy). Result: **13 risks (7 high, no score-9
blockers)**; **28 scenarios — P0 ×10** (signature reject, dedupe+kill switch, PII scrub,
write-boundary, FE PII parity = the security/compliance/spend guards), **P1 ×11** (core journey +
the three drills), P2 ×6, P3 ×1; ~27–43 h. **Answer to "are they P0?": the guards are P0, the
journey is P1** (Sentry email + TARGET flip = real workaround). New catch: R-013 prompt-injection
via attacker-influenced error text → 16.1 runbook hardening. Placed:
`_bmad-output/test-artifacts/test-design-epic-16.md` + epic-run section appended to
`test-design-progress.md` (June's system-level run preserved). Draft:
[test-design-epic-16_draft.md](test-design-epic-16_draft.md).

**Round 7 — ATDD red scaffolds for 16.2 (approved via chip).** `/testarch-atdd` run
(`bmad-testarch-atdd`, sequential, backend stack): the repo's **first `.feature`** —
`backend/tests/features/incident_relay.feature` (8 scenarios = AC-8: signature ×3, dedupe ×2,
kill switch, `TARGET` routing ×2) + `backend/tests/bdd/test_incident_relay_steps.py` (real
assertions; HMAC signature helper; `FakeLaneTransport` effect recorder; ONE adapter seam
`_invoke_relay()`), **all skip-marked per the workflow's red-phase rule** so CI stays green
until 16.2 activates them at the Vision Lock. Checklist/handoff →
`_bmad-output/test-artifacts/atdd-checklist-16-2-always-live-trigger-pipeline.md`; story Dev
Notes gained the `ATDD Artifacts` block. **What fought back:** (1) an interpreter trap, initially misread as env drift — bare `python`
resolves to the GLOBAL user Python 3.14 (missing pytest-bdd, `networkx` → 35 phantom collect
errors), while the canonical **`backend/.venv` was already fully synced**: venv run =
`8 skipped` and the FULL suite collects **2335 tests, 0 errors**. Corrected in the ATDD
checklist + folded into the TDAD install guide (interpreter-discipline warning + Step-4
canaries); a redundant global-interpreter `pip install pytest-bdd` landed en route (harmless).
(2) Gherkin tags raised unknown-mark warnings → registered the 6 contract tags in
`pyproject.toml` markers (house pattern; `@kill-switch` renamed `@kill_switch` — hyphens break
`-m` expressions). Verified (venv): `8 skipped, 0 errors` = pilot proof #1 (features/ collected
zero-config).

## What fought back

- **md-feedback MCP not connected in this session** → memos were read from the file but resolved
  in chat; the `USER_MEMO` blocks were left untouched (hand-editing them corrupts tracking hashes),
  which is why 16.1's revision is a separate `_v2` file.
- **`_artifacts/INDEX.md` changed under me** (parallel session) → re-read and re-applied the row
  edit cleanly.
- Mermaid validator returns ~170KB renders per diagram → verdicts extracted from the saved JSON
  instead of reading the blobs.

## What changed, file by file

**Project (AGY_AVIATIONCHAT — the approved placement):**
- `_bmad/bmm/stories/story-16-1-incident-triage-runbook.md` — NEW, `ready-for-dev`. The runbook
  brain (`.github/claude/incident-triage.md` to be built), 5 steps, conditional build-history,
  drill harness, local drill gate.
- `_bmad/bmm/stories/story-16-2-always-live-trigger-pipeline.md` — NEW, `backlog`. Relay
  (signature/dedupe/log-prefetch/`TARGET`) → Routine (primary) → Level-2 fix PR → `main` → GitHub
  issue; dormant rollback lane + rollback drill; E2E phone drill.
- `_bmad/bmm/stories/story-16-3-frontend-sentry-capture.md` — NEW, `backlog`. `@sentry/nextjs`,
  ErrorBoundary capture, FE Sentry project, source maps.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Epic 16 block appended after
  Epic 15 (header comment + 4 keys), mirroring house format.

**Home base (this session's artifacts + Daniel's library):**
- `_artifacts/AGY_AVIATIONCHAT/2026-07-09_incident-response-story-draft/` — v1 story (with
  Daniel's memos, untouched), `_v2` + 16.2/16.3 drafts, brainstorm/decision record,
  `implementation_plan.md`, this walkthrough.
- `_my_resources/diagrams_guides/system/sentry_error_response_team.md` — NEW (Daniel-directed):
  visual overview, 4 Mermaid diagrams + quick-reference tables + decision log.
- `_artifacts/INDEX.md` — session row (rounds 1–4, handoff).

## Verification (real output)

sprint-status.yaml parse check:
```
YAML OK
['epic-16', '16-1-incident-triage-runbook', '16-2-always-live-trigger-pipeline', '16-3-frontend-sentry-capture', 'epic-16-retrospective']
```

Mermaid validation (Mermaid Chart MCP), all four diagrams:
```
Big picture — crash to merged fix -> valid: True (type: flowchart)
One incident, step by step -> valid: True (type: sequence)
Branch model — where the fix flows -> valid: True (type: flowchart)
Epic 16 story map -> valid: True (type: flowchart)
```

Round-5 re-parse after the BDD/ATDD amendments (filter = keys containing "16"; the two extra
hits are pre-existing unrelated rows):
```
YAML OK
['11-16-ci-gates-ws-auth-hygiene', 'epic-16', '16-1-incident-triage-runbook', '16-2-always-live-trigger-pipeline', '16-3-frontend-sentry-capture', 'epic-16-retrospective', 'tea-16-e2e-p0-journey-pack']
```

No code was written this session (design + registration only), so no test suite ran.

## Task Checklist

- [x] Research: find the error reporter (Sentry), Firebase/logging reality, story conventions
- [x] Story 16.1 v1 draft + placement plan + INDEX row
- [x] Round-2 pivot: brainstorm doc (3 architectures, guide-agent-verified)
- [x] Round-3 re-slice: 16.1 v2 (runbook), 16.2 (pipeline), 16.3 (frontend) drafts
- [x] Round-4: `main`-monitoring correction folded into 16.1/16.2/plan
- [x] APPROVED placement: 3 story files + sprint-status Epic 16 block (YAML verified)
- [x] Visual overview `sentry_error_response_team.md` (4 diagrams, all validated)
- [x] Round-5: BDD/ATDD bound into 16.1–16.3 + sprint-status (16.2 = BDD pilot P2-8; 16.1 =
      documented waiver; 16.3 = vitest tests-first; YAML re-verified)
- [x] Round-6: epic-level test design via `bmad-testarch-test-design` (13 risks / 28 scenarios /
      P0-vs-P1 verdict) → placed in `_bmad-output/test-artifacts/` + progress file appended
- [x] Round-7: `/testarch-atdd` → first `.feature` (8 skip-marked RED scenarios) + step defs +
      checklist + story link-back; verified `8 skipped, 0 errors`; pytest-bdd installed (was
      pinned-but-missing); 6 contract tags registered in pyproject markers
- [x] Walkthrough + INDEX close-out (this doc)

## Your Actions

1. **Review the placed stories** (one click each):
   [16.1](../../../Projects/AGY_AVIATIONCHAT/_bmad/bmm/stories/story-16-1-incident-triage-runbook.md) ·
   [16.2](../../../Projects/AGY_AVIATIONCHAT/_bmad/bmm/stories/story-16-2-always-live-trigger-pipeline.md) ·
   [16.3](../../../Projects/AGY_AVIATIONCHAT/_bmad/bmm/stories/story-16-3-frontend-sentry-capture.md) ·
   [your visual overview](../../../_my_resources/diagrams_guides/system/sentry_error_response_team.md)

2. **Commit — AGY_AVIATIONCHAT repo** (from `Projects/AGY_AVIATIONCHAT`, branch `main_debug`):
   ```
   git add "_bmad/bmm/stories/story-16-1-incident-triage-runbook.md" "_bmad/bmm/stories/story-16-2-always-live-trigger-pipeline.md" "_bmad/bmm/stories/story-16-3-frontend-sentry-capture.md" "_bmad-output/implementation-artifacts/sprint-status.yaml" "_bmad-output/test-artifacts/test-design-epic-16.md" "_bmad-output/test-artifacts/test-design-progress.md" "_bmad-output/test-artifacts/atdd-checklist-16-2-always-live-trigger-pipeline.md" "backend/tests/features/incident_relay.feature" "backend/tests/bdd/test_incident_relay_steps.py" "backend/tests/bdd/__init__.py" "pyproject.toml"
   git commit -m "feat: register Epic 16 Automated Incident Response - stories + test design + ATDD red contract (first .feature, skip-marked; Sentry -> Routine -> fix PR on main)

   Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
   ```

3. **Commit — home-base repo** (from `Sudo_Hatter_Command`, branch `main_debug`):
   ```
   git add "_artifacts/AGY_AVIATIONCHAT/2026-07-09_incident-response-story-draft" "_artifacts/INDEX.md" "_my_resources/diagrams_guides/system/sentry_error_response_team.md"
   git commit -m "feat: Epic 16 incident-response design session - drafts, decision record, visual overview

   Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
   ```

4. **When ready to build:** start Story 16.1 (`ready-for-dev`) via the normal dev flow. 16.2's
   dev session opens with the `/sudo-bdd-tests` Vision Lock — it is the BDD pilot (audit P2-8),
   the first story to prove the `.feature` → ATDD-red → green loop end to end. Note for
   the 16.2 session: its Task 0 (Routines beta verification, secrets, IAM grants) is where your
   hands are needed; and that session must also reconcile the `git-policy.md` / `AGENTS.md` §8
   "never PR to main" wording with your incident-lane carve-out so future agents don't fight the
   pipeline.
