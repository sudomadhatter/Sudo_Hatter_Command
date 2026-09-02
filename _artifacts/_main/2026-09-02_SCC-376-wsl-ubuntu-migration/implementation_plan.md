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

**And the one gate most likely to fail, which should be proven on day one rather than at Phase 2's
end:** `acli` authentication. The house's entire Jira integration is `acli`, and the rule that governs
it says the token lives in the OS credential store — *"the macOS keychain on the Mac, the Windows
equivalent on the PC."* Linux has neither. Whether `acli` on Linux can reach a credential store in a
headless WSL distro is **unverified from here**, and it is a hard dependency of every close-out, every
Dev Record and every board transition.

**Amendment — Phase 1 proves `acli jira auth status` returns authenticated inside Ubuntu before Phase
2 begins.** If it cannot, that is a blocker to surface immediately with the fallback named (a
credential helper, or `$JIRA_API_TOKEN` from the operator's store), not a surprise discovered at
sign-off.

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
acli jira auth status                          # ✓ Authenticated  ← the A5 blocker
```

Every path is `/usr/…` or `/home/…`. Zero `/mnt/c`.

### Phase 2 — Repo and venvs · Team

Clone to `/home/dlohn/Sudo_Hatter_Command` on the Linux disk, **not** `/mnt/c`. Rebuild every venv as
a Linux venv — `.venv/Scripts/` ceases to exist, `.venv/bin/` is the only form. Arm the git hooks
per-machine (`git config --global core.hooksPath .githooks` — hooks are local config and a fresh clone
has none).

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

Everything Windows-shaped comes out, in a single revertable commit:

- `.vscode/settings.json` Zoo allow list — every Windows-shell row: `dir`, `type `, `findstr`,
  `where `, `del scratch\`, `set "JAVA_HOME=`, `Write-Host`, `Get-Item`, `Get-ChildItem`, `Select-*`,
  `Test-Path`, `Write-Output`, `more`, and every `backend\.venv\Scripts\` / `.venv\Scripts\` /
  `.venv_stale\` backslash row.
- `.claude/settings.json` — the same pass: any `\Scripts\`, `.exe`, or Windows-only rule.
- **A3's amendment lands in this same commit** — the interpreter-twin case is rewritten as the bare
  `python` rules are deleted, not afterwards.
- AGY's allow list — **this is a separate repo and needs its own AVCH ticket** (cross-repo work takes
  a ticket per repo; a lobby ticket editing files inside AGY produces a commit no AVCH ticket accounts
  for). Mint it when Phase 4 closes, not now.
- Retire the Windows `~/.claude/settings.json` and the Windows repo clone.
- `zoo_permissions_apply.py --apply` on **both** distros, VS Code fully closed (SQLite single-writer).
- `test_allow_scratchpad` case E — the uid case that could never pass on Windows — passes natively.
  The SCC-375 open item closes here.
- Guide §6 counts updated in the same commit (`test_guide_currency` gates this).

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

- [ ] The five amendments are accepted, amended, or overruled — each by name.
- [ ] Phase gates are executable as written by someone who was not in this session.
- [ ] The `acli`-on-Linux question (A5) is answered before Phase 2 begins.
- [ ] Every phase names one owner.
