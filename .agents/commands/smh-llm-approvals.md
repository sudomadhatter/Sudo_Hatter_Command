---
description: Audit recent agent chats for the terminal commands that stopped and waited for the operator's approval, show them as one list, and — on the operator's word — route the ones he picks into the ONE permission source that renders all three allow lists. It also surfaces the Claude rules that already stopped ASKING, which sit in a machine-local settings file that never travels. The operator types the command and answers one question; the agent does every read, every edit and every apply. Use when the operator says "what did I have to approve", "update the allow list", or "llm approvals".
platforms: [opencode, antigravity, claude, codex, zoo]
---

# /smh-llm-approvals — audit what you approved, then update the ONE source

> **Rules in force:** `.agents/rules/constitution.md` §Ask First (the operator's word gates every
> write) · `.agents/rules/command-shape.md` (`cd <abs> && …` in ONE line; `git -C` is auto-denied)
> · `.agents/rules/git-policy.md` — **this command runs no git of its own.** It is named because
> the git verbs below appear as *allow-list rules*, and that policy is why a rule covering
> `git reset`, `git clean` or `git push --force` must never be created by widening one that isn't.

**The operator runs nothing.** He types this command and, later, names the commands he wants
allowed. Every file read, every edit, and the apply are the agent's. A step that ends with
*"now run this in your terminal"* is this command failing.

---

## Step 1 — Read the chats

Three agents, three stores, three shapes. Read all three. None needs a script — they are files.

**Claude Code** — `~/.claude/projects/*/*.jsonl`, newest ~20 by modified time.

Each line is a JSON record. A refusal is a `tool_result` block with `"is_error": true` whose
content contains `doesn't want to proceed with this tool use`. ⛔ **That block does not carry the
command.** It carries a `tool_use_id`, and the command lives in an earlier `tool_use` block with
`"name": "Bash"` and that same `id`. So walk the file forward, remember each Bash `tool_use` by
its id, and pair each refusal back to the command it refused. Grepping for the rejection text
alone finds every denial and can name none of them.

**Claude Code, second half — the rules that already stopped asking.** The transcripts above find
commands that STOPPED. They cannot find the ones that stopped *asking*, because an approval the
operator granted in a terminal chat is written to no transcript — it is written to one of two
machine-local files, and neither of them travels:

- `~/.claude/settings.json` — user scope, outside every repo.
- `<repo>/.claude/settings.local.json` — project scope, gitignored (`.gitignore:58`), and normally
  absent.

The tracked `<repo>/.claude/settings.json` is the only Claude list that reaches the other machine,
so a rule living only in those two decides **here and nowhere else** — the other machine goes on
asking for that same command forever, and nothing in this door could see it until SCC-392. Read the
difference with the script that resolves all three paths on either machine:

```bash
cd <repo-abs> && python3 .agents/scripts/claude_permissions_status.py   # PC: python
```

Read-only, exit 0 either way — a machine with nothing local prints *no machine-local rows* and has
nothing to show. An absent `settings.local.json` counts as empty, not as an error, and so is an
empty one.

⛔ **If it exits 2 saying the project file could not be READ, re-run it with the Bash sandbox off.**
Measured 2026-09-04: under the sandbox this repo's `.claude/settings.local.json` is a mount artifact
— a character device — not a settings file, and reading it raises `PermissionError`. Outside the
sandbox the path is simply absent and the run is clean. The script refuses rather than guessing,
because treating an unreadable list as empty would under-report the very rows this step exists to
find — the same silent under-report SCC-355 cost this door once already.

**Zoo Code** — `<root>/*/ui_messages.json`, newest ~20 by modified time.

⛔ **Do not hardcode the store path, and do not write `%APPDATA%` into one — that is a cmd.exe
variable, not a path, and it expands to nothing in a glob or in Python.** Ask the resolver this
repo already ships and tests, which handles Mac and PC, **every named VS Code profile**, and the
`zoo-code.customStoragePath` setting — three cases a single hardcoded path silently misses:

