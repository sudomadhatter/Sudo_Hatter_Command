---
IsArtifact: true
ArtifactMetadata:
  title: "16.1 — Incident-Response Agent: Sentry Triage Workflow (DRAFT)"
  type: story
  date: 2026-07-09
Status: draft            # NOT yet registered — becomes ready-for-dev only after Daniel approves placement
Epic: 16 (proposed — see OPEN DECISIONS)
Story: 16.1
created: 2026-07-09
depends_on: story-11-5-production-alert-wiring (done — the alert chain this builds on)
source: _artifacts/AGY_AVIATIONCHAT/2026-07-09_incident-response-story-draft/
---

# Story 16.1: Incident-Response Agent — Sentry Triage Workflow (`/sudo-incident-response`)

> Story 11.5 made production crashes reach Daniel's inbox. This story builds the leg that comes AFTER the email: a standing agent workflow that pulls the Sentry issue, correlates the Cloud Run logs, maps the failing code path, reads the feature's own build history, and hands Daniel a root-cause **incident report with a proposed fix plan** — read-only, plan-first, never auto-committing. By the time the alert email is opened, the investigation is already done.

## Story

As **the engineering owner of a production aviation-education platform**, I want **an agent workflow that triages any serious production error the moment it fires — gathering the Sentry issue, the correlated Cloud Run logs, the failing code path, and the feature's build history into one incident report with a proposed fix plan**, so that **a crash costs me one "approved" instead of an evening of manual log-diving.**

---

## Context & Motivation

### What ships today — the alert chain ends at the inbox

The full alert transport was built in Stories 7.9 + 11.5 and **live-verified 2026-06-10** (email + fatal issue + release tag confirmed):

1. Backend unhandled exceptions → Sentry SDK (`backend/observability/sentry_init.py:54`, init called from `backend/main.py:59-61`; gated on `K_SERVICE` + `SENTRY_DSN`, so Cloud Run only).
2. Explicit P1s → `fire_p1_alert()` (`backend/utils/rkp_loader.py:19-52`) sends a `fatal`-level `P1_RKP_MANIFEST_FAILURE` capture; callers `backend/main.py:264` and `backend/services/lesson_plan_builder.py:127`.
3. Sentry alert rule (configured in the Sentry UI): fatal event → email **sudomadhatter@gmail.com**.
4. Deploy workflow ships `SENTRY_DSN` + `GIT_SHA` (`.github/workflows/deploy-backend.yml`), so every Sentry event carries the release commit SHA.

**Everything after step 4 is manual.** The email says "something died"; finding *what*, *where*, and *why* means hand-opening Sentry, hand-querying logs, and hand-reading code.

### Three verified facts that shape the design

