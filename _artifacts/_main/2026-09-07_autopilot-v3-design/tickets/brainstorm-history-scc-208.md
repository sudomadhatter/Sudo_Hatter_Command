# Brainstorm history - SCC-208 (an Idea ticket; deleted by the operator 2026-09-07 as brainstorm-only)

Snapshot taken with acli before the delete, so the rounds survive beside the design record they summarise
(`../implementation_plan.md`). Nothing here is law; the record is.

**Summary:** Retire the autopilot AP lane and design its replacement: a headless terminal orchestrator that runs the existing workflow  
**Type / status:** Idea / To Do  
**Created:** 

## Description (round 1 - the 2026-08-17 ruling)

STANDALONE TICKET by operator ruling, 2026-08-17. Cut out of SCC-197 wave 2 (was SCC-207, deleted as
a subtask) because it is a design brainstorm, not a fix, and it must not gate the wave-2 landing.

=========================  THE RULING THAT DEFINES THIS TICKET  =========================

Operator, 2026-08-17, verbatim:

  "after everything we changed the auto pilots are stale and not great we will probably retire them.
  we can use them for reference when making new ones but the old artifact stye sharing of knowledge
  is stale, we can use jira and the commets on the ticket for the agents if they need to talk. at
  this point to make a good autopilot all we need to do is build an orchestator agent who can run
  the work flow we already made. we can do all this in the terminal instead of a chat and just have
  the whole thing headless and it can spin up as many fresh session as it needs to all in the
  terminal. it will actually be better than the manual way I do it because I dont change to a fresh
  context window as often as I should. but that is a brain storm for another day."

So this ticket is NOT "restore the AP lane." It is: RETIRE the AP lane, and design its replacement.
The four -AP delivery options SCC-70 spent its life on are moot - option 4 (retire) is the ruling.

=========================  WHAT THE REPLACEMENT IS  =========================

An ORCHESTRATOR AGENT that drives the workflow this repo already has, rather than a bespoke pipeline
that reimplements it:

  - Runs in the TERMINAL, headless. No chat session is the host.
  - Spins up as many FRESH sessions as it needs. This is the actual advantage over the manual lane,
    in the operator's words: "it will actually be better than the manual way I do it because I dont
    change to a fresh context window as often as I should." Context hygiene becomes mechanical
    instead of remembered - which is the same defect SCC-203 just fixed one level down, where a
    review ran inside the builder's own context and nothing downstream could see it.
  - Agent-to-agent handoff moves to JIRA TICKET COMMENTS, not artifacts. The artifact-passing style
    (stage2-audit.json, stage4-review.json and friends) is declared stale. Note this repo already
    has the plumbing: jira_feed.py posts and reads ticket comments, and one Dev Record per ticket is
    already an update-in-place channel.
  - The existing /smh-* and /cicd-* commands ARE the workflow. The orchestrator runs them; it does
    not carry its own copy of their behaviour. That is what killed the -AP lane: three parallel
    command bodies that had to be delivered somewhere and then kept in sync.

The old engines are REFERENCE MATERIAL for this, not a base to patch:
  Projects/AGY_AVIATIONCHAT/scripts/autopilot-dev-story.ps1 (+ -opencode variant)
  Projects/NEXgen-VR-Director/scripts/autopilot-dev-story.ps1 (+ -opencode variant)
  Projects/BRKN_Tattoos/scripts/autopilot-dev-story.ps1 (+ -opencode variant)
  Lobby spec: .agents/commands/cicd-autopilot-claude.md (stage table at :173-176)

=========================  MEASURED GROUND TRUTH (2026-08-17) - keep, it explains WHY  =========================

Re-measured against the live tree while assessing SCC-70. Recorded here so nobody re-researches it,
and because it is the evidence that repairing the old lane was never worth it.

1. All four live engines in the two maintained projects still call the RETIRED underscore names
   /sudo-dev-story-tests_AP, /sudo-self-audit_AP, /sudo-code-review_AP. The lobby's real files are
   cicd-dev-story-tests-AP.md, cicd-self-audit-AP.md, cicd-code-review-AP.md.