```python
import importlib.util
spec = importlib.util.spec_from_file_location("z", ".agents/scripts/zoo_notify.py")
z = importlib.util.module_from_spec(spec); spec.loader.exec_module(z)
roots = z.store_roots()          # a LIST — the default profile plus each named profile
```

For reference, what it returns: on the Mac
`~/Library/Application Support/Code/User/globalStorage/zoocodeorganization.zoo-code/tasks`, and on
the PC the same tail under `C:/Users/<you>/AppData/Roaming/Code/User/`. Those are what the function
computes, not a substitute for calling it — a machine with a named profile or a custom store path
has roots this sentence does not name.

Each file is a JSON array of messages. A command that stopped for the operator is one where
`type` is `ask`, `ask` is `command`, and **`autoApprovalDecision` is
`null`**. That last field is Zoo's own record of what it did: `"approve"` means its matcher let
the command through and nobody was blocked, `"deny"` means the fence refused it **on purpose**,
and `null` means it had no opinion and had to stop and ask. Only `null` is what this audit is
about. The command text is the message's `text`.

⛔ **Do NOT filter on `partial`, however much it looks like a streaming artefact.** This door used
to require `partial` is not `true` and it silently under-reported: measured against the live store,
it listed 23 stopped commands and dropped 4. Zoo clears that flag when its OWN matcher
auto-approves and leaves it standing when the operator has to answer, so filtering on it discards
the very asks this door exists to surface — and the operator, reading a list that is missing his
own commands, has no way to tell. Same mechanism, same fix as `zoo_notify.classify()` (SCC-355).

**Antigravity** (the VS Code extension) — `~/.gemini/config/config.json`, one file per machine.

Antigravity keeps no ask log. What it keeps is the result of every "always allow" click: a rule
appended to `userSettings.globalPermissionGrants.allow`. ⛔ **What it stores is the FULL RESOLVED
string, not a prefix** — measured on the live store 2026-09-04, a click on
`find ~/.claude -name "*.md" …` stored that entire line, and a click on a file stored that one
file's path. A click therefore buys exactly what he clicked and nothing adjacent, which is the whole
reason those rows are worth routing back through this door. So the things the operator had to stop
for are exactly the rows in the live store that the tracked render does not contain. Read both files
and diff the `allow` arrays as sets — the rendered side is `.agents/permissions/antigravity.json`;
`python3 .agents/scripts/antigravity_permissions_apply.py --status` gives the counts. A store that
is already `in sync with tracked file` has nothing to show, and says so.

⛔ **Store-only rows come in two kinds and they are not the same question. Split them.**

- `command(…)` / `unsandboxed(…)` — a terminal command. Strip the wrapper and show the command, so
  he reads commands, not grammar.
- `read_file(…)` — a FILE the agent was blocked from reading. Not a command, and it must not be
  listed as one. Antigravity auto-allows reads *inside* the workspace and asks for everything
  outside it, so every row here is an out-of-workspace path. Show them under their own heading, and
  show the **folder** each one sits in beside it — the folder, not the file, is what Step 3 grants
  (SCC-387).

If a store folder is missing or empty, say so by name. An empty Zoo store is the normal state on
a machine where Zoo has not been used — it is not an error, and it must not read like one.

## Step 2 — Show the operator the list

One list, de-duplicated, newest first, in chat. Nothing else — no proposed rows, no
recommendations, no allow-list arithmetic. He reads the commands and decides.

```text
Commands that stopped for approval - 12 Claude sessions, 3 Zoo threads, 1 Antigravity store

Claude Code
  npx create-next-app my-app
  pnpm install --frozen-lockfile
  acli jira workitem view SCC-352

Zoo Code
  cd /Users/sudohatter/repo && git fetch origin main

Antigravity
  npm test
  find .agents -type f

Antigravity - files it was blocked from reading (outside the workspace)
  <home>/.claude/projects/<slug>/memory/<one file>       folder: <home>/.claude/projects/<slug>/memory
  <home>/.claude/projects/<slug>/memory/<another>        folder: <home>/.claude/projects/<slug>/memory

Claude - rules that already stopped asking, on THIS machine only
  Bash(gh:*)
  Bash(npm:*)
  Bash(bash:*)                                           permits ANY command
```

