---
IsArtifact: true
---

# SCC-376 — WSL2 / Ubuntu migration: walkthrough

**What changed, in one sentence.** The PC's working environment moved into WSL2 / Ubuntu so that both
machines run the **same** agent fence from the **same** file, and every Windows-shaped rule that existed
only to paper over the difference is gone.

## Why this existed

SCC-375 measured why Claude Code interrupted constantly on the PC and almost never on the Mac: Claude has
two independent ways not to interrupt — the allow list and the OS **sandbox** — and the sandbox does not
run on native Windows. That left the allow list as the entire fence on one machine and half the fence on
the other, and it is why the two machines had been drifting apart rule by rule. The operator's call was
to close the gap at the source rather than by adding more rules: Windows becomes the screen, Ubuntu does
the work, and a second distro keeps the two Zoo Code seats isolated from each other.

The goal was stated by the operator and held throughout: **the agent works unattended on both machines —
no prompts, no commands handed back, no per-machine files. Security serves that goal, not the reverse.**

## What shipped

**One portable user settings file.** `~/.claude/settings.json`, sha256 `e1a13e0d126f0478…`, byte-identical
on the Mac and inside both Ubuntu distros. Paths are written `~/`-relative, the Conductor hooks are kept
but guarded so they are a silent no-op where Conductor is not installed, and the macOS-only notifier was
replaced by a portable one that pushes to the phone from either machine and adds whichever desktop banner
exists. The generator that produces it, `portable_settings.py`, itemises every deviation from the Mac's
original, so the Phase 6 check reads a recorded list rather than a byte diff.

**The fences now describe what the machines actually run.** Zoo's tracked allow list went from 143 rows to
124: 22 Windows-shaped rows out by **exact match** — never by prefix, because `dir` is the head of
`dirname `, which had to survive — and three Unix rows in for the capabilities that had only ever had a
Windows spelling (pytest, ruff, the Firebase emulator). Claude's tracked list went from 161 to 141, and
the portable user file from 102 rules to 82. The largest single removal was the `git -C *` wildcard family
in all three files: a wildcard sitting *before* the git subcommand approves any option inserted at that
position, and `-c` / `--exec-path` there run arbitrary commands. Nothing legitimate got harder, because
the house pin idiom `cd <abs> && git <verb>` is judged per piece and every verb was already allowed.

**Both Zoo seats are fenced.** Phase 4 gave the PC two VS Code instances on two distros with isolated
model state. Phase 6 found that the second seat's master auto-approve toggles were **off**, which means it
consulted no list at all and asked for everything — with a perfectly synced allow list sitting beside it.
`zoo_permissions_apply.py` gained `--enable-auto-approve`, it now covers the second seat's store, and on
the PC it runs **from Ubuntu**, reaching both Windows stores through `/mnt/c`.

**One permissions guide.** `docs/migrations/terminal-permissions-guide.md`, 560 lines, replacing three
pages of 374 + 173 + 27. The split was a direct cause of how long this investigation took: three
documents, one subject, each true about its own third and silent about the other two.

## Decisions worth keeping

**Zoo's state lives on the Windows side, even though Zoo runs in the distro.** Measured twice, in Phase 4
and again in Phase 6, because it is genuinely counter-intuitive and I got it wrong the first time: the
extension host runs inside Ubuntu, but the VS Code *window* keeps its `globalState` in the Windows
user-data-dir. There is no `state.vscdb` anywhere in either distro. This is why the apply script reaches
through `/mnt/c` instead of looking locally, and why the two seats' isolation still comes from two
user-data-dirs rather than two distros.

**The unsandboxed-retry hatch stays open** (operator ruling). Closing it trades a silent success for a
silent agent *failure* unless the allow list has first been measured wide enough against real workloads,
and it never prompted anyone. Strict mode remains available behind a flag, with a zero-refusal battery as
its entry condition.

**AGY stays out of scope, by repo boundary.** Its `.claude/settings.json` differs from the lobby's, which
fires the port checklist; a lobby ticket editing files inside AGY produces a commit no AVCH ticket
accounts for. It ships as AVCH-116.

