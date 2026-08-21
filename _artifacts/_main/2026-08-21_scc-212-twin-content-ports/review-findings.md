---
IsArtifact: true
ArtifactMetadata:
  title: "SCC-212 — review findings: the five-lens fan-out, triaged"
  type: bug_list
  date: 2026-08-21
---

# SCC-212 — review findings (WORK IN PROGRESS — the fix pass is mid-flight)

**Engine run:** `review_mode: full` · `review_level: standard` · `lens_budget: standard` ·
`review_runtime: fan-out` · diff `origin/main...HEAD` (41 files) @ `a37b0338`.

All five lenses ran as subagents in their own clean contexts. **Every lens reproduced its
findings by execution rather than inference** — the Blind Hunter and Edge Case Hunter
independently reproduced the same top defect in a scratch repo.

```
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok — truncated pass, declared: received 4 of ~35 files (the 20-file cap); named every withheld file
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na: none
```

## STATUS OF THE FIX PASS

- [x] **B1** applied — the three broken commit blocks in `cicd-create-epic-sprint.md`
- [ ] everything below still owed

---

## CONFIRMED — fix in thread (all three disposition questions YES)

### Commands — defects this lane shipped

| # | Finding | Where | Fix |
|---|---|---|---|
| **B1** ✅ | **`printf … > epic-commit-msg.txt` writes to the lobby; `git -C "$PROJECT_ROOT" commit -F <relative>` reads it under PROJECT_ROOT → `fatal: could not read log file`, exit 128, and the next line pushes nothing while reporting success.** Reproduced 3× independently (blind, edge-case, and me). All THREE new commit blocks. | `cicd-create-epic-sprint.md` Steps 2, 3, 4 | DONE — `MSG=$(mktemp)` outside both trees + `commit -F "$MSG"` + `rm "$MSG"` per block. Also fixes the untracked-file leak that would have failed the Done block's own `status --short` gate |
| **B2** | `link-worktree-assets.py .claude/worktrees/<slug>` has **no `$PROJECT_ROOT`** — resolves against the lobby cwd. Reproduced: `error: not a directory`. The two sibling call sites in the SAME diff bind it correctly (one-of-three inconsistency, not a convention) | `cicd-quick-dev.md` Step 0.5 | bind `"$PROJECT_ROOT"/.claude/worktrees/<slug>` |
| **B4** | Step 7 verifies ancestry of `claude/*` branches **Step 6 already deleted** → `fatal: Not a valid object name`, `&&` short-circuits, no `landed` printed, agent concludes the lane did not land | `cicd-merge-epic-workingtrees.md` Step 7 | capture each lane's tip sha at 4.4, verify those shas |
| **B8** | The `$WORKTREE`/`$EPIC` binding moved to Step 0.6, a **separate shell block** — vars do not survive between blocks, so Step 0.7 runs `git -C ""` and its `>` redirects still create empty `/tmp` files → overlap reads clean. The exact scar the comment I deleted was guarding | `cicd-code-review.md` Step 0.7 | re-bind in the block, or state the blocks are one shell |
| **B3** | Kickoff leaves the project's **shared checkout standing on the epic branch**, which the merge door — edited in the same commit — says "holds no local `epic/*` branch by contract", and whose Step 4 hazard analysis assumes "that checkout stands on `main`". Also: Step 2 warns the checkout "may carry the operator's own uncommitted work" while the new Done gate demands `status --short` empty | `cicd-create-epic-sprint.md` 1b + Done; `cicd-merge-epic-workingtrees.md` Steps 4, 7 | return the checkout to `main` after the kickoff's last push; reconcile the two statements |
| **E2** | The outline backfill `acli … edit --description-file` **REPLACES** the description, and Step 1a's *reuse an existing Epic* path points it at a ticket that already has one → unrecoverable overwrite. The repo owns the guard for exactly this (`jira_feed.py index-row` reads back and exits 2) | `cicd-create-epic-sprint.md` Steps 1a, 2 | backfill only on the mint path, or read back |
| **E6** | The re-run guard covers one of three states: **(a)** local branch exists but the push failed → `fatal: a branch named … already exists` (reproduced); **(b)** the reuse path cannot test `origin/epic/<KEY>-<slug>` without already knowing the slug → a **second epic branch for one key** | `cicd-create-epic-sprint.md` Step 1b | `git ls-remote --heads origin 'epic/<KEY>-*'` + a local-branch arm |
| **E4** | The preflight call passes **no `--require-gates`**, so `check_gates` returns at `if not require: return` — the `gates` class the door names as blocking is structurally inert; a STALE receipt produces no row. The solo door passes the flag. Also `status` is not a section this script emits, and `surfaces`/`file-list` are error-capable and unnamed | `cicd-merge-epic-workingtrees.md` Step 2 | add `--require-gates suite,ruff,pyrefly`; fix the section list |
| **E5** | The `landed` carve-out is keyed on a **section that carries two different errors** — `check_landed` also routes `report_overlap` into `landed`, so "if the ONLY error is `landed`, proceed" dismisses the epic-branch-moved-under-you warning too. And `integration_branch()` returns a **local** ref, never `origin/epic/…` | `cicd-merge-epic-workingtrees.md` Step 2 | narrow the carve-out to the ancestor row by its message, not the section |
| **B6** | `cicd-code-review` Step 0.6 declares uncommitted work **out of scope**; `cicd-clean-code-audit` (its Step 3.5) now **sweeps it in**, and `any` in an unreviewed file is a FAIL | both | scope the audit's uncommitted read to standalone runs |
| **B7** | `close_command:` is written into `task.yaml` **before the diff exists**, in the same step that says the door is derived from the diff | `cicd-quick-dev.md` Step 0.5 | make it conditional / re-written when the diff settles |
| **E7** | `gate_receipt.py run` is given `--cwd` but **no `--project`/`--root`** → the receipt lands in the shared checkout while recording the worktree's sha; "commit it with the story" is then impossible and ③'s `list` prints "(no receipts)" — which the step itself calls a finding | `cicd-dev-story-tests.md` Step 4.5 | pass `--project "$PROJECT_ROOT"` |
| **E8** | `acli jira workitem view` has **no exit-code reading**, and its one branch ("no ticket → STOP") contradicts the `jira_feed.py start` table 15 lines below (exit 4 = transport, carry on) | `cicd-quick-dev.md` Step 0.5 | distinguish "no ticket" from "board unreachable" |
| **B9** | `git-policy.md` — my rewritten bullet names two doors; the untouched sentence four lines later still says "**The command that does this is `/smh-close-task-merge-tree`**" | `git-policy.md` | update the stale half |
| **A4** | The kickoff renumbering left two live cross-references pointing at steps that no longer exist: `jira.md:496` ("Step 1.5", the §Who-mints-tickets seam) and `SOP:2611` ("Step 3" for risk-scoring, which is now Step 4 — and the row omits the new hard stop) | `jira.md`, SOP | update both; `jira.md` joins the Declared Change Set |