2. -AP has NO delivery path under ANY name. sync-agents.ps1 skips it at every site: :459, :695
   (door generation), :842, :882 (opencode local), :972 (both global caches). Project targets
   hard-error at :115-121; -Maintained hard-errors at :98-105.

3. ⛔ THERE IS NO MACHINE-GLOBAL CLAUDE CACHE. ~/.claude/skills = 0 files, ~/.claude/commands = 0
   files. The only two global caches sync-agents writes are opencode (~/.config/opencode/commands,
   56 cmds) and antigravity (~/.gemini/antigravity/global_workflows, 37). Claude doors are generated
   into the LOBBY's .claude/skills only. This is what disproved SCC-70's recommended Option 2, whose
   whole rationale was "the doors land in the MACHINE-GLOBAL caches, which is exactly where the
   engines' claude -p calls resolve from inside any project repo." They do not.

4. THE REAL DEFECT, and it must not be reinherited: an unresolved stage name does not crash. The
   engine builds a prompt whose body says "Your full stage instructions live in the /<name> command
   above" and runs claude -p. The stage then runs with NO specification, improvises, and writes
   artifacts that look normal. ⛔ THE ORCHESTRATOR MUST FAIL LOUDLY on an unresolvable step, proven
   by a negative-control test. Carry this forward - it is the one line of SCC-70 worth keeping.

5. BRKN_Tattoos, the frozen fork, is the ONLY project where AP doors still exist (6 AP skills, 28
   .claude/commands, under the OLD names matching its OLD engines). The project deliberately not
   maintained is the only one whose autopilot could still resolve - direct evidence the breakage
   arrived with the 2026-08-07 thin-model strip.

=========================  EXPLICITLY NOT IN SCOPE (operator ruling, same message)  =========================

The retired /sudo-* command surface sitting in the project repos is FILE CLEANUP / DEBT, not a
defect this ticket fixes. Operator's words:

  "for AGY adn NexGen VR, they should not even have these / commands anymore. we only use them from
  the command center. they only thing either of them should still have it the required bmad agents
  since the storys and epics and sprint logs are all tracked with it. So yes im confused on that one
  too, but also not worried about it, sounds like file clean up."

  "BRKN again I dont care its just stale. This project is also finished so this is just file clean
  up. this is debt we will deal with if we need to update the site at a later time."

So the target state for AGY_AVIATIONCHAT and NEXgen-VR-Director is: NO slash-command surface at all,
BMAD agents ONLY (stories, epics and sprint logs are tracked with BMAD). That is consistent with the
thin model and with what is already there - AGY has 1 skill / 0 commands, NEXgen-VR has 0 / 0.
BRKN_Tattoos is a finished site; its 116 skills / 28 commands stay until the site needs an update.

If that cleanup is ever wanted it is its own small ticket, per repo (cross-repo law: a ticket per
repo). It is NOT a blocker for anything here.

=========================  SCOPE  =========================

BRAINSTORM FIRST - the operator has explicitly deferred this ("a brain storm for another day"). Do
not start building. When it is picked up:

1. Design the orchestrator: what drives it, how it launches a fresh session per step, how it decides
   a step passed, how it recovers. It runs the EXISTING commands - no forked command bodies.
2. Define the Jira-comment handoff contract: what one step leaves for the next, and how a step reads
   it. jira_feed.py is the existing channel; extend it rather than inventing a second one.
3. Negative control from day one: an unresolvable or failed step FAILS LOUDLY. Prove it with a test
   that fails against a naive implementation.
4. Rule on what happens to the three projects' six engine files and to cicd-autopilot-claude.md -
   deleted, or kept as reference with a do-not-run banner.
5. Nothing is owed to SCC-70 - it was deleted from Jira on 2026-08-17 (see the carried-forward
   section at the foot of this ticket). This ticket IS its successor.

=========================  ACCEPTANCE  =========================

