---
name: sentry-api-access-aviationchat
description: "How to manage AGY's Sentry (org aviationchat) programmatically — token in backend/.env, control-plane vs region hosts, the alert-rule API gotchas that cost four 400s"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 5472dcaa-aef1-45c2-a103-69869cb906bb
---

AGY's Sentry org `aviationchat` (project `python-fastapi`, US region) is manageable via API — no UI clicking needed:

- **Auth**: `SENTRY_AUTH_TOKEN` in `Projects/AGY_AVIATIONCHAT/backend/.env` (Daniel's user token, scopes `alerts:read/write, org:read, project:read`). The claude.ai Sentry MCP connector is READ-only for alert rules (no create/update tool in its catalog) — use curl + the token for writes.
- **Host split**: project/rule endpoints → `https://us.sentry.io/api/0/...`; integration-platform (sentry-apps, installations) endpoints → control plane `https://sentry.io/api/0/...` (region host 404s them).
- **Org is on the NEW "Monitors & Automations" UI** — never describe the old WHEN/IF/THEN builder to Daniel; either do it via API or read an existing rule first (`get_alert_rule` MCP) and mirror its vocabulary.
- **Internal-integration webhook apps** (e.g. `incident-relay-ff01f9`, uuid b01e07a0…): the "Alert Rule Action" toggle = `isAlertable` and was NOT actually on when Daniel created it (creation with blank webhook URL leaves it false). `PUT /api/0/sentry-apps/<slug>/ {"isAlertable": true}` works with the above token. Only AFTER that does the app appear as an action choice.
- **Correct action form** for such apps in issue alert rules: `sentry.rules.actions.notify_event_service.NotifyEventServiceAction` with `"service": "<app-slug>"` — NOT `NotifyEventSentryAppAction` (that's for apps with a settings schema; it 400s "Please configure your integration settings").
- **LevelFilter levels**: 50=fatal, 40=error (python logging scale). TaggedEventFilter match `ns` = "is not set".
- Live rule: `17286663` "P1 incident -> relay" = first-seen/regression (any) + level eq 50 + `incident_page` ns → notify incident-relay, **frequency 5** (lowered from 30 at close-out, 2026-07-13; PUT needs the FULL rule payload). The `incident_page is not set` filter is the [[incident-pipeline-16-2-operations]] loop guard — never remove it.
- **New-engine mapping**: the Monitors engine migrated rule 17286663 to workflow `3695667`; the legacy rule's `lastTriggered` can read `None` after cutover — check the workflow/Monitors UI for firing state. Numeric group id ≠ short-id (`7607174913` = `PYTHON-FASTAPI-B`) — resolve both forms before concluding two events exist.
- **Token has NO issue/event scopes** (Issue & Event = No Access, by design): org-issues list/resolve endpoints 403. Use the Sentry MCP (`search_issues`, `update_issue`) for issue ops — it's Daniel's OAuth with full scopes; curl+token only for rules/apps.
