---
IsArtifact: true
ArtifactMetadata:
  title: Stale-knowledge audit — one PC, one machine model, memories that prove themselves
  type: implementation_plan
  date: 2026-09-04
---

# Stale-knowledge audit — one PC, one machine model, memories that prove themselves

**Ticket:** to be minted on your approval — one `Task` under the toolkit epic, six `Subtask`s
**Lane:** `chore/<KEY>-stale-knowledge-audit` off `main` (one subtask takes its own branch first — §Order)
**Base:** `origin/main` @ `70154040`
**review-runtime:** fan-out

---

## What changes for you, Mr. Hatter

Today an agent told you the live Antigravity cache was on a Windows path you don't use, called an
abandoned clone "your live side", reported a repo you had updated at 17:36 as unchanged, and handed
you a test plan that asked you to count menu entries by eye. Every one of those came from **one
stale sentence in memory** — *"the command center is driven from TWO machines, this Mac AND a
Windows PC"* — written 2026-08-08 and never re-measured. There is no Mac. There is one PC.

After this ticket: the machine model is written **once**, from probes that ran on this PC; every
memory that names a path or a tool carries the one-line command that proves it, and the suite turns
red the day that command stops passing; the 30 memories, 6 rules, 13 commands and 14 docs that
still say "Mac" or "two machines" say what is true; `Fresh_Workspace_BMAD` is gone from git, not
just from a folder; and the test that has been auditing your **published teaching edition** as if it
were a thin project stops doing that, which turns the floor green and lets SCC-394 stamp **PASS**.