That last group is the odd one out, and it keeps its own heading for a reason: those rows are not
commands that stopped, they are rules that already stopped asking — granted once from a terminal
chat into a file that never leaves this machine. The question about them is not *may I run this*,
it is *should this travel*. Folded into the list above, that distinction is gone.

Indent **every** line of a multi-line command, so the operator can see where one ends and the
next begins. Then ask one question: **which of these do you want allowed?**

⛔ **Stop here.** His answer is the gate. Nothing below runs without it, and "looks good" is not
it — he must name the commands or say "all of them".

## Step 3 — Write what he picked

One file, then one render. Since SCC-378 the three platform lists are RENDERED from a single
source, `.agents/permissions/families.json`, by
`python3 .agents/scripts/permission_render.py`. **Edit the source, never the three rendered files**
— a hand edit to `.vscode/settings.json`, `.claude/settings.json` or
`.agents/permissions/antigravity.json` is drift, `permission_render.py --check` turns red, and the
next sync overwrites it. Each picked command becomes a family row (`id`, `cmd`, `why`, and the
platforms it applies to), or a `cmd` widened inside an existing family when it is the same intent;
the renderer derives each platform's grammar from `cmd`. Then run the renderer, and confirm
`--check` prints *in sync*.

⛔ **Then run the fence battery, BEFORE you report anything.** The render succeeding means the
three files match the source; it says nothing about whether a picked row tore a hole in the fence.

```bash
cd <repo-abs> && python3 .agents/scripts/tests/test_permission_parity.py
```

Add `--on-main` when a lane worktree exists — the battery refuses to run on `main` beside one.
A red row is not a test to fix: it is a pick that **cannot land**. Back that one row out of
`families.json`, re-render, and re-run until it is green. Then tell the operator which of his
picks could not land and **name the deny row that refused each one**, so he is reading his own
fence rather than a verdict.

Measured on the first real run (SCC-392, 2026-09-04): of 17 picks, five could not land —
`gh` and `env -u GITHUB_TOKEN gh` (`command(gh pr merge)`, `command(gh repo delete)`,
`command(gh release delete)`), `acli` (`command(acli jira workitem delete)`), `chmod`
(`command(chmod -[a-zA-Z]*R[a-zA-Z]* 777)`), and `npx`, which no deny row refuses but the
battery pins as must-ask because a bare prefix auto-approves downloading and running any
package. Running this check AFTER writing all 17 is what turned minutes of work into a day of
backing rows out one at a time.

The per-platform shapes below are what the RENDERER writes — read them to know what a row will
become, not as files to open.

**Claude Code** → `.claude/settings.json`, `permissions.allow`. Rule shape is
`Bash(<prefix> *)`.

⛔ **Match the narrowness already in the file.** That list scopes git to the subcommand —
`Bash(git status:*)`, `Bash(git push origin chore/:*)` — and omits `git reset`, `git clean` and
`git push --force` deliberately. A rule is only ever as wide as the command it came from:
`git fetch origin main` earns `Bash(git fetch *)`, never `Bash(git *)`. Widening one word past
the command is how a careful list becomes a blank cheque, and `permissions.deny` is empty, so
nothing downstream catches it.

⛔ **A harvested row is already a RULE, and the narrowness law above has nothing to measure it
against.** That law reads *a rule is only ever as wide as the command it came from* — but a row
lifted out of `~/.claude/settings.json` did not come from a command; it came from an earlier
decision whose command is long gone. So show it for what it is and get his word out loud before it
goes into the source. `Bash(bash:*)` and `Bash(sh:*)` are on that list today and each one permits
**any command at all**: locally that is his call on a machine he is watching, but the source renders
to BOTH machines, so promoting one is a different act from having granted it. ⛔ **And do not narrow
it for him** — this door does not compute prefixes (SCC-354). Show the row, say plainly what it
permits, and let him answer.

