# `_artifacts/` — shared memory (home base)

Plans, walkthroughs, and continuity owned by the home base, plus Sudo-managed exception histories.

| Question | Where it is answered |
|---|---|
| **Where does my session folder go?** | [`AGENTS.md`](./AGENTS.md) — the local law, and the **single** authority on placement. It is auto-attached via the adapters, so it is the copy that actually reaches an agent. |
| What already happened here? | [`INDEX.md`](./INDEX.md) — the session ledger, newest rows first. |
| What is the plan-first protocol? | [`.agents/rules/artifacts-always-first.md`](../.agents/rules/artifacts-always-first.md) |
| What is the whole workspace model? | [`docs/workspace-standard.md`](../docs/workspace-standard.md) |

> **⛔ The store is `_artifacts/` — never `_claude_artifacts/` or `_opencode_artifacts/`** (both retired and
> deleted). Every agent and tool writes here — `/bmad-dev-story`, `/bmad-quick-dev`, autopilot, or a hand
> session alike. If a story's `source:` line or an old note points at `_claude_artifacts/`, that is dead
> history — write here.

> **Placement is deliberately NOT restated on this page.** It used to be — in `AGENTS.md`, here, and in
> `INDEX.md`'s header — and the copies drifted apart. Per `workspace-standard.md` ("a Tier-2 `AGENTS.md` is a
> digest that points at canon — never a second canonical copy"), the law now lives in exactly one place.
> **If you are about to add placement rules to this file, add them to [`AGENTS.md`](./AGENTS.md) instead.**

## What each session folder carries
| File | When |
|---|---|
| `implementation_plan.md` | always — approved **before** any edits |
| `walkthrough.md` | at close — the ONE closing doc: what changed + **real pasted test output**, ending in `## Task Checklist` (final TodoWrite snapshot) + `## Your Actions`. **No separate `task-list.md`** |
| `code-review.md` / `self-audit-stress-test.md` / `bug-list.md` | when those run |

## Buckets you will see at the root
Each is a **parent** for session folders, never a session folder itself — see `AGENTS.md` for which one your
work belongs to.

- `Fresh_Workspace_BMAD/` and `OpenChat-Openrouter/` — the complete registered Sudo-managed exception set.
  These are operational histories, not the default for projects.
- `_main/` — the home base's own work: the standard, the master `.agents/` toolkit, the router, lobby wiring,
  and anything with no home yet. Current sessions sit directly beneath it; older sessions may be grouped
  under `<YYYY>/<MM>/`. (Formerly `_home`.)
- `_archived/` — optional retired-history bucket when one exists. **Archive, never delete**: old `INDEX.md`
  rows keep pointing at old paths, so a deleted folder turns a valid row into a dead one.

Inside a project bucket, story work nests under `epic_<E>/<story>/` — the epic folder houses all of its
stories (e.g. `epic_9/story-9.4-ios-shell/`, or an autopilot run `epic_14/2026-06-27_autopilot-14-6/`).

## Where a project's history actually lives
Every non-exempt project's history lives only in `Projects/<name>/_artifacts/`, even when work begins from
the lobby. The two exceptions are listed above and in `router.md`.

## Continuity
`active-context.md` is the pickup/handoff brief for its owning store: an exception's named bucket or
`_artifacts/_main/` for home-base work. Non-exempt projects use their project-local continuity contract.

The `INDEX.md` ledger is reconciled in batch by the SessionStart hooks and `/update-maps-indexes` — don't
hand-append a row every session.
