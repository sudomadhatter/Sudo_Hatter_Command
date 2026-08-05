# Project Skeleton

A ready-to-build project workspace: the routing brain, the agent toolkit, the BMAD method, the test
bench, and a FastAPI + Next.js stack, already wired together.

Companion to **[sudo-command-center](https://github.com/sudomadhatter/sudo-command-center)** — the
system you work *from*. This repo is what you clone *into it*, once per project.

> # ⛔ This is a template. Clone it — do not build in it.
>
> Every project starts as a **clone** of this repo. Never build inside the template itself.
>
> Building here tangles your first project with template history and leaves you without a clean
> template for your second. It is the most common way to ruin a good skeleton, and it is silent —
> everything works right up until you want project number two.

---

## Before you start

| You need | Version | Check |
|---|---|---|
| **Git** | any | `git --version` |
| **Python** | 3.11+ (3.13 recommended) | `python --version` |
| **Node** | 20+ — only if you want the frontend | `node --version` |
| **GitHub CLI** | any | `gh --version` |

Optional, and only when your project actually needs them: a **Google AI / Gemini** key
([aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)) and a **Firebase/GCP**
project. The skeleton runs without either — you just will not have AI or a database until you add them.

> **Platform note.** Built and used on **Windows with PowerShell**. On macOS/Linux you will need
> [PowerShell 7](https://github.com/PowerShell/PowerShell) for the helper scripts, and some paths are
> Windows-style. Everything conceptual works; some paths need flipping.

---

## Setup

**1. Get your own copy.** Either click **"Use this template"** on GitHub (cleanest — new repo, clean
history, one click), or clone and reset:

```bash
git clone https://github.com/sudomadhatter/sudo-project-skeleton.git my-project
cd my-project
rm -rf .git          # PowerShell: Remove-Item -Recurse -Force .git
git init
```

Put it inside your command center at `Projects/my-project` so the routing finds it.

**2. Replace the placeholders.** Search the repo for `{{` — every hit needs your value:

| Placeholder | Replace with | Lives in |
|---|---|---|
| `{{PROJECT_NAME}}` | your project name | `_bmad-output/project-context.md`, `_bmad-output/active-context/active-context.md`, `.antigravity/mcp.json`, `.env.example` |
| `{{PROJECT_DESCRIPTION}}` | one line | `_bmad-output/project-context.md` |
| `{{TECH_STACK_*}}` | your stack (defaults in `docs/tech-stack.md`) | `_bmad-output/project-context.md` |
| `{{ARCHITECTURE_PATTERN_DESCRIPTION}}` | your architecture, one line | `_bmad-output/project-context.md` |

Then re-point the workspace at its own new name: `AGENTS.md` §9, the SessionStart hook path in
`.claude/settings.json`, and the interpreter paths in `pyrefly.toml` and `pyrightconfig.json`.

> **Miss one and the failure is silent** — memory resolves to a folder that does not exist and the
> hook points at nothing, with no error to tell you. Search for `{{` and for `sudo-project-skeleton`
> before moving on, and confirm both come back empty.

**3. Backend**

```bash
python -m venv .venv
.venv\Scripts\activate                 # macOS/Linux: source .venv/bin/activate
pip install -r backend/requirements.txt
```

**4. Frontend** (skip if you do not need one)

```bash
cd frontend && npm install && cd ..
```

**5. Environment**

```bash
mkdir auth_keys
copy .env.example auth_keys\.env       # macOS/Linux: cp .env.example auth_keys/.env
```

Fill in only what your project actually uses. All of it is optional to start.

**6. Check it works**

```bash
.venv\Scripts\python.exe -m pytest --collect-only -q
```

Tests should be *collected* without errors. **Always spell out the venv path** rather than a bare
`python` — a bare `python` finds whatever interpreter is first on PATH and produces confident, wrong
answers about missing dependencies.

**7. Push it**

```bash
git checkout -b main_debug
git add . && git commit -m "chore: initial commit from skeleton"
gh repo create my-project --private --source . --remote origin
git push -u origin main_debug
```

---

## Then build

New to all this? Run **`/sudo-tour`** from the command center — it walks every step above and then
builds a story with you.

Otherwise, the ladder:

```
/bmad-product-brief          # what are we building and why?
/bmad-prd                    # what exactly does it need to do?
/bmad-create-architecture    # how will we build it?
/bmad-create-epics-and-stories
/sudo-create-epic-sprint     # the board + risk scores
```

**Stop after each one and check it says what you meant.** A wrong brief becomes a wrong PRD becomes
twelve wrong stories; the cost multiplies at every rung, and catching it early costs one sentence.

---

## The dev loop

| | Command | What it does |
|---|---|---|
| ① | `/sudo-write-story-tests` | Story spec, then **failing** acceptance tests — before any code exists |
| ② | `/sudo-dev-story-tests` | Plans, **stops for your approval**, implements until the tests pass |
| ③ | `/sudo-code-review` | Adversarial review + test and clean-code gates → PASS / CONCERNS / FAIL |

Close out with `/sudo-update-sprint-memory`, which files what was learned so the next session starts
informed.

**Tests come first for a reason.** A test written after the code tends to assert whatever the code
happens to do. Written first, it asserts what you actually wanted — and watching it fail proves it
*can* fail, which a test added afterwards never demonstrates.

**Every story gets its own git worktree** — a separate folder sharing one repository — so parallel
work never collides. Without it, whoever pushes last inherits everyone else's changes and a commit
named for one story quietly ships four.

**`main` is not the working branch.** Work lands on `main_debug`; promoting to `main` is a deliberate
human decision.

---

## The test gate

Quality gates are armed here, not bolted on later. `/sudo-code-review` runs the suite, a traceability
check (does every acceptance criterion have a test proving it?), an NFR audit, and a test-quality
review. It can return **CONCERNS** or **FAIL**, and it is supposed to.

Story risk scoring (P0–P3, set during `/sudo-create-epic-sprint`) decides how much of that a story
earns. Not everything deserves the full gate; deciding deliberately is the point.

---

## Layout

```text
my-project/
├── AGENTS.md              # THE BRAIN — workspace map + routing table (read first)
├── CLAUDE.md / GEMINI.md  # one-line adapters → "read AGENTS.md"
│
├── .agents/               # vendored toolkit: rules · skills · commands · workflows · scripts
├── .claude/ .opencode/    # per-tool copies (incl. the SessionStart hook) — generated, never hand-edit
│
├── docs/                  # repo-map · workspace-standard · tech-stack
├── scripts/               # repo-map generator · drift check
│
├── _bmad/                 # BMAD method module (BMAD-owned — never hand-edit)
├── _bmad-output/          # BMAD state: project-context · active-context · specs · sprint board
├── _artifacts/            # session memory — plans, walkthroughs (empty; fills as you work)
│
├── backend/               # FastAPI + ADK scaffold
├── frontend/              # Next.js / React / TypeScript scaffold
│
├── _my_resources/         # the repo owner's personal area — agents do not edit or cite it
└── firebase.json · pyproject.toml · .env.example · …
```

---

## How the structure works

An agent never reads the whole repo. `AGENTS.md` holds a routing table — *this kind of work → read
these files* — so each task loads only what it needs. Small context, faster answers, less invention.

Three layers: **entry** (`CLAUDE.md`/`GEMINI.md` → `AGENTS.md`), **routing** (the table inside
`AGENTS.md`), and **skills** (`.agents/skills/<name>/SKILL.md`, pulled on demand, never globally).

Session memory is project-local: plans and walkthroughs land in this repo's `_artifacts/`, so history
travels with the code. The live pick-up brief is `_bmad-output/active-context/active-context.md` — any
agent can resume from it with no chat history.

---

## If something breaks

| Symptom | Cause | Fix |
|---|---|---|
| Imports unresolved in the editor | Editor is on the wrong interpreter | Point it at `.venv`, then reload |
| `pytest` reports missing deps that are installed | Bare `python` found a global interpreter | Use `.venv\Scripts\python.exe -m pytest` |
| SessionStart hook errors | Placeholder paths not updated | Recheck step 2 — `.claude/settings.json` and `AGENTS.md` §9 |
| Agent starts building in the template | You are in the template, not a clone | Clone first (step 1) |

---

## Key documentation

| Document | Read it when |
|---|---|
| `AGENTS.md` | Always first — the brain + routing table |
| `docs/repo-map.md` | "Where is X?" |
| `docs/workspace-standard.md` | Shaping or maintaining a workspace |
| `docs/tech-stack.md` | You need the stack and versions |
| `.agents/rules/INDEX.md` | "Which rule governs this?" |

---

> **Keep it generic.** This carries the **stack**, not a **product**. Fill in domain specifics *after*
> you clone — that is what keeps the template reusable.