⛔ **Do NOT copy the apply warning at the end of this step onto Claude's path.** The Antigravity
apply REPLACES both arrays, which is why it carries a data-loss caveat. **Claude has no apply and
must not grow one** — its tracked file IS the live file, so a rendered row is in force the moment it
is saved, nothing is pushed into a store and nothing can be lost. A data-loss caveat here would be a
threat that does not exist. The machine-local files the harvest READ are never edited: a
now-redundant row there is the operator's own edit to ask for by name.

**Zoo Code** → `.vscode/settings.json`, `zoo-code.allowedCommands`. Plain string
prefixes, no wrapper. Same narrowness rule. ⛔ **Never touch `zoo-code.deniedCommands`** — the
deny list is the fence, and this command grows allows only.

**Antigravity** → `.agents/permissions/antigravity.json`, `globalPermissionGrants.allow`, as
`command(<prefix>)` plus an `unsandboxed(<prefix>)` twin (the first governs execution, the second
the sandbox escape; the renderer writes both). Each whitespace token is an anchored regex, so the
renderer escapes metacharacters — you never type `\.` yourself. Same narrowness rule; the `deny`
array is the fence and this command never adds to it.

**A picked FILE row is a different rule kind, not a differently spelled command.** Add it to the
source as `"grant": "read_file"`, with `cmd` set to the absolute **folder** — never the single file
that asked — and `"only": ["antigravity"]`. The renderer emits one bare `read_file(<dir>)` and no
twins, because the vendor matches file targets as paths rather than as per-token regexes and grants
a directory **recursively** (antigravity.google/docs/permissions, read 2026-09-04). The folder is
the unit for the same reason a prefix is the unit for a command: a per-file grant is exactly what
the click already wrote, and it buys one file. ⛔ Narrowness still binds, and it binds harder here
because a directory is recursive — grant the folder that asked, not its parent. `~/.claude/projects`
would sweep in every Claude session transcript on the machine; that is the operator's call to make
out loud, never a default you take for him.

⛔ **If the operator picked a command Zoo's deny list refuses, do not add it. Say which row
refused it and stop.** He asked to be un-blocked, not to have his own fence removed; if he wants
the deny row gone, that is his edit to ask for by name.

Then make Zoo actually see it. Zoo does not read `.vscode/settings.json` when it decides — it
reads VS Code's `globalState` SQLite database, which that file seeds exactly once on a fresh
machine and never again ([[zoo-approvals-decision-store]], SCC-351). So:

```bash
cd <repo-abs> && python3 .agents/scripts/zoo_permissions_apply.py --status   # PC: python
```

`--status` is read-only and safe with VS Code open — run it first and report what it says. The
write needs VS Code fully closed, because SQLite will not take a second writer:

```bash
osascript -e 'quit app "Visual Studio Code"'                                  # Mac
cd <repo-abs> && python3 .agents/scripts/zoo_permissions_apply.py --apply
```

⛔ **Both applies write OUTSIDE the repo, so they need the Bash sandbox OFF.** Zoo's store is
under VS Code's user data and Antigravity's is `~/.gemini/`; neither is in the sandbox's writable
set, and the failure is `OSError: [Errno 30] Read-only file system` raised from the script's own
`write_text` — a traceback that looks like a broken script and is not one. Run the `--status`
probes sandboxed (they only read), and the two `--apply` calls with it disabled.

Ask before quitting his editor — that is his window, with his unsaved work in it. If he says no,
leave the tracked file edited and tell him the Zoo rows are staged but not live until the apply
runs. **Claude's rows are live the moment the file is saved and need none of this.**

Then make Antigravity see it — its store is also per machine:

```bash
cd <repo-abs> && python3 .agents/scripts/antigravity_permissions_apply.py --status   # read-only, safe anytime
cd <repo-abs> && python3 .agents/scripts/antigravity_permissions_apply.py --apply    # writes the grants block, backs up once
```

No editor quit is needed (a plain JSON file, no database), but the extension re-reads it on a window
reload — ask him to reload the VS Code window and tell him so. The closing `--status` must read
*in sync with tracked file*.

