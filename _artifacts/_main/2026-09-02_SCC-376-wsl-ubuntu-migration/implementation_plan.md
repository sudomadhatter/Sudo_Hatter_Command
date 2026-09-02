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
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — line 2900 pointer; also the SOP-currency co-occurrence the script edits demand → F

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
  `/home/dlohn`, and `echo $PATH | tr ':' '\n' | grep -c '^/mnt/'` returns `0`.
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
- **A5 remains genuinely unresolved and is not a finding** — whether `acli` can authenticate on
  Linux is unverifiable from this machine. It is written into Phase 1's gate rather than guessed at.

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
