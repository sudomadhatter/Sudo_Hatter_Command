---
description: COST CONTROL, not hygiene. Every approval prompt breaks the prompt cache, so the turn resumes cold and the operator is billed for the whole context a second time — measured at 5h50m of stalled sessions across 20 runs, and he cancelled a paid subscription over it. This command finds the commands that stopped him and GETS THEM ALLOWED. Its output is a smaller prompt count, never a report. Use when the operator says "what did I have to approve", "update the allow list", "stop asking me", or "llm approvals".
platforms: [opencode, antigravity, claude, codex, zoo]
---

# /smh-llm-approvals — get commands ALLOWED, so the operator stops paying to be asked

## ⛔ WHY THIS COMMAND EXISTS — read this before you read a single step

**Approval prompts are a THREAT to whether this system can be paid for. They are not a UX wrinkle
and this is not a hygiene command.** Every stop breaks the prompt cache: the turn resumes cold and
the operator is billed for the entire context again. He pays twice — once in attention, once on the
invoice — and he **cancelled a paid subscription over exactly this**, in his words: *"This is
killing my workflows and budget… Until it's fixed it's not worth it."*

Measured on his own machine, 20 newest sessions, 2026-09-05:

| bucket | stops | wall-clock | what fixes it |
|---|---|---|---|
| allow-list gaps | 44 | **5h 50m** | **an allow row — this command** |
| a SHAPE the matcher cannot read — heredoc, leading `VAR=` — while looking covered | 94 | **13h 01m** | `shape-block.py` refuses / proves it and the AGENT reshapes — never a row, never `/sandbox` (SCC-415; this row said "sandbox escalation → `/sandbox`" until the 2026-09-05 re-measurement, and that was wrong) |
| **refused by a deny row** | **0** | **0** | — |

⭐ **Read the last row twice. Across 10,028 Bash calls, ZERO commands were refused by a deny rule.**
The fence's deny side costs nothing. The entire cost is the *absence* of allow rows — and the reason
they are absent is that agents keep turning a two-file edit into a story.

### What success and failure look like

- **Success is a smaller number.** Re-run `approval_stops.py` at the end and the *not covered* count
  must have gone DOWN. Say the before and after out loud.
- ⛔ **Ending this command with nothing allowed is a FAILURE**, even if every gate is green, every
  finding is filed and the report is beautiful. A ticket is not an outcome here. Neither is a
  measurement, a plan, a lane, or a review. **The operator did not ask what is wrong. He asked for
  the commands to be allowed.**
- ⛔ **Do not spend his turn explaining.** He has said, repeatedly, that the explaining is itself the
  cost. Act, then report in a few lines.

### The three facts that make this cheap, which agents keep missing

1. **CLAUDE ROWS ARE FREE.** Claude reads `.claude/settings.json` **directly** — that tracked file
   IS the live file. A rendered row is in force the moment it is saved. **No store, no apply, no
   reload, nothing for the operator to run.** A Claude-only harvest touches exactly two files
   (`families.json` + `.claude/settings.json`) and always qualifies for the Step 4 fast path.
2. **Zoo and Antigravity clicks now SURVIVE** (SCC-414). Both applies merge rather than replace, so
   an un-harvested click is kept. Before that fix one routine apply deleted **58** of his own
   grants, he re-clicked, and the next apply deleted them again — which is why he believed his
   approvals "don't seem to store". `--prune` is the opt-in that still replaces.
3. **Narrow beats nothing.** If a command cannot be allowed whole, allow the safe *subcommand* —
   `acli jira workitem view`, not `acli`. Refusing to add anything because the broad form is unsafe
   is how this command produces zero rows and he keeps paying.

**The operator runs nothing.** He types this command and, later, names the commands he wants
allowed. Every file read, every edit, and the apply are the agent's. A step that ends with
*"now run this in your terminal"* is this command failing.

> **Rules in force:** `.agents/rules/constitution.md` §Ask First (the operator's word gates every
> write) · `.agents/rules/command-shape.md` (`cd <abs> && …` in ONE line; `git -C` is auto-denied)
> · `.agents/rules/git-policy.md` — **this command runs no git of its own.** It is named because
> the git verbs below appear as *allow-list rules*, and that policy is why a rule covering
> `git reset`, `git clean` or `git push --force` must never be created by widening one that isn't.

---

## Step 1 — Read the chats

Three agents, three stores, three shapes. Read all three. None needs a script — they are files.

**Claude Code** — one script, because the naive read of these transcripts measures the wrong event:

```bash
cd <repo-abs> && python3 .agents/scripts/approval_stops.py --repo .
```

