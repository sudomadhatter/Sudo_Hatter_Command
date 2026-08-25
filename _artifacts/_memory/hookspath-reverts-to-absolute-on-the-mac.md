---
name: hookspath-reverts-to-absolute-on-the-mac
description: "On the Mac, this repo's local core.hooksPath keeps reverting from the installer's relative `.githooks` to an ABSOLUTE path, which reds test_install_git_hooks.py and test_hooks_armed.py. No script in the repo writes an absolute value. Observed twice in one session, 2026-08-24 (SCC-305)."
metadata: 
  node_type: memory
  type: project
  originSessionId: c38b7969-c282-4a42-a3f1-21aa5c1f0e0b
  modified: 2026-08-24T21:17:12.666Z
---

The lobby repo's **local** `core.hooksPath` on this Mac keeps coming back as the absolute
`/Users/sudohatter/Sudo_Hatter_Command/.githooks` instead of the installer's designed **relative**
`.githooks`. Twice in one working session (SCC-305, 2026-08-24), hours apart.

**Why it matters:** it is not cosmetic and it is not harmless. An absolute value resolves to the
MAIN checkout's hook dir for every worktree, so a lane's own `.githooks/` is never read — and two
suite files go red on it:

- `test_install_git_hooks.py` → *"live repository has core.hooksPath set"* (it asserts the value is
  literally `.githooks`)
- `test_hooks_armed.py` → every hook tracked in a lane's `.githooks/` reports *"absent from the
  directory git actually reads"*

Both look like the lane broke the hooks. Neither did. It costs a full 85s suite run each time,
because the failure only surfaces at the certification stamp.

**Nothing in the repo writes it.** Grepped every `.py`/`.ps1`/`.sh` under `.agents/` and `.githooks/`:
the only writer is `new-project.ps1`, and it writes the *relative* value. So the source is
machine-local — an IDE, an extension, or another session. Unidentified as of 2026-08-24.

**How to apply:**

1. **Check it before you stamp a suite, not after.** `git -C <main-checkout> config core.hooksPath`
   must print exactly `.githooks`. One second here saves an 85-second red.
2. **Fix it with the relative value, never the absolute one:**
   `git -C /Users/sudohatter/Sudo_Hatter_Command config core.hooksPath .githooks`
3. **Do not "fix" the tests.** The tests are right — a relative value is what arms every clone and
   every worktree ([[two-machines-mac-and-pc]], [[git-hooks-live-in-githooks-not-git-hooks]]).
4. **If it recurs a third time, find the writer** rather than resetting again — a value that comes
   back is a process rewriting it, and the resets are treating a symptom.
