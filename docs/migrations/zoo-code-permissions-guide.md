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
you. The pain had three causes: **(1)** the lists you edit in [`.vscode/settings.json`](../../.vscode/settings.json) are not the
lists Zoo decides with (they only seed it once — §3); **(2)** Zoo's matcher is a plain
starts-with test, so the house's own `git -C <path>` habit could never match a `git status`
allow (§4); **(3)** a handful of safe families (`cd`, `git push`, `gh pr`, `acli`, heredoc
python) were simply missing. The fix is one tracked list (§6), one apply script (§7), and a
command-shape law for the seats (§8). Measured on a real session: **34.1% auto-approved before,
88.2% after** (§9).

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
**The second seat (`code2`) has its own store.** The isolated VS Code instance launches with
`--user-data-dir ~/vscode-isolated`, so its Zoo state is `~/vscode-isolated/User/globalStorage/state.vscdb`
(PC: `%USERPROFILE%\vscode-isolated\User\globalStorage\state.vscdb`) — a store the apply script never
listed before SCC-376. **On the PC the stores stay on the Windows side:** Zoo runs inside the Ubuntu
distro (the workspace extension host), but the window keeps its globalState in the Windows
user-data-dir, so no `state.vscdb` exists in either distro (measured, SCC-376 Phase 4). The apply
script, run from Ubuntu, reaches both Windows stores through `/mnt/c`.

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
- **Env-prefix assignments:** `MSG=hi rm -rf /` is ONE piece whose head matches the `MSG=` allow —
  the assignment allows exist for the doors' standalone `VAR=…` lines and cannot tell the two
  shapes apart. The shape law (§8) bans the env-prefix spelling; the test pins the behavior.

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
`story-24-6-chuck-rebuild`, `/tmp/avch101-pyrefly.txt` and `acli jira workitem view SCC-366`, from
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
thread store, keeps the asks Zoo genuinely stopped on (`autoApprovalDecision` null — see §4), and
shows the operator that list in chat. He names which he wants allowed; the agent adds those rows
here and runs §7's apply. **A row is only ever as wide as the command it came from** — the operator
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
| Door variables | `REPO=`, `BRANCH=`, `EXPECTED_KEY=`, `BASE=`, `BEHIND=`, `HEAD_SHA=`, `PATHS=`, `VENV=`, `KEY=`, `MAIN=`, `WT=`, `W=`, `SCR=`, `SCRATCH=`, `EXT=`, `DB=`, `OUT=`, `MSG=`, `URL=`, `CODE=`, `E=`, `T=`, `D=`, `F=`, `R=`, `S=`, `P=`, `N=`, `L=`, `B=`, `A=`, `G=`, `M=`, `V=`, `X=` | The standalone assignments the doors print (their own pieces). Env-prefix laundering via these is the §5 residual; the shape law bans that spelling. |
| Dot-dir adds | `git add .agents/`, `git add .claude/`, `git add .vscode/`, `git add .roo/`, `git add .roomodes`, `git add .githooks/`, `git add .opencode/`, `git add .github/`, `git add .gemini/`, `git add .agent/` | One character longer than the `git add .` deny, so explicit dot-path staging works while the bare sweep stays dead. |
| Config reads | `git config --get `, `git config --list`, `git config -l` | Longer than the `git config` deny — reads work, writes refuse (a config write can disarm the hooks, §below). |
| Lane/epic prune re-allows | `git branch -d chore/`, `git branch -d claude/`, `git branch -d epic/` (+ quoted twins `git branch -d "chore/`, `git branch -d "claude/`, `git branch -d "epic/`), `git push origin --delete chore/`, `git push origin --delete claude/`, `git push origin --delete epic/` (+ quoted twins `git push origin --delete "chore/`, `git push origin --delete "claude/`, `git push origin --delete "epic/`, and env -u GITHUB_TOKEN twins of all six push forms) | The close ceremonies' own prune steps — longer than their denies, so they win ONLY for lane/epic branches, in both the quoted and unquoted spellings the doors print; `main` stays denied. Lowercasing makes `-D epic/…` ≡ `-d epic/…`: the epic-close door's forced delete rides the same re-allow by design. |
| Test toolchain (SCC-369 / SCC-373 / SCC-376) | `npx vitest `, `npm run `, `npm ci `, `node backend/tests/`, `test -`, `sleep `, `ps aux`, `ln -s `, `java -version`, `backend/.venv/bin/`, `.venv/bin/python -m pytest`, `.venv/bin/ruff check`, `firebase/tests/node_modules/.bin/firebase emulators:exec` | The gate suites and the AGY emulator tiers, Unix spelling only since SCC-376 (Java 17 and Node 22 live inside Ubuntu on the PC, natively on the Mac). `find ` stays out. |

