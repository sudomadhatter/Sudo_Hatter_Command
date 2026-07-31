# `_artifacts/` — LOCAL LAW (project-owned memory)

This project owns its session history here, regardless of where a chat starts or which tool runs it.

## The law

- Read `INDEX.md` before walking the tree.
- Story work goes under `epic_<E>/<story>/`.
- Debugging and ad-hoc repro work goes under `debugging/<YYYY-MM-DD>_<slug>/`.
- Project infrastructure or work with no better home goes under `_main/<YYYY-MM-DD>_<slug>/`.
- Never place a dated session folder directly at the `_artifacts/` root.
- Start with an approved `implementation_plan.md`; close with one `walkthrough.md`.
- Retire history to `_archived/`; never create a duplicate home-base project bucket.
