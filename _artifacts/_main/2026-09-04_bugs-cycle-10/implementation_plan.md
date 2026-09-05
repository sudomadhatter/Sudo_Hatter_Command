# SCC-373 — Bugs and Updates cycle 10, run as ONE consolidated lane

**Lane:** `chore/SCC-373-bugs-cycle-10` off `origin/main` @ `5c444d22`
**Riders:** SCC-409 (Part B) · SCC-410 (Part C)
**Part A (SCC-374) is already on main** — it shipped as its own lane, PR #136, and its key was later
deleted from the board. Nothing in this lane touches it.

Both parts are defects in the **instruments that watch the permission fence** — one under-reports
coverage, one cannot see a laundering row. Neither changes what any agent is allowed to do today.
Part C adds one **deny** family, which can only ever make the fence stricter.

---

## The two defects, measured on this lane's base

**Part B — `approval_stops.py` reports a third of the fence as absent.**
`allow_prefixes()` strips the suffixes `:*` and ` *` but never a bare trailing `*`. Battery A2b
established that a prefix ending in `/ = - :` must be spelled `Bash(X/*)`, because Claude reads
`Bash(X:*)` as `Bash(X *)` — so the bare-star spelling is the **working** one. Measured on this
base: **54 of the 153** rendered Claude `Bash(...)` allow rows are bare-star, including
`Bash(python3 .agents/scripts/*)` and every `Bash(<VAR>=*)` row. Every one of them comes out of
`allow_prefixes()` with its `*` still attached and therefore matches nothing, so the door bills the
operator for stops that an existing allow row already covers. This is the instrument error that
inflated SCC-406's claimed savings.

**Part C — the battery cannot see an `env -C` laundering row, and the fence does not deny the wrapper.**
A3 proves Claude never auto-approves anything in `DESTRUCTIVE`. That list carries `env -u
GITHUB_TOKEN` twins but no `env -C` twin. Claude carries **no deny list at all** (0 deny rows on
this base), so a single `Bash(env -C:*)` allow row auto-approves `env -C <dir> rm -rf /` and four
more — proven on PR #165, which passed the whole battery green and was closed unmerged.

⭐ **Measured while scoping, and it changes Part C's shape:** the wrapper is not denied *anywhere*.
`env -C /tmp rm -rf /` today reads **ask** on zoo, claude and antigravity alike. So adding the five
twins to `DESTRUCTIVE` on its own turns **A2** red (zoo and antigravity must DENY every destructive
command), not just arm A3. The ticket did not anticipate that. Closing it properly therefore needs
one new **deny** family for the `env -C` / `env --chdir=` wrapper, rendered to the two platforms
that have deny lists. That is the difference between arming a tripwire and closing the hole, and it
is why this plan is slightly larger than SCC-410 as filed.

---

## Acceptance — every row is checkable by a command

| # | Statement | The command that proves it |
|---|---|---|
| A | `allow_prefixes()` returns `python3 .agents/scripts/` for the row `Bash(python3 .agents/scripts/*)` — the bare `*` is stripped | new case in `tests/test_approval_stops.py` |
| B | A slow call to a command that a bare-star row already covers is reported as **zero** stops | new case in `tests/test_approval_stops.py` |
| C | `DESTRUCTIVE` carries the five `env -C` twins and A3 is still green on this base | `tests/test_permission_parity.py` |
| D | Injecting `Bash(env -C:*)` into the rendered Claude list turns A3 **RED** naming the env -C rows; removing it returns the battery to green | temporary injection, reverted, output pasted in the walkthrough |
| E-tracked | `env -C <dir> <destructive>` and `env --chdir=<dir> <destructive>` are **denied** in the rendered zoo and antigravity lists | `tests/test_permission_parity.py` A2 |
| E-live | the live stores' state is **measured and recorded**, and the apply is handed to Mr. Hatter with its command (Zoo's needs VS Code fully closed) | `--status` of both apply scripts, output in the walkthrough |
| F | `permission_render.py --check` prints **in sync** for zoo, claude and antigravity, and `tests/run_all.py` is green at the tip | both commands, output pasted |
| G | No allow row is added, widened, or re-spelled anywhere in this lane | `git diff` of `families.json` shows only a new `deny` entry |

---

## Steps, each naming its assertion

**Step 1 (Part B, red first).** Add two cases to `tests/test_approval_stops.py`: one calling the real
`allow_prefixes()` against a temp repo whose `.claude/settings.json` carries a bare-star row (A), one
end-to-end through `scan()` with that prefix stubbed in, asserting zero stops for a slow covered
command (B). Both must be seen RED against the unfixed script, for the right reason — the returned
prefix still carrying its `*`.

**Step 2 (Part B, green).** Add `"*"` to the suffix tuple in `allow_prefixes()`, ordered **after**
`":*"` and `" *"` so the longer suffixes strip first. One line. Re-run: both cases green.

