# SCC-441 — the five lens reports and the clean-code gate, verbatim (2026-09-11)

These are the raw returns of the `code-review-engine` Step 1 fan-out run by `/smh-code-review` at
`dd5a5c42`, copied unedited from each subagent's final message. They are the evidence behind the
findings table in `walkthrough.md` § Code Review (2026-09-11). Where the table and these disagree,
these win — the table is the assessor's reading of them.

Each repo-reading lens ran in its own isolated worktree copy cut at `dd5a5c42`; each reports its
`git rev-parse --show-toplevel` as its first line. The Blind Hunter ran on the diff text alone.

---

> Editorial note (2026-09-11, the fix lane): three paths the lenses quoted are TEMP-REPO FIXTURES or hypotheticals, not files in this tree - a test named test_foo (§1), a docs file named mine and a temp repo's CI workflow (§5). They are prefixed `<fixture>/` in place so `check_links.py` reads them as shapes rather than claims. No other character of the reports changed.

## 1. Blind Hunter (diff only, no repo access)

I have read the full diff (all 13,998 lines) plus run two mechanical cross-checks over it. Here is my report.

### Findings

**severity: important** · **confidence: 0.75** · `.agents/commands/smh-quick-dev.md` (diff lines 2263‑2274, Step 0.5 fence) — *`$L` is used in a fence that never binds it, and the line above it `cd`s away from the lobby*

The edit replaced a self-contained absolute fill with a cross-fence variable:

```
-cd <the lobby's absolute path — the arg resolves from the LOBBY> && python3 .agents/scripts/link-worktree-assets.py .claude/worktrees/<slug>
+cd "$L" && python3 .agents/scripts/link-worktree-assets.py .claude/worktrees/<slug>   # ⛔ the script lives in the LOBBY
```

Evidence chain:
1. `L` is bound only in the **Step 0** fence (diff line 2205). This fence (Step 0.5) contains no `L=`.
2. The repo's own semantics, asserted in this same diff: *"A ```bash fence is its OWN SHELL: nothing a previous fence assigned survives into it"* (`test_boot_epic_branch_read.py`, diff lines 4548‑4558) — and the author records reproducing exactly this death on 2026‑09‑11 in another door.
3. So `$L` is empty; `cd ""` exits 0 **without moving**, and the immediately preceding line in the same fence is `cd "<the new tree>"` (diff line 2270). cwd is therefore the new worktree.
4. `.agents/scripts/link-worktree-assets.py` *does* exist there (a lobby worktree is a full lobby checkout), so the script runs — with the relative arg `.claude/worktrees/<slug>` resolving to `<new tree>/.claude/worktrees/<slug>`, which does not exist. The lane's worktree assets (settings/hooks/skills links) are never linked, and nothing in the door checks.

Corroborating: the unrenamed twin `smh-dev-task-tests.md` (diff line 1541 of the new file) **kept** the safe absolute-fill form, so this is a divergence introduced by this edit, not pre-existing. The author built a per-fence `unbound_L()` checker for precisely this defect class (diff 4559‑4578) but wired it to `cicd-boot-sprint-memory.md` only (`A6`, diff 4625‑4628). My scan of the diff found the same unbound pattern in four more places the checker never looks: `smh-quick-dev.md` Step 1 and Step 5, and `cicd-quick-dev.md` Step 5 (two lines) — those fail more loudly (`python3 .agents/scripts/scope_check.py` → *No such file or directory* when cwd is not the lobby), so the Step 0.5 instance is the dangerous one. **Inferred** from the diff (I have no repo access to execute the doors).

---

**severity: important** · **confidence: 0.8** · `.agents/critical-surfaces.json` (diff line 3075) × `.agents/commands/smh-quick-dev.md` Step 3 (diff line 2569) — *the lobby quick lane's mandatory RED file lives on a surface the lane's own scope check refuses*

1. The lobby's map declares `".agents/scripts/tests/"` under the `ci` surface.
2. `scope_check.pattern_hit` treats a trailing `/` as a prefix (diff 4367‑4373), so `<fixture>/.agents/scripts/tests/test_foo.py` matches → `OVERLAP`, exit 3.
3. `/smh-quick-dev` **Step 3** requires, for any work on a script: *"a real test in `.agents/scripts/tests/test_<name>.py`, run via `run_all.py`"*.
4. Therefore Step 1 (`--paths <the planned set>`, which must include that test file) returns `OVERLAP` for **every** script-shaped quick-lane task — a soft stop only an operator sentence lifts. If the agent omits the test from the planned set, Step 5's `--diff origin/main` sees the committed test file and **ejects** the finished lane to `/smh-dev-task-tests`.
5. The door's own Step 1 prose lists the lobby surface as *"`.github/`, the hooks, the preflights, the permission fence"* (diff 2449‑2450) and never mentions the test directory, so the agent is surprised either at Step 1 or after the work is done.

The map's `why` does deliberately name "gate test", so the *map* is intentional; the defect is that the lane mandates writing into it. Net effect: the quick lane is unusable for script work — which its own Step 3 table explicitly contemplates. **Inferred** (path-matching verified against the code in the diff).

---

**severity: important** · **confidence: 0.7** · `.agents/scripts/scope_check.py` `main()` (diff 4452‑4458) and the Step 5 fences of both quick lanes (diff 1260‑1261, 2805) — *the eject tripwire returns `CLEAR` on an empty diff, the one vacuity the house rule two steps earlier forbids*

1. With `--diff BASE`, `paths` comes from `diff_paths()`; if that list is empty, `main()` skips the `--paths` arm's empty-input guard entirely (that guard is inside the `else:` branch, diff 4459‑4464), prints `CLEAR`, and exits 0.
2. Two reachable ways to get zero: (a) the lane has uncommitted work only — the script "counts committed changes only" (docstring, diff 4315‑4316); (b) `--repo` is filled with the shared checkout rather than the lane tree. Both doors write Step 1 as `--repo "$REPO"` / `--repo "$PROJECT_ROOT"` and Step 5 as `--repo "<the tree>"`; an agent reusing the Step 1 spelling points at a checkout standing on `main`, where `merge-base origin/main HEAD` is HEAD and the diff is empty.
3. Result: `CLEAR` + `DIFF: 0 file(s) vs origin/main`, no eject, and the lane hands off.
4. Both doors quote `tests-must-gate-for-real` as *"An empty diff is a STOP, not a pass … a gate that reads nothing reports green having checked nothing"* — for Step 3, two steps earlier.

Engaging with the stated design: the author chose visibility (`DIFF: <n>`) over refusal and wrote *"so a zero-file run is visibly zero"* (INDEX.md, diff 3874). Visibility is not a gate — and the same author made the sibling input (`--paths` empty) a hard `ERROR` on exactly the opposite reasoning ("silence is UNKNOWN scope"). Nothing in either door instructs the agent to assert `n > 0`. **Inferred**; I could not execute the script (no repo access, read-only).

---

**severity: important** · **confidence: 0.7** · `.agents/commands/cicd-close-story-merge-tree.md` Step 3 (diff 3278‑3287) — *the walkthrough is required to carry the PR URL and to be committed before the PR exists*

1. *"The walkthrough's landing line is written before the PR opens and carries only what is knowable then: the branch, the range, and **the PR URL**."*
2. *"⛔ The walkthrough rides the PR — commit it on the story branch BEFORE the PR opens … write those lines, commit them on the story branch, and only then run Arm A's fence."*
3. Arm A's fence is `git push` → `gh pr create` → `gh pr checks --watch` → `gh pr merge` (diff 3234‑3241). The PR URL first exists at `gh pr create`, i.e. strictly after the required commit.
4. So the instruction is unsatisfiable. The two ways out are both bad: omit the URL from the record the close-out reads, or commit after `gh pr create` — which the same bullet forbids ("it does not change after") and which moves the PR head while `gh pr checks --watch` is running, re-triggering the epic's required checks.

Blast radius is modest (a missing or late URL, or one extra check run), but every FULL/LIGHT close-out hits it. **Inferred** from the diff text alone.

---

**severity: suggestion** · **confidence: 0.7** · `.agents/scripts/scope_check.py` `GENERIC` (diff 4334‑4346) vs `.agents/rules/critical-surfaces.md` (diff 3376‑3379) — *the fallback set does not protect the line itself, so an unmapped repo's line can widen itself*

The rule states the invariant and its enforcement: *"The `ci` surface of every map lists the LINE ITSELF — the map, `scope_check.py`, and this rule … A line that can widen itself is not a line, and the enforcement is a row, not a sentence."* That enforcement is a row **in a map**, and it therefore cannot exist in a repo that has no map — which today is every project (the rule itself says AviationChat's and the skeleton's maps are still rows on AVCH‑152).

