# SCC-411 — cycle 11 runs as ONE lane: every open INDEX row closed, none carried forward

**Ticket:** SCC-411 (the 2026-09 rolling ticket, cycle 11 — reopened 2026-09-06 after a close-out that left nine collected rows unrun)
**Lane:** `chore/SCC-411-bugs-cycle-11`, cut from `origin/main` at `aa408738`
**Date:** 2026-09-06

> **Why this lane exists.** SCC-411 was closed Done with ten INDEX rows in its description, nine of
> them never turned into work. The operator's ruling: the pile does not move to the successor and it
> does not split into more tickets — it CLOSES, here, under the ticket that collected it
> (`work-consolidation.md`: a rolling ticket big enough is RUN as one lane). SCC-419 (cycle 12)
> stays clean and holds the baton; the board carries exactly one open cycle in progress.

## 1. What is true today, measured at `aa408738` — every row reproduced or shown closed

Every verdict below came from the repo's own matchers over the RENDERED lists
([repro_cycle11.py](/tmp/claude-1001/-home-dlohn-Sudo-Hatter-Command/587b12e9-5ea4-4b6b-b211-df02b25136ec/scratchpad/repro_cycle11.py),
run from this tree) or from a plain shell command named in the row.

| Row | Claim in the ticket | Measured today | State |
|---|---|---|---|
| 1 | `env -i`, `env FOO=1`, `nice`, `xargs`, `command` in front of `rm -rf /` are ASK, not DENY | all five read `ask` on Zoo, Claude and Antigravity; `env -C` reads `deny` on Zoo and Antigravity | open — a DECISION row (§2) |
| 2 | `approval_stops.py` has no row in `.agents/scripts/INDEX.md` | `grep -n approval_stops .agents/scripts/INDEX.md` → nothing | open |
| 3 | `vscode_running()` fails OPEN in a sandboxed shell | in this sandbox `tasklist.exe` prints `WSL (35 - ) ERROR: UtilConnectUnix:505: socket failed 1` and exits 0; the function catches only `OSError`, finds no `Code.exe`, returns False | open |
| 4 | Zoo auto-approves `git branch -rd origin/REF` | `-rd` → zoo=**allow**; worse than filed: `-r -d` and `-r --delete` → **allow on all three**, Claude through its `Bash(git branch -r:*)` row. Real git 2.43 deletes the remote-tracking ref for every one of them | open, wider |
| 5 | the `-d` family's escapes: multi-argument list, `--delete`, `-f -d` | `git branch -d chore/SCC-1-x main` → allow ×3; `--delete main` → zoo=allow ag=allow; `-f -d main` → zoo=allow ag=allow. Also measured: `-v -d`, `-vv -d`, `--format=… -d` all DELETE in real git, and Claude allows `-v:*`, `-vv:*`, `--format:*`; git REFUSES `-a`, `--list`, `--merged`, `--contains` together with `-d`, so those rows are not holes | open, wider |
| 6 | `zoo_pieces()` never scores a backtick body | `zoo_pieces("git branch -d chore/x \`echo main\`")` → one piece; the `$()` spelling grabs the body. Both spellings read allow ×3 today because the body `echo main` is innocent — the danger is the branch LIST being laundered, not the body | open — a DECISION row (§2) |
| 7 | no assertion bounds any lane re-allow prefix | widening `git branch -d chore/` → `git branch -d c` (and `claude/` → `cl`, `epic/` → `e`) in memory flips **0** rows of BATTERY, CEREMONY, ASK_BATTERY, LEGIT_READS, RESIDUAL_APPROVE, and `git branch -d canything-at-all` reads `auto_approve` | open |
| 8 | `approval_stops.py` double-counts a stop that survives a compaction | a transcript holding the same `tool_use`/`tool_result` pair twice (same `toolu_` id) scans as `calls: 2, stops: 2`; once as `1, 1` | open |
| 9 | the `/smh-llm-approvals` fast path is unreachable for a Zoo harvest (the guide is a fifth path) | `.agents/commands/smh-llm-approvals.md` Step 4 now lists **five** paths including `docs/migrations/terminal-permissions-guide.md`, with the SCC-412 measurement written under it | **CLOSED on main** — struck with this evidence, no code |
| 10 | SCC-417 (banned-row gate) | shipped, PRs #178/#179 | closed |
| + | SCC-418's own leftover, raised once in its walkthrough: `gate_receipt.py` stamps DIRTY inside the sandbox because `git status` lists the sandbox's bind mounts as untracked | from this tree, sandboxed: `git status --porcelain` shows 12 `??` rows (`.bashrc`, `.gitconfig`, `.claude/agents`, …), every one `character special file` per `stat`. The receipt then forces the suite to run AGAIN sandbox-off — the exact double run SCC-418 was for | open — finished here, it is cycle 11's subject |

