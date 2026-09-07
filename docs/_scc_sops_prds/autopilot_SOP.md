# The Autopilot SOP

*The robot that runs your own workflow for you. This page is where the autopilot is explained and
where it is kept current — the main [`workflows_testing_SOP.md`](workflows_testing_SOP.md) links
here rather than carrying a second copy.*

---

## 1. What it is, in one paragraph

You type one command and go to bed. A **lead** session — an ordinary Claude chat running
`/cicd-autopilot-claude` — walks one story through the **same doors you would type by hand**, calling
a small script once per step. Each call launches a fresh headless Claude process, a **child**, wearing
one of the six Wonderland seats, running one door **by name**. The child answers with a short
structured result; the script writes that result onto the Jira ticket as a comment and the lead reads
one paragraph, not a transcript. When something needs you, it lands on your phone as a ticket comment
that begins `Needs Mr. Hatter`. When the story is review-ready it stops. It cannot merge anything.

**The one design decision everything else follows from:** the autopilot owns **no copy** of any door,
rule or seat. It passes names, never text. Edit a door in the morning and the robot runs the new one
that night, with no sync step, no regeneration and nothing to forget.

---

## 2. The three layers

**A door** is a slash command you type today. **A seat** is one Wonderland team member. **A child** is
one headless process running one step. **The runner** is the script that launches children and holds
the rules an agent must not be trusted with.

```mermaid
flowchart TD
    YOU(["you\nyour chat, or your phone"]) -->|"one command"| LEAD["THE LEAD\nan ordinary Claude session\nrunning /cicd-autopilot-claude"]
    LEAD -->|"one call per step\ndoor NAME + seat + budget"| RUN["THE RUNNER\n.agents/scripts/autopilot_run.py\nholds what a prompt cannot"]
    RUN -->|"claude -p, fresh session\nwearing one seat"| KID["A CHILD\nruns the EXISTING door\nby name, not by text"]
    KID -->|"reads at the moment of use"| SRC[".agents/commands/ the doors\n.agents/rules/ the law\nthe six seat masters"]
    KID -->|"a small JSON result"| RUN
    RUN -->|"jira_feed.py step\none comment per child"| TICKET["THE TICKET\nthe handoff between children\nand the record you read"]
    TICKET --> LEAD
    RUN -.->|"needs_human"| PHONE(["your phone\nNeeds Mr. Hatter"])
    PHONE -.->|"your answer"| LEAD
```

**Why the ticket and not memory.** Nothing passes between children in process memory — each is a fresh
session. The next child learns what happened by reading the ticket, exactly as you do. That is not a
limitation worked around; it is what makes the run auditable after the fact, and it is why a comment
that fails to post is treated as a step that did not happen.

---

## 3. One story, end to end

Six children for a clean run. Every one is a fresh session with a new id, and the ids are on the
ticket, so "did the reviewer really start clean?" is a thing you can check rather than trust.

```mermaid
flowchart TD
    L["Step 0 - bind the project\nCLI version, story ready-for-dev,\nepic branch not behind main"] --> W["open the story's worktree\none story, one worktree, one lock"]
    W --> C1["child 1 - WHITE RABBIT\nruns the plan half of the story door\nreturns the plan path"]
    C1 --> C2["child 2 - QUEEN OF HEARTS\nruns the pre-dev audit on that plan\nfresh session, no inherited assumptions"]
    C2 --> V{"audit verdict"}
    V -- "NO-GO" --> ESC["ESCALATE\nthe plan gate re-arms - his call"]
    V -- "GO" --> C3["child 3 - CHESHIRE CAT\nbuilds against the audited plan"]
    C3 --> Q{"did the child ask\na question?"}
    Q -- "yes, answerable from the repo" --> GNAT["child - THE GNAT\nread-only lookup, cites the line"]
    GNAT -->|"the only resume in a run"| C3
    Q -- "yes, but it would need a GUESS" --> ESC
    Q -- "no" --> C4["child 4 - THE REVIEWER\nNO seat, reviewing model,\na session id never used before"]
    C4 --> R{"review verdict"}
    R -- "PASS" --> PARK["park: story to review,\nticket to In Review, one line to your phone"]
    R -- "CONCERNS or FAIL" --> C5["child 5 - CHESHIRE CAT\nONE fix cycle, in the lane"]
    C5 --> C6["child 6 - THE REVIEWER\nfresh session, new sha"]
    C6 --> R2{"second verdict"}
    R2 -- "PASS" --> PARK
    R2 -- "anything else" --> ESC
    PARK --> DONE(["you: read it, then\n/cicd-close-story-merge-tree"])
```

⛔ **There is no arrow to `main`.** Landing is not a rule the lead is asked to keep — the runner has
no verb for it at all, so it is not a thing an agent can talk itself into.

---

## 4. The charter — what the lead may pass without you

Approved 2026-09-07. Your launch word is a **batch approval** scoped to these rows and to **one
story**; it does not travel to the next one. The runner writes the scope into the ticket's first
comment, so what was in force is on the record rather than in someone's context.

