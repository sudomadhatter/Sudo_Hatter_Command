# SCC-396 — `zoo_notify` had no Linux branch, so Ubuntu and WSL resolved to the Mac path

**Lane:** `chore/SCC-396-zoo-linux-root` · **Ticket:** SCC-396 · **Date:** 2026-09-04
**Found by:** a live `/smh-llm-approvals` run, which reported "0 Zoo threads" on a machine where
the Zoo store plainly exists.

## The defect

`zoo_notify.user_dir()` branched exactly two ways:

```python
if platform == "win32":  <APPDATA>/Code/User
else:                    ~/Library/Application Support/Code/User
```

There was no Linux branch, so Ubuntu and WSL fell into the **Mac** arm and resolved to a path that
cannot exist there. Nothing raised: `store_roots()` is built on `user_dir()`, so it returned a
missing directory and every caller reported zero threads — which is indistinguishable from Zoo
never having been used. `shape_scan.py:176` reads it too.

A second, independent gap sat behind it. Under VS Code Remote (WSL, SSH, dev containers) the
extension runs **server-side** and keeps its task store in the remote home at
`~/.vscode-server/data/User/globalStorage/`. No branch named that, so a correct Linux branch
**alone** would still have reported zero on this machine.

### Measured, 2026-09-04, on the live WSL box

| | |
|---|---|
| `store_roots()` returned | `~/Library/Application Support/.../tasks` — **missing** |
| the store actually at | `~/.vscode-server/data/User/globalStorage/zoocodeorganization.zoo-code/tasks` — **exists** |
| `~/.config/Code` | **absent** — no native Linux VS Code on this box |

That last row is why both halves of the fix were needed rather than just the first.

## Why it mattered

`/smh-llm-approvals` Step 1 reads Zoo through this resolver, and that command's own body warns
twice against exactly this failure class — the SCC-355 `partial` filter, which silently dropped 4
of 23 stopped commands. A silent under-report is worse than an error because the operator, reading
a list missing his own commands, has no way to tell. It cost nothing on the day it was found only
because the store was genuinely empty.

## The fix — one file

`.agents/scripts/zoo_notify.py`

1. **`user_dir()` gained the missing third branch** — `linux` → `$XDG_CONFIG_HOME` or
   `~/.config/Code/User`, matching the three-way shape `vscode_sync.get_vscode_user_dir()` has used
   all along. An `xdg` seam mirrors the existing `appdata` seam so the branch is testable.
2. **New `user_dirs()`** returns every candidate `User` directory — the local install **and** the
   Remote server root.
3. **`store_roots()` enumerates all of them**, each with its named profiles. The *first* root is
   still returned whether or not it exists, because `main` reads an all-missing list as "Zoo is not
   installed" and exits 2; a further candidate only earns a row when it is really on disk.
4. **`main` now reads `customStoragePath` from every candidate.** Under Remote the `settings.json`
   carrying that setting sits beside the server-side store, not in the local `User` dir.

## The two siblings — audited, and deliberately NOT changed

The operator asked for PC, Ubuntu and Mac across these resolvers. Two were already correct, and
verifying that mattered more than changing them:

- **`zoo_permissions_apply.candidate_dbs()`** already branches three ways and reaches the Windows
  stores through `/mnt/c` under WSL. Its docstring says no `state.vscdb` exists in the distro —
  **re-verified 2026-09-04, none does.** It hunts the globalState DB; `zoo_notify` hunts the task
  store. They live in different places and both notes are true at once. Changing it to match would
  have been wrong.
- **`vscode_sync.get_vscode_user_dir()`** already branches three ways including
  `$XDG_CONFIG_HOME`. Adding the Remote root would point at a file that does not exist and is not
  the right one anyway: under Remote-WSL the user `settings.json` lives on the **client**, and
  `~/.vscode-server/data/User/settings.json` is the machine-settings file, a different thing.
  Verified absent on this box, as is `~/.config/Code/User/settings.json`.

## Evidence

