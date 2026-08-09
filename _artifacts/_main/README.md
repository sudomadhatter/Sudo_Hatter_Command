# `_artifacts/_main/` — the home-base bucket (formerly `_home`)

The bucket for the **command center's own work** done from the home base: the routing system, the master
`.agents/` toolkit, the workspace standard, repo-map/INDEX maintenance, and any cross-project work that
isn't owned by a single `Projects/<name>/`. This is rule 2 of the placement standard
(full rules → [`../README.md`](../README.md) and [`../INDEX.md`](../INDEX.md)).

> Renamed from `_home` → `_main` on 2026-06-26. Non-exempt project work always goes to the project's own
> `_artifacts/`; only Sudo-managed exceptions registered in `router.md` use sibling named buckets.

## Structure
- **Current general / system task** → `<YYYY-MM-DD>_<slug>/` (date first so folders sort chronologically).
- **Historical month** → `<YYYY>/<MM>/<YYYY-MM-DD>_<slug>/`; each populated month carries its own
  `INDEX.md`, while `_main/INDEX.md` remains the complete routing ledger.
- **Retired** → `_archived/`.

## Continuity
`active-context.md` here is the pickup/handoff brief for home-base work. The home-base ledger is the
shared [`../INDEX.md`](../INDEX.md); append a row there at hand-off.
