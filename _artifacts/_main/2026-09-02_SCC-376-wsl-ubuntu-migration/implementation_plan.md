---
IsArtifact: true
ArtifactMetadata:
  title: SCC-376 — the PC moves to WSL2 / Ubuntu 24.04
  type: implementation_plan
  date: 2026-09-02
---

# SCC-376 — The PC moves to WSL2 / Ubuntu 24.04

Ticket: [SCC-376](https://sudo-command.atlassian.net/browse/SCC-376) · parent [SCC-48 Machine
Migration Standardizing](https://sudo-command.atlassian.net/browse/SCC-48)
Predecessor: [SCC-375](https://sudo-command.atlassian.net/browse/SCC-375) — the audit that established
*why* this is worth doing.

## Why this is the right call, stated once

SCC-375 measured the problem and named the cause: Claude Code has two independent ways not to
interrupt the operator — the **allow list** (string rules, works everywhere) and the **sandbox**
(the OS fences what a command may touch, so the prompt is skipped whatever shape the command has).
The sandbox runs on macOS, Linux and WSL2, and **not on native Windows**. On the Mac it carries the
load. On the PC it does nothing, which leaves the allow list as the entire fence.

That audit recommended against moving to WSL. The operator overruled it, and the decision stands:
this plan executes the move. What follows is not a re-argument. It is the set of things that will
break if the plan is followed literally, each with the amendment that fixes it — established by
probing the live distro and reading the gate suites on 2026-09-02, not by reasoning about them.

---

## Declared Change Set

Planning lane — the only phase that produces a lobby repo diff is Phase 5. AGY is **out of scope
here on purpose** (see `⚠️ AUDIT FINDING F2` in Phase 5); it ships under its own AVCH ticket with
its own plan and its own port section.

- NEW `_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/implementation_plan.md` — this plan → E
- NEW `_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/tickets/SCC-376.md` — the ticket's fast-read outline → E
- EDIT `_artifacts/_main/INDEX.md` — the session row `check_maps` F2 requires → E
- EDIT `.vscode/settings.json` — Phase 5 strips the Windows-shell Zoo rows and adds the Unix twins → C
- EDIT `.claude/settings.json` — Phase 5 strips the `\Scripts\` / `.exe` rules → C
- EDIT `.agents/scripts/tests/test_settings_allowlist.py` — case A3 amended in the same commit as the deletion → C
- EDIT `docs/migrations/zoo-code-permissions-guide.md` — §6 counts follow the row change, gated by `test_guide_currency` → C
- NEW `docs/migrations/terminal-permissions-guide.md` — Phase 7: the three split pages merged into one → F
- DELETE `docs/migrations/terminal-global-permission.md` — absorbed by the merged guide → F
- DELETE `docs/migrations/claude-terminal-permission.md` — absorbed by the merged guide → F
- DELETE `docs/migrations/zoo-code-permissions-guide.md` — absorbed by the merged guide → F
- EDIT `.agents/scripts/tests/test_zoo_permissions.py` — re-key off `## 6.`/`## 7.` onto stable markers, and repoint `GUIDE` → F
- EDIT `.agents/scripts/zoo_permissions_apply.py` — docstring pointer follows the move → F
- EDIT `.agents/scripts/shape_scan.py` — docstring pointer follows the move → F
- EDIT `.roo/rules/zoo-team.md` — two pointers follow the move → F
- EDIT `.agents/rules/jira.md` — guardrail 5 gains the Linux row; "never persist it anywhere" was written for two machines that both have a credential store → A
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — line 2900 pointer; also the SOP-currency co-occurrence the script edits demand → F
- DELETE `.antigravity/mcp.json` — retired IDE's MCP config (Mac-path-hardcoded) → F
- DELETE `docs/migrations/antigravity_extensions/` — retired IDE's extension-migration guide, ids file, sync script → F
- EDIT `docs/migrations/INDEX.md` — row 10 (the Antigravity extensions guide) removed → F
- EDIT `.vscode/extensions.json` — `google.google-antigravity` recommendation removed → F
- EDIT `.agents/scripts/tests/test_settings_allowlist.py` — Phase 7 (added 2026-09-02): case B4 inverted, the retired surface must NOT be recommended → F
- EDIT `.agents/scripts/tests/test_command_surfaces.py` — Phase 7 (added 2026-09-02): CS-15 is three LIVE platform MCP configs, with the retired one asserted absent → F
- EDIT `docs/repo-map.md`, `docs/doc-graph.md` — Phase 7 (added 2026-09-02): regenerated after the file set changed → F
- EDIT `.agents/scripts/zoo_permissions_apply.py` — Phase 5 (added 2026-09-02): `candidate_dbs` lists the isolated `code2` seat and, under WSL, both Windows stores through `/mnt/c`; an unreadable sibling account reads as absent; `vscode_running` asks `tasklist.exe` by full path → C
- EDIT `.agents/scripts/tests/test_zoo_permissions.py` — Phase 5 (added 2026-09-02): the `candidate_dbs` pin, present/absent halves plus the locked-account half → C
- EDIT `.agents/hooks/shape-guard.py` — Phase 5 (added 2026-09-02): the rule-1 nag no longer claims `git -C * <verb>` allow rules exist → C
- EDIT `.agents/rules/jira.md` — Phase 5: guardrail 5's Linux row (declared above as → A; lands in C) → C
- EDIT `_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/portable_settings.py` — Phase 5 (added 2026-09-02): step 6 drops the `git -C *` rules from the user file → C
- EDIT `_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/claude-user-settings.portable.json` — Phase 5 (added 2026-09-02): regenerated, 82 rules, sha `e1a13e0d…` → C
- EDIT `_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/mac_install.sh` — Phase 5 (added 2026-09-02): the rules diff names the 20 expected `-` lines → C

## Five amendments the plan needs before Phase 1 starts

Each of these is measured, not predicted. The command that produced each finding is given so the
team can reproduce it.

### A1 · ⛔ The distro has no user account. Everything runs as root.

```
user=root  home=/root  uid=0
home_dirs=(empty)
```

Every `~` in the plan resolves to `/root`, not `/home/dlohn`. This matters in three places at once,
and it has to be fixed **first**, before the toolchain goes in:

- Phase 2 clones to `~/Sudo_Hatter_Command`, which as root is `/root/Sudo_Hatter_Command`.
- Phase 3's whole purpose is the sandbox. A sandbox under **uid 0** is a far weaker containment
  claim than one under a normal user, and Phase 3's gate ("a command demonstrably blocked from
  writing outside the repo") is exactly the thing uid 0 is best at defeating.
- Phase 4 creates `Ubuntu-zoo2` by exporting Ubuntu *after* Phase 3. Build the rig as root and the
  export duplicates the mistake into both distros, where it costs twice as much to undo.

**Amendment — new Phase 1 step 0, before anything else is installed:**

```bash
adduser dlohn && usermod -aG sudo dlohn
printf '[user]\ndefault=dlohn\n' >> /etc/wsl.conf     # alongside the existing [boot] systemd=true
```

Then `wsl --shutdown` and reopen. **Gate:** `whoami` returns `dlohn`, `id -u` is not 0, and
`echo $HOME` is `/home/dlohn`.

### A2 · Phase 2's gate number cannot be reached on Linux

The plan's Phase 2 gate reads *"test_allow_readonly_chain 156/156."* That is the **Windows** number.
Block R of that file — the MSYS `/c/…` block SCC-375 added — puts its three ALLOW cases behind
`if os.name == "nt"` (line 419), because the `/c/` spelling only exists on Windows. Its four REJECT
cases run on both platforms by design.

So on Linux the file is **153/153**, and a team holding out for 156 will either stop and escalate or,
worse, "fix" a test that is behaving correctly.

**Amendment — the gate is the exit code and the block, never a hardcoded total:**

```bash
python3 .agents/scripts/tests/test_allow_readonly_chain.py > /tmp/chain.txt 2>&1; echo "EXIT=$?"
grep -c 'R · silent on' /tmp/chain.txt        # must be 4 — the REJECT half still runs on Linux
```

**Gate:** `EXIT=0`, and the R-block reject count is 4. Run it bare — a piped gate returns the pipe's
exit code, not the gate's.

### A3 · ⛔ Phase 5 as written makes Phase 6 unpassable

`test_settings_allowlist` case **A3** (line 76) requires that the `python3 X` and `python X` rule
families are **both non-empty** and that every rule in each has its twin in the other:

```python
c.check("A3 interpreter twins hold in BOTH directions (python3 Mac / python PC)",
        bool(py3) and bool(py) and not missing, ...)
```

Bare `python` is the **PC** spelling — the Mac has only `python3`, and so does Ubuntu 24.04 out of
the box. Phase 5 says *"any Windows-only rule goes."* Followed literally, it deletes every
`Bash(python …)` rule, `py` becomes empty, **A3 fails**, and Phase 6's *"all test suites green from
WSL"* can never hold.

This is the same defect class SCC-375 just closed: a test pinning a shape the system is deliberately
leaving behind. The twin requirement existed because the two machines disagreed about the interpreter.
After this migration they agree, and the requirement is obsolete.

**Amendment — A3 is amended in the SAME commit that deletes the rules**, never after. The check
becomes a one-directional assertion that `python3` rules exist and that no bare-`python` rule remains,
with the reason written in the case's comment the way A2b's is. Deleting the rules first and fixing
the test second leaves a red suite in the tree, which is the state Phase 0 exists to avoid.

### A4 · "Byte-identical to the Mac file" can certify a broken file

Phase 3 hands over the Mac's `~/.claude/settings.json` unchanged, and Phase 6 checks byte-identity.
That is the right default and it should stay. The gap is that the **user-level** file is untracked and
has no equivalent of the tracked file's case **A4** (`no machine-absolute path in any tracked rule`,
line 79), which already rejects `/Users/…` and `X:\…`.

If the Mac file contains `/Users/<name>/…` paths or `additionalDirectories` entries that are Mac-only,
byte-identity on Linux certifies a file pointing at directories that do not exist.

**Amendment — one added step in Phase 3, before the file is installed:**

```bash
grep -n '/Users/\|/private/\|additionalDirectories' ~/.claude/settings.json
```

Empty output means byte-identical is correct and Phase 6's check stands as written. Any hit is a
**one-line ruling from the operator per entry** — never a silent rewrite by the team, and never a
quiet exception to the byte-identity gate. Whichever way each is ruled, the ruling is recorded here
so Phase 6 checks the file the operator actually approved.

### A5 · Phase 1 prerequisites that are missing today

Measured inside the distro:

| Probe | Result | Consequence |
|---|---|---|
| `command -v node` | MISSING | expected — nvm installs it |
| `command -v npm` | `/mnt/c/Program Files/nodejs/npm` | Windows npm with no Windows node behind it — a broken half-state `appendWindowsPath=false` removes |
| `command -v claude` | `/mnt/c/Users/dlohn/AppData/Roaming/npm/claude` | the leak Phase 1 targets, confirmed |
| Windows `PATH` entries | **50** | the size of the leak |
| `command -v unzip` | MISSING | **`gh` and `acli` installers commonly need it — install it before them** |
| `command -v git`, `python3`, `curl` | present, `/usr/bin` | fine |
| `ps -p 1 -o comm=` | `systemd` | already correct; `/etc/wsl.conf` keeps `[boot] systemd=true` |

**`acli` authentication — RESOLVED by the operator's research (2026-09-02), and downgraded from an
unproven blocker to a day-one step.** The house's entire Jira integration is `acli`, and the rule
that governs it says the token lives in the OS credential store — *"the macOS keychain on the Mac,
the Windows equivalent on the PC."* Linux has neither, which is why this was flagged. Atlassian's
own headless-Linux guidance does not use a keychain at all: it authenticates with an API token read
from **standard input**.

```bash
echo "$JIRA_API_TOKEN" | acli jira auth login --email sudomadhatter@gmail.com --site sudo-command.atlassian.net --token
```

`--token` reads from stdin; `--web` is the browser flow used on the Mac and needs a desktop. The
token is a standard Atlassian API token from id.atlassian.com → Security → API tokens.

Two things settle on day one, **in this order** — the order matters because the first answer decides
whether the second is needed at all:

1. **Does the session persist?** Log in once, open a brand-new shell, run `acli jira auth status`.
   If it is still authenticated, `acli` has written a session under `~/.config` (or similar) and the
   environment variable was needed exactly once — nothing further to arrange. Confirm the file's
   location and record it here.
2. **Only if it does NOT persist** does the token need a home in the shell profile, and only then
   does the trap below bite.

> ### ⚠️ `~/.bashrc` is invisible to the shells agents actually spawn
>
> Ubuntu's default `~/.bashrc` begins with an interactivity guard and returns immediately for a
> non-interactive shell — which is precisely what every agent tool call gets. A `JIRA_API_TOKEN`
> exported there is present when the operator types in a terminal and **absent for every automated
> call**, producing exactly the failure mode `.agents/rules/jira.md` warns about: an `acli` failure
> that is a fact about the shell, not about the board. This is the Linux twin of the house scar
> `interactive-startup-files-are-invisible-to-automation`. If a profile home is needed, prove it with a non-interactive
> probe — `bash -c 'echo ${JIRA_API_TOKEN:+set}'` — not by opening a terminal and looking.

> ### ⚠️ Keep the token on stdin, never in an argument
>
> The piped form above is not merely Atlassian's documented shape, it is the *safe* one: a token
> passed as `--token "$JIRA_API_TOKEN"` lands in shell history and in `ps` output for every user on
> the box. Anyone "simplifying" the pipe away reintroduces that. The token never goes in the repo,
> never in a commit, and never on a command line.

**Downstream edit this obliges, named so it is not forgotten:** `.agents/rules/jira.md` guardrail 5
currently reads *"The token stays in the OS credential store. Never echo, copy, or persist it
anywhere"* — written for two machines that both have one. Linux has none, so the Linux path
necessarily persists a token somewhere, and the rule must gain that row or it reads as permanently
violated. It is a rule edit, so it belongs in **Phase 5's commit** with the other law changes, not
in Phase 1.

**Gate — Phase 1 proves `acli jira auth status` returns authenticated inside Ubuntu, from a
non-interactive shell, before Phase 2 begins.**

---

## What the plan gets right, said plainly

Two calls are worth confirming rather than leaving unremarked, because they are the ones most often
gotten wrong.

**Exporting `Ubuntu-zoo2` after Phase 3, not before.** The second distro inherits a base that has
already passed the sandbox gate, so the rig is proven once instead of twice. Doing it before Phase 3
would mean debugging two distros in parallel.

**All-or-nothing, with the Windows fence frozen as the fallback until Phase 5.** Phase 5 deletes that
fallback, which is correct — but it should be said out loud that the way back after Phase 5 is a
`git revert` of the Phase 5 commit, not a rebuild. That is why Phase 5 must be **one commit**, not
spread across several.

---

## The phases, with owners and gates

Owner column is the plan's own split: **Team** = engineering (repo, toolchain, hooks, tests, ticket),
**Desktop** = Desktop Team (editor, two-instance rig, sign-off), **Operator** = Mr. Hatter.

### Phase 0 — Freeze · Team · today

No new Windows-side rules. The Windows fence stays exactly as SCC-375 left it and is the fallback
until Phase 5 closes.

**Gate:** `.vscode/settings.json`, `.claude/settings.json` and AGY's `.claude/settings.json` are
unchanged from the SCC-375 merge (`a87f1b5a`) — `git diff a87f1b5a -- <the three files>` is empty.

### Phase 1 — Linux toolchain · Team

1. **A1 first:** create the `dlohn` user, add to `sudo`, set `[user] default=dlohn` in `/etc/wsl.conf`.
2. Add `appendWindowsPath=false` under `[interop]` in `/etc/wsl.conf`. `wsl --shutdown`, reopen.
3. `apt install unzip` (A5), then install nvm → **Node 22 LTS** (the Mac's pin; Node 26 breaks vitest
   jsdom storage).
4. Install `gh`, `acli` and `claude` (native installer) inside Ubuntu.

**Gate — every line must hold:**

```bash
whoami; id -u; echo $HOME                      # dlohn / non-zero / /home/dlohn
echo "$PATH" | tr ':' '\n' | grep -c '^/mnt/'  # must be 0
for t in node npm claude acli gh python3; do printf '%-8s %s\n' "$t" "$(command -v $t)"; done
node --version                                 # v22.x
echo "$JIRA_API_TOKEN" | acli jira auth login --email sudomadhatter@gmail.com \
     --site sudo-command.atlassian.net --token   # once; --token reads stdin, --web needs a desktop
bash -c 'acli jira auth status'                # ✓ from a NON-interactive shell — the real test
bash -c 'echo ${JIRA_API_TOKEN:+set}'          # only matters if the session did not persist
```

Then open a brand-new shell and re-run `acli jira auth status`. Still authenticated means the
session persisted and the environment variable was needed exactly once — **record where it persisted
to** in A5 above.

Every path is `/usr/…` or `/home/…`. Zero `/mnt/c`.

### Phase 2 — Repo and venvs · Team

Clone to `/home/dlohn/Sudo_Hatter_Command` on the Linux disk, **not** `/mnt/c`. Rebuild every venv as
a Linux venv — `.venv/Scripts/` ceases to exist, `.venv/bin/` is the only form. Arm the git hooks
per-machine (`git config --global core.hooksPath .githooks` — hooks are local config and a fresh clone
has none).

> ### ⚠️ FINDING F7 — the lobby is TEN SUBMODULES deep, and a fresh clone has none
>
> Found by executing Phase 2, not by reading. The clone landed and both gate suites passed, but the
> full suite came back **70/71** on `test_sops_prds_folder` → **T9 · every prose path reference
> resolves**. It is not a Linux bug and not a regression: `.gitmodules` declares ten submodules under
> `Projects/`, a fresh clone initialises none of them, and T9 resolves prose paths against project
> roots — so references like `_bmad/bmm/stories/` (which lives inside `AGY_AVIATIONCHAT`) resolve on
> the PC and nowhere on the new box. The test says so itself in its own NOTE and still fails rather
> than skipping, which is the correct behaviour.
>
> **Consequence for the plan: Phase 5's gate — `run_all.py` green from inside WSL — is unreachable
> until the submodules are initialised.** Phase 2 said "clone the repo" and never said "and its ten
> children", so this would have surfaced as a mystery red at the end of Phase 5 instead of on day one.
>
> **Phase 2 gains a step:** `git submodule update --init --recursive` — which needs `gh auth login`
> first, because the child repos are private. Re-run the full suite after and expect 71/71.

> ### ⚠️ AUDIT FINDING F5 — landing-order dependency on SCC-323
>
> `origin/chore/SCC-323-hookspath-immunisation` is unmerged and ships
> `docs/migrations/scripts/arm_hooks_path.py` plus `Arm-HooksPath.ps1` — the installer for exactly
> the hand-typed `git config` line above. **If SCC-323 lands first, Phase 2 calls the installer
> rather than retyping the command**; a script plus an instruction is not delivery.
> Note also that `Arm-HooksPath.ps1` is PowerShell and becomes dead weight on the PC once this
> migration completes — flag it to that lane rather than deleting it from here.

**Gate — run bare, read the exit code:**

```bash
python3 .agents/scripts/tests/test_allow_readonly_chain.py > /tmp/chain.txt 2>&1; echo "EXIT=$?"
grep -c 'R · silent on' /tmp/chain.txt         # 4
python3 .agents/scripts/tests/test_settings_allowlist.py  > /tmp/allow.txt 2>&1; echo "EXIT=$?"
git config --get core.hooksPath                # .githooks
```

Both `EXIT=0`. **Expect 153 on the chain file, not 156 — see A2.** `test_settings_allowlist` is
28/28 on both platforms.

### Phase 3 — Sandbox on · Team, with the Operator supplying the file

The operator copies `~/.claude/settings.json` off the Mac and hands it over. Run the **A4 probe**
before installing it; any hit gets a one-line ruling from the operator and the ruling is recorded in
this plan. Then it becomes Ubuntu's `~/.claude/settings.json`, unchanged.

`sandbox.enabled: true` and `autoAllowBashIfSandboxed: true` are live on the PC for the first time.

**Gate — Desktop Team verifies containment, and it must be demonstrated, not assumed:**

A command that attempts a write outside the repo is **blocked by the sandbox**, with the refusal shown.
Contained, not inferred from the setting being present. This is the moment the PC has two fences, and
it is the one gate in this plan that cannot be replaced by reading a config file.

### Phase 4 — Editor and rig · Desktop Team

VS Code stays on Windows, connected via Remote-WSL. Colors, badges, keybindings and the clone-sync are
unchanged. Install the work extensions (Claude Code, Zoo Code, Python) **into Ubuntu** — a Remote-WSL
extension installed on the Windows side does not run in the distro. Create `Ubuntu-zoo2` by exporting
Ubuntu after Phase 3 and importing it under the new name; install the same extensions; point `code2`
at it.

**Gate:** change the model in one Zoo instance; the other does not move.

### Phase 5 — Cleanup to match the Mac · Team · ONE commit

Everything Windows-shaped comes out, in a single revertable commit.

> ### ⚠️ AUDIT FINDING F3 — this pass DELETES ONLY, and three capabilities lose their allow row
>
> Measured against `.vscode/settings.json`: the **only** rows covering pytest, ruff and the firebase
> emulator are Windows-shaped, and no Unix twin exists for any of them.
>
> ```
> pytest via venv     unix twin present: NONE
> ruff via venv       unix twin present: NONE
> firebase emulator   unix twin present: NONE
> backend venv        unix twin present: ['backend/.venv/bin/']   ← the only one that survives
> ```
>
> A delete-only Phase 5 therefore leaves Zoo prompting for the **entire test toolchain** — the exact
> problem this migration exists to remove, reintroduced by the cleanup step. **Add these three rows
> in the same commit as the deletions:**
> `.venv/bin/python -m pytest` · `.venv/bin/ruff check` ·
> `firebase/tests/node_modules/.bin/firebase emulators:exec`

> ### ⚠️ AUDIT FINDING F4 — `dir` is a prefix, and it takes `dirname ` with it
>
> Zoo matches by lowercase starts-with. `.vscode/settings.json` carries both `'dirname '` and
> `'dir'`, so a sweep on `dir` deletes **`dirname `** — a POSIX command that must survive the
> migration and which the house scripts use. Delete the row `'dir'` by **exact match**, never by
> prefix. This is the same defect class SCC-375 closed: a prefix matching more than it names.

- `.vscode/settings.json` Zoo allow list — remove by **exact match**: `dir`, `type `, `findstr`,
  `where `, `del scratch\`, `set "JAVA_HOME=`, `Write-Host`, `Get-Item`, `Get-ChildItem`,
  `Select-Object`, `Select-String`, `Test-Path`, `Write-Output`, `more`, and the 6 backslash rows.
  Measured: **20 rows out of 143, leaving 123** — then **+3 Unix twins per F3**, landing at 126.
  ⛔ `dirname ` is NOT in that set (F4).
- `.claude/settings.json` — the same pass: any `\Scripts\`, `.exe`, or Windows-only rule.
- **A3's amendment lands in this same commit** — the interpreter-twin case is rewritten as the bare
  `python` rules are deleted, not afterwards.
- Retire the Windows `~/.claude/settings.json` and the Windows repo clone.
- `zoo_permissions_apply.py --apply` on **both** distros, VS Code fully closed (SQLite single-writer).
- `test_allow_scratchpad` case E — the uid case that could never pass on Windows — passes natively.
  The SCC-375 open item closes here. (No edit declared: if it needs one, that is a new finding.)
- Guide §6 counts updated in the same commit (`test_guide_currency` gates this).

> ### ⚠️ AUDIT FINDING F2 — AGY is OUT OF SCOPE for this ticket
>
> The first draft of this plan listed AGY's `.claude/settings.json` in this phase. That file exists
> in two repos and the copies **differ** — `git diff --no-index` returns `1`, 111 insertions /
> 267 deletions — which fires `.agents/rules/port-checklist.md:29` and makes all six port checks due
> **in this plan**, or the audit is a NO-GO.
>
> It is scoped out rather than answered here, because the honest boundary is the repo: cross-repo
> work takes a ticket per repo, and a lobby ticket editing files inside AGY produces a commit no
> AVCH ticket accounts for. **AGY ships under its own AVCH ticket, with its own plan carrying its
> own port section.** Mint it when Phase 4 closes.

**Gate:** `python3 .agents/scripts/tests/run_all.py` green, run bare, from inside WSL.

### Phase 6 — Sign-off · Desktop Team

One checklist, run on the PC. Every line holds or the phase does not pass:

```
[ ] Sandbox verified ACTIVE by demonstrated containment (Phase 3 gate), not by reading the config
[ ] Zero Windows binaries resolve from inside either distro
[ ] Repo and venvs on the Linux filesystem, not /mnt/c
[ ] All test suites green from WSL, run bare
[ ] code and code2 isolated — model change in one does not move the other
[ ] Zoo and Claude allow lists contain no Windows-shell rows
[ ] PC ~/.claude/settings.json byte-identical to the operator's Mac file, with any A4 rulings recorded
[ ] Running as a normal user, not root (A1)
```

### Phase 7 — One permissions guide · Team · **the last step of this ticket**

Three documents currently describe one subject, and the split is a direct cause of how long this
took to diagnose: the front door says *"each agent carries its own store and its own matcher"*, and
then the two facts that actually explain the months of friction — that Claude's sandbox does not
exist on Windows, and that `Bash(X:*)` means `Bash(X *)` — live in two different deep dives, neither
of which the other links to at the point of need.

| Today | Lines | What it is |
|---|---|---|
| `docs/migrations/terminal-global-permission.md` | 26 | the cross-agent front door: which agent, which store, which matcher, how to add an approval that sticks |
| `docs/migrations/zoo-code-permissions-guide.md` | 352 | the Zoo deep dive — §1–§11, the extracted v3.80.1 matcher, the seeding trap, the canonical lists |
| `docs/migrations/claude-terminal-permission.md` | 172 | the Claude deep dive — settings hierarchy, worktree asset linking, the escape guard, sandbox boundaries |

**Target: one file, `docs/migrations/terminal-permissions-guide.md`**, and the three originals are
**deleted, not stubbed** — the house rule is retire, don't accrete. Written *after* Phase 6 on
purpose: roughly a third of the current content documents Windows machinery Phase 5 deletes (the
backslash rows, the `X:*` spelling trap, "Windows has no sandbox"), so writing it earlier would
document a system we are about to demolish and then rewrite it.

**What it must carry that no current page does** — the knowledge this ticket and SCC-375 bought:

1. **The two-fence model, first, as the organising idea.** Allow list and sandbox are independent;
   the sandbox is the one that does the heavy lifting; which platforms have it. Every other section
   hangs off that, because it is the fact that explains the whole history.
2. **The failure catalogue** — each with its measurement, because a symptom the reader recognises is
   worth more than a rule they must apply: the `X:*` spelling that matches nothing, the MSYS `/c/`
   blind spot, the `VAR=` vocabulary gap, cp1252 crashes creating the `PYTHONIOENCODING=` habit,
   and the seeding trap where the tracked file is not the decision store.
3. **Laundering prefixes as a named concept**, with the three refusals on record (`if exist `,
   `ForEach-Object`, `PYTHONIOENCODING=`) and *why* the best-looking numbers came from the change
   that was refused.
4. **The post-migration state** — one shape, Unix, on both machines — so the guide describes what
   is, not the history of what was.

**Added by the operator 2026-09-02 — the Antigravity leftovers go in this same last step.**
Antigravity the IDE was retired on 2026-08-29 (daily driving moved to VS Code; its always-proceed bug
is upstream). Three leftovers sit in this ticket's territory and are deleted in the Phase 7 commit:

- DELETE `.antigravity/mcp.json` — the IDE's MCP config for md-feedback, hard-coded to a Mac path, so it never worked on the PC in any case
- DELETE `docs/migrations/antigravity_extensions/` (the guide, the ids file, the sync script) and its `docs/migrations/INDEX.md` row 10
- EDIT `.vscode/extensions.json` — drop the `google.google-antigravity` recommendation

**Explicitly NOT in Phase 7: retiring Antigravity as a *platform*.** That is the 46 launchers in
`.agents/workflows/` (its command menu), the `GEMINI.md` front doors, the `.gitattributes` mirror rules,
the `~/.gemini/antigravity/global_workflows` cache `sync-agents.ps1` writes, the platform entry in
`_bmad/_config/manifest.yaml`, and 22 references in the testing SOP — measured 2026-09-02: 184 files
mention Antigravity. That is a sync-agents change with the SOP-currency gate on it, and it gets its own
ticket — **SCC-378**, opened 2026-09-02 on the operator's approval with the eight-step plan on the
ticket itself (outline: [`tickets/SCC-378.md`](tickets/SCC-378.md)); a migration ticket must not absorb
a platform retirement.

> ### ⚠️ AUDIT FINDING F6 — this merge is a PATH MOVE, and one of the three is machine-read
>
> `test_guide_currency` does not merely mention the Zoo guide, it **parses** it:
>
> ```python
> GUIDE = ROOT / "docs" / "migrations" / "zoo-code-permissions-guide.md"   # :26
> sec = text.split("## 6.")[1].split("## 7.")[0]                            # :304
> ```
>
> A naive merge throws `IndexError` on that split. **Do not contort the merged document to preserve
> a section literally numbered `## 6.`** — a section-number split is brittle by construction and any
> future reorganisation breaks it silently. Re-key the test to stable markers
> (`<!-- zoo-lists-begin -->` / `<!-- zoo-lists-end -->`) placed around the canonical-lists table,
> and move `GUIDE` to the new path, **in the same commit as the merge.** Fix with mechanism, not
> wording.
>
> **Every referencing site, measured — all updated in that same commit:**
> `.roo/rules/zoo-team.md:79,85` · `docs/_scc_sops_prds/workflows_testing_SOP.md:2900` ·
> `.vscode/settings.json:29` (comment) · `.agents/scripts/zoo_permissions_apply.py:8` (docstring) ·
> `.agents/scripts/shape_scan.py:5` (docstring) · `.agents/scripts/tests/test_zoo_permissions.py:4,26,303`
> · `docs/doc-graph.json` (a cache — regenerate with `.agents/scripts/generate_doc_graph.py`, never
> hand-edit). Relocated links are **mis-pathed, not dead** —
> nothing 404s, they just quietly point at nothing.
>
> Touching `.agents/scripts/*.py` and `.agents/rules/` arms the SOP currency gate, so
> `workflows_testing_SOP.md` is staged in the same commit — which it needs anyway for its line 2900.
> The gate and the work agree here; no `[sop-ok]` opt-out is warranted.

**Gate:**

```bash
python3 .agents/scripts/tests/test_zoo_permissions.py      # green against the NEW path + markers
python3 .agents/scripts/check_links.py                     # no reference to any of the three old paths
python3 .agents/scripts/tests/run_all.py                   # bare, from inside WSL
```

Plus one read-through check that is not machine-checkable and is stated so it is not skipped: a
person who was not in these sessions can find, from the contents alone, *why Claude asked for
approval on a command they thought was allowed* — that is the question the three split documents
could not answer, and it is the whole reason this phase exists.

---

## Proposed subtasks — NOT minted

Under house law a piece earns a `Subtask` when it earns its own `chore/<KEY>-<slug>` branch in its own
worktree; a ticket with no branch is a row nothing will ever write to. Measured against that, only two
phases produce a repo diff:

| Would-be subtask | Branch | Why it qualifies |
|---|---|---|
| **Phase 5 — lobby cleanup** | `chore/<KEY>-strip-windows-rules` | a real diff across three tracked files plus the A3 amendment |
| **Phase 5 — AGY cleanup** | AVCH ticket, own repo | cross-repo; needs its own key |

Phases 0–4 and 6 are environment and rig work with no lobby commit. They stay as the checklist above
rather than becoming board noise.

**Nothing is minted until the operator approves this plan and says go.**

## Acceptance

Lettered so the Declared Change Set can point at a row. Each names something observable.

- **A** — Ubuntu runs as a non-root user: `whoami` is `dlohn`, `id -u` is non-zero, `$HOME` is
  `/home/dlohn`, and `echo $PATH | tr ':' '\n' | grep -c '^/mnt/'` returns `0`. **And** `acli jira
  auth status` reports authenticated **from a non-interactive shell**, with the session's persistence
  location recorded in this plan.
- **B** — the sandbox is demonstrably containing: a command that writes outside the repo is refused,
  with the refusal pasted as evidence. Not inferred from the config.
- **C** — after Phase 5, `run_all.py` is green **run bare from inside WSL**, and Zoo's allow list
  carries a Unix row for pytest, ruff and the firebase emulator (F3) while still carrying
  `dirname ` (F4).
- **D** — `code` and `code2` are isolated: a model change in one does not move the other.
- **E** — this plan, the ticket outline and the INDEX row exist in the tree, and the ticket's
  `## Plan` checklist matches this plan's phases one for one.
- **F** — one guide at `docs/migrations/terminal-permissions-guide.md`; the three originals are gone
  from the tree; `check_links.py` reports no reference to any of the three old paths;
  `test_zoo_permissions.py` is green against the new path and the new markers; and the guide opens
  with the two-fence model rather than with any single agent's store.

## Self-Audit (2026-09-02)

Level: **LEDGER+BLAST** — the plan's change set touches a rule-adjacent gate suite, a door surface
(`.vscode` / `.claude` settings both platforms read), and a file that exists in more than one repo,
so the heavier level is mandatory rather than chosen. Mode: **PRE-WORK**.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every path/script/rule the plan names exists on disk
             the `## Declared Change Set` block parses
             plan-named Zoo rows actually exist in .vscode/settings.json
             does a Unix twin survive each Phase 5 deletion
             ticket acceptance precondition (>=2 rows, each with an observable)
             lane fit — does the change set touch a deployable product path
read:        .agents/rules/artifacts-always-first.md:181-188
             .agents/scripts/tests/test_allow_readonly_chain.py:418-441
             .agents/scripts/tests/test_settings_allowlist.py:55-84
             .vscode/settings.json (143 allow rows), .claude/settings.json (161 allow rules)
             .agents/scripts/{run_all,zoo_permissions_apply,declared_change_set,risk_seam}.py — all EXIST
             .agents/scripts/tests/test_zoo_permissions.py (owns test_guide_currency)
verdict:     findings below — F1, F3, F4
```

```
lens:        2 Parity + Blast
checks_run:  cross-repo copy — git diff --no-index on the two .claude/settings.json
             sibling worktrees — git fetch origin main, git worktree list, unmerged branches
             a gate/hook surface — does the plan ship it ARMED
             SOP / usage surface — both halves in the same commit
             twins — is there a cicd-*/smh-* sibling of anything the plan changes
read:        .agents/rules/port-checklist.md:25-39
             git worktree list -> ONE tree (this one); no sibling lane holds these paths
             git branch -a --no-merged origin/main -> 8 branches, one relevant
             origin/chore/SCC-323-hookspath-immunisation -> arm_hooks_path.py, Arm-HooksPath.ps1
             risk_seam: not run — the command centre is markdown and returns `unclassified`
             permanently and correctly (SCC-289); judgement taken from the diff instead
             RE-RUN after Phase 7 was added: path-move sweep for the three merged guides —
             10 referencing sites across .roo/, docs/, .vscode/ and .agents/scripts/,
             one of which PARSES the document rather than linking it
verdict:     findings below — F2, F5, F6
```

> **Amendment note.** Phase 7 (merging the three permission guides) was added by the operator
> **after** the first audit pass. Rather than let it ride unaudited, Lens 2's path-move row was
> re-run against it — that is what produced **F6**. Lens 1 and Lens 3 were re-read against the new
> phase and produced nothing further. No fourth lens was added; the amendment rule forbids it.

```
lens:        3 Pre-Mortem (bounded — attaches narrative, originates nothing)
checks_run:  the silent failure, the other-machine failure, the fresh-clone failure,
             the sibling-lands-first failure — each attached to an anchored finding above
read:        no new files; operates on lens 1 and 2 output only
verdict:     three narratives attached to F2, F3, F4; nothing unattached, nothing discarded
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/rules/port-checklist.md:29` + `git diff --no-index` → `differ=1`, 111 ins / 267 del | *"the plan's SCOPE names a file that **exists in more than one repo**"* | **F2 · NO-GO ground.** Phase 5 named AGY's `.claude/settings.json`, whose copies differ, so all six port checks were due in this plan and none were answered. **Fixed:** AGY scoped out to its own AVCH ticket. | blocker |
| `.vscode/settings.json` — measured `unix twin present: NONE` for pytest, ruff, firebase emulator | `'.venv\Scripts\python.exe -m pytest'`, `'.venv\Scripts\ruff.exe check'`, `'firebase\tests\node_modules\.bin\firebase emulators:exec'` | **F3.** Phase 5 was delete-only, so the whole test toolchain loses its allow row and Zoo starts prompting for it — the problem this migration exists to remove, reintroduced by its own cleanup step. **Fixed:** three Unix twins added to the same commit. | high |
| `.vscode/settings.json` — rows `['dirname ', 'dir']` | `dirname ` | **F4.** Zoo matches by starts-with, so a prefix sweep on `dir` deletes `dirname `, a POSIX command that must survive. Same defect class SCC-375 closed. **Fixed:** exact-match deletion, `dirname ` named as excluded. | high |
| the plan file itself + `.agents/rules/artifacts-always-first.md:181` | *"an absent block is the reviewer's important finding"* | **F1.** The plan shipped with no `## Declared Change Set` block and no artifact frontmatter, so the review drift check and this audit's own Scope Ledger had nothing to parse and the level defaulted to the heavier one. **Fixed:** both added. | medium |
| `origin/chore/SCC-323-hookspath-immunisation` → `docs/migrations/scripts/arm_hooks_path.py` | the file exists on that branch, unmerged | **F5.** Phase 2 hand-types the `core.hooksPath` command that SCC-323 is shipping an installer for. **Fixed:** Phase 2 now defers to the installer if SCC-323 lands first, and flags `Arm-HooksPath.ps1` as post-migration dead weight to that lane rather than deleting it from here. | medium |
| `.agents/scripts/tests/test_zoo_permissions.py:26,304` | `GUIDE = ROOT / "docs" / "migrations" / "zoo-code-permissions-guide.md"` and `sec = text.split("## 6.")[1].split("## 7.")[0]` | **F6.** Phase 7's merge is a path move of a **machine-read** document: the test hardcodes the path and splits on literal section numbers, so a naive merge throws `IndexError` and 10 referencing sites go quietly mis-pathed. **Fixed:** Phase 7 re-keys the test onto stable markers instead of section numbers, and names every referencing site with its line for the same commit. | high |

### Pre-Mortem narratives (attached, never originating)

- **F3, the silent one.** Phase 5 lands, `run_all.py` is green, Phase 6 signs off — because no suite
  asserts that Zoo's allow list covers pytest. The breakage appears the next time someone runs the
  tests through Zoo and answers an approval prompt per command, weeks later, with nothing connecting
  it to the cleanup commit.
- **F4, the other-machine one.** `dirname ` vanishes. It is used inside house scripts and shell
  chains rather than typed directly, so it prompts intermittently and reads as flakiness.
- **F2, the fresh-clone one.** AGY's settings get edited from a lobby lane. The AVCH board has no
  row for it, and the next AGY close-out preflight finds a diff no ticket accounts for.
- **F6, the silent one.** The merge lands, the suite is red on an `IndexError` nobody expected from
  a documentation change, and the obvious fix — re-adding a `## 6.` heading to satisfy the split —
  restores green while leaving the same brittleness in place for the next person to reorganise the
  page. The failure is not the red; it is the plausible wrong fix waiting behind it.

### Observations (uncounted, non-blocking)

- Acceptance row *"phase gates are executable by someone who was not in this session"* was
  unobservable as first written. Replaced with the lettered A–E rows above, each naming a command or
  a state. Recording it because a vague acceptance list is what makes the Scope Ledger match
  everything and produce nothing.
- The Scope Ledger table is trivially clean: this plan creates only its own artifacts, and every one
  serves row **E**. No artefact is created that no acceptance row requires.
- Lane fit is correct — the change set touches no deployable product path
  (`backend/ frontend/ firebase/ functions/ mobile/ .github/`), so `/smh-close-task-merge-tree` is
  the right door and `/cicd-push-e2e` is not.
- **A5 was closed by the operator after this audit ran, and the closure is better than the flag.**
  It was recorded as unverifiable from this machine and written into Phase 1's gate rather than
  guessed at; the operator supplied Atlassian's headless-Linux guidance — `--token` over stdin, no
  keychain — which converts a possible blocker into a day-one step. Two things were added on top of
  that research because they are specific to this machine rather than to `acli`: Ubuntu's
  `~/.bashrc` returns early for the non-interactive shells agents spawn, and the token must stay on
  stdin rather than in an argument where `ps` and shell history can read it. Recording the sequence
  because "I could not verify this" was the right answer at audit time and is no longer the answer.

### Sibling landing-order

One worktree (this one); no sibling lane holds any declared path. The only ordering constraint is
**F5 · SCC-323 before Phase 2** if that branch lands first — and it is a substitution, not a
conflict, so neither order breaks the other.

```
Audit verdict: GO
```

**Found NO-GO on the first pass, flipped by remediation in this same pass — the honest record.** The
grounds were **F2**: the port rule fired mechanically (a file in two repos, copies measurably
differing) and the plan answered none of its six checks. That is one of the two named NO-GO grounds,
not a judgement call. It is cleared by scoping AGY out to its own AVCH ticket rather than by
answering the checks, because the repo is the honest boundary. F1, F3, F4 and F5 are fixed inline in
the sections they affect, marked `⚠️ AUDIT FINDING` so the builder reads each in context.

The verdict describes the plan **as it now stands**, which is the plan being put up for approval.

## Execution log (2026-09-02) — what actually happened, phase by phase

Written from the Linux clone, because the shared Windows tree was moved to another lane's branch
mid-session. Every line below is a measurement, not a plan.

### Phase 0 — PASS

`git diff --stat a87f1b5a -- <the three settings files>` is empty. The Windows fence is frozen and
remains the fallback.

### Phase 1 — PASS (operator ruling: passwordless sudo for `dlohn`)

| check | result |
|---|---|
| `whoami` / `id -u` / `$HOME` | `dlohn` / `1001` / `/home/dlohn` |
| Windows PATH entries leaking in | **50 → 0** |
| `/etc/wsl.conf` | `[boot] systemd=true` kept; `[user] default=dlohn` and `[interop] appendWindowsPath=false` added; `.scc376.bak` kept |
| sudoers | `/etc/sudoers.d/dlohn` NOPASSWD, validated by `visudo -c` |
| toolchain | node **v22.23.2** · npm 10.9.8 · gh 2.99.0 · acli 1.3.36 · claude (native) · unzip |
| `gh auth status` / `acli jira auth status` | both authenticated — done by the PC team |

**A finding the plan did not anticipate, and it was load-bearing.** nvm and the `claude` installer
both write their PATH export into `~/.bashrc`, and Ubuntu's `~/.bashrc` returns early for a
non-interactive shell — which is exactly what every agent tool call gets. Left alone, `node`, `npm`
and `claude` were present when the operator typed and **MISSING for automation**; the `claude`
installer printed the warning itself. All four are symlinked into `/usr/local/bin` and every tool is
now proven from `bash -c`. Same scar as the A5 token trap; it bit the toolchain first.

**Correction.** The acli gate was written with the wrong email (`dlohneiss@gmail.com`); the Jira
account is **`sudomadhatter@gmail.com`**. The PC team hit `Unauthorized` on the first try because of
it. Fixed above.

### Phase 2 — PASS

Repo at `/home/dlohn/Sudo_Hatter_Command` on `/dev/sdc` (the Linux disk), cloned from the local
Windows checkout (full history, no network, no auth needed), remote repointed at GitHub,
`core.hooksPath=.githooks` armed, hooks executable.

| gate | result |
|---|---|
| `test_allow_readonly_chain` | **153/153**, exit 0 — A2 confirmed exactly: 4 R-block reject cases present, 0 allow cases |
| `test_settings_allowlist` | 28/28, exit 0 |
| `test_allow_scratchpad` | **187/187**, exit 0 — the SCC-375 open item (case E, the uid test) closed by the migration itself |
| `run_all.py` after submodules + assets | **71/71**, exit 0 |

**F7 resolved.** `git submodule update --init --recursive` brought in all ten `Projects/` children
(needed `gh auth setup-git` first — `gh auth login` alone does not wire git's credential helper).
T9 then still named eight paths: `backend/.venv`, `backend/.env`, `frontend/node_modules`,
`firebase/tests/node_modules` under AGY, and `docs/.maps-journal.jsonl` — all **gitignored,
per-machine assets** that a fresh clone never has. Rebuilt for Linux, AGY only (the frozen projects
are left alone on purpose): `.env` copied disk-to-disk with mode 600 and never printed, `npm ci` in
both node trees (687 + 488 packages on Node 22), the journal copied from the PC checkout.

**One honest caveat, then fixed.** The first `python3 -m venv` created `backend/.venv` and died on
`ensurepip` because `python3.12-venv` was not installed — so T9 went green on a directory that was
not a venv. A directory is not a venv. The package was installed, the venv rebuilt, requirements
installed, and `pytest` / `ruff` proven from `.venv/bin/`. Recorded because a green that lies is the
house's oldest scar.

### Phase 3 — prerequisites in; waiting on the Mac file

The plan said "copy the Mac's settings file". The vendor sandbox doc says the Linux/WSL2 sandbox
needs **two packages the plan never named**, plus an Ubuntu 24.04-specific AppArmor step:

| prerequisite | result |
|---|---|
| `bubblewrap` + `socat` | installed, `/usr/bin` |
| `kernel.apparmor_restrict_unprivileged_userns` | key does not exist in this WSL kernel — doc says skip the profile |
| `@anthropic-ai/sandbox-runtime` (seccomp, optional; on WSL2 it is what blocks Windows-binary launches) | installed |
| `bwrap --unshare-user … /bin/true` | **namespace created — OK** |

**The mechanism that ends the two-machine divergence.** The sandbox doc states that `~/` in
`allowWrite` resolves to `$HOME` on each machine. So the Mac's `/Users/sudohatter/Sudo_Hatter_Command`
and Linux's `/home/dlohn/Sudo_Hatter_Command` are **one identical line**, `~/Sudo_Hatter_Command`.
Phase 3 therefore installs a **portable** `~/.claude/settings.json`, not a per-machine one, and the
same file goes back to the Mac — which is what "match the Mac" was always meant to buy.

**A4 was worse than predicted.** The Mac probe found twelve hooks pointing at Mac-only *programs*
(`~/.conductor/hook.sh` ×11, `~/.claude/notify.sh` ×1), not merely paths. A path can be rewritten;
a program that does not exist on Linux cannot. Phase 6's gate changes from "byte-identical" to
**"identical except a recorded, itemised deviation list"**: the four `allowWrite` paths → `~/`, the
eleven Conductor hooks removed, the notifier hook removed with a Linux notifier as a named follow-on.
Everything else — including all 62 permission rules — travels untouched.

### Phase 3 — installed (portable), containment gate pending the Ubuntu login

The Mac's `~/.claude/settings.json` (100 allow rules, `defaultMode: auto`, a network allowlist,
`excludedCommands` keeping `acli`/`gh` outside the sandbox) was transformed by
[`portable_settings.py`](../../../_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/portable_settings.py)
into **one file for both machines**, committed here as
[`claude-user-settings.portable.json`](claude-user-settings.portable.json) (sha256 `44554a0303dccfaf…`) and
installed as Ubuntu's `~/.claude/settings.json`. On Linux `~/` resolves to `/home/dlohn/…`, on the
Mac to `/Users/sudohatter/…` — verified by `os.path.expanduser` on the installed file.

**The itemised deviation list — this is what Phase 6 checks, not a byte diff.** Generated by the
transform, not typed:

```
== deviations from the Mac file (this IS the Phase 6 list) ==
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command  ->  ~/Sudo_Hatter_Command
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command/.git  ->  ~/Sudo_Hatter_Command/.git
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command/.claude/worktrees  ->  ~/Sudo_Hatter_Command/.claude/worktrees
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command/Projects  ->  ~/Sudo_Hatter_Command/Projects
  hooks.Notification: removed 1 Mac-only hook(s) (notify.sh)
  hooks.Notification: removed 1 Mac-only hook(s) (.conductor/)
  hooks.Notification: event block emptied and removed
  hooks.Stop: removed 1 Mac-only hook(s) (notify.sh)
  hooks.Stop: removed 1 Mac-only hook(s) (.conductor/)
  hooks.Stop: event block emptied and removed
  hooks.SessionStart: removed 1 Mac-only hook(s) (.conductor/)
  hooks.SessionStart: event block emptied and removed
  hooks.UserPromptSubmit: removed 1 Mac-only hook(s) (.conductor/)
  hooks.UserPromptSubmit: event block emptied and removed
  hooks.PermissionRequest: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PermissionRequest: event block emptied and removed
  hooks.PreToolUse: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PreToolUse: event block emptied and removed
  hooks.PostToolUse: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PostToolUse: event block emptied and removed
  hooks.PostToolUseFailure: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PostToolUseFailure: event block emptied and removed
  hooks.SubagentStart: removed 1 Mac-only hook(s) (.conductor/)
  hooks.SubagentStart: event block emptied and removed
  hooks.SessionEnd: removed 1 Mac-only hook(s) (.conductor/)
  hooks.SessionEnd: event block emptied and removed
  hooks.PreCompact: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PreCompact: event block emptied and removed
  allow rule (dead X/:* spelling, SCC-375): Bash(git push -u origin chore/:*)  ->  Bash(git push -u origin chore/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(git push origin chore/:*)  ->  Bash(git push origin chore/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(python3 .agents/scripts/:*)  ->  Bash(python3 .agents/scripts/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(git -C * push -u origin chore/:*)  ->  Bash(git -C * push -u origin chore/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(git -C * push origin chore/:*)  ->  Bash(git -C * push origin chore/*)
== untouched: 102 allow rules, sandbox.enabled=True, autoAllowBashIfSandboxed=True ==
remaining /Users/ references: 0  (must be 0)
```

Every hook in the Mac file was a Mac-only program, so the portable file carries **no hooks** — said
plainly rather than shipping an empty block. A Linux (and Mac) notifier is a named follow-on. The
five dead-spelling rules are the SCC-375 defect; leaving them in a file being written fresh for both
machines would have been knowingly shipping it, so they are a **fourth recorded deviation**, not a
silent fix.

**Gate status:** prerequisites proven (`bwrap` creates a namespace), settings installed, but the
containment probe needs `claude` logged in inside Ubuntu and the Linux clone trusted — at the time
of this commit `~/.claude.json` shows no account and `hasTrustDialogAccepted` false for
`/home/dlohn/Sudo_Hatter_Command`. The login done earlier was the **Windows** `claude`, a separate
install. The probe (`p3_containment_probe.sh`) asks Claude to write to `/etc/` and must be refused,
then inside the repo and must succeed; result recorded when run.

### Phase 3 — GATE PASSED, and it took three probes to make the pass honest

**Probe 1 mis-aimed.** Targeted `/etc/`, which `dlohn` cannot write even *without* a sandbox, so it could
not distinguish the OS fence from ordinary Unix permissions — and Claude declined the command on
policy grounds anyway, exercising nothing. A model refusal is not containment.

**Probe 2 exposed a real hole — in the Mac's config too.** Target moved to `~/scc376-probe.txt`: writable
by the user, outside `allowWrite`, phrased as a task. **The file landed.** Claude's own words were
*"without the sandbox hop"*, and the vendor doc names the mechanism: the **unsandboxed retry escape
hatch** — when bwrap refuses a write, Claude may retry with `dangerouslyDisableSandbox`, and *"in auto
mode the classifier evaluates the underlying command instead of prompting you."* The OS fence held; the
policy let the command back out. The Mac file does not set `allowUnsandboxedCommands`, so the Mac has
this hole today.

**Probe 3 passed.** `allowUnsandboxedCommands: false` (the doc's *Strict sandbox mode*) on the installed
file, then the same three-part probe:

| step | result |
|---|---|
| control — plain `sh -c "echo > ~/scc376-probe.txt"` | **OK** — the path is writable unsandboxed |
| gate A — same write via Claude's Bash tool | **refused by the OS**; Claude: *"the shell sees it as read-only and the file was never created"*; file absent after |
| gate B — write inside `~/Sudo_Hatter_Command` via Claude's Bash tool | **WROTE**, 7 bytes, mode 644; file present after |

This is what "demonstrated, not inferred" was always meant to buy. It is now the **fifth recorded
deviation** in [`portable_settings.py`](portable_settings.py); the installed and committed
[`claude-user-settings.portable.json`](claude-user-settings.portable.json) are byte-identical
(sha256 `1601dff8c5e65189…`). Anything that must run outside the sandbox stays in `excludedCommands`
(`acli`, `gh`, `jira_feed.py`, `task_preflight.py` today). **Consequence for the Mac when it
adopts this file:** Claude can no longer retry outside the sandbox there either — a `git merge`
that hits a protected path will fail with *Read-only file system* instead of offering a retry, and
the fix is `excludedCommands` or running it by hand, per the doc.

The full deviation list, generated by the transform:

```
== deviations from the Mac file (this IS the Phase 6 list) ==
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command  ->  ~/Sudo_Hatter_Command
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command/.git  ->  ~/Sudo_Hatter_Command/.git
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command/.claude/worktrees  ->  ~/Sudo_Hatter_Command/.claude/worktrees
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command/Projects  ->  ~/Sudo_Hatter_Command/Projects
  hooks.Notification: removed 1 Mac-only hook(s) (notify.sh)
  hooks.Notification: removed 1 Mac-only hook(s) (.conductor/)
  hooks.Notification: event block emptied and removed
  hooks.Stop: removed 1 Mac-only hook(s) (notify.sh)
  hooks.Stop: removed 1 Mac-only hook(s) (.conductor/)
  hooks.Stop: event block emptied and removed
  hooks.SessionStart: removed 1 Mac-only hook(s) (.conductor/)
  hooks.SessionStart: event block emptied and removed
  hooks.UserPromptSubmit: removed 1 Mac-only hook(s) (.conductor/)
  hooks.UserPromptSubmit: event block emptied and removed
  hooks.PermissionRequest: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PermissionRequest: event block emptied and removed
  hooks.PreToolUse: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PreToolUse: event block emptied and removed
  hooks.PostToolUse: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PostToolUse: event block emptied and removed
  hooks.PostToolUseFailure: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PostToolUseFailure: event block emptied and removed
  hooks.SubagentStart: removed 1 Mac-only hook(s) (.conductor/)
  hooks.SubagentStart: event block emptied and removed
  hooks.SessionEnd: removed 1 Mac-only hook(s) (.conductor/)
  hooks.SessionEnd: event block emptied and removed
  hooks.PreCompact: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PreCompact: event block emptied and removed
  allow rule (dead X/:* spelling, SCC-375): Bash(git push -u origin chore/:*)  ->  Bash(git push -u origin chore/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(git push origin chore/:*)  ->  Bash(git push origin chore/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(python3 .agents/scripts/:*)  ->  Bash(python3 .agents/scripts/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(git -C * push -u origin chore/:*)  ->  Bash(git -C * push -u origin chore/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(git -C * push origin chore/:*)  ->  Bash(git -C * push origin chore/*)
  sandbox.allowUnsandboxedCommands: (unset = true)  ->  false  (escape hatch closed)
== untouched: 102 allow rules, sandbox.enabled=True, autoAllowBashIfSandboxed=True ==
remaining /Users/ references: 0  (must be 0)
```

### Verifying the PC team's hand-back note (2026-09-02)

A polished note is a claim; each line was checked against the distro.

| the note said | measured | disposition |
|---|---|---|
| gh, acli, claude authenticated in Ubuntu | all three present; claude account `dlohneiss@gmail.com` | **true** (my earlier "not logged in" probe predated the login) |
| — | repo trust dialog **not** accepted (`hasTrustDialogAccepted: false`) | **gap the note missed**; set per Claude's own instruction, recorded above |
| three hook files call Windows binaries (`run-hook.sh`, `session-start-context.sh`, `INDEX.md`) | every hit is a *comment* or the dispatcher's candidate list; `run-hook.sh:52` probes `python3 → python → py`, `:53` `pwsh → powershell` | **rejected** — it is the cross-platform shim working as designed; not a Phase 5 item |
| Java, Firebase CLI, Docker missing | `java`, `firebase`, `docker` all MISSING | **true**; AGY emulator-tier prerequisites, team-owned. Note from the doc: `docker` is incompatible with the sandbox and needs `docker *` in `excludedCommands` |
| `OPENROUTER_API_KEY` → add to `~/.bashrc` | absent in a non-interactive shell | **true that it is absent; wrong home.** `~/.bashrc` returns early for non-interactive shells (A5, and the node/claude symlink finding). `~/.profile` is the reliable home for the VS Code server's login shell |
| — | Claude warned twice: `Bash(git -C * push … chore/*)` in the **project** settings has a wildcard before the subcommand and *"approves any options inserted at that position … -c and --exec-path can run arbitrary commands"* | **new; Phase 5** — the same laundering class as `git -C` in Zoo |

### Phase 3 — the operator's ruling (2026-09-02): match the Mac; never make the agent's job harder

The goal, restated by the operator and confirmed: **the agent works unattended on both machines** — no
prompts, no commands handed back, no per-machine files. Security serves that goal, not the reverse.

Against that goal, closing the unsandboxed-retry hatch was the wrong ship: it never prompted anyone
(auto mode's classifier judges the retried command), and closing it trades a silent success for a
silent agent failure unless the fence is measured wide enough — which would have needed the whole
workload battery first. **Reverted.** The installed file matches the Mac's behaviour: hatch open.
Strict mode stays in [`portable_settings.py`](portable_settings.py) behind `STRICT = False`, with
[`p3_battery.sh`](../../../_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/) as its entry
condition — zero refusals on real workloads, or it does not ship. The containment demonstration above
stands as evidence of what the fence *can* do; it is not what is deployed.

**The notifier is replaced, not dropped.** The Mac's `notify.sh` was macOS-only. The portable
[`notify.sh`](notify.sh) pushes to ntfy (the phone, from either machine — the channel the house
already uses, topic `mac-sudo-command`) and adds whichever desktop banner exists (terminal-notifier
on macOS, notify-send on Linux). Hooks run **outside** the sandbox per the vendor doc, so no network
allowlist entry is needed. The two hooks are back in the portable file pointing at
`~/.claude/notify.sh`, identical on both machines. Tested on Linux with the documented Stop payload
(`last_assistant_message`, `cwd`): exit 0, push sent.

Installed `~/.claude/settings.json` sha256 `fe300a766f337233…`, byte-identical to the committed
[`claude-user-settings.portable.json`](claude-user-settings.portable.json). Deviations now: paths →
`~/`; Conductor hooks removed; notifier **replaced** with the portable one; the five dead `X/:*`
rules respelled. Nothing else differs from the Mac.

```
== deviations from the Mac file (this IS the Phase 6 list) ==
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command  ->  ~/Sudo_Hatter_Command
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command/.git  ->  ~/Sudo_Hatter_Command/.git
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command/.claude/worktrees  ->  ~/Sudo_Hatter_Command/.claude/worktrees
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command/Projects  ->  ~/Sudo_Hatter_Command/Projects
  hooks.Notification: removed 1 Mac-only hook(s) (notify.sh)
  hooks.Notification: removed 1 Mac-only hook(s) (.conductor/)
  hooks.Notification: event block emptied and removed
  hooks.Stop: removed 1 Mac-only hook(s) (notify.sh)
  hooks.Stop: removed 1 Mac-only hook(s) (.conductor/)
  hooks.Stop: event block emptied and removed
  hooks.SessionStart: removed 1 Mac-only hook(s) (.conductor/)
  hooks.SessionStart: event block emptied and removed
  hooks.UserPromptSubmit: removed 1 Mac-only hook(s) (.conductor/)
  hooks.UserPromptSubmit: event block emptied and removed
  hooks.PermissionRequest: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PermissionRequest: event block emptied and removed
  hooks.PreToolUse: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PreToolUse: event block emptied and removed
  hooks.PostToolUse: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PostToolUse: event block emptied and removed
  hooks.PostToolUseFailure: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PostToolUseFailure: event block emptied and removed
  hooks.SubagentStart: removed 1 Mac-only hook(s) (.conductor/)
  hooks.SubagentStart: event block emptied and removed
  hooks.SessionEnd: removed 1 Mac-only hook(s) (.conductor/)
  hooks.SessionEnd: event block emptied and removed
  hooks.PreCompact: removed 1 Mac-only hook(s) (.conductor/)
  hooks.PreCompact: event block emptied and removed
  hooks.Notification + hooks.Stop: re-added, pointing at the PORTABLE ~/.claude/notify.sh (replaces the Mac-only notifier)
  allow rule (dead X/:* spelling, SCC-375): Bash(git push -u origin chore/:*)  ->  Bash(git push -u origin chore/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(git push origin chore/:*)  ->  Bash(git push origin chore/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(python3 .agents/scripts/:*)  ->  Bash(python3 .agents/scripts/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(git -C * push -u origin chore/:*)  ->  Bash(git -C * push -u origin chore/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(git -C * push origin chore/:*)  ->  Bash(git -C * push origin chore/*)
== untouched: 102 allow rules, sandbox.enabled=True, autoAllowBashIfSandboxed=True ==
remaining /Users/ references: 0  (must be 0)
```


### Phase 3 — the Mac is optimised by the SAME file (2026-09-02)

The operator asked what the migration can do for the Mac while we are here. The answer is the design:
there is one file, so every fix the transform makes lands on the Mac the moment the Mac installs it, and
the Mac's own `notify.sh` (pasted 2026-09-02) is now folded into the portable notifier so the swap loses
nothing it did.

| on the Mac today | after the portable file |
|---|---|
| 5 allow rules carry the dead `X/:*` spelling (SCC-375) and match nothing — every `git push origin chore/…` and `python3 .agents/scripts/…` goes to auto mode's classifier instead of the allow list | respelled `X/*`: a deterministic allow, no classifier round-trip |
| the notifier is macOS-only (`/opt/homebrew/bin/terminal-notifier`, `osascript`) | the same banner (context line, first line of the reply, markdown stripped, 140-char cap), the same `Tags: robot` push, the same `~/.claude/last-hook-input.json` debug copy — plus `notify-send` on Linux |
| the push can be LOST: measured on Linux, about 15 ms after a hook's shell exits Claude sends SIGTERM to the hook's process group. The Mac script backgrounds its curl (`… &`) and exits, so that TERM can take the push with it; the banner, being foreground, always lands | the body runs in a detached subshell with its stdio closed and `trap '' TERM HUP INT` — python3 and curl inherit the ignore, the push completes, and the hook returns instantly. Proven through Claude's own hook runner below. Works the same in print mode (`claude -p`) and on a session's last turn, on both machines |
| 11 Conductor hooks on absolute `/Users/sudohatter/…` paths, one per event (PreToolUse and PostToolUse fire on every tool call) | kept and path-portable, each guarded `if [ -x ~/.conductor/hook.sh ]; then …; fi` — runs exactly as before where Conductor is installed, a silent no-op where it is not; the exit code passes through the `if`, so nothing Conductor relies on changes |
| 5 rules prefixed `env -u GITHUB_TOKEN …` — the allow list has been carrying a workaround for a token exported somewhere in the Mac's shell that shadows `gh`'s keychain login | unchanged in the file; [`mac_install.sh`](mac_install.sh) reports whether it is set and which rc file exports it, without printing it. Removing the export at its source retires the workaround — the operator's call once the report names the file |

The Conductor question the previous section left open is closed by the guard: the file no longer needs
to know whether Conductor is in use. Nothing in the file is Mac-only or Linux-only any more; the
`/Users/` count is 0.

**Mac install — one command, with a backup and a pasted-back report.** [`mac_install.sh`](mac_install.sh)
backs up both files with a timestamp, installs from the branch without checking it out, validates the JSON
before anything is replaced, prints the sha256 (must equal `90b39f9f36eb24b8…`), diffs the rules against the backup
(a rule the Mac gained since 2026-09-02 shows as a `-` line and goes into the source file, never lost),
instruments Conductor / `GITHUB_TOKEN` / `core.hooksPath` / node / grep, and fires the notifier with a real
Stop-shaped payload:

    cd ~/Sudo_Hatter_Command && git fetch origin chore/SCC-376-wsl-ubuntu-plan && git show FETCH_HEAD:_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/mac_install.sh > /tmp/mac_install.sh && bash /tmp/mac_install.sh

**Evidence on Linux (this commit):**

| probe | result |
|---|---|
| installed `~/.claude/settings.json` | sha256 `90b39f9f36eb24b8…`, byte-identical to the committed file; `/Users/` count 0; hatch open (Mac behaviour) |
| notifier piped both payload shapes, topic read back from ntfy | `Sudo_Hatter_Command — Done and pushed — first line` and `Sudo_Hatter_Command — Claude needs your permission to use Bash`, tag `robot` — the Mac's exact format |
| the Conductor guard string through `sh` with `hook.sh` absent | exit 0, silent |
| hook env passthrough (throwaway project, sync hook) | `NTFY_TOPIC` reached the hook |
| what kills an async hook's work | a plain `sleep 2; echo` async hook never wrote; a traced detached notifier died mid-`python3`; a timestamped body caught **SIGTERM 16 ms after its start** (its python3 exited 143), continued only because it trapped TERM, and posted; a `setsid` twin was never signalled. A sync hook with a detached body added 0 s to a 4.3 s run |
| **end to end**: Claude's own runner → Stop → `notify.sh` → ntfy, read back | 1 message(s) read back: `Claude Code | Sudo_Hatter_Command — SCC-376 hook e2e` |

Phase 5 scope note: the 20 `git -C *` rules in the **user** file are the same wildcard-laundering class
Claude flagged in the project file — same fix, same commit, both files.

The deviation list, regenerated (this IS the Phase 6 list):

```
== deviations from the Mac file (this IS the Phase 6 list) ==
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command  ->  ~/Sudo_Hatter_Command
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command/.git  ->  ~/Sudo_Hatter_Command/.git
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command/.claude/worktrees  ->  ~/Sudo_Hatter_Command/.claude/worktrees
  allowWrite: /Users/sudohatter/Sudo_Hatter_Command/Projects  ->  ~/Sudo_Hatter_Command/Projects
  hooks: 11 Conductor hook(s) KEPT, path -> ~/, guarded `if [ -x ~/.conductor/hook.sh ]; then ...; fi` (runs as before where Conductor exists; silent no-op where it does not)
  hooks: 2 notifier hook(s) path -> ~/.claude/notify.sh — the PORTABLE notifier (the Mac's banner behaviour folded in; ntfy on both machines; notify-send on Linux)
  allow rule (dead X/:* spelling, SCC-375): Bash(git push -u origin chore/:*)  ->  Bash(git push -u origin chore/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(git push origin chore/:*)  ->  Bash(git push origin chore/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(python3 .agents/scripts/:*)  ->  Bash(python3 .agents/scripts/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(git -C * push -u origin chore/:*)  ->  Bash(git -C * push -u origin chore/*)
  allow rule (dead X/:* spelling, SCC-375): Bash(git -C * push origin chore/:*)  ->  Bash(git -C * push origin chore/*)
== untouched: 102 allow rules, sandbox.enabled=True, autoAllowBashIfSandboxed=True, hooks={'Notification': 2, 'Stop': 2, 'SessionStart': 1, 'UserPromptSubmit': 1, 'PermissionRequest': 1, 'PreToolUse': 1, 'PostToolUse': 1, 'PostToolUseFailure': 1, 'SubagentStart': 1, 'SessionEnd': 1, 'PreCompact': 1} ==
remaining /Users/ references: 0  (must be 0)
```


### Phase 6 evidence — the Mac installed the same file (2026-09-02 14:25)

The operator ran [`mac_install.sh`](mac_install.sh) on the Mac. Measured there, from the pasted report,
and read back from here where a read-back was possible:

| check | Mac | Linux | verdict |
|---|---|---|---|
| `~/.claude/settings.json` sha256 | `90b39f9f36eb24b8` | `90b39f9f36eb24b8` | **identical** — Phase 6's core line holds on both machines |
| allow rules vs the Mac's own backup | 0 removed, 0 added | — | nothing lost. The Mac's live file had already been respelled since the 2026-09-02 paste, so the "5 dead rules on the Mac today" row above describes the pasted file, not the Mac at install time |
| notifier self-test | exit 0; the push read back from the house topic at 14:25:37 as `Sudo_Hatter_Command — SCC-376 Mac install complete: the portable notifier works`, tag `robot` | proven through Claude's own runner above | **both channels live on both machines** |
| Conductor | `hook.sh` present, **Conductor.app not installed** | absent | 11 guarded hooks still fork a dead app's script on every event on the Mac → [`mac_tune.sh`](mac_tune.sh) renames `~/.conductor`; the guard then silences all 11 with the settings file unchanged |
| `GITHUB_TOKEN` | unset; no rc file exports it | unset | the 5 `env -u GITHUB_TOKEN …` rules are inert on both machines; harmless, left in place |
| `core.hooksPath` | global **UNSET**, but the lobby resolves **`.githooks`** from `file:.git/hooks.conf` and AGY from its own `hooks.conf` (read back later, below) | `.githooks` (lobby, local) | armed on both machines at repo level. The install report's "UNSET" read only the global level — instrument fixed |
| node / python3 / grep | v22.23.2 / 3.14.7 / BSD grep 2.6.0 | 22 (LTS) / 3.12.3 / GNU grep | Node 22 on both per the plan. `grep` on the Mac measured as **BSD grep** from a terminal script, while a Claude session on 2026-09-01 measured ugrep 7.8.4 — the shadow depends on the launch context, so gates keep using counts, never `-q` |

One stray push: a probe at 14:17 ran without a self-test topic and sent `hookprobe — ok` to the house
topic. Mine; no action.

**2026-09-02, later — [`mac_tune.sh`](mac_tune.sh) read back from the Mac (the operator pasted a re-run).**
Both items are now measured, not reported. `~/.conductor` is **absent** — "nothing to do; hook.sh
absent, the 11 hooks are silent no-ops" — so the first run had already renamed it. And `core.hooksPath`
was **armed all along**: from inside the lobby it resolves to `.githooks` with origin `file:.git/hooks.conf`
(the SCC-323 include shape, repo-local), AGY resolves the same from its own `hooks.conf` under
`.git/modules/`, and the payload is the full set (commit-msg, post-checkout, post-commit, post-merge,
post-rewrite, pre-commit, pre-push). The install report's "core.hooksPath: UNSET" was my instrument
reading the **global** level only — the pointer measured at the wrong level, the scar
`hooks-armed-measures-pointer-not-payload` one level down. The tune script was right to leave global
alone (it arms only when unset at every level). Fixed in [`mac_install.sh`](mac_install.sh): it now
prints the effective value with its origin from inside the lobby, and the global level separately.
Phase 6's two Mac rows close here.

**Tree cleanup, 2026-09-02, operator-approved.** The PC checkout (on `main`) carried drift no lane owned.
Measured, then acted on:

| item | what it was | action |
|---|---|---|
| `.claude/settings.json` (modified) | rewritten by Claude on the PC during SCC-375: one throwaway allow rule for a `wsl.exe … test_sops_prds_folder.py` command, three rules dropped, keys reordered — unreviewed | reverted to `HEAD` |
| `.vscode/settings.json.bak-llm-approvals` | the pre-SCC-373 backup of the Zoo approvals file; the live file is committed | deleted |
| `scratch/mutation_sweep_24_7.py` | AviationChat story 24.7's mutation-sweep evidence, cited by that story's walkthrough at this exact path | **stays** until AVCH-109 closes; that lane moves it into the story's own artifacts before close-out |
| three `_artifacts/_memory/` edits | this session's (hook SIGTERM memory, grep correction, index) | committed on this lane at `1293a058`; they clear from the tree when the lane lands |
| five memory deletions seen earlier | SCC-377's deliberate retirement, merged on `main` | nothing; the Linux clone's memory-store guard was re-baselined to acknowledge it |

### Phase 4 — the Desktop Team's paste issued; every mechanic proven on this PC first (2026-09-02)

The operator asked for one copy-and-paste command for the Desktop Team. Each thing the paste relies on
was measured or exercised on the PC first; three of the plan's assumptions did not survive contact.

| the plan assumed | measured | consequence |
|---|---|---|
| VS Code already talks to WSL | `ms-vscode-remote.remote-wsl` was **not installed** on Windows, and `~/.vscode-server` did not exist in Ubuntu — the distro had never been connected | installed here from the CLI (v0.104.3). It lives in the extensions dir both instances share, so `code2` has it too |
| "install the extensions into Ubuntu" is one command | `code --remote wsl+Ubuntu --install-extension …` is **silently ignored** — it reported the Windows copies as already installed and the distro stayed empty. The working path is VS Code's own shim run *inside* the distro (`/mnt/c/Microsoft VS Code/bin/code --install-extension …`): it downloads the server headlessly and installs into `~/.vscode-server/extensions` | done here for Ubuntu — Claude Code 2.1.258, Zoo Code 3.81.100433 (pinned to the Windows version; it is a pre-release channel), Python 2026.4.0 with debugpy, pylance and envs: 6 dirs. The export carries them into zoo2 |
| `code .` keeps working from an Ubuntu terminal | Phase 1's `appendWindowsPath=false` took the Windows shim off PATH | the paste symlinks `/usr/local/bin/code` to the shim — the same scar the node/claude symlinks closed |
| Java, Firebase CLI and Docker are all missing (the hand-back note) | Firebase CLI: `firebase/tests/node_modules/.bin/firebase` from Phase 2's `npm ci`; nothing global needed. Docker: AGY runs `docker` only inside the GitHub deploy workflow — no local tier needs it, and the vendor doc says it is incompatible with the sandbox | **Java 17 is the one real gap** (rules + e2e emulator tiers; the two orchestrators have no Linux discovery branch, so `JAVA_HOME` must be set). The paste installs `openjdk-17-jre-headless` and puts `JAVA_HOME` in `~/.profile` (the VS Code server probes an interactive login shell, so `~/.profile` is what it reads; `~/.bashrc` is not). Docker Desktop's WSL toggle stays **off** for both distros; the Firebase CLI needs nothing |
| `OPENROUTER_API_KEY` → `~/.profile` | its only consumer is `autopilot-dev-story.ps1`, and `pwsh` is not installed in Ubuntu — there is no Linux consumer yet; when the engine is ported it reads a gitignored `.env` | not persisted anywhere; nothing to do |
| the two-instance rig and the roster | the roster is project-level (`.roomodes` at the repo root plus `.roo/`), so it travels with every clone; the Windows-side `custom_modes.yaml` / `mcp_settings.json` are 16- and 26-byte empties. Under Remote-WSL, Zoo runs *inside* the distro, so its globalState (model, approvals, keys) lives in `~/.vscode-server/data/User/globalStorage/` **there** — one per distro | this is exactly why two distros isolate two seats. The provider profile is imported once per distro by hand (`zoo-code.importSettings` exists). **Phase 5 consequence:** `zoo_permissions_apply.py` knows only the Windows and Mac paths today and must learn the distro path, run from inside each distro |
| export/import carries the user | an imported distro has no launcher, so its default user comes from `/etc/wsl.conf` — `[user] default=dlohn` from Phase 1, carried by the image | the paste verifies `whoami`=dlohn and a Windows PATH leak of 0 inside zoo2 |
| — | the export also copies `~/.claude/.credentials.json`; two distros sharing one OAuth session invite a silent logout of the primary | the paste removes the copy in zoo2 (Zoo's seat; `claude /login` there if ever needed) |

The paste is [`phase4_pc.ps1`](phase4_pc.ps1): preconditions, the Linux half in Ubuntu (Java, profile,
`code` door, extensions, probe), a hard stop for the operator to close every window, `wsl --shutdown`,
`wsl --export … --vhd` (a block copy of the 21.6 GB disk; C: has 1.3 TB free), `wsl --import
Ubuntu-zoo2 … --vhd --version 2`, the strip-and-probe in zoo2, `code2.cmd` rewritten to land on
`wsl+Ubuntu-zoo2` (the old launcher kept as `code2.cmd.bak-scc376`, the isolated user-data-dir and
the clone-sync untouched), then the report. It is re-runnable, prints no secret, and keeps the
exported `.vhdx` as the Phase 3 snapshot. The gate at the end is by hand, and the reload is what
keeps it honest: change the model in instance 2, **reload instance 2** (proves the change was saved),
**reload instance 1** (proves it re-read its own state), instance 1 unchanged.

Already done on the PC before the paste was written, both in Phase 4's own scope: the Remote-WSL
extension on Windows, and the three work extensions inside Ubuntu.

### Phase 4 — CLOSED, gate PASS (Desktop Team, 2026-09-02); the close-out note verified line by line

The Desktop Team's note is a claim; each line was checked against both distros and the Windows side.

| the note said | measured | disposition |
|---|---|---|
| gate PASS — different models in the two instances; instance 1 unchanged after a reload | the two **Windows** stores carry Zoo's state with different models: primary `gtp 5.6-sol` (zoo-gateway), isolated `glm 5.3-flash` (openrouter). No `state.vscdb` exists anywhere under either distro's home. The remote extension-host log shows Zoo activating **inside Ubuntu** at 16:50, 16:56 and 17:13 | **true**, and measured independently of the screen. It also corrects my Phase 4 record — below |
| zoo2 probe: `dlohn`/1001, PATH leak 0, ext4, `JAVA_HOME` set, Claude login stripped, 6 extensions | re-measured identical. Ubuntu: 7 extensions (the team added `github.vscode-pull-request-github`; harmless), its Claude login present as intended. Both: `JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64`, openjdk 17.0.20 from a login shell | **true** |
| integrity: 157,047 files both, submodules 10/10, `git fsck` clean, 17G both | submodules 10/10 in both; head `28cc443f` in both; Ubuntu clean; **zoo2 has one modified file**, `docs/repo-map.md` (5 lines each way — the map recorder regenerated a cache inside zoo2; `git checkout -- docs/repo-map.md` there when that seat is idle) | true for what was re-run; the file count and fsck are the team's numbers |
| export 20.10 GB, import rc=0, `code2` → `wsl+Ubuntu-zoo2`, old launcher kept | both vhdx are 21,587,034,112 bytes (20.10 GiB); `code2.cmd` is the paste's, `code2.cmd.bak-scc376` is the old one; the transcript ends 16:07:07 | **true** |
| deviation 1 — the code door opened a *Windows* window | not reproducible from here. The shim's mechanism explains the symptom: it asks `Code.exe` to locate the Remote-WSL extension and, if that answer comes back empty, falls through to a plain local window with the Linux path as its argument. VS Code **updated** between my install (commit `08d4889f`, the `new_code*` files staged in `bin\` that afternoon were the pending update) and the team's run (`520fb30b`); the server in both distros is `520fb30b2d`, re-downloaded | owned by the team; `code1.cmd` is the right door and the paste's gate now says so |
| deviation 2 — the shim broken, then restored with the versioned path | `bin\code` now carries `COMMIT=520fb30b…` with its three `cli.js` references hard-coded to `520fb30b2d\resources\app\out\cli.js` (the vendor's own file reaches the same folder through a `VERSIONFOLDER` variable); `/usr/local/bin/code` in **both** distros is a 3-line real file that `exec`s the shim | works. The updater rewrites `bin\` on the next update, so the hand patch is transient by design. The paste's `ln -sfn` would have replaced that real file with a symlink on a re-run — **now guarded**: the door is created only when nothing is there |
| deviation 3 — `code1.cmd` added | present; mirrors `code2.cmd` without the isolated user-data-dir and without the clone-sync | **adopted**: the paste creates it when absent, and gate step 1 reads `code1` |

**Correction to the Phase 4 record above.** Zoo *does* run inside the distro (the workspace extension
host), but its `globalState` — model, profiles, approvals — is kept by the window on the **local** side,
in that instance's user-data-dir `state.vscdb`, not in the distro: measured, not assumed (Zoo active in
the remote host; no state file in the distro; both models in the two Windows stores). So the two Windows
user-data-dirs are what isolate the two seats' models, exactly as before the migration; the second distro
isolates the shell, the clone and Claude's own process. **Phase 5, corrected:** `zoo_permissions_apply.py`
needs no distro path — but it does not cover the isolated instance's store either
(`vscode-isolated/User/globalStorage/state.vscdb`; it lists the default profile and named profiles
only), so Phase 5 adds that candidate and applies to **both stores**. Zoo's file-based settings (custom
modes, its MCP list) are the part that lives on the extension-host side, in the distro — both empty
stubs; the roster is `.roomodes` and travels with the clone.

**AGY's ticket minted, as this plan said it would be when Phase 4 closed: AVCH-116** — the port of the
lobby's landed Phase 5 shape into AGY's own `.claude/settings.json`, with the six port-checklist
questions answered in its plan first, sequenced after Phase 5 lands on `main`, Zoo's side left with
AVCH-114. Outline: [`tickets/AVCH-116.md`](tickets/AVCH-116.md).

Phase 4 is closed. Phase 5 is next and is mine.

### Phase 5 — LANDED (2026-09-02): ONE commit, and the fence now reads as what the two machines run

Everything Windows-shaped is out of the tracked permission files, in one revertable commit, with the
tests amended in the same commit so the tree never carried a red. Every number below was measured in the
Ubuntu clone, not copied from the audit.

| file | before → after | what moved |
|---|---|---|
| `.vscode/settings.json` (Zoo allow) | **143 → 124** | **22 out by exact match**: the 21 Windows-shaped rows (the audit counted 20 — it missed that both `backend/.venv/Scripts/` and `.venv/Scripts/python.exe -m pytest` are Windows spellings) plus bare `python `, which resolves on neither machine (Ubuntu: `command -v python` empty; the Mac: python3 only). **3 in** per F3: `.venv/bin/python -m pytest`, `.venv/bin/ruff check`, `firebase/tests/node_modules/.bin/firebase emulators:exec`. `dirname ` survives (F4). Deny list untouched at 105. `python.defaultInterpreterPath` → `backend/.venv/bin/python` — it had pointed at `Scripts/python.exe` on the Mac all along. The SCC-338 / SCC-373 comment blocks are replaced by one SCC-376 note that keeps the laundering-prefix refusals (`if exist `, `ForEach-Object`, `find `, bare `del`) on record |
| `.claude/settings.json` (tracked Claude allow) | **161 → 141** | 7 Windows-only rules out (`export MSYS_NO_PATHCONV=1`, the five bare-`python` rules, `backend/.venv/Scripts/*`) and the **13 `git -C *` wildcard rules** — Claude's own warning: a wildcard before the subcommand approves any option at that position, and `-c` / `--exec-path` there run arbitrary commands; command-shape.md rule 1 already bans the spelling, and `cd <abs> && git <verb>` is judged per piece and allowed |
| `claude-user-settings.portable.json` (the ONE user file) | **102 → 82** rules | the 20 `git -C *` rules, dropped by the generator's new step 6 and itemised in its deviation list like every other change. sha256 **`e1a13e0d126f0478…`** (was `90b39f9f…`). Installed in Ubuntu and Ubuntu-zoo2; the Mac re-runs its one-liner |
| `test_settings_allowlist.py` | A3 rewritten, A6 added | A3 is one-directional now — python3 rules exist and no bare-python rule remains; the twin requirement pinned the shape the migration leaves behind (A3 amendment, as declared). A6 pins the removals: no `\Scripts\` / `.exe` / `MSYS_NO_PATHCONV` spelling and no `git -C *` rule, so a "promote what got blocked" pass cannot quietly reverse this commit. 29/29 |
| `zoo_permissions_apply.py` + `test_zoo_permissions.py` | `candidate_dbs` grows two candidates | the isolated `code2` seat (`~/vscode-isolated/User/globalStorage/state.vscdb`, on every platform) and, **under WSL, both Windows stores through `/mnt/c`** — the Phase 4 correction made real: Zoo keeps its state on the Windows side, so the apply runs from Ubuntu and needs no Windows checkout. `vscode_running` asks `tasklist.exe` by full path (the distro's PATH carries no Windows entries; unable to ask = treat as running). **Found by running it, not by reading:** `/mnt/c/Users` holds other accounts (`CodexSandboxOffline`, `Default`) that raise `PermissionError` on stat, and pathlib propagated it out of the first `is_dir()` — an unreadable account now reads as absent, with the chmod-000 half in the test. 23/23 |
| `docs/migrations/zoo-code-permissions-guide.md` | §2, §6, §7, §11 | the second seat's store and the PC-stores-are-Windows-side fact (§2); the count line `124 allow / 105 deny`, the Interpreters row, a "Windows rows left with the PC" note and a Test-toolchain family row (§6, `test_guide_currency` green); the from-Ubuntu procedure (§7); the Claude row no longer cites `git -C *` (§11) |
| `.agents/rules/jira.md` | guardrail 5 | the Linux row: no credential store inside Ubuntu, so `acli` keeps the token in its own config under `~/.config/acli/` (mode 600, the operator's home); it goes in on stdin, never as `--token "$VAR"` |
| `.agents/hooks/shape-guard.py` | rule-1 nag text | it no longer tells the agent that "a handful of verbs with an explicit `git -C * <verb>` rule get through" — none do now |

**Gate — `python3 .agents/scripts/tests/run_all.py`, bare, inside Ubuntu: 71/71 files passed, rc 0, 26 s.**
Bare per file: `test_settings_allowlist` 29/29 · `test_zoo_permissions` 23/23 · `test_allow_readonly_chain`
153/153 (the Linux number, A2) · `test_allow_scratchpad` **187/187 — case E, the uid case that could never
pass on Windows, passes natively; the SCC-375 open item is closed by the migration itself, no edit needed.**

**The apply script, run from Ubuntu with VS Code open (`--status` is read-only), sees both Windows stores:**

```
/mnt/c/Users/dlohn/AppData/Roaming/Code/User/globalStorage/state.vscdb      (instance 1, code1)
  allowedCommands: 170  (DRIFT: 6 tracked entries missing from store, 52 store-only entries)
  deniedCommands:  106  (DRIFT: 0 tracked entries missing from store, 1 store-only entries)
  autoApprovalEnabled: True   alwaysAllowExecute: True   destructiveCommandGuardEnabled: False
/mnt/c/Users/dlohn/vscode-isolated/User/globalStorage/state.vscdb            (instance 2, code2)
  allowedCommands: 123  (DRIFT: 6 tracked entries missing from store, 5 store-only entries)
  deniedCommands:  105  (in sync with tracked file)
  autoApprovalEnabled: None   alwaysAllowExecute: False
  WARNING: master toggles off - no list is consulted until autoApprovalEnabled AND alwaysAllowExecute are on
```

Two facts from that read that Phase 6 has to act on. The primary store carries **52 store-only rows** —
learned approvals and their fragments — that the apply wipes by design (the SCC-369 reasoning; the
tracked file is the policy). And **the `code2` seat's master toggles are OFF**: until they are switched on
in that instance's Zoo Auto-Approve panel, the second seat consults no list and asks for everything —
which is the state the Desktop Team saw as "instance 2 works" during the Phase 4 gate, because a seat
that asks for everything is never wrong, only slow.

**What Phase 5 could not do from a VS Code-hosted session on the Windows side, handed to Phase 6 as
its first lines:** (1) the apply itself — it refuses while `Code.exe` runs, by design, and this session
is `Code.exe`; the SQLite write over drvfs was proven separately (create, update, `copy2` backup, all on
`/mnt/c`); (2) the `code2` toggles — a click in that window; (3) retiring the Windows
`%USERPROFILE%\.claude\settings.json` — a rename, reversible; (4) the Windows clone
`C:\Sudo_Hatter_Command` — it holds **six uncommitted files from other sessions** (two modified and four
untracked memory files under `_artifacts/_memory/`, plus AVCH-109's `scratch/mutation_sweep_24_7.py`),
so deleting it is the operator's word, after those are carried over or committed by their owners. Nothing
else Windows-shaped remains.

Phase 5 is landed. Phase 6 is the Desktop Team's; its paste follows in the next commit.

### Phase 6 — the Desktop Team's paste issued (2026-09-02); every Linux mode proven in both distros first

Phase 6 is the Desktop Team's sign-off, and after Phase 5 it is four Windows-side actions plus the
eight-line checklist, so it ships the way Phase 4 did: ONE paste, [`phase6_pc.ps1`](phase6_pc.ps1), run
in PowerShell with **both VS Code windows closed** (it refuses while `Code.exe` is alive — the Zoo apply
writes the two stores VS Code overwrites on exit). It is idempotent, so it is re-run after the one click
it cannot make.

    cd C:\Sudo_Hatter_Command; git fetch origin chore/SCC-376-wsl-ubuntu-plan; git show FETCH_HEAD:_artifacts/_main/2026-09-02_SCC-376-wsl-ubuntu-migration/phase6_pc.ps1 | Out-File -Encoding ascii $env:TEMP\phase6_pc.ps1; powershell -NoProfile -ExecutionPolicy Bypass -File $env:TEMP\phase6_pc.ps1

| step | what it does | proven before issue |
|---|---|---|
| 1 | syncs both distros' clones to the lane (dropping zoo2's regenerated `docs/repo-map.md`, the Phase 4 remedy) and installs the ONE user file in each | run now in both: `clone: 9ab2ae82, 0 dirty`; `user file: sha e1a13e0d126f0478 (committed: e1a13e0d126f0478)`; zoo2's cache dropped |
| 2 | `zoo_permissions_apply.py --apply` **from Ubuntu**, into both Windows stores, then `--status`; counts the four *in sync* lines and the stores whose master toggles are ON | the refusal path from Ubuntu: `REFUSED: VS Code is running`, rc 2 (this session is `Code.exe`); the SQLite write over drvfs proven on a throwaway db (Phase 5 log); `--status` reaching both stores (Phase 5 log) |
| 3 | renames `%USERPROFILE%\.claude\settings.json` → `.retired-scc376` (reversible) | a rename; nothing to prove |
| 4 | reports the Windows clone's uncommitted files and **does not delete it** | the six files are other sessions' memory files and AVCH-109's scratch; the operator says when |
| 5 | probes both distros (user/uid, PATH leak, filesystem, which binaries resolve, sandbox flag, the tracked lists' Windows-row count) and runs the lobby gate bare inside Ubuntu | run now in both: `user=dlohn uid=1001`, `PATH leak=0`, `windows binaries resolving: 0`, `sandbox.enabled=True`, `zoo 124 rows, 0 Windows-shell rows`, `claude 141 rows, 0 Windows-shell rows, 0 git -C rows`; gate `71/71 files passed`, rc 0 |
| 6 | prints the eight checklist lines against those live values, naming the recorded gates (Phase 3 containment, Phase 4 isolation) where a line is a record rather than a re-run | — |
| 7 | the ONE by-hand click: the `code2` seat's Zoo Auto-Approve master toggle and Execute (its store reads them OFF), then re-run the paste; line [5] must read 2 of 2 | the toggle state was read from the store (Phase 5 log) |

**The Mac's half is the operator's one-liner, unchanged** — [`mac_install.sh`](mac_install.sh) re-run installs the
regenerated file; its sha must print `e1a13e0d126f0478`, and its rules diff will show exactly 20 `-` lines,
all `Bash(git -C * …)`, removed on purpose (the script now says so). Anything else in that diff is news.

Phase 6 passes when the pasted transcript reads: 4 of 4 in-sync lines, 2 of 2 stores with toggles ON, both
probes clean, the gate green, the Windows user file retired, and the Mac's sha equal.

### Phase 6 evidence — the Mac installed the Phase 5 file (operator paste-back, 2026-09-02 18:22)

The operator re-ran the one-liner on the Mac. Read line by line against what Phase 5 committed:

| line | the Mac printed | disposition |
|---|---|---|
| sha256 | `e1a13e0d126f0478` | **equal** to the committed file and to both distros — checklist line [7] holds on the Mac side |
| rules / mode / sandbox | 82 · `auto` · sandbox on · hatch open | the Phase 5 file, Mac behaviour preserved |
| rules diff vs the backup | 20 removed, 0 added; all twenty `Bash(git -C * …)` | exactly the expected set; no Mac-grown rule lost |
| Conductor | `hook.sh` absent, app not installed | the 11 guarded hooks stay silent no-ops |
| `GITHUB_TOKEN` | unset in this shell; exported from nowhere | the five `env -u GITHUB_TOKEN` rules are now pure redundancy on the Mac, harmless |
| `core.hooksPath` | `file:.git/hooks.conf .githooks` from the lobby; global unset | armed, as the tune read-back found |
| node / python3 / grep | v22.23.2 · 3.14.7 · BSD grep 2.6.0 | the pinned Node; BSD grep in this launch context (the ugrep scar is context-dependent) |
| notifier | exit 0 | banner and push fired on the Phase 5 file |

The Mac needs nothing further from this ticket. Phase 6 now waits only on the PC paste's transcript.

### Phase 6 — the Desktop Team's transcript verified line by line (2026-09-02); seven of eight held, line [5] did not

The team ran the paste and reported all eight lines clean. Seven are. **Line [5] was reported PASS by a
counter that could not count**, and the store it certified was fenced by nothing.

| the transcript said | measured here, after the run | disposition |
|---|---|---|
| both clones at `803e6ca1`, 0 dirty, user file sha equal in both | identical | **true** |
| Zoo apply: both stores `in sync with tracked file`, 124/105 | identical, and the backups exist (`state.vscdb.scc-backup`, 17:08 and 18:27) | **true** |
| `in-sync lines: 8 of 4` · `master toggles ON: 2 of 2` | **wrong, and it is the same defect twice.** `--apply` prints its status block, then the script printed `--status` again, so every line was counted twice; and `autoApprovalEnabled: True` was counted across BOTH stores' blocks. The isolated store's own bytes: `alwaysAllowExecute: false`, `autoApprovalEnabled` **absent** | **line [5] FAILS.** The `code2` seat has had a perfectly synced allow list and no fence switch: it consults no list at all and asks for everything |
| Windows `~\.claude\settings.json` retired | `settings.json.retired-scc376`, 12,179 bytes, 18:12 — **and a new 71-byte `settings.json` appeared at 18:42** carrying two notification preferences and nothing else | **true, and harmless**: a Windows-side Claude session rewrote its own preferences file. It carries no permissions, no hooks and no sandbox block, so nothing is fenced by it |
| Windows clone reported, 7 files, not deleted | identical 7 | **true** (the plan said 6; the seventh is `MEMORY.md`, also another session's) |
| probes, both distros: uid 1001, PATH leak 0, ext4, 0 Windows binaries, 0 Windows rows, 0 `git -C` rows | identical | **true** |
| gate `71/71`, rc 0, bare inside Ubuntu | identical | **true** |

**Finding 1 (the team's), adopted.** `wslpath -u $WINTMP` returns empty because PowerShell strips the
backslashes passing the path through `wsl.exe`, so every Linux step ran with no script. Their manual
`/mnt/c/…` construction — the shape `phase4_pc.ps1` already used — is now the committed line, with the
reason written above it.

**Finding 2 (the team's), rejected on measurement.** The claim was that both seats now run Remote-WSL, so
Zoo's live state moved into each distro's `~/.vscode-server/data/User/globalStorage/state.vscdb`, making
the Windows-store check the wrong thing. There is **no `state.vscdb` anywhere under either distro's
`.vscode-server`** — only a `zoocodeorganization.zoo-code` *directory*, which is the extension's
file-based storage (tasks, its MCP list), not the memento database. Meanwhile the two Windows stores
carry the two seats' different models right now — primary `gtp 5.6-sol`, isolated `glm 5.3-flash` — and
their mtimes move as the seats are used. The Windows stores are the decision stores; the check measures
exactly the right thing. This is the same correction Phase 4's close-out made, and it is worth stating
twice because it is genuinely counter-intuitive: **the extension host runs in the distro, the window's
`globalState` stays local.**

**Both defects fixed in the paste, and the remaining action is a command, not a click.**
`zoo_permissions_apply.py` gains `--enable-auto-approve` (with `--apply` only): it turns
`autoApprovalEnabled` and `alwaysAllowExecute` **on** in any store where they are off, touches no other
key, never turns one off, and backs up first — both halves pinned by a new case in
`test_zoo_permissions.py` (24/24). The paste's step 2 now uses it, and its summary is **computed by
re-reading the stores** rather than scraped from printed lines: one `VERDICT stores=N in-sync=N
toggles-on=N` line, and a closing `PHASE 6: all eight lines hold.` only when every count is full. Step 7
no longer asks for a Zoo panel click; it says what a short count means (a VS Code process still alive
when step 2 ran).

I could not run the toggle write from here: this session **is** VS Code, and the guard refused — which is
the guard working. It needs one re-run of the paste with the windows closed.

Phase 6 is not signed off. It is one paste away.

### Phase 6 — PASS (Desktop Team, 2026-09-02, second run); all eight lines hold, and the counts are computed

The corrected paste was run from `7f6b4171` with every VS Code window closed, exactly as issued, no local
patches. Verified against the stores from here afterwards.

| line | evidence in the transcript | re-measured |
|---|---|---|
| [1] sandbox ACTIVE | `sandbox.enabled=True` in both distros; containment demonstrated at the Phase 3 gate | — (recorded gate) |
| [2] zero Windows binaries | `windows binaries resolving: 0`, `PATH leak=0`, both distros | yes |
| [3] repo on the Linux disk | `clone fs=ext2/ext3` (how `stat` names the ext4 family), both | yes |
| [4] suites green from WSL, bare | `run_all rc=0 :: 71/71 files passed` | yes, same numbers here |
| [5] both seats isolated **and fenced** | `applied … [master toggles turned ON: autoApprovalEnabled, alwaysAllowExecute]` on the isolated store, then `VERDICT stores=2 in-sync=2 toggles-on=2` | yes — both stores read lists in sync, toggles ON |
| [6] no Windows rows in either list | `zoo 124 rows, 0 Windows-shell rows | claude 141 rows, 0 Windows-shell rows, 0 git -C rows` | yes |
| [7] user file == the committed portable file | `sha e1a13e0d126f0478` in both distros; the Mac printed the same at 18:22 | yes |
| [8] normal user | `user=dlohn uid=1001`, both | yes |

`PHASE 6: all eight lines hold.` The second seat's fence switch went on during this run — the first run
had certified it while it was off — and the count that says so is now computed from the stores, not
scraped from printed lines.

**One defect in the paste, found by the team in this run and fixed.** Step 3 printed
`renamed -> …retired-scc376` while PowerShell's own error above it said the rename had failed: with
`$ErrorActionPreference = 'Continue'`, a failed `Rename-Item` writes its error and the success string on
the next line still runs. The file at `~\.claude\settings.json` is the 71-byte preferences file a
Windows Claude session rewrote after the first run (`agentPushNotifEnabled`, `inputNeededNotifEnabled` —
no permissions, no hooks, no sandbox). Step 3 now **checks the result and classifies the file**: it
reports "left in place … preferences only, it fences nothing" when the retired copy already exists and
the current file carries no fencing key, prints `RENAME FAILED` if a rename it attempted did not happen,
and **stops** if a file carrying `permissions`/`hooks`/`sandbox` ever reappears beside an existing
retired copy. A retire step that reports success over a file it did not move is the one thing it must
never do.

**Phase 6 is signed off.** Phase 7 is the last step of this ticket and is mine.

### Phase 7 — LANDED (2026-09-02): three permission pages became one, and the Antigravity leftovers are gone

**One guide.** [`docs/migrations/terminal-permissions-guide.md`](../../../docs/migrations/terminal-permissions-guide.md)
— 560 lines, replacing 374 + 173 + 27. The Zoo page is the spine and was carried **section for section,
verbatim**, with every internal `§N` reference remapped by a script rather than by eye; the cross-agent
front door became §1 and the Claude page became §3, rewritten rather than copied because its content was
Windows-shaped (`\Scripts\` venvs, `powershell.exe`, `c:/` write boundaries) and carried
machine-absolute `file:///Users/…` links — both of which this ticket retired. New §14 lists the command
that verifies each claim. The three old pages are deleted; their names survive as prose in the note that
says so, for anyone arriving on an old bookmark.

**The currency test no longer keys on section numbers.** `test_guide_currency` sliced `## 6.` to `## 7.`
to find the canonical lists. A merge that renumbers every section would have made it slice a different
chapter — or raise `IndexError` inside the one test whose job is to notice staleness. The lists now sit
between `<!-- CANONICAL-LISTS:START -->` / `END` markers that travel with the content, and a **control
case** asserts the slice is a real one (over 2,000 chars and containing a family table), because a
marker pair that bound nothing would let the scan certify a guide it never read.

**Three tests pinned the shape this phase removes — the same class three times.** Each was amended in
this commit, never afterwards: `test_settings_allowlist` **B4** required the retired
`google.google-antigravity` recommendation (now inverted: it must be absent);
`test_command_surfaces` **CS-15 A** required all four platform MCP configs to exist, including the
Antigravity one being deleted (now three live platforms, with **CS-15 A2** asserting the retired config
does not come back); and `test_guide_currency` above. This is the A3 / A2b family the audit named at the
start, and it has now fired at every phase that deleted anything.

| deleted | why |
|---|---|
| `terminal-global-permission.md`, `claude-terminal-permission.md`, `zoo-code-permissions-guide.md` | absorbed, section for section |
| `.antigravity/mcp.json` | a config for a platform nobody runs (SCC-349) |
| `docs/migrations/antigravity_extensions/` (3 files) + its `INDEX.md` row 10 | the extension-carry guide for that platform |
| the `google.google-antigravity` workspace recommendation | it offered a fresh clone the retired IDE |

Retiring Antigravity as a **platform** — its command surface, its workflow launchers, `platforms:`
declarations — remains **SCC-378**, deliberately not this ticket.

**Gate: `run_all.py` 71/71 files, rc 0, bare, inside Ubuntu.** `check_maps` and `check_links` were run
against a clean clone at the same head first, so the difference is attributable: the only unresolved
paths this phase adds are the plan's own DELETE declarations pointing at the files it declares deleted,
which is what a declaration is for. The guide contributes one, a `/tmp/…` filename quoted as an example
of store debris, carried from the old page. Three map findings pre-date this lane and are untouched by
it (a dead `auth_keys` path in two places, a missing level-2 INDEX under `.agents/templates/`).

**SCC-376 is complete.** Phases 0-7 are closed, both machines run the same portable file, both Zoo seats
are fenced, and the gate is green from inside WSL. What remains is downstream and already ticketed:
**AVCH-116** (AGY's port of this shape, after this lands on `main`) and **SCC-378** (the Antigravity
platform retirement).