**Step 3 (Part B, mutants).** Reorder the tuple to put `"*"` first and confirm a case fails (proves
the ordering is load-bearing); revert. Delete the `break` and confirm behaviour is unchanged
(documents that the loop is single-strip by design, or exposes that it is not).

**Step 4 (Part C, red first).** Add the five `env -C /tmp …` twins to `DESTRUCTIVE`, mirroring the
existing `env -u GITHUB_TOKEN` block. Run the battery: **A2 must go red** on zoo and antigravity.
That red is the reproduction of the deny-side hole, and it is captured before anything is fixed.

**Step 5 (Part C, green).** Add ONE deny family to `families.json` covering the chdir wrapper in both
spellings, with explicit renders for zoo (literal prefix) and antigravity (per-token anchored regex,
which also picks up the existing `cd .* &&` house twin pass). Claude renders nothing — it has no
deny list, and A3 is its guard. Re-render, re-run: A2 green, A3 green.

**Step 6 (Part C, the tripwire proof — acceptance D).** Inject `Bash(env -C:*)` into the rendered
Claude allow list, run the battery, capture A3 RED naming the env -C rows, revert the injection, and
confirm green. This is the case the whole part exists for, and PR #165 is the proof it was reachable.

**Step 7 (the batch, one block).** `permission_render.py --check`, then `tests/run_all.py`, then the
`git diff --name-only origin/main...HEAD` scope guard. One block, read together (work-consolidation
rule 3).

**Step 7.5 (audit finding F1/F2 — added by the self-audit).** Run the **read-only** `--status` of
`zoo_permissions_apply.py` and `antigravity_permissions_apply.py` and paste both into the
walkthrough. ⚠️ **AUDIT FINDING: neither `--apply` runs in this lane.** Zoo's needs VS Code fully
closed, and Antigravity's live store is already adrift by 43 store-only allow rows that an apply
would silently delete. The walkthrough hands Mr. Hatter both commands and says plainly that the
new deny row is tracked-green and not yet live on this machine.

**Step 8.** Walkthrough, review, stop for the merge sign-off. Riders flip to Done first, SCC-373 last.

---

## Declared Change Set

- EDIT `.agents/scripts/approval_stops.py` — strip a bare trailing `*` in `allow_prefixes()` → A
- EDIT `.agents/scripts/tests/test_approval_stops.py` — two red-first cases for the bare-star row → A
- EDIT `.agents/scripts/tests/test_permission_parity.py` — five `env -C` twins in `DESTRUCTIVE` → C
- EDIT `.agents/permissions/families.json` — one new deny family for the `env -C` / `env --chdir=` wrapper → E
- EDIT `.vscode/settings.json` — re-rendered Zoo deny rows → E
- EDIT `.agents/permissions/antigravity.json` — re-rendered Antigravity deny rows → E
- NEW `_artifacts/_main/2026-09-04_bugs-cycle-10/task.yaml` — lane manifest, riders declared → F
- NEW `_artifacts/_main/2026-09-04_bugs-cycle-10/implementation_plan.md` — this plan → F
- NEW `_artifacts/_main/2026-09-04_bugs-cycle-10/walkthrough.md` — the lane's record → F

`.claude/settings.json` is **deliberately not** in this list: Claude carries no deny list, so a new
deny family renders nothing there. If that file moves, the change was not what this plan describes.

---

## What this lane will NOT do

- **No allow row is added, widened or re-spelled.** Acceptance G is the check.
- **`allow-find` is not re-widened to Antigravity.** SCC-405 backed it out because a bare `find`
  token there grants `find . -delete`; the reason is written into the family's own `why`.
- **The sibling wrappers are not swept.** Measured on this base, `env -i`, `env FOO=1`, `nice`,
  `xargs` and `command` in front of `rm -rf /` all read **ask** on all three platforms — safe today,
  and the same class as this defect. `nice`/`xargs`/`command` are general-purpose and denying them
  wholesale could bite real work, so they are out of scope here and go to the open rolling ticket
  (SCC-411) as one row at close-out if they survive the review.

---

## Self-Audit (2026-09-04)