1. A design recorded and ruled on by the operator before any code.
2. The orchestrator runs the existing workflow commands; no duplicated command bodies anywhere.
3. Fresh session per step, demonstrated - not claimed.
4. Handoff via Jira ticket comments, demonstrated end to end on one real ticket.
5. A failed or unresolvable step fails loudly, proven by a test that can fail.
6. The sudo-command-center scope carried forward below is either done here or minted as its own
   ticket - it must not be lost a second time.

=========================  CARRIED FORWARD FROM SCC-70, WHICH NO LONGER EXISTS  =========================

⛔ SCC-70 was DELETED from Jira on 2026-08-17, partway through this assessment, taking its subtask
SCC-81 with it (a parent delete cascades). Not recoverable - acli exposes archive/unarchive only, and
SCC-70 was deleted rather than archived. Its measured claims are preserved above. This section
preserves the ONE scope it carried that is not covered above, so it does not vanish with the ticket.

SUDO-COMMAND-CENTER REBUILD (SCC-70 had absorbed this from SCC-81, which said it can be deleted once
folded in - so this text is now the only surviving record of it).

  Target: sudomadhatter/sudo-command-center - the TEACHING EDITION. A project-agnostic clone of this
  command center, the repo shared with other people. It is NOT sudo-project-skeleton, which is a
  separate, clean PROJECT template repo. SCC-81's own summary named the wrong repo ("Update git sudo
  project skeleton") while its body named the right one ("the clone repo of sudo hatter command...
  the one I share with others"); the body is correct.

  SEQUENCING, and it is the reason this belongs on THIS ticket: the teaching-edition rebuild must not
  start until the autopilot question above is ruled on. Rebuilding it first would bake the dead AP
  lane into the repo strangers clone. It also runs after the command-center rebuild already in
  flight lands.

  If this is picked up on its own it should be minted as its own ticket and this section deleted here.

## Comment 1 - Sudo Hatter

Information found above the brainstorming session one information found here as a brainstorming session two:

## Comment 2 - Sudo Hatter

Brainstorm round 3 (2026-09-07, Claude session) - DESIGN for ruling. Nothing built, nothing minted.

Full record in the lobby: _artifacts/_main/2026-09-07_scc-208-autopilot-v3-design/implementation_plan.md

THE SHAPE. One interactive LEAD session (the March Hare, Remote Control on) never does the work itself. For each step it calls a small deterministic RUNNER script, and the runner launches a fresh headless "claude -p" child for that one step. Each child starts AS one Wonderland seat - a Claude agent definition (.claude/agents/<seat>.md) rendered from the same smh-team-*.md master that already makes the Zoo mode - with that seat's skills preloaded and its rules named, and it runs the EXISTING door (/cicd-dev-story-tests, /cicd-self-audit, /cicd-code-review), never a copy. Every child returns a structured result (done / blocked / needs_human / failed) and the runner writes it onto the story's ticket as a comment before the lead sees it. The review is a fresh child on Fable at max with NO seat identity (SCC-362 carried into the robot). The lead answers what its written charter allows and escalates the rest as one tap on the phone (Remote Control chip) with a durable "Needs Mr. Hatter" comment on the ticket that it polls for a reply.

TERMINAL PERMISSIONS (the threat from round 2). In a headless child a prompt cannot wait: the CLI denies the tool call at once and the model sees it. So the failure changes from "a stall that breaks the cache and bills the context twice" to "a step that could not do its work", and the child reports it (denials[] in its result). Next morning /smh-llm-approvals harvests the denial into an allow row - the list keeps getting better, as you said. Children run --permission-mode auto, not bypass: bypass buys nothing here (this repo has ZERO Claude deny rows - the fence is six PreToolUse hooks + the git hooks + the GitHub ruleset, all of which bind a child exactly as a chat). One trap written down so it costs nothing: the runner must go on sandbox.excludedCommands (like jira_feed.py) or the child cannot reach the model from inside the lead's sandbox.

MEASURED TODAY. CLI 2.1.258 installed; --permission-prompts none (explicit prompt=deny) needs 2.1.259. Agent teams do not spawn under -p, so the "lead in chat with sub-agents" is built from claude -p children + the ticket thread. .claude/agents/ does not exist yet. Remote Control + push notifications are already on at startup on this machine.

