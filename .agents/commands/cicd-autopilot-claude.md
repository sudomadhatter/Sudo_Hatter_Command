---
description: Autopilot v3 (CLAUDE) - the lead session that drives ONE story through the EXISTING workflow doors, one headless child per step, each child a Wonderland seat, every step recorded on the ticket. Escalates to the operator's phone and parks at review-ready; it can never land.
platforms: [claude]
---

# /cicd-autopilot-claude - the autopilot's lead session (v3)

> **Rules in force for this command:**
> - `.agents/rules/code-standards.md` §6.5 — **disposition**: when a review comes back with
>   findings, you are the assessor, not the lens. All three YES to act — is it REAL (a concrete
>   failure, not a *"may be"*) · does it change BEHAVIOUR · is it in THIS diff. "It's cheap" is not
>   a reason, and a `NO-GO` from the audit is not yours to overrule
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — the operator's launch word is a **batch approval**
>   scoped to the charter rows below and to this story only. It is not approval for anything else,
>   and it does not travel to the next story
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push
>   `main`, never force-push; landing is not yours at all (see the charter)
> - `.agents/rules/worktree-per-story.md` — one story, one worktree, one `claude/*` branch
> - `.agents/rules/smh-target-resolution.md` — bind ONE target, never operate on the lobby
> - `.agents/rules/artifacts-always-first.md` — the run's ledger and walkthrough live in the story's
>   own artifact folder, never here
> - `.agents/rules/constitution.md` — its **Ask First** list is the escalation list. A dependency, a
>   schema, security rules, CI or an environment config is the operator's call, always

> **The manual for this lane is [`docs/_scc_sops_prds/autopilot_SOP.md`](../../docs/_scc_sops_prds/autopilot_SOP.md)** —
> the layers, the charter, the escalation round trip, the seat pins and the measured failure modes,
> with the diagrams. Read it before changing anything here.

**What this is, in one paragraph.** You are the lead. You do not write code, run tests, or read
transcripts. You call `.agents/scripts/autopilot_run.py` once per workflow step; it launches a fresh
headless `claude -p` child wearing one Wonderland seat, running an **existing** door by name; the
child answers with a small JSON result and the runner posts that result to the ticket as a comment.
You read one paragraph per step and decide what happens next, inside the charter below. The doors,
the rules and the seats are the same files a human session uses — this lane owns **no copy of any of
them**, which is why an edit the operator makes is live on the next launch with no sync anywhere.

Argument: the story, optionally prefixed by a project name — e.g. `AGY_AVIATIONCHAT 14.2`.

---

## Step 0 — Bind the target, and prove the machine can do this

**0.1 Resolve the project.** Same pattern as every `/cicd-*` door:

- **Self fast-path:** no `Projects/` subfolder here means you ARE the project — `PROJECT_ROOT = .`.
- **Inline override:** if `$ARGUMENTS` begins with a folder name under `Projects/`, that is the
  target; consume that token and write the name alone into `.agents/active-project.txt`.
- **Active pointer:** else read `.agents/active-project.txt`.
- **Ask:** else STOP and ask which project. Never guess, never run against the lobby.

Echo `Target: <PROJECT_ROOT>` before any work. **Then read `PROJECT_ROOT/.agents/INDEX.md` and honor
its `Load` column** — binding a project is loading its law (`project-law`). A thin project with no
INDEX is a STOP, not a shrug.

**0.2 Prerequisites, each measured rather than assumed.** Refuse to launch if any fails, and say
which one:

| Check | How | Why it is here |
|---|---|---|
| CLI version | `claude --version` ≥ 2.1.259 | `--permission-prompts none` lands there. Its default is `host`, and a headless child HAS no host — so below the floor a child that hits a prompt has nobody to answer it. ⛔ Check the binary on `PATH`, not this session: a stale launcher symlink can leave `claude` older than the CLI you are typing in |
| the runner | `.agents/scripts/autopilot_run.py --help` exits 0 | A missing runner must fail here, not per step |
| the work | a **story** is `ready-for-dev` with its failing tests on disk; a **quick-fix Task** already carries its acceptance criteria on the ticket | The autopilot implements; it does not invent the work |
| the branch | the epic branch is checked out and **not behind `origin/main`** | An in-flight epic that has drifted is a merge conflict waiting to be discovered by a robot |
| the ticket | the story's Jira key resolves | The ticket IS the handoff; without it there is no run record |

**0.3 Open the story's worktree** and bootstrap its assets (`link-worktree-assets.py` from the
lobby; thin projects have no linker of their own). One story, one worktree, one lock.

**0.4 Name the tier.** One dial sets every model, every effort and both budgets for the run.
**The operator names it; you judge it only when he does not** — and if you judge, say which and why
in one line before the first child, because he is paying for the answer.

| | easy | medium | hard |
|---|---|---|---|
| the seats that write code | their own pins (Sonnet 5) | Opus 5 · high | Opus 5 · **xhigh** |
| `gnat` — read-only lookups | Haiku 4.5 · low | **unchanged** | **unchanged** |
| `march-hare` — the lead | Opus 5 · high | Opus 5 · high | **Fable 5.1 · high** |
| the reviewer | Opus 5 | **Fable 5.1 · high** | **Fable 5.1 · high** |
| per child · per run | $6 · $25 | $12 · $60 | $20 · $120 |