⛔ **The apply REPLACES both arrays — it does not merge.** Every click-written row he did *not* pick
is gone the moment it runs. That is the design (the tracked file is the fence, not the store), but
it is his to know before it happens: say how many store-only rows are about to be dropped, by name,
and get his word. This is the one step of this command that can take a permission away.

## Step 4 — Land it

⛔ **This step is the reason the command exists in one piece.** Steps 1-3 leave FOUR modified
tracked files in the working tree — `.agents/permissions/families.json` and its three renders —
and a door that stops here hands the next agent a decision it has no basis to make. Improvising
next to `main` means reaching for the heaviest thing available: a plan, a worktree, a five-lens
review, a pull request. None of that is warranted, and the reason is written down: this change
class is DATA whose correctness is fully machine-checked by the two gates Step 3 already ran, and
the operator's approval was captured live at the Step 2 gate.

**That exemption is named in `.agents/rules/artifacts-always-first.md` § "When to Skip", and it
is conditional on all four guards holding** — his live pick, `--check` in sync, the battery green,
and the diff confined to those four paths. Anything else in the diff and the exemption is void and
the work takes the full lane. ⛔ **`lane_qualify.py` still answers `TASK` for these paths and that
is correct** — it classifies by path and cannot see this door's guards, so a hand edit to
`families.json` outside this command keeps the full lane. Do not "fix" it to agree.

The road, given a ticket key and a slug:

```bash
cd <repo-abs> && git checkout -b chore/<KEY>-<slug> origin/main
cd <repo-abs> && git add .agents/permissions/families.json .agents/permissions/antigravity.json .claude/settings.json .vscode/settings.json
cd <repo-abs> && git commit -m "<KEY> chore(permissions): harvest <n> approved rows into the shared source"
```

⛔ Explicit paths only — never `git add -A`, `.` or `-u`; a permissions run is exactly when other
lanes have work in the tree. The armed `commit-msg` hook refuses a commit with no valid Jira key.

Then `main`. It is protected by a required status check, so a direct push is rejected — the road
is **Road 2**, which `main_write_gate.py` already calls *the local door's road*:

```bash
cd <repo-abs> && git checkout main && git merge --no-ff chore/<KEY>-<slug> -m "Merge chore/<KEY>-<slug> into main"
cd <repo-abs> && git push origin main:refs/heads/gate/<KEY>-<slug>
```

Wait for that check to go green on the pushed sha, then mint the single-use token and push:

```bash
cd <repo-abs> && sh .agents/scripts/git-hooks/mint-push-token.sh --command "<this command>" --branch chore/<KEY>-<slug> --key <KEY> --operator-approval "<his words, verbatim>"
cd <repo-abs> && git push origin main
```

The token is single-use, expires in 30 minutes, and is spent by that push — so mint it LAST and
commit nothing after it. If the operator's pick at Step 2 was not an unambiguous yes to landing
this, delete `.git/main-push-approval` and ask him instead.

⚠️ Under the sandbox, `.git/config.lock` can appear as a character device (`crw-rw-rw- nobody
nogroup 1, 3`) rather than a real lock, and git fails with *could not lock config file*. It is a
mount artifact, not a stale lock — re-run with the sandbox off rather than deleting anything.

## Step 5 — Report what changed

Name each row added and which file it went into, name each pick that could NOT land with the deny
row that refused it, confirm the apply result, and say plainly what is live now versus staged.
Then stop.

## What this command does NOT do

- It does not propose rows, rank them, or compute a "minimal prefix". The operator reads real
  commands and picks. Machine-chosen breadth was built once and cut (SCC-354): every defect it
  produced lived in the choosing, and the operator never asked for it.
- It does not touch any deny list — Zoo's, Antigravity's, or a future one.
- It does not edit the two machine-local Claude files — it READS them. Deleting a row from
  `~/.claude/settings.json` because the source now covers it is the operator's own edit to ask
  for by name, never a tidy-up this door performs.
- It does not edit the three rendered files. The source is the only thing it writes; the render does the rest.
- It does not make the operator run anything.