### Instruments — my own assertion script and the guard

| # | Finding | Fix |
|---|---|---|
| **L1** | `LOADERS-scope` dereferences `_cs`, a walrus bound only inside the *true arm* of a conditional expression → `UnboundLocalError` when the guard is False. Reproduced twice. Worse than a red row: **no `FAILED:` line**, so `mutation_sweep.judge` scores it a SWEEP ERROR | restructure the binding |
| **L2** | A bare `--red`, `--red=` or `--red ""` leaves `REF=""` → falsy → **silently measures the working tree and prints `109/109`**, with the banner's RED marker also dropped. The transcript is byte-identical to a green run. This is the exact `_harness._case_filter` scar, re-committed | refuse a lost value, like the harness does |
| **L3** | `CR-pin` is keyed on `merge-tree`, which occurs **5 times as unrelated command names** — reproduced: deleting the whole of Step 0.7 leaves the row PASS. My own comments on `MERGE-12` and `QD-C2-cr` condemn exactly this shape | re-aim at Step 0.7's own text |
| **L4** | `QD-C5`'s predicate is keyed on a **trailing space** — reds on a semantically identical file (false red) and greens on `git diff --name-only origin/main`, which reads a ref, not the worktree (false green). The one row that bypasses `flat()` | make it robust |
| **T1** | **My F11 "fix" degraded the row into the bare truthiness its own comment condemns**: `LAW_OPEN.sub("", t)` strips matches of the same regex `laws()` iterates, so `law_map(unfenced)` is `{}` **by construction** for every input. The per-id sensitivity survives one block up in `E4` | strip only the FIRST opener; assert a strict subset |
| **T2** | **Five ported obligations have no assertion in any tier** — reproduced by gutting all five with every gate green: the empty-diff STOP in `cicd-code-review` (the highest-consequence — the gate-that-cannot-fail class this whole ticket is about), both mutation-doctrine bullets in `cicd-dev-story-tests`, the `landed` exemption and the additive-totals arithmetic in the merge door | add a row each |
| **T3** | Rows pinning a **single generic word** can be gutted green — reproduced for `MERGE-11` (`"additive"`); same construction in `DEV-03b`, `DEV-17`, `MERGE-05`, `QD-C12` | key on the decision, not the vocabulary |
| **T5** | The six `FENCE … byte-identical` rows are **absent, not red**, under `--red` (103 cases vs 109) and nothing says six checks disappeared | emit a failing check in the `else` arm |
| **L5** | The module docstring names an `exists()` guard that does not exist | correct it |
| **L6** | The `LOADERS` check **title** still says "task-lane" after this diff added a story-lane command to it | correct it |
| **L7** | `FENCED_TODAY`'s scope sentence says "Three of the seven still carry none" — now 5 fenced of 7 | correct it |

