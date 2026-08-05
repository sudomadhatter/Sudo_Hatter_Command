---
description: Guided first run of this system — six stops from empty clone to a shipped story. Resumable, skippable, and it teaches by doing real work on a real project rather than a toy.
---

# /sudo-tour — the guided first run

Six stops, from a fresh clone to a story that actually shipped. **You do real work on a real project**
— there is no sandbox and no toy example, because a tour you cannot reuse teaches nothing.

Argument (`$ARGUMENTS`): a stop number to jump to (`3`), or empty to resume where they left off.

> **Training mode should be on** for this (a `.training-mode` file at the repo root). If it is off,
> say so once and offer `/training on` — then respect the answer either way.

---

## Resuming — detect, do not count

**Never track progress in a counter or a file.** Look at the world and work out which stop they are
on. A newcomer who closes the terminal, comes back tomorrow, and types `/sudo-tour` should land in
the right place with no bookkeeping.

| Stop | Done when… |
|---|---|
| 1 | `.env` exists and `GITHUB_PAT_CLASSIC` has a non-placeholder value |
| 2 | a folder exists under `Projects/`, it is a git repo, it has an `origin` remote, and its current branch is `main_debug` |
| 3 | that project has `_bmad-output/sprint-status.yaml` listing at least one story |
| 4 | at least one story on that board is `done` |
| 5 | — (always available; it is the wrap-up) |

Announce where you are resuming and why, in one line: *"Keys are set and you have a project, so we
pick up at stop 3 — turning an idea into a backlog."* Then ask before proceeding.

---

## Stop 0 — What this thing is

No commands. Two minutes of plain language.

Cover, in this order:

1. **The folder IS the program.** There is no framework and no database. Markdown files describe how
   the agent should behave, and the agent becomes what the files say. That is why the work is
   portable, greppable, and yours — it lives in your repo, not in a vendor's memory.
2. **Least-context loading.** The agent never reads the whole repo. `AGENTS.md` holds a routing table
   — *this kind of work → read these files* — so each task pulls only what it needs. Small context,
   fast answers, fewer hallucinations.
3. **The two rules above every command**, which they will meet within minutes:
   - **Plan first.** No file gets modified until they approve a written plan. The agent researches,
     writes `implementation_plan.md`, shows it in chat, and stops. Say plainly that this will feel
     slow exactly once, and then it will feel like the only sane way to work.
   - **`main` is not yours to push.** Day-to-day work lands on `main_debug`. `main` is the owner's
     alone. More at stop 2.

End with: *"Everything after this is you doing it. Ready?"*

---

## Stop 1 — Keys

Goal: the system can reach GitHub and a model.

1. Show them `.env.example` and have them copy it to `.env`.
2. Walk the **REQUIRED** block only — `GITHUB_PAT_CLASSIC` and `GITHUB_REPO`. Link the token page,
   name the two scopes (`repo`, `workflow`), and explain what each is for. Do not walk the optional
   block; mention it exists and move on.
3. **Anthropic key:** explain honestly that it is *not* needed if they drive Claude Code with a Pro or
   Max subscription — the CLI authenticates on its own. Set it only for API billing or headless runs.
4. Verify, do not assume:
   ```
   gh auth status
   ```
   If `gh` is not installed, that is the lesson right there — install it, then re-run.

**Teach here:** why `.env` is gitignored and `.env.example` is not, and that a leaked token is leaked
even if the commit is deleted afterwards.

---

## Stop 2 — A project, on GitHub

Goal: a real repo of their own, on the right branch.

1. **The skeleton is a template, not a workshop.** Say it before anything else: they clone it *per
   project* and never build inside it. Building in the template tangles their first project with
   template history and leaves them no clean template for the second.
2. Clone the project skeleton into `Projects/<their-name>`, drop its git history, and re-init:
   ```
   git clone <skeleton-repo-url> Projects/<name>
   Remove-Item -Recurse -Force Projects/<name>/.git
   git -C Projects/<name> init
   ```
   (If the skeleton is published as a GitHub *template repository*, "Use this template" does this in
   one click with clean history — prefer it and say why.)
3. Create the remote and push:
   ```
   gh repo create <name> --private --source Projects/<name> --remote origin
   git -C Projects/<name> checkout -b main_debug
   git -C Projects/<name> add . ; git -C Projects/<name> commit -m "chore: initial commit from skeleton"
   git -C Projects/<name> push -u origin main_debug
   ```
4. **Why `main` is a trap.** `main_debug` is where work lands. `main` is the production line and the
   owner's call alone. The point is not ceremony — it is that "it works on my branch" and "it is safe
   to ship" are different claims, and the branch split is what keeps them different.
5. Add a row for the project in `router.md`, and a line in `.agents/maintained-projects.txt`. Explain
   that this is how the fan-out commands find it later.
