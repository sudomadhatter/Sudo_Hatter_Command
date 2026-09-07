---
IsArtifact: true
ArtifactMetadata:
  title: SCC-431 - Autopilot v3, the Zoo half (phone remote, then the Zoo variant)
  type: implementation_plan
  date: 2026-09-07
---

# Implementation Plan - SCC-431: Autopilot v3, the Zoo half

**Parent:** SCC-429 (Task). **The design** this lane builds is
`_artifacts/_main/2026-09-07_autopilot-v3-design/implementation_plan.md` sections 10 (the remote) and 2.6 (the
variant) - attached to SCC-429 and carried to `main` on the SCC-430 lane, so it is not on this branch until that
lane lands; the ticket attachment is the durable copy meanwhile.
**Lane:** `chore/SCC-431-zoo-remote` in `.claude/worktrees/scc-431-zoo-remote`, base `origin/main` @ `d70347ba`.
**Mode:** per-subtask lane; runs AFTER SCC-430 (the operator's order, and the `step` verb it imports).

## Goal

Give Zoo Code a two-way phone remote on the operator's iPhone - Zoo's own IPC socket for events and text replies, a
Telegram bot with an allow-list as the authenticated inbound, a fifty-line companion extension for Approve/Reject,
`code tunnel` as the fallback - prove it from the phone, then make the Zoo variant of the autopilot on the
March Hare seat.

Glossary: the **IPC socket** is the Unix socket Zoo opens when `ROO_CODE_IPC_SOCKET_PATH` is set, on which it
broadcasts every task event and accepts a `SendMessage`; a **followup ask** is Zoo's `ask_followup_question`
prompt, the one a text message answers; a **tool ask** is an approval prompt, which a text message REJECTS with
feedback - only the in-process API approves it; the **companion** is the small VS Code extension that exposes that
API on a local socket; the **bridge** is `zoo_bridge.py`, the process that joins the socket, the companion and
Telegram.

## Acceptance - the ticket's checklist, one row each (proof named per row)

| Row | Statement (checkable) | Proved by |
|---|---|---|
| **A** | Measured on both machines: which contexts inherit `ROO_CODE_IPC_SOCKET_PATH` (the WSL VS Code server, the Mac's extension host); the installed 3.83 bundle's **wire values** match the design's event list | `measurements.md` here: the probe's output per context on each machine, and the enum diff taken against the wire strings (`taskInteractive`, `taskCompleted`, …), not the minified member names |
| **B** | Events, not polling: the bridge subscribes to the socket and maps `taskInteractive` → "needs you", `taskCompleted` → "turn done", `message` → the ask text and type; **the installed service no longer runs `zoo_notify.py --watch`** | `test_zoo_bridge.py: test_events_map_to_notifications` on captured frames; row F's installer test asserts the service line names the bridge, not `--watch` |
| **C** | `zoo_bridge.py` (stdlib): Telegram long polling, chat-id allow-list, refuses `StartNewTask` from the phone, a text reply goes in as `SendMessage`, a text on a tool ask is refused rather than sent, every escalation mirrored to the ticket; the token reaches the process through the environment only and never touches disk | `test_allowlist_refuses_unknown_chat`, `test_start_new_task_refused`, `test_text_reply_becomes_send_message`, `test_text_on_tool_ask_is_refused_not_sent`, `test_escalation_mirrors_to_ticket`, `test_token_never_in_argv_or_log`, `test_no_listening_tcp_socket`, `test_service_line_carries_no_token` |
| **D** | The companion (`extension.js` + `package.json` + `README.md`) exposes approve / reject on a local socket, declares `extensionKind: ["workspace"]`, is packaged by a stdlib script, and is installed on the Mac and in the PC's WSL extension host; `code tunnel` reachable from the phone | `test_build_vsix_layout` (the zip carries `extension.vsixmanifest`, `[Content_Types].xml`, `extension/package.json`); `code --list-extensions` on both machines showing the id; one tunnel URL opened from the phone (the operator's screenshot); the README is what the card's install row points at |
| **E** | Proof from the iPhone: one followup answered by text and visible in the Zoo conversation; one tool ask approved by a tap; both mirrored on the ticket; the poller off for a day with nothing missed | `walkthrough.md` with the four items, the operator's screenshots, and the ticket comments they produced |
| **F** | The per-machine setup is a card: the socket variable, the token, the `.vsix`, the VS Code CLI, the tunnel; both sides of the PC named; `zoo_notify_install.py` installs the bridge **into WSL on the PC** | `docs/migrations/install_guides/zoo-remote-setup.md` exists and every command on it was pasted into a shell on that side; `test_zoo_notify_install.py` asserts the Windows Startup `.cmd` launches through `wsl.exe` and the plist/`.cmd` carry no token |
| **G** | The Zoo variant: the March Hare master gains the escalation contract and the `step` verb; the team rule names the phone path and the regenerated Zoo copies land with it; one real story driven from the Zoo seat; Zoo's headless `roo` CLI weighed | the masters' and rules' diff including `.roo/rules/zoo-team.md`; `test_zoo_team.py` green; the story ticket's thread; `roo-cli.md` here with the measured command surface and the call (build / defer) |

## ⚠️ AUDIT FINDINGS baked in (self-audit 2026-09-07, this file's `## Self-Audit` section)

The first draft's blocker and the seven important findings are resolved in the steps below. The four that change
what gets built, stated once here because they are easy to lose in a step:

1. **The PC's service must run inside WSL.** `zoo_notify_install.py:115` writes
   `start "" /min pythonw "<repo>\.agents\scripts\zoo_notify.py" --watch` - a **Windows-side** process. The socket is
   a Unix socket inside the WSL2 distro (the extension host that runs Zoo lives there), and a Windows process cannot
   connect to it. The Startup `.cmd` must launch `wsl.exe` instead, or row F's service starts and never subscribes
   while its dry-run proof passes anyway.
2. **Keyway cannot be read by a script.** Its verbs are `pull / run / set / diff / scan / doctor` - there is no
   `get`. The house's no-disk path is `keyway run -e <env> -- <cmd>`, so keyway is the **launcher**, not a call the
   bridge makes. The bridge reads `TELEGRAM_BOT_TOKEN` from its environment and nothing else.
3. **`--poll` does not exist and the observable was a tautology.** `zoo_notify.py:450` already gates the poller
   behind `--watch`, which is opt-in. Row B's real observable is that the installed service stops naming it.
4. **The tunnel has no binary in WSL.** `which code` inside the distro resolves to the VS Code server's remote-cli
   shim, whose `--help` has no `tunnel`; `/usr/local/bin/code` execs the Windows desktop launcher, which would tunnel
   the wrong host. The card and Ask-First 4 now carry "install the standalone VS Code CLI in the distro".

## Decisions carried from the design and the operator's rulings

- **Telegram, ruled.** His phone is iOS; the ntfy iOS app cannot type a reply, so ntfy is out for the inbound half.
  Claude stays on Remote Control and gets nothing (ruled 2026-09-07) - this lane touches nothing on the Claude side.
- **Ruling 5 open:** the companion extension with the tunnel as fallback is the recommendation; the tunnel alone is
  the alternative. Step 4 is written for the recommendation; if he rules the other way, Step 4 shrinks to the card row.
- The bridge **refuses `StartNewTask`** from the phone; the phone answers and approves, it never starts work.
- **A public ntfy topic is never an inbound** - a prompt-injection path into an agent holding credentials
  (design 10.2's security paragraph). The allow-list is by Telegram chat id, and the bot ignores everything else.
- The March Hare writes its escalations as **followup asks**, so the phone's text lands IN the conversation; each
  one is mirrored to the ticket through `jira_feed.py step --status needs_human` (SCC-430's verb) as the durable record.
- Stdlib only, both sides; the companion is plain JavaScript with no build step; the `.vsix` is a zip written by a
  Python script.

## Port check (the rule fired; this is the section it demands)

Measured with `git diff --no-index`. `Projects/sudo-command-center/.agents/` carries `zoo_notify.py` (differs, 110
lines), `zoo_notify_install.py` (differs, 32), `rules/zoo-team.md` (differs, 12) and `commands/smh-team-march-hare.md`
(identical). **Disposition: out of scope.** `docs/workspace-standard.md:253-260` states that submodule is *"the
published teaching edition of this lobby - a sanitized export, never edited in place"*, regenerated by
`export-teaching-edition.ps1` from the `claude/teaching-edition` branch and *"no - it is a mirror"* in the audited
column; its diffs are the sanitizer's (`SCC-` → `HISTORY-`, `com.sudohatter` → `com.your-local-user`). Nothing to
port; the next export carries this lane.

**One real port obligation, and it is another repo's ticket.** `Projects/AGY_AVIATIONCHAT/.roo/rules/zoo-team.md`
is **tracked in the AGY repo** (landed by `557b081b`, AVCH-114) and is byte-identical to the lobby's copy today.
Row G edits the lobby master, so the AGY copy silently diverges and a Zoo seat opened inside AviationChat keeps a
rule with no phone path. The lobby's sync only writes the lobby's `.roo` (`sync-agents.ps1:665`; projects stay
thin), so nothing closes this automatically. Per check 6, the port needs that repo's own key: **an AVCH ticket
re-ports `.roo/rules/zoo-team.md` after this lane lands.** Raising it is part of row G's close-out, not a
silent leftover.

## Steps (one per acceptance row; each names the assertion that proves it)

### Step 1 - Measure first (row A)

`zoo_bridge.py probe`: prints whether `ROO_CODE_IPC_SOCKET_PATH` is set in this process, whether the socket file
exists, connects, and prints the first frames (the `Ack`, then events) with their JSON shapes. Run it three ways on
the PC (a WSL login shell; a VS Code terminal inside the WSL server; the Windows side, with `python`) and once on
the Mac (a terminal spawned by VS Code).

⚠️ **Diff the WIRE VALUES, not the member names.** The bundle minifies the enum to
`a[a.TaskInteractive="taskInteractive"]="TaskInteractive"`, so a search for `TaskToolFailed` returns zero while
`taskToolFailed` returns six. Compare `taskInteractive`, `taskCompleted`, `taskAborted`, `taskToolFailed`,
`taskIdle`, `taskAskResponded`, `StartNewTask`, `SendMessage`, `"Ack"` against design 10.2.

**Proof:** `measurements.md` carries the probe output per context and the enum diff. If the VS Code server does
not inherit the variable from `~/.profile`, the card (Step 6) puts it on the launch line instead - recorded here.

### Step 2 - Events, not polling (row B)

`zoo_bridge.py watch`: connect to the socket, keep the connection, and turn events into notifications:
`taskInteractive` → push "needs you" with the ask text, `taskCompleted` → "turn done" with token usage,
`message` carrying an ask → the ask type and text kept as the pending item, `taskAborted` / `taskToolFailed` →
"failed".

**`zoo_notify.py` is left alone.** Its poller is already opt-in behind `--watch` (`:450`), it owns `classify()` and
`DEFAULT_TOPIC` which two other modules import, and 46 cases pin it. Retiring the poller means the **installer stops
writing `--watch`** (Step 6), not a new flag here.

**Proof:** `test_events_map_to_notifications` replays frames captured in Step 1 through a fake socket server and
asserts the notification per event; the poller's retirement is row F's assertion.

### Step 3 - The bot (row C)

`zoo_bridge.py serve`: one process, two loops. Outbound: each notification from Step 2 becomes a Telegram message
to the allow-listed chat, with inline buttons **Approve** / **Reject** when the pending item is a tool ask.
Inbound (long polling `getUpdates`): a message from a chat id not on the allow-list is dropped and counted; a text
reply while a followup ask is pending goes in as `SendMessage` (answers it in the conversation); a text reply while
a **tool** ask is pending is refused with a one-line reply ("that is an approval - tap Approve or Reject"), because
a text on a tool ask is a rejection with feedback in Zoo's code; a tap goes to the companion (Step 4); any command
that would create work (`/new`, `StartNewTask`) is refused. Every pending ask is mirrored to the ticket as
`Needs Mr. Hatter` through `jira_feed.py step --status needs_human` when a ticket key is known (from the task's
first message or a `--key` flag), else skipped and logged.

**The token.** `TELEGRAM_BOT_TOKEN` from the environment, or exit 5 printing the one-time setup - the shape of
`jira_ticket.py:34`, minus the middle tier, because keyway has no readable verb (finding 2). The token reaches the
environment because the service is launched under `keyway run -e <env> -- …` (Step 6). It goes into the request
header and nowhere else; argv and every log line are scrubbed.

⚠️ **Keep the `step` argv in one constant** - SCC-430 writes that verb, and this lane's test pins its shape; one
constant makes the rebase one line.

**Proof:** `test_allowlist_refuses_unknown_chat`, `test_start_new_task_refused`, `test_text_reply_becomes_send_message`,
`test_text_on_tool_ask_is_refused_not_sent`, `test_escalation_mirrors_to_ticket` (fake acli), `test_token_never_in_argv_or_log`,
`test_no_listening_tcp_socket` (`serve` binds nothing on TCP; Telegram is polled outward, the other two sockets are
local Unix sockets).

### Step 4 - The companion and the tunnel (row D) - ruling 5

`.agents/zoo-companion/`: `package.json` (activation on startup, no contributed UI, **`"extensionKind": ["workspace"]`**
- Zoo is workspace-kind and its `exports` are only visible from the same server-side host under Remote-WSL),
`extension.js` (about fifty lines: on activate, get
`vscode.extensions.getExtension("zoocodeorganization.zoo-code").exports`, open a Unix socket at
`$ZOO_COMPANION_SOCKET` (default beside the IPC socket), accept `{"op": "approve"|"reject"|"primary"|"secondary"}`,
call `approveCurrentAsk()` / `pressSecondaryButton()` / `pressPrimaryButton()`, reply with `isReady()` and the
result - all four names verified present in the installed 3.83 bundle), `README.md` (what it is, how it is built and
installed; the card's install row points here). `build_vsix.py` (stdlib `zipfile`) writes
`zoo-companion-<version>.vsix` **into this artifact folder**, not the repo root, so no untracked binary sits in
`git status`. Install is the operator's hand on each machine:
`code --install-extension <path>.vsix` - in WSL, the extension host that runs Zoo; on the Mac, the desktop.

**The tunnel needs a binary first.** Inside the distro `code` is the server's remote-cli shim with no `tunnel`
subcommand, and `/usr/local/bin/code` execs the Windows desktop launcher (wrong host). The card's tunnel row starts
with installing the standalone VS Code CLI in Ubuntu, then `code tunnel` there and on the Mac, signed in with the
same account.

**Proof:** `test_build_vsix_layout` opens the built zip and asserts the three required entries; the operator's
`code --list-extensions` output on both machines in `walkthrough.md`; one tunnel URL opened from the phone. The
`.vsix` layout is taken from the manifest of the installed Zoo extension - VS Code strips `[Content_Types].xml` and
flattens `extension/` on install, so the zip shape is proven by the test and its acceptance by the first successful
`--install-extension`.

### Step 5 - Proof from the iPhone (row E)

With the bridge running on the PC: a March Hare task that asks a followup question - answered by text from the
phone, the answer visible in the Zoo conversation; a task that raises a tool ask - approved by a tap; both mirrored
on the ticket; the poller left off for a day, and the day's notifications compared against the thread store
(`zoo_notify.py:120`, the `globalStorage/zoocodeorganization.zoo-code/tasks` tree).

**Proof:** the four items in `walkthrough.md` with the operator's screenshots and the ticket comment links. These
are operator observations, not tests, and are labelled as such.

### Step 6 - The setup card and the installer (row F)

`docs/migrations/install_guides/zoo-remote-setup.md`: create the bot (BotFather), `keyway set` the token, the
chat-id allow-list, `ROO_CODE_IPC_SOCKET_PATH` per context (from Step 1's measurement), install the standalone VS
Code CLI in WSL, install the `.vsix` on both machines, sign in the tunnel, start the bridge; every command pasted
into a shell on that side before it is written; both sides of the PC named. One row on `machine_setup_card.md`.

`zoo_notify_install.py` installs the **bridge**: on the Mac a launchd agent whose `ProgramArguments` are
`<abs keyway> run -e <env> -- python3 <repo>/.agents/scripts/zoo_bridge.py serve` (launchd's PATH is
`/usr/bin:/bin:/usr/sbin:/sbin` and nothing else, so keyway is absolute and `-e` is mandatory or it blocks on a
keypress); on the PC a Startup `.cmd` that runs `wsl.exe` into the distro and launches the same line there
(finding 1). ⚠️ `apply()` refuses a `--repo` inside `.claude/worktrees/` (`:181-188`), so the dry run is pointed at
the main checkout.

**Proof:** the card exists and reads in present tense; `test_zoo_notify_install.py` (which today asserts `--watch`,
`zoo_notify.py` and `pythonw` at `:87-90` and `:284-286`) is updated to assert the bridge, `wsl.exe` in the `.cmd`,
and that neither service file contains the token.

### Step 7 - The Zoo variant (row G) - after SCC-430 lands

`smh-team-march-hare.md`: an "Escalation contract" section - escalations are `ask_followup_question` (so the phone
answers them), each mirrored with `jira_feed.py step --status needs_human`; every delegated step posts `step` on
completion. ⚠️ The section must not put a modal grant (`may` / `can` / `should`) near the word `Verdict:` -
`test_zoo_team.py` B5 scans every master's body for exactly that.

`.agents/rules/zoo-team.md`'s delegation-plumbing paragraph names the bridge as the phone path. ⚠️ **That rule has a
tracked, generated twin**: `.roo/rules/zoo-team.md` carries `<!-- GENERATED by sync-agents … -->` and Zoo injects
every file in `.roo/rules/` into every seat's prompt. Run `/smh-sync-agents` and commit the regenerated copy and the
rewritten `.agents/.sync-manifest.json` with it, or no Zoo seat ever reads the change.

One real story driven from the March Hare seat with the bridge on. `roo-cli.md` here: the headless `roo` CLI's
measured command surface (`--print`, the NDJSON prompt stream, platform builds) and the call on whether the Zoo
variant should run children through it the way the Claude half runs `claude -p` - a note and a recommendation, no
build in this lane. And the AVCH ticket from `## Port check` is raised here.

**Proof:** the masters' and rules' diff including the regenerated `.roo` copy; `test_zoo_team.py` green; the story
ticket's comment thread; `roo-cli.md` with the measured surface.

## Declared Change Set

- NEW `.agents/scripts/zoo_bridge.py` — probe, watch and serve: the IPC subscriber, the Telegram bot, the companion client → B
- NEW `.agents/scripts/tests/test_zoo_bridge.py` — events mapping, allow-list, StartNewTask refusal, text-on-tool-ask refusal, ticket mirror, token hygiene, no TCP listener → C
- NEW `.agents/zoo-companion/package.json` — the companion manifest, extensionKind workspace → D
- NEW `.agents/zoo-companion/extension.js` — approve / reject over a local socket via Zoo's exports → D
- NEW `.agents/zoo-companion/README.md` — what it is, how it is built and installed; the card's install row points here → D
- NEW `.agents/zoo-companion/INDEX.md` — every level-2 folder under `.agents/` requires one (check_maps 2.5) → F
- NEW `.agents/scripts/build_vsix.py` — stdlib zip of the companion into a `.vsix`, written into the artifact folder → D
- NEW `.agents/scripts/tests/test_build_vsix.py` — the zip layout VS Code requires → D
- NEW `docs/migrations/install_guides/zoo-remote-setup.md` — the per-machine card → F
- NEW `_artifacts/_main/2026-09-07_scc-431-zoo-remote/measurements.md` — the probe output per context and the wire-value enum diff → A
- NEW `_artifacts/_main/2026-09-07_scc-431-zoo-remote/walkthrough.md` — the RED/GREEN captures and the phone proof → E
- NEW `_artifacts/_main/2026-09-07_scc-431-zoo-remote/roo-cli.md` — the headless `roo` CLI weighed → G
- EDIT `.agents/scripts/zoo_notify_install.py` — installs the bridge, through `wsl.exe` on the PC and `keyway run -e` on both → F
- EDIT `.agents/scripts/tests/test_zoo_notify_install.py` — the service is the bridge, launched into WSL, carrying no token → F
- EDIT `docs/migrations/install_guides/machine_setup_card.md` — one row for the Zoo remote → F
- EDIT `.agents/commands/smh-team-march-hare.md` — the escalation contract and the `step` verb → G
- EDIT `.agents/rules/zoo-team.md` — the delegation-plumbing paragraph names the phone path → G
- EDIT `.roo/rules/zoo-team.md` — the tracked generated copy Zoo actually reads, regenerated by the sync → G
- EDIT `.agents/.sync-manifest.json` — rewritten by that sync run → G
- EDIT `.agents/INDEX.md` — the inventory row for `zoo-companion/` → F
- EDIT `.agents/scripts/INDEX.md` — rows for the bridge and the vsix builder → B
- EDIT `_artifacts/_main/INDEX.md` — this lane folder's row → A
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the Zoo remote as a usage surface, present tense → G
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one line → G

## Verification plan

- Per part: the part's test file RED (fake socket / fake Telegram endpoint / fake acli) then GREEN, captured in
  `walkthrough.md`; per guard, revert the guarded line and name the case that goes red. Rows A, E and the operator
  halves of D and G are observations, not tests, and say so.
- Lane tip, once, sandboxed: `python3 .agents/scripts/gate_receipt.py`.
- ⚠️ **`sop_currency.py` is armed and fires per commit**: `.agents/scripts/*.py`, `.agents/commands/*.md` and
  `.agents/rules/*.md` are surfaces (tests and `INDEX.md` are exempt). Steps 1-3, 4 (`build_vsix.py`), 6 and 7 each
  need the SOP staged in that commit or `[sop-ok]` in the message. `.agents/zoo-companion/*` and `.roo/*` are not
  surfaces. The plan-only commit that grounds this lane touches only `_artifacts/`, which is not a surface, so it needs no marker.
- Both sides: `python3` in WSL and on the Mac, `python` for the Windows-side probe run, `wsl.exe` for the PC service;
  no venv, no npm.
- No deployable path is touched.

## Ask-First items (the operator's word, before the step that needs it)

1. **Ruling 5** (companion + tunnel, or tunnel alone) - before Step 4.
2. **The bot token**: he creates the bot with BotFather and `keyway set`s it; the token is never in git, chat, argv,
   or a service file - before Step 3's live test.
3. **`ROO_CODE_IPC_SOCKET_PATH`** exported on each machine (an environment config edit, his hand, per the card) -
   before Step 1's second run.
4. **Installing the standalone VS Code CLI in WSL, installing the `.vsix` on both machines, and signing in
   `code tunnel`** - his hands, before Step 5. The CLI install is a dependency install.
5. **Which story** for Step 7's live run.

## Not in this lane

Anything on the Claude side (Remote Control stays as is). The `roo` CLI as a build (weighed only). The runner and
the `step` verb (SCC-430; this lane consumes `step`, it does not write it). The teaching-edition mirror, and the
AviationChat copy of the team rule, which gets its own AVCH ticket (`## Port check`).

## Landing order with SCC-430

This lane **imports** `jira_feed.py step` from SCC-430 (Steps 3 and 7) and shares four paths with it:
`.agents/commands/smh-team-march-hare.md` (SCC-430: the frontmatter; here: the body - clean hunk split),
`.agents/scripts/INDEX.md`, `_artifacts/_main/INDEX.md`, `.agents/.sync-manifest.json` (both lanes run the sync,
so the manifest conflicts by construction and is resolved by re-running the sync on the rebased tip, never by hand),
plus the SOP and its changelog. SCC-430 lands first (the operator's order); this lane rebases those hunks.
Steps 1 to 6 (the remote) have no dependency on SCC-430 except the ticket mirror, which degrades to "skipped and
logged" until `step` exists - so the remote can be built and proven beside SCC-430 if the operator wants it sooner.

## Self-Audit (2026-09-07)

**Level: LEDGER+BLAST** (the change set touches a rule with a generated twin, a seat master, scripts others import,
a new folder under `.agents/`, and the operator's install guides). **Mode: PRE-WORK.** Lenses 1 and 2 ran blind to
each other in isolated read-only agents; Lens 3 ran after them over their survivors. **Every finding below was
raised against the first draft and is resolved in the plan above** - the blocker by declaring the missing edit, the
four behaviour-changing ones by rewriting the steps they broke.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  existence of every path/command/script/rule/flag/tool the plan names (zoo_notify.py's poller and store
             path, zoo_notify_install.py's platform arms and dry run, its test's 30 cases, keyway --help, code --help
             and the WSL shim, the Zoo extension ids on both hosts, the bundle's enum strings, jira_ticket.py's token
             shape, zoo-team.md's delegation paragraph, gate_receipt.py, check_maps 2.5 and 7, record_map_changes,
             sync-agents.ps1's enumerations); declared_change_set.py parse; both-sides command fit; lane fit;
             the Scope Ledger (observables A-G, NEW x row, caller counts); tests-must-gate-for-real; step references
read:        the plan; the design record §2.6, §10.2, §10.4-10.5; zoo_notify.py; zoo_notify_install.py;
             test_zoo_notify_install.py; test_zoo_notify.py; run_all.py; jira_ticket.py; jira_feed.py (grep for step);
             zoo-team.md:74-84; smh-team-march-hare.md; .agents/INDEX.md and every level-2 INDEX.md; check_maps.py;
             record_map_changes.py; sync-agents.ps1; task_preflight.py:1576-1595; smh-close-task-merge-tree.md:244;
             machine_setup_card.md; keyway-setup.md; the installed Zoo extension's .vsixmanifest and dist/extension.js;
             which python python3 pythonw code keyway; code --help; code tunnel --help; /usr/local/bin/code
verdict:     findings below
```

```
lens:        2 Parity + Blast
checks_run:  zoo-team.md's citing commands and _RULE_POINTERS; .roo tracking (git ls-files) and what the sync
             regenerates; the march-hare master's generated surfaces and test_zoo_team's comparison; zoo_notify*
             callers, tests and INDEX rows; the new .agents/ folder against check_maps and the sync; SOP-ENFORCE
             armed and which steps trip it; the port rule (find + diff across Projects, AGY's tracked copy and its
             last commit); twins; secrets (keyway's verbs, jira_ticket's resolution, .gitignore, hook scanning);
             sibling worktrees and SCC-430's declared set; risk_seam classify; the installer's platform arms
read:        both lane plans; workflow_lint.py:70-143; sync-agents.ps1 (31-47, 129, 221-416, 511, 581, 639-946,
             1228-1262); smh-sync-agents.md; test_zoo_team.py; .roo/commands/smh-team-march-hare.md;
             .roo/rules-orchestrator/01-persona.md; .roomodes:4-12; .roo/rules/zoo-team.md:1; zoo_notify.py and its
             two tests; .agents/scripts/INDEX.md:32-40; .agents/INDEX.md; check_maps.py; refresh_maps.py;
             .githooks/{commit-msg,pre-commit}; the git-hooks dir; sop_currency.py:1-140; port-checklist.md;
             workspace-standard.md:253-260; declared_change_set.py; smh-code-review.md:275;
             sharing_keys_secrets_secure.md; keyway-setup.md; jira_ticket.py:34,64-79,256-287; .gitignore;
             Projects/sudo-command-center (4 diffs); Projects/AGY_AVIATIONCHAT/.roo/rules/zoo-team.md
verdict:     findings below
```

```
lens:        3 Pre-Mortem (bounded: attaches narratives, originates nothing)
checks_run:  for each surviving anchored finding, the silent-failure / other-machine / fresh-clone /
             sibling-lands-first narrative
read:        the survivors of lenses 1 and 2 only
verdict:     three narratives attached (below the table); no unattached output
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/scripts/task_preflight.py:1585,1591` + `check_maps.py:501` + `smh-close-task-merge-tree.md:244` | `plan.append("python3 .agents/scripts/check_maps.py --depth3-only --strict")` … `"--strict" is what makes it a gate at all`; `problems.append(f"{rel_bucket}/INDEX.md: missing row for \`{s}/\`")` | this lane's folder is on disk with no ledger row, so the close-out gate refuses; the sibling lanes SCC-411 and SCC-418 both declare that edit and this plan did not | **blocker - resolved**: `EDIT _artifacts/_main/INDEX.md` declared |
| `.agents/scripts/zoo_notify_install.py:115,19-20` + design §10.2 | `start "" /min pythonw "…zoo_notify.py" --watch`; `PC -> a .cmd in the Startup folder run through pythonw`; the design puts the extension host and the socket inside WSL | a Windows process cannot connect to a Unix socket inside the WSL2 distro, so the installed service would start and never subscribe - while the dry-run proof passed anyway | important - resolved: Step 6 launches through `wsl.exe`, and the test asserts it |
| `keyway --help` + `keyway-setup.md:104-128` + `jira_ticket.py:34,256` | verbs are `pull / run / set / diff / scan / doctor` - no read verb; `keyway run` injects secrets **into memory only**; without `-e` it "blocks until a key is pressed"; jira_ticket's middle tier is the **OS store**, not keyway | the plan's "env → keyway → exit 5" had no call a script could make, and a launchd plist inherits no shell environment, so the token would have ended up written into a service file | important - resolved: env-only inside the bridge; `keyway run -e <env> --` is the launcher, keyway absolute; a test asserts no service file carries the token |
| `which code` + `code --help` + `/usr/local/bin/code` | the WSL `code` is the server's remote-cli shim (`grep -c tunnel` = 0); `/usr/local/bin/code` is `exec "/mnt/c/Microsoft VS Code/bin/code"` - the Windows desktop, the wrong host | row D's tunnel item had no binary able to run it inside the distro, and the dependency was in neither the card nor Ask-First | important - resolved: installing the standalone VS Code CLI is a card row and part of Ask-First 4 |
| `.agents/scripts/tests/test_zoo_notify_install.py:87-90,284-286` | `assert "--watch" in args`; `assert script.parts[-3:] == (".agents", "scripts", "zoo_notify.py")`; `assert "pythonw" in body` | Step 6 turns at least four of that file's 30 cases red, and the file - which row F names as its own proof - was not declared | important - resolved: declared, and row F's proof is stated as the updated assertions |
| `.roo/rules/zoo-team.md:1` + `sync-agents.ps1:722,129` + `git ls-files .roo` | `<!-- GENERATED by sync-agents from .agents/rules/zoo-team.md - edit the master, never this copy -->`; `$floor = @(… 'zoo-team.md')`; the copy, `.roomodes` and `.agents/.sync-manifest.json` are all tracked | row G's rule edit would reach no Zoo seat until the sync regenerates the tracked copy, and both outputs would surface as undeclared drift at review | important - resolved: both declared, and Step 7 runs the sync |
| `Projects/AGY_AVIATIONCHAT/.roo/rules/zoo-team.md` (tracked, `557b081b`, AVCH-114) + `port-checklist.md` check 6 + `sync-agents.ps1:665` | the AGY copy is tracked there and identical to the lobby's today; the lobby sync writes only the lobby's `.roo`; `the port needs a work item in **that project's** Jira key` | row G silently diverges a second repo's copy, and nothing closes it automatically | important - resolved: `## Port check` names an **AVCH** ticket as part of row G's close-out |
| `.agents/scripts/check_maps.py:404-424` | `if not idx.exists(): problems.append(f"{rel}/INDEX.md: missing (level-2 folder requires an INDEX.md)")` - all nine existing `.agents/` folders carry one | `.agents/zoo-companion/` would report missing on every session's maps check after landing | important - resolved: `NEW .agents/zoo-companion/INDEX.md` and the `.agents/INDEX.md` row declared |
| `.agents/scripts/zoo_notify.py:450` + `test_zoo_notify.py:806` | `mode.add_argument("--watch", action="store_true", help="poll the store and notify on changes")` - there is no `--poll`, and the poller is already opt-in | `test_poller_off_by_default` had no observable: a flag gating an opt-in mode asserts a tautology, and a rename would pass the existing case vacuously | important - resolved: `zoo_notify.py` is left alone; the real observable is that the installed service stops naming `--watch` |
| the installed bundle, `dist/extension.js` | `a[a.TaskInteractive="taskInteractive"]="TaskInteractive"`; `TaskToolFailed` (PascalCase) returns 0 hits, `taskToolFailed` returns 6 | row A's enum diff, taken against member names, would report three false misses on a correct build | important - resolved: Step 1 diffs the wire values |
| `.agents/scripts/zoo_notify_install.py:181-188` | `REFUSED - {repo} is a git worktree, and it gets pruned` | Step 6's dry run pointed at this lane's worktree would refuse and read as a failure | minor - resolved: the dry run is pointed at the main checkout |
| the first draft's change set | `NEW .agents/zoo-companion/README.md` with no acceptance row naming it | Scope Ledger: an artefact no row requires | minor - resolved: row D names the README as what the card's install row points at |
| the first draft's row C | `test_no_listening_tcp_socket` appeared in the verification plan but not in the test file's declared description | the change set understated what the file proves | minor - resolved: declared |

### Lens 3 - Pre-Mortem narratives (attached to the findings above, originating nothing)

- **The silent one, on the installer finding.** Shipped as first drafted, the operator runs the installer on the PC,
  sees the Startup `.cmd` written, reboots, and gets nothing on his phone - while every test is green, because the
  dry run only proves what the file says, not that the process can reach the socket. He would reasonably conclude
  Telegram or the bot was wrong and debug the wrong half for an evening.
- **The fresh-clone one, on the keyway finding.** The token ends up in the launchd plist because that is the only
  place a service can read it from. It is mode-644 in his home, it is in every Time Machine snapshot, and nothing
  in the repo's guards would ever mention it, because the leak is outside git entirely.
- **The other-machine one, on the AGY port.** The lobby's Zoo seats gain the phone path; the AviationChat repo's
  copy does not. Weeks later a March Hare run inside that project escalates into silence, and the rule text he
  reads in the lobby says the opposite of what that seat was actually given.

### Observations (uncounted)

- The four names the companion calls are present in the installed 3.83 bundle: `approveCurrentAsk`,
  `pressPrimaryButton`, `pressSecondaryButton`, `isReady`. `ROO_CODE_IPC_SOCKET_PATH` is read at activation.
- No `.vsix` exists anywhere on disk, so the three-entry zip layout is taken from the installed extension's manifest
  and from the format's spec. `test_build_vsix_layout` proves the zip's shape; only a real `--install-extension`
  proves VS Code accepts it, which is exactly what row D's operator step does.
- `test_zoo_team.py` B5 scans each master's body for a modal grant near `Verdict:`; the new Escalation contract
  section must avoid `may`/`can`/`should` in that neighbourhood. Noted in Step 7.
- The sync neither copies nor purges an unknown `.agents/zoo-companion/`: its enumerations are named families and
  its purge is manifest-scoped. The INDEX requirement above is the only thing the new folder owes.
- No hook scans for token-shaped strings; `keyway scan` is documented but wired into nothing. `test_token_never_in_argv_or_log`
  plus the new service-file assertion are the whole guard, which is why both exist.
- `risk_seam.py classify` returns `unclassified` in the command centre (SCC-289) - expected; every judgement came
  from the diff and the tests.
- `.claude/worktrees/scc-386-memory-long-term-only` is a stale plain directory, not a registered worktree.

### Landing-order dependency

`git worktree list` shows the lobby and both new lanes at `d70347ba`, zero commits ahead, artifacts untracked. The
overlap with SCC-430 is by declaration: `smh-team-march-hare.md` (its frontmatter there, its body here - a clean
hunk split), `.agents/scripts/INDEX.md`, `_artifacts/_main/INDEX.md`, `.agents/.sync-manifest.json` (both lanes run
the sync, so it conflicts by construction and is resolved by re-running the sync on the rebased tip, never by hand),
the SOP and its changelog, plus this lane's import of `jira_feed.py step`. **SCC-430 lands first.** If this lane
ever landed first, its ticket mirror degrades to "skipped and logged" until `step` exists, and SCC-430's frontmatter
hunk rebases trivially onto this lane's body edit.

Audit verdict: GO