The one thing you asked to know for sure — **why the Windows clone exists** — gets a measured answer
in Subtask B. My current read, from evidence and not memory: it is the workspace the **Antigravity
IDE** opens. That IDE is a Windows application (its store is `C:\Users\dlohn\.gemini\antigravity-ide\`,
its transcripts name `Sudo_Hatter_Command`, and VS Code's own workspace list records the repo opened as
`file:///c:/Sudo_Hatter_Command`); a Windows app opens Windows paths. You were right to keep it.

---

## The facts this plan stands on

Every row was measured today on this PC. The **Probe** column is the command that proves it; those
commands become the `probe:` lines in Subtask C.

| # | Fact | Probe |
|---|---|---|
| F1 | One PC. Windows, with Ubuntu inside WSL2. Not a Mac, not two machines. | `grep -c microsoft-standard-WSL2 /proc/version` → 1 |
| F2 | Three ways this repo is opened: Windows-native `C:\Sudo_Hatter_Command`; WSL `ubuntu` at `/home/dlohn/Sudo_Hatter_Command` (this shell); WSL `ubuntu-zoo2` at the same path (Zoo — its clone is unconfirmed, §B) | VS Code `workspaceStorage/*/workspace.json` `folder` values |
| F3 | The Windows clone is the **same repo**, `main` @ `ab68505e`, **90 commits behind**, and its 3,850 dirty rows are line-ending flips only (865,077 insertions = 865,077 deletions; the EOL-insensitive diff is empty). **No work lives there.** | `git rev-list --count ab68505e..HEAD` · `git diff --ignore-all-space --stat` |
| F4 | Antigravity on the Ubuntu side is the **CLI** (`agy`, installed Sep 3, `~/.gemini/antigravity/cli.log`); the **IDE** lives on the Windows side (`antigravity-ide/`, last conversation Aug 25). The memory says the opposite. | `test -f ~/.gemini/antigravity/cli.log && test ! -d ~/.gemini/antigravity-ide` |
| F5 | Two workflow caches, one per side: Ubuntu `~/.gemini/antigravity/global_workflows` = 40 files, 0 BMAD; Windows `C:\Users\dlohn\.gemini\antigravity\global_workflows` = 42 files, 2 BMAD, last written Sep 1. SCC-394's purge cleans **whichever side runs the sync** (`$UserHome` = `USERPROFILE` else `HOME`; `USERPROFILE` is empty under WSL pwsh). | `ls ~/.gemini/antigravity/global_workflows \| wc -l` · pwsh `$env:USERPROFILE` |
| F6 | The CLI reads `.agents/skills/<name>/SKILL.md` at runtime — its own log names two of ours. SCC-394's door is proven by the product, not a doc. | `grep -c '\.agents/skills/.*SKILL\.md' ~/.gemini/antigravity/log/*.log` |
| F7 | All ten `Projects/*` entries are git **submodules** (mode `160000`). `Fresh_Workspace_BMAD` is declared at `.gitmodules:13`. Deleting its folder does not remove it. | `git ls-files -s Projects/ \| grep -c 160000` → 10 |
| F8 | `Projects/sudo-command-center` is the **published teaching edition**: `claude/teaching-edition` carries `export-teaching-edition.ps1`, `lobby.manifest.json` and `replacements/` (sanitized `jira.md`, `operator-profile.md`, `maintained-projects.txt`, `memory-MEMORY.md`, `router.md`). You refreshed it today at 17:36 (`86e0d95`). It carries 28 rule files **by design**. | `git ls-tree claude/teaching-edition .agents/scripts/teaching-edition/` |
| F9 | `test_rule_frontmatter.py` walks **every** `Projects/*` with an `.agents/` dir, skipping one hardcoded name, and fails three assertions on the teaching edition. `maintained-projects.txt` — whose header says *"Never hand-loop over `Projects/*`"* — names only `AGY_AVIATIONCHAT` and `NEXgen-VR-Director`. The floor is 72/73 because of this and nothing else. | `python3 .agents/scripts/tests/test_rule_frontmatter.py` → 20/23 |
| F10 | `claude/teaching-edition` (live, last commit today) ships **43** files under `.agents/workflows/`, with **14** pins in `validate_teaching_edition.py` and **6** in `lobby.manifest.json`. SCC-394 deletes that surface. Its walkthrough calls this "three files". | `git ls-tree -r --name-only claude/teaching-edition \| grep -c '^\.agents/workflows/'` |
| F11 | Stale-machine-model footprint: **30** repo memories, **2** session memories, **6** rules, **13** commands, **14** docs + `AGENTS.md`. | the greps in §D |

---

## The ticket and its subtasks

One `Task`, six `Subtask`s. Per `jira.md` §Subtasks the agent decides which ride the parent lane and
says why: **A takes its own branch** because it is ten lines that unblock SCC-394 and must land
before anything else; **B–F ride the parent lane** because they touch the same memory, rule and
command files and would conflict as separate branches.

| Subtask | What | Lands as |
|---|---|---|
| **A — Audit the projects we maintain, not every folder** | `test_rule_frontmatter.py`'s project scan reads `maintained-projects.txt`; the hardcoded skip goes; the teaching edition and the five separate projects stop being audited as thin projects | own branch, **first** |
| **B — Pin the machine model from disk** | One memory, written from F1–F5 with each probe attached; the reason the Windows clone is kept, with evidence; Zoo's clone confirmed or not | rider |
| **C — Memories prove themselves** | Every memory that names a path/tool/version gets a `probe:`; a runner executes them in the suite; the 30 stale ones are rewritten or deleted | rider |
| **D — Rules, commands, docs say what is true** | The 34 files that say "Mac" / "two machines" / "keychain" re-aimed at one PC with two sides; the SOP page updated (the `sop_currency` gate demands it) | rider |
| **E — `Fresh_Workspace_BMAD` leaves git** | Submodule removed properly: gitlink, `.gitmodules` stanza, `.git/modules/`, the folder; the 4 live code references cleaned; the 16 history mentions left as history | rider |
| **F — The project map, written down** | What each of the ten submodules **is** and which mechanism keeps it current — including your ruling that the skeleton is seeded from AviationChat's stack but is **not** a blind copy | rider |

### Subtask A — how

Replace the loop at `test_rule_frontmatter.py:242-249`: read the allowlist via the same helper
`check_maps.py` already uses (`fan_out_targets`), iterate exactly those names, and drop the
`Fresh_Workspace_BMAD` special case. The four assertions keep their teeth on the two projects the
lobby actually drives (AviationChat carries 7 rules, VR-Director 3 — both pass today). Add one
control that proves the exclusion is deliberate: a fixture project **off** the list with a tier-1
copy must **not** fire. Update the header comment in `maintained-projects.txt` to say the test reads
it too. Evidence: 23/23, `run_all.py` 73/73.

### Subtask B — how

Write `_artifacts/_memory/one-pc-windows-and-wsl.md` from F1–F5, replacing
`two-machines-mac-and-pc.md` (delete, not edit — the name is the wrong claim). Each fact carries its
probe. Three things get **measured** rather than asserted: (1) which paths the IDE opens — grep its
transcripts under `antigravity-ide/brain/*/.system_generated/` for `c:/Sudo_Hatter_Command` vs
`wsl$`; (2) whether `ubuntu-zoo2` carries its own clone — `wsl.exe -d ubuntu-zoo2 -- git -C
/home/dlohn/Sudo_Hatter_Command rev-parse HEAD` from an unsandboxed shell (the sandboxed one
returned nothing today); (3) why the Windows clone shows CRLF — read
`/mnt/c/Users/dlohn/.gitconfig` for `autocrlf` (today's probe read WSL's git config, which is the
wrong file). The section **"Why the Windows clone is kept"** states the answer with the evidence
lines, so the next agent does not re-derive it from a guess.

### Subtask C — how

Two parts, and the second is the one that stops this recurring.

*Triage.* Read all 147 repo memories and my 11 session memories. Each factual claim is either
**measurable** (a path, a binary, a version, a count) or a **ruling/preference**. Measurable claims get
a probe written and **run**; a failing probe means the memory is rewritten to what is true now, or
deleted if it was only ever true on a machine that does not exist. The 30 in F11 are the known set;
the triage finds the rest. Every write and delete is narrated in chat in one line, per the memory rule.

*The mechanism.* A `probe:` line under `metadata:` (a plain shell command; exit 0 = still true — no
DSL). `.agents/scripts/memory_probe.py` runs every probe with a timeout and prints one row per memory;
`test_memory_store.py` gains a check that reds when any probe fails and **names the file**. The
existing `memory_audit.py` candidates pass gains one row: a memory that names an absolute or `~/`
path and carries no probe. That is a **candidate**, not a red — otherwise the store goes red in one
shot and the trigger gets ignored, which the memory-store test already guards against. The memory
rule gets one paragraph making the probe line law for any memory that names a path.

### Subtask D — how

Mechanical sweep, file by file, of the 34 in F11. The rewrite target is one sentence: *one PC; the
Windows side runs PowerShell, `python`, the Antigravity IDE and the credential store; the Ubuntu side
runs bash, `python3`, Claude Code, Codex, opencode, `agy` and reads the token from `~/.profile`.*
Every "Mac" becomes the right side or goes; `python` vs `python3` stays (it is still true, for the
other reason); "keychain" becomes the Windows credential store or `~/.profile`. The SOP page and its
changelog are on the list, so the `sop_currency` gate is satisfied by the diff itself.

### Subtask E — how

`git submodule deinit -f Projects/Fresh_Workspace_BMAD` · `git rm -f Projects/Fresh_Workspace_BMAD` ·
delete the `.gitmodules` stanza (lines 13–15) · `rm -rf .git/modules/Projects/Fresh_Workspace_BMAD`.
Then the references: the **live** ones (`check_maps.py`, `sync-agents.ps1`, `test_rule_frontmatter.py`
— already gone via A — and `maintained-projects.txt`) are cleaned; the 16 doc/memory mentions that
say "retired 2026-08-07" are history and stay. Evidence: `git ls-files -s Projects/ | grep -c 160000`
→ 9, `grep -rl Fresh_Workspace_BMAD .agents/scripts` → empty.

### Subtask F — how

One table in `docs/workspace-standard.md` (the file that already defines what a project is) with a
row per submodule: **what it is** · **kept current by** · **audited by the lobby's suite?**

| Submodule | What it is | Kept current by | Audited |
|---|---|---|---|
| `sudo-command-center` | the published teaching edition of this lobby | `export-teaching-edition.ps1` from `claude/teaching-edition` | no — it is a mirror |
| `sudo-project-skeleton` | the new-project template | seeded from AviationChat's stack, **by hand, never a blind copy** — AviationChat-specific rules do not propagate (your ruling, 2026-09-04) | no — it is a template |
| `AGY_AVIATIONCHAT` | a maintained thin project (board `AVCH`) | its own lanes | **yes** (`maintained-projects.txt`) |
| `NEXgen-VR-Director` | a maintained thin project | its own lanes | **yes** (`maintained-projects.txt`) |
| the other five | separate projects, updated to what they need | themselves | no |

`maintained-projects.txt`'s header links to it. Nothing else changes — the table records the model
the tests now implement.

---

## Order of landing

1. **Subtask A** on its own branch → `main` is green (73/73).
2. **SCC-394** rebases on that (one file overlaps, trivially), corrects its walkthrough — the
   two-sided cache in F5, the real teaching-edition numbers in F10, the IDE→CLI paragraph in
   `antigravity-uses-workflows-not-commands.md` — restamps **PASS**, and lands via
   `/smh-close-task-merge-tree` on your word.
3. **The parent lane (B–F)** cuts from the new `main`. It lands after SCC-394 on purpose: the sweep
   touches the memory, rule and command files SCC-394 rewrote, and it should read their final text
   rather than rebase 156 files.

---

## Acceptance

| Row | Done means | Evidence |
|---|---|---|
| A | `test_rule_frontmatter.py` audits exactly the projects in `maintained-projects.txt`; a control project off the list with a tier-1 copy does not fire | 23/23; `run_all.py` 73/73 |
| B | one machine memory, every fact with a passing probe; "why the Windows clone is kept" answered with evidence; Zoo's clone confirmed or recorded as absent | `memory_probe.py` rows for the file, all PASS |
| C | zero memories assert a Mac; every memory naming a path carries a probe; the runner is in the suite and red on a failing probe (proven by a deliberately false probe in a fixture) | `memory_probe.py` exit 0; the fixture test red then green |
| D | zero rules/commands/docs say "Mac", "two machines" or "keychain" except as dated history | the F11 greps return only lines carrying a date marker |
| E | `Fresh_Workspace_BMAD` absent from `.gitmodules`, the index, `.git/modules/` and disk; no live script names it | `git ls-files -s Projects/ \| grep -c 160000` → 9 |
| F | the project table exists and `maintained-projects.txt` points at it | `check_links` clean on the new anchors |
| G | SCC-394 restamped **PASS** on a green floor with the corrected rows | its walkthrough `Verdict: PASS @ <sha>` |
| H | suite receipts green in both lanes; `workflow_lint`, `check_maps --strict`, `check_links` unchanged or better | `gates/suite.json` in each lane |

## Declared Change Set

Rows A–H are the acceptance table above.

- EDIT `.agents/scripts/tests/test_rule_frontmatter.py` — project scan reads the allowlist; hardcoded skip removed; control added → A
- EDIT `.agents/maintained-projects.txt` — header names the test as a reader and links the project table → A, F
- NEW `_artifacts/_memory/one-pc-windows-and-wsl.md` — the machine model, from probes → B
- DELETE `_artifacts/_memory/two-machines-mac-and-pc.md` — the wrong claim, by name → B
- EDIT `_artifacts/_memory/MEMORY.md` — index rows for the deletes, renames and rewrites → B, C
- EDIT `_artifacts/_memory/README.md` — store rules gain the probe line → C
- NEW `.agents/scripts/memory_probe.py` — runs every `probe:`; one row per memory; nonzero exit on any failure → C
- EDIT `.agents/scripts/tests/test_memory_store.py` — a failing probe reds the suite and names the file; fixture with a false probe → C
- EDIT `.agents/scripts/memory_audit.py` — candidate row: a path-naming memory with no probe → C
- EDIT `.agents/scripts/INDEX.md` — the new script's row → C
- EDIT `.agents/rules/agent-memory-is-long-term-only.md` — the probe line becomes law for path-naming memories → C
- EDIT `_artifacts/_memory/antigravity-uses-workflows-not-commands.md` — IDE→CLI; sides named; probes → C
- EDIT `_artifacts/_memory/a-script-plus-an-instruction-is-not-delivery.md` — triage → C
- EDIT `_artifacts/_memory/budget-is-a-live-constraint-announce-spend.md` — triage → C
- EDIT `_artifacts/_memory/claude-notifications-hook-schema-and-ntfy.md` — triage; likely DELETE → C
- EDIT `_artifacts/_memory/codex-is-fourth-platform.md` — triage → C
- EDIT `_artifacts/_memory/firestore-rules-tests-need-java.md` — triage → C
- EDIT `_artifacts/_memory/git-branch-model-standard.md` — triage → C
- EDIT `_artifacts/_memory/git-hooks-live-in-githooks-not-git-hooks.md` — triage → C
- EDIT `_artifacts/_memory/github-408-on-satellite-uplink.md` — triage → C
- EDIT `_artifacts/_memory/gitnexus-index-not-actually-live.md` — triage → C
- EDIT `_artifacts/_memory/grep-here-is-ugrep-qv-inverts.md` — triage; likely DELETE → C
- EDIT `_artifacts/_memory/hook-background-work-gets-sigterm.md` — triage → C
- EDIT `_artifacts/_memory/hooks-armed-measures-pointer-not-payload.md` — triage → C
- EDIT `_artifacts/_memory/jira-attachments-need-the-rest-token.md` — triage → C
- EDIT `_artifacts/_memory/jira-integration-live.md` — triage → C
- EDIT `_artifacts/_memory/mac-authored-code-hides-windows-bugs.md` — triage; likely DELETE → C
- EDIT `_artifacts/_memory/memory-store-is-read-by-every-platform.md` — triage → C
- EDIT `_artifacts/_memory/node-26-breaks-vitest-jsdom-storage.md` — triage → C
- EDIT `_artifacts/_memory/one-door-per-platform-per-command.md` — triage → C
- EDIT `_artifacts/_memory/one-shot-permission-persists-in-context.md` — triage → C
- EDIT `_artifacts/_memory/portable-memory-store-dot-slug-trap.md` — triage → C
- EDIT `_artifacts/_memory/rglob-sweeps-must-prune-the-walk.md` — triage → C
- EDIT `_artifacts/_memory/suite-red-file-may-have-run-nothing.md` — triage → C
- EDIT `_artifacts/_memory/windows-authored-code-hides-posix-bugs.md` — triage; stays true for one PC with two sides → C
- EDIT `_artifacts/_memory/zoo-code-replaces-roo-code.md` — triage → C
- EDIT `_artifacts/_memory/zsh-does-not-word-split-gate-args.md` — triage; likely DELETE → C
- EDIT `_artifacts/_memory/interactive-startup-files-are-invisible-to-automation.md` — triage; likely DELETE → C
- EDIT `.agents/rules/agent-memory-is-long-term-only.md` — "macOS vs Windows vs WSL" → one PC, two sides → D
- EDIT `.agents/rules/git-policy.md` — sweep → D
- EDIT `.agents/rules/port-checklist.md` — sweep → D
- EDIT `.agents/rules/jira.md` — "keychain on the Mac" → the two stores that exist → D
- EDIT `.agents/rules/code-standards.md` — sweep → D
- EDIT `.agents/rules/sop-currency.md` — sweep → D
- EDIT `.agents/commands/cicd-clean-code-audit.md` — sweep → D
- EDIT `.agents/commands/smh-llm-approvals.md` — sweep → D
- EDIT `.agents/commands/smh-merge-multiple-workingtrees.md` — sweep → D
- EDIT `.agents/commands/smh-sync-vscode.md` — sweep → D
- EDIT `.agents/commands/cicd-merge-epic-workingtrees.md` — sweep → D
- EDIT `.agents/commands/INDEX.md` — sweep → D
- EDIT `.agents/commands/cicd-close-story-merge-tree.md` — sweep → D
- EDIT `.agents/commands/smh-clean-code-audit.md` — sweep → D
- EDIT `.agents/commands/cicd-prune-worktree.md` — sweep → D
- EDIT `.agents/commands/smh-close-task-merge-tree.md` — sweep → D
- EDIT `.agents/commands/smh-self-audit.md` — sweep → D
- EDIT `.agents/commands/smh-update-maps-indexes.md` — sweep → D
- EDIT `.agents/commands/smh-quick-dev.md` — sweep → D
- EDIT `AGENTS.md` — sweep → D
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — sweep; satisfies the SOP gate → D
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — the entry → D
- EDIT `docs/_scc_sops_prds/sharing_keys_secrets_secure.md` — sweep → D
- EDIT `docs/_scc_sops_prds/autopilot_bmad_dev_loop.md` — sweep → D
- EDIT `docs/_scc_sops_prds/jira_integration_guide.md` — sweep → D
- EDIT `docs/_scc_sops_prds/git_walkthrough_settings.md` — sweep → D
- EDIT `docs/migrations/install_guides/repo-gate-stack-setup.md` — sweep → D
- EDIT `docs/migrations/install_guides/python_vytest-updates-other-machines.md` — sweep → D
- EDIT `docs/migrations/install_guides/new_machine-migration-guide.md` — sweep → D
- EDIT `docs/migrations/install_guides/machine_setup_card.md` — sweep → D
- EDIT `docs/migrations/install_guides/jira-api-token-setup.md` — sweep → D
- EDIT `docs/migrations/install_guides/vscode-ide-extension-migration.md` — sweep → D
- EDIT `docs/migrations/install_guides/keyway-setup.md` — sweep → D
- EDIT `docs/migrations/install_guides/scratchpad-allow-hook-per-machine.md` — sweep → D
- EDIT `.gitmodules` — the `Fresh_Workspace_BMAD` stanza removed → E
- DELETE `Projects/Fresh_Workspace_BMAD` — the gitlink and the folder → E
- EDIT `.agents/scripts/check_maps.py` — the live reference → E
- EDIT `.agents/scripts/sync-agents.ps1` — the live reference → E
- EDIT `docs/workspace-standard.md` — the project table → F
- EDIT `docs/repo-map.md` — regenerated → H

Session memories (outside the repo, `~/.claude/projects/.../memory/`): `wsl-jira-token-needs-a-login-shell.md`
loses its "Mac uses the keychain" line; `MEMORY.md` gains a row for the machine model. Not in the
change set because they are not repo files; narrated in chat when written.

## Not in this ticket

- **The teaching-edition port** (43 workflow files → skills, 14 validator pins, 6 manifest pins).
  That is `claude/teaching-edition`'s own lane (SCC-280) and it must land **after** SCC-394. This
  ticket only corrects SCC-394's description of it.
- **Bringing the Windows clone current.** It is 90 commits behind with no work in it. Your call
  (below) — the fix is one `git pull` from PowerShell and a `core.autocrlf` setting; Subtask B
  writes the instruction, it does not run it.
- **The Antigravity global-skills cache** for project workspaces (`~/.gemini/config/skills/`) —
  SCC-394's stated follow-on, unchanged.

## Your decisions

Three, and they are product calls, not engineering ones.

1. **Which projects the lobby's suite audits.** The plan implements: the two on
   `maintained-projects.txt` (AviationChat, VR-Director) and no others — the mirrors and the five
   separate projects are theirs. **Say if that list is wrong.**
2. **`Fresh_Workspace_BMAD` leaves git**, not just the folder. You said "it's deleted"; Subtask E
   makes git agree. The GitHub repo `sudomadhatter/Fresh_Workspace_BMAD` itself is untouched.
3. **The Windows clone.** Keep it (the IDE's workspace) — and either bring it current once so the
   IDE reads the same doors as the CLI, or leave it as is. I would bring it current: the Sep 1
   cache write says the Windows side still runs syncs, and a sync from a 90-commit-old tree writes
   90-commit-old doors.

Then, with A landed: SCC-394 rebases, corrects, restamps PASS, and you sign it off.