**Red first.** Four tests written before the fix, all failing for the right reason — the assertion
output named the Mac path on a `platform="linux"` call:

```
FAILED test_store_root_resolves_on_linux_and_not_to_the_mac_path
FAILED test_linux_honours_xdg_config_home
FAILED test_store_roots_finds_the_remote_server_root_under_wsl
FAILED test_store_roots_enumerates_both_linux_roots_and_their_profiles
4 failed, 46 deselected
```

**Green after.** `test_zoo_notify.py` — **50 passed**, the 46 pre-existing cases unchanged.

**Proved on the live machine**, not only in a tmpdir:

```
store_roots():
   /home/dlohn/.config/Code/User/globalStorage/zoocodeorganization.zoo-code/tasks (missing)
   /home/dlohn/.vscode-server/data/User/globalStorage/zoocodeorganization.zoo-code/tasks EXISTS
```

**Full suite:** `run_all.py` → **72/73 files passed**.

### What CI caught that both machines missed — and it was mine

The first `main-write-gate` run **failed on my own new test**,
`test_store_roots_enumerates_both_linux_roots_and_their_profiles`, while every operator machine was
green. Root cause, read from the log rather than guessed:

`user_dir()` consulted `XDG_CONFIG_HOME` **unconditionally**. GitHub's runner sets that variable;
neither operator box does. So a test that pinned a fake `home` in a tmpdir had its sandbox silently
replaced by the runner's real config dir — it did not fail because the resolver was wrong, it failed
because the test had escaped into live machine state.

That is precisely the escape this file already documents for `HOME` and `APPDATA` in
`test_main_actually_honours_custom_storage_path_end_to_end`: *"a test that silently escapes its
sandbox and reads live user data is worse than a red one; it was red only by luck."* This was the
third hatch in the same wall, and it went red only on the server.

**Fixed at cause, twice:**

1. An explicit `home` now means a caller pinned the machine, so the ambient `XDG_CONFIG_HOME`
   loses to it; the variable is read only when resolving the **live** machine. `user_dirs()`
   forwards `home` **unresolved** so that distinction survives the call.
2. The end-to-end child's environment now pops `XDG_CONFIG_HOME` alongside `NTFY_TOPIC`, sealing
   the third hatch the way the other two already were.

**Pinned so it cannot return:** a new case sets `XDG_CONFIG_HOME` to a decoy and asserts a pinned
`home` still wins. Verified both ways —
`XDG_CONFIG_HOME=/runner/fake python3 test_zoo_notify.py` → **51/51**, and plain → **51/51**.

⭐ The gate did its job here, and the lesson generalises past this lane: **two machines that agree
are not a platform matrix.** Both operator boxes lacked the variable, so local green proved nothing
about the third environment that actually runs the fence.

## The one red, and why it is not this lane's

`test_rule_frontmatter.py` fails with 3 cases, all naming `Projects/sudo-command-center`: 28 rules
on disk with 0 rows in its `INDEX.md`, and a project-local copy of the tier-1 `project-law.md`.

