# Terminal approvals — the one guide (Claude Code · Zoo Code · the rest)

**One page for: which agent will ask, where its decision actually lives, how to change a list so the
change sticks, and what the fence is really worth.** Every agent carries its OWN store and its OWN
matcher — there is no VS Code master permission system governing extensions, so editing the wrong
surface changes a display, not a decision. Standing design (operator ruling, 2026-08-30): **allows are
broad; denies are the fence** — under a broad allow an un-denied spelling does not ask, it RUNS, so the
deny list is the minimum set naming real damage.

Everything about Zoo here was verified by reading and executing Zoo Code v3.80.1's own compiled source
(the matcher extracted verbatim and run against a real 551-command session), not inferred from docs.

> **This page replaces three (SCC-376 Phase 7).** `terminal-global-permission.md` (the cross-agent front
> door) is now §1, `claude-terminal-permission.md` (the Claude deep dive) is now §3, and
> `zoo-code-permissions-guide.md` is §2 and §4 onward, carried section for section. The split was a
> direct cause of how long the SCC-376 investigation took: three pages, one subject, each true about
> its own third and silent about the other two. Origin: SCC-351.

---

## 1. Which agent decides, and from which store

| Agent | Decision store | Matcher | Add an approval that sticks |
|---|---|---|---|
| **Claude Code** | `.claude/settings.json` (tracked `permissions.allow`) + `settings.local.json` under the project's `.claude/` (machine-local, gitignored, linked into worktrees) + `~/.claude/settings.json` (the ONE portable user file since SCC-376) | per-rule `Bash(prefix:*)` patterns, judged per command segment | add the rule to the right tier — tracked for both machines, local for one machine only; live immediately. Deep dive: §3 |
| **Zoo Code** (VS Code) | VS Code globalState `state.vscdb`, which the tracked [`.vscode/settings.json`](../../.vscode/settings.json) `zoo-code.*` lists SEED exactly once and never again | lowercase starts-with per command PIECE, longest prefix wins allow-vs-deny, tie goes to deny | edit the tracked lists, keep [test_zoo_permissions.py](../../.agents/scripts/tests/test_zoo_permissions.py) green, quit VS Code, run the apply script, reopen. Deep dive: §4 onward; procedure: §9 |
| **opencode** | its own config under `.opencode/` | WHOLE-string prefix (no per-piece split) — compounds rarely match | accept prompts, or add whole-string prefixes by hand. **Outside `/smh-llm-approvals`** (SCC-354): a whole-string prefix unblocks exactly one invocation, so a list grown that way carries one row per command and stops being readable |
| **Codex** | `~/.codex/` config (`approval_policy` / sandbox), per machine | policy-level, not per-command lists | set the policy per machine. **Outside `/smh-llm-approvals`** (SCC-354): there is no per-command list to grow — the policy is the whole decision |
| **Antigravity** (VS Code extension `google.google-antigravity`, bundles the `agy` CLI) | `~/.gemini/config/config.json` → `userSettings.globalPermissionGrants` (`allow` / `deny` arrays), per machine; the tracked rendering is [`.agents/permissions/antigravity.json`](../../.agents/permissions/antigravity.json) | one anchored regex per whitespace token against the command's leading tokens; strict **Deny > Ask > Allow**; two rule types, `command(X)` for execution and `unsandboxed(X)` for escaping the sandbox | add the family to the ONE source [`.agents/permissions/families.json`](../../.agents/permissions/families.json), render (`/smh-sync-agents`, or `python3 .agents/scripts/permission_render.py`), then per machine `python3 .agents/scripts/antigravity_permissions_apply.py --apply` and reload the VS Code window. Deep dive: §3A |

**Where the PC's stores live, and why it surprises people (SCC-376).** The PC works inside WSL2 /
Ubuntu, and Claude's fence travels with it: `~/.claude/settings.json` is a Linux file inside the distro,
byte-identical to the Mac's. **Zoo's does not.** Zoo runs inside the distro (the workspace extension
host) but the VS Code *window* keeps its `globalState` on the Windows side — measured twice, in Phase 4
and again in Phase 6: no `state.vscdb` exists anywhere under either distro. So the apply script is run
**from Ubuntu** and reaches the Windows stores through `/mnt/c`. There are **two** of them, because the
second seat (`code2`) launches with its own `--user-data-dir`:

```
%APPDATA%\Code\User\globalStorage\state.vscdb                  <- instance 1 (code1)
%USERPROFILE%\vscode-isolated\User\globalStorage\state.vscdb    <- instance 2 (code2)
```

**Command shape matters as much as the lists.** The house pin idiom is `cd <abs> && git <verb>` in ONE
compound line — `git -C` is auto-denied as a launder shape, fills are absolute, and a lobby script
called after any `cd` needs the lobby pinned first. The law: [`command-shape.md`](../../.agents/rules/command-shape.md)
(§The law, §Absolute fills, §Zoo), restated for the seats in §10.

**Growing the lists without re-reading sessions by eye** is `/smh-llm-approvals` (SCC-352): it audits
recent Claude and Zoo chats for every command that stopped for approval, shows the operator the list,
and adds the ones he names to both allow lists. It proposes nothing and never edits a deny list. Full
mechanics in §13.0.

---

## 2. The one-paragraph story

Zoo only auto-runs a terminal command when every piece of it starts with an entry on the ALLOW
list, and refuses it when any piece starts with an entry on the DENY list. Everything else asks
you. The pain had three causes: **(1)** the lists you edit in [`.vscode/settings.json`](../../.vscode/settings.json) are not the
lists Zoo decides with (they only seed it once — §5); **(2)** Zoo's matcher is a plain
starts-with test, so the house's own `git -C <path>` habit could never match a `git status`
allow (§6); **(3)** a handful of safe families (`cd`, `git push`, `gh pr`, `acli`, heredoc
python) were simply missing. The fix is one tracked list (§8), one apply script (§9), and a
command-shape law for the seats (§10). Measured on a real session: **34.1% auto-approved before,
88.2% after** (§11).

---

---

## 3. Claude Code — the deep dive (settings tiers, sandbox, worktrees)

Claude has **two independent ways not to interrupt**, and confusing them is why the PC used to prompt
constantly while the Mac almost never did: the **allow list** (pattern rules) and the **OS sandbox**
(`sandbox.enabled`, with `autoAllowBashIfSandboxed` auto-approving anything the sandbox itself contains).
The sandbox does not run on native Windows, which left the allow list as the entire fence on the PC —
the finding that produced SCC-376 and moved the PC's work into WSL2 / Ubuntu.

### 3.1 The settings tiers, in precedence order

1. **User (`~/.claude/settings.json`)** — the machine-level file. Since SCC-376 it is ONE portable file
   installed identically on the Mac and inside both Ubuntu distros: paths written `~/`, hooks guarded so
   an absent tool is a silent no-op, and no machine-absolute path anywhere. It carries `sandbox.enabled`,
   the sandbox filesystem boundaries and the broad allow rules. Its committed source of truth is
   [`claude-user-settings.portable.json`](../../_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/claude-user-settings.portable.json);
   install it with the one-liner in that lane's plan and compare the sha.