PHONE, TWO-WAY. Claude side: exists today - Remote Control mirrors the whole lead chat, so you type or tap from the phone. Zoo side: the outbound half exists (zoo_notify.py pushes through ntfy on every ask Zoo could not auto-decide and every turn end); the INBOUND half is the gap - Zoo has no remote surface and no API to inject a message.

ZOO REMOTE - ITS OWN SUBTASK (your word today). Builds the inbound half only: (1) zoo_notify.py learns the "Needs Mr. Hatter" shape with a Click action opening the ticket; (2) zoo_inbox.py, a sibling service on a SECRET ntfy reply topic (keyway-secrets), posts each reply you send from the ntfy app onto the escalated ticket as an "Operator reply" the March Hare's 60-second poll reads; (3) a reply typed in the Jira app is the same thing, zero build; (4) raw permission asks are the one thing no inbox can click - fallback is a VS Code Remote Tunnel (vscode.dev on the phone shows the real Zoo panel), which is why the design keeps raw asks rare and routes every DECISION through the ticket. Telegram is the swap for the ntfy reply topic if you want chat UX - the inbox script is the only file that names the channel. Proof: one escalation answered from the phone and acted on. Independent of the runner, can start beside S1. /smh-plan-task mints it with the rest.

ZOO VARIANT (phase 2, Claude first). Section 2.6 of the record: the lead is the March Hare mode itself, children are new_task subtasks (fresh contexts), seats are the .roomodes already rendered from the same masters, the step verb is the same script. No runner possible in Zoo; the law lives in the March Hare master plus structure (no seat runs the review, so it parks at review-ready where March Hare parks today).

RULINGS NEEDED (product calls only):
1. The charter table (record section 2.5) row by row - which gates the lead may pass on your launch word. The row worth a second look: your launch word covering step 2's "continue" in /cicd-dev-story-tests, which today is your model-switch moment. NO-GO audits, new dependencies, schema/CI/security changes, file deletes, a second non-PASS review, and any landing always escalate or never happen.
2. Telegram deferred for the Claude lead (tap chip + ticket cover it).
3. Old lane: delete the three -AP twins and the opencode launcher now; fold the deepseek lane into a runner flag; banner the six .ps1 engines "reference only" now and delete AGY's + NEXgen's after the first real story passes; BRKN's stay.
4. Zoo remote inbound channel: ntfy reply topic (recommended, already installed and yours) or Telegram.

PREREQUISITES before the first spike (both need your word): CLI upgrade to >= 2.1.259; two settings rows taking the runner out of the lead's sandbox (an /smh-llm-approvals Step 4 edit, not a lane).

Build order after ruling (via /smh-plan-task): S0 half-day spike (agent+skills preload under -p, json-schema round trip, child network, phone chip) -> S1 runner + negative-control test (missing door exits non-zero with no claude call) -> S2 seats rendered by /smh-sync-agents -> S3 jira_feed.py step verb -> S4 the /cicd-autopilot door -> S5 one real AGY story -> S6 retire the old lane -> S7 Zoo remote (own subtask, can run beside S1) -> S8 Zoo variant.

## Comment 3 - Sudo Hatter

Brainstorm round 3b (2026-09-07, same Claude session) - CONTEXT AND COST. Answers the question "how is each agent's cached information handled, how do they share artifacts, and how do we stop every sub-agent re-researching the codebase". Record: section 9 of _artifacts/_main/2026-09-07_scc-208-autopilot-v3-design/implementation_plan.md (vendor pages and community sources cited there).

YOU WERE RIGHT. Round 3 as written - six fresh children each free to explore - is the 15x bill Anthropic measures for naive multi-agent (4x for one agent vs chat, 15x for multi-agent). The fix is five layers, cheapest first; none of it is novel, it is what Anthropic, HumanLayer, the Ralph loop crowd and the Roo/Cline memory-bank pattern all converged on.

