# Git at Story Close-Out (Multi-Team Repo)

> **Context:** A project may be worked by multiple agents/teams in parallel on the same branch.
> At any moment several agents' uncommitted changes can coexist in the working tree.
> These rules keep history clean and each team's work independently revertable. This rule
> supersedes the old blanket "never run git commit/push — provide the command" hard-stop.

## When you may commit

ONLY at **story close-out** — after the code review has passed and the story is ready to flip to
`done`. NEVER commit mid-work, and never as a substitute for the plan-approval gate. (Mid-work, the
old discipline stands: no commits.)

## Commit ONLY your own work — explicit paths

- Stage with **explicit paths** for the files YOU changed this session:
  `git add path/one path/two …`.
- **NEVER `git add -A`, `git add .`, or `git add -u`** — they sweep the other parallel teams'
  uncommitted work into your commit. This is the single most important rule here.
- Before committing, **verify the staged set**: `git diff --cached --stat` must show ONLY your
  files. If anything else appears, unstage it (`git restore --staged <path>`) before continuing.
- Scope the commit message to your story only.

## Ask before pushing — push separately

- After committing, **ASK Daniel before you `git push`.** The commit is yours to make at close-out;
  the push is the outward, shared action and gets an explicit go-ahead.
- Push your work as **its own commit, separate** from other teams' changes — never bundle.
- If the push is rejected (remote moved under you), **STOP and report**. Do not force-push, and do
  not blind-rebase while other teams' uncommitted work sits in the tree.

## What still holds

- **Plan-first gate unchanged:** no project-file edits without an approved `implementation_plan.md`.
- **Close-out is earned:** only commit when the story is genuinely review-passed and ready for `done`
  (see `completion-not-illusion`).
- The `walkthrough.md` "Your Actions" still documents the exact commit + push, so the record exists
  whether you run it or Daniel does.
