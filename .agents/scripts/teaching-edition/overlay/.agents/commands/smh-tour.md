---
description: Guided onboarding for a new command-center owner, sourced live from the current workflow SOP and command bodies.
---

# /smh-tour — build the first real project while learning the system

This is a checkpointed curriculum, not a second workflow manual. The authoritative procedure is
[`docs/_scc_sops_prds/workflows_testing_SOP.md`](../../docs/_scc_sops_prds/workflows_testing_SOP.md).

## Live-source hard stop

At the start of **every stop**:

1. Open the current local SOP and read the section(s) named by that stop.
2. Open every command body the stop is about under `.agents/commands/`.
3. If the command and SOP disagree, stop and identify the mismatch. Never teach remembered mechanics,
   repair the disagreement silently, or substitute plausible instructions.
4. Explain what will happen before running a command, preserve every approval/write/merge gate, then
   explain the result and the next checkpoint.

The SOP changes as the system changes. This rule is why the tour follows those changes without copying
hundreds of lines that will become stale.

## State and resuming

Look in `_artifacts/_main/onboarding/` for the runtime file named `tour-state.md`. If it exists, read
it and offer to resume at the first incomplete stop. If it does not exist, begin at Stop 0. After each
checkpoint the operator accepts, write the completed stop, chosen command-center name, chosen project
name, and relevant paths to that file. Never store credentials there.

Training mode is optional throughout. `/smh-training off` changes the voice, not the tour or system.

## Stop 0 — name the command center and learn the two laws

Read SOP **Start here**, §1–§4. Ask what the owner wants to call their command center. When they are
still downloading, teach the destination-name form:

```bash
git clone https://github.com/sudomadhatter/sudo-command-center.git <chosen-command-center-name>
cd <chosen-command-center-name>
```

For a downloaded archive, rename the extracted folder before opening it. The folder name is their
local identity; it does not rewrite every internal source identifier.

Teach the two laws using the SOP's current words: plan first and the owner alone marks work done. Show
where `AGENTS.md`, `router.md`, `.agents/`, `Projects/`, and `_artifacts/` fit. Checkpoint: the owner can
say what the agent proposes, what the owner approves, and what survives to the next session.

## Stop 1 — verify the command-center shell

Read SOP §10 and §14 plus `.agents/scripts/INDEX.md`. Verify Git, PowerShell 7, the platform's Python
spelling, GitHub authentication, and the generated-shell gate. In a teaching export, run
`python3 .agents/scripts/validate_teaching_edition.py .` (on Windows, use the available Python
spelling); do **not** substitute the source repository's `tests/run_all.py` suite, whose source-only
export tests are deliberately absent. Explain optional environment keys from `.env.example`; never
request or echo secret values. State plainly: **this shell has no Jira board and no active Jira
binding.** Checkpoint: the teaching validator passes and the owner knows which missing optional
integration can safely remain missing.

## Stop 2 — ask for the first project name, then clone the paired skeleton

Open `.agents/commands/smh-new-project.md` and `.agents/scripts/new-project.ps1`. Ask:
**“What do you want to name your first project?”** Validate that the answer is a safe single folder
name and confirm the destination `Projects/<name>` does not already exist.

Then invoke `/smh-new-project <name>`. It clones
`https://github.com/sudomadhatter/sudo-project-skeleton` into `Projects/<name>`, removes the template's
history, initializes the project's own repository, and arms its repo-local hooks. Complete the command's
printed wiring steps: placeholders, localized repo map, and a routing row. Do not invent a remote URL or
create/publish a GitHub repository without the owner's separate authorization.

Jira remains optional. Only after this project actually has its own Jira site/project/board should the
owner copy `Projects/<name>/.agents/jira.conf.example` to
`Projects/<name>/.agents/jira.conf`, set that project's `JIRA_SITE` and `JIRA_KEYS`, verify the active
site from `acli jira auth status` matches `JIRA_SITE`, and arm its repo-local enforcement marker.
Checkpoint: `Projects/<name>/AGENTS.md` exists, its local git history starts with the scaffold commit,
and `router.md` reaches it.

## Stop 3 — choose the right lane

Read SOP §5, §8, and §9. Work one real upcoming change through the lane chooser:

- a BMAD story uses the story lane;
- bounded project work may use `/cicd-quick-dev`;
- command-center Task work uses `/smh-quick-dev`;
- a command-center change that cannot break the system may qualify for `/smh-quick-fix`.

Define epic, story, Task, branch, worktree, artifact, and gate on first use. Checkpoint: the owner can
name the lane and the evidence that selected it.

## Stop 4 — run one real story through the gated loop

Read SOP §6, §10, §11, §14 and the current bodies for:

1. `/cicd-write-story-tests` — create the story and prove the acceptance test is red for the right reason;
2. `/cicd-dev-story-tests` — write the plan, stop for literal approval, implement, widen tests, certify;
3. `/cicd-code-review` — adversarial review and the real test/clean-code gate;
4. `/cicd-close-story-merge-tree` — save, land on the epic branch, push, then close the ticket;
5. `/cicd-push-e2e` — gate and ship the finished epic to `main` only with owner sign-off.

Use the owner's real first project and real story. Never seed a toy change merely to manufacture a
green tour. If the project has no Jira board yet, explain the dependency and stop before a workflow
whose current command requires a key; do not fake one. Checkpoint: the owner has seen RED→GREEN,
approval, review verdict, and the distinction between landing a story and shipping an epic.

## Stop 5 — operate the system without losing the thread

Read SOP §7, §12, §13, §15, §16 and §17–§19. Cover the current Task close-out
`/smh-close-task-merge-tree`, switching machines, the live queue when Jira exists, autopilot as an
optional project-local engine, incident routing, and the command atlas. Show where the owner can read
the depth instead of memorizing it.

Checkpoint: summarize the owner’s actual command center and first project, show the remaining actions,
and offer `/smh-training off`. Do not turn it off unless asked.
