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

No code was written this session (design + registration only), so no test suite ran.

## Task Checklist

- [x] Research: find the error reporter (Sentry), Firebase/logging reality, story conventions
- [x] Story 16.1 v1 draft + placement plan + INDEX row
- [x] Round-2 pivot: brainstorm doc (3 architectures, guide-agent-verified)
- [x] Round-3 re-slice: 16.1 v2 (runbook), 16.2 (pipeline), 16.3 (frontend) drafts
- [x] Round-4: `main`-monitoring correction folded into 16.1/16.2/plan
- [x] APPROVED placement: 3 story files + sprint-status Epic 16 block (YAML verified)
- [x] Visual overview `sentry_error_response_team.md` (4 diagrams, all validated)
- [x] Walkthrough + INDEX close-out (this doc)

## Your Actions

1. **Review the placed stories** (one click each):
   [16.1](../../../Projects/AGY_AVIATIONCHAT/_bmad/bmm/stories/story-16-1-incident-triage-runbook.md) ·
   [16.2](../../../Projects/AGY_AVIATIONCHAT/_bmad/bmm/stories/story-16-2-always-live-trigger-pipeline.md) ·
   [16.3](../../../Projects/AGY_AVIATIONCHAT/_bmad/bmm/stories/story-16-3-frontend-sentry-capture.md) ·
   [your visual overview](../../../_my_resources/diagrams_guides/system/sentry_error_response_team.md)

2. **Commit — AGY_AVIATIONCHAT repo** (from `Projects/AGY_AVIATIONCHAT`, branch `main_debug`):
   ```
   git add "_bmad/bmm/stories/story-16-1-incident-triage-runbook.md" "_bmad/bmm/stories/story-16-2-always-live-trigger-pipeline.md" "_bmad/bmm/stories/story-16-3-frontend-sentry-capture.md" "_bmad-output/implementation-artifacts/sprint-status.yaml"
   git commit -m "feat: register Epic 16 Automated Incident Response - stories 16.1-16.3 (Sentry -> Routine -> fix PR on main, rollback lane, frontend capture)

   Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
   ```

3. **Commit — home-base repo** (from `Sudo_Hatter_Command`, branch `main_debug`):
   ```
   git add "_artifacts/AGY_AVIATIONCHAT/2026-07-09_incident-response-story-draft" "_artifacts/INDEX.md" "_my_resources/diagrams_guides/system/sentry_error_response_team.md"
   git commit -m "feat: Epic 16 incident-response design session - drafts, decision record, visual overview

   Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
   ```

4. **When ready to build:** start Story 16.1 (`ready-for-dev`) via the normal dev flow. Note for
   the 16.2 session: its Task 0 (Routines beta verification, secrets, IAM grants) is where your
   hands are needed; and that session must also reconcile the `git-policy.md` / `AGENTS.md` §8
   "never PR to main" wording with your incident-lane carve-out so future agents don't fight the
   pipeline.