**DENY families** (every `git `/`gh ` deny also exists as an `env -u GITHUB_TOKEN ` twin — generated,
enforced by the test — because the broad env-twin allow would otherwise bypass it)

| Family | Entries | Why |
|---|---|---|
| Filesystem | `rm -rf`, `rm -r`, `sudo`, `chmod -R 777`, `chown -R`, `dd if=`, `mkfs`, `del /s`, `rmdir /s`, `Remove-Item -Recurse` | Irreversible. Bare `rm <file>` stays unlisted → asks. |
| Outward git | `git push origin "main` (the quoted-target spelling of the flagship deny — quotes defeat prefixes, so the two main-push spellings are pinned; arbitrary quoting stays a documented residual, §5), `git push --force`, `git push -f`, `git push --force-with-lease`, `git push --mirror`, `git push --all`, `git push origin main`, `git push -u origin main`, `git push --set-upstream origin main`, `git push origin main:`, `git push origin HEAD:`, `git push origin +`, `git push origin :`, `git push --delete`, `git push origin --delete` | `main` is never an agent's; history rewrites never auto-run. Lane/epic deletes and the story-landing `git push origin HEAD:epic/` re-allowed above (longest-prefix beats the `HEAD:` deny — the close/kickoff doors land on epic branches with exactly that spelling). (The GitHub `main-write-gate` ruleset is the primary lock on `main`; these rows are the local echo.) |
| Work destruction | `git reset --hard`, `git clean -f`, `git clean -d`, `git clean -x`, `git clean --force`, `git branch -D`, `git branch -M`, `git rebase`, `git filter-branch`, `git reflog expire`, `git reflog delete`, `git update-ref`, `git gc --prune`, `git stash drop`, `git stash clear`, `git restore .`, `git checkout -- `, `git checkout .` | Each destroys committed or uncommitted work, or the recovery data for it. `-f`/`-d`/`-x`/`--force` leave the dry-run `git clean -n` approvable (the `-x`/`--force` escape spellings were verified auto-approving in the close-out review and denied). `update-ref` is denied whole: any spelling rewrites or deletes a ref. `git checkout main` is deliberately NOT denied — parking a checkout on main is a real ceremony step, and the damage (pushing main) is fenced elsewhere. |
| Reroute/disarm | `git remote remove`, `git remote rm`, `git remote rename`, `git remote set-url`, `git config` | A remote edit reroutes pushes silently; a config write can disarm the hooks (`core.hooksPath`). Config READS are re-allowed above. |
| Sweeps | `git add -A`, `git add .`, `git add -u`, `git add --all` | The git-policy ban — a sweep carries other sessions' work. |
| Launder shapes | `git -C`, `git --git-dir` | Under the broad `git ` allow these would bypass every verb deny (§4). Auto-denied: the agent gets an immediate refusal and rewrites to `cd … && git …`. (Lowercasing means `git -c` — config override — is denied by the same row.) |
| Outward tools | `gh pr merge`, `gh repo delete`, `gh release delete`, `acli jira workitem delete` | Merges are the operator's click; deletions are operator words. |

### 6.1 What the manifest does NOT contribute — the notification probe (SCC-355)

The same `package.json` read that produced the lists above answers a second question, so it is
recorded beside them rather than in a session artefact that nobody re-reads.

**Measured on v3.80.1:** the extension contributes **19 settings keys** and **20 commands**, and
**not one of them is a notification, a sound, or an event hook.** There is no `onDidX` contribution,
no notification setting, and nothing an external script can subscribe to.

That is a negative result, and it is load-bearing: it is why Zoo notification parity is a *watcher*
over the thread store rather than a hook, and why no amount of settings tuning will ever produce a
ping. Anyone who goes looking for the hook should find this paragraph before they spend the hour.