WHERE THE MONEY GOES. A child's bill is (a) the fixed prefix, (b) the research, (c) the work, (d) the hand-off reads. Measured today: the lobby's SessionStart hook injects 56 KB (about 14,000 tokens) into every session; AviationChat's project-context is 19 KB and its architecture shards 128 KB, so a child that "reads everything to be safe" spends 50-100k tokens before writing a line - and the naive design did that six times.

THE FIVE LAYERS.
0. Siblings share one prefix. Same worktree, model, tools, seat, skills; --exclude-dynamic-system-prompt-sections is MANDATORY (the vendor's page says the cache is scoped to one directory AND one git snapshot, and children commit, so without it every child after a commit misses); first child launched alone (parallel identical requests all pay full price - the entry is readable only after the first response starts streaming).
1. A grounding pack, researched once per story. One cheap child (the Gnat, Sonnet, low effort, read-only) writes context-pack.md: touched files with line anchors, symbols and contracts, where tests live and how they run, the rules from project-context.md that apply, blast radius, what the previous story learned. 5-8 KB. Every later child reads it FIRST, explores only what it lacks, appends what it learns. Vendor and community precedent: Anthropic's "structured note-taking" and 1,000-2,000-token sub-agent returns, HumanLayer's research->plan->implement files with file:line, Aider's repo map, Cline's memory bank.
2. Fork, don't restart, inside a lane. The build child is `claude -p --resume <plan-session> --fork-session`. Vendor, verbatim: "a fork inherits the parent's system prompt, tools, and conversation history exactly, so its first request reads the parent's cache." Consequence: a fork chain is ONE seat, one model, one effort - so the Cheshire Cat runs the dev door end to end (plan, then the build as a fork, then the fix as a fork); the White Rabbit does not run it (round 3 corrected). Even a cache MISS on a fork is one re-read of the transcript (about fifty cents for 100k tokens on Opus 4.8); redoing the research is many turns. The DeepSeek lane forfeits the fork (different endpoint, different cache) and pays layer 1 instead.
3. Independence only where the law buys it. Audit and review start fresh (SCC-362) but read the pack, plan, walkthrough and diff - distilled documents - not the tree. The review's five lenses cost what a human review costs today, bounded by the engine's own lens budget.
4. The lead holds summaries only. A child returns a few hundred tokens; the lead never opens a transcript; its own idle cache miss is small by construction.
5. Seat memory across stories: the shared _artifacts/_memory store (148 facts) plus the sub-agent `memory: project` slice per seat - long-term facts only, per the house rule.

"THEY STILL FOLLOW THE PROCESS, THEY JUST SWITCH PERSONAS." Exactly: the door is the process, the seat is who runs it, the pack is Step 0's grounding. One amendment to the doors, in their one body, never a fork: Step 0.6 gains "if a context-pack.md exists for this story, read it before exploring, and append what you learn". Humans get the same benefit.

CACHE FACTS THE DESIGN LEANS ON (vendor pages read today). Reads cost a tenth of base (a fortieth on Fable 5.1); writes 1.25x (5-minute) or 2x (1-hour); -p runs sit in the main bucket and get the ONE-HOUR cache on the subscription; forks and sub-agents get five minutes unless subagentPromptCacheTtl is set; proof of which bucket a child got is `claude -p "hello" --output-format json` -> usage.cache_creation. Skills and commands append as user messages (cache-safe); a model switch, an effort change on non-Fable models, an MCP server dropping, a bare-tool deny rule, or a Claude Code upgrade break the prefix.

THE ONE RISK THE LOOKUP FOUND. A measured case: ten identical calls with --system-prompt got ZERO cache reads (only the default prompt carries the cache marker). A seat delivered by --agent may behave the same way - undocumented. So S0 measures both deliveries on ten identical launches: --agent <seat> (preferred: skills preload, tools, memory) versus the same seat file passed as --append-system-prompt-file after the cached default prompt with --system-prompt-snapshot on. The one that reads wins.

FIRST-PARTY ALTERNATIVE, WEIGHED. Claude Code now ships "dynamic workflows" (a script orchestrating up to 16 sub-agents, results kept out of any context window, per-agent schema, built-in cache stagger and cost view, resumable, runs under -p, and its own rule is "no mid-run user input - run each stage as its own workflow", i.e. our lead-plus-escalation shape). The runner still wins for this lane on the two rows that carry the money and the law: the fork (workflows cannot inherit a transcript) and the review's real five-lens fan-out (a workflow agent cannot spawn sub-agents). Workflows are the right future home for the review engine itself - separate ticket.

RUNNER ADDITIONS. Every child's usage (input / cache_read / cache_write / output / cost) goes on the ticket's step comment plus a run total; "fresh session, demonstrated" gains "cache reuse, demonstrated" - S0 runs one small story naive and layered and both totals go on the ticket. Launch order first-alone. Fork chains homogeneous (the runner refuses a fork that changes seat, model or effort). The pack is a required step: no pack, no plan child.

ZOO. Roo/Zoo's subtask contract ("each subtask operates in complete isolation, it does not inherit the parent's context") means the Zoo variant needs the pack MORE than Claude, and has no fork. The house's active-context.md already is the Cline memory bank; the pack is its per-story slice, platform-neutral by construction.

NO NEW RULINGS from this round - it is engineering. The four rulings from round 3 stand.

## Comment 4 - Sudo Hatter

Brainstorm round 3c (2026-09-07, same Claude session) - THE ZOO REMOTE: phone to desktop, both directions. Answers "what are our options for mobile communication from my PC or Mac to my phone". Record: section 10 of _artifacts/_main/2026-09-07_scc-208-autopilot-v3-design/implementation_plan.md (every claim sourced there).

THE HEADLINE. The earlier assumption that Zoo has no way in was wrong. Zoo kept Roo Code's whole programmable surface (measured on the installed 3.83.100457 bundle and read in Zoo's source): an IPC Unix socket (enabled by the env var ROO_CODE_IPC_SOCKET_PATH) that accepts StartNewTask / ResumeTask / SendMessage and broadcasts every task event (Message with the ask type, TaskInteractive = needs you, TaskCompleted with token usage, TaskDelegated for the new_task hand-offs), plus an in-process extension API with approveCurrentAsk / pressPrimaryButton / pressSecondaryButton. Two facts decide the design: a text SendMessage ANSWERS a pending followup question (the March Hare asking you something) but on a pending tool ask it is "denied with feedback", so approvals need the in-process API, reachable only from a small companion VS Code extension. Roo's own "Roomote Control" died with Roo (2026-05-15) and Zoo cannot revive it (the bridge code is gone from Zoo's source).