### Docs

| # | Finding | Fix |
|---|---|---|
| **A1** 🔴 | **The walkthrough has NO `## Disposition ledger`** — acceptance row 1's own named checker. The walkthrough even references "the ledger's 'replaced by' column", and the commit that shipped it is titled "the ledger". The per-ID mapping, the 11 dismissal reasons and the 12 replaced backlog edits exist in **no shipped artifact** | write it |
| **A2** | `QD-C12` is filed **SETTLED but is live and was applied** — its case is RED at `origin/main`. Counts are **56 live / 10 settled**, not 55/11 | fix the roster |
| **A3** | **M16 was declared in the plan's table and is absent from `sweep.json`**; the walkthrough reports "15/15" with no dismissal | add it, or dismiss it explicitly |
| **A6** | The walkthrough's pasted RED transcript says `3/102`; the shipped file yields `3/103` | re-run and re-paste |
| **B5/T6** | The SOP says "**Six laws fenced across four pairs**" then enumerates **15 laws across 5 pairs**, and points at a test that disagrees with its own number | state both correctly |
| **T4** | ~100 acceptance rows are **lane-local** and vanish when the lane is archived; the durable protection is then 6 fences + 1 `LOADERS` entry | promote the highest-consequence literals into a `CS-14 · SCC-212` block in `test_command_surfaces.py` |

---

## DISMISSED — with the reason (the three-question test)

- **A5 — two of eight rules pointers have no inline obligation in a step body**
  (`reproduce-before-you-fix`, `code-standards` §6.5). Acceptance row 2's trigger is *"where Part E
  hoisted a law into a rule"* — neither of these is a Part E hoist, and **nothing was replaced**:
  the command carried no such obligation before, so no pointer displaced one. Each pointer states
  its obligation in its own line. **Does not change behaviour** → dismissed, recorded here.
- **A8 — `git-policy` says "invoking the door IS the sign-off" twice in six lines.** Real
  duplication, no behaviour change. Subsumed by B9, which is the half that is actually *wrong*.
- **T1's rider — `E4` hardcodes the `disposition` literal** and would red if that law were renamed.
  Same class as F11, one row away — but **pre-existing and not in this diff** (question 3).
- **Edge Case's one-off `63/64`** on `rederive-record` identity, unreproducible across 11 further
  runs and most likely a sibling session mutating the live tree during a sweep. Recorded, not
  chased; the fence is byte-identical on inspection and 15/15 mutants killed.

---

## The calibration note

Every finding above came back **reproduced**, not inferred — the two hunters independently hit the
same top defect. The distribution is the signal: **the lenses found almost nothing wrong with the
55 ports themselves** (the Acceptance Auditor confirmed every claimed-applied ID is present in the
diff, and the six fences are byte-identical on both sides). What they found is concentrated in
**the machinery this lane added around the ports** — my new bash blocks, my assertion script, and
my own fix to the parity guard. That is worth carrying forward: the ported content was
well-measured; the scaffolding written *to prove* it was not held to the same bar.