**Level: LEDGER+BLAST** — the declared set touches two scripts others import, a battery, the one
permission source, and two rendered platform files. Mode: PRE-WORK.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every path/script/command the plan names exists on disk (8/8)
             declared change set parses -> 9 entries, 0 incomplete
             deployable-path check on the declared set -> none (correct door: smh-close-task-merge-tree)
             port trigger: approval_stops.py / permission_render.py / permission_matchers.py / families.json
                           in Projects/* -> 0 copies, so no port section is owed
             stdlib-only, python3-vs-python: both parts run stdlib only, no venv
             Scope Ledger precondition: 7 acceptance rows (A-G), each with a naming command
             Scope Ledger: 3 NEW artefacts (task.yaml, this plan, walkthrough.md), each required by row F
read:        .agents/scripts/approval_stops.py:67-84 · .agents/scripts/tests/test_approval_stops.py:30-78
             .agents/scripts/tests/test_permission_parity.py:78-105,196-213 · .agents/permissions/families.json
             .agents/scripts/permission_render.py:180-210 · .agents/scripts/INDEX.md
verdict:     clean
```

```
lens:        2 Parity + Blast
checks_run:  script changed -> callers (.agents/commands/smh-llm-approvals.md, its own test), .githooks/ (none),
                               .agents/scripts/INDEX.md (see Observations)
             gate/hook surface -> "does it ship ARMED?"  <- THIS IS WHERE THE FINDINGS ARE
             sibling worktrees -> git fetch origin, then per tree: scc-398-stale-knowledge-audit
                                  diff vs origin/main is EMPTY (it merged as PR #167); no landing-order dependency
             twins -> no cicd-*/smh-* command file is touched; nothing to port
             risk_seam -> unclassified, as it always is in the command centre (no code graph); judgement from the diff
             live-store state read with the read-only --status of both apply scripts
read:        .agents/scripts/zoo_permissions_apply.py:1-14 · .agents/scripts/antigravity_permissions_apply.py:1-10
             zoo_permissions_apply.py --status (both stores) · antigravity_permissions_apply.py --status
verdict:     findings below
```

```
lens:        3 Pre-Mortem
checks_run:  attached the silent-failure narrative to F1; the other-machine narrative to F1; no unattached output
read:        (attaches only to findings the anchored lenses raised)
verdict:     findings below (attached to F1)
```

### Findings

| # | anchor | literal text read | consequence | severity |
|---|---|---|---|---|
| F1 | `.agents/scripts/zoo_permissions_apply.py:3-8` | "Zoo Code decides auto-approval from VS Code globalState (SQLite ``state.vscdb``…), **NOT** from ``.vscode/settings.json`` — the tracked file seeds the store exactly once on a fresh machine and never again, and ``deniedCommands`` **never seeds at all**." | Acceptance E proves the **render** denies `env -C`; it does not make the live fence deny it. Editing `.vscode/settings.json` moves nothing on this machine — `deniedCommands` never seeds from the tracked file at all. The lane would land a deny row that is green in the repo and absent from the tool, on both this box's stores. | **high** |
| F2 | `antigravity_permissions_apply.py --status` | `status : DRIFT allow: store-only=43 tracked-missing=3 \| deny: store-only=0 tracked-missing=0` | The live Antigravity store is **already** adrift on the allow side. So `--apply` is not a clean no-op for this lane: pushing one new deny row would also delete 43 store-only allow rows and add 3 tracked ones — changes this plan does not declare and did not measure. The apply must not be run blind from this lane. | medium |

**Pre-mortem attached to F1 — the silent one.** Nothing fails loudly. `permission_render.py --check`
prints *in sync*, the battery is green, the walkthrough says `env -C` is denied, and every one of
those statements is true **about the tracked files**. The live Zoo store keeps answering `ask` for
`env -C`, which is safe but weaker than the record claims, and the gap is invisible until someone
reads `--status`. **Other-machine variant:** the applies are per-machine (Mac *and* PC), so even a
correct apply here leaves the other seat behind.

### Both findings are baked into the plan, not left as a bill

- **Step 7.5 is added** (see below): after the batch verification, run the read-only `--status` of
  both apply scripts and record the exact live numbers in the walkthrough.
- **Acceptance E is split in two.** `E-tracked` is what this lane proves and lands: the battery says
  the rendered zoo and antigravity lists deny both spellings. `E-live` is an **operator action at
  close-out**, named with its command, because Zoo's apply requires VS Code to be **fully closed**
  and that is Mr. Hatter's call, not an agent's:

  ```
  python3 .agents/scripts/zoo_permissions_apply.py --apply           # VS Code fully closed
  python3 .agents/scripts/antigravity_permissions_apply.py --status  # READ FIRST - F2's drift
  ```
- **This lane does NOT run either `--apply`.** F2 is the reason: the Antigravity store's 43
  store-only allow rows are somebody's un-harvested grants, and silently deleting them inside a
  bug-fix lane is exactly the "rogue widening" this cycle exists to clean up after.

### Observations (uncounted, no severity)

- `.agents/scripts/INDEX.md` carries 30 rows for 41 scripts on disk, and `approval_stops.py` has no
  row — it shipped in SCC-407 without one. Not this plan's defect and not in its declared set;
  `check_maps.py` passes, so the INDEX is evidently curated rather than exhaustive.
- The live Zoo stores each report `allowedCommands: 124 (DRIFT: 1 tracked entry missing)` against a
  tracked 125. Pre-existing, allow-side, and unrelated to this lane.
- `destructiveCommandGuardEnabled: False` on both Zoo stores. Noted, not touched — changing a live
  guard flag is nowhere near this lane's scope.

Audit verdict: GO
