# Arming the gate stack in a project repo

**What this gets you:** a repo where a bad commit is *refused* rather than noted. Wrong Jira key —
rejected. Merge aimed at a branch the model forbids — rejected. Push landing on `main` without a
single-use approval token — rejected. Today only `AGY_AVIATIONCHAT` and the command centre have
this. A repo without it will take any commit you give it.

**Who this is for:** you, standing in a repo that is missing some or all of it. Work top to bottom;
each section says what breaks if you skip it.

---

## ⛔ First, the trap: "armed" does not mean "gated"

Run the arm-check against a repo and it will happily tell you this:

```
== hooks arm-check - C:\Sudo_Hatter_Command\Projects\NEXgen-VR-Director ==

ARMED - core.hooksPath=.githooks
```

That repo has **one** hook — `post-commit`, a map-drift recorder that vetoes nothing — and **zero**
gate scripts. Nothing in it can refuse a commit. It still reads `ARMED`.

The reason is that `core.hooksPath` and the hooks themselves are two different problems:

| | What it is | Travels with a clone? | What checks it |
|---|---|---|---|
| `core.hooksPath` | local git config pointing at `.githooks` | **No** — per machine, always | `hooks_armed.py` |
| `.githooks/` contents | the hook scripts themselves | Yes — tracked files | **nothing, before this page** |

`hooks_armed.py` answers *"is this machine pointed at the hooks directory?"* It does not open the
directory. So a repo with an empty `.githooks/` passes the only check the system had.

**Read the arm-check as necessary, never sufficient.** The inventory in §2 is the sufficient half.

A worked example of what that costs: `NVS-69` added `.agents/jira.conf` to NEXgen-VR-Director so the
commit-msg Jira gate would stop being a silent no-op. The conf file is correct. NEXgen has no
`commit-msg` hook, so nothing reads it, and the ticket looked like it had closed a hole it had only
prepared to close.

---

## 1. Point this machine at the hooks

Do this once per repo **per machine**. Git never carries `core.hooksPath` across a clone, so a
fresh checkout ships every gate off.

```bash
python docs/migrations/scripts/arm_hooks_include.py .     # PC
python3 docs/migrations/scripts/arm_hooks_include.py .    # Mac
```

To do every maintained repo at once, and verify:

```bash
python docs/migrations/scripts/install_git_hooks.py
python docs/migrations/scripts/install_git_hooks.py --verify-only
```

⛔ **Do not run `git config core.hooksPath .githooks`.** It looks equivalent and is not. That writes
the key into `.git/config`, and Claude Code's worktree setup parses that file, resolves the relative
value to an **absolute** one, and writes it back to the *shared* config. After that every worktree
runs the main checkout's hooks instead of its own — so a lane's gates are not the gates being
enforced on it, and nothing tells you. The installer puts the value in an **included** file that git
follows and a plain ini reader does not (SCC-323).

The enforcement suite asserts `core.hooksPath` is set *and relative*, so an unarmed repo stays red
rather than quietly passing.

---

## 2. The inventory — what a fully gated repo contains

Measured against `AGY_AVIATIONCHAT`, 2026-08-25. Copy the missing files from there.

### `.githooks/` — seven hooks

| Hook | Refuses | Skipping it means |
|---|---|---|
| `commit-msg` | a commit with no valid key for this repo; a merge landing on a forbidden branch | wrong-project keys and illegal merges land silently |
| `pre-commit` | a file with broken encoding | mojibake enters the tree |
| `pre-push` | a lane carrying another lane's unlanded work; any push to `main` without a token | `main` has no mechanical gate at all |
| `post-commit` | *(advisory)* records map drift | the map cache goes stale unnoticed |
| `post-checkout` | *(advisory)* shouts when store files vanish | a `git reset --keep` deletes memories with no error, no diff, no red |
| `post-merge` | *(advisory)* same check after a merge | as above |
| `post-rewrite` | *(advisory)* same check after a rebase | as above |

The four `post-*` hooks **cannot veto** — the operation already happened. Their value is that a human
sees the regression within one command rather than three weeks later.

### `.agents/scripts/git-hooks/` — the gate scripts

```
commit-msg-jira.sh          every commit carries this repo's key
merge-target-guard.sh       a merge lands on a branch the model allows
pre-push-main-approval.sh   nothing reaches main without a single-use token
pre-push-merge-backstop.sh  a lane is not carrying another lane's work
pre-commit-encoding.sh      encoding check
mint-push-token.sh          mints the single-use token at sign-off
install-encoding-hook.ps1   installs the encoding hook
```

### The three arming files

```
JIRA-ENFORCE            commit-msg-jira.sh REJECTS instead of warning
MERGE-TARGET-ENFORCE    merge-target-guard.sh REJECTS
MAIN-PUSH-ENFORCE       pre-push-main-approval.sh REJECTS
```