CLAUDE'S SIDE IS ALREADY DONE. The vendor's page confirms Remote Control forwards the local session's permission prompts and questions to the phone and keeps them open until you answer (this closes the earlier unverified item). And Claude Code ships first-party CHANNELS (research preview): Telegram, Discord and iMessage plugins push messages into a running session and reply through it; the Telegram plugin declares the permission relay and sends Allow / Deny inline buttons (covers Bash, Write, Edit; not trust or MCP-consent dialogs; first answer wins). Setup is a BotFather token, /plugin install telegram@claude-plugins-official, launch with --channels, pair, then /telegram:access policy allowlist. Needs Bun. Not for -p runs (the lead is interactive, so fine). Desktop app also has Dispatch (message a task from the Claude app; Pro/Max).

THE OPTIONS FOR ZOO (full table in the record): Telegram bot bridge (text + buttons, iOS and Android, chat-id allow-list, no inbound port, free) · ntfy http actions on the existing poller (buttons on both phones; the iOS ntfy app CANNOT compose free text, an open bug leaves the notification uncleared after a tap, and a safe reply topic costs $6/month reserved or self-hosting) · companion VS Code extension (the only script-level Approve; must be installed in the WSL extension host on the PC and on the Mac) · VS Code Remote Tunnel in the phone browser (`code tunnel` run INSIDE WSL on the PC, the Windows toggle starts the wrong side; the real Zoo button; usability on a phone unverified) · Tailscale Serve + code serve-web · SSH + tmux (no good for a VS Code panel) · Happy Coder / ccgram / VibeTunnel (Claude-only; VibeTunnel has no Windows build) · Pushover / Pushcut / Home Assistant (nothing the others lack).

