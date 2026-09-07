---
IsArtifact: true
ArtifactMetadata:
  title: SCC-208 Autopilot v3 - the Wonderland lead (brainstorm round 3, design for ruling)
  type: design
  date: 2026-09-07
---

# SCC-429 - Autopilot v3: the Wonderland lead (DESIGN, for the operator's ruling)

> **Provenance.** Brainstormed in four rounds on 2026-09-07 under SCC-208, an Idea ticket the operator
> deleted the same night as brainstorm-only; its description and five comments are snapshotted in
> [`tickets/brainstorm-history-scc-208.md`](tickets/brainstorm-history-scc-208.md). The build is
> **SCC-429** (Task, under the CI/CD grouping epic SCC-33) with two subtasks minted in his order:
> **SCC-430** Claude (sections 2, 3, 5, 9, 11) and **SCC-431** Zoo (sections 10 and 2.6). This file
> is attached to SCC-429 and rides to `main` on the SCC-430 lane; the fast-read outlines are `tickets/SCC-429.md` here and `tickets/SCC-4xx.md` inside each lane folder (`2026-09-07_scc-430-autopilot-claude/`, `2026-09-07_scc-431-zoo-remote/`).
> Every "SCC-208" below is the brainstorm ticket, kept as written.

- **Ticket:** [SCC-208](https://sudo-command.atlassian.net/browse/SCC-208) - retire the AP lane, design its replacement
- **Status:** DESIGN ONLY. Nothing built, nothing minted. Acceptance item 1 of the ticket says the
  design is recorded and ruled on before any code; this file is that record. The build plan comes
  per subtask through `/smh-plan-task` once the rulings in section 7 are in.
- **Rounds so far:** round 1 is the ticket description (2026-08-17: headless, terminal, fresh session
  per step, Jira comments as the handoff, run the existing doors). Round 2 is the operator's comment
  of 2026-09-06 (a Wonderland team like the Zoo profiles, a team lead that handles the sub-agents'
  questions and approvals and reports only to him, terminal approvals named as the threat, each
  agent carrying its own skills and commands). This is round 3: the shape that satisfies both.
- **Reference material read for this round:** [cicd-autopilot-claude.md](../../../.agents/commands/cicd-autopilot-claude.md),
  the three frozen `-AP` twins, [zoo-team.md](../../../.agents/rules/zoo-team.md) and the six
  `smh-team-*.md` seat masters, [approval-cost-is-a-threat.md](../../../.agents/rules/approval-cost-is-a-threat.md),
  [command-shape.md](../../../.agents/rules/command-shape.md), [terminal-permissions-guide.md](../../../docs/migrations/terminal-permissions-guide.md),
  [jira_feed.py](../../../.agents/scripts/jira_feed.py), the AGY engine
  `Projects/AGY_AVIATIONCHAT/scripts/autopilot-dev-story.ps1`, the live Claude settings on this
  machine, and the vendor's current headless / sub-agent / agent-teams / remote-control pages
  (checked today, not recalled).

---

## 0. The answer in one paragraph

One **lead** session, interactive, with Remote Control on, plays the March Hare. It never does the
work itself. For each step of the workflow it calls a small deterministic **runner** script, and the
runner launches a **fresh headless `claude -p` child** for that one step. Each child is started *as
one Wonderland seat* - a Claude agent definition the runner builds at launch from the same
`smh-team-*.md` master that already makes the Zoo mode (section 11: no second file, so no drift) -
with that seat's skills preloaded and its rules named, and the child
runs the **existing door** (`/cicd-dev-story-tests`, `/cicd-self-audit`, `/cicd-code-review`),
never a copy of it. Every child returns a structured result (done, blocked, needs a human, failed)
and the runner writes that result onto the story's Jira ticket as a comment before the lead sees
it. The lead answers what its written charter lets it answer, and escalates the rest to the
operator as one tap on his phone (Remote Control) with a durable copy on the ticket. Terminal
permissions stop being a threat because in a headless child a prompt cannot wait - it becomes an
instant denial the child reports upward, and the next morning's `/smh-llm-approvals` harvests it
into an allow row. The lead holds only summaries, so it is cheap to keep open and cheap to restart
cold; the token-heavy work happens in children that never wait on anyone. **And the children do
not each re-research the codebase** (section 9, added in round 3b): one cheap child writes a
grounding pack per story, the build child is a *fork* of the plan child so the researched context
arrives as a cache read, siblings share a byte-identical prefix, and only the two children the law
says must be independent - the audit and the review - start fresh, reading distilled documents
rather than the tree.

Glossary for this file: a **door** is one of the slash commands the operator types today; a
**seat** is one Wonderland team member (March Hare, White Rabbit, Cheshire Cat, Caterpillar, Queen
of Hearts, the Gnat); a **child** is one headless `claude -p` process running one step; the
**runner** is the Python script that launches children and holds the rules an LLM must not be
trusted with; **the charter** is the written list of gates the lead may pass without the operator.

---

## 1. What is true today (measured this session, so nobody re-derives it)

| Fact | Consequence for the design |
|---|---|
| Installed CLI is **2.1.258**. Its `--permission-mode` choices are `acceptEdits`, `auto`, `bypassPermissions`, `manual`, `dontAsk`, `plan`. The vendor's `--permission-prompts none` flag (make every would-prompt an explicit deny) lands in **2.1.259** - one version ahead. | The "prompt equals deny" rule the design relies on is the documented headless behaviour today and becomes an explicit flag after one upgrade. The upgrade is an Ask-First item (dependency) - listed as a prerequisite in section 5. |
| `bypassPermissions` **still honours deny rules** (vendor docs). This repo has **zero** Claude deny rows in both `~/.claude/settings.json` (223 allow, 0 deny) and `.claude/settings.json` (217 allow, 0 deny, 4 ask on GitHub MCP writes). | The permission *mode* of a child is not where safety lives here. The fence is six `PreToolUse` hooks (heredoc block, branch-delete guard, cwd-escape guard, push-to-main ask, plus two auto-allows), the git hooks (`pre-push` bounces `main`, `commit-msg` gates) and the GitHub ruleset on `main`. All of those bind a headless child exactly as they bind a chat. |
| **Agent teams** (one session spawning named teammates with a mailbox) are experimental and **do not spawn under `-p`**. | The round-2 picture "the lead in chat with the sub-agents" is built from `claude -p` children plus a Jira thread, not from the teams feature. |
| **Custom sub-agents** (`.claude/agents/<name>.md`) support `skills:` (preload at start), `model`, `permissionMode`, `tools` / `disallowedTools`, `maxTurns`, `isolation: worktree`, `hooks`, `memory`. The CLI's `--agent <name>` applies a custom agent to a whole session. `.claude/agents/` **does not exist yet** in this repo (the sandboxed `ls` shows mount-point ghosts; sandbox-off it is absent). | This is the mechanism for "each sub-agent has its skills and rules highlighted": the seat's frontmatter preloads its skills; the seat's body names its rules the way the doors do. One master per seat: the sync renders it to Zoo, the runner renders it to Claude at launch as `--agents` JSON that never touches disk (section 11). |
| Remote Control is **on at startup** on this machine, with agent push and input-needed notifications enabled. `AskUserQuestion` renders as a tap chip on the phone and [mobile-mode.md](../../../.agents/rules/mobile-mode.md) already rules that a tap on Approve IS the gate. | The operator's "approve on the fly" channel exists for anything the lead *chooses* to ask. Whether a raw permission prompt of the lead itself also shows on the phone is unverified (section 8, one-minute test). |
| Measured cause of the approval cost (SCC-415): allow-list gaps 5h50m, two command *shapes* 13h, deny refusals 0. `shape-block.py` now refuses the shapes before the gate and hands the agent the reshape. | In a child those same events cost seconds, not hours: an allow gap is an instant deny the child reports; a bad shape is refused with the remedy and the child rewrites it. The list still grows the same way - every reported denial is an `/smh-llm-approvals` row next morning. |
| The three `-AP` twins are frozen (SCC-209) and reference retired names. The three project engines are 2052 / 1500 / 1275 lines of PowerShell, diverged. `jira_feed.py` posts comments only through `devrecord`, `finish` and `flag` (each reads the ticket back); there is no generic step-comment verb. | Section 4 rules on the twins and engines. Section 2.2 adds one verb to `jira_feed.py` rather than a second channel. |
| The reviewing law (SCC-362): no seat that built, tested or orchestrated writes a verdict; the review runs on the operator's reviewing model in its own session. | The robot's review step is a plain fresh child on Fable at max effort with **no seat identity**, and the runner refuses to launch it on any session id it has seen. |

---

## 2. The shape

### 2.1 Three layers, and why each is the kind of thing it is

| Layer | What it is | Why this and not the alternative |
|---|---|---|
| **Lead** | An interactive Claude session running the new `/cicd-autopilot <project> <story>` door - the March Hare charter written for Claude. Remote Control on. Holds only step summaries. | Round 2 needs someone to answer the children's questions without waking the operator. That is judgment, so it is an LLM. Interactive because that is the only surface Remote Control mirrors to the phone. Small context because an idle lead loses its cache after five minutes, and a cold restart of a summary-only context is cheap. |
| **Runner** | `autopilot_run.py` (lobby, stdlib) - launches one child per call, enforces the rules in 2.2, posts the step to Jira, returns the child's structured result to the lead. | The round-1 ruling was "no LLM coordinator, that would just be tax" and it was right about *law*: fresh session per step, review independence, fail loud, budgets, no landing. Those are rules an LLM can rationalise past, so they live in code. The LLM lead decides only inside the charter. |
| **Seats** | Headless children, `claude -p --agent <seat> --model … --effort … --max-budget-usd … --json-schema …`, cwd = the story worktree, each running an existing door. | A child is a genuinely fresh context (the operator's stated advantage over his own manual habit), can be pinned to a model and a budget, returns machine-readable output, and inherits every hook and every settings file the chat does. Sub-agents inside the lead would share the lead's process and could not spawn their own sub-agents, which the review door needs for its five-lens fan-out. |

### 2.2 The Wonderland seats as Claude agents

One master per seat already exists at `.agents/commands/smh-team-<seat>.md` and renders to a Zoo
mode. *Amended in round 3d (section 11):* there is **no second file**. The runner reads that master
at every launch and hands the child a session-only definition through `--agents <json>` - never
written to disk, and it outranks any `.claude/agents/` file (sub-agents page, read this session).
The prompt is the same one-line pointer `.roomodes` carries ("read the master and follow it end to
end"); Claude's keys (`claude-skills:`, `claude-model:`, `claude-tools:`) sit in the master's
frontmatter beside the existing `mode-*` keys.

| Seat | Runs which door in the robot | `skills:` preloaded | `model` / `effort` | Never |
|---|---|---|---|---|
| White Rabbit - PM | story shaping and scoping questions for the lead; owns the **grounding pack** step with the Gnat (section 9.3, Layer 1). *Corrected in round 3b:* it does **not** run ② - a fork chain must keep one system prompt, so the seat that plans ② is the seat that builds it | `cicd-self-audit`, the artifact and plan-first rules named in the body | Opus 4.8 / medium | writes code; passes a gate |
| Queen of Hearts - QA | `/cicd-self-audit` on the plan (the old Stage 2); review-readiness after the build (suites bare, `gate_receipt.py`, drift declared) | `cicd-self-audit`, `bmad-testarch-*`, `tests-must-gate-for-real` | Opus 4.8 / max | weakens an assertion; writes a verdict |
| Cheshire Cat - ENGINEER | ② `/cicd-dev-story-tests` **end to end** - the plan up to the Step 2 stop, then (as a fork of that same session) Steps 2.5-5 from the audited plan, then the one fix cycle ③ may send back | `cicd-dev-story-tests`, `code-standards`, the project's stack skills (`python-patterns`, `react-best-practices`, firebase-*) | Opus 4.8 / medium, **or the DeepSeek lane** via the runner's `--dev-model` and base-URL flags (the cost lever of `/cicd-autopilot-deepseek4` survives as a flag; the lane forfeits the fork, section 9.3) | touches git beyond its own `claude/*` commits; installs a dependency |
| Caterpillar - DESIGNER | only when the story's diff touches user-facing UI; called by the lead, not by default | `emil-design-eng`, `visual-fx-3d`, `smh-designer` | Opus 4.8 / medium | back-end work |
| The Gnat - LIBRARIAN | read-only lookups the lead needs to answer a child's question | `lobby-search`, the project's `.agents/INDEX.md` | Sonnet 5 / low, `tools:` read-only | edits; runs a command |
| *(no seat)* - the reviewer | ③ `/cicd-code-review` - the real door, five lenses fanned out inside the child | none preloaded (the door loads its engine) | **Fable 5.1 / max**, fresh session, no `--agent` | ever resume a session the runner has seen |

The **"rules highlighted"** half is the seat body's *Rules in force* block, the same block every
door carries. Path-scoped rules still auto-load when the child opens a matching file, and
`rule-trigger.py` still fires on the child's prompt, because hooks run under `-p` unless `--bare`
is passed - and the runner never passes it.

### 2.3 What the runner enforces that no prompt can

1. **A door is a file, and a missing file fails loud.** The runner resolves the door to its path
   under `.agents/commands/` (or the project's skills) and exits non-zero *before* any `claude`
   call if it is absent. This is the one line of SCC-70 worth keeping: the old engine built a
   prompt saying "your instructions live in the command above" and ran with nothing. Proven by a
   negative-control test that fails against that naive behaviour. *And the runner passes the
   door's name, never its text* (section 11): the child loads the master through the same
   generated launcher skill the chat uses, at the moment of use, so an edited door is live on the
   next launch with no sync.
2. **Fresh session per step, recorded.** A new UUID per child. The child's JSON result carries
   `session_id`; the runner writes it into the step's Jira comment. Acceptance item 3 is then a
   count on the ticket, not a claim. The only `--resume` the runner ever issues is to deliver the
   lead's *answer* to a child that returned a question - never to start a new step on an old
   context.
3. **A structured result or a failure.** `--output-format json --json-schema` with the contract
   `{status: done | blocked | needs_human | failed, summary, artifacts[], question?, evidence{sha,
   suite_totals}, denials[]}`. Anything that does not parse is `failed`. The lead never reads a
   transcript.
4. **Budgets.** `--max-budget-usd` and `--max-turns` per child; a run-level cap in the runner. A
   budget cut is a deliberate halt, never retried.
5. **Review independence.** The ③ child runs on the reviewing model, in a session id the runner
   has never issued, with no seat identity, against the sha the lead names. The runner refuses
   any other combination. This is [zoo-team.md](../../../.agents/rules/zoo-team.md)'s review gate,
   carried into the robot instead of waived by it.
6. **No landing step exists.** The runner has no verb that touches an epic branch or `main`.
   Landing stays `/cicd-close-story-merge-tree` on the operator's word, unchanged.
7. **Every step is a Jira comment.** One new verb, `jira_feed.py step --key <KEY> --stage <n>
   --body-file <f>`, posting and reading back like `devrecord` does. A second marker comment,
   `Needs Mr. Hatter`, is the escalation record (same shape as the existing `User tasks` marker,
   updated in place rather than stacked).
8. **One story, one worktree, one lock** - carried over from the old engine as-is, including the
   asset bootstrap (`link-worktree-assets.py` from the lobby; thin projects have no linker of
   their own, per the standing memory note).

### 2.4 Terminal permissions - the threat, and how it is handled

The threat the operator named is real, but it is a different threat in a headless child than in a
chat. In a chat a prompt **waits**: the cache dies at five minutes, the whole context is re-billed,
and the wait is measured in hours when he is away. In a headless child there is nobody to wait
for. The CLI denies the call at once and the model sees the denial. So the failure changes from
"a stall that costs money" to "a step that could not do its work", and the design makes that a
signal instead of a mystery.

| What happens in the child | Child's behaviour | Lead's behaviour |
|---|---|---|
| Command runs inside the sandbox (children inherit `~/.claude/settings.json`: sandbox on, `autoAllowBashIfSandboxed`, worktrees under `.claude/worktrees` inside `allowWrite`) | runs | nothing |
| Command matches an allow row (223 user, 217 project) | runs | nothing |
| Command would prompt (an allow gap) | denied instantly; the child appends it to `denials[]`, reshapes if the hook told it how, else returns `blocked` with the exact command | retries once if the child proposed a reshape; otherwise escalates with the command text. Next morning `/smh-llm-approvals` reads the child's transcript like any other and the row is added - the list gets better every run, which is the operator's own point |
| Hook `deny` (heredoc, branch delete outside `chore/claude/epic`, cwd escape) | refused with the remedy text; the child rewrites the command | nothing |
| Hook `ask` (`require-push-approval.py`: push to `main`, commit on `main`) | becomes a deny in headless - **correct**, that is the fence working | never escalates this; it is reported as a child misbehaviour |
| A destructive git spelling no row names | `.githooks/pre-push` bounces `main`, `commit-msg` gates refuse, the GitHub ruleset refuses without the main-write-gate check | reported |

**Mode for children: `--permission-mode auto`, not `bypassPermissions`.** Bypass buys nothing
here (there are no deny rows to bypass, so the only things it would waive are the hook asks and
the classifier), and what it does to a hook's `ask` is unverified. Auto is the house default, the
classifier auto-approves the routine cases it already approves in chat, and everything it cannot
judge denies. After the upgrade to 2.1.259 the runner adds `--permission-prompts none` so the
rule is explicit rather than implied.

**The one sandbox fact that would silently kill the first run.** The lead calls the runner through
its own Bash tool, inside its own sandbox, whose network allowlist does not include the Anthropic
API. A child spawned under that sandbox cannot reach the model. The remedy is the same one
`jira_feed.py` and `task_preflight.py` already have: the runner goes on
`sandbox.excludedCommands` with a matching allow row (a two-file edit under `/smh-llm-approvals`
Step 4). The child then runs its *own* sandbox for its *own* Bash calls, so nothing is lost. Any
other order of discovery costs a session; it is written here so it costs nothing.

**"Approve on the fly."** The lead is interactive with Remote Control already on at startup. An
escalation is an `AskUserQuestion` chip (a tap is the approval, per the mobile lane) plus a
`PushNotification`, and the durable copy is the `Needs Mr. Hatter` Jira comment. While it waits the
lead polls the ticket every sixty seconds for a reply from the operator's account, so he can also
answer from the Jira app when the phone session is not open. **Telegram is deferred, not
refused:** it would be a second channel to keep in sync with the ticket, and round 1 already ruled
the ticket the LLM-neutral channel (Zoo and opencode agents can read the same comments). Re-open
it only if answering through Jira proves too slow in practice.

### 2.5 The charter - what the lead may pass without him (this is the product decision)

Legal basis: [000-PLAN-FIRST-GATE.md](../../../.agents/rules/000-PLAN-FIRST-GATE.md)'s batch
clause - *one recorded approval covers the plans it lists* - which `/smh-plan-task` already uses.
The launch word for `/cicd-autopilot` is that recorded approval, scoped to the rows marked
**lead** below, for this story only. The runner writes the launch and its scope into the first
Jira comment.

| Gate inside the door | Today | Proposed |
|---|---|---|
| ② Step 2 `continue` (run the audit here) | operator | **lead** - the audit is a Queen child, fresh session |
| ② Step 2.5 questions before code | operator | **lead** answers from the story, the plan and a Gnat lookup; if it would have to *guess*, it escalates |
| Audit verdict NO-GO | operator re-scopes | **escalate** - the plan-first gate re-arms and that is his call |
| New dependency, schema, security rules, CI or environment config | Ask First | **escalate** - the old engine's "self-install and log it" policy is dropped; the constitution wins |
| Deleting a file | Ask First | **escalate** |
| ③ verdict PASS | operator | **lead** posts review-ready and parks; the operator still owns review to done |
| ③ verdict CONCERNS or FAIL | operator | **lead** sends the findings back to one Cheshire child (fix in lane), then one fresh ③ child; a second non-PASS **escalates**. CONCERNS never ships by itself (standing ruling) |
| Landing on the epic branch or `main` | operator | **never** - no runner verb exists |
| Anything the door itself marks `PIPELINE_BLOCKER` | operator | **escalate** |

### 2.6 Phase 2 - the Zoo variant (operator direction, 2026-09-07: Claude first, then a Zoo-specific version)

Most of this design is platform-neutral by construction - that is why the seats are masters and the
handoff is the ticket. What changes for Zoo, and what does not:

| Component | Claude v3 | Zoo variant |
|---|---|---|
| Lead | the `/cicd-autopilot` door in an interactive session | the March Hare mode itself (`orchestrator`) - it already exists and already delegates |
| Children | `claude -p --agent <seat>` launched by the runner | `new_task` with `mode` set to the seat's slug. A Zoo subtask is a fresh context, which is the equivalent of a fresh session; it runs unattended only with the *Subtasks* and *Mode switching* auto-approve tiles on (per [zoo-team.md](../../../.agents/rules/zoo-team.md)) |
| Seat definitions | `.claude/agents/<seat>.md`, rendered from the masters | `.roomodes`, rendered from the same masters - already in place |
| Handoff record | `jira_feed.py step` | the same script and verb, run from Zoo's terminal (the `python3 .agents/scripts/jira_feed.py` family is on the tracked Zoo allow list - re-verify in phase 2) |
| Push to the phone | Remote Control plus `PushNotification` plus the tap chip | [`zoo_notify.py`](../../../.agents/scripts/zoo_notify.py), already installed per machine as a service: it polls the thread store (Zoo has no hook surface) and pushes through ntfy on every approval-ask Zoo could not auto-decide and on every turn end. **Nothing new to build for the push half.** |
| His reply | a tap on the chip, or a Jira reply the lead polls | Zoo has no Remote Control: he replies in the Zoo panel, or on the ticket, which the March Hare polls with the same sixty-second loop. **This is the one place Zoo is weaker:** a Zoo *permission* ask can only be answered at the desk; only the ticket-shaped escalations can be answered from the phone |
| Terminal permissions | a prompt is an instant deny in the child; hooks refuse the bad shapes | Zoo has no hooks: the fence is its deny list (`git -C` auto-denied, the destructive battery) plus the git hooks and the GitHub ruleset. A prompt inside a subtask **waits** - that wait is exactly the ask `zoo_notify` pages him for - so the Zoo variant leans harder on the allow list being complete, and `/smh-llm-approvals` already harvests Zoo threads too |
| The law the runner holds | code | prose in the March Hare master plus structure: no seat can run ③, so the Zoo autopilot parks at review-ready, exactly where the March Hare parks today, and the operator switches the model and runs ③ himself |

Net: the Zoo variant is the March Hare charter gaining the escalation contract (post `Needs Mr.
Hatter`, poll the ticket) and the `step` verb. What it cannot have is the deterministic runner;
what it does not need is a new push channel, because `zoo_notify.py` already reaches the phone.

#### 2.6.1 The Zoo remote - its own subtask (operator, 2026-09-07: *"I need a remote set up for Zoo, it's one sub ticket for sure. I want to be able to communicate from my phone."*)

> **Superseded in round 3c (section 10):** the assumption below that Zoo has "no API to inject a
> message" was wrong - Zoo kept Roo's IPC socket and extension API. Section 10 carries the measured
> surface, the option catalogue and the recommendation; this subsection's framing of the subtask
> stands, its option list does not.

**Where each platform stands on two-way phone communication today:**

| Direction | Claude lead | Zoo lead (March Hare) |
|---|---|---|
| Desktop to phone | Remote Control mirrors the whole chat; push notifications on at startup | `zoo_notify.py` pushes to the phone through ntfy (title plus body, public topic named per machine, `NTFY_TOPIC` overrides) on every ask Zoo could not auto-decide and every turn end. **Exists.** |
| Phone to desktop | Remote Control: he types or taps in the mirrored chat. **Exists.** | **Nothing.** Zoo has no remote surface and no API to inject a message into a thread. The only reply paths are the Zoo panel at the desk, or a comment on the ticket - which nothing reads back yet. |

So the Claude side already meets the requirement, and the gap is entirely on the Zoo side's inbound
half. The subtask builds that half and nothing else:

| Piece | What it is | Why this shape |
|---|---|---|
| **Escalation-aware push** | `zoo_notify.py` learns the `Needs Mr. Hatter` shape: title `<KEY> needs you`, body the question, and an ntfy `Click` header opening the ticket in the Jira app (ntfy's `Click` / `Actions` publish headers - verify against the ntfy docs in the subtask, not from memory) | one tap from the banner to the place he answers |
| **Inbox** | `zoo_inbox.py`, a sibling service installed by the same `zoo_notify_install.py --apply`: subscribes to a *reply* topic on ntfy, and posts each message he sends from the ntfy app as a comment on the escalated ticket with an `Operator reply` marker, read back like every other write | the March Hare's sixty-second ticket poll then sees his answer with no Zoo API and no new app: ntfy is already on both machines and on his phone |
| **The Jira app as the zero-build path** | a reply typed directly on the ticket from the Jira app is the same `Operator reply` to the poll loop | works the day the poll loop exists, before the inbox is built |
| **Raw permission asks** | the one thing no inbox can answer, because only the Zoo panel can click Approve. Fallback: a VS Code Remote Tunnel, so `vscode.dev` on the phone shows the real Zoo panel | first-party, no Zoo API needed, clumsy on a phone - which is why the design keeps raw asks rare (allow list plus door-shaped commands) and routes every *decision* through the ticket instead |
| **Secret** | a reply topic that can approve work cannot be a public name: the topic is a secret (or an ntfy access token) kept under `keyway-secrets`, never in git | an ntfy topic is public by name; the outbound topic can stay so, the inbound one cannot |

**Telegram** is the alternative to the ntfy reply topic, not to the design: a bot gives a real chat
thread and costs a bot token to manage. The inbox script is the only file that names the channel,
so swapping ntfy for Telegram later is a one-file change. Recommendation: ntfy first, because it is
already installed and already his; Telegram if he wants the chat feel.

**Proof for the subtask:** one real escalation raised by the March Hare, answered from the phone
through the ntfy app, landing on the ticket, and the March Hare resuming on it - the ticket thread
is the evidence. It depends on nothing in the runner, so it can start alongside S1.

---

## 3. One worked example - Story 14.2, end to end

The operator types `/cicd-autopilot AGY_AVIATIONCHAT 14.2` in a chat, or from his phone through
Remote Control. The lead binds the project, confirms the epic branch is checked out and not behind
`main`, reads that 14.2 is `ready-for-dev` with its failing tests on disk, and asks the runner to
open the story worktree. The runner posts Jira comment 1: launched, the charter rows in force,
budget cap, and a line saying session ids will follow.

The runner launches child 1 as the White Rabbit on Opus, cwd the worktree, running
`/cicd-dev-story-tests 14.2` up to its Step 2 stop. It returns `done` with the plan path and its
session id. Comment 2. The lead reads one paragraph, not a transcript, and dispatches child 2, the
Queen on Opus at max, running `/cicd-self-audit` on that plan. It returns `done`, verdict GO, three
findings appended into the plan. Comment 3.

GO is a charter row, so the lead passes ② Step 2 itself and dispatches child 3, the Cheshire Cat on
Opus, running ② from Step 2.5 to Step 5 against the audited plan. Twenty minutes in the child hits
a real ambiguity - an acceptance criterion says one thing and an existing fixture assumes another
- and returns `question` with the two file lines. The lead asks a Gnat child (Sonnet, read-only)
which one the epic's architecture note actually says; the Gnat cites the line; the lead resumes
child 3 with that answer, the only `--resume` in the run. Child 3 finishes: `done`, walkthrough
path, suite totals, sha. Comment 4.

The runner launches child 4 with **no seat**, Fable at max, a session id nobody has used, running
the real `/cicd-code-review 14.2` at that sha; inside it the five lenses fan out as they do for a
human. It returns CONCERNS with one finding. Charter row: one fix cycle. Child 5 (Cheshire) fixes
it in the lane; child 6 (fresh review, Fable) returns PASS at the new sha. Comment 6.

The lead flips the story to `review`, the runner moves the ticket to In Review with its Dev Record
as the old engine did, and the operator's phone gets one line: *14.2 review-ready, PASS at
`<sha>`, six fresh sessions, $X.* He runs `/cicd-close-story-merge-tree 14.2` when he chooses.

What an escalation looks like instead: at child 3 the Cat reports that the story needs a package
that is not installed. That is an Ask-First row, so the lead posts `Needs Mr. Hatter` with the
package name and why, pushes to the phone, and the tap chip reads *Install and pin it / Stop here.*
He taps from the porch. The lead resumes child 3 with his word, and the ticket shows who decided.

---

## 4. What happens to the old lane (scope item 4)

| Thing | Ruling proposed |
|---|---|
| `cicd-dev-story-tests-AP.md`, `cicd-self-audit-AP.md`, `cicd-code-review-AP.md` (frozen, SCC-209) | **Delete.** They are the forked bodies the ticket forbids, they reference retired names, and nothing resolves them. `git show` keeps them if a paragraph is ever wanted. |
| `cicd-autopilot-claude.md` | **Rewrite in place** as the v3 door. The SOP, the atlas and the INDEX already point at this name. |
| `cicd-autopilot-opencode.md` | **Delete.** The runner drives the `claude` CLI; there is no opencode lead and pretending to a port is how the old lane drifted. Said plainly rather than kept as a promise. |
| `cicd-autopilot-deepseek4.md` | **Fold into a runner flag** (`--dev-model` plus base-URL and key env, scoped to the Cheshire child exactly as the engine scoped it). The cost lever survives; the separate command does not. |
| The six `autopilot-dev-story*.ps1` engines in AGY, NEXgen-VR and BRKN | **Banner now** (*reference only - do not run*, pointing here). **Delete AGY's and NEXgen's** once acceptance items 3 to 5 pass on one real story. BRKN's stay - frozen fork, the operator's ruling. |
| `docs/_scc_sops_prds/autopilot_bmad_dev_loop.md` and SOP section 15 | Rewrite after the spike, from the runner as built - not before. |
| The teaching-edition rebuild (`sudo-command-center`, carried from SCC-70) | Mint as its own ticket once section 7 is ruled; it must not start before, per the sequencing note on SCC-208. |

---

## 5. Build order, for `/smh-plan-task` once ruled

| Step | What it proves | Evidence |
|---|---|---|
| **S0 - spike, half a day** | On 2.1.258: `claude -p --agent <seat>` honours a seat's `skills:`; the `--json-schema` result round-trips; a child reaches the model when the runner is excluded from the lead's sandbox; a `PushNotification` plus tap chip reaches the phone. **Plus the three cost measurements of section 9:** `--agent` versus `--append-system-prompt-file` on ten identical launches (which delivery reads the cache); a `--resume --fork-session` child's `cache_read_input_tokens` against its parent; the same small story run naive and layered, both totals on the ticket | session ids, one JSON result, one phone screenshot from the operator, and a four-column usage table per child |
| **S1 - runner and negative control** | a missing door exits non-zero with no `claude` call; a result without `status` is `failed`; the ③ launch refuses a seen session id | `test_autopilot_run.py` red against the naive engine behaviour, then green |
| **S2 - the seat renderer** (amended, section 11) | the runner's function that turns a seat master's frontmatter into `--agents` JSON at launch; the six masters gain `claude-*` keys; **no `.claude/agents/` file is written** | parity test, the twin of `test_zoo_team.py`: rendered JSON against master frontmatter, never against a table typed into the test |
| **S3 - the ticket verbs** | `jira_feed.py step` and the `Needs Mr. Hatter` marker, read back like `devrecord` | `test_jira_feed.py` cases |
| **S4 - the door** | `/cicd-autopilot` body: the charter of 2.5, the launch approval scope, the escalation shape | `test_command_surfaces.py` |
| **S5 - one real story** | acceptance items 3 and 4 on an AGY story, budget capped | the ticket's comment thread and session count |
| **S6 - retire** | section 4 executed | the deletions, the banners, SOP and atlas rows |
| **S7 - the Zoo remote** (its own subtask, operator's ruling; independent of the runner, can run beside S1) | section 10.4: the IPC event bridge, the Telegram bot, the companion extension, the tunnel fallback; the thread-store poller retired once proven | a `followup` answered by text from the phone inside the Zoo conversation, a tool ask approved by a tap, both mirrored on the ticket, the poller off for a day with nothing missed |
| **S8 - the Zoo variant** (phase 2, after S5 is proven) | section 2.6: the March Hare master gains the escalation contract and the `step` verb | one real story driven from the Zoo seat, the ticket thread as evidence |

Prerequisites needing the operator's word before S0: the CLI upgrade to 2.1.259 or later (Ask
First, dependency), and the two settings rows that take the runner out of the lead's sandbox
(under `/smh-llm-approvals` Step 4, not a lane).

---

## 6. The one tradeoff that matters, and the call

**Lead as judge, or lead as dispatcher.** A lead that may decide anything is the fastest robot and
the one that quietly re-scopes a NO-GO at 3 a.m. A lead that may decide nothing is the old
PowerShell engine with a chat bolted on, and it wakes him for every question the Gnat could have
answered. The call here is **dispatcher with a written charter**: the lead decides only the rows
marked *lead* in 2.5, the runner holds every rule that must not bend, and the ticket records who
decided each gate. That is SCC-362's lesson - judgment-shaped prose gets rationalised past, so the
judgment step runs where the law is code - applied one level up.

---

## 7. For the operator's ruling (product calls only)

**Ruled 2026-09-07, round 3d, his words:** *"Claude already has remote, we don't need anything more
than that. Zoo is the one I am interested in making work remote and we would have to build that. I
also have an iOS phone."* That closes 2, 4 and 6 below. Open: 1, 3, 5.

1. **The charter table in 2.5**, row by row. The row most worth a second look: his launch word
   covering ② Step 2's `continue`, which today is his model-switch moment.
2. ~~**Telegram deferred** in favour of the tap chip plus the ticket~~ **Ruled:** the Claude lead
   stays on Remote Control, nothing added.
3. **Section 4**: delete the AP twins and the opencode launcher now, banner the engines, delete
   two of the three after S5.
4. ~~**The Zoo remote's inbound channel** (section 10.4): a Telegram bot bridge as recommended, or
   ntfy actions~~ **Ruled by the phone:** iOS, so the Telegram bot (the ntfy iOS app cannot type a
   reply). The subtask itself is already ruled - his word - and `/smh-plan-task` mints it with the
   rest.
5. **The Zoo approve path** (10.4): the companion extension as recommended, with `code tunnel` as
   the fallback; or the tunnel alone.
6. ~~**The Claude lead's phone surface** (10.4): Remote Control as it is, or add the first-party
   Telegram channel~~ **Ruled:** Remote Control as it is. The phone carries two apps, the Claude app
   and Telegram.

Everything else in this file is engineering and is the recommendation as written.

---

## 8. UNVERIFIED (to be measured in S0, not assumed)

- Whether Remote Control mirrors a *raw permission prompt* of the lead to the phone. The design
  does not depend on it - designed escalations use the chip, which does render - but it decides how
  much of the lead's own routine he sees.
- What a hook's `ask` becomes under `bypassPermissions`. Irrelevant under the recommended `auto`,
  recorded so nobody chooses bypass on the assumption that it is harmless.
- `--agent <seat>` combined with `-p` on 2.1.258 honouring `skills:` preloads. In the help text,
  not yet exercised. *Round 3d adds the pair:* `--agent <seat>` resolving a seat defined on the same
  launch line by `--agents <json>` (the docs state each half; the combination is the S0
  measurement). Fallback: `--append-system-prompt-file` carrying the same pointer sentence - still
  no file the sync has to keep current.
- The nested child's network under the lead's sandbox. Assumed blocked from the allowlist
  (`api.anthropic.com` absent); S0 measures it before the excluded-command row is written.
- Whether a `--resume … --fork-session` child actually reads the parent's cache in practice
  (the API rule says an identical prefix on the same model hits; Claude Code's own replay is what
  S0 measures, through the `usage` block the child's JSON result carries).
- Zoo's panel through a `code tunnel` on a phone screen: on record for Roo in Codespaces and
  code-server, never on a phone. One look from the operator settles it.
- Whether the WSL VS Code server inherits `ROO_CODE_IPC_SOCKET_PATH` from `~/.profile`; if not, the
  variable goes on the launch line instead. First step of the Zoo subtask.
- The IPC and API surface read from Zoo's `main` source matching the installed 3.83.100457 bundle
  in every command; the bundle carries the same names, the argument shapes are assumed.

---

## 9. Context and cost - research once, fork many (round 3b, the operator's question of 2026-09-07)

> *"How are we handling the cached information from each agent? How are they sharing artifacts?
> They still need to follow the process correctly, they are just switching personas. Each sub-agent
> must not do its own full research every time - that would destroy my token costs."*

He is right, and the design as written in sections 2 and 3 would have done exactly that: six fresh
children, each free to explore the tree from nothing. This section is the fix. The short form: a
child's bill has four parts, and each part has a different cheapest source.

### 9.1 Where a child's tokens go, and what it costs today

| Part of the bill | What it is | Measured today |
|---|---|---|
| **The fixed prefix** | system prompt, tool schemas, `AGENTS.md` / `CLAUDE.md`, the seat's preloaded skills, whatever hooks inject at session start | The lobby's `SessionStart` hook injects **56 KB, about 14,000 tokens**, into every session (the 41.7 KB hand-off plus the 8.4 KB repo map plus the gates). A project child gets the project's own hooks instead (AviationChat's `.claude/settings.json` injects nothing at start; it carries a `Stop` hook only). |
| **The research** | tool results from reading the codebase to understand the story | Unbounded by design today: the ② door's Step 0.6 and Step 1 re-derive the story's ground every run. AviationChat's `project-context.md` is 19 KB and its architecture shards total 128 KB - a child that "reads everything to be safe" spends 50,000 to 100,000 tokens before it writes a line, and the naive design does that six times. |
| **The work** | the child's own output and tool calls | the part actually worth paying for |
| **The hand-off reads** | plan, walkthrough, diff | small by construction - the artifact rule keeps them dense |

### 9.2 The cache facts the design leans on (from the API reference, read this session)

- **A cache hit is a byte-identical prefix on the same model in the same workspace.** Any byte
  that differs invalidates everything after it. Tools render first, then the system prompt, then
  the messages.
- **Reads cost a tenth of base input** (a fortieth on Fable 5.1). Writes cost 1.25× on the
  five-minute cache and 2× on the one-hour cache. A read refreshes the timer for free. This
  session's own system notice says Claude Code is using the **one-hour** cache on this plan,
  dropping to five minutes only in usage overage.
- **Parallel children with the same prefix all pay full price.** An entry becomes readable only
  after the first response starts streaming, so N siblings launched at once write N entries and
  read none. The runner therefore launches the first child of a run alone and the rest after it.
- **A fork must copy the parent's prefix verbatim.** Same model, same tools, same system prompt;
  fork-specific content goes at the end. Switching models is a guaranteed miss (caches are
  model-scoped), and so is changing the effort level mid-chain.
- **Measured by Anthropic:** caching alone cut agent-loop cost by 2.5× to 3.7× at 81% to 90% hit
  rates. It is the largest single lever on every model they measured.
- **Two CLI flags exist for exactly this.** `--system-prompt-snapshot on` (the default for the
  built-in prompt) records the system prompt once per conversation and reuses it verbatim on every
  request *and on resume*. `--exclude-dynamic-system-prompt-sections` moves the per-machine parts
  (cwd, environment, git status, memory paths) out of the system prompt into the first user
  message so that sessions share a byte-identical system prefix. Both are in the 2.1.258 help text.
  Whether the exclusion flag still applies when `--agent` supplies the system prompt is unverified
  (the help says it is ignored with `--system-prompt`); S0 measures it.

**Read from the vendor's own Claude Code pages this session (prompt caching, sessions, workflows),
and they sharpen the four points above:**

- **The cache is scoped to one machine, one directory and one git snapshot.** The system prompt
  embeds the working directory, platform, shell and memory paths, *and* the branch and recent
  commits captured at startup - so "sequential sessions share the prefix only when the git status
  snapshot at startup matches". Every child of a run already shares one worktree; what changes
  between children is the git snapshot, because children commit. Without the exclusion flag, every
  child after a commit misses. The flag is therefore mandatory for Layer 0, not a refinement.
- **Which cache lifetime a child gets.** Claude Code puts requests in two buckets. The *main
  conversation* bucket - interactive turns **and `-p` runs** - gets the one-hour cache on a
  subscription within plan usage, five minutes on usage credits or an API key. *Everything else* -
  sub-agents, workflows, forks, compaction - gets five minutes unless a setting says otherwise. The
  settings are `promptCacheTtl` and `subagentPromptCacheTtl` (or the matching
  `CLAUDE_CODE_PROMPT_CACHE_TTL` / `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL` variables, v2.1.242+),
  each `5m` or `1h`. Proof of which one a run got: `claude -p "hello" --output-format json` and read
  `usage.cache_creation` - one-hour writes appear as `ephemeral_1h_input_tokens`.
- **A fork reads its parent's cache, and it keeps its parent's system prompt.** Verbatim: "a fork
  inherits the parent's system prompt, tools, and conversation history exactly, so its first
  request reads the parent's cache." The consequence for seats is in Layer 2 below: a fork that
  changes the seat changes the system prompt and misses.
- **Even a missed fork is cheap next to redoing the research.** A miss re-*reads* the transcript
  once at base input price: a 100,000-token researched context is about fifty cents on Opus 4.8.
  Redoing the research is many turns of tool calls and output. So the fork's worst case is a small
  fixed cost, and the naive design's cost is the whole investigation again. This is the arithmetic
  that makes "fork, don't restart" the rule even when the cache is cold.
- **What never breaks the prefix, and matters here:** invoking a skill or a command appends a user
  message (the door's body rides in the conversation, not the system prompt); editing repository
  files appends a change notice; changing permission mode is cache-safe; on Fable 5.1 changing
  effort keeps the cache (v2.1.260+). What does break it: a model switch, an effort change on other
  models, an MCP server connecting or dropping while its tools sit in the prefix, a bare-tool deny
  rule, a Claude Code upgrade (a resumed session after an upgrade re-reads everything).

### 9.3 Five layers, cheapest first

**Layer 0 - siblings share one prefix (free after the first child).** Every child of a run is
launched in the same worktree with the same model, the same tool set, the same seat file, the same
preloaded skills, `--exclude-dynamic-system-prompt-sections` (mandatory: the git snapshot in the
default system prompt changes every time a child commits), and the snapshot on, with the
run-specific text appended at the end. The runner freezes the injected context for the run (the
hand-off and the repo map are read once at launch and passed as a file, not re-read by every
child's hook). The first child warms the cache; every later child of the same seat reads it at a
tenth of the price. Children of *different* seats have different system prompts and do not share
- which is fine, because the expensive part is not the prefix but the research, and that is
Layers 1 and 2.

**Layer 1 - a grounding pack, researched once per story.** Before the plan, one cheap child (the
Gnat, Sonnet 5, low effort, read-only) does the codebase research for THIS story and writes
`context-pack.md` into the run folder: the files the story touches with line anchors, the symbols
and contracts they lean on, where the tests live and how they run, the rules from
`project-context.md` that apply, the blast radius, and what the previous story in the epic
learned. Five to eight kilobytes. Every later child reads the pack **first**, explores only what
the pack lacks, and appends what it learned - the pack accretes like the walkthrough. This is
what BMAD's story file is meant to be ("all the context the agent will need") and rarely is,
because it is written before the tree is opened; the pack is its runtime companion, written from
the real tree at run time. It is also the seed of the Zoo variant's "seat memory", since a file is
platform-neutral.

**Layer 2 - fork, don't restart, inside a lane.** The implement child is not a fresh session. It
is `--resume <plan-session-id> --fork-session`: the plan child's whole researched context arrives
as a cache **read**, not a re-read, and the fork leaves the plan session untouched so a fix cycle
can fork it again. This is the old engine's "the Dev team resumes its own chat so it never
re-researches", made safer. Three consequences the runner enforces. **One seat per fork chain:** a
fork inherits its parent's system prompt exactly, and a seat *is* a system prompt, so the seat
that plans ② is the seat that implements ② and fixes ③'s findings - the **Cheshire Cat, end to
end**, which is also what the door itself is (② is one door: plan, stop, build). The White Rabbit
does not run ② in the robot; its work is the story shaping and the pack (section 2.2 is corrected
accordingly). **One model, one effort per chain** (Opus 4.8 today), because either change is a
miss. **The DeepSeek lane forfeits the fork** (a different endpoint is a different cache) and pays
Layer 1 instead - cheaper per token, no cache read, said plainly rather than discovered.

**Layer 3 - independence is bought on purpose, and only where it is worth it.** The audit child and
the review child are fresh by design: the SOP already calls this "the price of independence", and
SCC-362 makes it law for the review. What they must not do is *explore*: they read the pack, the
plan, the walkthrough and the diff - distilled artifacts - and nothing else unless the pack is
silent. The review's five lenses are sub-agents with their own prefixes (no cache is shared with
their parent, per the cost guide), which is the same cost a human ③ pays today and is bounded by
the engine's own `lens_budget: capped`.

**Layer 4 - the lead holds summaries only.** A child returns a structured result of a few hundred
tokens; the lead never opens a transcript. So the lead's context stays small, and the one cache
miss the design cannot avoid - the lead waiting on the operator longer than the cache lives - is
a miss on a small prefix, not on a researched one.

**Layer 5 - what a seat remembers across stories.** Two stores, both bounded by the house rule
that memory is long-term only: the shared `_artifacts/_memory` store every session already loads
(148 facts today), and the sub-agent `memory: project` field, which gives each seat its own slice -
the Queen keeps the Playwright browser path, the Cat keeps the Turbopack symlink rule. Story-scoped
facts never go there; they go in the pack and die with the run.

### 9.4 "They still need to follow the process - they are just switching personas"

Exactly so, and this is the sentence that keeps the design honest. The **door is the process**;
the **seat is who runs it**; the **pack is Step 0's grounding**. One amendment to the doors, in
their one body, never a fork: Step 0.6's grounding gains a clause - *if a `context-pack.md` exists
for this story, read it before exploring, and append what you learn to it*. A human running the
door reads the same clause and benefits the same way. The persona changes what is preloaded and
what the seat refuses; it changes nothing about the steps.

### 9.5 What the run looks like with the layers on (Story 14.2 again)

| Child | Seat / model | Prefix | Research source | Context source |
|---|---|---|---|---|
| 0 | Gnat, Sonnet, low | its own | explores (the only child that does) | writes the pack |
| 1 | Cat, Opus - ② up to the Step 2 stop | warms the Cat prefix | the pack | story file, ① tests |
| 2 | Queen, Opus max - `/cicd-self-audit` | its own | the pack | the plan |
| 3 | Cat, Opus - ② from Step 2.5 on | **fork of child 1**, same seat | inherited, cache read | plan plus audit |
| 4 | reviewer, Fable max - `/cicd-code-review` | fresh (different model, by law) | the pack | plan, walkthrough, diff; lenses capped |
| 5 | Cat, Opus - fix | **fork of child 1**, same seat | inherited, cache read | the finding |
| 6 | reviewer, Fable max | fresh | the pack | as child 4 |

Only one child explores. Two children inherit a researched context as a cache read. The two that
pay full prefix price are the two the law says must be independent, and they read distilled
documents rather than the tree. This is a structure, not a measurement; the measurement is the
first acceptance item below.

### 9.6 What this adds to the runner and the acceptance list

1. **Every child's JSON result carries its `usage` block**, and the runner records per child
   `input`, `cache_read`, `cache_write`, `output` and cost in the step's Jira comment, plus the run
   total. "Fresh session, demonstrated" gains a sibling: **"cache reuse, demonstrated"** - S0 runs
   the same small story naive and layered and the two totals go on the ticket.
2. **Launch order:** first child alone, siblings after it starts streaming.
3. **Fork chains are homogeneous:** one model, one effort, one tool set; the runner refuses a fork
   that would change any of them.
4. **The pack is a step**, with a schema the Queen can audit and the reviewer can read: no pack,
   no plan child.
5. **Children run back to back**, so the five-minute cache is refreshed by their own reads; an
   operator escalation that outlives the cache costs one prefix re-write on resume, which is
   priced and accepted, and the lead's own idle miss is small by construction (Layer 4).
6. **The runner sets the cache lifetime deliberately.** A `-p` child is main-conversation bucket
   (one hour on the subscription); a fork is not, and gets five minutes by default. Children run
   back to back, so five minutes is the cheaper write for them; the runner leaves the default and
   the S0 spike reads `usage.cache_creation` to prove which bucket each child landed in. If a real
   run shows forks missing across an escalation wait, `subagentPromptCacheTtl: 1h` is the one-line
   remedy, at 2× on the write.
7. **One house tool needs a warning label.** `approval_stops.py` reads the session transcripts under
   `~/.claude/projects/`; the vendor says that format is internal and changes between versions.
   The runner does not parse transcripts - it reads the child's JSON result - and the approvals
   harvest keeps working by the same grace it does today.

### 9.7 The first-party alternative: dynamic workflows, and why the runner still wins for this lane

Claude Code now ships an orchestrator of its own: a **dynamic workflow** is a JavaScript script,
written by Claude and saved as a `/command`, that spawns up to sixteen sub-agents at once, keeps
every intermediate result in script variables instead of any context window, gives each agent a
result schema, holds same-prefix siblings for up to five seconds so they read the first one's
cache, shows per-agent token counts live, and resumes within the session. It runs under `-p` too.
Its one hard rule is the one this design already has: "no mid-run user input - for sign-off
between stages, run each stage as its own workflow". That is the lead-plus-escalation shape,
confirmed from the vendor's side.

| Need | Python runner over `claude -p` children | Dynamic workflow |
|---|---|---|
| Fresh context per step | yes, and a session id the ticket can cite | yes |
| **Inherit the researched context** (Layer 2) | **yes** - `--resume --fork-session` | no fork; a workflow agent starts from its own prefix, so the build re-reads the plan and pack rather than inheriting the transcript |
| Seat identity with preloaded skills | `--agent <seat>` (verified in the help; S0 proves it) | agent type per `agent()` call - plausible from the fan-out rule ("same agent type"), unverified |
| ③'s five-lens fan-out inside the review | a `-p` child spawns its own sub-agents, so the real door runs as it does for a human | a workflow agent is itself a sub-agent and cannot spawn more; the lenses would run inline unless the engine is rewritten *as* a workflow |
| Model, effort, budget per step | flags per child | model per agent; budget at the run level |
| Cache stagger for parallel siblings | the runner launches the first alone | built in |
| Live cost view | the runner logs `usage` per child to the ticket | `/workflows` view |
| Code to maintain | one script and its tests | none, but a script Claude wrote that you read and rerun |

The runner wins on the two rows that carry the money and the law: the fork (the largest single
saving in this section) and the review's real fan-out (SCC-362). Workflows are the right home for
one thing later: the review engine's lens fan-out is, almost literally, the vendor's own example
of a workflow script, and rewriting the engine that way would give ③ a resumable, cost-visible
run for humans and robots alike. That is a separate ticket, not this one.

### 9.8 What Anthropic and the community actually do (web research, 2026-09-07)

The headline from the lookup: **nobody has found a way to make a fresh child inherit research for
free.** Every working design does one of three things - writes the research to a file once and
makes each child read the file instead of exploring; forks a session that already holds the
research so the child's first request is a cache read; or keeps the request prefix byte-identical
so siblings read each other's cache. Those are Layers 1, 2 and 0 above, which is reassuring: the
design is not novel, it is the consensus with names on it.

| Source | What they do | What it confirms or changes here |
|---|---|---|
| Anthropic, *How we built our multi-agent research system* (2025-06) | Orchestrator plus workers with separate context windows; workers act as "intelligent filters" and return condensed results; "subagents call tools to store their work in external systems, then pass lightweight references back"; every brief carries an objective, an output format, tool guidance and boundaries. Cost: agents run about 4× a chat, multi-agent about **15×** | Layer 4 (summaries only) and the structured result contract. The 15× is the bill the naive design would have sent. |
| Anthropic, *Effective context engineering for AI agents* (2025-09) | Just-in-time retrieval by lightweight identifiers (paths, line numbers); a sub-agent "might explore extensively, using tens of thousands of tokens, but returns only a condensed summary of 1,000-2,000 tokens"; structured note-taking in a notes file | The pack is the notes file; the Gnat is the exploring sub-agent; 1,000-2,000 tokens is the size of a child's return. |
| Anthropic, *Lessons from building Claude Code: prompt caching is everything* (2026-04) | Plan mode keeps every tool in the request so the prefix never changes; deferred tools are stubs; compaction forks "with the exact same system prompt, user context, system context, and tool definitions"; they alert on cache hit rate and "declare SEVs if they're too low" | The fork rule, from the people who wrote the fork. And the runner's per-child `usage` log is our version of their alert. |
| HumanLayer, *Advanced context engineering for coding agents* (2025-08) | Research → plan → implement as three phases, each writing a markdown file of paths, line numbers and data flow; implementation runs from the plan; keep context utilisation at 40-60%; sub-agents return "file paths, line numbers, conceptual summaries" | The pack's schema, almost verbatim. Their reported team spend ($12k per month on Opus) is the scale at which this discipline was worth formalising. |
| The Ralph Wiggum loop (Huntley 2025-07; quickstarts 2026-01) | `while true: cat PROMPT.md \| claude` - a fresh context every iteration, with state in files (`PROMPT.md`, a task list with pass flags, a progress file) and in git; "a progress file short-circuits exploration" | Fresh-per-step with files as memory is the operator's own round-1 instinct, proven at scale by others. Their quality cliff at roughly 150k of a 200k window is why children stay small. |
| Claude Code agent teams (docs, v2.1.178+) | A file-locked task list and JSON mailboxes as the shared memory; "the lead's conversation history does not carry over"; about **7×** tokens in plan mode; **not available under `-p`** | Confirms the round-3 finding, and the ticket-as-mailbox choice: a JSON mailbox on one machine is strictly less durable than a Jira thread. |
| claude-flow / ruflo (ruvnet) | A SQLite memory with namespaces and TTLs; big payloads in an artifact store, agents pass **manifest ids** rather than copying text; pre-tool hooks assemble a context bundle "under a few kilobytes, top-5 artifacts only" | The reference-not-copy rule: a child names the plan by path, never pastes it. And a bundle cap for what the runner injects. |
| Gas Town (Yegge, 2026-04) | State in git-worktree "hooks" that survive crashes; a "seance" that reads predecessor sessions' event logs "without re-reading entire codebases" | The worktree-as-state we already have; the seance is what the pack's "what the previous story learned" line does. |
| ccswarm, Claude Squad, Conductor | tmux plus a worktree per agent; **no shared memory between agents** | Isolation without sharing is the naive design. Flagged so nobody copies them for this. |
| Claude-Handover (2026-04) | a `HANDOVER.md` with nine sections - goal, progress, build and test status, uncommitted changes, decisions, failed approaches, blockers, resumption steps - "ephemeral infrastructure, not project documentation" | The house already has this as the walkthrough's `## Close-Out Handoff` and the plan's `## Self-Audit`; the pack adds "failed approaches" so a fork does not retry them. |
| Roo Code Boomerang / Orchestrator (docs 2026-05); Cline Memory Bank; RooFlow | `new_task(mode, message)`: "each subtask operates in complete isolation, it does not automatically inherit the parent's context"; the message must carry all context; the child returns one summary. Cline's bank: six files every task reads first (`projectbrief`, `productContext`, `activeContext`, `systemPatterns`, `techContext`, `progress`) | **The Zoo variant needs the pack more than Claude does**, because a Zoo subtask inherits nothing and has no fork. The house's `active-context.md` already is the Cline bank; the pack is its per-story slice. |
| Aider repo map; the vendor's `costs` and `memory` pages; Repomix | A tree-sitter, PageRank-ranked map fitted to a token budget so the model "can figure out by itself which files it needs"; a "codebase-overview" skill so Claude "gets this context immediately instead of reading multiple files"; `CLAUDE.md` under 200 lines; `.claude/rules` with `paths:` | The house repo map (8.4 KB) is this already; the pack is the story-scoped map. The 200-line advice is a measured target for what the lobby injects at start (56 KB today). |
| Measured caching in production (Deriv, 2026-07; mer.vin, 2026-08) | Hit rate 20% → 86% and input cost down 77% by ordering *instructions → shared context → history → latest message* and rendering deterministically; **ten identical calls with `--system-prompt` got zero cache reads** (only the default prompt carries the cache marker), about 4.4× overspend | The order is the runner's prompt layout. The zero-reads case is the one risk to Layer 0 - see the S0 item below. |
| Cost reports (claudefa.st; Augment 2026-05) | Delegation overhead about 4,000 tokens per hand-off before any work; deep tasks reach 96% of the score at 46% of the cost, short tasks pay a 60% markup for nothing; stacked verification about 2.3× baseline, a light supervisor cuts about 30% | Delegate only steps that read far more than the brief plus report - which is every door here - and never delegate a one-command step; run the audit and review once each, not in layers. |

**The one risk the lookup surfaced.** A seat delivered as a custom system prompt may fall outside
Claude Code's own cache marking, the way `--system-prompt` measurably does. Whether `--agent
<seat>` behaves like `--system-prompt` (replaces the default) or like an appended block is not
documented. So the design names both deliveries and lets S0 choose: **preferred** `--agent <seat>`
for its `skills:` preload, tools and memory; **fallback** the same seat file passed as
`--append-system-prompt-file` (appended after the cached default prompt, with
`--system-prompt-snapshot on` so resumes and forks reuse it verbatim), skills invoked by name in
the child's first message (a skill invocation appends a user message and is cache-safe), tools
scoped with `--allowedTools`. Ten identical launches, read `cache_read_input_tokens`: the delivery
that reads wins.

### 9.9 What round 3b changed in the design

1. The Cheshire Cat runs ② end to end (plan, then a fork for the build, then a fork for the fix);
   the White Rabbit shapes the story and owns the pack step with the Gnat. Section 2.2 corrected.
2. A grounding-pack step precedes the plan; the doors' Step 0.6 gains the one "read the pack
   first, append what you learn" clause, in their one body.
3. `--exclude-dynamic-system-prompt-sections` is mandatory on every child; launch order is first
   child alone; fork chains are one seat, one model, one effort.
4. The runner records every child's `usage` on the ticket, and S0 gains three measurements: naive
   versus layered on one story; the cache bucket each child lands in; `--agent` versus appended
   seat on ten identical launches.
5. Dynamic workflows are recorded as the first-party alternative and deferred; the review engine
   as a workflow is a separate ticket.
6. The Zoo variant inherits the pack as its primary saving, because a Zoo subtask inherits nothing
   and cannot fork.

---

## 10. The Zoo remote - phone to desktop, both directions (round 3c, 2026-09-07)

> *"For the subtask for Zoo, let's brainstorm and research the community for this next. What are our
> options for setting up mobile communications from my PC or Mac to my phone?"*

Section 2.6.1 scoped the subtask on the assumption that Zoo has no way in. That assumption was
wrong, and the correction changes the recommendation. This section replaces 2.6.1's option list;
its subtask framing stands.

### 10.1 Where each platform stands today (verified this session)

| | Claude Code (the lead) | Zoo Code (the March Hare) |
|---|---|---|
| Desktop to phone | Remote Control mirrors the session to the Claude app; push "when actions required" covers permission prompts and questions | `zoo_notify.py` polls Zoo's thread store and pushes through ntfy (title plus body, public topic named per machine). Installed as a service on both machines |
| Phone to desktop, text | Remote Control: prompts and `AskUserQuestion` answers from the phone | nothing |
| Phone to desktop, a permission prompt | **Remote Control forwards the local session's permission prompts to the phone and keeps them open until answered** (vendor page, read today; this closes section 8's first unverified item) | nothing |
| First-party chat bridges | **Channels** (research preview): Telegram, Discord and iMessage plugins push messages into a running interactive session and the session replies through them; a channel that declares the *permission relay* capability can forward permission prompts, and "anyone who can reply through the channel can approve or deny tool use in your session". Not for `-p`. Sender allow-lists by pairing | none |
| Launch from the phone | Desktop app **Dispatch**: message a task from the Claude app and the desktop spawns a session (Pro or Max) | none |

So the Claude side is finished twice over: Remote Control for the app, channels if he prefers a
chat app. The whole subtask is the Zoo column.

### 10.2 What Zoo can actually do from outside (measured on the installed 3.83.100457 bundle and read in Zoo's source on GitHub)

Zoo kept Roo Code's programmable surface intact. Two doors exist, and they differ in exactly one
capability.

**Door 1 - the IPC socket, no extension needed.** When the extension host starts with the
environment variable `ROO_CODE_IPC_SOCKET_PATH` set, Zoo opens a Unix-socket server at that path
(`new IpcServer(socketPath).listen()`, in `src/extension/api.ts`). Over it a script can send:

| Command | What it does in Zoo |
|---|---|
| `StartNewTask` (configuration, text, images, newTab) | starts a task - the March Hare's whole run, launched from a script |
| `ResumeTask` (taskId) | resumes a parked task |
| `SendMessage` (text, images) | delivers text into the running task. In Zoo's `Task.ts`, `submitUserMessage` calls `handleWebviewAskResponse("messageResponse", text)`: a pending **`followup` ask is answered by it** - which is precisely the March Hare asking the operator a question - while for a pending **`tool` or `command` ask it is feedback, not approval** (Roo treats text on a tool ask as reject-with-feedback) |
| `CancelTask`, `CloseTask`, `DeleteQueuedMessage`, `GetModes`, `GetCommands` | housekeeping |

And it **broadcasts every task event** to connected clients: `Message` (each chat message,
asks included, with the ask type), `TaskInteractive` (the task is waiting on the user - the exact
"needs you" moment), `TaskIdle`, `TaskCompleted` with token and tool usage, `TaskAskResponded`,
`TaskDelegated` and its completion (the `new_task` hand-offs between seats), `TaskToolFailed`,
`TaskTokenUsageUpdated`. That is the event surface the SOP row says Zoo does not have; it exists,
behind an environment variable, and it makes the thread-store poller unnecessary.

**Door 2 - the in-process extension API.** The same object is exported to other extensions
(`vscode.extensions.getExtension("zoocodeorganization.zoo-code").exports`) and carries what the
socket does not: `approveCurrentAsk()` (a real `yesButtonClicked`), `pressPrimaryButton()`,
`pressSecondaryButton()`, `isReady()`, `getConfiguration()`. Reaching it takes a **bridge
extension** - a few dozen lines that subscribe to the API's events and expose approve / reject /
send on a local socket. It must be installed per machine (a local `.vsix`).

**What this means for the two requirements:**

- **Replying with text or a decision from the phone** needs only Door 1. The phone's message
  reaches a desktop bridge script, which writes it into the running task with `SendMessage`. If the
  March Hare asked a `followup` question, that *is* the answer, in the conversation, with no ticket
  polling. The ticket comment stays as the durable record.
- **Clicking a Zoo permission prompt from the phone** needs Door 2 (or a phone UI - 10.3). A tool
  ask cannot be approved by text; it needs `approveCurrentAsk`.

**Where the socket lives on each machine.** On the Mac the extension host is local, so the socket
is a local path and the bridge runs beside it. On the PC the workspace is inside WSL, so the
extension host runs *inside Ubuntu* (the extension is installed under `~/.vscode-server` too, measured) - the
socket is a Linux path, the environment variable has to be exported from the WSL login shell the
server inherits, and the bridge runs in WSL, where `zoo_notify.py` already runs. Zoo's bundle also
reads `ZOO_CODE_BASE_URL` and the `ROO_CODE_CLOUD_*` variables, so a Roo-era cloud client is still
compiled in; whether anything answers it after Roo's shutdown is a 10.3 question.

**Security, stated before the options.** `SendMessage` puts text into a coding agent that holds
your credentials and your repositories. Whatever channel feeds the bridge is a prompt-injection
path for anyone who can write to it. A public ntfy topic is disqualified for the inbound half; the
inbound channel must authenticate the sender (a Telegram chat-id allow-list, a reserved ntfy topic
with an access token, or Tailscale-only reachability), and the bridge should refuse `StartNewTask`
from the phone unless the operator explicitly wants launches, since that is the highest-impact
command on the socket.

### 10.3 The option catalogue (community and vendor research, 2026-09-07; URLs in the research record on the ticket)

Two corrections to 10.2 from the research. First, **Roo's own remote control is dead and Zoo cannot
revive it**: Roo's "Roomote Control" was a cloud bridge merged 2025-09-10; Roo shut its extension,
cloud and router on 2026-05-15; Zoo's source has no bridge directory and no `remoteControlEnabled`
setting, and its cloud config still points at the dead `app.roocode.com`. Second, the IPC socket's
`SendMessage` on a pending **tool** ask is confirmed in Zoo's source as *denied with feedback*
(`toolDeniedWithFeedback`), so the socket must never be used to answer an approval. One addition:
Zoo ships a headless **`roo` CLI** (a standalone agent through a VS Code shim, `--print`, NDJSON
prompt streams, macOS and Linux tarballs). It does not attach to a running VS Code, so it is not a
remote; it is a lever for the Zoo *autopilot* variant (S8), because it is Zoo's `claude -p`.

| Option | Text reply | Button reply | Clicks a Zoo approval | Mac | PC (WSL) | iOS | Android | Effort | Cost |
|---|---|---|---|---|---|---|---|---|---|
| **Claude Remote Control** (Claude app) | yes | yes | no | yes | yes | yes | yes | none, already on | plan |
| **Claude channels, Telegram plugin** (first-party, research preview; needs Bun; `--channels` at launch; pairing then an allow-list policy) | yes | **Allow / Deny inline buttons**: the plugin declares the permission relay and forwards Bash, Write and Edit prompts; the first answer, terminal or phone, wins; trust and MCP-consent dialogs are not relayed | no | yes | yes | yes | yes | low | free |
| **Telegram bot bridge for Zoo** (a Python bot on the Bot API, long polling, no inbound port, chat-id allow-list; feeds Zoo's IPC socket for text and the companion extension for buttons) | yes | yes | **yes, through the companion** | yes | yes | yes | yes | medium | free |
| **ntfy `http` actions** (extend the existing poller: up to three buttons per push, each a POST to a reply topic; desktop subscribes by SSE) | Android and web only - **the iOS app cannot compose a message** | yes | through the companion | yes | yes | yes, with an open bug (the notification does not clear after a tap) | yes | low | free on a public topic, $6/month for a reserved one, or self-host |
| **Companion extension for Zoo** (about fifty lines: reads Zoo's exports, listens on a local socket, calls `approveCurrentAsk` / `pressSecondaryButton`; or `zoo-code.acceptInput`, which presses the primary button when approval buttons are showing) | n/a | n/a | **yes, the only script-level path** | yes | yes, installed in the WSL extension host | n/a | n/a | medium | free |
| **VS Code Remote Tunnel in the phone browser** (`code tunnel`; on the PC run it *inside WSL*, the Windows toggle starts the wrong side; same GitHub or Microsoft account both ends; Zoo's webview renders in the browser as a workspace extension - Roo is on record running in Codespaces and code-server) | yes | yes | **yes, the real button** | yes | yes | yes | yes | low | free |
| **Tailscale Serve plus `code serve-web` or code-server** | yes | yes | yes | yes | yes | yes | yes | medium | free |
| **SSH plus tmux** (Blink or Termius over Tailscale) | yes | yes | no (Zoo is a panel, not a terminal) | yes | yes, with the WSL port dance | yes | yes | low | app |
| **Happy Coder** (wraps `claude`; end-to-end encrypted relay; iOS and Android; approves permissions) | yes | yes | no | yes | yes | yes | yes | low | free |
| ccgram, Claude-Code-Remote, VibeTunnel, Omnara | Claude-only bridges; VibeTunnel has no Windows build; Omnara's mobile product could not be verified | | no | | | | | | |
| Pushover, Pushcut, Home Assistant | push with a webhook at best; nothing the rows above lack | | no | | | | | | |

### 10.4 The recommendation, and the one tradeoff

> **Ruled 2026-09-07 (round 3d):** the Claude lead stays on Remote Control and gets nothing more;
> the Zoo remote is the thing to build; his phone is **iOS**. So the phone carries two apps - the
> Claude app for Claude, Telegram for Zoo - and the "one app" argument in this section is history.
> iOS settles the inbound choice: the ntfy iOS app cannot type a reply, so the Telegram bot it is.
> The four pieces below stand. Still open: the approve path (ruling 5).

**One phone app for both platforms, and that app is Telegram.** The inbound half of the Zoo remote
has to be authenticated (10.2's security paragraph), it has to accept free text on whatever phone
he holds (the ntfy iOS app cannot type), and it has to carry buttons. A Telegram bot with a chat-id
allow-list does all three for free, from WSL and from the Mac, with no inbound port. And Claude
already has a first-party Telegram channel with Allow and Deny buttons, so the same app serves the
lead. ntfy keeps the job it does well - outbound pings - or retires; it does not become the inbound
channel.

**The Zoo remote, in four pieces:**

| Piece | What it is | What it replaces |
|---|---|---|
| **Events, not polling** | The bridge subscribes to Zoo's IPC socket. `TaskInteractive` is "needs you", `TaskCompleted` is "turn complete", `Message` carries the ask text and type. The poller over the thread store retires once this is proven; its store format is internal to Zoo | `zoo_notify.py --watch` |
| **The bot** | `zoo_bridge.py`, stdlib only like the rest of the toolkit: Telegram Bot API by long polling, chat-id allow-list, refuses `StartNewTask` from the phone. A **text** reply goes in as `SendMessage`, which answers a pending `followup` ask - so the March Hare's escalations are written as `ask_followup_question`, and the phone answers them *in the conversation*. An **Approve / Reject** tap goes to the companion. Every escalation is mirrored to the ticket as the `Needs Mr. Hatter` comment, so the durable record is unchanged | the reply topic and `zoo_inbox.py` of 2.6.1 |
| **The companion** | A fifty-line VS Code extension that takes Zoo's exports and exposes approve / reject on a local socket; packaged as a `.vsix`, installed on the Mac and in the PC's WSL extension host | nothing - this is the piece that did not exist |
| **The tunnel** | `code tunnel` set up once per machine (inside WSL on the PC) as the fallback for the dialogs no bridge relays, and for looking at the panel itself | the "raw asks are desk-only" limitation |

**For the Claude lead:** Remote Control stays the baseline - it is on at startup, it forwards
permission prompts and questions to the phone today, and it costs nothing to keep. The Telegram
channel plugin is the optional unification: an hour of setup (BotFather token, plugin install,
`--channels` on the lead's launch line, pairing, allow-list), reversible, and a research preview
whose flag syntax may change. Recommend adding it after the Zoo bot exists, so the phone ends up
with one app and two bots rather than two apps.

**The tradeoff that is his:** one app (Telegram, two bots, one of them a preview feature) against
two apps (the Claude app for Claude, ntfy for Zoo with buttons only on iOS). The rest is engineering.

**Prerequisites that are Ask-First:** a Telegram bot token (kept under `keyway-secrets`, never in
git); the `ROO_CODE_IPC_SOCKET_PATH` variable exported where each extension host inherits it (the
Mac's launch environment; the WSL login shell the VS Code server starts from - whether the server
inherits `~/.profile` is measured in the subtask's first step); installing a local `.vsix` on both
machines; Bun, only if the Claude channel is added.

**Proof for the subtask:** one `followup` question from the March Hare answered by text from the
phone and visible in the Zoo conversation; one tool ask approved by a tap; both mirrored on the
ticket; the poller off and nothing missed for a day.

### 10.5 What section 10 changes elsewhere in this design

1. Section 2.6.1's option list is superseded by 10.3 and 10.4; its subtask framing stands.
2. Section 7, ruling 4 becomes: *Telegram bridge for the Zoo inbound half (recommended) or ntfy
   actions*; a fifth ruling is added: *the companion extension as the approve path, with the tunnel
   as fallback*; and a sixth: *whether the Claude lead also moves to the Telegram channel*.
3. Section 8 gains three unverified items: Zoo's webview usability on a phone through a tunnel; the
   WSL VS Code server inheriting the socket variable from the login shell; and the IPC surface being
   identical on the installed 3.83 build and the `main` source read today.
4. The Zoo variant (S8) gains a lever: Zoo's headless `roo` CLI as its equivalent of `claude -p`.

---

## 11. Drift - the autopilot owns no copy of the workflow (round 3d, 2026-09-07)

The operator's requirement, in his words: *"I want this to scale on top of the development workflow
we use, not be something stand alone. When we make edits to the workflows and the / commands and
the rules, it auto-updates because it's using the same ones. I don't want to worry about drift."*

**The answer is yes, and it is true by construction rather than by discipline, because the house
already works that way.** Every surface an agent reads today is a *pointer* to the master, resolved
at the moment of use; the autopilot adds no second copy of any of them. This section is the proof,
taken from the tree this session, and the one rule the build must keep.

### 11.1 How each surface reaches an agent today, and what the autopilot adds

| Surface | How it reaches a Claude session today (read this session) | How it reaches Zoo | What the autopilot adds |
|---|---|---|---|
| **A door** (`/cicd-*`, `/smh-*`) | `.claude/commands` is a **retired** door (the sync writes nothing there). Claude enters through a **generated launcher skill**, `.claude/skills/<name>/SKILL.md`, whose whole body is *"read `.agents/commands/<name>.md` and follow it END TO END"*. The master is loaded at invocation, not at sync. An edit to a door body is live on the next invocation with no sync at all; a sync is needed only when a door is **added, renamed or retired** (its launcher), and the manifest plus `-Status` police that | `.roo/commands/<name>.md`, the same one-paragraph pointer, generated by the same sync | **Nothing.** The runner passes the door's *name* to the child, the way the operator types it (`/cicd-dev-story-tests AGY_AVIATIONCHAT 14.2`), never its text. The child loads the master through the same launcher the chat uses. The runner's only check is that the master file exists (2.3 rule 1) |
| **A seat** (March Hare, Cheshire Cat, ...) | none yet - Claude has no seat today | `.roomodes` is GENERATED, and each `roleDefinition` is itself a pointer: *"Read `.agents/commands/smh-team-march-hare.md` and follow it END TO END"*; `.roo/rules-<slug>/01-persona.md` is the same pointer. `test_zoo_team.py` compares GENERATED against MASTER on every suite run | **A renderer, not a file.** The runner reads the seat master's frontmatter at every launch and hands the child a session-only definition through `--agents <json>` (verified on the sub-agents page: *"exist only for that session and aren't saved to disk"*, and they outrank any `.claude/agents/` file). The prompt is the same pointer sentence `.roomodes` carries. So `.claude/agents/<seat>.md` is **never written** - there is no second file to go stale, and a stale one could not shadow the master anyway |
| **The rules** (`.agents/rules/*.md`) | Three paths, all live: the three floor rules are `@`-imported by `CLAUDE.md`; `.claude/rules/` is read natively; and the `rule-trigger.py` UserPromptSubmit hook matches every prompt against the rules' `triggers:` and injects *"this prompt matches standing law - read before you act"* (that is how the mobile and Zoo-team rules arrived in this very turn). The SessionStart hook adds active-context and the repo map | `.roo/rules/` holds the four rules the seats share (`zoo-team` plus the floor), a copy the sync owns - the existing arrangement | **Nothing.** A `-p` child runs every hook the chat runs. The design therefore **forbids `--bare`** on any child: `--bare` skips hooks, and the hooks are how the law reaches the child |
| **The skills** (`.agents/skills/`, `.claude/skills/`) | A seat's `skills:` list preloads the **full content** of each named skill at startup (sub-agents page). The content is read from the skill file at that moment | the seat's master names its skills in prose; Zoo has no preload | **Only the list.** The list of skills per seat lives in the master's frontmatter (a `claude-skills:` key beside the existing `mode-groups:`), so editing a skill's body is live at the next launch, and changing *which* skills a seat carries is an edit to the master, same as today |
| **The charter** (2.5, what the lead may pass) | does not exist yet | - | **A house door, not runner code.** The charter is the body of the rewritten `cicd-autopilot-claude.md` (S4), under the same `sop-currency` gate as every other door. The runner never reads it; the lead does, the way it reads any door |
| **The order of the steps** (① ② ③) | `workflows_testing_SOP.md` (the operator's manual) and the lane door that cites it | the March Hare master, which cites the same two pages | **Nothing.** The runner has **no list of doors**. It is called once per step with a door name, a seat, a budget and a cwd. This is the exact difference from the retired `.ps1` engines, which hard-coded the stages in 2,052 lines and drifted the day the doors changed |

### 11.2 What the runner does own, so the drift surface is bounded

Five things, none of them workflow content: how to launch a child (the flag set), the result schema
(2.3 rule 3), the `jira_feed.py step` verb, the seat renderer (master frontmatter to `--agents` JSON),
and the budget table. When the workflow changes, nothing in the runner changes. When Claude's CLI
changes, only the runner changes. Everything the operator edits day to day - a door, a rule, a skill,
a seat's charter - is read by the autopilot's children from the same file the chat reads, at the same
moment, through the same launcher.

### 11.3 The one rule the build keeps, and its test

**The runner may not contain the text of any door, rule, or seat.** Acceptance test in S1: a grep
of `autopilot_run.py` for any heading or sentence that also appears in `.agents/commands/` or
`.agents/rules/` fails the suite; and the seat renderer's unit test is the Zoo one's twin - it
compares the JSON the runner would hand to `--agents` against the master's frontmatter, never
against a table typed into the test. The Zoo variant (S8) inherits all of this unchanged, because
`.roomodes` and `.roo/commands/` already are pointers.

### 11.4 What round 3d changes elsewhere in this design

1. Section 2.2's "second projection `.claude/agents/<seat>.md`" is withdrawn; the seat is rendered at
   launch (11.1, row 2). S2 becomes the renderer and its parity test, and no agent file is written.
2. Section 2.3 rule 1 gains its second half: the runner passes the door's name, never its text.
3. Section 8 gains one item: whether `--agent <seat>` resolves a seat defined by `--agents <json>` on
   the same launch line, running the whole `-p` session as that seat with its `skills:` preloaded.
   The docs state each half; S0 measures the pair. Fallback if not: `--append-system-prompt-file`
   with the same pointer sentence, which is still no file on disk.
4. **Rulings closed by his word today:** ruling 2 and ruling 6 - the Claude lead stays on Remote
   Control and gets nothing more (no Telegram channel); ruling 4 - the Zoo inbound is the Telegram
   bot, because his phone is iOS and the ntfy iOS app cannot type a reply. Still open: rulings 1, 3
   and 5. Section 10.4's "one app" argument is history: the phone carries the Claude app for Claude
   and Telegram for Zoo.