## 7. Applying the lists per machine — [`zoo_permissions_apply.py`](../../.agents/scripts/zoo_permissions_apply.py)

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
| The 49/19 lists as set up by hand in the UI (before) | **34.1%** |
| Canonical lists, commands as historically written | **74.4%** |
| Canonical lists + doors rewritten to the §8 shape | **88.2%** |

Destructive battery: **68 commands, 0 auto-approved, 68 auto-denied.** Ceremony set: **25/25
auto-approved** (preflight, gates, receipt, flight event, PR create/checks, transition, prunes in
quoted AND unquoted spellings, epic-close branch delete, parking the checkout back on main).
Legit-read pins: `git clean -n`, `git config --get`, `git config --list` all auto-approve. The
remaining asks are one-off diagnostics plus the handful of door blocks still written as multi-line
`if`/loops (banned §8 shapes for seats; they prompt when copied verbatim) — which is the design:
rare things prompt, the pipeline runs.

Close-out review additions (same day, after the measurement): the battery grew to 76 rows, `mktemp` joined the allows (an assignment scores as its `$()` body, so `MSG=$(mktemp)` was asking), and the deny list to 103 with the verified escape spellings (`git clean -x`/`--force`, bare `git update-ref`, `git remote rename` + env twins) — deny-side only, so the approve rates above are unchanged; an ASK battery now pins the third tier (unknown tools keep asking).

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
| **Claude Code** | [.claude/settings.json](../../.claude/settings.json) (tracked) + `.claude/settings.local.json` (per machine) | Pattern rules (`Bash(git status:*)` prefixes — the `git -C *` mid-wildcard rows left in SCC-376: a wildcard before the subcommand approves any option at that position), compound commands checked per segment | Already at target level. Deny-less; unmatched → ask; hard stops live in hooks + rules. |
| **Zoo Code** | this guide | lowercase starts-with prefix, per piece | The subject of this page. |
| **opencode** | its own config under `.opencode/` | WHOLE-string prefix, no per-piece split | **Outside `/smh-llm-approvals`** (SCC-354): a whole-string prefix unblocks exactly one invocation, so a list grown this way carries one row per command and stops being readable. Add rows by hand when a command is worth it. |
| **Codex** | `~/.codex/` config (`approval_policy` / sandbox), per machine | policy-level, not per-command lists | **Outside `/smh-llm-approvals`** (SCC-354): there is no per-command list to grow — the policy is the whole decision. |
| **Antigravity** | its own per-machine allowlist config (AGY carries 49 local allow rules) | its own | Promoting AGY's rules into tracked settings is the standing AVCH-ticket decision (SCC-346 hand-back). Same principle applies: find the decision store, track the source, script the apply. |

### 11.0 Growing a list — the audit door

[`/smh-llm-approvals`](../../.agents/commands/smh-llm-approvals.md) covers both surfaces that keep
per-command lists. It reads the operator's recent Claude sessions and Zoo threads, shows him every
terminal command that stopped and waited for him, and — once he names the ones he wants allowed —
edits `.claude/settings.json` and this guide's `.vscode/settings.json` and runs §7's apply.

Zoo is the surface that needs it most. Claude Code puts a *don't ask again* button in its own
approval prompt, so its list grows while the operator works; Zoo has no such affordance, and §3's
seeding trap means the tracked file cannot fill the gap either. Claude still gets read, because
Claude Code cannot edit its own settings — the agent running the command does that edit.

The door proposes nothing and touches no deny list. The operator reads real commands and picks.

### 11.1 Notifications — the third surface, and the one Zoo does not have

Approvals are only half of "does the operator know". The other half is whether anything *tells* him
when a turn stops. Claude has had banners plus phone pushes since 2026-08-14; Zoo ran silent until
SCC-355, for the reason §6.1 measures — there is no hook to hang one on.

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

**The store it watches** is the same `globalStorage` tree §2 maps, plus every named profile, and it
honours `zoo-code.customStoragePath` when that setting is set — read from user settings and from
each profile's settings, the same two places §7's apply script looks.

### 11.1 Installing it, per machine

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

**Update procedure for this page:** change the lists → update §6's tables in the same commit →
run the suite (the fixtures pin §6 against the tracked file) → apply per machine (§7). The
sop-currency gate will demand the SOP row when a usage surface changes.
