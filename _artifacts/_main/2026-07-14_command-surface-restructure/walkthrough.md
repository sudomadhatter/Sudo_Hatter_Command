# Command-Surface Restructure + E2E Gate — Walkthrough (2026-07-14)

**Why (Daniel):** the `/` menus had grown confusing — a Gemini-agent change had promoted the
incident drill into the Claude menu, robot-lane `_AP` entries sat in human menus, most `1_*`
commands were stale, there was no e2e gate before promoting `main_debug` → `main`, and the
825-line testing guide had stopped being usable.

## What changed

### Renames (git-mv, history preserved; all 4 platforms + AGY + Fresh)
| Old | New | Notes |
|---|---|---|
| `sudo-incident-response` | `security_team_aviationchat` | name now says what it is; **removed from the Claude menu** (platforms back to `[opencode, antigravity, codex]` — reverts Gemini commit e4d51de's claude add + its skill). AGY runbook's 2 prose refs updated. |
| `1_update-maps` | `sudo-update-maps` | incl. `check_maps.py` ×4, `record_map_changes.py` ×2, `sync-agents.ps1` wrapper-guard, skills dirs, 12 doc/INDEX refs |
| `1_live_testing_team` | `sudo-live-testing-team` | **revamped from a self-referential wrapper to a full command**: boots backend+frontend (absorbs `1_run-restart-dev-env`), watches backend logs, coaches the DevTools check, files researched bug docs (verified vs docs-say) that feed the sudo story flow |
| `1_push-to-main-and-deploy` | `sudo-push-e2e` | now the ONE shipping command: paths A (`main_debug` push) / B (full merge → `main`) / C (cherry-pick → `main`); **B/C hard-require `/sudo-e2e` GREEN**; adds the path-C back-merge reconcile (main never ahead) |

### New
- **`/sudo-e2e`** — runs the TEA-16 hermetic harness (`npm run test:e2e` in the project frontend:
  `firebase emulators:exec` auth+firestore `--project demo-agy` → Playwright journeys config →
  fresh :3100 dev server → seeded learners → network-mocked backend, **no uvicorn needed**;
  Java 17 auto-discovered). Reports `E2E GATE: GREEN/RED` — the promotion evidence.

### Deleted (recoverable from git)
`1_check-for-tech-stack-updates`, `1_clean-test-scripts`, `1_firebase-user-cleanup`,
`1_make-workflow-from-chat`, `1_run-all-tests-back_front` (③'s gate now runs suites directly —
`sudo-code-review` Step 3 patched), `1_run-restart-dev-env` (absorbed).

### Robot-lane rule (sync-agents.ps1)
`Sync-CommandDir -SkipAP`: `*_AP` commands vendor ONLY into project tool dirs (the autopilot
engines `Push-Location` into the project and resolve them there — verified in
`Projects/*/scripts/autopilot-dev-story*.ps1`). Lobby menus + all global caches skip them and
auto-purge strays every sync. Lobby's 6 `_AP` surface files removed.

### Guide rewrite
`_my_resources/diagrams_guides/workflows_tea_testing/sudo_workflows_testing.md`: 825 → ~280 lines —
lifecycle map + commands-by-lane + story loop/gate + P0–P3 + L1–L4 + ATDD/BDD plainly + TEA tool
cheat-sheet + security-team overview (2 mermaid diagrams, standards-compliant). Old content →
`tea_deep_reference.md` (header carries the old→new name map). Folder INDEX rows updated.

### Telegram / incident pipeline — verified healthy end-to-end
Sentry webhook → **relay** (`AGY backend/relay/app.py`): HMAC verify → kill switch
(`INCIDENTS_PAUSED`) → dedupe by `incident:<short-id>` label → scrubbed log pre-fetch → route by
`TARGET` (unknown = fail-safe suppress). **TARGET=github (primary)**: `repository_dispatch` →
`incident-response.yml` (least-privilege, concurrency-queued, WIF logging read, claude-code-action
v1 `prompt:` → runbook verbatim) → GitHub issue + `claude/incident-*` branch → **Telegram page
AFTER the report** (TL;DR + report link + branch + tap-to-copy Error-Team Prompt; HTML-escaped +
UTF-8-scrubbed; `continue-on-error` so a page glitch never fails triage) + 🛑 failure page so a
dead lane is never silent. **Fallback**: `POST /incident/fire` (bearer-token, fail-closed) →
issue + Sentry-fatal → email. **One cosmetic gap:** `backend/routers/incident.py`'s docstring
still calls the routines lane "primary" — as-built primary is the GitHub Actions lane (per the
yml header + 16.2 close). Flagged, not fixed (AGY code file, one-line doc edit, owner's call).

## Verification
- `check_maps.py` (lobby): all checks clean after repo-map regen
- `sync-agents -Maintained`: lobby 12 claude cmds / 39 opencode / globals 39+19+12; AGY + Fresh vendored
- Ghost purge: 88 old-name files/dirs removed from AGY+Fresh; globals mirror-purged; legacy OpenCode cache clean
- GitNexus: lobby re-indexed ✅ e808c85=HEAD; AGY re-indexed ✅ (was 2+ behind)
- doc-graph regenerated (237 docs); PS + Python parse checks green
- Fresh living-template: `docs/workspace-standard.md` re-vendored from lobby canon (also to AGY)

## Task Checklist
- [x] Rename ×4 + revamp ×1 + new ×1 + delete ×6, all surfaces
- [x] Robot-lane `_AP` exclusion (sync rule + lobby cleanup)
- [x] Guide rewrite + deep-reference companion + INDEX rows
- [x] Telegram/incident pipeline audit (healthy; 1 cosmetic docstring flag)
- [x] Sync fan-out + ghost purge + doc-graph + GitNexus re-index + repo-map
- [ ] Commits (three repos — see Your Actions)
- [ ] AGY `incident.py` docstring correction (optional, 1 line)

## Your Actions
```powershell
# LOBBY (Sudo_Hatter_Command) — the restructure
git add -A
git commit -m "refactor(toolkit): command-surface restructure — sudo-* renames, /sudo-e2e + /sudo-push-e2e gate, robot-lane _AP exclusion, guide rewrite" -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"

# AGY_AVIATIONCHAT — runbook refs + vendored toolkit + workspace-standard
cd Projects/AGY_AVIATIONCHAT
git add .github/claude/incident-triage.md .agents .claude .opencode docs/workspace-standard.md
git commit -m "chore(toolkit): vendor 2026-07-14 command renames (security_team_aviationchat, sudo-e2e gate set) + runbook drill-name refs" -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
cd ../..

# Fresh_Workspace_BMAD — vendored toolkit + workspace-standard
cd Projects/Fresh_Workspace_BMAD
git add .agents .claude .opencode docs/workspace-standard.md
git commit -m "chore(toolkit): vendor 2026-07-14 command renames + workspace-standard re-vendor" -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
cd ../..
```
