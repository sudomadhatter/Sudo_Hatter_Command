# Zoo Code Auto-Approve — the permissions guide

**What this page is.** The one reference for how terminal-command auto-approval actually works in
Zoo Code, why it used to prompt you fifty times a session, the canonical allow/deny lists, and the
exact procedure to change them without starting a new investigation. Everything in here was
verified by reading and executing Zoo Code v3.80.1's own compiled source (the matcher was
extracted verbatim and run against a real 551-command session), not inferred from docs.
Sibling surfaces (Claude Code, Antigravity) are covered at the bottom so all three agents can be
tuned to the same level. SCC-351.

---

## 1. The one-paragraph story

Zoo only auto-runs a terminal command when every piece of it starts with an entry on the ALLOW
list, and refuses it when any piece starts with an entry on the DENY list. Everything else asks
you. The pain had three causes: **(1)** the lists you edit in `.vscode/settings.json` are not the
lists Zoo decides with (they only seed it once — §3); **(2)** Zoo's matcher is a plain
starts-with test, so the house's own `git -C <path>` habit could never match a `git status`
allow (§4); **(3)** a handful of safe families (`cd`, `git push`, `gh pr`, `acli`, heredoc
python) were simply missing. The fix is one tracked list (§6), one apply script (§7), and a
command-shape law for the seats (§8). Measured on a real session: **34% auto-approved before,
~87% after** (§9).

---

## 2. Where approvals live — every store, every surface

| Store | Path (Mac) | What it does |
|---|---|---|
| **Decision store** (the only one that decides) | `~/Library/Application Support/Code/User/globalStorage/state.vscdb` → SQLite `ItemTable` key `ZooCodeOrganization.zoo-code` → JSON `allowedCommands` / `deniedCommands` | What `lyi()` (the matcher) actually receives. UI edits write here. |
| Tracked workspace settings | [`.vscode/settings.json`](../../.vscode/settings.json) → `zoo-code.allowedCommands` / `zoo-code.deniedCommands` | **Source of truth in git.** Seeds the decision store (see §3), shown in the UI union, applied per machine by the script (§7). |
| VS Code USER settings (Global) | `~/Library/Application Support/Code/User/settings.json` | The UI mirrors its edits here. Never edit by hand; per machine, not tracked. |
| Master toggles | same state.vscdb JSON: `autoApprovalEnabled`, `alwaysAllowExecute` (+ the tiles: `alwaysAllowReadOnly/Write/ModeSwitch/Subtasks/Mcp`) | Both master keys must be `true` or no list is ever consulted. Set in Zoo's Auto-Approve panel, per machine. |

**PC paths:** `%APPDATA%\Code\User\globalStorage\state.vscdb` and `%APPDATA%\Code\User\settings.json`.
**VS Code profiles:** a non-default VS Code profile keeps its own `state.vscdb` under
`User/profiles/<id>/globalStorage/` — the apply script (§7) finds every copy that carries the Zoo key.

**There is no VS Code "master permissions" system.** VS Code itself never approves or denies
terminal commands — each agent extension carries its own machinery (§11). Editing VS Code settings
only matters where an extension declares and reads a key.

## 3. The seeding trap (why the tracked file is not enough)

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

**Consequence:** after ANY edit to the tracked lists, run the apply script (§7) on each machine.
Editing the file alone changes the display, not the behavior.

## 4. The matcher, exactly (v3.80.1 `lyi`/`Cil`/`syi`/`_$e`)

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
| A `$(…)` subshell body is scored as its own piece but **NOT re-split** on `&&` | `$(cd /tmp && rm -rf /)` is one piece starting `cd ` → it would auto-approve. Known residual (§5); shape rule bans `$( … && … )`. Top-level `cd /tmp && rm -rf /` splits fine and the `rm -rf` deny catches it. |
| A bare assignment `VAR=x` is its own piece; `VAR=$(body)` vanishes leaving only the body | Assignments cannot launder anything. The handful of variable names the doors print (`REPO=`, `BRANCH=`, …) are allowlisted; `VAR=$(cd … && git …)` approves via the body's `cd ` prefix. |
| `git add .` deny prefix-matches `git add .agents/…` | Our repo's paths start with dots. Re-allows one character longer (`git add .agents/` etc.) win over the deny; the bare sweep `git add .`/`git add ./` stays denied. |
| `2>&1` is masked; `> file` rides inside its piece | Redirections never block an otherwise-allowed command. |

## 5. The honest security model — what these lists are and are not