## Pitfalls hit, and what each cost

**A test that pins the shape you are removing fires at every deletion.** It happened four times and each
was amended in the *same* commit, never afterwards: the interpreter-twin case demanded a bare-`python`
rule for every `python3` rule; case B4 demanded the retired Antigravity extension recommendation; CS-15
demanded all four platform MCP configs including the one being deleted; and `test_guide_currency` found
the canonical lists by slicing between `## 6.` and `## 7.`, which the merge would have turned into a
different chapter or a crash inside the one test whose job is noticing staleness. Deleting first and
fixing the test second leaves a red suite in the tree.

**A summary that counts printed lines can certify the opposite of the truth.** The first Phase 6 run
reported all eight checklist lines clean. One was not: the script counted `--apply`'s status block and a
second `--status` twice, and counted a toggle across both stores, so it read "2 of 2" while the second
seat's own bytes said its fence switch was off. The summary is now computed by re-reading the stores.

**A step that reports success it did not achieve.** Phase 6's retire step printed `renamed ->` while
PowerShell's own error above it said the rename had failed — with `ErrorActionPreference = Continue` the
success string runs anyway. It now checks the result and classifies the file.

**Crossing into WSL from a Windows shell.** Three probes answered confidently about the wrong clone,
reporting a plausible branch, an old head and thousands of falsely modified files, because an inline
`wsl.exe … bash -c "cd ~/repo && …"` ran in the Windows cwd mapped to `/mnt/c`. Acting on it would have
"recovered" a repository that was already correct. This is now **law 4 in `command-shape.md`**, with the
remedy rather than just the ban, pinned by a test proved to go red when the law line is deleted.

**`wslpath` is unusable from PowerShell** (found by the Desktop Team): the backslashes are stripped
passing the path through `wsl.exe`, so it returns empty and every step downstream runs with no script.

## Evidence

| gate | result |
|---|---|
| `python3 .agents/scripts/tests/run_all.py`, bare, inside Ubuntu | **71/71 files passed, rc 0** |
| `test_allow_scratchpad` | 187/187 — case E, the uid case that could never pass on Windows, passes natively; the SCC-375 open item closed itself |
| `test_allow_readonly_chain` | 153/153 (the Linux number the audit predicted) |
| Phase 3 sandbox gate | containment **demonstrated**, not read off a config |
| Phase 6 checklist, second run | all eight lines; `VERDICT stores=2 in-sync=2 toggles-on=2` |
| Mac install | sha `e1a13e0d126f0478`, 20 removed rules all `git -C *`, nothing lost |

## Follow-ons (already ticketed — no new work is being proposed here)

- **AVCH-116** — AGY's port of this shape into its own `.claude/settings.json`, after this lands on `main`.
- **SCC-378** — retiring Antigravity as a *platform* (its command surface and `platforms:` declarations).
  This ticket removed only its leftovers in this repo; the operator confirms the IDE itself is already
  gone from his machines and that his `~/.gemini` folder is deliberately kept.

## Your Actions

- [x] The merge itself — lands via this branch's PR
- [x] Delete the Windows clone `C:\Sudo_Hatter_Command` — it still holds 7 uncommitted files belonging to
      other sessions (four new memory files, two modified ones, and AVCH-109's mutation-sweep script under `scratch`).
      Remedy: their owners commit them, or say the word and I carry the memory files into the Ubuntu clone
      under a memory commit; then the folder can go. Nothing in this ticket reads from it any more — the
      Windows `~\.claude\settings.json` is already retired by rename. -- verified 2026-09-02 (operator): Operator decision 2026-09-02: 'Im still finishing two storys here on this windows one... we are not deleting this so I have to finish them here since the chats are here.' The clone is RETAINED on purpose; its unique work was preserved first - AVCH-110 (54 commits) and AVCH-102 (51) pushed to their own branches, 3 AGY stashes and 2 remote-less branches left in place, and the 26 worktree junctions I had unlinked were re-linked.