RECOMMENDATION: ONE PHONE APP FOR BOTH PLATFORMS, TELEGRAM. The inbound half must be authenticated (a public ntfy topic is a prompt-injection path into an agent holding your credentials), must take free text on whatever phone you hold, and must carry buttons; a Telegram bot with a chat-id allow-list does all three for free from WSL and Mac. Claude already has the first-party Telegram channel with Allow/Deny, so the same app serves the lead. ntfy keeps outbound pings or retires.

The Zoo remote in four pieces: (1) EVENTS NOT POLLING - the bridge subscribes to Zoo's IPC socket; TaskInteractive = needs you, TaskCompleted = turn complete; the thread-store poller retires once proven (its format is internal to Zoo). (2) THE BOT - zoo_bridge.py, stdlib, Telegram Bot API by long polling, chat-id allow-list, refuses StartNewTask from the phone; a text reply goes in as SendMessage and answers the March Hare's followup question IN the conversation (so the March Hare's escalations are written as ask_followup_question); Approve/Reject taps go to the companion; every escalation is mirrored to the ticket as the "Needs Mr. Hatter" comment. (3) THE COMPANION - a fifty-line VS Code extension exposing Zoo's approve/reject on a local socket, packaged as a .vsix, installed on the Mac and in the PC's WSL extension host. (4) THE TUNNEL - code tunnel set up once per machine as the fallback for dialogs no bridge relays and for looking at the panel.

For the Claude lead: Remote Control stays the baseline (on at startup, zero cost); the Telegram channel is the optional unification, about an hour of setup, reversible, a research preview whose flag syntax may change. Recommend adding it after the Zoo bot exists, so the phone ends with one app and two bots rather than two apps.

THE TRADEOFF THAT IS YOURS: one app (Telegram, two bots, one of them a preview feature) versus two apps (the Claude app for Claude, ntfy for Zoo with buttons only on iOS).

RULINGS (replacing ruling 4 of round 3): 4) Zoo inbound: Telegram bot bridge (recommended) or ntfy actions. 5) Zoo approve path: companion extension with the tunnel as fallback (recommended), or the tunnel alone. 6) Claude lead: Remote Control as is, or add the Telegram channel for one app.