**Run on clean `main` with `--on-main`, it fails identically — the same 3 cases, 20/23.** This lane
touches three files, none in that tree. It arrived with the teaching-edition submodule repoint
(SCC-280, PR #152/#153).

⚠️ **It is red LOCALLY only, and the reason is the more interesting half.** `main-write-gate.yml`
checks out with `actions/checkout@v4` and sets no `submodules:` key, so `Projects/sudo-command-center`
is an **empty directory on the runner** — `test_rule_frontmatter.py` walks projects on disk, finds
none, and all three cases pass vacuously. Proof rather than inference: **PR #153, the pull request
that performed the repoint, passed `main-write-gate` green** and merged at 22:34:33Z. So CI is
green and nothing is blocked; the red fires only where the submodule is populated, which is both
operator machines.

That makes the tier-1 project-law check **structurally dead server-side** — it exists to catch a
project forking the constitution, `main-write-gate` runs the full suite so that law is enforced on
the way to `main`, and it has never once been able to see a project. Same defect class as this
lane's own bug and as SCC-355: reporting success while looking at nothing. Recorded on SCC-397.

## SOP

The watcher row in `workflows_testing_SOP.md` claimed the notifier "reads the thread store Zoo
already writes — every profile". That was **false on Linux for the life of the feature**, so the
`sop_currency` gate was answered by updating the page, not by `[sop-ok]`. It now names Mac, Windows
and Linux/WSL, records the Remote-server root, and carries the do-not-"fix"-`zoo_permissions_apply`
warning so the next reader does not undo the distinction.

## Gate

- `test_zoo_notify.py` — **51 passed** (5 new, 46 pre-existing unchanged), verified both with and
  without `XDG_CONFIG_HOME` set
- `run_all.py` — **72/73 files passed**; the single LOCAL red is `test_rule_frontmatter.py`,
  reproduced identically on clean `main` (`--on-main`, 20/23) and tracked as SCC-397. CI does not
  see that one at all — it is the submodule case below — and CI's own first red was mine, fixed above
- Live-machine proof that the resolver now reaches the real store
- `sop_currency.py` — satisfied by a real SOP edit
- Suite receipt: [`gates/suite.json`](gates/suite.json) — `fail`, exit 1, 27.4s @ `05c7fb54`

**No `Verdict:` stamp is written, deliberately.** The receipt records the suite's true exit code,
and that code is 1 — from `test_rule_frontmatter.py`, a red this lane did not cause and cannot fix
without leaving its scope. SCC-363's gate is right that a verdict cannot stand on a failing receipt,
and the honest answer is to withhold the stamp rather than bypass the gate with `[verdict-ok]`.
Same call, same reason, as SCC-375.

**What that leaves provable, which is the part that matters:** the four new cases were red before
the fix and green after, `test_zoo_notify.py` is 50/50 with its 46 pre-existing cases untouched,
the resolver reaches the real store on the live machine, and every other file in the suite passes.
The withheld stamp is about one unrelated red, not about this change.

## Your Actions

- [x] The merge itself — lands via this branch's PR

*(SCC-175 checks that row against ancestry, not against its tick: `chore/SCC-396-zoo-linux-root`
is an ancestor of `origin/main` at `0010b09b`, PR #154.)*

**Nothing is owed to the operator on this lane.** The one finding that needed a decision — which
half of the `sudo-command-center` INDEX / tier-1 problem to fix, and whether `main-write-gate`
should check out submodules or refuse an empty project directory — is **SCC-397**, with both halves
and their remedies written on the ticket. It is tracked there, not here, so it does not hold this
close-out.

### Correction to this record (2026-09-04, post-merge)

**The lane manifest was missing, and that is the same omission twice over.** `task.yaml` is
**Step 0** of this door — *"author the task manifest if the task never got one"* — and this lane
went straight to the fix without opening the door first. It cost two gates, both of which were
right to refuse:

- `devrecord` died with *"no task.yaml declares the branch you are on, so there is no manifest to
  read the lane slug from"*.
- `finish` **re-opened the ticked merge row**: SCC-175 verifies that tick against ancestry rather
  than trusting it, and it resolves the lane tip from `task.yaml` `branch:` or a walkthrough
  `Verdict: … @ <sha>`. This lane had neither — the verdict is withheld on purpose — so the tip was
  unresolvable and the row correctly held. *A tick is a claim, and that is the check.*

The manifest is now written. It is the missing artifact, not a workaround for the gate.


This section originally carried `- [ ] Merge the PR when the checks are green` and a second
checkbox for the SCC-397 decision. Both were wrong, and `jira_feed.py check-actions` refused the
close-out over the first — correctly. From the operator's word on, the merge, the re-invocation,
the Dev Record and the prune are the **ceremony's** steps, not his; `## Your Actions` holds only
what he alone DECIDES. The door says to run that check **before** the PR, where the fix is free,
and this lane skipped it — so the fix cost a second pull request. Recorded rather than quietly
amended, because the next lane's author is the person this note is for.