1. **There are no Firebase Cloud Functions.** The backend runs on Cloud Run, so "check the logs" means **Google Cloud Logging** (`gcloud logging read`, project `aviationchat`) — not Firebase Functions logs. Firestore (`aviationchat-database`) is only consulted when an incident implicates data state.
2. **The frontend has NO Sentry.** `frontend/src/components/ErrorBoundary.tsx:61-63` holds a commented-out `Sentry.captureException` TODO; no `@sentry/*` package is installed. A crash in the browser today reaches nobody. (→ follow-up Story 16.3, see Dev Notes.)
3. **The Sentry MCP works from the command center** — verified live 2026-07-09: org `aviationchat`(https://aviationchat.sentry.io, region us.sentry.io), single project `python-fastapi`. The agent can read issues/events without any new plumbing when run interactively.

Two more assets the workflow can stand on:

- **GitNexus** indexes this repo (\~40k symbols) — `context`/`trace`/`impact` turn a stack frame into a code-path map and blast radius (→ `docs/gitnexus.md`).
- **Every shipped feature has a paper trail**: its story file (`_bmad/bmm/stories/`, with a File List of every touched file), its walkthrough (`_artifacts/epic_<E>/<story>/walkthrough.md`, including "what fought back"), and its component spec (`_bmad-output/component-specs/`). This is the "go look at how the feature is built" step — cheap and high-signal **if bounded** (see Dev Notes).

---

## ⚠️ OPEN DECISIONS FOR DANIEL

1. **Epic placement.** Recommendation: open **Epic 16 — "Automated Incident Response"** (this story is 16.1; sketches for 16.2/16.3 in Dev Notes). Epic 11 (production hardening) is `done` + retrospected — reopening it would muddy a closed audit trail. Say the word and this renumbers.

<!-- USER_MEMO
  id="3yq_tA9U"
  type="question"
  status="open"
  owner="human"
  source="generic"
  color="blue"
  text="yes"
  anchorText="Epic placement. Recommendation: open Epic 16 — &quot;Automated Incident Response&quot; (th"
  anchor=""
  createdAt="2026-07-09T14:42:40.351Z"
  updatedAt="2026-07-09T14:42:40.351Z"
-->

2\. \*\*How far "auto-triggered" goes in THIS story.\*\* Recommendation: \*\*16.1 ships the workflow itself, invoked on demand\*\* (email arrives → you say "triage the latest incident" or run \`/sudo-incident-response\`). True hands-off auto-trigger (Sentry webhook → GitHub Action running the agent headless) is \*\*Story 16.2\*\* — it needs its own decisions (API key in GitHub secrets, billing, where reports land when your PC is off) and shouldn't block getting the triage brain built.

<!-- USER_MEMO
  id="SzWLBHDE"
  type="question"
  status="open"
  owner="human"
  source="generic"
  color="blue"
  text="This is not what I am thinking. we need something that always live and ready to go not a / command. I want a dedicated agent somehow set up with a trigger that fires. we can have this top level here, but it should always be live not restricted to my computer being on. How can we do this ? "
  anchorText="How far &quot;auto-triggered&quot; goes in THIS story. Recommendation: 16.1 ships the work"
  anchor=""
  createdAt="2026-07-09T14:42:40.351Z"
  updatedAt="2026-07-09T14:42:40.351Z"
-->

3. \*\*Frontend coverage.\*\* "If the site crashed" currently only covers the backend. Wiring \`@sentry/nextjs\` + the ErrorBoundary TODO is \*\*Story 16.3\*\* — approve it as part of the epic or defer.

<!-- USER_MEMO
  id="C01x90Dz"
  type="question"
  status="open"
  owner="human"
  source="generic"
  color="blue"
  text="we "
  anchorText="3. **Frontend coverage.** &quot;If the site crashed&quot; currently only covers the backen"
  anchor=""
  createdAt="2026-07-09T14:44:31.326Z"
  updatedAt="2026-07-09T14:44:31.326Z"
-->

---

## Acceptance Criteria

1. **The workflow exists as a command.** `/sudo-incident-response [sentry-issue-id | "latest"]` is authored in the master `.agents/commands/` and vendored to this project via `/sync-agents`. `"latest"` (default) means: newest unresolved error-or-fatal issue in Sentry project `python-fastapi`.
2. **Sentry retrieval.** The workflow pulls: issue title, level, event count, first/last seen, environment, release (GIT_SHA), and the newest event's full stack trace + hashed user id. Primary transport: the Sentry MCP (org `aviationchat`). Documented fallback for headless/future use: Sentry API with a `SENTRY_AUTH_TOKEN` env var (name documented in `.env.example` — **no secret value in the repo**).
3. **Log correlation.** The workflow queries Google Cloud Logging for the Cloud Run service in a ±15-minute window around the event (`gcloud logging read`, `severity>=ERROR` plus the request window at lower severity when needed) and quotes the relevant excerpts in the report. If `gcloud`is unauthenticated, the report says so plainly and continues — a partial report is still a report.
4. **Code-path mapping.** Top in-app stack frames are resolved to `file:line` and mapped with GitNexus (`context` on the failing symbol, `impact` for blast radius, repo `AGY_AVIATIONCHAT`). If the GitNexus index is stale (known per-machine rot), the workflow falls back to direct file reads and notes the degradation — it never blocks on the graph.
5. **Build-history context (bounded).** The workflow identifies the owning feature by matching stack files against story File Lists / component specs, then reads **at most**: the story file, its `walkthrough.md`, and the matching component spec. It does NOT crawl the artifact tree. The report cites which story built the failing code and any relevant "what fought back" history.
6. **The incident report artifact.** Output lands at `_artifacts/debugging/<YYYY-MM-DD>_<issue-slug>/incident-report.md` (project-local, per this project's debugging bucket) with sections: **TL;DR** (what broke, severity, blast radius, confidence) · **Timeline** · **Evidence** (Sentry + log excerpts) · **Code path** · **Root-cause hypothesis** (with confidence level) · **Proposed fix plan** (implementation-plan shaped — awaiting "approved", per the plan-first gate) · **Suggested tests** · **Your Actions**. Every file reference is a clickable link. No secrets, no raw PII (user ids arrive pre-hashed via `_before_send`, `sentry_init.py:81-90`).
7. **Read-only guarantee + live drill.** The workflow modifies NOTHING outside `_artifacts/` and never runs `git commit`/`push`. Fixing the bug is a separate, human-approved plan. Verified by a live drill reusing the Story 11.5 forced-failure pattern (`_test_scripts/sentry_smoke_test.py`): plant a P1 → run the workflow → Daniel confirms the report names the planted failure, the correct file, and a sane fix plan. Story stays in `review` until the drill passes.

---

## Tasks / Subtasks

- [ ] Task 1 — Author `/sudo-incident-response` (AC: 1, 2, 3, 4, 5)

  - [ ] Master command in `.agents/commands/sudo-incident-response.md`: argument parsing (`issue-id | latest`), then the five-step runbook (Sentry pull → log correlation → code-path map → build-history read → report write), each step with its graceful-degrade rule

  - [ ] `/sync-agents AGY_AVIATIONCHAT` to vendor it (command surface: Claude + opencode; Antigravity mirror per sync rules)

- [ ] Task 2 — Access plumbing docs (AC: 2, 3)

  - [ ] `.env.example`: add `SENTRY_AUTH_TOKEN` (commented, name-only) beside the existing `SENTRY_DSN` block; note MCP-first, token-fallback

  - [ ] Verify `gcloud` auth prerequisite documented in the command's preflight (project `aviationchat`)

- [ ] Task 3 — Incident-report template (AC: 6)

  - [ ] Template with the eight required sections embedded in the command (single source — no separate template file to drift)

- [ ] Task 4 — Live drill (AC: 7)

  - [ ] Re-run the 11.5 forced-failure smoke → invoke `/sudo-incident-response latest` → review report accuracy with Daniel → paste the report path + verdict in Completion Notes

---

## Dev Notes

### The triage runbook (what the command actually does)

```plaintext
/sudo-incident-response [issue-id | latest]
 1. SENTRY   — MCP: resolve issue (org aviationchat, project python-fastapi);
               pull metadata + newest event stack trace + release SHA
 2. LOGS     — gcloud logging read: Cloud Run service, ±15 min window,
               severity>=ERROR first, widen only if the trace is inconclusive
 3. CODE     — map top in-app frames → file:line; GitNexus context/impact
               for the failing symbol + blast radius (fallback: direct reads)
 4. HISTORY  — owning story via File List / component-spec match;
               read story + walkthrough + spec ONLY
 5. REPORT   — write incident-report.md to _artifacts/debugging/<date>_<slug>/;
               link it in chat; STOP (fix plan awaits "approved")
```

### Sentry access — two transports

- **Interactive (this story's lane):** Sentry MCP, already connected at the command center and verified 2026-07-09. Org `aviationchat`, project `python-fastapi`, region `https://us.sentry.io`.
- **Headless fallback (16.2 will need it; document now):** Sentry REST API with `SENTRY_AUTH_TOKEN`. Never committed; `.env.example` carries the name only — same convention as the existing `SENTRY_DSN` block at `.env.example:78-82`.

### Cloud Logging — the actual "check the logs" commands

There are no Firebase Functions; backend logs live in Cloud Logging under the Cloud Run service. Example shape (exact service name to be confirmed in Task 2 preflight):

```plaintext
gcloud logging read 'resource.type="cloud_run_revision" AND severity>=ERROR
  AND timestamp>="<event−15m>" AND timestamp<="<event+15m>"'
  --project=aviationchat --limit=100 --format=json
```

Firestore (`aviationchat-database`) is read-only consulted ONLY when the trace implicates data state (e.g. a malformed document) — via `firebase` CLI or the admin SDK script pattern, never writes.

### Is the build-history step overkill? (Daniel asked)

No — **if bounded**. Walkthroughs record "what fought back and how it was solved," which is exactly the context that turns a stack trace into a root cause fast (e.g. a known-fragile venv sync, a deliberate N_FLOOR guard). The cap in AC-5 (story file + walkthrough + spec, nothing more) keeps it to \~3 file reads instead of a tree crawl. If the owning story can't be identified in one match pass, the report says "no build-history match" and moves on.

### Guardrails (constitution-aligned)

- **Read-only triage.** The ONLY write is the report into `_artifacts/`. The proposed fix plan inside the report IS the `implementation_plan.md` for the follow-up fix session — plan-first gate intact.
- **Never commits, never pushes** (git-policy; same guardrail the autopilot carries).
- **No secrets in the report** — DSNs, tokens, and env values are referenced by name only.
- **PII**: user ids are SHA-256-hashed before they ever reach Sentry (`_before_send`); the report inherits that.

### Follow-up stories (sketches — registered with the epic if approved)

- **16.2 — Auto-trigger (true "always ready").** Recommended shape: Sentry alert-rule webhook → GitHub Actions `repository_dispatch` → `claude-code-action` runs the same runbook headless → report committed to a `claude/incident-<id>` branch + GitHub issue opened. Works while the PC is off. Needs: `ANTHROPIC_API_KEY` repo secret (billing decision), `SENTRY_AUTH_TOKEN` secret, report-delivery choice. Alternative (simpler, PC-bound): local cron polling Sentry via MCP.
- **16.3 — Frontend Sentry.** `@sentry/nextjs` + uncomment the ErrorBoundary capture (`ErrorBoundary.tsx:61-63`, tagged by zone). Privacy policy already discloses Sentry (`frontend/src/app/privacy/page.tsx:195`). Without this, browser-side crashes never enter the 16.1 pipeline at all.

### Project Structure Notes

- New: `.agents/commands/sudo-incident-response.md` (master, lobby) → vendored to `Projects/AGY_AVIATIONCHAT/.agents/commands/` + `.claude/commands/` via `/sync-agents`
- Modified: `.env.example` (one commented env-var name)
- No backend/frontend source changes in this story. No new dependencies.

## References

- \[Source: \_bmad/bmm/stories/story-11-5-production-alert-wiring.md — the alert chain + smoke-test pattern\]
- \[Source: backend/observability/sentry_init.py — gates, PII hashing, release tagging\]
- \[Source: backend/utils/rkp_loader.py:19-52 — fire_p1_alert\]
- \[Source: docs/gitnexus.md — code-graph tooling\]
- \[Source: \_artifacts/INDEX.md (project-local) — debugging bucket convention\]
- \[Verified 2026-07-09: Sentry MCP live — org `aviationchat`, project `python-fastapi`\]

<!-- HIGHLIGHT_MARK color="#93c5fd" text="3. **Frontend coverage.** &quot;If the site crashed&quot; currently only covers the backend. Wiring `@sentry/nextjs` + the ErrorBoundary TODO is **Story 16.3** — approve it as part of the epic or defer." anchor="3. **Frontend coverage.** &quot;If the site crashed&quot; currently only covers the backen" -->

<!-- CHECKPOINT id="ckpt_mrdm8y6x_u4k8nq" time="2026-07-09T14:42:42.585Z" note="auto" fixes=0 questions=2 highlights=0 sections="⚠️ OPEN DECISIONS FOR DANIEL" -->

<!-- CHECKPOINT id="ckpt_mrdmyo4x_l5tq0k" time="2026-07-09T15:02:42.609Z" note="auto" fixes=0 questions=3 highlights=0 sections="⚠️ OPEN DECISIONS FOR DANIEL" -->