ASK-FIRST PREREQUISITES: a Telegram bot token under keyway-secrets; ROO_CODE_IPC_SOCKET_PATH exported where each extension host inherits it (WSL login shell - whether the VS Code server inherits ~/.profile is the subtask's first measurement; Mac launch environment); installing a local .vsix on both machines; Bun only if the Claude channel is added.

PROOF FOR THE SUBTASK: one followup question answered by text from the phone and visible in the Zoo conversation; one tool ask approved by a tap; both mirrored on the ticket; the poller off for a day with nothing missed.

ONE MORE LEVER FOUND: Zoo ships a headless `roo` CLI (a standalone agent through a VS Code shim, --print, NDJSON prompt streams, macOS and Linux builds). Not a remote (it does not attach to a running VS Code) but it is Zoo's `claude -p`, and it changes what the Zoo AUTOPILOT variant (S8) can be.

## Comment 5 - Sudo Hatter

Brainstorm round 3d (2026-09-07, same Claude session) - RULINGS RECEIVED + THE DRIFT CHECK. Record: section 11 of _artifacts/_main/2026-09-07_scc-208-autopilot-v3-design/implementation_plan.md (section 7 updated, S2 amended).

RULED (operator, his words): "Claude already has remote, we don't need anything more than that. Zoo is the one I am interested in making work remote and we would have to build that. I also have an iOS phone." That closes rulings 2 and 6 (the Claude lead stays on Remote Control, no Telegram channel for Claude) and ruling 4 (iOS: the Zoo inbound half is the Telegram bot bridge, because the ntfy iOS app cannot type a reply). The phone carries two apps: the Claude app for Claude, Telegram for Zoo. Still open: 1 (the charter rows), 3 (delete the AP twins and the opencode launcher, banner the engines), 5 (the Zoo approve path: companion extension with the tunnel as fallback, recommended, or the tunnel alone).

THE DRIFT REQUIREMENT, his words: "I want this to scale on top of the development workflow we use, not be something stand alone. When we make edits to the workflows and the / commands and the rules it auto-updates because it's using the same ones. I don't want to worry about drift."

THE ANSWER IS YES, BY CONSTRUCTION. The house already works that way and the autopilot adds no copy of anything. Verified on the tree this session:
- DOORS. .claude/commands is a RETIRED door (the sync writes nothing there). Claude enters a / command through a generated launcher skill (.claude/skills/<name>/SKILL.md) whose whole body is "read .agents/commands/<name>.md and follow it END TO END"; Zoo's .roo/commands/<name>.md is the same pointer. The master is loaded at invocation, so an edited door is live on the next launch with NO sync; a sync is needed only to add, rename or retire a door (its launcher), and the sync manifest + -Status police that. The runner passes the door's NAME to the child (the way the operator types it), never its text.
- SEATS. .roomodes is GENERATED and each roleDefinition is itself a pointer ("Read .agents/commands/smh-team-march-hare.md and follow it END TO END"); test_zoo_team.py compares GENERATED against MASTER on every suite run. The Claude seat gets the same shape with even less on disk: the runner reads the seat master at every launch and hands the child a session-only definition through --agents <json> (sub-agents docs: "exist only for that session and aren't saved to disk", and they outrank any .claude/agents/ file). So .claude/agents/<seat>.md is NEVER written. This withdraws round 3's "second projection" and amends S2 to a renderer plus its parity test (rendered JSON against master frontmatter, never a table typed into the test).
- RULES. They reach a headless child by the same three live paths the chat uses: CLAUDE.md's @ imports of the floor rules, .claude/rules/, and the rule-trigger.py UserPromptSubmit hook that matches every prompt against the rules' triggers (plus the SessionStart hook's active-context and repo map). A -p child runs every hook the chat runs, so the design FORBIDS --bare on any child: it skips hooks, and the hooks are how the law arrives.
- SKILLS. A seat's skills: list preloads the FULL skill content at launch, read from the file at that moment; only the list per seat lives in the master's frontmatter (a claude-skills: key beside the existing mode-groups:). Editing a skill body is live at the next launch.
- THE CHARTER (what the lead may pass without him): the body of the rewritten cicd-autopilot-claude.md door, under the same sop-currency gate as every door. The runner never reads it; the lead does, the way it reads any door.
- THE ORDER OF THE STEPS: the runner has NO list of doors. It is called once per step with a door name, a seat, a budget and a cwd. That is the exact difference from the retired .ps1 engines, which hard-coded the stages in 2,052 lines and drifted the day the doors changed.

WHAT THE RUNNER OWNS (so the drift surface is bounded): the launch flag set, the result schema, the jira_feed.py step verb, the seat renderer, and the budget table. None of it is workflow content. A workflow change touches nothing in the runner; a Claude CLI change touches only the runner.

THE RULE THE BUILD KEEPS, WITH ITS TEST (S1): the runner may not contain the text of any door, rule or seat. A grep of autopilot_run.py for any heading or sentence that also appears in .agents/commands/ or .agents/rules/ fails the suite. The Zoo variant (S8) inherits all of this unchanged, because .roomodes and .roo/commands/ already are pointers.

ONE NEW S0 MEASUREMENT: --agent <seat> resolving a seat defined by --agents <json> on the same launch line (the docs state each half; S0 measures the pair). Fallback: --append-system-prompt-file carrying the same pointer sentence, still nothing on disk for a sync to keep current.

NEXT: rulings 1, 3 and 5, then /smh-plan-task SCC-208 (mints the Zoo remote subtask with the rest). Nothing built.

