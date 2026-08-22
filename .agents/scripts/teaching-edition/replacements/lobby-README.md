# Command Center — Teaching Edition

This repository is the home base for an AI-assisted development system: the rules, commands, gates,
documentation, and the `Projects/` lobby from which you operate real project repositories.

It works as a maintained pair:

| Repository | Role |
|---|---|
| [`sudo-command-center`](https://github.com/sudomadhatter/sudo-command-center) | The home base you open with your agent. Shared workflow law lives here. |
| [`sudo-project-skeleton`](https://github.com/sudomadhatter/sudo-project-skeleton) | The project-level starting point cloned once per real project into `Projects/<name>`. |

The command center begins as a shell: `Projects/` is empty and there is **no Jira board** or active
Jira binding. The onboarding agent asks what to name your command center and first project, then builds
that first project from the paired skeleton.

## 1. Choose the command-center name

The final argument to `git clone` is your local command-center name:

```bash
git clone https://github.com/sudomadhatter/sudo-command-center.git <chosen-command-center-name>
cd <chosen-command-center-name>
```

If you downloaded an archive for inspection, rename the extracted folder before opening it. The tutor
can find the shell from its live SOP without Git metadata; branch, sync, and shipping workflows still
require a real clone. The folder name chooses local identity and does not rewrite source files.

## 2. Verify the basics

You need Git, PowerShell 7 (`pwsh`), Python 3.11+, and one supported agent surface: Claude Code,
Codex, opencode, or Antigravity/Gemini. GitHub CLI is needed when you later create/publish remotes.

```bash
git --version
pwsh --version
python3 --version                 # Windows may use: python --version
python3 .agents/scripts/validate_teaching_edition.py .   # Windows may use: python
```

The root `.env.example` lists optional command-center integrations. Copy it to `.env` only for values
you actually use; never commit `.env` or paste secrets into the example.

## 3. Open the command center and start the tutor

Start a new agent session at this repository root and invoke:

```text
/smh-tour
```

The tour reads `docs/_scc_sops_prds/workflows_testing_SOP.md` and the current command bodies at every
stop. It does not carry a second frozen explanation of the development workflow.

During onboarding the agent asks:

> What do you want to name your first project?

It then runs `/smh-new-project <name>`, which clones
`https://github.com/sudomadhatter/sudo-project-skeleton` into `Projects/<name>`, drops the template's
history, initializes the project's own repository, and completes the local routing/placeholders.
Creating or publishing a remote repository remains your separate decision.

## Jira comes later

The command-center shell has no Jira board. A new project also starts without an active Jira binding,
so its commit gate does not demand a board that does not exist.

When you create a Jira site/project/board for that project:

1. Copy `Projects/<name>/.agents/jira.conf.example` to
   `Projects/<name>/.agents/jira.conf`.
2. Replace the placeholder site/key with that project's values.
3. Add the workflow columns the SOP describes, including `To Do Next` if you want operator ranking.
4. Arm that project's repo-local Jira enforcement marker only after the board works.

Each project owns its board and key. This exported shell never points at the source owner's board.

## Training mode

The committed `.training-mode` sentinel ships teaching on. The ignored `.training-mode-off` marker
lets the command change that local preference without dirtying tracked files. Control it at any time:

```text
/smh-training status
/smh-training off
/smh-training on
```

Turning it off changes only the teaching voice and leaves `git status` clean. The plan, worktree,
test, review, and shipping gates remain the real system.

## The workflow in one screen

The current procedure always lives in
[`docs/_scc_sops_prds/workflows_testing_SOP.md`](docs/_scc_sops_prds/workflows_testing_SOP.md).
The tutor opens these sections instead of copying them:

- §5 chooses the lane.
- The story loop is `/cicd-write-story-tests` → `/cicd-dev-story-tests` →
  `/cicd-code-review` → `/cicd-close-story-merge-tree`.
- A finished epic ships through `/cicd-push-e2e`.
- Command-center Task work uses `/smh-quick-dev` → `/smh-code-review` →
  `/smh-close-task-merge-tree`.

Every commit-producing lane gets its own worktree. No implementation begins until an approved plan
exists, and no agent decides on your behalf that work is done.

## What the main folders mean

| Path | Purpose |
|---|---|
| `AGENTS.md` | Root routing law and safety gates. |
| `.agents/` | Authored commands, rules, skills, scripts, and generated platform workflows. |
| `docs/_scc_sops_prds/` | Operator procedures; the workflow SOP answers “what do I type?” |
| `Projects/` | Initially empty. Each named project is its own repository. |
| `_artifacts/` | Plans, walkthroughs, and continuity records created while you work. |
| `router.md` | Maps incoming work to the correct named project. |

This teaching edition is generated from a working command center through an allow-list, personal-file
transforms, a secret/name leak scan, and a fresh-shell validator. The generated tree carries no source
git history; publish it as a new repository rather than as a fork.