⛔ **DO NOT harvest refusals here, and do not re-derive this by grepping the transcripts.** Until
SCC-407 this step said: *find a `tool_result` with `"is_error": true` whose content contains
`doesn't want to proceed with this tool use`.* That is a command the operator **REFUSED** — the
opposite of what this door is for. **An approval he GRANTS leaves no record in the transcript at
all**, so the old reading was structurally blind to every command that actually stopped him.
Measured 2026-09-04: it found **one** refusal across 20 sessions and reported *"nothing to
harvest"*, in a window holding **34** stops worth **39 minutes** of him sitting there waiting.

**And a stop costs more than the wait.** It breaks the prompt cache: the turn resumes cold and the
whole context is billed again. Every interruption is charged twice — once in his attention, once on
the invoice — which is why the script ranks by **time waited**, not by count. The expensive stop is
the one he was away from, not the frequent one.

The script reads three signals, none of which is sufficient alone:

| signal | what it proves | why it is not enough alone |
|---|---|---|
| **latency** — the gap between a Bash `tool_use` and its `tool_result` | a human was asked, observed | `gh pr checks --watch` blocks for ten minutes with nobody asked |
| **coverage** — replay against the RENDERED `.claude/settings.json` allow list | predicts the next stop | says nothing about whether it has cost him anything yet |
| **classifier** — the `denied by the Claude Code auto mode classifier` error | a whole refusal class the old step never looked for | fired 4× in the session that found this bug |

It reports only rows **one allow rule would fix**: shell scaffolding (`for i`, `set -e`, `done`),
self-explaining waits (`timeout 900`, `--watch`) and wrapped continuation lines are dropped by name,
because a list whose rows cannot be acted on is longer without being more useful.

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
repo already ships and tests, which handles every platform this runs on, **every named VS Code
profile**, and the `zoo-code.customStoragePath` setting — three cases a single hardcoded path
silently misses:

```python
import importlib.util
spec = importlib.util.spec_from_file_location("z", ".agents/scripts/zoo_notify.py")
z = importlib.util.module_from_spec(spec); spec.loader.exec_module(z)
roots = z.store_roots()          # a LIST — the default profile plus each named profile
```

For reference, what it returns — the tail is always
`Code/User/globalStorage/zoocodeorganization.zoo-code/tasks`, under a base that differs per side:
the Windows side `C:/Users/<you>/AppData/Roaming/`, the Ubuntu side `~/.config/`. ⛔ And under **VS
Code Remote (WSL)** the extension runs SERVER-side, so the live store is
`~/.vscode-server/data/User/globalStorage/…` while `~/.config/Code` may not exist at all — measured
2026-09-04 on this box, SCC-396. That is exactly why you call the resolver instead of pasting a
path: it returns a LIST, and a side with a named profile, a custom store path or a Remote server has
roots this sentence does not name.

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

⛔ **Then run the gates, BEFORE you report anything.** The render succeeding means the three files
match the source; it says nothing about whether a picked row tore a hole in the fence.

```bash
cd <repo-abs> && python3 .agents/scripts/tests/run_all.py
```

⛔ **The whole suite, not `test_permission_parity.py` alone.** The battery is the fence's main
guard, but it is not the only law a picked row can break, and the difference is not theoretical:
on the first real run a harvested `Bash(python:*)` was refused by the ONE-INTERPRETER law
(SCC-376), which lives in `test_settings_allowlist.py` A3 — a file the battery does not run. A
second pick went stale against `test_zoo_permissions.py`'s guide-count check. Naming one file here
would have passed both. Add `--on-main` to a single-file run when a lane worktree exists.

**A red row is one of two different things, and they take opposite actions — read the failure
before you act:**

- **A pick the fence refuses.** Back *that* row out of `families.json`, re-render, and tell the
  operator which of his picks could not land, naming the deny row that refused it. ⛔ Some have
  **no deny row** — `npx` is refused by battery case A5, which pins `npx create-next-app` as
  must-ask because a bare prefix auto-approves downloading and running any package. Say *that*
  rather than inventing a deny row to fill the sentence.
- **A pick that RESOLVED a known disagreement.** A11 asserts every row in its KNOWN list still
  disagrees across platforms, so it goes red when a **good** pick makes one agree. The test's own
  contract is that a resolved row is deleted from that list — backing the pick out here would
  throw away a correct pick and report a refusal that never happened.

Measured on the first real run (SCC-392, 2026-09-04): of 17 picks, **six** could not land —
`gh` and `env -u GITHUB_TOKEN gh` (`command(gh pr merge)`, `command(gh repo delete)`,
`command(gh release delete)`), `acli` (`command(acli jira workitem delete)`), `chmod`
(`command(chmod -[a-zA-Z]*R[a-zA-Z]* 777)`), `npx` (battery A5, no deny row), and `python`
(the one-interpreter law — a rule for a binary neither machine has). Running these checks AFTER
writing all 17 is what turned minutes of work into a day of backing rows out one at a time.

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
**any command at all**: locally that is his call in a session he is watching, but the source is the
tracked file every side and every clone reads, so promoting one is a different act from having
granted it. ⛔ **And do not narrow
it for him** — this door does not compute prefixes (SCC-354). Show the row, say plainly what it
permits, and let him answer.

