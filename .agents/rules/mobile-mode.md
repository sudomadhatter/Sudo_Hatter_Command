---
name: mobile-mode
description: "The web/mobile lane. Activates automatically when the session runs in a remote/cloud container (Claude Code on the web or phone), or when Daniel says 'mobile'. Adapts git, the approval gate, artifacts, and verification for a phone — where there is no terminal to paste into and typing is expensive. Overrides the desktop defaults in git-policy.md and artifacts-always-first.md for the duration of the session."
activation: On Demand (auto on web/mobile)
---

# Mobile Mode

> **Why this exists.** The rest of the rule set was written for a desktop dev loop: Daniel runs git in
> a terminal, types "approved", and runs the app locally. On a phone none of that is true — there is no
> terminal to paste into, the keyboard is the slowest part of the session, and the app only runs in the
> remote container. This rule is the **mobile lane**: a small set of explicit overrides that make the
> command center usable from a phone. It supersedes the desktop defaults it names, and nothing else.

## When this lane is active

- **Auto:** the session runs in a remote / cloud container (Claude Code on the web or the mobile app).
  This is the normal case for phone use.
- **Manual:** Daniel says "mobile" / "mobile mode" in any session.
- **Off:** a local desktop session — the desktop defaults (`git-policy.md`, `artifacts-always-first.md`)
  apply unchanged.

When active, announce nothing ceremonial — just behave per the overrides below.

## Override 1 — Git  (supersedes `git-policy.md` "Default")

On the phone there is no terminal, so the "hand Daniel the command" default does not work. Instead:

- **Sync first (always).** Before committing, `git fetch` and pull `--ff-only` if the branch is behind
  origin — phone and desktop share branches, so never commit on a stale one. If it has diverged, STOP
  and flag it. (Full rule → `git-policy.md` → "Sync-first".)
- **Commit and push for him.** After approved work, commit your OWN files and push to the designated
  feature branch — no waiting for a terminal that does not exist.
- **Keep the safe-commit mechanics from `git-policy.md`.** Explicit paths only (`git add path/one path/two`);
  **NEVER `git add -A` / `git add .` / `git add -u`**; verify `git diff --cached --stat` shows only your
  files before committing; scope the message to this task.
- **Push retries:** on network failure, retry 4× with exponential backoff (2s, 4s, 8s, 16s). Use
  `git push -u origin <branch>`. If the push is rejected because the remote moved, STOP and report — do
  not force-push or blind-rebase.
- **Ask before the PR.** Opening / converting a draft PR is an outward action — present it as a
  **tap-confirm** (see Override 2) and wait for the tap before creating it.
- **"Your Actions" becomes "review the PR."** The `walkthrough.md` closing section links the pushed
  branch / draft PR (`review PR #N`) instead of pasting a git command Daniel can't run.

## Override 2 — Approval gate  (supersedes the typed "approved" gate in `artifacts-always-first.md`)

Typing the exact word "approved" on a phone keyboard is the worst part of mobile.

- Present the plan **inline in chat, TL;DR first** (the headline + the files it touches), then offer a
  tappable **Approve / Change** via `AskUserQuestion`.
- A tap on **Approve IS the gate** — it is equivalent to typing "approved." A tap on **Change** means
  revise, do not build.
- Everything else about the gate holds: **no project-file edits before the tap**, and **one plan per
  code-touch** (an epic-level tap is not a license to skip per-story taps).
- Use the same tap-confirm for the pre-PR check in Override 1.

## Override 3 — Lighter, chat-first artifacts

The artifact set from `artifacts-always-first.md` still applies — `implementation_plan.md`,
`walkthrough.md`, `task-list.md`, plus the `INDEX.md` row and `active-context.md` update. But on mobile:

- **TL;DR-first and terse.** Lead every artifact and every chat reply with the headline; details below.
- **Chat replies stay short** — a summary plus the PR/branch link, not a file dump. Daniel reads the
  chat on a small screen; he opens files only when he wants to.
- The walkthrough is still honest (real test output, deviations) — just front-loaded and lean.

## Override 4 — Verification runs here, not on Daniel's phone

- **The agent runs tests / the app in the container** and pastes a short result. Never ask Daniel to
  run a command, start a server, or open a local URL on his phone.
- Keep the evidence bar from `karpathy-guidelines.md` / `completion-not-illusion.md`: paste actual
  output, never claim a pass you didn't observe. Mobile changes *who* runs it, not *whether* it's proven.

## Hard stops (mobile lane)

- Mobile mode relaxes *how* git and approval happen — it NEVER relaxes the safe-commit mechanics
  (explicit paths, no `git add -A`), the no-edit-before-approval rule, or the evidence bar.
- Still **ask before the PR** and before any other outward/irreversible action — a tap, not silence.
- If you are unsure whether the session is mobile, ask once; default to the desktop rules until told.