Chain: quick lane in an unmapped project → Step 1 `--paths .agents/critical-surfaces.json` → no `GENERIC` pattern matches it (`.github/`, `.githooks/`, `.agents/hooks/`, `.agents/scripts/git-hooks/`, `*.rules`, `firebase.json`, and the segment fragments `auth|session|billing|payment|entitlement`) → `CLEAR`, exit 0 → the lane writes a map. If that map declares even one path, `load_map` returns non-empty rows, `fragments` goes `False` (diff 4484‑4485) and the generic set — including `.github/` and the auth/billing fragments — is switched off for every later run. Three rows in `GENERIC` would close it. **Inferred.**

---

**severity: nitpick** · **confidence: 0.7** · `.agents/commands/cicd-push-e2e.md` (diff 710‑712 vs 733) — *one door, two answers for `AMBIGUOUS`*

Step 0's inserted mode block says `AMBIGUOUS` *"is a STOP: name the one you mean or prune the other **before anything else runs**"*. Step 1 then says `AMBIGUOUS` → *"show each with `git log --oneline origin/main..<branch> | head` and decide together"*. The second is the old, useful behaviour; as written the agent is told to stop before reaching it.

---

### Areas examined with nothing to report

- **Generated-mirror parity.** I compared every mirror's diff body against its source programmatically: all 34 `.opencode/` and `.claude/skills/` mirrors are byte-identical to their `.agents/` masters in this commit, and the `.roo/` launchers are thin stubs whose descriptions were updated in step. The three masters changed without an `.opencode` mirror (`cicd-autopilot-claude.md`, `smh-team-cheshire-cat.md`, `smh-team-queen-of-hearts.md`) are accounted for — the author's own Part C artifact records that the autopilot is claude-only with no opencode mirror. No stale mirror found.
- **`epic_mode.py`.** Exit mapping (`word.split(" ",1)[0]`), the `-light-epic-` containment test vs a `light` slug, origin-only ref reading, the empty-`--repo` guard, `.git`-as-a-file in a linked worktree, and the `uncommented()` comment strip all behave as documented. No defect found.
- **`closeout_preflight._stale_against_sha`.** I specifically checked the exclude-only pathspec `[":(exclude)_artifacts/", ":(exclude)_bmad-output/"]` for the classic "git matches nothing when given only negative pathspecs" trap — `gitglossary` is explicit that with no non-exclude pathspec the exclusions apply to the whole result set, so the documented "whole tree minus the planning surfaces" behaviour is correct. `_QUICK_LANE_RE` matches the exact line every door and rule tells the agent to write, in all the lenient markdown forms the tests exercise, and rejects the near-misses. No defect found.
- **The `/smh-quick-fix` → `/smh-quick-dev` → `/smh-dev-task-tests` re-pointing sweep** (74 references across commands, rules, scripts and tests): I read every one of them in the diff and found no reference left pointing at the retired door as a live lane, and no case where the rename picked the wrong successor.

**6 findings** (4 important, 1 suggestion, 1 nitpick).

---

## 2. Edge Case Hunter (isolated worktree)

