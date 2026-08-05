# Command Center

A workspace that turns AI coding agents into a development team with actual process — planning gates,
tests that have to pass, code review, and a written record of every decision.

There is no framework here and no database. **The folder structure is the program.** Markdown files
describe how an agent should behave, and the agent becomes what the files describe. That means the
whole system is plain text, version-controlled, greppable, and yours — it lives in your repo rather
than a vendor's memory, and it drives Claude Code, opencode, Antigravity/Gemini and Codex equally.

**Two repos work together:**

| Repo | What it is |
|---|---|
| **[sudo-command-center](https://github.com/sudomadhatter/sudo-command-center)** ← you are here | The system. Where you work *from*. Holds the rules, commands, and your projects |
| **[sudo-project-skeleton](https://github.com/sudomadhatter/sudo-project-skeleton)** | The template you clone **per project** — stack, BMAD method, and test bench pre-wired |

---

## Before you start

| You need | Why | Check it |
|---|---|---|
| **Git** | everything is version-controlled | `git --version` |
| **GitHub CLI** ([cli.github.com](https://cli.github.com)) | creating repos and pushing from inside the flow | `gh --version` |
| **Python 3.11+** | the scripts, the linters, the test harness | `python --version` |
| **Node 20+** ([nodejs.org](https://nodejs.org)) | only if your project has a frontend | `node --version` |
| **An AI coding agent** | Claude Code, opencode, Antigravity, or Codex | — |

> **Platform note — read this one.** This system was built and is used on **Windows with PowerShell**.
> The helper scripts are `.ps1` and several paths are Windows-style (`.venv\Scripts\activate`).
>
> On **macOS or Linux** everything conceptual works — the rules, the commands, the agents, the whole
> method — but you will need [PowerShell 7](https://github.com/PowerShell/PowerShell) (`pwsh`) for the
> helper scripts, and you will hit backslash paths that need flipping. Nothing is unfixable; just know
> you are the first one down that road rather than expecting a paved one.

---

## Setup

**1. Clone it**

```bash
git clone https://github.com/sudomadhatter/sudo-command-center.git command-center
cd command-center
```

**2. Add your keys**

```bash
cp .env.example .env          # Windows: copy .env.example .env
```

Open `.env` and fill in the **REQUIRED** block — just two entries:

- `GITHUB_PAT_CLASSIC` — a GitHub token. Create at
  [github.com/settings/tokens](https://github.com/settings/tokens) → *Generate new token (classic)* →
  tick **`repo`** and **`workflow`**.
- `GITHUB_REPO` — your GitHub username or org.

Everything below that block is optional and each one is off until you fill it in. **You do not need an
Anthropic API key** if you use Claude Code with a Pro or Max subscription — the CLI signs in on its
own.

**3. Authenticate GitHub**

```bash
gh auth login
gh auth status                 # should say "Logged in to github.com"
```

**4. Install the Python tools**

```bash
python -m pip install -r requirements.txt
```

**5. Check it works**

```bash
python .agents/scripts/tests/run_all.py
```

You should see `6/6 files passed`. If you do, the system is live.

**6. Open the folder with your agent and type:**

```
/sudo-tour
```

---

## What happens next

`/sudo-tour` is a six-stop guided run: from this clone to a story that actually shipped, on a real
project of yours rather than a toy. It resumes wherever you left off — just run it again. Stop 2
walks you through cloning the project skeleton and putting it on GitHub.

**Training mode is on.** The `.training-mode` file at the root tells agents to teach as they go:
explain before executing, define every term, and answer questions with the reasoning behind them.
Turn it off whenever you are ready:

```
/training off
```

It is reversible (`/training on`), and nothing in the system is gated behind it — what is left when it
goes is the real system, not a reduced one.

---

## The two rules everything rests on

**Plan first.** No file is modified until you approve a written plan. The agent researches, writes an
`implementation_plan.md`, shows it to you in chat, and stops. This will feel slow exactly once. Then
it will feel like the only sane way to work with something that can rewrite forty files while you get
coffee.

**`main` is not the working branch.** Day-to-day work lands on `main_debug`. Promoting to `main` is a
deliberate human decision. "It works" and "it is safe to ship" are different claims, and two branches
is what keeps them different.

---

## The dev loop

Once you have a project and a backlog, every story runs the same three steps:

| | Command | What it does |
|---|---|---|
| ① | `/sudo-write-story-tests` | Writes the story spec, then **failing** acceptance tests — before any code |
| ② | `/sudo-dev-story-tests` | Plans, stops for your approval, implements until the tests pass |
| ③ | `/sudo-code-review` | Adversarial review + test and clean-code gates → PASS / CONCERNS / FAIL |

Then `/sudo-update-sprint-memory` closes the story and files what was learned.

Each story runs in its own **git worktree** — a separate folder sharing one repository — so parallel
work never collides. Ask any agent here to explain any of this; that is what training mode is for.

---

## What is in here

| Folder | What it holds |
|---|---|
| `.agents/` | The toolkit — `rules/` (how agents behave), `commands/` (the `/slash` commands), `skills/` (specialist know-how, loaded on demand), `scripts/`, `templates/` |
| `.claude/` `.opencode/` `.antigravity/` `.agent/` | Per-tool copies so commands resolve in whichever agent you run. Generated by `/sync-agents` — **never hand-edit them** |
| `docs/` | Reference shelf: the site map, the workspace standard |
| `_bmad/` | The BMAD method module — agile lifecycle from product brief to retrospective |
| `Projects/` | Empty. Your projects go here, each its own git repo |
| `_artifacts/` | Empty. Session memory — plans and walkthroughs, written as you work |
| `AGENTS.md` | **The brain.** The routing table: *this kind of work → read these files* |
| `router.md` | Your project directory. Empty until you add one |

`CLAUDE.md` and `GEMINI.md` are one-line adapters that both say "read `AGENTS.md`" — one front door
per tool, one brain.

---

## If something breaks

| Symptom | Cause | Fix |
|---|---|---|
| `/sudo-tour` does nothing | Your agent has not picked up the commands | Restart the agent session. If it persists, run `/sync-agents` |
| `gh: command not found` | GitHub CLI not installed | [cli.github.com](https://cli.github.com), then `gh auth login` |
| `run_all.py` fails on import | Wrong Python, or deps not installed | `python --version` (need 3.11+), then re-run step 4 |
| Scripts fail on macOS/Linux | They are PowerShell | Install [PowerShell 7](https://github.com/PowerShell/PowerShell) and run with `pwsh` |
| The agent talks like it knows you | `operator-profile.md` is still the blank template | Fill it in — see below |

---

## Three things to personalise early

1. **`.agents/rules/operator-profile.md`** — describes who the agent is working *for*. It ships as a
   blank template on purpose: a profile describing someone else is worse than none, because the agent
   would confidently optimise for the wrong reader. Fill it in; it changes how every reply is written.
2. **`router.md`** — the routing table. Add a row per project as you create them.
3. **`.agents/maintained-projects.txt`** — the list the fan-out commands sweep.

---

## A note on what you are looking at

This is a generated edition of a working command center — exported by a script that ships the system
and none of its owner's projects, history, or notes. So this is real machinery that has been used in
anger, with the personal layer removed, rather than a demo built to be shown.

How it works: a manifest lists what ships, so privacy is reviewed once as a list rather than
re-decided file by file; a substitution pass rewrites the names that remain; and a leak scan with no
exception list runs last — any hit blocks the push.

The export tooling itself is the one thing not in this repo, and for a reason worth knowing. Its
manifest's search terms *are* the private names, so running the substitution pass over it rewrites
every rule into an identity mapping — a copy that would report hundreds of substitutions while
scrubbing nothing. A privacy tool that cannot survive its own pass has to stay home.
