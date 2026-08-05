---
name: agy-school-identity-ghost-doc-window
description: "A school is schools/{slug} with the code as a QUERIED FIELD — so a superseded code-keyed doc that still carries `code` keeps answering by-code lookups. The migration now retires those docs itself (rename, never delete); the window is CLOSED, and the shape is the lesson."
metadata: 
  node_type: memory
  type: project
  originSessionId: db7ff31d-93b1-482f-8606-5d35ebbd0bfd
  modified: 2026-07-30T17:34:40.594Z
---

Story 21.4 (2026-07-30) re-keyed the registry: `schools/{school_id}` is a stable name-slug, `code` is a
rotatable FIELD, and lookups are `.where("code","==",…)` queries. `AdminScope`/JWT/`scoped_user_query` all
bind `school_id` — **never** re-introduce a code-reading gate.

## The hazard, and why it is worth remembering after the fix

`migrate_school_identity.py` copies each old `schools/{code}` doc forward and — per the never-delete ruling
([[agy-archive-never-delete-ruling]]) — leaves the original standing. But the original still carried its
`code` field, and lookups had become code-FIELD queries. So a *superseded* doc kept answering:

- a redemption could land in the **ghost** → `users/{uid}.school_id = <the code>`, invisible to any
  `school_id`-scoped roster, never activatable;
- **a rotated code did not go dead** — the ghost still matched it. AC2 open for as long as the ghost stood.

**The generalisable shape: when you change a lookup from BY-ID to BY-FIELD, every superseded record that
still carries that field becomes a live duplicate.** Never-delete plus field-queries is the trap; either
one alone is fine. Ask it of any migration that re-keys a collection.

## Resolved (2026-07-30 follow-on, on `main_debug`)

The migration now **retires** each old doc as its last per-school act: `code` → `code_retired`, plus
`migrated_to` and `retired_at`. It deletes NOTHING — the document, its members and the code's value all
survive, so the ruling holds and it stays reversible. Safe mid-rolling-deploy too: pre-21.4 code resolves
`schools.document(code)` by DOCUMENT ID and never reads the field. Pinned by `MIG-008` (dead code stays
dead after a rotation) and `MIG-009` (a retired doc must not re-migrate forever — `_is_old_model` checks
`migrated_to` FIRST, because a retired doc has no `code` left and the old `data.get("code") or doc_id`
fallback read its own id back).

Deleting the retired docs is now optional tidiness. Also fixed the same day: a migration **re-run after a
rotation** used to revert it (the payload copied `code` from the SOURCE doc; every other field already
preferred the LIVE target) — see [[agy-ruff-changed-files-is-a-hard-gate]] for the sibling
"test the re-run after a real mutation, not after nothing" lesson.

Related: [[agy-redemption-has-two-doors]], [[agy-domain-is-always-org]], [[agy-school-seat-cap-fails-closed]].