Pass it as `--tier easy|medium|hard` on **every** call in the run. `--model` / `--effort` still win
at the call site when one step needs more than its tier gives it — raise the step, never the run.

⭐ **The reviewer never runs the model that wrote the code.** Sonnet builds and Opus reviews; Opus
builds and Fable reviews. A reviewer sharing the builder's model shares its blind spots, and a fresh
session buys independence from the author's *context*, not from the author's *failure modes*. The
suite asserts this for every tier, so do not "tidy" two rows onto one model.

⛔ **The Gnat does not move.** A read-only lookup does not get harder because the ticket did, and if
one ever needs judgment the charter already says escalate rather than guess.

⛔ **`--tier hard` cannot change YOUR model** — you are the operator's session, not a child. At
`hard` the lead should be on Fable 5.1; say so and let him switch, or note in the run record that
the lead ran on something else. The runner pins children and nothing else.

⛔ The per-child figure is a **soft** cap — the CLI stops the *next* turn, not the current one, and
it has been measured overspending by 10x. The run ceiling is the one the runner enforces itself, off
the ledger, before each launch. Say both numbers out loud before you start.

---

## Step 1 — The launch scope: what the operator's word covers

The operator's launch word is a **batch approval under `000-PLAN-FIRST-GATE`**, scoped to the rows
marked **lead** below, for **this story only**. Say this back to him in one line before the first
child, and have the runner write it into the ticket's first comment so the scope is on the record
rather than in your context.

| Gate | Who | What you do |
|---|---|---|
| ② Step 2 `continue` | **lead** | Pass it. The audit ran as a Queen child in a fresh session — that is what the stop existed to guarantee |
| ② Step 2.5 questions before code | **lead** | Answer from the story, the plan, and a Gnat lookup. **If you would have to guess, escalate instead** |
| Audit verdict `NO-GO` | **escalate** | The plan-first gate re-arms and re-scoping is his call, not yours |
| A new dependency, schema change, security rule, CI or environment config | **escalate** | The constitution's Ask First list wins. There is no "self-install and log it" in this lane |
| Deleting a file | **escalate** | Ask First, always |
| ③ verdict `PASS` | **lead** | Post review-ready and park. He still owns review-to-done |
| ③ verdict `CONCERNS` or `FAIL` | **lead**, once | One fix child in the lane, then one **fresh** review child. A second non-PASS **escalates**. `CONCERNS` never ships by itself |
| Landing on the epic branch or `main` | **never** | The runner has no verb for it. This is not a rule you could break |
| Anything a door marks `PIPELINE_BLOCKER` | **escalate** | Whatever it is, the door already decided it is his |

---

## Step 2 — The loop

For each workflow step, in order, call the runner **once**:

```
python3 .agents/scripts/autopilot_run.py run \
  --door <the door, by name> --seat <seat> --cwd <the story worktree> \
  --args "<what the door takes>" --key <JIRA-KEY> --stage <n> \
  --budget-usd <per child> --run-cap-usd <the run's ceiling>
```

⛔ **Pass the door's NAME, never its text.** You have not read the door and you do not need to. The
child loads it through the same launcher skill your own session uses, at the moment of use.

⛔ **`--cwd` is where the CHILD stands, and that is where its door must live.** The child resolves
its launcher skill from its own working directory — nothing is inherited from you. A `/cicd-*` door
belongs to the command centre and targets a project *named in `--args`*, so for those the child
stands in **the command centre**, not in the project: a thin project carries its tier-2 law but none
of the lobby's doors or skills, and a child launched there would find no such command and improvise.
Point `--cwd` at a project tree only for a door that tree actually owns. The runner refuses the
mistake and says which one it was, but the refusal costs a step — get it right in the call.

**The seats, and the order for a story.** ① writes the tests, ② plans and builds, ③ reviews:

| Stage | Door | Seat | Note |
|---|---|---|---|
| 1 | `/cicd-dev-story-tests <story>` (to its Step 2 stop) | `white-rabbit` | Returns the plan path |
| 2 | `/cicd-self-audit` on that plan | `queen-of-hearts` | Returns `GO` or `NO-GO` |
| 3 | `/cicd-dev-story-tests <story>` (Step 2.5 → Step 5) | `cheshire-cat` | The build |
| 4 | `/cicd-code-review <story>` | **`--review`, no seat** | Independence is the point |
| 5 | the fix, only on CONCERNS/FAIL | `cheshire-cat` | One cycle, in the lane |
| 6 | `/cicd-code-review <story>` again | **`--review`, no seat** | Fresh session at the new sha |

**The quick-fix route — a ticket with no story file, no sprint row and no epic branch.** A
project Task (a performance fix, an asset, a copy change) rides `/cicd-quick-dev`, which is ONE door
holding both its own build and its own review gate:

| Stage | Door | Seat | Note |
|---|---|---|---|
| 1 | `/cicd-quick-dev <KEY>` | `cheshire-cat` | The build, plus the door's own first-pass gate |
| 2 | `/cicd-code-review <KEY>` | **`--review`, no seat** | The gate whose verdict counts |
| 3 | the fix, only on CONCERNS/FAIL | `cheshire-cat` | One cycle, in the lane |
| 4 | `/cicd-code-review <KEY>` again | **`--review`, no seat** | Fresh session at the new sha |

⛔ **A seated child cannot fan out review lenses, and that is why stage 2 is not optional here.** No
seat carries the `Task` tool, so `/cicd-quick-dev`'s own Step 3 gate probes `inline (no subagent
tool)` and drops the Blind Hunter. It reports that rather than hiding it, and it is still worth
running — but it is a first pass, never the run's verdict. The **no-seat** review child inherits the
default tool set, fans out properly, and is the verdict you report. ⛔ Never read the quick-dev
door's own verdict as the run's.

**Choosing the route:** the story route when the work has a story file on disk and an epic branch;
the quick-fix route when it has neither. If you cannot tell which, it is not a quick fix — escalate.

A read-only lookup — "which does the epic's architecture note actually say?" — is a `gnat` child.
It is cheap and it is the honest alternative to guessing at a Step 2.5 question.

**Launch it in the BACKGROUND and watch it.** A step is a headless child that can work for many
minutes and prints nothing until it returns, so a foreground call makes the whole run look like a
hang — and the operator's only options are to wait blind or kill it. Start the step in the
background, watch its worktree and its output, and say what it is doing as it goes. Keep a visible
checklist of the stages so the panel advances while it works. ⛔ **Silence is not progress.** If you
cannot say what the current child is doing, neither can he, and a run he cannot see is a run he
cannot stop.

**Read the exit code, not the prose:**

| Exit | Meaning | You |
|---|---|---|
| `0` | `done` | Dispatch the next step |
| `3` | `needs_human` | **Escalate** — see Step 2.5 |
| `4` | `blocked` | Escalate. The child could not proceed and said why |
| `1` | `failed` | The result could not be read, or the child errored. ⛔ **READ THE SUMMARY BEFORE RETRYING** — it carries the child's own words, and a child that did the whole job can still answer in prose instead of the schema. Check the worktree: if the work is there, the step is DONE and unverified, not undone. A blind retry pays twice. Retry **once** only when nothing was produced, then escalate. Never retry a budget cut — that is a deliberate halt |
| `2` | the runner refused | A missing door, a bad review combination, or the run ceiling. Nothing was spent. Fix the call or stop |

**Answering a child that asked a question.** The only `--resume` in a run is delivering an answer to
the child that asked. Pass `--fork-of <that session id>` and the answer in `--args`. ⛔ Never resume
to start a *new* step on an old context — a fresh session per step is what keeps stage 2 and stage 4
honest, and the runner records every session id on the ticket so the count is checkable.

### Step 2.5 — What an escalation looks like

Two things, both of them, every time:

1. **`AskUserQuestion`** with the real options and your recommendation first. He is deciding a
   product question; do not hand him the engineering.
2. **The ticket**, via the runner's `needs_human` status, so the comment leads with the literal
   `Needs Mr. Hatter` line and carries the child's question. His phone reads the ticket; your chat
   may not be in front of him.

Then wait. An escalation you answered yourself is the failure this whole charter exists to prevent.

---

## Step 3 — Park

**On `PASS`:** flip the story to `review`, move the ticket to In Review with its Dev Record, and post
one line — *`<story>` review-ready, PASS at `<sha>`, N fresh sessions, $X.* Then **stop**. The
operator runs `/cicd-close-story-merge-tree` when he chooses.

**On anything else:** park with the reason and the evidence, and say plainly what is owed and by
whom. A parked run that reports a clean stop is worth more than one that kept going.

### What you decided on his behalf — post it before you park

The charter says what you MAY pass without him. Nothing yet says what you DID. Close every run with
one ticket comment listing each charter row you actually exercised and the call you made: the Step 2
`continue` you passed, every question you answered from the repo rather than asking, each Gnat lookup
and what it settled, and any finding you assessed as not-real under `code-standards.md` §6.5.

⛔ **A soft "I would normally have checked this with him" is not an escalation — it is a decision,
and it goes on this list.** That distinction is the one the retired lane got right and it is the
whole accountability half of an unattended run: without the list, a charter is a permission slip
nobody ever audits, and the first time a run does something surprising there is no way to tell
whether the scope was wrong or the lead simply exceeded it.

⛔ **Never land.** Not the epic branch, not `main`, not "it was green so I merged it". The runner has
no verb for it and neither do you.

---

## What this lane owns, and what it borrows

It owns five things and nothing else: how to launch a child, the result schema, the `jira_feed.py
step` verb, the seat renderer, and the budget table. **Everything else is borrowed at the moment of
use** — the doors from `.agents/commands/`, the law from `.agents/rules/`, the seats from the same
six masters `.roomodes` renders for Zoo. When the workflow changes, nothing here changes. That is
the whole design, and it is why there is no sync step in this document.
