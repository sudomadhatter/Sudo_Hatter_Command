# `_artifacts/opencode/` — opencode's artifact namespace

All artifacts produced by **opencode** LLMs live under this folder, kept separate from Claude's
top-level `_artifacts/` so the two tools don't collide. Inside here, opencode applies the **same three
placement rules** the home base uses (full model → `../../_docs/workspace-standard.md`):

1. **Project work** → `opencode/<project>/<YYYY-MM-DD>_<slug>/` (the `<project>` = the `Projects/<name>/`
   folder name, e.g. `opencode/aviationChat-AGY/`). **Create the project folder if missing; otherwise reuse it.**
2. **Main / home-base / cross-project work** → `opencode/_main/<YYYY-MM-DD>_<slug>/`.
3. **Stories** → nest under the parent **epic folder**: `opencode/<project>/<epic>/<story>/`
   (create the epic folder if missing). Random/system tasks → `<YYYY-MM-DD>_<slug>/`; retired → `_archived/`.

## Each session folder carries
The same lean set as everywhere else: `implementation_plan.md` (approved before edits), `walkthrough.md`
(+ "Your Actions"), `task-list.md`; add `code-review.md` / `self-audit-stress-test.md` / `bug-list.md` when
those run.

## Logging
Add one row per session to the relevant `INDEX.md`: project work → that project's `_artifacts/INDEX.md`;
main work → the home-base [`../INDEX.md`](../INDEX.md).