| Gate | Who decides | Why it sits there |
|---|---|---|
| ② Step 2 `continue` | **the lead** | The audit already ran as a Queen child in a fresh session — which is the thing that stop existed to guarantee |
| ② Step 2.5 questions before code | **the lead** | Answered from the story, the plan and a Gnat lookup. **If it would need a guess, it escalates instead** |
| Audit verdict `NO-GO` | **you** | The plan-first gate re-arms; re-scoping is a judgment about what to build |
| New dependency, schema, security rule, CI or environment config | **you** | The constitution's Ask First list wins. The old engine's "self-install and log it" is dropped |
| Deleting a file | **you** | Ask First, always |
| ③ verdict `PASS` | **the lead** | It posts review-ready and parks. You still own review-to-done |
| ③ verdict `CONCERNS` or `FAIL` | **the lead**, once | One fix child, then one fresh reviewer. A second non-PASS escalates. `CONCERNS` never ships by itself |
| Landing on the epic branch or `main` | **nobody** | No runner verb exists |
| Anything a door marks `PIPELINE_BLOCKER` | **you** | The door already decided it is yours |

---

## 5. When it needs you

An escalation is **two things, both of them, every time**: a question in the chat with real options
and a recommendation, and a ticket comment whose first line is the literal marker. Your phone reads
the ticket; the chat may not be in front of you.

```mermaid
flowchart LR
    KID["a child returns\nneeds_human + its question"] --> RUN["the runner exits 3\nand posts the comment"]
    RUN --> T["the ticket\nfirst line: Needs Mr. Hatter\nthen the child's question"]
    RUN --> CHAT["the lead asks you in chat\noptions + its recommendation"]
    T --> YOU(["you, wherever you are"])
    CHAT --> YOU
    YOU -->|"your word"| RESUME["the lead resumes THAT child\n--fork-of its session id"]
    RESUME --> ON["the run continues,\nand the ticket shows who decided"]
```

⛔ **The lead waits.** An escalation it answered itself is the single failure the charter exists to
prevent, and it would be invisible — the run would look normal and be wrong.

---

## 6. The seats, and what each one costs

Each seat is one file, `.agents/commands/smh-team-<seat>.md`, and it is the **same file** that defines
that seat in Zoo. Three frontmatter keys pin the Claude side.

| Seat | Role | Model | Effort | Why |
|---|---|---|---|---|
| The Gnat | read-only research | haiku | low | Looks things up and cites lines. Cheap on purpose — it is called often |
| White Rabbit | PM / planning | sonnet | medium | Writes the plan; does not build |
| Caterpillar | design / front end | sonnet | medium | |
| Cheshire Cat | the builder | sonnet | high | Does the work that has to be right |
| Queen of Hearts | tests & QA | sonnet | high | Writes the failing tests and audits the plan |
| March Hare | the lead | opus | high | Decides; almost never a child |

⛔ **No seat can spawn its own subagents.** `Task` is on nobody's tool list — a headless child that
can launch more children is an unbounded bill with no ledger row.

⛔ **Never leave a child unpinned.** An unpinned child inherits the 1M-context Opus and costs six to
twenty times more; measured, a one-word answer cost **$0.157–$0.496** unpinned against **$0.024** on
haiku.

**Why forking is worth caring about.** A child launched fresh rebuilds ~12,600 tokens of prompt; a
child *forked* from a warm parent builds ~340 and reads the rest from cache. Measured over five
steps: **$0.158 naive against $0.059 layered — 63% cheaper**, and 82% once the parent amortises.

---

## 7. The five failure modes, all of them silent

Every one of these was measured against the real CLI, and **not one produces an error**. That is why
they are written down: none is guessable from reading the code.

| What breaks | What you would see | What holds it |
|---|---|---|
| A resumed child **loses its seat** — identity, model and tool limits — and keeps going | Nothing. Later steps look normal and run wrong | The runner re-sends the seat on every launch, forks included |
| `--max-budget-usd` is a **suggestion**: it stops the *next* turn, not the current one. Capped at $0.05, measured spends of **$0.496** and **$0.296** | A bill 10x the cap, reported as "budget exhausted" | `--run-cap-usd`, summed off the run's own ledger before each launch |
| A reply that **parses but carries no status** | A no-op recorded as success | Anything without a status is `failed`, never `done` |
| The child's transcript store is **unwritable**, so nothing can be forked | "No conversation found" — which reads as *forking does not work* | The runner points `CLAUDE_CONFIG_DIR` somewhere writable and seeds it |
| The workspace is **untrusted**, so every fork reads **zero** cached tokens | Nothing at all. Runs succeed; only the bill changes | The runner sets the trust flag in its own config directory |

---

## 8. Keeping this current

| If you change… | Do this |
|---|---|
| a door, a rule, or a skill | **Nothing.** The children read the file at the moment of use |
| a seat's character, model, tools or effort | Edit `.agents/commands/smh-team-<seat>.md`. ⛔ At most three `claude-*` keys, below `mode-groups`, one line each — the sync reads only the first 12 lines and a seat that falls outside that window is dropped from Zoo silently |
| how a child is launched, or the result contract | `.agents/scripts/autopilot_run.py`, and its tests in `.agents/scripts/tests/test_autopilot_run.py` |
| how a step reaches the ticket | `jira_feed.py step`, and `test_jira_feed.py` |
| the charter | Here, and in the door's own Step 1 table. Both, in the same commit — they are read by different people |

**The five things this lane owns**, and the reason the list is short: how to launch a child, the
result contract, the `step` verb, the seat renderer, and the budget table. Everything else is
borrowed at the moment of use. When the workflow changes, nothing here changes; when Claude's CLI
changes, only the runner does.
