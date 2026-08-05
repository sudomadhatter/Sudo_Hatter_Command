# Project Skeleton

A ready-to-build project workspace: the routing brain, the agent toolkit, the BMAD method, the test
bench, and a FastAPI + Next.js stack, already wired together.

> # ⛔ This is a template. Clone it — do not build in it.
>
> Every project starts as a **clone** of this repo. Never build inside the template itself.
>
> Building here tangles your first project with template history, and leaves you without a clean
> template for your second. It is the single most common way to ruin a good skeleton, and it is
> silent — everything works right up until you want project number two.
>
> ```bash
> git clone <this-repo-url> my-project
> cd my-project
> rm -rf .git          # PowerShell: Remove-Item -Recurse -Force .git
> git init
> ```
>
> Or click **"Use this template"** on GitHub, which does the same thing with clean history.

---

## Quick start

**1. Clone it** (above), then **2. replace the placeholders:**

| Placeholder | Replace with | Lives in |
|---|---|---|
| `{{PROJECT_NAME}}` | your project name | `_bmad-output/project-context.md`, `_bmad-output/active-context/active-context.md`, `.antigravity/mcp.json`, `.env.example` |
| `{{PROJECT_DESCRIPTION}}` | one line | `_bmad-output/project-context.md` |
| `{{TECH_STACK_*}}` | your stack (defaults in `docs/tech-stack.md`) | `_bmad-output/project-context.md` |
| `{{ARCHITECTURE_PATTERN_DESCRIPTION}}` | your architecture, one line | `_bmad-output/project-context.md` |

Then re-point the workspace at its own new name: `AGENTS.md` §9 and the SessionStart hook path in
`.claude/settings.json`, plus the interpreter paths in `pyrefly.toml` and `pyrightconfig.json`.

> **Miss one and the failure is silent** — memory resolves to a folder that does not exist and the
> hook points at nothing, with no error to tell you. Search the repo for `{{` and for the old name
> before you move on.

**3. Backend:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
```

**4. Frontend:**
```bash
cd frontend && npm install
```

**5. Environment:**
```bash
mkdir auth_keys
copy .env.example auth_keys\.env      # then fill in your real values
```

**6. Build:** `/bmad-product-brief` → `/bmad-prd` → `/bmad-create-architecture` →
`/bmad-create-epics-and-stories` → `/sudo-create-epic-sprint`.

New to all of this? Run **`/sudo-tour`** from the command center instead — it walks every step above
and then builds a story with you.

---

## The dev loop

Once you have a backlog, every story runs the same three steps:

| | Command | What it does |
|---|---|---|
| ① | `/sudo-write-story-tests` | Story spec, then **failing** acceptance tests — before any code exists |
| ② | `/sudo-dev-story-tests` | Plans, **stops for your approval**, implements until the tests pass |
| ③ | `/sudo-code-review` | Adversarial review + test and clean-code gates → PASS / CONCERNS / FAIL |

Close out with `/sudo-update-sprint-memory`, which files what was learned so the next session starts
informed.

**Tests come first for a reason.** A test written after the code tends to assert whatever the code
happens to do. Written first, it asserts what you actually wanted — and watching it fail proves it
*can* fail, which an assertion added afterwards never demonstrates.

**Every story gets its own git worktree** — a separate folder sharing one repository — so parallel
work never collides in the same files. Without it, whoever pushes last inherits everyone else's
changes and a commit named for one story quietly ships four.

**`main` is not the working branch.** Work lands on `main_debug`; promoting to `main` is a deliberate
human decision. "It works" and "it is safe to ship" are different claims.

---

## The test gate

Quality gates are armed here, not bolted on later. `/sudo-code-review` runs the suite, a traceability
check (does every acceptance criterion have a test that proves it?), an NFR audit, and a test-quality
review. It can return **CONCERNS** or **FAIL**, and it is supposed to.

Story risk scoring (P0–P3, set during `/sudo-create-epic-sprint`) decides how much of that a story
earns. Not everything deserves the full gate; deciding deliberately is the point.

---

## Layout

```text
your-project/
├── AGENTS.md              # THE BRAIN — workspace map + routing table (read first)
├── CLAUDE.md / GEMINI.md  # one-line adapters → "read AGENTS.md"
│
├── .agents/               # vendored toolkit: rules · skills · commands · workflows · scripts
├── .claude/ .opencode/    # per-tool copies (incl. the SessionStart hook) — generated, never hand-edit
│
├── docs/                  # reference shelf: repo-map · workspace-standard · tech-stack
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

Session memory is project-local: plans and walkthroughs land in this repo's `_artifacts/`, so the
history travels with the code. The live pick-up brief is
`_bmad-output/active-context/active-context.md` — any agent can resume from it with no chat history.

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