The lists are a **friction dial plus a fence against common destructive spellings — not a
sandbox.** Three residuals are structural and accepted, because the real protections live
elsewhere:

- **Interpreters are approve-anything.** `python3 `/`python ` are allowed (the whole toolkit runs
  on them), and a python one-liner can do anything a shell can. True for Claude Code too.
- **Subshell laundering** (§4): a compound inside `$( )` is scored as one piece.
- **Prefix blindness to late flags/paths:** `git worktree remove x --force`,
  `pwsh -NoProfile -File .agents/scripts/../../evil.ps1` — a prefix can't see past its own length.

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

## 6. The canonical lists — and the reasoning per family

The source of truth is [`.vscode/settings.json`](../../.vscode/settings.json) (`zoo-code.*` keys),
tracked in git. The design: **broad allow on the working families + enumerated denies on the
irreversible/outward spellings + longer re-allows for the lane-scoped exceptions.** A test
([test_zoo_permissions.py](../../.agents/scripts/tests/test_zoo_permissions.py)) re-runs the
destructive battery and the ceremony set against these lists on every suite run, so a bad edit
goes red before it ships.

**ALLOW families**

| Family | Entries | Why |
|---|---|---|
| Navigation | `cd ` | The pin that replaces `git -C` — every door command is `cd <abs> && …`, self-contained per call. |
| Git, broad | `git `, `env -u GITHUB_TOKEN git ` | Every read/write verb the flows use (status, diff, log, fetch, add <paths>, commit, push, worktree, stash list…). The dangerous spellings are DENIED below and win by length where they overlap. |
| Interpreters | `python3 `, `python ` | The toolkit (`.agents/scripts/*`, tests, heredoc one-offs). Both spellings per the two-machines law. |
| PowerShell, scoped | `pwsh -NoProfile -File .agents/scripts/` | The sync generator. `-Command` is deliberately NOT allowed. |
| Jira | `acli jira workitem ` | Board reads/writes inside ceremonies (`delete` denied). |
| GitHub CLI | `gh pr `, `gh run ` | Open PRs, watch checks. `gh pr merge` denied — merges are the operator's click. `gh api` not allowed (arbitrary REST incl. merges). |
| Read-only + fs helpers | `ls cat head tail sed grep rg find wc diff cp mkdir echo printf sort uniq awk cut tr basename dirname readlink file stat du cmp command -v which jq touch date pwd true` | Claude-parity read/copy set. |
| Door variables | `REPO= BRANCH= EXPECTED_KEY= BASE= BEHIND= HEAD_SHA= PATHS= VENV= KEY= MAIN= WT= W= SCR= EXT= DB= OUT= MSG= URL= CODE= T= D= F= R= S= P= N= L= B= A= G= M= V= X=` | The assignments the doors print. An assignment is its own piece — it cannot launder (§4). |
| Dot-dir adds | `git add .agents/` `.claude/` `.vscode/` `.roo/` `.roomodes` `.githooks/` `.opencode/` `.github/` `.gemini/` `.agent/` | One character longer than the `git add .` deny, so explicit dot-path staging works while the bare sweep stays dead. |
| Lane-scoped re-allows | `git branch -d chore/`, `git branch -d claude/`, `git push origin --delete chore/`, `git push origin --delete claude/` (+ `env -u GITHUB_TOKEN` twins) | The close-out ceremony's own prune steps — longer than their denies, so they win only for lane branches; `main`/`epic/*` stay denied. |

**DENY families**

| Family | Entries | Why |
|---|---|---|
| Filesystem | `rm -rf`, `rm -r`, `sudo`, `chmod -R 777`, `chown -R`, `dd if=`, `mkfs`, `del /s`, `rmdir /s`, `Remove-Item -Recurse` | Irreversible. Bare `rm <file>` stays unlisted → asks. |
| Outward git | `git push --force`, `-f`, `--force-with-lease`, `--mirror`, `--all`, `git push origin main`, `-u origin main`, `origin main:`, `origin HEAD:`, `origin +`, `--delete`, `origin --delete` | `main` is never an agent's; history rewrites never auto-run. Lane-scoped deletes re-allowed above. |
| History/board destruction | `git reset --hard`, `git clean`, `git checkout main`, `git switch main`, `git branch -D`, `git branch -M`, `git rebase`, `git filter-branch`, `git reflog expire/delete`, `git update-ref -d`, `git gc --prune=now`, `git stash drop/clear`, `git remote remove/rm/set-url` | Each can destroy work or reroute pushes silently. |
| Sweeps | `git add -A`, `git add .`, `git add -u`, `git add --all` | The git-policy ban — a sweep carries other sessions' work. |
| Launder shapes | `git -C`, `git --git-dir` (+ `env -u GITHUB_TOKEN` twins) | Under a broad `git ` allow these would bypass every verb deny (§4). Auto-denied: the agent gets an immediate refusal and rewrites to `cd … && git …`. |
| Outward tools | `gh pr merge`, `gh repo delete`, `gh release delete`, `acli jira workitem delete` | Merges are the operator's click; deletions are operator words. |