**Presence is the whole signal — nothing reads the contents.** Delete one and that gate drops to
warn-only. Use the body for the incident that armed it; that is what `AGY_AVIATIONCHAT` does.

⚠️ **Warn-only is worse than off in an IDE.** VS Code hides git hook output, so a warning looks
exactly like a clean success. Ship hooks armed.

### `.agents/jira.conf`

```sh
JIRA_KEYS="AVCH"
```

⛔ **Without this file the Jira gate is a silent no-op.** It reads `JIRA_KEYS` and, finding it empty,
`exit 0`s — passing anything:

```sh
JIRA_KEYS=""
[ -f .agents/jira.conf ] && . ./.agents/jira.conf
[ -n "$JIRA_KEYS" ] || exit 0
```

Space-separate if a repo legitimately answers to more than one project.

---

## 3. Two hook-authoring hazards that have already bitten

Both are in `AGY_AVIATIONCHAT`'s hooks as comments. They are here because each cost a real incident
and neither is obvious from reading working code.

**`exec` replaces the shell process.** A hook that ends `exec gate2.sh` runs nothing written after
it, and nothing says so. `commit-msg` was a single-purpose `exec` shim; adding a second gate above
the `exec` worked, and adding a *third* would have silently never run. **Call and check each gate;
`exec` only the last, so its exit code becomes the hook's.**

**`pre-push` gets its refs on STDIN, and a stream is readable once.** Hand raw stdin to the first
gate and the second reads EOF — its `while read` loop never executes and **it exits 0**, silently
allowing every push, including the ones to `main` it exists to refuse. Read the refs once into a
file under the git dir and feed each gate from that file. This failure is the exact class the gate
family exists to close, hiding inside the fix for it.

**Probe for the interpreter; never assume one.** Every hook does `python3 → python → py`. The Mac
has no bare `python`; a python.org PC has no `python3`. A hook that assumes either exits 127 in
silence.

**Layer 1 is POSIX `sh` on purpose.** For weeks the *entire* claimed push enforcement was a
Claude-only hook invoked as `powershell -NoProfile -Command "python ..."`. The Mac has neither
binary, so it exited 127 silently on every push. Six merges reached `main` on one sign-off with
nothing in the way. A git hook written in `sh` is the only layer both machines, all four agent
platforms, and your own terminal share.

---

## 4. The GitHub half — and why it is not a duplicate

> **Full treatment:** [`github-ci-gates-setup.md`](github-ci-gates-setup.md) — the workflow anatomy,
> the ratchet pattern, the `fetch-depth` trap, rulesets, and how to prove each gate actually
> refuses something. This section is the summary; that page is how you build it.

Layers 1 and 2 live on a computer and run at `git push`. **A merge performed on GitHub's servers —
the web "Merge pull request" button, or the REST API — never touches a computer.** Those layers are
not bypassed there; they are *absent*. A PR has landed on `main` exactly that way, from a web
session, with nothing structurally able to look at it.

So the server needs its own gate:

1. **`.github/workflows/main-write-gate.yml`** — runs the enforcement suite, the toolkit lint, and
   `main_write_gate.py`, which checks the merge came from an `epic/*` or `chore/*` branch carrying a
   key this repo answers to.
2. **A ruleset on `main`** requiring that check. **Keep the bypass list empty.**

⚠️ **Rulesets need a paid plan on a private repo.** `NEXgen-VR-Director` returns
`403 Upgrade to GitHub Pro or make this repository public` for both `/rulesets` and
`/branches/main/protection`. On such a repo the server half **does not exist**, the local hooks are
the only enforcement, and the PR door is a convention rather than a gate. Know which situation you
are in before trusting it.

**This is not a copy of layer 1.** Layer 1 enforces *authorisation* — one sign-off buys one merge —
through a token under `.git/` that by design never leaves the machine. That half cannot cross to a
server. The two halves guard different things and you need both.

---

## 5. Verify — and do not accept the arm-check alone

```bash
python docs/migrations/scripts/install_git_hooks.py --verify-only
```

Then check the payload, which is the half nothing automates yet:

```bash
ls .githooks/                                # expect 7
ls .agents/scripts/git-hooks/                # expect the scripts + 3 ENFORCE files
cat .agents/jira.conf                        # expect JIRA_KEYS set
```

Finally, make one gate actually fire. A gate you have never seen refuse anything is a gate you are
trusting on faith:

```bash
git commit --allow-empty -m "no key here"    # expect REJECTED
```

If that commit succeeds, the stack is not gating regardless of what the arm-check says.

---

## Related

- [`github-ci-gates-setup.md`](github-ci-gates-setup.md) — the server-side half in full
- [`new_machine-migration-guide.md`](new_machine-migration-guide.md) — the wider per-machine setup
- [`keyway-setup.md`](keyway-setup.md) · [`jira-api-token-setup.md`](jira-api-token-setup.md) — the
  credentials the Jira gate and `acli` need
- `.agents/rules/git-policy.md` — the branch model these gates enforce, and the full token contract