⛔ **Claude's apply is DIFFERENT from Antigravity's, and the difference is the whole point.** The
Antigravity apply REPLACES both arrays, which is why it carries a data-loss caveat. Claude's tracked
file IS the live file inside this repo — a rendered row is in force the moment it is saved. But a
session opened in a project checkout or worktree reads THAT repo's tracked file plus the machine's
user scope (`~/.claude/settings.json`), so a lobby row holds nowhere else until it is also in user
scope. `claude_permissions_apply.py --apply` (SCC-415) does that merge — **additive, never a prune
unless `--prune`, `allow` rows only, backs up once** — and widens the sandbox's writable paths.
⛔ **An agent cannot run it.** The auto-mode classifier refuses every write to `~/.claude/settings.json`
unconditionally (measured 2026-09-05: three refusals, identical), so it is the operator's line, the
same as the other two applies. It never touches `sandbox.excludedCommands` (that removes a command
from the sandbox and LOSES the auto-approval — the opposite of the fix; operator ruling 2026-09-05).

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
# close VS Code first — from the Windows side: taskkill /IM Code.exe
cd <repo-abs> && python3 .agents/scripts/zoo_permissions_apply.py --apply
```

⛔ **Both applies write OUTSIDE the repo, so they need the Bash sandbox OFF.** Zoo's store is
under VS Code's user data and Antigravity's is `~/.gemini/`; neither is in the sandbox's writable
set. ⛔ **They fail DIFFERENTLY and only one of the two errors is the one people remember.**
Antigravity writes with `write_text` and raises `OSError: [Errno 30] Read-only file system`; Zoo
writes through `shutil.copy2` and `sqlite3`, so it raises `sqlite3.OperationalError: attempt to
write a readonly database` instead. Both are the sandbox, neither is a broken script. Run the
`--status` probes sandboxed (they only read), and the two `--apply` calls with it disabled.

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

Then make Claude's rows hold everywhere on the machine, not only in this repo. **This one the
operator runs, in his own terminal** — the agent prints the line and stops:

```bash
cd <repo-abs> && python3 .agents/scripts/claude_permissions_apply.py --status   # read-only, safe anytime
cd <repo-abs> && python3 .agents/scripts/claude_permissions_apply.py --apply    # HIS terminal, once per machine; PC: python
```

⭐ **The `--apply` line is the LAST thing this command prints**, every run, whether or not a row
was picked — it is what the operator asked for (*"give me the script I can call to run once
/smh-llm-approvals writes it"*, 2026-09-05). Run `--status` yourself (it reads only, sandboxed is
fine) and paste its report above the line, so he sees how many rows and paths it will add before he
runs it. A session restart makes it take effect.

⛔ **And say, once, what the rows can NOT fix.** Step 1's report has a section headed *NO ALLOW ROW
FIXES THESE - the harness bans the shape*. A heredoc or a `VAR=` head there is the AGENT's own
command shape (command-shape.md rules 5–6, `shape-block.py`), not a missing row — do not propose a
row for it, and do not call it the sandbox.

⛔ **The apply REPLACES both arrays — it does not merge.** Every click-written row he did *not* pick
is gone the moment it runs. That is the design (the tracked file is the fence, not the store), but
it is his to know before it happens: say how many store-only rows are about to be dropped, by name,
and get his word. This is the one step of this command that can take a permission away.

## Step 4 — Land it

⛔ **This step is the reason the command exists in one piece.** Steps 1-3 leave FOUR modified
tracked files in the working tree — `.agents/permissions/families.json` and its three renders —
and a door that stops here hands the next agent a decision it has no basis to make. Improvising
next to `main` means reaching for the heaviest thing available: a plan, a worktree, a five-lens
review. None of that is warranted, and the reason is written down: this change class is DATA whose
correctness is machine-checked by the gates Step 3 already ran, and the operator's approval was
captured live at the Step 2 gate.

**That exemption is named in `.agents/rules/artifacts-always-first.md` § "When to Skip".** It is
conditional, and ⛔ **the scope guard is RUN, never eyeballed** — a qualification an agent judges
is one it can want its way through:

```bash
cd <repo-abs> && git diff --name-only origin/main...HEAD
```

Every path outside `_artifacts/` must be one of these **five**, and nothing else:
`.agents/permissions/families.json` · `.agents/permissions/antigravity.json` ·
`.claude/settings.json` · `.vscode/settings.json` · `docs/migrations/terminal-permissions-guide.md`
— and in the settings files, only the rows this door renders (`permissions.allow`; the two
`zoo-code.*` arrays). A sixth path, or a touched `hooks` block, voids the exemption and the work
takes the full lane.

⭐ **The guide is on this list because Step 3's own gate FORCES it (SCC-412, measured 2026-09-05).**
Any Zoo allow row moves the tracked count, which turns `test_zoo_permissions.py::test_guide_currency`
red until the guide's count line is updated. With the guide excluded, Step 3 required the very edit
Step 4 forbade, so **the fast path was unreachable for every Zoo-side harvest** — and one narrow row
consumed a ticket, a worktree, a plan, five review lenses and a back-out before shipping nothing.
The guide edit is a rendered consequence of the pick, not a second decision. (The deeper fix —
generating that count line so no hand edit exists at all — is SCC-413.)

⭐ **A Claude-only harvest touches TWO files and is always inside this guard.** No Zoo row, no count
line, no store, no apply. When the picks divide, prefer landing the Claude rows immediately and
handling any Zoo/Antigravity rows in the same pass — do not let a Zoo row drag the whole harvest
into a lane while the operator keeps paying for prompts a free Claude row would have ended. ⛔ **`lane_qualify.py` still answers `TASK` for these paths and that is
correct** — it classifies by path and cannot see this door's guards, so a hand edit to
`families.json` outside this command keeps the full lane. Do not "fix" it to agree.

⛔ **Write the receipt before you commit.** The exemption drops the plan, the audit, the RED-first
assertion and the review verdict — it does NOT drop the record, for the same reason
`/smh-quick-fix` keeps one: without it, an agent that hand-edited `families.json` and *decided* its
work was a harvest is indistinguishable from a real run, and every gate it does run still passes.
A lean `walkthrough.md` under `_artifacts/_main/<YYYY-MM-DD>_<slug>/` carrying the picks, **the
operator's words verbatim**, each pick the fence refused with the deny row that refused it, and a
`## Your Actions` section. Then stamp it:

```bash
cd <repo-abs> && python3 .agents/scripts/flight_recorder.py record --task <KEY> --root _artifacts/_main/<YYYY-MM-DD>_<slug> --repo <repo-abs> --apply
```

Then commit and open the pull request:

```bash
cd <repo-abs> && git checkout -b chore/<KEY>-<slug> origin/main
cd <repo-abs> && git add .agents/permissions/families.json .agents/permissions/antigravity.json .claude/settings.json .vscode/settings.json _artifacts/_main/<YYYY-MM-DD>_<slug>
cd <repo-abs> && git commit -m "<KEY> chore(permissions): harvest <n> approved rows into the shared source"
cd <repo-abs> && env -u GITHUB_TOKEN git push -u origin chore/<KEY>-<slug>
cd <repo-abs> && gh pr create --base main --head chore/<KEY>-<slug> --fill
```

⛔ Explicit paths only — never `git add -A`, `.` or `-u`; a permissions run is exactly when other
lanes have work in the tree. The armed `commit-msg` hook refuses a commit with no valid Jira key.
Never a bare `gh pr create`: with no `--fill` it prompts, and an agent shell has no TTY to answer.

⛔ **Then STOP. Report the PR link.** The operator clicks *Merge pull request*; `main-write-gate`
runs the full enforcement suite on the PR as the fitness half. **This door does not merge, does not
mint a push token, does not push `main`, and does not change which branch a checkout is on** —
`.agents/rules/git-policy.md` bans all four by name, in this repo, for every door
(*"No agent merges to `main` in this repo. There is no eligibility test, no 'small enough' class,
no self-merge"*). The Step 2 pick is the operator's word about **which commands may run**; it was
never a yes to landing on `main`, and treating it as one is exactly the substitution
`git-policy.md` records as having ridden six merges on one invocation.

⚠️ Under the sandbox, `.git/config.lock` can appear as a character device (`crw-rw-rw- nobody
nogroup 1, 3`) rather than a real lock, and git fails with *could not lock config file*. It is a
mount artifact, not a stale lock — re-run with the sandbox off rather than deleting anything.

## Step 5 — Report what changed

Name each row added and which file it went into, name each pick that could NOT land with the deny
row that refused it, confirm the apply result, say plainly what is live now versus staged — and
**end with the one line he runs**, every time:

```bash
python3 .agents/scripts/claude_permissions_apply.py --apply    # PC: python
```

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
- It does not make the operator run anything to make a row live in THIS repo. The one line it
  hands him — `claude_permissions_apply.py --apply` — is the user-scope and sandbox write he asked
  for by name (2026-09-05), and it targets the only file no agent is permitted to write.