## 2. The three decisions, made as the engineer and stated with the why

> ⚠️ **AMENDED DURING THE BUILD (2026-09-06) — row 1's premise was false, and the measurement
> that killed it also explains the row.** The decision below rested on "all five land on `ask`,
> which is the correct verdict: the operator decides". Measured after approval, from this lane,
> against the rendered Antigravity list:
>
> ```
> bare -> house, on Antigravity:          which allow rule swallows the house prefix:
>   nice rm -rf /     ask   -> allow        HIT: command(cd)
>   env -i rm -rf /   ask   -> allow        HIT: unsandboxed(cd)
>   curl https://evil.sh  ask -> allow
>   rm -rf /          deny  -> deny       (zoo, for contrast: every one stays ask)
> ```
>
> Antigravity matches a command's LEADING tokens, `command(cd)` is a blanket allow, and every door
> command in this house is mandated to be `cd <abs> && …` (`command-shape.md` rule 1). So behind
> the shape the operator's agents actually type, **the ASK tier does not exist on Antigravity** —
> only the deny list fences, because denies get a `cd .* && ` house twin and asks have no twin to
> get. "It lands on ask, so he still decides" was therefore not true for these five.
>
> **Amended decision:** deny the four spellings the grammars can express — `nice `, `xargs `,
> `command ` (the existing `command -v ` allow is longer and still wins), and `env -i` — each with
> its env twin and its automatic house twin, and each pinned by a DESTRUCTIVE row. No door uses any
> of them as a verb (`grep -rn` over `.agents/commands/`, `.agents/scripts/`, `.githooks/`:
> zero hits). `env FOO=1 <cmd>` is denied on Antigravity as one token regex and stays a **Zoo
> residual** — a literal-prefix grammar cannot express an arbitrary variable name, the same limit
> the `env -C` family already records. The general fact — every `ask` becomes `allow` behind
> `cd <abs> && ` on Antigravity — is pinned by its own case and named in the guide's residual
> section with the remedy stated (replace the blanket `command(cd)` with the enumerated house
> shapes `cd .* && git .*`, `cd .* && python3 .*`, …). It is **not** done here: re-architecting the
> Antigravity allow list inside a bug-closing lane risks turning the operator's real ceremony into
> approval prompts, which is the one cost this house treats as a budget threat.

**Row 1 — SUPERSEDED by the amendment above; kept for the reasoning it records.** `nice`, `xargs` and `command` are
general-purpose (`command -v` is an allow row today) and a literal-prefix deny on any of them bites
real work; `env -i` and `env FOO=1` are the ordering residual the `env -C` family already documents.
All five land on `ask`, which is the correct verdict: the operator decides. What is missing is the
PIN — nothing today would notice an allow row admitting them. So: the five join Zoo's `ASK_BATTERY`
and the parity `UNKNOWN` battery (A5 demands `ask` on all three), and the guide's §7 residual cell
names them. No deny row. That closes the row as a decision with a falsifiable assertion behind it.

**Row 6 — the model is not changed; the launder is closed where it can be and pinned where it
cannot.** Whether real Zoo scores a backtick body is not measurable from here, and a model that
scores what the platform may not score would certify a hole (the battery reads the model). The real
danger is a substituted TARGET in a branch delete — `git branch -d chore/x \`echo main\`` deletes
`main` on every platform, and no prefix or per-token grammar can see it. On Claude the guard in
row 5 refuses any substitution inside a delete list. On Zoo and Antigravity it is a documented
residual: the backtick spelling joins `RESIDUAL_APPROVE` (a behaviour pin — if the model ever
changes, the test flips and the guide row must move with it) and the guide §7 gets one line.