2. **Project tracked (`.claude/settings.json`)** — committed: hooks, `ask` rules, the worktree base ref,
   and the allow rules the whole team gets. This is the copy a fresh clone and the other machine see.
3. **Project local — `settings.local.json`, under the project's `.claude/`** — gitignored, machine-only, and **linked into every
   worktree** (see 3.3). Anything here dies at the machine boundary, so a rule that both machines need
   belongs in tier 2, not here.

> ⛔ A local file *overrides* the global one. A project whose `settings.local.json` omits
> `sandbox.enabled` / `autoAllowBashIfSandboxed` turns the sandbox off for that project even though the
> user file enables it — which reads exactly like "the sandbox stopped working".

### 3.2 What SCC-376 removed from these files, and why it stays removed

- **Every Windows-only spelling** — `\Scripts\` venv paths, `.exe` rules, `MSYS_NO_PATHCONV`, and the
  bare-`python` family (neither machine resolves bare `python`: the Mac has `python3`, and so does
  Ubuntu). A dead rule widens nothing, but it hides drift — the fence must read as what the machines run.
- **Every `Bash(git -C * <verb>:*)` rule.** A wildcard *before* the subcommand approves any option
  inserted at that position, and `git -c` / `--exec-path` there run arbitrary commands. `cd <abs> && git
  <verb>` is judged per piece and every verb is already allowed in that shape, so nothing legitimate got
  harder. Both removals are pinned by case **A6** in
  [`test_settings_allowlist.py`](../../.agents/scripts/tests/test_settings_allowlist.py) so a later
  "promote what got blocked" pass cannot quietly reverse them.
- **The interpreter-twin requirement** (case A3) was rewritten in the same commit: it demanded a bare
  `python` twin for every `python3` rule because the two machines used to disagree. They no longer do.

### 3.3 Worktrees inherit nothing by default

Claude reads its configuration from inside the worktree it is running in, and the machine-local files are
gitignored, so a fresh `.claude/worktrees/*` starts with no permissions and no sandbox policy — every
tool call prompts. [`link-worktree-assets.py`](../../.agents/scripts/link-worktree-assets.py) symlinks
the runtime assets in at creation: `node_modules`, `auth_keys`, `.venv`, `.env`, `.env.local`,
`settings.local.json`, `scratchpad-root`. Verify with
`python3 .agents/scripts/tests/test_link_worktree_assets.py --on-main`.

### 3.4 The cwd-escape guard and the scratchpad

[`guard-cwd-escape.py`](../../.agents/hooks/guard-cwd-escape.py) stops `cd` commands that leave the
workspace, because Claude's shell cwd resets to the primary repo root and a relative path then reads the
wrong tree. The session scratchpad is exempt so verification runs do not beg for approvals: on POSIX the
built-in root `/(?:private/)?tmp/claude-<uid>/` matches, and any machine whose scratchpad lives elsewhere
points at it with the machine-local `.claude/scratchpad-root` file. Generic escapes (`cd /tmp`, `cd ~`,
`cd ../other-repo`) stay guarded. Verify with
`python3 .agents/scripts/tests/test_cwd_escape_hook.py --on-main`.

### 3.5 Hooks run from `.agents/hooks/`, never a `.claude/` copy

Every hook is wired as `sh "$CLAUDE_PROJECT_DIR/.agents/hooks/run-hook.sh" .agents/hooks/<script>`
(SCC-300). `run-hook.sh` probes for an interpreter rather than naming one — the bug it exists to prevent
is five hooks exiting 127 in silence on a machine with `pwsh` but no `powershell`, `python3` but no
`python`. The duplicate `.claude/hooks/` directory is retired: the OS sandbox denies writes under
`.claude/hooks`, so a hook living there breaks `git merge` and `git checkout` outright.

### 3.6 Sandbox filesystem boundaries

`sandbox.filesystem.allowWrite` must name the repo, its `.git`, the worktrees root, `Projects/`, and the
temp directories — written `~/`-relative so ONE file serves both machines:

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "filesystem": {
      "allowWrite": [
        "~/Sudo_Hatter_Command",
        "~/Sudo_Hatter_Command/.git",
        "~/Sudo_Hatter_Command/.claude/worktrees",
        "~/Sudo_Hatter_Command/Projects",
        "/tmp",
        "/private/tmp"
      ]
    }
  }
}
```

**The unsandboxed-retry hatch is deliberately left OPEN** (operator ruling, 2026-09-02). A write refused
by the sandbox can be retried unsandboxed and auto-approved under `defaultMode: auto`. Closing it
(`allowUnsandboxedCommands: false`) trades a silent success for a silent agent *failure* unless the allow
list has first been measured wide enough against real workloads, and it never prompted anyone. Strict
mode stays available behind a flag in that lane's `portable_settings.py`, with a zero-refusal battery as
its entry condition.

**What the sandbox does on WSL2 / Ubuntu — measured 2026-09-03 (SCC-384), so nobody re-derives it.**
The boundaries above are exactly what the agent sees, and four consequences follow that look like
breakage the first time:

- **`~/.config` and `~/.npm/_cacache` are outside `allowWrite`.** So `npm install -g <anything>`
  fails with `EROFS: read-only file system` on the npm cache, `gcloud` (which writes its own
  `~/.config/gcloud`) fails or reports `ADC token failed`, and copying a credential into `~/.config`
  is refused with `Read-only file system`. Each of these is the hatch's intended case: the agent
  retries unsandboxed once, and the retry is auto-approved. It is not a reason to widen `allowWrite`
  to the home directory.
- **`$TMPDIR` is unset under the unsandboxed retry.** A redirect written `> $TMPDIR/out.txt` becomes
  `> /out.txt` and dies with `Permission denied`. Spell the scratchpad path out in full on a retry.
- **Denied paths are `/dev/null` bind-mounts, not absences.** The sandbox mounts a character device
  over every `denyWithinAllow` entry (`.claude/hooks`, `.claude/skills`, `~/.bashrc`, ...). Two
  visible effects: `git status` in the sandboxed shell shows phantom `?? .bash_profile`,
  `?? .claude/hooks` rows that vanish unsandboxed, and any git operation that must remove or replace
  one of those paths — `git reset --hard` touching `.claude/settings.json`, `git worktree prune` on
  `.git/worktrees/*` metadata — fails with `Device or resource busy`. `.git/config.lock` is one of
  the mounted paths too, so `git push -u` / `git branch --set-upstream-to` push fine and then report
  `could not lock config file ...: File exists` — the push happened, only the tracking line did not.
  Read `git status` from an unsandboxed call before believing a repo is dirty; use `--mixed` where
  `--hard` is refused.
- **`sudo` is never the agent's.** `apt`, `add-apt-repository`, anything under `/usr` — the operator
  runs those in the IDE's integrated terminal (it IS the Ubuntu shell; no restart of the IDE), with
  the *Linux* user password, not the Windows one. The kit lists every such line in one block:
  [`new_machine-migration-guide.md` §5](install_guides/new_machine-migration-guide.md).

### 3.7 A fresh clone has no local file, and that is felt immediately

`settings.local.json` is gitignored, so a clone starts without it: the worktree linker finds
nothing to link, and tool calls inside worktrees fail prefix matching and prompt repeatedly.
`.agents/scripts/new-project.ps1` (and `/smh-new-project`) seed it from the skeleton's OS template when
scaffolding. On an existing repo, copy the sibling project's file and correct the write boundaries.

---

## 3A. Antigravity — the deep dive (store, two rule types, absolute deny, the apply)

The Antigravity **extension** (`google.google-antigravity`, installed in VS Code on both machines; it
bundles the `agy` CLI, which is not on PATH and not what the operator drives) was reinstalled on
2026-09-03 after the Ubuntu move. The desktop IDE's retirement (SCC-349) stands; the platform's does
not — SCC-378 inverted that ticket. Everything below was measured on v1.1.0 / `agy` 1.1.25 that day.

### 3A.1 The store

`~/.gemini/config/config.json` → `userSettings.globalPermissionGrants`, a JSON object with `allow` and
`deny` arrays of rule strings. Per machine, like Zoo's globalState; unlike Zoo's it is a plain file with
no SQLite and no second writer we have measured, so the apply needs no "editor closed" refusal — a
window reload is what makes the extension re-read it. Every OTHER key in that object is machine-local
(`remoteControlHostname` names the machine) and the apply preserves them all.

The extension's own "always allow" click records a **prefix**, not the whole command — `unsandboxed(git
status)`, `unsandboxed(acli)` — which is why a fresh install accumulates a usable list by hand and why
that list is also the record of what the operator had to click through (`/smh-llm-approvals` reads it).

### 3A.2 Two rule types, and which one the click writes

| Rule | Governs | Written by |
|---|---|---|
| `command(X)` | **execution** — may this command run at all | the render, from the source |
| `unsandboxed(X)` | **escaping the sandbox** — may it run outside container isolation when sandbox mode is on | the "always allow" click, because the default (no `--sandbox`) makes every command an unsandboxed one |

A fresh install therefore fills the *escape* list and never the *execution* list — measured 2026-09-03:
59 `unsandboxed(...)` grants, 0 `command(...)`, 0 denies, and the operator approving essentially every
command. The render writes **both** types for every allow family, so the fence holds whether or not
`--sandbox` is ever used.

⛔ **Sandbox mode does NOT auto-approve.** Claude's `autoAllowBashIfSandboxed` lets a contained command
run without asking; Antigravity's documentation says the opposite in plain words — approval rules apply
unchanged inside the sandbox, which only changes *where* a command runs. So the allow list is the whole
fence here, exactly the position native Windows put Claude in before SCC-376, and `--sandbox` is not a
lever for interruptions.

### 3A.3 The matcher, exactly

Each whitespace-separated token of a rule is an **anchored regex** (`^(?:tok)$`) matched against the
command's leading tokens; a rule with more tokens than the command cannot match; the rest of the command
is free. Precedence is **strictly `Deny > Ask > Allow`** — a deny wins whatever else matches. Three
consequences the battery caught on day one, each of which Zoo's prefix matcher hides:

| Fact | Consequence |
|---|---|
| Deny is absolute | Zoo's "a longer allow beats the deny" re-allow trick does NOT port. Denies name the **target**: `git push origin --delete (main\|master)` blocks main and leaves `chore/` deletes legal; `git branch -D (main\|master\|develop)` likewise. Regex is case-sensitive, so `-D` and `-d` are different rules here (they are the same rule in Zoo) |
| Metacharacters must be escaped | `command(git add .)` means *git add any-single-character*. The render writes `git add \.`; the dot-dir re-allows Zoo needs (`git add .agents/`) are unnecessary here because `.agents/` does not match `^(?:\.)$` |
| Tokens are anchored, so flag CLUSTERS and attached spellings are one token | `-f` never matches `-fd`; `--git-dir` never matches `--git-dir=/x`. The render writes `git clean -[a-zA-Z]*[fdx][a-zA-Z]*` and `git --git-dir.*`. `git clean -n` stays approvable (no f/d/x) |

`env -u GITHUB_TOKEN git push --force` starts with the token `env`, so a `git push --force` deny does
not see it — every git/gh deny carries its `env -u GITHUB_TOKEN` twin, as in Zoo.

**Chains.** The vendor's page ([antigravity.google/docs/permissions](https://antigravity.google/docs/permissions/),
read 2026-09-03) documents the per-token rule and says nothing about `&&`, `;` or `|`. If the whole line
is matched, the house shape every door command takes — `cd <abs> && git <verb> …` (`command-shape.md`
rule 1) — begins with the allowed token `cd`, and no deny row can see past it. So the render writes a
second twin of **every** deny behind `cd .* && ` (the `house_twin_prefix` in the source): if the
extension reads the whole line, the twin denies the house shape; if it splits chains, the twin is a dead
row and the plain deny fires. Either way the fence holds for the shape agents are told to write. A chain
with a *different* head (`git status; rm -rf /`) is a residual (§7) until the live probe in the SCC-378
walkthrough's `## Your Actions` settles which way the extension reads a line.

Cluster classes are not only for `rm` and `git clean`: the push/branch/add/config denies are spelled the
same way (`git push -[a-zA-Z]*f[a-zA-Z]*`, `git push --force.*`, `git branch -[a-zA-Z]*[dD][a-zA-Z]*`,
`git add -[a-zA-Z]*[Au][a-zA-Z]*`, `git config (?!(--get|--list|-l)$).*`), and the targets Zoo leaves
legal by its longer allows are left legal here by a lookahead (`--delete (?!"?(chore|claude|epic)/).*`,
`HEAD:(?!epic/).*`). Found by the SCC-378 code review, which walked the mirror with `-fu`, `-Df`, `-Av`,
`--local core.hooksPath` and `--delete develop` and watched each auto-approve.

### 3A.4 Where the list comes from, and how it reaches the machine

Nothing is edited in `config.json` by hand. The source is `.agents/permissions/families.json`; the
render (`permission_render.py`, run by `/smh-sync-agents`) writes `.agents/permissions/antigravity.json`
beside Zoo's and Claude's lists; `antigravity_permissions_apply.py --apply` pushes that file's
`globalPermissionGrants` into the store (backing it up once as `config.json.scc-backup`), and `--status`
must read *in sync with tracked file*. The unified battery
(`tests/test_permission_parity.py`) proves the three rendered lists give the same verdict on the same
commands: destructive → deny, ceremony → allow, unknown tool → ask.

---
## 4. Where approvals live — every store, every surface

| Store | Path (Mac) | What it does |
|---|---|---|
| **Decision store** (the only one that decides) | `~/Library/Application Support/Code/User/globalStorage/state.vscdb` → SQLite `ItemTable` key `ZooCodeOrganization.zoo-code` → JSON `allowedCommands` / `deniedCommands` | What `lyi()` (the matcher) actually receives. UI edits write here. |
| Tracked workspace settings | [`.vscode/settings.json`](../../.vscode/settings.json) → `zoo-code.allowedCommands` / `zoo-code.deniedCommands` | **Source of truth in git.** Seeds the decision store (see §5), shown in the UI union, applied per machine by the script (§9). |
| VS Code USER settings (Global) | `~/Library/Application Support/Code/User/settings.json` | The UI mirrors its edits here. Never edit by hand; per machine, not tracked. |
| Master toggles | same state.vscdb JSON: `autoApprovalEnabled`, `alwaysAllowExecute` (+ the tiles: `alwaysAllowReadOnly/Write/ModeSwitch/Subtasks/Mcp`) | Both master keys must be `true` or no list is ever consulted. Set in Zoo's Auto-Approve panel, per machine. |

**PC paths:** `%APPDATA%\Code\User\globalStorage\state.vscdb` and `%APPDATA%\Code\User\settings.json`.
**VS Code profiles:** a non-default VS Code profile keeps its own `state.vscdb` under
`User/profiles/<id>/globalStorage/` — the apply script (§9) finds every copy that carries the Zoo key.
**The second seat (`code2`) has its own store.** The isolated VS Code instance launches with
`--user-data-dir ~/vscode-isolated`, so its Zoo state is `~/vscode-isolated/User/globalStorage/state.vscdb`
(PC: `%USERPROFILE%\vscode-isolated\User\globalStorage\state.vscdb`) — a store the apply script never
listed before SCC-376. **On the PC the stores stay on the Windows side:** Zoo runs inside the Ubuntu
distro (the workspace extension host), but the window keeps its globalState in the Windows
user-data-dir, so no `state.vscdb` exists in either distro (measured, SCC-376 Phase 4). The apply
script, run from Ubuntu, reaches both Windows stores through `/mnt/c`.

**There is no VS Code "master permissions" system.** VS Code itself never approves or denies
terminal commands — each agent extension carries its own machinery (§13). Editing VS Code settings
only matters where an extension declares and reads a key.

---

## 5. The seeding trap (why the tracked file is not enough)

Verified in v3.80.1 source, function by function:

- The approval decision (`Task.ask → getState() → myi()`) reads `allowedCommands` /
  `deniedCommands` from **globalState only**. It never consults `settings.json` at decision time.
- On **activation**, exactly one line seeds it:
  `globalState.get("allowedCommands") || globalState.update("allowedCommands", config)` — i.e. the
  tracked file is copied in **only when the state key does not exist at all** (first run ever).
  An empty list `[]` is truthy in JS, so even an emptied state never re-seeds.
- **`deniedCommands` has no seeding line at all.** Denies reach the decision store only via the
  UI, the import, or the apply script.
- The settings UI shows the **union** of state + settings file — so a file-only entry *looks*
  present in the panel and still decides nothing. This is the trap that burns a fresh machine.

**Consequence:** after ANY edit to the tracked lists, run the apply script (§9) on each machine.
Editing the file alone changes the display, not the behavior.

---

## 6. The matcher, exactly (v3.80.1 `lyi`/`Cil`/`syi`/`_$e`)

1. The command string is parsed into **pieces**: split on newlines and on `&&`, `||`, `;`, `|`
   — after masking quotes, `$VAR`, `${...}`, `$(...)`, redirections.
2. Each piece is matched **lowercased** against each list by **plain starts-with**. No wildcards,
   no regex, no word boundaries. The **longest** matching prefix wins when allow and deny both hit.
3. Verdict: any denied piece → **auto-deny** (Zoo refuses without asking); all pieces allowed →
   **auto-approve**; anything unmatched → **ask**.

Behaviors that follow (each verified by executing the real extracted code):

| Fact | Consequence |
|---|---|
| `git -C /path status` starts with `git -C`, not `git status` | Verb-level rules can never see through `-C`. The house shape is now `cd <abs> && git <verb>` — two pieces, both matchable. `git -C` and `git --git-dir` are DENIED so they cannot launder past verb denies under the broad `git ` allow. |
| Lowercasing: `git branch -D` ≡ `git branch -d` | You cannot allow the safe flag and deny the destructive one. Fence by **target** instead: deny `git branch -D` (blocks both), re-allow `git branch -d chore/` and `git branch -d claude/` (longer prefix wins). Same trick for `git push origin --delete chore/`. |
| A quoted payload or a **heredoc survives as ONE piece** | `python3 - <<'EOF' … EOF` and `python3 -c '…'` (even multi-line inside the quotes) auto-approve under `python3 `. Multi-line python needs no special casing. |
| **Backslash line-continuations are NOT joined** | The continuation lines become orphan pieces (`--outline …`) that match nothing → ask. Shape rule: one logical line per command. |
| A `$(…)` subshell body is scored as its own piece but **NOT re-split** on `&&` | `$(cd /tmp && rm -rf /)` is one piece starting `cd ` → it would auto-approve. Known residual (§7); shape rule bans `$( … && … )`. Top-level `cd /tmp && rm -rf /` splits fine and the `rm -rf` deny catches it. |
| A bare assignment `VAR=x` is its own piece; `VAR=$(body)` vanishes leaving only the body | Assignments cannot launder anything. The handful of variable names the doors print (`REPO=`, `BRANCH=`, …) are allowlisted; `VAR=$(cd … && git …)` approves via the body's `cd ` prefix. |
| `git add .` deny prefix-matches `git add .agents/…` | Our repo's paths start with dots. Re-allows one character longer (`git add .agents/` etc.) win over the deny; the bare sweep `git add .`/`git add ./` stays denied. |
| `2>&1` is masked; `> file` rides inside its piece | Redirections never block an otherwise-allowed command. |

---

## 7. The honest security model — what these lists are and are not

The lists are a **friction dial plus a fence against common destructive spellings — not a
sandbox.** Three residuals are structural and accepted, because the real protections live
elsewhere:

- **Interpreters are approve-anything.** `python3 `/`python ` are allowed (the whole toolkit runs
  on them), and a python one-liner can do anything a shell can. True for Claude Code too.
- **Subshell laundering** (§6): a compound inside `$( )` is scored as one piece.
- **Prefix blindness to late flags/paths:** `git worktree remove x --force`,
  `pwsh -NoProfile -File .agents/scripts/../../evil.ps1` — a prefix can't see past its own length.
  The same blindness in a different token order — `git push origin -d main`, `git push -d origin main`,
  `git push origin refs/heads/main`, `git restore --source=HEAD .`, `git checkout origin/main -- .` —
  is allowed on Zoo and Antigravity alike (measured by the SCC-378 review); adding those rows is a Zoo
  decision change and sits with the operator (that walkthrough's `## Your Actions`).
- **Antigravity and chains** (§3A.3): the house `cd <abs> && …` shape is fenced by the `cd .* && `
  deny twin; a chain with any other allowed head (`git status; rm -rf /`, `true && dd …`) is not, until
  the live probe says whether the extension reads a line whole or splits it.
- **Env-prefix assignments:** `MSG=hi rm -rf /` is ONE piece whose head matches the `MSG=` allow —
  the assignment allows exist for the doors' standalone `VAR=…` lines and cannot tell the two
  shapes apart. The shape law (§10) bans the env-prefix spelling; the test pins the behavior.

What actually guards the things that matter: the GitHub **`main-write-gate`** ruleset (merges to
`main` happen only through a green PR — no local terminal can do it), the **armed git hooks**
(commit-msg key/SOP gates, pre-push carrying-foreign-work net), **worktree isolation** per lane,
and the ceremony doors. The threat model here is *the model doing something dumb*, not an
adversary crafting escapes — an agent that WANTS to bypass the list already has python.

Two Zoo features to leave alone, and why:
- **`destructiveCommandGuardEnabled` stays OFF.** Verified in source: when ON, `myi()` returns
  approve **before consulting the lists at all** and defers to an external screening binary
  (`dcg` v0.7.7) with its own unknown rule set. It replaces our fence, not supplements it.
- **`zoo-code.autoImportSettingsPath`** imports a full settings export on activation — the export
  format **requires provider profiles, which carry API keys**, so it can never be a tracked
  channel. Per-machine manual import stays what it is; delete the export file after (it carries
  keys).

---

<!-- CANONICAL-LISTS:START - test_guide_currency parses between these two markers. -->

## 8. The canonical lists — and the reasoning per family

The source of truth is [`.vscode/settings.json`](../../.vscode/settings.json) (`zoo-code.*` keys),
tracked in git: **124 allow / 105 deny** entries. The design rule, in the operator's words
(2026-08-30): *denies are the absolute minimum — only things that would really cause damage.* And
one mechanic makes that minimum load-bearing: under a broad allow, an un-denied spelling does not
ask — it **auto-runs**. So the allows are broad working families, and every deny row names real
damage and never collides with a legitimate ceremony step (both properties enforced by
[test_zoo_permissions.py](../../.agents/scripts/tests/test_zoo_permissions.py): a 68-row
destructive battery must all deny, the 25-step ceremony set must all approve, on every suite run).

### ⛔ The store also has to be SHRUNK, and 2026-09-01 is why (SCC-369)

Growth is only half of it. Zoo's "always allow" click does not store the command you approved — it
stores the **fragments** its own splitter produced. By 2026-09-01 the Mac's store held **255 allow
entries against the tracked 112**, and reading all 143 store-only rows found three piles and no
policy in any of them. **Shell wreckage:** `do`, `done`, `}`, `for d in`, `{ echo`, `exit 1` — a
`for` loop somebody approved, shredded into tokens, plus `giast` and `giast status --short`, a typo
of `git status` permanently blessed. **Dead one-off literals:** rows naming
`story-24-6-chuck-rebuild`, a one-off pyrefly output file under `/tmp`, and `acli jira workitem view SCC-366`, from
work that closed weeks earlier and can never match again. And the pile that mattered — **bare
tokens that outrank the fence**: `rm`, `git`, `env`, `acli`. The deny list stops `rm -rf` and
`rm -r`, so bare `rm` in the allow list meant **`rm -f somefile` and `rm *.md` auto-ran with no
prompt**, and bare `env` walked around every `env -u GITHUB_TOKEN git …` deny row.

**The operator made the call, on the measurement.** Offered the choice between wiping only the four dangerous rows and a full reset, he first chose the narrow option; the cost of keeping the other 139 was then measured — `zoo_permissions_apply.py` has no surgical remove, so keeping them meant committing debris like `do`, `done` and `giast` into `.vscode/settings.json` as repo policy — and on that evidence he chose **"Full wipe — all 143"**. The agent measured; the operator named the disposition.

⚠️ **After the eight promotions the numbers move once, and this is why they differ.** One of the eight (`ln -s `) already existed in the store, so `--status` now reads **142 store-only and 7 tracked rows missing from the store**, not 143 and 8. Both describe the same reconciliation before the apply; after it, both lists read *in sync with tracked file*.

**The reconciliation was measured, not judged.** Of the 143, **101 were already covered** by a
tracked prefix; only 42 would newly prompt after a reset, and every one was debris, a typo, a dead
literal, or a **bare token whose useful form is already tracked with a trailing space** — the store
had `git`, the tracked file has `git `, and a real command (`git status`) starts with `git ` and
stays approved. Exactly eight rows were real, recurring and uncovered, and those were promoted into
the tracked file: `npx vitest `, `npm run `, `test -`, `sleep `, `ps aux`, `ln -s `, and the
two-machine venv twin `backend/.venv/bin/` + `backend/.venv/Scripts/`. `find ` was deliberately NOT
promoted — `find -delete` and `find -exec rm` are destructive and no deny row sees them.

⭐ **The wipe closed the `rm -f` hole by itself, with no deny-list change**, because the tracked file
carries no `rm` row at all. And it is the only direction that keeps the two machines equal: those
143 rows lived in one Mac's SQLite file and had never existed on the PC, which was already running
on the tracked list alone. Reset with `zoo_permissions_apply.py --apply` (VS Code fully quit); its
closing `--status` must read *in sync with tracked file* on **both** lists.

**Growing the allow list from what actually got blocked.** `/smh-llm-approvals` reads Zoo's own
thread store, keeps the asks Zoo genuinely stopped on (`autoApprovalDecision` null — see §6), and
shows the operator that list in chat. He names which he wants allowed; the agent adds those rows
here and runs §9's apply. **A row is only ever as wide as the command it came from** — the operator
reads real commands and picks, and nothing computes a "shortest prefix" on his behalf. That
restraint is this section's opening mechanic applied to list growth: under a broad allow an
un-denied spelling does not ask, it RUNS, so `n` would unblock `npx create-next-app` and silently
approve `npm publish`, `node evil.js` and `nc -l 4444` alongside it. Breadth is the decision, and
the decision is the operator's.

### The Windows rows left with the PC (SCC-376)

The PC now works inside WSL2 / Ubuntu, so the rows only a Windows shell could ever match — the
SCC-338 read verbs (`Get-ChildItem`, `dir`, `findstr`, …), the SCC-373 toolchain twins
(`backend\.venv\Scripts\`, `.venv\Scripts\ruff.exe check`, …), `set "JAVA_HOME=`, `where `, `type `
and bare `python ` — came out: **22 rows, by exact match, never by prefix** (`dir` is the head of
`dirname `, which stays). Three capabilities had ONLY a Windows spelling and gained their Unix row in
the same commit: `.venv/bin/python -m pytest`, `.venv/bin/ruff check`,
`firebase/tests/node_modules/.bin/firebase emulators:exec`. The refusals those two tickets recorded
still stand: `if exist `, `ForEach-Object`, `find ` and bare `del` are laundering prefixes and never
come back. A dead row widens nothing, but it hides drift — the fence must read as what the machines run.

**ALLOW families**

| Family | Entries | Why |
|---|---|---|
| Navigation | `cd ` | The pin that replaces `git -C` — every door command is `cd <abs> && …`, self-contained per call. |
| Git, broad | `git `, `env -u GITHUB_TOKEN git ` | Every read/write verb the flows use. The damage spellings are DENIED below and win or lose by prefix length exactly where intended. |
| GitHub CLI | `gh pr `, `gh run `, `env -u GITHUB_TOKEN gh pr `, `env -u GITHUB_TOKEN gh run ` | Open PRs, watch checks. `gh pr merge` denied — merges are the operator's click. `gh api` not allowed (arbitrary REST incl. merges). |
| Interpreters | `python3 ` | The toolkit and heredoc one-offs. One spelling since SCC-376: bare `python` resolves on neither machine. |
| PowerShell, scoped | `pwsh -NoProfile -File .agents/scripts/` | The sync generator. `-Command` is deliberately NOT allowed. |
| Jira | `acli jira workitem ` | Board reads/writes inside ceremonies (`delete` denied). |
| Read-only + fs helpers | bare `ls`/`pwd`/`true`/`date`/`head`/`sort`/`uniq`/`wc`/`cat`/`echo` (pipe tails run bare), the rest spaced: `tail `, `sed `, `grep `, `rg `, `diff `, `cp `, `mkdir `, `printf `, `awk `, `cut `, `tr `, `basename `, `dirname `, `readlink `, `file `, `stat `, `du `, `cmp `, `command -v `, `which `, `jq `, `touch ` | Claude-parity read/copy set. Trailing spaces where a bare entry would swallow a different binary (`tr` → `trap`, `tail` → `tailscale`). `find` is deliberately absent (`-delete`/`-exec rm` ride behind the prefix) — it asks. |
| Door variables | `REPO=`, `BRANCH=`, `EXPECTED_KEY=`, `BASE=`, `BEHIND=`, `HEAD_SHA=`, `PATHS=`, `VENV=`, `KEY=`, `MAIN=`, `WT=`, `W=`, `SCR=`, `SCRATCH=`, `EXT=`, `DB=`, `OUT=`, `MSG=`, `URL=`, `CODE=`, `E=`, `T=`, `D=`, `F=`, `R=`, `S=`, `P=`, `N=`, `L=`, `B=`, `A=`, `G=`, `M=`, `V=`, `X=` | The standalone assignments the doors print (their own pieces). Env-prefix laundering via these is the §7 residual; the shape law bans that spelling. |
| Dot-dir adds | `git add .agents/`, `git add .claude/`, `git add .vscode/`, `git add .roo/`, `git add .roomodes`, `git add .githooks/`, `git add .opencode/`, `git add .github/`, `git add .gemini/`, `git add .agent/` | One character longer than the `git add .` deny, so explicit dot-path staging works while the bare sweep stays dead. |
| Config reads | `git config --get `, `git config --list`, `git config -l` | Longer than the `git config` deny — reads work, writes refuse (a config write can disarm the hooks, §below). |
| Lane/epic prune re-allows | `git branch -d chore/`, `git branch -d claude/`, `git branch -d epic/` (+ quoted twins `git branch -d "chore/`, `git branch -d "claude/`, `git branch -d "epic/`), `git push origin --delete chore/`, `git push origin --delete claude/`, `git push origin --delete epic/` (+ quoted twins `git push origin --delete "chore/`, `git push origin --delete "claude/`, `git push origin --delete "epic/`, and env -u GITHUB_TOKEN twins of all six push forms) | The close ceremonies' own prune steps — longer than their denies, so they win ONLY for lane/epic branches, in both the quoted and unquoted spellings the doors print; `main` stays denied. Lowercasing makes `-D epic/…` ≡ `-d epic/…`: the epic-close door's forced delete rides the same re-allow by design. |
| Test toolchain (SCC-369 / SCC-373 / SCC-376) | `npx vitest `, `npm run `, `npm ci `, `node backend/tests/`, `test -`, `sleep `, `ps aux`, `ln -s `, `java -version`, `backend/.venv/bin/`, `.venv/bin/python -m pytest`, `.venv/bin/ruff check`, `firebase/tests/node_modules/.bin/firebase emulators:exec` | The gate suites and the AGY emulator tiers, Unix spelling only since SCC-376 (Java 17 and Node 22 live inside Ubuntu on the PC, natively on the Mac). `find ` stays out. |

**DENY families** (every `git `/`gh ` deny also exists as an `env -u GITHUB_TOKEN ` twin — generated,
enforced by the test — because the broad env-twin allow would otherwise bypass it)

| Family | Entries | Why |
|---|---|---|
| Filesystem | `rm -rf`, `rm -r`, `sudo`, `chmod -R 777`, `chown -R`, `dd if=`, `mkfs`, `del /s`, `rmdir /s`, `Remove-Item -Recurse` | Irreversible. Bare `rm <file>` stays unlisted → asks. |
| Outward git | `git push origin "main` (the quoted-target spelling of the flagship deny — quotes defeat prefixes, so the two main-push spellings are pinned; arbitrary quoting stays a documented residual, §7), `git push --force`, `git push -f`, `git push --force-with-lease`, `git push --mirror`, `git push --all`, `git push origin main`, `git push -u origin main`, `git push --set-upstream origin main`, `git push origin main:`, `git push origin HEAD:`, `git push origin +`, `git push origin :`, `git push --delete`, `git push origin --delete` | `main` is never an agent's; history rewrites never auto-run. Lane/epic deletes and the story-landing `git push origin HEAD:epic/` re-allowed above (longest-prefix beats the `HEAD:` deny — the close/kickoff doors land on epic branches with exactly that spelling). (The GitHub `main-write-gate` ruleset is the primary lock on `main`; these rows are the local echo.) |
| Work destruction | `git reset --hard`, `git clean -f`, `git clean -d`, `git clean -x`, `git clean --force`, `git branch -D`, `git branch -M`, `git rebase`, `git filter-branch`, `git reflog expire`, `git reflog delete`, `git update-ref`, `git gc --prune`, `git stash drop`, `git stash clear`, `git restore .`, `git checkout -- `, `git checkout .` | Each destroys committed or uncommitted work, or the recovery data for it. `-f`/`-d`/`-x`/`--force` leave the dry-run `git clean -n` approvable (the `-x`/`--force` escape spellings were verified auto-approving in the close-out review and denied). `update-ref` is denied whole: any spelling rewrites or deletes a ref. `git checkout main` is deliberately NOT denied — parking a checkout on main is a real ceremony step, and the damage (pushing main) is fenced elsewhere. |
| Reroute/disarm | `git remote remove`, `git remote rm`, `git remote rename`, `git remote set-url`, `git config` | A remote edit reroutes pushes silently; a config write can disarm the hooks (`core.hooksPath`). Config READS are re-allowed above. |
| Sweeps | `git add -A`, `git add .`, `git add -u`, `git add --all` | The git-policy ban — a sweep carries other sessions' work. |
| Launder shapes | `git -C`, `git --git-dir` | Under the broad `git ` allow these would bypass every verb deny (§6). Auto-denied: the agent gets an immediate refusal and rewrites to `cd … && git …`. (Lowercasing means `git -c` — config override — is denied by the same row.) |
| Outward tools | `gh pr merge`, `gh repo delete`, `gh release delete`, `acli jira workitem delete` | Merges are the operator's click; deletions are operator words. |

### 8.1 What the manifest does NOT contribute — the notification probe (SCC-355)

The same `package.json` read that produced the lists above answers a second question, so it is
recorded beside them rather than in a session artefact that nobody re-reads.

**Measured on v3.80.1:** the extension contributes **19 settings keys** and **20 commands**, and
**not one of them is a notification, a sound, or an event hook.** There is no `onDidX` contribution,
no notification setting, and nothing an external script can subscribe to.

That is a negative result, and it is load-bearing: it is why Zoo notification parity is a *watcher*
over the thread store rather than a hook, and why no amount of settings tuning will ever produce a
ping. Anyone who goes looking for the hook should find this paragraph before they spend the hour.

<!-- CANONICAL-LISTS:END -->

---

## 9. Applying the lists per machine — [`zoo_permissions_apply.py`](../../.agents/scripts/zoo_permissions_apply.py)

`python3 .agents/scripts/zoo_permissions_apply.py --status` (on the PC: from Ubuntu — the Windows
stores, the `code2` seat's included, are reached through `/mnt/c`) shows, for every
`state.vscdb` that carries the Zoo key: counts, master-toggle values, and drift vs the tracked
file. `--apply` writes the tracked lists into the decision store (leaving a one-time
`state.vscdb.scc-backup` beside each db). It **refuses while VS Code is
running** (VS Code flushes its own state on exit and would overwrite). Procedure, any time the
lists change:

1. Edit `zoo-code.allowedCommands` / `deniedCommands` in [`.vscode/settings.json`](../../.vscode/settings.json). Commit through a lane like any settings change.
2. Quit VS Code fully. Run the script with `--apply`. Reopen.
3. `--status` again — state and file must read identical.

New machine setup = clone, toggles on in Zoo's Auto-Approve panel (master + Read/Write/ModeSwitch/Subtasks tiles), then the same three steps.

---

## 10. The command-shape law for Zoo seats (mirrored in `command-shape.md` §Zoo)

- **One logical line per command.** No backslash continuations (orphan pieces → prompts).
- **`cd <abs path> && git <verb> …`** — never `git -C` (auto-denied by design). Every command
  line pins its own target; cwd resets between calls are irrelevant.
- **No shell loops** in terminal commands (`do rm …` shapes launder; iterate in python or repeat the call).
- **No `$( … && … )` compounds.** Plain `VAR=$(cd X && git …)` for the door-printed reads is fine.
- **Multi-line payloads go inside quotes or a heredoc** (one piece, §6) — or write the script with
  Zoo's file tools (auto-approved writes) and run `python3 <file>`.
- Prefer the door text verbatim — the doors are being kept in this shape by the suite.

---

## 11. The measured record (2026-08-30, real session of 551 commands, real extracted matcher)

| Configuration | Auto-approved |
|---|---|
| The 49/19 lists as set up by hand in the UI (before) | **34.1%** |
| Canonical lists, commands as historically written | **74.4%** |
| Canonical lists + doors rewritten to the §10 shape | **88.2%** |

Destructive battery: **68 commands, 0 auto-approved, 68 auto-denied.** Ceremony set: **25/25
auto-approved** (preflight, gates, receipt, flight event, PR create/checks, transition, prunes in
quoted AND unquoted spellings, epic-close branch delete, parking the checkout back on main).
Legit-read pins: `git clean -n`, `git config --get`, `git config --list` all auto-approve. The
remaining asks are one-off diagnostics plus the handful of door blocks still written as multi-line
`if`/loops (banned §10 shapes for seats; they prompt when copied verbatim) — which is the design:
rare things prompt, the pipeline runs.

Close-out review additions (same day, after the measurement): the battery grew to 76 rows, `mktemp` joined the allows (an assignment scores as its `$()` body, so `MSG=$(mktemp)` was asking), and the deny list to 103 with the verified escape spellings (`git clean -x`/`--force`, bare `git update-ref`, `git remote rename` + env twins) — deny-side only, so the approve rates above are unchanged; an ASK battery now pins the third tier (unknown tools keep asking).

---

## 12. Incident notes worth keeping

- **Zoo rewrites `.roomodes` through its own YAML writer** when project modes are touched in its
  UI (observed 2026-08-30: generated header stripped, em-dashes flattened to `-`, block scalars
  collapsed). Treat any hand/UI edit of `.roomodes` as dirt: regenerate with `/smh-sync-agents`;
  the suite's currency checks (test_zoo_team B-blocks) go red on the drift.
- The UI's Auto-Approve panel writes BOTH the decision store and USER settings — so panel edits
  diverge from the tracked file silently. `--status` shows the drift; re-apply after reconciling.
- **A "dirty" repo that is only dirty inside the sandbox** (2026-09-03): the `/dev/null` bind-mounts
  in §3.6 make `git status` list the denied paths as untracked. The same command unsandboxed shows a
  clean tree. Never sweep or `git add` on the strength of a sandboxed status.

---

## 13. Every surface side by side, and how a list grows

The table repeats §1's answer with the detail that only matters once you are changing something.
Claude and Zoo have their own sections above (§3 and §4 onward); these rows exist so no surface is
left un-named when someone asks "and what about that one?".

| Surface | Store | Matcher | Notes |
|---|---|---|---|
| **Claude Code** | [.claude/settings.json](../../.claude/settings.json) (tracked) + `settings.local.json` (per machine) + the portable user file | Pattern rules (`Bash(git status:*)` prefixes — the `git -C *` mid-wildcard rows left in SCC-376: a wildcard before the subcommand approves any option at that position), compound commands checked per segment | §3. Deny-less; unmatched goes to ask (or to auto mode's classifier); hard stops live in hooks + rules, and the OS sandbox is the second fence. |
| **Zoo Code** | VS Code globalState, two stores on the PC | lowercase starts-with prefix, per piece | §4 onward — most of this page. |
| **opencode** | its own config under `.opencode/` | WHOLE-string prefix, no per-piece split | **Outside `/smh-llm-approvals`** (SCC-354): a whole-string prefix unblocks exactly one invocation, so a list grown this way carries one row per command and stops being readable. Add rows by hand when a command is worth it. |
| **Codex** | `~/.codex/` config (`approval_policy` / sandbox), per machine | policy-level, not per-command lists | **Outside `/smh-llm-approvals`** (SCC-354): there is no per-command list to grow — the policy is the whole decision. |
| **Antigravity** | `~/.gemini/config/config.json` → `globalPermissionGrants`, per machine; rendered from the one source into `.agents/permissions/antigravity.json` | per-token anchored regex, Deny absolute (§3A) | LIVE again since 2026-09-03 (SCC-378) — the desktop IDE is gone (SCC-349); the VS Code extension is the platform. Its store is applied by `antigravity_permissions_apply.py`; it has the same two-fence shape as the others: find the decision store, track the source, script the apply. AGY's own allow rules ride AVCH-116 (the port of this ticket's shape) and AVCH-114 (the Zoo half), never a lobby ticket. |

### 13.0 Growing a list — the audit door

[`/smh-llm-approvals`](../../.agents/commands/smh-llm-approvals.md) covers both surfaces that keep
per-command lists. It reads the operator's recent Claude sessions and Zoo threads, shows him every
terminal command that stopped and waited for him, and — once he names the ones he wants allowed —
edits `.claude/settings.json` and this guide's `.vscode/settings.json` and runs §9's apply.

Zoo is the surface that needs it most. Claude Code puts a *don't ask again* button in its own
approval prompt, so its list grows while the operator works; Zoo has no such affordance, and §5's
seeding trap means the tracked file cannot fill the gap either. Claude still gets read, because
Claude Code cannot edit its own settings — the agent running the command does that edit.

The door proposes nothing and touches no deny list. The operator reads real commands and picks.

### 13.1 Notifications — the third surface, and the one Zoo does not have

Approvals are only half of "does the operator know". The other half is whether anything *tells* him
when a turn stops. Claude has had banners plus phone pushes since 2026-08-14; Zoo ran silent until
SCC-355, for the reason §8.1 measures — there is no hook to hang one on.

| Surface | How the operator is notified | Wiring |
|---|---|---|
| **Claude Code** | Notification + Stop hooks → `~/.claude/notify.sh` | `~/.claude/settings.json`, per machine |
| **Zoo Code** | [`zoo_notify.py`](../../.agents/scripts/zoo_notify.py) polls the thread store Zoo already writes | installed as a background service by [`zoo_notify_install.py --apply`](../../.agents/scripts/zoo_notify_install.py), once per machine; no hook exists |

**What it fires on, exactly.** Two events: an **approval-ask** and a **turn end**.

- An ask pages him only when Zoo's own `autoApprovalDecision` is **null** — the matcher had no
  opinion, so it asked. An ask Zoo auto-approved never interrupted anyone (34 of 53 on the two
  threads measured) and must not raise a banner.
- A **turn end** pages him unconditionally. It is a turn finishing, not a decision, so the
  `autoApprovalDecision` filter does not apply to it and never did — the first cut of the SOP row
  said "only when `autoApprovalDecision` is null" without that carve-out, which was wrong as
  written.
- ⛔ **`partial` is consulted for a `say` and NEVER for an `ask`.** It looks like a streaming
  artefact and it is not: Zoo clears that flag when its own matcher auto-approves and leaves it
  standing when the operator has to answer, so an ask flagged `partial` is the operator-facing ask
  itself. Ten asks in the live store carry `partial` **and** `isAnswered` together — Zoo stamped the
  answer on top and never cleared the flag. Filtering on it discards 81% of the `tool` asks that
  want him, `tool` being the subagent launch where Zoo sits blocked longest.
- Every **other** ask type pages him. The filter is a **deny-list**, not an allow-list, and that is
  deliberate: `auto_approval_max_req_reached` is the ask Zoo raises *because* auto-approval hit its
  cap and he must step in, and an allow-list built from a two-thread sample dropped it silently.
  A notifier fails **open** — a spurious banner costs a glance, a missed one costs the feature.

**The store it watches** is the same `globalStorage` tree §4 maps, plus every named profile, and it
honours `zoo-code.customStoragePath` when that setting is set — read from user settings and from
each profile's settings, the same two places §9's apply script looks.

### 13.2 Installing it, per machine

The watcher is a foreground poll loop, so something has to run it. That something is a service, not
an instruction — an install step a human must remember is not a delivery mechanism, and the first
cut of this feature was silent on the Mac from the day it landed precisely because nobody ran it.

```bash
python3 .agents/scripts/zoo_notify_install.py --apply     # PC: python
python3 .agents/scripts/zoo_notify_install.py             # status, read-only, the default
python3 .agents/scripts/zoo_notify.py --self-test         # prove both channels in five seconds
```

`--apply` registers a launchd agent on the Mac (`RunAtLoad` + `KeepAlive`, so it starts at login and
restarts if it dies) and a `pythonw` `.cmd` in the Startup folder on the PC. Two things it carries
that a naive copy would lose: `NTFY_TOPIC`, because launchd sources no shell profile and the topic
lives in `~/.zshrc`; and a `PATH` reaching `/opt/homebrew/bin`, because launchd's default `PATH`
cannot see `terminal-notifier` — without it the banner half dies while the push half keeps working,
which is harder to diagnose than total silence. Logs land in `~/Library/Logs/zoo-notify.log`.

⭐ **`--status` checks more than "loaded".** The job embeds this repo's absolute path, so moving or
renaming the repo leaves an agent that `launchctl list` still shows and that does nothing. Status
reads the recorded path back and checks it on disk; `--apply` again is the fix.

⭐ **A restart while Zoo is already waiting still pages you.** The first sweep is otherwise silent —
Zoo keeps every task directory forever and a finished thread's tail stays an ask on disk, so a cold
start would page once per historical thread. The exception is narrow: an unanswered ask whose thread
was written in the last five minutes. `--prime-window 0` restores total silence.

**Update procedure for this page:** change the lists → update §8's tables in the same commit →
run the suite (the fixtures pin §8 against the tracked file) → apply per machine (§9). The
sop-currency gate will demand the SOP row when a usage surface changes.

---

## 14. Verifying any of this

| what | command |
|---|---|
| the Zoo lists behave (destructive battery denies, ceremony approves, guide counts current) | `python3 .agents/scripts/tests/test_zoo_permissions.py` |
| the tracked Claude + Zoo lists travel, with the SCC-376 removals pinned | `python3 .agents/scripts/tests/test_settings_allowlist.py` |
| worktrees inherit the local settings | `python3 .agents/scripts/tests/test_link_worktree_assets.py --on-main` |
| the cwd guard allows the scratchpad and blocks real escapes | `python3 .agents/scripts/tests/test_cwd_escape_hook.py --on-main` |
| everything at once | `python3 .agents/scripts/tests/run_all.py` |

Run them **bare** — a piped gate hides its exit code.