Isolation: toplevel `/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/agent-a0969d2636c00e2c4` (my own copy, NOT the builder's tree) · HEAD `dd5a5c425ed521335588573dda98341b4f0af8c2`.

---

- **severity: important** · **confidence: 0.95** · `.agents/commands/cicd-quick-dev.md:237,401,402` and `.agents/commands/smh-quick-dev.md:117,158,315` — **the `$L` fix shipped in this very commit is incomplete: its own new detector finds six more instances it was never pointed at.** *(reproduced)*

  HEAD's commit message says the new check is "block-scoped rather than another `REQUIRED` row, because … a second door-step that repeated the call unbound would stay invisible to it", and the new `unbound_L()` comment says "**every fence, not just Step 2b's**". But the function is only ever called against `BOOT` (`test_boot_epic_branch_read.py:30`, `COMMANDS / "cicd-boot-sprint-memory.md"`). Running the repo's *own* `unbound_L()` over `.agents/commands/*.md`:

  ```
  cicd-quick-dev.md:237  cd "$L" && python3 .agents/scripts/scope_check.py --repo "$PROJECT_ROOT" --paths …
  cicd-quick-dev.md:401  cd "$L" && python3 .agents/scripts/scope_check.py --repo "<the tree>" --diff origin/epic/…
  cicd-quick-dev.md:402  cd "$L" && python3 .agents/scripts/scope_check.py --repo "<the tree>" --diff origin/main
  smh-quick-dev.md:117   cd "$L" && python3 .agents/scripts/link-worktree-assets.py .claude/worktrees/<slug>
  smh-quick-dev.md:158   cd "$L" && python3 .agents/scripts/scope_check.py --repo "$REPO" --paths …
  smh-quick-dev.md:315   cd "$L" && python3 .agents/scripts/scope_check.py --repo "<the tree>" --diff origin/main

  repo's own unbound_L(): 6 offending line(s) across .agents/commands/
  .opencode/commands: 6 offending line(s)      ← mirrored faithfully
  ```

  Evidence chain, `/cicd-quick-dev`:
  - Step 1: `L=$(pwd)` is bound at `cicd-quick-dev.md:92`, inside Step 0.5's fence. Step 1's fence (opens line 236) is a new shell, so `L` arrives empty.
  - `cd ""` exits 0 **without moving**; Step 0.5's last `cd` left the shell inside `$PROJECT_ROOT`/the new tree.
  - `.agents/scripts/scope_check.py` does not exist in a thin project — verified: `ls /home/dlohn/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/.agents/scripts/scope_check.py` → *No such file or directory* (that dir holds only `INDEX.md` and `git-hooks/`).
  - Reproduced with the line exactly as written, `L` unset, cwd in the project:
    ```
    cwd before: /home/dlohn/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT
    python3: can't open file '.../AGY_AVIATIONCHAT/.agents/scripts/scope_check.py': [Errno 2] No such file or directory
    exit=2
    ```
    Control with `L` bound to a lobby that carries the script: `CLEAR` / `MAP: none …` / exit 0.
  - So the critical-surfaces soft stop — the entire point of SCC-443 — never executes at Step 1, and the same at Step 5's tripwire. The door's own text ("`ERROR` → the check did not run") mitigates only if the agent reads stderr; no verdict word is printed at all, and the door's instruction is "Read line 1, the word, never the exit code."

  The full test suite is **86/86 green** on this tree, so nothing catches it. Remedy is one line per fence: `L=$(pwd)` at the top, as Step 0.5 already does.

- **severity: important** · **confidence: 0.85** · `.agents/scripts/scope_check.py:188` — **an absolute path silently defeats a mapped repo's critical-surfaces check: `CLEAR`, exit 0.** *(reproduced)*

  `norm_path()` strips `./` segments and normalises backslashes but does nothing to an absolute path, and `pattern_hit()` for a repo's own map is `path == pattern` / `path.startswith(pattern)` against repo-relative patterns.

  ```
  --paths .agents/scripts/main_write_gate.py                  → OVERLAP  ci: the gates …   (exit 3)
  --paths <repo>/.agents/scripts/main_write_gate.py           → CLEAR                      (exit 0)
  --paths /.agents/scripts/main_write_gate.py                 → CLEAR                      (exit 0)
  ```

  Reachability: `--repo` is documented "repo root, **absolute** — never the cwd", so the same command line requires one absolute argument and silently requires the others to be relative, with no validation. The generic fallback set is unaffected (`segment_hit` splits on `/`), so this fails open only in repos that *have* declared a map — the lobby today, AviationChat and the skeleton with AVCH-152, i.e. exactly where the map is the authority. Author intent runs the other way: the script refuses empty `--paths` because "silence is UNKNOWN scope, never clear"; a path that cannot match is the same silence, and it prints the clear word. `test_scope_check.py` (39 assertions) has no absolute-path case. Remedy: in `main()`, after `repo = Path(args.repo).resolve()`, rebase any absolute path onto `repo` (or `ERROR` on one that lies outside it).

- **severity: important** · **confidence: 0.8** · `.agents/critical-surfaces.json:20-48` — **the lobby's `ci` surface omits the four gate scripts the quick lane's own Step 3 floor runs, so a quick lane can weaken the linter whose green it then reports.** *(reproduced)*

  The changelog claims the surface "grew from four gate scripts to the whole gate family plus its tests, so the quick lane cannot quietly rewrite what 'green' means." It has not. `workflow_lint.py`, `check_links.py`, `check_maps.py` and `mutation_sweep.py` are absent, and so is the brand-new `epic_mode.py`:

  ```
  scope_check.py --repo <lobby> --paths .agents/scripts/epic_mode.py \
        .agents/scripts/lane_qualify.py .agents/scripts/workflow_lint.py
  CLEAR          (exit 0)
  ```

  The loop is concrete: SOP §2147 defines `/smh-quick-dev` Step 3 as "`run_all.py`, `workflow_lint.py --toolkit-only`, `check_maps.py`, `check_links.py` run bare". A quick lane naming `.agents/scripts/workflow_lint.py` at Step 1 gets `CLEAR`, edits it, then reports Step 3 green against the linter it just changed. The line is drawn inconsistently rather than narrowly: `sop_currency.py` and `hooks_armed.py` (lines 37-38) are listed and are neither preflight, receipt, hook nor fence — they are checks, exactly like the four omitted ones. `.agents/scripts/tests/` is a prefix, so `run_all.py` itself *is* covered; it is the four bare-run scripts and `epic_mode.py` that are not.

- **severity: suggestion** · **confidence: 0.75** · `.agents/scripts/scope_check.py:180-186` — **`--diff` with zero changed files prints `CLEAR`, which the same script refuses to do for `--paths`.** *(reproduced)*

  ```
  --diff HEAD (no commits since the base)     → CLEAR / DIFF: 0 file(s) vs HEAD   (exit 0)
     …with uncommitted edits to .github/workflows/ci.yml AND auth.py sitting in the tree
  --paths .github/workflows/ci.yml auth.py    → OVERLAP (two lines)               (exit 3)
  ```

  The author addressed the visibility half — `INDEX.md:79` says the count is printed "so a zero-file run is visibly zero" — but not the verdict half, and both the script's docstring and every door say "**Read the word, not the exit code**". The word is `CLEAR`. Mitigation is real though: both doors say the tripwire runs "committed, after the lane's last commit", so reaching zero needs the agent to run Step 5 early. Remedy consistent with the `--paths` arm: make a zero-file `--diff` print `ERROR` (or at least a non-`CLEAR` word) rather than the pass word.

- **severity: suggestion** · **confidence: 0.7** · absent from `.agents/scripts/task_preflight.py` (cf. `closeout_preflight.py:291-345`) — **the quick lane's approval-staleness check exists only on the project close-out; the lobby close-out never dereferences the sha.** *(traced, not executed)*

  `closeout_preflight` now matches `_QUICK_LANE_RE` and calls `_stale_against_sha(..., "approved")`, which `rep.err`s when code moved after the operator's sha. `/smh-quick-dev` writes the identical line (`smh-quick-dev.md:282`) but hands off to `/smh-close-task-merge-tree` → `task_preflight.check_gate`, which only runs `VERDICT_RE`; with no `Verdict:` it takes the `not stamped` branch and logs "no review Verdict line in this task's own walkthrough - the full gate runs" (`task_preflight.py:1474`), returning `None`. The sha on the record line is never read. The author did engage with the lobby case — SOP §2168: "A lane with no review verdict simply means that close-out runs the whole gate itself instead of inheriting a green, which is the safe direction" — and that is a fair answer for *mechanical* freshness. It is not an answer for the distinct question `_stale_against_sha` was written to ask: did the operator see the tree being landed. Remedy: call the same helper from `check_gate`'s `not stamped` branch when `_QUICK_LANE_RE` matches.

- **severity: suggestion** · **confidence: 0.7** · `.agents/scripts/epic_mode.py:61-78` — **`uncommented()`'s stated safety invariant is false; here is the input that breaks it.** *(reproduced)*

  The docstring argues the scan can only ever strip *more* than it should, "which under-reports armed … It fails toward the loud answer." An **unmatched apostrophe** earlier in the line opens a quote that never closes, so the `#` is treated as inside a scalar and nothing is stripped — over-reporting, the direction the same docstring calls dangerous:

  ```
  line       : "    run: echo it's fine   # TODO: skip on -light-epic-"
  uncommented: "    run: echo it's fine   # TODO: skip on -light-epic-"   → light_armed() = True
  ```

  Eight sibling cases (plain comment, indented comment, real `contains()` check, armed line plus trailing comment, possessive apostrophe *inside* the comment, balanced quote then apostrophe) all behave correctly. The triggering line is contrived — it needs an unquoted apostrophe and the token in a trailing comment on the same line — so the practical risk is low; what is worth the assessor's attention is that the invariant as written is not the one the code holds. Remedy: treat an unterminated quote as "no quote was open" and re-scan for the comment marker.

---

**Checked and clean** (negative results, all executed): the exclude-only pathspec fallback in `_stale_against_sha` works as documented on git 2.43 — a lobby-shaped fixture with no `PRODUCT_DIRS` and post-approval edits to `docs/` and `.agents/` returned both files and blocked, so the "asked of every tracked file" claim holds. All 32 `.opencode/` mirror pairs for branch-touched files are byte-identical; `.roo/` differences are intentional generated launchers, not drift. Retired `/smh-quick-fix` is gone from every surface (`.agents`, `.opencode`, `.roo`, `.claude/skills`). All 12 `epic_mode.py` call sites pin `cd "$L"` **with** an in-fence `L=$(pwd)`. `epic_mode.py`'s empty-`--repo`, non-git-repo and `AMBIGUOUS` paths all behave as documented, and every door handles `AMBIGUOUS`. Suite: **86/86 files passed**.

**6 findings: 3 important, 3 suggestion, 0 critical, 0 nitpick.**

---

## 3. Literal-Correctness Hunter (isolated worktree, 20-file cap)

`git rev-parse --show-toplevel` = `/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/agent-a634a20752bdb4c8a` · `git rev-parse HEAD` = `dd5a5c425ed521335588573dda98341b4f0af8c2` — my own isolated copy, at the expected commit.

**TRUNCATED PASS — I reviewed 20 of the 148 changed files.** I received patches for `.agents/.sync-manifest.json`, `.agents/commands/INDEX.md`, and 18 `.agents/commands/*.md` files (autopilot-claude, boot-sprint-memory, clean-code-audit, close-story-merge-tree, code-review, create-epic-sprint, dev-story-tests, e2e, merge-epic-workingtrees, prune-worktree, push-e2e, quick-dev, resume, write-story-tests, smh-close-task-merge-tree, smh-code-review, smh-designer, smh-dev-task-tests). I did **not** receive the 128 files listed in `lc_withheld.txt` — including every `.agents/rules/*` edit, every `.agents/scripts/*` change (`epic_mode.py`, `scope_check.py`, `closeout_preflight.py`, `task_preflight.py`, `lane_qualify.py`, the whole test suite), `AGENTS.md`, the SOP docs, all `.opencode/` and `.roo/` generated twins, and the task artifacts. **This is not a clean pass over the change set.** I used no top-up on a withheld *command* file; I did open script and rule definitions as ground truth, as the brief directs ("read the script's argparse setup, ls the path, open the rule file").

---

### severity: important · confidence: 0.9 · `.agents/commands/cicd-quick-dev.md:237`, `:401-402` · `cd "$L"` in a fence that never binds `L`

**Definition opened:** `.agents/rules/command-shape.md` §Absolute fills — *"Capture `L=$(pwd)` at the top of the fence, before any `cd`, and pin the call: `cd "$L" && python3 .agents/scripts/<tool>.py …"*, and *"once a fence (or an earlier fence — cwd persists between tool calls) has `cd`'d into a project or a worktree, a bare `python3 .agents/scripts/<tool>.py` resolves against a tree that does not carry the script."*

`L=$(pwd)` appears only at lines 54 and 92. The two new `scope_check.py` fences (Step 1 at 236-238, Step 5 at 400-403) each open a fresh shell and use `cd "$L"` with nothing binding it. The sibling insertion in `cicd-boot-sprint-memory.md:121` states the hazard in its own comment — *"this fence is its OWN shell - Step 0's L does not reach here"* — and binds `L`; these two do not.

- Step 1: Step 0.5's worktree fence and Step 0.6/0.7 leave the shell in the project or its worktree.
- Step 2: Step 1's fence runs `cd "" && python3 .agents/scripts/scope_check.py …`.
- Step 3: `cd ""` exits 0 without moving — reproduced: `bash -c 'cd /tmp && cd "$UNBOUND" && pwd'` → `/tmp`, rc=0.
- Step 4: the interpreter resolves the script against the project tree. **Reproduced:** `cd Projects/AGY_AVIATIONCHAT && python3 .agents/scripts/scope_check.py --repo . --paths backend/x.py` → `python3: can't open file '.../Projects/AGY_AVIATIONCHAT/.agents/scripts/scope_check.py': [Errno 2] No such file or directory`, exit 2. No project carries `.agents/scripts/` at all (`ls -d Projects/*/.agents/scripts` → no such file).

Step 5 is the eject tripwire; a lane whose tripwire dies with exit 2 hands off unchecked. Reproduced.

---

### severity: important · confidence: 0.85 · `.agents/commands/cicd-autopilot-claude.md:168` · the lead is granted an `approved` authority the rules reserve to the operator

**Definitions opened:** `.agents/rules/artifacts-always-first.md` § When to Skip, the quick-lane entry: *"Step 2 writes a short `implementation_plan.md` … and stops for the literal `approved`; Step 4 writes `walkthrough.md` and stops for the literal `approved` again.* **Both stops are Mr. Hatter's.**" And `.agents/rules/000-PLAN-FIRST-GATE.md:28`: *"Has **Mr. Hatter** said the exact phrase 'approved'?"*

The new cell reads `(both `approved` stops are the lead's)`. The same file's line 109 scopes the launch word to *"the rows marked **lead** below"* — and the charter table (lines 113-124, unchanged context) has no row for either quick-lane approval. The diff widened the lead's authority in the route description without widening the charter it points at.

- Step 1: lead runs stage 1 `/cicd-quick-dev <KEY>` as a seated `cheshire-cat` child.
- Step 2: `cicd-quick-dev` Step 2 stops for the literal `approved`; per line 168 the lead supplies it, so a project file is modified with no operator word.
- Step 3: Step 4 stops again; lead supplies it, then writes the record line the diff itself quotes at line 174: `Review: none - quick lane; walkthrough approved by the operator @ <sha>`.
- Step 4: `closeout_preflight.py:290` `_QUICK_LANE_RE` = `r"^[>\-*\s]*\**\s*Review:\**\s*none\s*[-—–]\s*quick lane;\s*walkthrough approved by the operator\s*@\s*`?([0-9a-f]{7,40})"` matches it and emits an INFO — *"quick lane, no review was asked for; walkthrough approved by the operator"*. The close-out proceeds on a machine-read record asserting an operator approval that never happened.

Inferred from the definitions (not executed end-to-end); the regex and both rule texts are quoted verbatim from the tree.

---

### severity: important · confidence: 0.8 · `.agents/commands/cicd-quick-dev.md:330` · names a LOBBY-only script inside a `§BIND`-scoped project command

The rewritten bullet is `- **Story lane only:** advance the story to **`review`** on the way out (`story_status.py`, the normal dev→review flip …)`. It replaced text that attributed the flip to the `bmad-quick-dev` skill.

**Definitions opened:** `.agents/scripts/story_status.py` exists only in the lobby; `find Projects -name story_status.py` returns nothing and `Projects/*/.agents/scripts` does not exist. `cicd-quick-dev.md:22` binds `smh-target-resolution.md` §STD + §BIND — *"every path and child tool call resolves under `PROJECT_ROOT`"*.

This contradicts the file's own standing note three sections earlier (Step 3, kept by this diff): *"⛔ **Prose here on purpose.** `check_links.py` is a LOBBY script and a thin project does not carry it… The `smh-*` doors name the command because they run in the command centre; **naming it here would cite a file that is not on the target (SCC-285)**."* An agent obeying §BIND looks for `PROJECT_ROOT/.agents/scripts/story_status.py`, which is absent in every project in the tree. Inferred; the absence is verified by `find`.

---

### severity: important · confidence: 0.7 · `.agents/commands/cicd-create-epic-sprint.md:135` (and the LIGHT fence at :123) · the mode token's position is claimed but not enforced

The changed line asserts *"the mode token sits between the key and the sprint number (`-epic-` for FULL, `-light-epic-` for LIGHT)"*, and the FULL fence cuts `epic/<JIRA-KEY>-epic-<N>-<slug>` with a free-text `<slug>`.

**Definition opened:** `.agents/scripts/epic_mode.py`, `classify()`: `mode = "LIGHT" if LIGHT_TOKEN in branch else "FULL"` with `LIGHT_TOKEN = "-light-epic-"` — an unanchored substring test over the whole ref name. The script's own docstring claims position (*"`-light-epic-` after the key is the whole switch… The word `light` anywhere else in the slug is not it"*) but the code does not implement it.

**Reproduced** by calling `epic_mode.classify()` directly:

```
epic/AVCH-18-epic-19-student-archive            -> FULL
epic/AVCH-18-light-epic-19-student-archive      -> LIGHT
epic/SCC-441-epic-24-light-epic-rollout         -> LIGHT   <-- cut by the FULL fence
```

A FULL epic whose slug contains `light-epic-` — not far-fetched for this feature area; the current lane is literally `dev-styles-quick-lane-light-epic` — prints `LIGHT`. Every door then takes the LIGHT arm: `cicd-close-story-merge-tree` Arm A tells the agent *"the two E2E checks show as skipped — that is the design, not a red"*, `cicd-push-e2e` Step 1 records *"first and only E2E run"*, and in a repo where CI reads the same token the E2E actually is skipped on an epic the operator chose FULL for. Reproduced.

---

### severity: important · confidence: 0.7 · `.agents/commands/cicd-close-story-merge-tree.md:408-411` · the merge-sha read names a ref that does not exist in the mode that reaches it

The new paragraph says the merge sha *"is its ONLY home"* and gives one way to get it: `cd "<the story worktree>" && git rev-parse origin/epic/<JIRA-KEY>-<slug>`.

**Definition opened:** the same file, lines 340-346 (Arm B, added by this diff): *"**Then Step 4 does not run yet.** … Resume with `/cicd-close-story-merge-tree --after-merge <JIRA-KEY>` once the operator has clicked: verify with `git merge-base --is-ancestor claude/… origin/main`, then Step 4."* And `epic_mode.py`: TRUNK is defined as *"no `origin/epic/*` at all"*.

- Step 1: TRUNK project, Arm B opens the PR into `main` and stops.
- Step 2: operator merges; the agent re-invokes `--after-merge <KEY>`, which routes to Step 4.
- Step 3: Step 4's instruction runs `git rev-parse origin/epic/<JIRA-KEY>-<slug>` in a repo with no `origin/epic/*` → `fatal: ambiguous argument … unknown revision`, exit 128.

The paragraph's reasoning is Arm-A-scoped ("does not exist until Arm A's `gh pr merge` returns") but its claim and its command are unconditional, and TRUNK is the one mode that arrives here without an epic ref. Inferred.

---

### severity: suggestion · confidence: 0.8 · `.agents/commands/cicd-prune-worktree.md:346` · "Only `/cicd-park` sets an upstream" is false in this same file

The rewritten Step 5 rests on a two-case enumeration whose premise is `Only /cicd-park sets an upstream (push -u); the landing pushes the branch as its PR's head with no -u`.

**Definition opened:** the same file, line 226 — the preserve-uncommitted-work path runs `cd "$PROJECT_ROOT"/.claude/worktrees/<slug> && git push -u origin claude/<JIRA-KEY>-<slug>` — and `cicd-close-story-merge-tree.md` (in this diff, Step 3) names it explicitly: *"Step 5's `/cicd-prune-worktree` treats uncommitted work as data to preserve: it commits the tree and runs `git push -u origin claude/<KEY>-<slug>`."*

So a never-parked lane that reached Step 2 dirty lands in the bullet that says *"No upstream, so `-d` already uses merged-into-HEAD and the order changes nothing"* — when in fact it has an upstream set minutes earlier by this same command, and remote-last `-d` passes vacuously exactly as for a parked branch. The section's conclusion (remote first) still holds; the case analysis a reader is meant to reason from does not. Inferred from two quoted lines in the tree.

---

### severity: nitpick · confidence: 0.7 · `.agents/commands/cicd-push-e2e.md:59` vs `:74` · the `AMBIGUOUS` arm the same diff adds is unreachable by the rule the same diff adds

Line 59 (inserted Step 0 block): "`AMBIGUOUS` … is a STOP: name the one you mean or prune the other **before anything else runs**." Line 74 (rewritten Step 1): "**`AMBIGUOUS`** → show each with `git log --oneline origin/main..<branch> | head` and decide together." Both are added lines. Taken literally the Step 0 stop fires first and Step 1's arm never runs. One of the two should say which wins. Inferred.

---

**7 findings: 5 important, 1 suggestion, 1 nitpick — 3 reproduced by execution, 4 inferred from quoted definitions.** Areas I checked and found clean: every script and flag the diff names exists with the claimed interface (`epic_mode.py --repo`, `scope_check.py --repo/--paths/--diff`, `gate_receipt.py run --task/--gate/--root/--cwd`, `mutation_sweep.py --table`, `declared_change_set.py parse`, `workflow_lint.py --toolkit-only`, `sop_currency.py --paths`, `jira_feed.py devrecord/start/check-actions/index-row/finish` and every flag passed); the quick lane's `Review: none - quick lane; …` record line matches `closeout_preflight.py`'s `_QUICK_LANE_RE` byte for byte and `task_preflight.py` correctly treats its absent verdict as "the full gate runs"; every `git-policy.md` and `critical-surfaces.md` section anchor the diff cites resolves; the five-surface claim matches `.agents/critical-surfaces.json`; door parity for the renamed `smh-dev-task-tests` is complete across `.agents/commands`, `.opencode`, `.roo` and both skill trees, the sync manifest is consistent in both of its lists, no dangling `/smh-quick-fix` door reference survives, and `workflow_lint.py --toolkit-only` is 0 errors / 0 warnings on this tree.

---

## 4. Acceptance Auditor (isolated worktree, review_mode: full)

Isolation: `/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/agent-a86a39192c1850a39` @ `dd5a5c425ed521335588573dda98341b4f0af8c2` — my own copy, HEAD is the stated `dd5a5c42`.

### Coverage — every acceptance row in the plan and its five parts

Verification method noted per row: **ran** = I executed the check in my tree; **read** = I inspected the file.

| Row | Statement | State | Evidence |
|---|---|---|---|
| **A·A** | `git-policy` names FULL/LIGHT/TRUNK, both shapes, the token in the switch fence; `quickdev` + direct-push bullet gone | satisfied | ran `grep -rc quickdev .agents/rules/*.md AGENTS.md` → 0; `git-policy.md:32-46,77-106` carry both shapes and the containment rule; `test_trunk_mode.py` block A green |
| **A·B** | Quick lane + rails exist once in `git-policy`; `worktree-per-story` points at them | satisfied | `git-policy.md:167` `## Two toggles, and the rails that never move`; `worktree-per-story.md:72-73` cites it |
| **A·C** | `constitution:23`, `AGENTS.md` GATES, `rules/INDEX` rows, `living-template-sync` `.github` row + matching lists | satisfied | read `constitution.md:23`, `AGENTS.md:154-156`, `rules/INDEX.md:50,51,56`, `living-template-sync.md:5-10` (globs == paths, `.github/**` in both) |
| **A·D** | Landing is the PR road; no fence pushes `HEAD:epic/` | satisfied | ran `grep -n "HEAD:epic" .agents/rules/git-policy.md` → empty |
| **A·E** | RED→GREEN; `run_all`/`workflow_lint`/`check_maps` green | satisfied | ran all three at HEAD: 86/86 files, 0 err/0 warn/8 info, check_maps silent-clean |
| **A·F** | SOP mode block + changelog same commit; `.roo` mirror regenerated | satisfied | changelog row SCC-442 present; `.roo/rules/constitution.md` in the same commit's tree |
| **B·A** | Rule lists five surfaces + map format; lobby map names its gates and says which don't apply | satisfied | read `critical-surfaces.md:23-30`, `.agents/critical-surfaces.json` (5 keys, 4 empty with a `why`) |
| **B·B** | `CLEAR`/`OVERLAP` on line 1, reason per overlap, 0/3, empty→2, merge-base `--diff`, never prompts | satisfied | ran the plan's own Verification #4 → `OVERLAP` + `ci:` line, exit 3; `--paths` empty → `ERROR`, exit 2; `grep -c "input(" ` → 0 |
| **B·C** | Repo map overrides generic; missing map prints the loud line and still checks generic | satisfied | read `scope_check.py` `load_map`/`main`; hardened past spec — an all-empty map also falls back loudly |
| **B·D** | RED→GREEN; `run_all` 85/85 | satisfied (count moved) | ran `run_all` → 86/86 at HEAD (85 was B's own tip; E added `test_epic_mode.py`) |
| **B·E** | Both INDEX rows; `check_maps --strict` clean; `test_rule_frontmatter` green | satisfied | `rules/INDEX.md:56`; check_maps clean; suite green |
| **B·F** | SOP table row + changelog same commit | satisfied | changelog row SCC-443 present |
| **C·A** | Steps 0/0.5/0.7/1/2/3/4/4.5/5 in order, both `approved`, no review gate/engine | satisfied | ran `grep -n "^## "` → exact order; `grep -c code-review-engine` → 0; `test_review_engine` green |
| **C·B** | Step 2 emits a `## Declared Change Set`; the door is an emitter | satisfied | read `cicd-quick-dev.md:282`; `test_declared_change_set.py` S7 green |
| **C·C** | Step 1 + Step 5 call `scope_check.py`; only the operator's quoted word overrides; never proposes a light epic | satisfied (literal count diverges, recorded) | 4 hits not 2 (prose + 3 calls) — walkthrough records the divergence; `grep -n light-epic` → 0 |
| **C·D** | Step 3 RED→GREEN; Step 0.7 fence byte-identical to the twin; directive line stays | satisfied | `test_twin_parity`, `test_directive_quote` green in the suite run |
| **C·E** | Quick-lane record line passes the close-out preflight; "neither" still errs | satisfied | read `closeout_preflight.py:290-428`; regex matches the doors' literal template exactly |
| **C·F** | Guard toml no longer names the door as the gate; `zoo-team`/`AGENTS.md` carry no mandatory review or plan exemption | satisfied | read `bmad-quick-dev.toml:23,44,64-66`; `AGENTS.md:86-99` |
| **C·G** | Autopilot requests review at stage 2, reads no door verdict | satisfied | ran `grep -c "first-pass gate"` → 0 |
| **C·H** | SOP §8, lane table, stop-points, atlas, quickref, changelog same commit; gates green | satisfied | changelog row SCC-444; gates re-run green at HEAD |
| **D·A** | `smh-dev-task-tests.md` is the old body, ≤6 changed lines | satisfied (git reports `A`, recorded) | walkthrough records why git cannot pair them; body verified as the full lane (Steps 1.5/1.6/2/3/3.5/4) |
| **D·B** | New `smh-quick-dev` is the five-step quick lane; `smh-quick-fix.md` gone; INDEX points at the replacement | satisfied (count diverges, recorded) | ran `grep -n "^## "` → the five steps; `smh-quick-fix.md` absent; `commands/INDEX.md:58` is the pointer |
| **D·C** | No live `smh-quick-fix` reference outside history | satisfied | ran the sweep — 7 hits, all retirement notices or changelog history |
| **D·D** | Launchers on every platform; `smh-dev-task-tests` present in all four; `smh-quick-fix` absent from all; manifest updated | satisfied | ran `ls` on all eight paths; `.sync-manifest.json:62,123` |
| **D·E** | The pinned tests move in the same commit; suite/maps/links green | satisfied | ran `check_links --base origin/main` → clean; suite 86/86 |
| **D·F** | SOP §9, quick-lane section, quickref, `artifacts-always-first` § When to Skip, changelog | satisfied | read `artifacts-always-first.md:315-345`; changelog row SCC-445 |
| **E·A** | `epic_mode.py` word + cost line per mode; AMBIGUOUS exits 2; local-only head is not a mode | satisfied | read the script; `test_epic_mode.py` green in the suite |
| **E·B** | Kickoff asks FULL/LIGHT/TRUNK, cuts the right name, records the word on the banner; no `quickdev` in commands | **partly — see findings 1 and 6** | ask + cut fence correct (`:107-129`); `grep -rc quickdev .agents/commands` → 0; the post-cut assertion at `:146` still admits only the FULL shape; the banner instruction exists only in the TRUNK paragraph |
| **E·C** | Twelve doors print the mode line; no door keeps its own `for-each-ref` epic query | satisfied | ran both greps → 12 files / 0 files |
| **E·D** | Two arms; no `HEAD:epic/` fence; the walkthrough rides the PR | satisfied | ran `grep -n HEAD:epic` on the door → only two prose lines saying it is retired; `test_trunk_mode` block B green |
| **E·E** | `/cicd-push-e2e` names LIGHT; `/cicd-e2e` names the branch under test + on-demand run | satisfied | ran `grep -c LIGHT` → 4 and 5; `cicd-e2e.md:2,8,63` |
| **E·F** | Both hand-authored launchers current in both copies; mirrors re-synced | satisfied | ran `diff` on all seven `.agents/skills` ↔ `.claude/skills` pairs → identical; opencode mirrors carry the right bodies |
| **E·G** | SOP, atlas, changelog same commit; gates green | satisfied | changelog row SCC-446; gates re-run green |
| **P·A–E** | Each part's table green | satisfied except E·B | as above |
| **P·G** | Every commit leads with its part's key | satisfied | `git log --format=%s origin/main..HEAD` — SCC-441/442/443/444×2/445/446, no bare subjects |
| **P·H** | One gate at the tip green; riders flip, parent stays open | satisfied in substance, evidence stale — **finding 4** | `task.yaml` carries `riders:[442..446]` + `landing_mode: partial`; receipts stamped `46bc4267`, four commits behind HEAD |
| **P·F** | The closure lane (TEA guide § 6.0, SOP § 6, `smh-new-project.md`) after AVCH-152 | **deferred and recorded** | `declared_change_set.py diff` at HEAD → `unimplemented: [smh-new-project.md, tea_testing_guide.md]` exactly; walkthrough's open box; `tickets/AVCH-152.md` carries the CI/ruleset arming plan |

The LIGHT toggle's server side (the `pr-check.yml` `if:` and the ruleset split) is **deferred and properly recorded** — it is Part E's "Not in this lane", it is AVCH-152's Plan rows 1–2, and `epic_mode.light_armed()` prints a loud `NOT ARMED HERE` caveat derived from the repo so the gap cannot go quiet. I did not treat it as missing.

### Findings

- **severity: important** · **Part E row B** ("asks FULL / LIGHT / TRUNK, **cuts the right name**") · **The kickoff door hard-stops on the LIGHT branch it just told the operator to cut.**
  `.agents/commands/cicd-create-epic-sprint.md:146` reads: *"The echoed line must read `Epic branch: epic/<JIRA-KEY>-epic-<N>-<slug>` — anything else → STOP."* Eighteen lines above it the lane's own new fence cuts `epic/<JIRA-KEY>-light-epic-<N>-<slug>` (`:128`). Concrete failure: the operator answers LIGHT, the agent cuts `epic/AVCH-18-light-epic-19-adk`, line 143's `rev-parse` echoes `Epic branch: epic/AVCH-18-light-epic-19-adk`, and line 146 instructs it to STOP. This line is *not* in the diff — it was correct before, because both pre-lane shapes began `epic/<KEY>-epic-<N>-`; LIGHT replaces `-epic-` with `-light-epic-`, so the lane broke it. `.opencode/commands/cicd-create-epic-sprint.md:146` carries the same text. Reproduced by reading; `grep -rn "Epic branch: epic/"` returns exactly these two lines.

- **severity: important** · **Parent plan, Toggle 1** ("the quick lane, **defined once for both levels**") · **The lobby quick lane records the operator's approval sha and nothing ever reads it; the identical defect was found and fixed on the project side in this same lane.**
  On the project side, `closeout_preflight.py:416-425` matches `_QUICK_LANE_RE` and then calls `_stale_against_sha`, whose own comment says the check exists because *"the quick-lane branch captured its sha, printed eight characters of it and dropped it, so a walkthrough the operator approved at one tree read clean after later commits."* On the lobby side, `/smh-close-task-merge-tree:163` runs **only** `task_preflight.py`, and `task_preflight.check_gate` (`:1391`) reads `VERDICT_RE` alone — I grepped for `quick lane` / `_QUICK_LANE` in that file and got zero hits. Concrete failure: operator approves the lobby walkthrough at sha X; the agent commits three more files; `task_preflight` finds no `Verdict:`, treats it as benign, the full gate runs green, the PR opens, and he merges work he never saw. The `@ <sha>` on `smh-quick-dev.md:282`'s record line is decorative. The author's stated rationale (`smh-quick-dev.md:290-292`: *"it runs the full machine gate itself, the stronger check for a small diff"*) is true about the *tree's* health and silent about the *approval's* scope — a green suite answers "is this correct", not "is this the tree he looked at", which is the exact question `_stale_against_sha` was added to answer.

- **severity: suggestion** · **Parent row H / the drift check the plan says this file feeds** · **One undeclared path at the shipping tip carries no disposition.**
  Ran `declared_change_set.py diff <plan> --changed <git diff --name-only --no-renames origin/main...HEAD>` at HEAD: `undeclared` is 8, and the walkthrough's disposition list (taken at `85454a49`) names 7. The extra is `.agents/scripts/wf_common.py`, added at a later commit — a new `norm_path()` helper, purely additive with no existing behaviour touched, so the risk is the record, not the code. `unimplemented` is exactly the two Part F bullets, as designed.

- **severity: suggestion** · **Parent row H** ("one gate **at the tip** green") · **Every piece of gate evidence is stamped four commits behind HEAD.**
  `gates/suite.json` and `preflight-receipt.json` both record `46bc4267`; the walkthrough's "Gates at the shipping tip" says `85454a49`. HEAD is `dd5a5c42`, whose subject is *"fix(gates): the two reproduced defects, each pinned by a test seen red"* — i.e. gate code and tests moved after the evidence was taken. `main_write_gate.py:392-395` states this exact rule for itself: *"a receipt produced three commits ago is byte-identical and vouched for code it never saw."* I re-ran all four gates at HEAD and the substance holds — `run_all` 86/86, `workflow_lint --toolkit-only` 0 errors/0 warnings/8 info, `check_maps --depth3-only --strict` clean, `check_links --base origin/main` clean — so this is a refresh before the PR, not a red. One knock-on: the receipt's `verdict_sha: 46bc4267` still points at the `Verdict: PASS` stamp that `fcaccebf` retracted from the walkthrough.

- **severity: suggestion** · **Part E §4 / row D** · **Arm A tells the agent a skipped E2E "is the design, not a red" unconditionally, in the one repo state where that is false.**
  `cicd-close-story-merge-tree.md:308-311`: *"on LIGHT only the two fast checks run and the two E2E checks show as skipped — that is the design, not a red."* The author engaged with exactly this risk elsewhere: `epic_mode.light_armed()`'s docstring says *"LIGHT is a local convention until a repo's `pr-check.yml` skips its E2E jobs on the token — which today NO repo does"*, and appends a `⛔ NOT ARMED HERE` caveat to the mode line. That mitigation sits at Step 0; the sentence an agent reads at the landing moment, 250 lines later, carries no pointer back to it. A one-clause conditional ("unless Step 0's mode line said NOT ARMED") would close it.

- **severity: suggestion** · **Part E row B**, third clause ("records the word on the banner") · **The banner instruction exists only inside the TRUNK-answer paragraph.**
  `cicd-create-epic-sprint.md:114` is in the TRUNK bullet; its aside *"the FULL and LIGHT answers record theirs the same way"* points at an instruction that has no FULL/LIGHT home, and Step 3's board write (`:213-225`) says nothing about the mode word. Row B's own check (`grep -rc quickdev` = 0) does not test this clause at all. Impact is small because FULL/LIGHT are readable from the branch name and TRUNK — the case with no branch to read — is the one that *does* carry the instruction.

- **severity: nitpick** · **Part E §3** ("echo both lines; they govern…") · `epic_mode.py` can print `ERROR` (not a git repo, git failed) and 11 of the 12 doors name only `AMBIGUOUS` as a stop. Measured: `grep -c AMBIGUOUS` → 1 in each of 12; `grep -c '\`ERROR\`'` → 0 in 11 (the one hit, in `cicd-quick-dev.md`, is `scope_check`'s ERROR). The word is loud and carries its own reason line, so the practical exposure is small.

- **severity: nitpick** · **the lane record** · `_artifacts/_main/INDEX.md:7` says "144 files"; the diff at HEAD is 148 paths.

**8 findings: 0 critical · 2 important · 4 suggestion · 2 nitpick.** No acceptance row is unsatisfied in substance except Part E row B's cut-verification clause (finding 1); Part F and the AVCH-152 server side are deferred and recorded correctly.

---

## 5. Test-Adequacy Auditor (isolated worktree)

`/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/agent-a3cb4803334078419` @ `dd5a5c425ed521335588573dda98341b4f0af8c2` — my own isolated worktree, HEAD is exactly the SHA under review.

**Baseline**: `python3 .agents/scripts/tests/run_all.py` → `86/86 files passed` (30s). Every mutation below was applied in the tree, run, and restored by SHA-256 comparison.

**Final `git status --short`:**
```
?? .claude/agents
?? .claude/commands
?? .claude/hooks
?? .claude/launch.json
?? .claude/loop.md
?? .claude/routines
?? .claude/scheduled_tasks.json
?? .claude/workflows
```
`git diff --stat HEAD` is **empty** — zero tracked modifications. Those eight `??` rows are the sandbox bind-mount points; they were present at session start and I never wrote to them.

---

### Findings

**severity: important** · `.agents/commands/cicd-quick-dev.md:346`, `.agents/commands/smh-quick-dev.md:282` ↔ `.agents/scripts/closeout_preflight.py:289` · **The quick lane's record-line WRITER and READER are never checked against each other — a gate that cannot fail**
Missing tier: a contract/unit test binding the door template to `_QUICK_LANE_RE`. `test_closeout_preflight.py` QL1–QL16 exercises the reader exhaustively, but every string it feeds is typed inside the test file; nothing reads the doors. **Mutation run:** I changed `walkthrough approved by the operator @ <sha>` → `walkthrough signed off by the operator @ <sha>` in all ten writer files (both doors, both `.opencode` mirrors, `cicd-autopilot-claude.md`, `zoo-team.md`, `artifacts-always-first.md`, `.roo/rules/zoo-team.md`, the SOP and its changelog) and ran the **whole suite: 86/86 files passed**. The consequence is already proved by the test file's own QL16 CONTROL row — "a different verb" is *not* the record line, so a lane that did exactly what the door said gets `no Verdict: line - the review step has not run`, and the agent's natural repair is to add a `Verdict:` stamp, which pulls `walkthrough_roster` in for lenses that never launched (the SCC-173 trap this design exists to avoid). Suggested test: in `test_command_surfaces.py` (precedent: CS-24 "the approval-sha WRITER and READER agree"), extract the literal template line from each quick-lane door, substitute a real sha, and assert `closeout_preflight._QUICK_LANE_RE.search(...)` matches.

**severity: important** · `.agents/scripts/tests/test_scope_check.py:~205` ("the script has no override flag") · **The no-bypass assertion greps for one word; the two bypasses the rule names by name walk straight through**
Missing tier: a behavioural unit case, not a source grep. The check is `"override" not in src.lower().replace(...)`, while `critical-surfaces.md` § The stop says "There is no agent override, **no `--force`**, no 'small enough' class". **Mutations run (`test_scope_check.py`, 80/80 green both times; also re-run against the whole suite for the first → 86/86):**
- added `ap.add_argument("--force", action="store_true")` plus `if args.force: print("CLEAR"); return EXIT["CLEAR"]` → **SURVIVED**
- added `if os.environ.get("SCOPE_CHECK_SKIP"): print("CLEAR"); return EXIT["CLEAR"]` → **SURVIVED**

Either is a real, agent-passable way to make the quick lane's only line over auth/billing/CI print `CLEAR`. Suggested test: run the script with `--force`, `--yes`, `--skip`, `--no-check` and an env-var sweep against a path that must OVERLAP, and assert every invocation still exits 3 with `OVERLAP` on line 1 (behavioural, so it cannot be evaded by naming the flag something other than "override").

**severity: important** · `.agents/scripts/scope_check.py:180` (`diff_paths`) · **The merge-base is the whole point of `--diff` and no test distinguishes it from the two-dot diff**
Missing tier: a unit case whose fixture advances `main` after the fork. The module docstring says "never the two-dot range (`risk_seam.py` names the two-dot mistake as the expensive one)", but `test_scope_check.py` block E builds the branch and never moves `main`, so the two spellings are identical there. **Mutation:** `changed_since_fork(repo, "HEAD", fork)` → `changed_since_fork(repo, "HEAD", base)` — **SURVIVED** `test_scope_check.py` (80/80) and the full suite (86/86). **Reproduced behaviour difference** in a repo where the lane touched only `<fixture>/docs/mine.md` and `main` then landed `<fixture>/.github/workflows/ci.yml`:
- HEAD: `CLEAR` / `DIFF: 1 file(s) vs main`, exit 0
- mutant: `OVERLAP` / `DIFF: 2 file(s) vs main` / `.github/workflows/ci.yml  ci: …`, exit 3

That is the eject tripwire firing on a file the lane never touched — the false positive the rule itself says is "the first thing the operator switches off", and `main` moving under a lane is the house's normal state. Suggested test: extend block E — after cutting the docs branch, commit a `.github/` change on `main`, then assert `--diff main` is still `CLEAR`.

**severity: important** · `.agents/scripts/scope_check.py:102` (`load_map`) · **A bare-word path in a repo's own map is a silently dead pattern — the exact failure the `null`/empty validation was added to prevent**
Missing tier: a unit case in `test_scope_check.py` block D. `load_map` rejects a non-string or whitespace entry with the reason "a dead pattern reads as a protected surface", but a bare word is dead the same way: with `fragments=False` it falls to `path == pattern`, so `"paths": ["auth"]` matches only a repo-root file literally named `auth`. This is the likeliest authoring mistake, because `critical-surfaces.md` itself publishes `auth`, `session`, `billing`, `payment`, `entitlement` as the generic fragment list one page above the map format. **Reproduced (no mutation needed):** a map declaring `{"auth": {"why": "accounts", "paths": ["auth"]}}` answers `CLEAR` for `backend/auth/token.py`, exit 0. Suggested test: a map whose only path is a bare word must exit 2 with `ERROR` naming the entry (or, if bare words are meant to be fragments, assert the OVERLAP — either way, pin one).

**severity: suggestion** · `.agents/scripts/scope_check.py:130` (`pattern_hit`) · **The "a declared path is never widened into a substring search" contract has no case**
Missing tier: a unit case. **Mutation:** dropped the `fragments and` guard — **SURVIVED** (80/80). **Reproduced difference:** with the map above, HEAD says `CLEAR`, mutant says `OVERLAP backend/auth/token.py  auth: accounts`. Block B's "a repo map WINS" case uses only patterns containing `/` or `.`, so it never reaches this branch. Suggested test: one map with a bare-word path, asserting exact-file semantics (pairs naturally with the finding above).

**severity: suggestion** · `.agents/scripts/scope_check.py:146` (`overlaps`) · **The documented "at most ONE line per path" contract is unpinned**
Missing tier: a unit case with a path on two surfaces. **Mutation:** deleted the `break` — **SURVIVED** `test_scope_check.py` (80/80) and the full suite (86/86). **Reproduced:** `--paths backend/auth/session.py` in an unmapped repo prints one line at HEAD and two identical-surface lines under the mutant (it hits both the `auth` and the `session` generic fragments). Block B's `len(hit) == 1` row cannot catch it because every map path there claims a disjoint set. Suggested test: assert exactly one overlap line for `backend/auth/session.py` in an unmapped repo.

**severity: suggestion** · `.agents/scripts/epic_mode.py:76` (`uncommented`) · **The quote-awareness branch is dead to the suite**
Missing tier: one unit line-case. **Mutation:** deleted the quote tracking entirely — **SURVIVED** `test_epic_mode.py` (30/30) and the full suite (86/86); block E3's "a REAL read on a line that ALSO carries a comment" case has the `#` *after* the token, so a naive first-`#` cut still keeps it. **Reproduced:** `run: echo "build #4 targets -light-epic-"` keeps the token at HEAD and loses it under the mutant, flipping a genuinely armed repo to `NOT ARMED`. **Engaging with the author's stated rationale:** the docstring argues the scan "fails toward the loud answer" and under-reporting armed is "merely redundant" — that is right, and it is why this is a suggestion rather than important. It is still a branch nothing executes. Suggested test: one `light_armed` case on a workflow line carrying a `#` inside a quoted scalar before the token.

**severity: suggestion** · `.agents/scripts/closeout_preflight.py:300-335` (`_stale_against_sha`) · **Three of the helper's small decisions are unexecuted by any case**
Missing tier: unit cases in `test_closeout_preflight.py`. All three mutants **SURVIVED** (115/115): (a) `say = rep.warn if what == "reviewed" else rep.err` → `say = rep.err` — the verdict arm's *warn*, which the comment calls "asymmetric on purpose… the asymmetry is the whole point", has no case; only the approved arm's err is pinned by QL9/QL10; (b) removing `":(exclude)_bmad-output/"` from the fallback pathspec — QL19 pins `_artifacts/` only; (c) widening `PRODUCT_DIRS` to include `.github/` at the call site, which the import comment bans by name ("PRODUCT_DIRS, never DEPLOY_DIRS — `.github/` is not product code", SCC-118). Suggested test: one fixture with an unresolvable **verdict** sha asserting a WARN and no ERROR; one fallback-arm fixture committing under `_bmad-output/` asserting no STALE; one fallback-arm fixture with a `.github/` dir present asserting the pathspec still falls back.

**severity: suggestion** · `_bmad/custom/bmad-quick-dev.toml:35-46` · **"No house door launches this skill" is now load-bearing law with no guard**
Missing tier: a door-scan case. SCC-444 collapsed the plan-first gate's two satisfactions to one on the strength of that sentence, but `test_bmad_token_gate_retired.py` only pins the token-size facts; no test asserts the premise. I verified it holds today (`grep -rln bmad-quick-dev .agents/commands/*.md` → nothing). The analogous retirement one file over — `quickdev` absent from four law files — *is* pinned by `test_trunk_mode.py` block A with the reasoning "a retired mode named in the law is a mode an agent will try to select". Suggested test: assert no `.agents/commands/*.md` names `bmad-quick-dev` while the toml carries "There is exactly ONE way that gate is satisfied".

**severity: nitpick** · `.agents/scripts/epic_mode.py:88` / `scope_check.py:198` · Two micro-branches nothing runs: `light_armed` accepts `.yaml` as well as `.yml` but every fixture writes `pr-check.yml` (mutation to `(".yml",)` **SURVIVED**, 30/30); and `args.repo.strip()` guards a whitespace-only `--repo`, but only `""` is tested (mutation to `not args.repo` **SURVIVED**, 80/80). Both fail toward the loud side. One suggested test each: a `pr-check.yaml` arming case, and `--repo "  "`.

---

**Areas I checked and found adequate — reportable as clean:** the LIGHT/FULL/TRUNK classification (block A–D of `test_epic_mode.py` kills the obvious mutants, including local-vs-origin and the `light` in-slug case); the "a comment is not an implementation" probe (E3 is a genuine red-seen gate); the `_QUICK_LANE_RE` *reader* itself (QL16's seven lenient forms plus four controls, including a 6-char sha — tightening or loosening the regex reds); `_stale_against_sha`'s no-product-dir fallback arm (QL17–QL20c, and the author explicitly recorded that the pre-fix version left the file green); and the retirement of `/smh-quick-fix` — every one of the five surviving live-law references explicitly says "retired", so no stale routing exists.

**Tier 3 (judge-style behavioural tests):** none exist here, for this diff or anywhere in the repo. Roughly 3,000 lines of new agent-prompt behaviour ship in `smh-quick-dev.md`, `cicd-quick-dev.md` and `smh-dev-task-tests.md`, all verified by markdown scans that the instruction *text is present* — never that an agent following it stops on OVERLAP, or writes the record line the reader parses. I raise this once, as the house's architecture rather than this lane's omission; the cheapest partial substitute is the writer/reader binding in finding 1, which converts one prompt-behaviour claim into a machine-checkable one.

**Count: 10 findings — 4 important, 5 suggestion, 1 nitpick. Six reproduced by executed mutation (all restored byte-for-byte), two reproduced by direct execution without mutation, two by absence-of-coverage inspection. Tree left clean.**

---

## 6. Clean-code gate, Step 3.5 (isolated worktree, nested — §2A + §2C only)

Isolation verified: toplevel is `/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/agent-abd9da8742d72915b` (my own copy, **not** the SCC-441 dev tree), HEAD `dd5a5c425ed521335588573dda98341b4f0af8c2` = `dd5a5c42` as expected. Read-only throughout — no tracked file was edited, written or deleted.

### What I found, in plain terms

The substance of this lane is two new gate scripts, and both are unusually well-reasoned code — the comments carry real *why*, the error paths refuse empty input loudly instead of quietly passing, and the `closeout_preflight.py` change is itself a repair of a check that could not fail. The convention half of the audit came back completely clean, and so did the AIDEV-anchor half.

What did not survive is a pair of factual claims inside `epic_mode.py`'s own comments, and they matter more than their size suggests because this file's whole job is to stop an agent believing something about CI that isn't true.

The first is a **self-contradiction the branch introduced**. The module docstring's "THE TOKEN" paragraph tells the reader that `-light-epic-` is "the same substring the epic ruleset globs and `pr-check.yml` reads with `contains()`" — a present-tense statement that the CI wiring exists. Sixty lines below, `light_armed`'s docstring says the opposite: LIGHT "is a local convention until a repo's `pr-check.yml` skips its E2E jobs on the token — which today NO repo does." Git history shows exactly how it happened: commit `4d7b3a2e` wrote the docstring and had no `light_armed` at all; commit `85454a49` added the arming detector and never went back to the top of the file. The reader who opens this file starts at line 1, forms the belief the detector exists to prevent, and never questions a LIGHT cost line.

The second is a **safety argument that is demonstrably backwards**. `uncommented()` claims an escaped `\"` "can only make the scan strip MORE... It fails toward the loud answer." I reproduced the opposite: on `run: echo "a \" b" # -light-epic- is only a comment` the early quote-close lets the *next* `"` re-open a quote that swallows the `#`, so nothing is stripped and the token survives out of a pure comment. `light_armed` then returns True, the NOT-ARMED caveat is suppressed, and the cost line promises "two checks, E2E once" in a repo still running four — which is precisely what the same file calls "the worst kind of wrong" and "hides a live E2E." The existing test block E covers the full-line comment and the inline trailing comment; this shape is the gap between them.

### Findings

| # | file:line | Severity | Standard | Concrete consequence | Remedy |
|---|---|---|---|---|---|
| 1 | `.agents/scripts/epic_mode.py:24-25` | **important** | §2A / code-standards §1 — "stale comments left behind by a change" | Module docstring asserts `pr-check.yml` already "reads with `contains()`"; `light_armed:85-87` in the same file says no repo does. Verified by history: `4d7b3a2e` wrote the docstring with no `light_armed`, `85454a49` added it and left the docstring. An agent reading the file's opening paragraph concludes LIGHT is wired and accepts a LIGHT cost line unchallenged — the exact belief `light_armed` was added to break. | Re-word to future tense — the token is what a repo's `pr-check.yml` *will* read once armed (AVCH-152) — and point the paragraph at `light_armed`. |
| 2 | `.agents/scripts/epic_mode.py:65-68` | **important** | §2A / code-standards §1 — a comment making a false factual claim | "can only make the scan strip MORE… fails toward the loud answer" is false. Reproduced: `run: echo "a \" b" # -light-epic- is only a comment` strips **nothing**, token survives from a pure comment → `light_armed` True → NOT-ARMED caveat suppressed → cost line promises the LIGHT discount in an unarmed repo. That is the over-report direction the file itself calls "hides a live E2E". | Skip the character after a `\` while inside a double-quoted scalar (one line in the loop); that makes the docstring's claim true again. Add the case to test block E beside the two comment shapes already pinned. |
| 3 | `.agents/scripts/scope_check.py:188` | nitpick | §2C / code-standards §2 — "no dead branches" | `(args.paths or [])` — reached only when `args.diff is None`, and the required mutually-exclusive group plus `nargs="*"` then guarantees a list (`[]` at worst), never `None` (reproduced against argparse). The guard reads as though `--paths` can be absent, a state the parser refuses; a later edit may build real `None` handling on top of a case that cannot occur. | `[norm(p) for p in args.paths if norm(p)]`. |

### Areas that came back with zero findings — stated, not padded

**AIDEV anchors:** zero added, zero removed, zero invalidated across the entire 148-file diff; the four changed scripts carry none, so nothing was silently dropped.

**Rest of §2A:** no commented-out code. No unowned `TODO`/`FIXME` — the only `TODO` strings are quoted test-fixture data and prose *about* a TODO, and the fixture's own is `# TODO(AVCH-152):`. No comment merely restating its code; the comment density here is high but every block carries an `SCC-<n>` provenance and a reason.

**§2C convention table, entirely clean on added lines:** no line over 120 chars; every added `def` carries full argument and return annotations; no f-string without a placeholder; `Path(__file__).resolve().parent` throughout with no hardcoded CWD; both-machines clean — no bare `python`, no `C:/` path, no `;` separator, no `robocopy`, and the twelve door call lines all carry the `# PC: \`python\`` twin. No leftover debug prints (every `print(` on an added line is the scripts' documented stdout contract), no bare `except:` or unlogged `except Exception`.

**Gates ship able to fail:** both new scripts refuse unknown input loudly — `--repo ""` → ERROR, empty `--paths` → ERROR *"silence is never clear"*, unparseable map → ERROR, empty map → loud GENERIC fallback rather than a quiet `CLEAR`.

**Strong claims I verified as TRUE** (the §2A check cuts both ways): "twelve doors now call this" — exactly 12 `cicd-*.md` files, and pinned by a test; the `lane_qualify.py:24-27` citation lands exactly on the READ THE WORD block; `sop_currency._SURFACES`, `lane_qualify.norm` and `sop_currency._norm` all exist as described; "Import-safe: guarded by `if __name__ == '__main__'`" — AST-verified, zero non-declarative top-level nodes in `task_preflight.py`; "PRODUCT_DIRS, never DEPLOY_DIRS, `.github/` is not product code" — `DEPLOY_DIRS = PRODUCT_DIRS + (CI_DIR,)`, five product dirs, lobby carries none; "the caller fetches first" — `git fetch origin --prune` precedes the mode line in the doors I sampled.

### Imported results and the machine floor

Imported unchanged from the caller at this same sha, not re-run per the narrowing: `run_all.py` 86/86 files passed · `workflow_lint.py --toolkit-only` 0 errors, 0 warnings, 8 info (UTF-8 BOM notices on vendor `testarch-*` files) · `check_links.py --base origin/main` clean · `check_maps.py --depth3-only --strict` clean · `py_compile` green on the 3 changed `.py` files. The §2B drift-hunt was not re-swept; findings 1 and 2 surfaced during the §2A comment pass.

**The four machine-floor commands of code-standards §6 — `ruff check`, `pyrefly check`, `npm run lint`, `npx tsc --noEmit` — do not exist in this repo.** There is no venv, no `backend/`, no `frontend/`, no `package.json`, and no linter or type checker installed. This is not a skipped check: the enforcement suite plus `workflow_lint --toolkit-only` and `py_compile` **are** the objective floor here, and they are green.

Suggested gate verdict for you to assess: **CONCERNS** — both important findings are comment-contract violations, which the ladder caps at CONCERNS; nothing in the FAIL column fired.

```
$ git status --short
?? .claude/agents
?? .claude/commands
?? .claude/hooks
?? .claude/launch.json
?? .claude/loop.md
?? .claude/routines
?? .claude/scheduled_tasks.json
?? .claude/workflows
```

Zero tracked modifications — every `??` row is a sandbox bind mount, not a file I created.