## 7. Applying the lists per machine — `zoo_permissions_apply.py`

`python3 .agents/scripts/zoo_permissions_apply.py --status` (PC: `python`) shows, for every
`state.vscdb` that carries the Zoo key: counts, master-toggle values, and drift vs the tracked
file. `--apply` writes the tracked lists into the decision store. It **refuses while VS Code is
running** (VS Code flushes its own state on exit and would overwrite). Procedure, any time the
lists change:

1. Edit `zoo-code.allowedCommands` / `deniedCommands` in [`.vscode/settings.json`](../../.vscode/settings.json). Commit through a lane like any settings change.
2. Quit VS Code fully. Run the script with `--apply`. Reopen.
3. `--status` again — state and file must read identical.

New machine setup = clone, toggles on in Zoo's Auto-Approve panel (master + Read/Write/ModeSwitch/Subtasks tiles), then the same three steps.

## 8. The command-shape law for Zoo seats (mirrored in `command-shape.md` §Zoo)

- **One logical line per command.** No backslash continuations (orphan pieces → prompts).
- **`cd <abs path> && git <verb> …`** — never `git -C` (auto-denied by design). Every command
  line pins its own target; cwd resets between calls are irrelevant.
- **No shell loops** in terminal commands (`do rm …` shapes launder; iterate in python or repeat the call).
- **No `$( … && … )` compounds.** Plain `VAR=$(cd X && git …)` for the door-printed reads is fine.
- **Multi-line payloads go inside quotes or a heredoc** (one piece, §4) — or write the script with
  Zoo's file tools (auto-approved writes) and run `python3 <file>`.
- Prefer the door text verbatim — the doors are being kept in this shape by the suite.

## 9. The measured record (2026-08-30, real session of 551 commands, real extracted matcher)

| Configuration | Auto-approved |
|---|---|
| The 49/19 lists as set up by hand in the UI (before) | **34%** |
| Canonical lists, commands as historically written | **73%** |
| Canonical lists + doors rewritten to the §8 shape | **~87%** |

Destructive battery: **46 commands, 0 auto-approved** (45 denied, 1 ask). Ceremony set: **20/20
auto-approved** (preflight, gates, receipt, flight event, PR create/checks, transition, prune).
Residual asks are one-off diagnostics — which is the design: rare things prompt, the pipeline runs.

## 10. Incident notes worth keeping

- **Zoo rewrites `.roomodes` through its own YAML writer** when project modes are touched in its
  UI (observed 2026-08-30: generated header stripped, em-dashes flattened to `-`, block scalars
  collapsed). Treat any hand/UI edit of `.roomodes` as dirt: regenerate with `/smh-sync-agents`;
  the suite's currency checks (test_zoo_team B-blocks) go red on the drift.
- The UI's Auto-Approve panel writes BOTH the decision store and USER settings — so panel edits
  diverge from the tracked file silently. `--status` shows the drift; re-apply after reconciling.

## 11. The other two surfaces (so all agents ride at the same level)

| Surface | Store | Matcher | Notes |
|---|---|---|---|
| **Claude Code** | [.claude/settings.json](../../.claude/settings.json) (tracked) + `.claude/settings.local.json` (per machine) | Pattern rules: `Bash(git -C * status:*)` mid-wildcards, compound commands checked per segment | Already at target level. Deny-less; unmatched → ask; hard stops live in hooks + rules. |
| **Zoo Code** | this guide | lowercase starts-with prefix, per piece | The subject of this page. |
| **Antigravity** | its own per-machine allowlist config (AGY carries 49 local allow rules) | its own | Promoting AGY's rules into tracked settings is the standing AVCH-ticket decision (SCC-346 hand-back). Same principle applies: find the decision store, track the source, script the apply. |

**Update procedure for this page:** change the lists → update §6's tables in the same commit →
run the suite (the fixtures pin §6 against the tracked file) → apply per machine (§7). The
sop-currency gate will demand the SOP row when a usage surface changes.