6. **Install the dependencies now**, so the test bench is real before stop 4 needs it:
   ```
   cd Projects/<name>
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```
   Confirm it works — `.venv\Scripts\python.exe -m pytest --collect-only -q` — and say why the venv
   path is spelled out rather than a bare `python`: a bare `python` finds whatever global interpreter
   is on PATH and produces confident, wrong answers about missing dependencies.

---

## Stop 3 — From an idea to a backlog

Goal: their own idea, turned into stories a machine can build.

This is the ladder. Run it **from inside their project**, one rung at a time, and after each one show
what it produced and why the next rung needs it:

| Command | Produces | Why the next step needs it |
|---|---|---|
| `/bmad-brainstorming` | raw ideas, widened then narrowed | a brief written from one idea is a guess |
| `/bmad-product-brief` | what it is and who it is for | the PRD needs an audience to be specific about |
| `/bmad-prd` | requirements + acceptance criteria | stories without ACs cannot be tested or closed |
| `/bmad-create-architecture` | the technical spine | stories that ignore architecture contradict each other |
| `/bmad-create-epics-and-stories` | epics broken into stories | the board needs items |
| `/sudo-create-epic-sprint` | the sprint board + risk scores | the dev loop reads the board |

**Do not run these back to back without stopping.** After each, ask whether the output matches what
they actually meant. This is the single highest-leverage habit in the whole system: a wrong brief
becomes a wrong PRD becomes twelve wrong stories, and the cost of the mistake multiplies at every
rung. Catching it here costs one sentence.

**Teach here:** acceptance criteria are the contract. When they write one, ask "how would a machine
prove this is done?" If there is no answer, the criterion is a wish, not a requirement.

At the end they will risk-score each story P0–P3. Explain what the levels buy: how much testing a
story earns, and therefore how long it takes. Not everything deserves the full gate.

---

## Stop 4 — Build one, for real

Goal: one story from red test to merged, using the loop they will use forever.

Pick the **smallest** story on their board. If nothing is small, say so and help them split one —
learning the loop on a big story teaches the story, not the loop.

Then the three steps, explaining each before running it:

1. **`/sudo-write-story-tests`** — writes the story spec, then failing acceptance tests **before any
   code exists.** Show them the tests failing. This is the point where most people push back, so
   answer it head on: a test written after the code tends to assert what the code happens to do. A
   test written first asserts what you actually wanted, and the red run proves the test can fail —
   an assertion that never fails is decoration.
2. **`/sudo-dev-story-tests`** — plans, stops for their approval, then implements until the tests
   pass. **The approval stop is the whole system in one interaction.** Read the plan with them. Point
   out that they can redirect here for free, and that this is the cheapest moment in the entire
   lifecycle to change their mind.
3. **`/sudo-code-review`** — adversarial review plus the test and clean-code gates, ending in a
   verdict. If it comes back CONCERNS or FAIL, **do not fix it silently** — walk them through the
   finding. A review that only ever passes is theatre.

Then land it and close out with `/sudo-update-sprint-memory`.

**Teach here:** the work happened in a git *worktree* — a separate folder sharing one repository — so
this story's edits never mixed with anything else. Show them `git worktree list`. The reason is
concrete: several efforts against one checkout means whoever pushes last inherits everybody's work,
and a commit titled for one story quietly ships four.

---

## Stop 5 — What was holding the net

Goal: show them the machinery that was running underneath, then get out of the way.

1. **What ran without being asked:** the plan-first gate, the artifact trail in `_artifacts/`, the
   test gate, the clean-code audit, the repo-map drift check on session start. Point at the actual
   files produced during stop 4 — the plan they approved, the walkthrough, the review section.
2. **The one thing still on them:** promoting `main_debug` to `main`. Nothing automates that, by
   design.
3. **Where to look things up:** `AGENTS.md` for routing, `.agents/rules/INDEX.md` for which rule
   governs what, `docs/` for the reference shelf, `/sudo-*` for the dev loop.
4. **Mention autopilot, do not teach it.** There is an autonomous multi-stage loop. Say it exists,
   say it is worth trying once the manual loop is second nature, and say plainly that its engine has
   no single canonical copy so it varies between projects — which is exactly why it is a bad place
   to learn.
5. **Offer the switch once:**
   > That is the tour. Training mode is still on — I will keep explaining as we go. When you would
   > rather I just work, `/training off`. You can turn it back on any time, and nothing in the system
   > is gated behind it.

   Offer once. If they decline, drop it and never raise it again.

---

## Notes

- **Any stop can be skipped**, and stops can run out of order. If they skip stop 3 and ask for stop 4,
  say what stop 4 will be missing (a board, a story) and let them decide.
- **Never fake a result** to keep the tour moving. If a command fails, that failure IS the stop —
  debug it together. A tour that only works when nothing goes wrong teaches nothing about this system,
  where things going wrong is the normal case and the gates exist for exactly that reason.
- **Do not lecture.** Each stop is a conversation with commands in it, not a lesson with a quiz.