**Rows 4 and 5 — one guard on Claude, finite rows on the other two, the rest a named residual.**
Claude runs hooks, so ONE `PreToolUse` guard closes the entire family there: any `git branch` that
carries a delete flag (`-d`, `-D`, `--delete`, or a cluster holding `d`/`D`, in any position) is
DENIED unless every target starts with `chore/`, `claude/` or `epic/` (quoted or bare) and no target
carries a substitution. That covers the multi-argument list, `-r -d`, `-v -d`, `-vv -d`,
`--format … -d`, `-f -d`, `--delete` and the backtick launder in one place, and it is the remedy
the ticket names. Deny, never ask (an ask is an auto-deny in auto mode and strands a headless run —
`shape-block.py`'s law), fails open, silent on everything that is not a branch delete. Zoo and
Antigravity cannot run it; they get deny rows for every spelling measured to delete that their
grammar CAN express — `-rd`, `-r -d`, `-r --delete`, `--delete`, `-f -d`, `-f --delete`, `-v -d`,
`-vv -d` — each with a DESTRUCTIVE twin so a later narrowing reds A2/A12, and the unbounded form
("any other option before the delete flag", `--format=<value> -d`) is recorded as the same ordering
residual the `env -C` family carries. The `-d <list>` escape on those two platforms stays exactly
what the ticket says it is: inexpressible in a permission row, so documented, never claimed closed.

## 3. Acceptance — every row is a command or an inspection, and Step 2 makes each fail first

| Row | Statement | Proof |
|---|---|---|
| A | Every measured delete spelling is DENIED on Zoo and Antigravity: `git branch -rd X`, `-r -d X`, `-r --delete X`, `--delete main`, `-f -d main`, `-f --delete main`, `-v -d main`, `-vv -d main`, plus `env -u GITHUB_TOKEN` twins and the `cd <abs> && ` house shape; every ceremony spelling still ALLOWS | each spelling in parity `DESTRUCTIVE` (A2, A3, A6, A12) and Zoo `BATTERY`; `CEREMONY` and A4/A13 unchanged and green; `permission_render.py --check` exit 0; `test_env_twin_invariant` green |
| B | The Claude guard `guard-branch-delete.py` DENIES a branch delete whose target list holds anything outside `chore/`, `claude/`, `epic/`, or holds a substitution, in any flag position; ALLOWS the doors' own prune spellings; is SILENT on every non-delete `git branch` and on every non-git command; never returns `ask`; fails open on garbage input; wired exactly once in the single PreToolUse Bash group; has an INDEX row | `test_guard_branch_delete.py` (own harness, HOME redirected like `test_shape_block.py`); the wiring case mirrors `test_wired_inside_the_single_pretooluse_bash_group` |
| C | Widening any lane re-allow by ONE character reds the battery | near-miss rows `git branch -d chore`, `chores/x`, `claude`, `claudes/x`, `epic`, `epics/x` in Zoo `BATTERY` and parity `DESTRUCTIVE`; the mutant sweep widens each prefix in `families.json`, re-renders, and names the case that goes red |
| D | ⚠️ **AMENDED DURING THE BUILD** (see §2). Four of the five wrappers are pinned **DENY** on Zoo and Antigravity; only `env FOO=1` remains ASK | `BATTERY` (deny) for `nice`/`xargs`/`command`/`env -i` + `ASK_BATTERY` for `env FOO=1`; the guide §7 cell names all five. The original row said ASK for all five, and the measurement that changed decision row 1 changed this row with it — it was left stale until the code review caught it |
| E | The backtick launder is pinned as a Zoo/Antigravity residual and refused by B on Claude | `RESIDUAL_APPROVE` carries the spelling; guide §7 line; B's substitution case |
| F | `scan()` counts a replayed pair ONCE | new case in `test_approval_stops.py`: the duplicated pair → `calls == 1`, `stops == 1`; control: two DIFFERENT ids → `2, 2` |
| G | `vscode_running()` fails CLOSED: an answer that is not a process table means "running" | cases with `subprocess.run` stubbed: the verbatim WSL interop error → True; `INFO: No tasks are running…` → False; a table naming `Code.exe` → True; a table without it → False; `OSError` → True |
| H | `approval_stops.py` has its INDEX row | `check_maps.py --depth3-only --strict` exit 0; the row names the SCC-407 question and the door |
| I | The receipt ignores an untracked entry that is a sandbox MASK, and only that | `gate_receipt._measure_dirt` consults the module-level `is_sandbox_mask`; a faked mask row → `dirty_tree: False`; a real file beside it → `True` and named; the predicate itself is driven against real filesystem objects (`/dev/null`, a 0444 empty file, a symlink to a device, a 0444 file with content). ⚠️ Widened by the code review: the predicate covered ONE mask shape and a second exists, and the filter had shipped in one of four tree gates while the changelog claimed all — both closed |
| J | Row 9 is struck with its evidence, no code | the outline's `## Done` cites `smh-llm-approvals.md` Step 4's five-path list |
| K | The whole suite is green in ONE sandboxed run at the shipping SHA; guide count line current; every mutant killed by a NAMED case, narrowings included; one SOP aside + changelog row for the new guard | `run_all.py` from the lane, in-sandbox; `gate_receipt.py run … --gate suite` clean; `mutants.json`; `sop_currency.py` |

## 4. Steps — RED first, one row at a time

1. **RED, all rows at once**, before any fix: add the new battery rows, the guard's test file, the
   scan case, the `vscode_running` cases and the receipt case. Run each file bare and paste the red.
   `guard-branch-delete.py` does not exist yet, so its test fails on "hook missing", which is the
   right reason for a file that is the fix.
2. **A** — `families.json`: extend `deny-git-branch`'s explicit `zoo` and `antigravity` renders
   with the eight spellings (+ env twins; the house twins come from the render pass). Run
   `permission_render.py` to regenerate `.vscode/settings.json` and `antigravity.json`
   (`.claude/settings.json`'s allow list is untouched by A — no Claude row changes). Update the
   guide's count line and the Work-destruction Entries cell. Claude's `-r`/`-v`/`-vv`/`--format`
   allows are KNOWN-pinned in parity with the guard named as the fence, the same way
   `git push origin main` is pinned to `require-push-approval.py`.
3. **B** — write the guard beside `shape-block.py`: split atoms with `allow-readonly-chain.py`'s
   quote-aware `split_atoms`, find `git … branch` with `require-push-approval.py`'s `GIT_OPTS`,
   tokenise the rest, classify flags vs targets, decide. Wire it; INDEX row; the SOP aside.
4. **C, D, E** — battery rows and guide lines.
5. **F** — `scan()`: remember every `tool_use` id seen in the file; a repeated id is skipped
   (both the use and its result), so `total` and `stops` count the event once.
6. **G** — `vscode_running()`: the WSL/Windows arm returns True unless the output looks like a
   `tasklist` answer (a header row containing `Image Name`, or the `INFO: No tasks` form).
7. **H, I** - the INDEX row; `_measure_dirt(work, out_dir)` filters sandbox-mask entries through the module-level `is_sandbox_mask`.
8. **Mutants** — one per fix, narrowings not only deletions: drop one deny spelling; loosen the
   guard's namespace test to `startswith("c")`; make the guard accept a substitution; make it `ask`;
   widen each lane re-allow by one character (row C's proof); dedupe on the wrong key; flip the
   `vscode_running` default; filter every `??` entry in the receipt instead of only devices.
9. **Close** — suite in ONE sandboxed run; receipt; review; the outline's `## Done` gives every one
   of the ten rows its disposition, so the ticket description says what happened to each.

## 5. Landing order and blast radius

`git worktree list` shows only the lobby on `main` and this lane. Nothing else is in flight. The
guard touches `.claude/settings.json`'s hooks block only; the permission renders touch
`.vscode/settings.json` and `antigravity.json`; the operator's own stores need
`zoo_permissions_apply.py --apply` / `antigravity_permissions_apply.py --apply` after the merge —
the close-out prints both lines, as `/smh-llm-approvals` does.

⚠️ **AUDIT FINDING (baked in).** Two files the conventions require were missing from the change set.
(1) `_artifacts/_main/INDEX.md` carries one row per lane folder (`:7` is SCC-418's) — this lane
gets its row. (2) `.agents/rules/git-policy.md:236` is where the Claude-side git fences are named
(`require-push-approval.py` **PreToolUse hook**); the branch-delete guard is the same kind of
fence and is named there in the same commit, exactly as `command-shape.md:171` names
`shape-block.py`. The pre-mortem for (2): a later agent reads git-policy, finds only the push
hook, re-derives the delete escape as "no fence exists" and files this row again — the cycle
this ticket is closing. Two procedural notes from the same pass: Claude Code snapshots hooks at
session start, so the guard is live in the NEXT session after the merge, not the running one (the
SOP aside says so); and the sandbox denies writes to `.claude/settings.json` in this lane too, so
`permission_render.py` runs once sandbox-off with that reason stated, or the two rendered files
are written with the Write tool from `--check`'s output.

## Declared Change Set

- NEW `.agents/hooks/guard-branch-delete.py` — the Claude branch-delete guard → B
- NEW `.agents/scripts/tests/test_guard_branch_delete.py` — its own harness and wiring case → B
- EDIT `.claude/settings.json` — one hook entry in the single PreToolUse Bash group, nothing else → B
- EDIT `.agents/hooks/INDEX.md` — the guard's row and contents entry → B
- EDIT `.agents/rules/git-policy.md` — the guard named beside `require-push-approval.py` as the second Claude-side fence (audit finding 2) → B
- EDIT `_artifacts/_main/INDEX.md` — this lane folder's row (audit finding 1) → K
- EDIT `.agents/permissions/families.json` — eight deny spellings on `deny-git-branch` → A
- EDIT `.vscode/settings.json` — rendered by `permission_render.py` → A
- EDIT `.agents/permissions/antigravity.json` — rendered by `permission_render.py` → A
- EDIT `docs/migrations/terminal-permissions-guide.md` — count line, Entries cell, §7 residual lines → A
- EDIT `.agents/scripts/tests/test_permission_parity.py` — DESTRUCTIVE, UNKNOWN, KNOWN rows → A
- EDIT `.agents/scripts/tests/test_zoo_permissions.py` — BATTERY, ASK_BATTERY, RESIDUAL_APPROVE rows and the `vscode_running` cases → C
- EDIT `.agents/scripts/approval_stops.py` — dedupe replayed tool_use ids in `scan()` → F
- EDIT `.agents/scripts/tests/test_approval_stops.py` — the replay case and its control → F
- EDIT `.agents/scripts/zoo_permissions_apply.py` — `vscode_running()` fails closed → G
- EDIT `.agents/scripts/INDEX.md` — the `approval_stops.py` row → H
- EDIT `.agents/scripts/gate_receipt.py` — device-aware `_measure_dirt` → I
- EDIT `.agents/scripts/tests/test_gate_receipt.py` — the faked-device case and its control → I
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — one aside naming the guard → K
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one row → K
- NEW `_artifacts/_main/2026-09-06_scc-411-bugs-cycle-11/task.yaml` — the lane manifest → K
- NEW `_artifacts/_main/2026-09-06_scc-411-bugs-cycle-11/tickets/SCC-411.md` — the outline → J
- NEW `_artifacts/_main/2026-09-06_scc-411-bugs-cycle-11/walkthrough.md` — the record → K
- NEW `_artifacts/_main/2026-09-06_scc-411-bugs-cycle-11/mutants.json` — the sweep → K

## Self-Audit (2026-09-06)

**Level: LEDGER+BLAST** (the change set touches a hook, three scripts others call, a rule, and
two platforms' permission renders). Mode: PRE-WORK. Repo: `Sudo_Hatter_Command` | Branch:
`chore/SCC-411-bugs-cycle-11` at `aa408738`.

```
lens:        1 Repo Reality
checks_run:  Declared Change Set parses; every EDIT path exists on disk and every NEW path does not;
             plan steps 1-9 referenced exist; both-sides commands (python3, stdlib only); lane fit;
             Scope Ledger (NEW artefacts x acceptance row); acceptance precondition (>=2 rows, each
             with an observable)
read:        declared_change_set.py parse -> 24 entries, "incomplete": []; ls over 18 EDIT paths (24 entries = 18 EDIT + 6 NEW) ->
             all ok; .agents/hooks/guard-branch-delete.py and its test -> absent (NEW); Declared
             paths: no backend/ frontend/ firebase/ functions/ mobile/ .github/ -> Task door
             /smh-close-task-merge-tree is right; NEW artefacts: guard -> B, test -> B, task.yaml ->
             K, outline -> J, walkthrough -> K, mutants -> K (no empty cell); rows A-K each name a
             command or a case
verdict:     clean
```

```
lens:        2 Parity + Blast
checks_run:  a gate or hook (ships armed? every place the last deny hook is named); a script
             (callers outside tests, its test, scripts/INDEX.md); a rule; SOP same-commit; twins
             (cicd-*/smh-* doors); files in >1 repo; sibling worktrees; risk seam
read:        grep -rl shape-block -> .claude/settings.json, .agents/hooks/INDEX.md,
             .agents/rules/command-shape.md, .agents/scripts/approval_stops.py:143 (harness_ban -
             a shape row, not a hook registry), smh-llm-approvals.md:21,396 (the harvest table -
             shape-specific), test_claude_permissions_apply.py:148-149 (reads the PreToolUse group
             - B's wiring case covers it), the SOP + changelog, _artifacts/_main/INDEX.md:7,10;
             callers: gate_receipt.py:240 `_measure_dirt(work, out_dir)` (one caller, own file),
             zoo_permissions_apply.py:237 `if args.apply and vscode_running()` (one caller),
             scan() called by approval_stops.main only; git ls-files .claude/hooks -> nothing
             tracked (the settings wiring runs .agents/hooks/ directly through run-hook.sh);
             ls Projects/*/.agents/hooks -> none (hooks exist in ONE repo); no command file
             changes -> no twin to port; git worktree list -> the lobby on main and this lane
             only; risk_seam classify -> {"status": "unclassified", "root": "."} (the centre
             has no code graph - correct, SCC-289)
verdict:     findings below
```

```
lens:        3 Pre-Mortem
checks_run:  the silent one, the other-machine one, the fresh-clone one, the sibling-lands-first
             one - attached to lens 2's findings only
read:        .agents/rules/git-policy.md:236-239 (the only Claude-side git fence named is the
             push hook); .claude/settings.json:223 (hooks are read at session start)
verdict:     findings below (attached)
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/rules/git-policy.md:236` | "2. `require-push-approval.py` **PreToolUse hook** (canonical source `.agents/hooks/`, deployed to every `.claude/hooks/`)" | the rule that enumerates Claude's git fences would not name the new one; the pre-mortem: a later agent reads it, sees only the push hook, re-derives the `-d <list>` escape as unfenced and files this row a third time. Baked in: EDIT `git-policy.md`, same commit as the guard | medium |
| `_artifacts/_main/INDEX.md:7` | "\| `2026-09-05_scc-418-suite-passes-in-one-sandbox-run/` \| SCC-418 (subtask of SCC-411, the rolling ticket) — …" | every lane folder carries a row; the plan declared none, and `check_maps.py --strict` at close-out would go red on the omission. Baked in: EDIT `_artifacts/_main/INDEX.md` → K | low |

### Observations (uncounted)

- `git-policy.md:236` says the hook is "deployed to every `.claude/hooks/`", but nothing is tracked
  there and `.claude/settings.json:223` runs `.agents/hooks/` directly. Stale wording in a line this
  lane touches anyway; corrected in passing only if the edit lands on that sentence, otherwise left.
- `approval_stops.py:143` names `shape-block.py` inside `harness_ban` because those are SHAPES the
  door must never offer a row for. A guard-refused `git branch -d main` returns to the agent in
  milliseconds and never reaches the wait threshold, so it is not a stop and needs no ban row.
- Claude Code reads hooks at session start: the guard protects the NEXT session after the merge.
- The sandbox denies `.claude/settings.json` writes in this lane; the render step runs sandbox-off
  once with the reason stated, or the two files are written from `--check`'s diff.

Sibling landing-order dependency: none — `git worktree list` holds the lobby on `main` and this lane.

Audit verdict: GO

## Approval

**Approved (2026-09-06):** the operator's literal `Approved`, given in session after the reopen
ruling — "move the ticket you just closed that is clearly far from done since you doubled the job
and FIX IT". Audit verdict at the stop: `GO`.
