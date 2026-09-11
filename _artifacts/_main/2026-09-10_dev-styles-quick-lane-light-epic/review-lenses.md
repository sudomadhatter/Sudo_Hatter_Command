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

---

# Second pass (2026-09-11, at `ffca21c7` — after the thirty-row fix batch)

> The five lens reports, the Evidence Verifier's table and the Compound Synthesis role's findings, verbatim, from the `/smh-code-review` run whose record is walkthrough.md § Code Review (2026-09-11, second pass). Paths the lenses quote from their TEMP-REPO fixtures are prefixed `<fixture>/` so `check_links.py` reads them as shapes rather than claims; no other character changed.

## Blind Hunter (diff only, no repo access)

Blind Hunter — diff only, no repo access, read 15576 of 15576 lines (the 2,941 lines of `.opencode/` and `.roo/` mirror hunks at patch L7170–10141 were verified byte-identical to their `.agents/` source hunks by a programmatic comparison over the patch, not re-read by eye).

### Findings

- **severity: important** · **confidence: 0.8** · `.agents/rules/git-policy.md` hunk `@@ -153,6 +164,46 @@` (patch L3648, § Two toggles table row 5) · The "defined once" lane definition puts the eject tripwire in the close-out door; the sibling rule in the same diff says the close-out doors never run it
  Evidence chain: Step 1 — git-policy row 5 reads "5. Close | the normal close-out door for the level. **Its** eject tripwire re-runs the scope check on the real diff" (L3648); the doors, INDEX and artifacts-always-first all point at this section as the single definition ("this door IS the quick lane, defined there once", L811-812, L2180-2181, L3325). Step 2 — `critical-surfaces.md` § The wire-in (L3501-3503) states the opposite: "Step 5 of the same two doors, before the hand-off (not the close-out: the close-out doors do not call this script, and saying they did sent a reader to the wrong door)". Step 3 — the diff confirms which is true: the only `scope_check.py` call sites are `cicd-quick-dev.md` Steps 1/5 and `smh-quick-dev.md` Steps 1/5 (`test_scope_check.py` block G, L6551-6564), and the close-out gate `task_preflight.py` gains only the record-line reader (L4600-4603, L4696-4719), no scope check. Step 4 — an agent that reads the hub rule (59 inbound refs per `doc-graph.md` L15472) believes the door will trip and treats the quick-dev door's Step 5 as a courtesy; nothing at `/smh-close-task-merge-tree` runs the line, so an under-declared overlap reaches `main` unchecked. The implementation plan carries the same wrong row (L10577), so this is a design-record error propagated into law, not a typo.
  Reproduced or inferred: inferred from the diff — the two rule texts are quoted verbatim and the absence of any close-out call site is what the diff's own test G asserts.

- **severity: important** · **confidence: 0.7** · `.agents/commands/smh-quick-dev.md` hunk `@@ -156,374 +150,191 @@` (patch L2605-2612, Step 3 "the lobby floor, bare") · The quick lane's only machine floor is four bare script lines with no tree pin, so it measures whatever tree the shell was last left in — by the door's own sequence, the shared checkout on `main`
  Evidence chain: Step 1 — Step 1's fence ends with `cd "$L" && python3 .agents/scripts/scope_check.py …` (L2480-2481), leaving cwd at the lobby's shared checkout; Step 2 is prose only. Step 2 — Step 3's floor fence is `python3 .agents/scripts/tests/run_all.py` / `workflow_lint.py --toolkit-only` / `check_maps.py` / `check_links.py --base origin/main` with no `cd "<tree>" &&` on any line (L2608-2611); the RED table one paragraph up also names `run_all.py` unpinned (L2581). Step 3 — the house's own doctrine, restated in this diff, is that cwd persists between tool calls and "cwd is not intent" (L378-379, L822, the retired text at L1067-1070); the same file pins every OTHER fence (`cd "$REPO"` L2312-2317, `cd "$L"` L2481, L2863), and the full lane routes the identical floor through `gate_receipt.py … --cwd <worktree>` (L1861-1864). Step 4 — run from the shared checkout on `main`, `run_all.py` never sees the lane's new test file, `check_links.py --base origin/main` diffs `main` against itself and reports clean over nothing, and `workflow_lint` lints the unchanged toolkit: the floor prints green totals that the walkthrough pastes as evidence (L2631-2632) while the lane's tree was never measured. `cicd-quick-dev.md` Step 3 (L1135-1140) has the same shape in prose with no fence at all.
  Reproduced or inferred: inferred from the diff; the vacuous outcome depends on the cwd the previous tool call left, which is exactly the state the diff's own rules say must never be relied on.

- **severity: important** · **confidence: 0.85** · `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/handoff.md` hunk `@@ -0,0 +1,181 @@` (patch L10383-10385, L10401-10427, L10465-10472, L10526) · The hand-off record, written "for the next agent", states a suite receipt, a freeze and an unfixed findings table that the sibling records in the same diff contradict
  Evidence chain: Step 1 — handoff.md: "Suite | `run_all.py` 86/86 files … `<fixture>/gates/suite.json` stamped @ `dd5a5c42`" (L10384) and "`<fixture>/gates/suite.json` — the suite receipt @ `dd5a5c42`" (L10526). Step 2 — the receipt shipped beside it says `"sha": "fb2639ac…"`, `87/87 files passed` (L10329, L10340), and the walkthrough's gate line agrees: "Gates at the fix tip (`fb2639ac`) … 87/87" (L12912-12914). Step 3 — handoff.md § How to continue instructs "Get the operator's word before touching any rule, gate or test … It is not lifted now" (L10466-10469) and § What is broken lists rows 1, 8, 9 as open (L10409-10424); the walkthrough's `## Your Actions` records the freeze lifted ("approved to fix this", L12993) and its § Changes applied marks all 29 text/code rows `applied @ <sha>` (L13048-13076, L13123-13130). Step 4 — a next agent that starts where the file tells it to (handoff first, "check it; do not take it on trust") re-derives 30 fixes that already landed, or refuses under a freeze that was lifted; a stale hand-off that contradicts the record it points at is the exact failure the file's own opening paragraph warns about.
  Reproduced or inferred: inferred purely from the diff; every quoted claim and its contradiction are in the patch.

- **severity: suggestion** · **confidence: 0.85** · `.agents/commands/cicd-quick-dev.md` hunk `@@ -66,17 +86,21 @@` (patch L908-913) and `.agents/commands/smh-quick-dev.md` hunk `@@ -51,25 +59,29 @@` (patch L2317-2318) · `git worktree add --no-track …` followed by `git branch --unset-upstream` is a guaranteed `fatal:` on every quick-lane open
  Evidence chain: Step 1 — the fence cuts the lane with `--no-track` (L908, L910, L912, L2317), which by definition writes no `branch.<name>.merge`/`remote` config. Step 2 — the next line runs `cd … && git branch --unset-upstream   # belt and braces: no upstream until the lane's own first push` (L913, L2318). Step 3 — `git branch --unset-upstream` on a branch with no upstream exits 1 with `fatal: Branch '<name>' has no upstream information`. Step 4 — every quick-lane Step 0.5 now prints a `fatal:` line mid-fence; the doors elsewhere tell the agent to read exit codes and treat a red as a stop (L1612-1619), so the "belt" is a false red that a later reader either stops on or "fixes" by dropping `--no-track` — restoring the upstream-to-epic the comment two lines up forbids. The correct shape (`--no-track` alone) already exists in this diff at `cicd-write-story-tests.md` L1397-1402.
  Reproduced or inferred: inferred from the diff; git's behaviour on `--unset-upstream` with no upstream is deterministic.

- **severity: suggestion** · **confidence: 0.75** · `.agents/scripts/scope_check.py` `load_map` (patch L4440-4451) with `pattern_hit` (L4406-4412) · A directory declared without its trailing slash, or any path with a leading `/`, is accepted as a "protected" exact pattern that can never match a real path — the same dead-entry class the new bare-word guard closes, one character wider
  Evidence chain: Step 1 — `load_map` refuses `null`/empty entries and bare words that name no root file, both on the stated reasoning "a dead pattern reads as a protected surface" (L4434-4439, L4441-4450); it validates nothing else. Step 2 — an entry like `"answers": {"paths": ["backend/agents/specialist"]}` (the rule's own example minus its slash, L3431) or `"/backend/"` (`norm_path` strips only `./`, L6887-6890) falls to `path == pattern` / `path.startswith("/backend/")` (L4406-4412). Step 3 — `git diff --name-only` never yields a directory path and no repo-relative file equals or starts with those strings, so `<fixture>/backend/agents/specialist/faa.py` answers `CLEAR`, exit 0, with no `MAP:` line to say anything is wrong. Step 4 — the map author sees a row and believes the surface is guarded; the quick lane walks through it. The author's engagement with the bare-word case argues for this one: it is the likelier slip (a copied directory path missing its `/`) and it is detectable the same way (`(repo / pat).is_dir()` → ERROR "a directory needs a trailing `/`").
  Reproduced or inferred: inferred from the code in the diff; `test_scope_check.py` block D (L6395-6433) pins the bare-word case only.

- **severity: suggestion** · **confidence: 0.7** · `.agents/commands/cicd-quick-dev.md` Step 4 (patch L1249-1264) and `.agents/commands/smh-quick-dev.md` Step 4 (patch L2640-2680) · The machine-read record line "walkthrough approved by the operator @ <sha>" is written by the agent BEFORE the stop that obtains the approval, and the only guard on that phrase whitelists it
  Evidence chain: Step 1 — Step 4 orders: write the walkthrough carrying `Review: none - quick lane; walkthrough approved by the operator @ <sha>` in `## Evidence` (L1249-1255, L2640-2672), THEN "STOP and wait for the literal word `approved`" (L1263-1264, L2779-2780); nothing rewrites the line after the word arrives. Step 2 — both close-outs read that line as the lane's evidence of approval and dereference only the sha (`_QUICK_LANE_RE`, L4600-4603; `closeout_preflight` L3972-3981; `task_preflight.check_gate` L4705-4719). Step 3 — `test_approved_word_is_the_operators.py` block B explicitly asserts "the record line itself does not fire … the writer names the operator, which is the point" (L4797-4799), so the one suite check on granting `approved` deliberately excludes the one place an agent writes the operator's approval into a record before he has given it. Step 4 — the operator answers Step 4 with a correction or silence; the walkthrough already carries a valid-sha approval record that both preflights accept. The close-out invocation is itself a sign-off, which bounds the harm, but the record asserts an event that had not happened when it was written.
  Reproduced or inferred: inferred from the diff's step ordering and the two readers.

- **severity: suggestion** · **confidence: 0.7** · `.agents/commands/smh-non-crit-pr-push.md` hunk `@@ -30,8 +30,8 @@` (patch L2080) with `.agents/scripts/lane_qualify.py` L4267-4268 · `TASK-LIGHT` now routes a small toolkit edit to the FULL lane while citing a right-sizing licence that no door in the diff carries — the quick lane that exists for exactly that work is not offered
  Evidence chain: Step 1 — the table row: "`TASK-LIGHT` | stop. Same road as `TASK` — `/smh-dev-task-tests` — but the measured blast radius is small, so that lane may right-size its ceremony (SCC-302)" (L2080); `lane_qualify.py`'s docstring says the same (L4267-4268). Step 2 — the SOP paragraph that defined the licence ("the plan may be a paragraph and the review fan-out may collapse to one inline pass") is deleted in this diff (L13828-13837), and the renamed full lane `smh-dev-task-tests.md` (L1483-2011) contains no right-sizing clause — its only exemption is the self-audit `Skip` for "a typo, a comment, a one-line doc tweak" (L1749-1750). Step 3 — the same diff defines the quick lane as the home for "a small rule edit" (`AGENTS.md` L10276, `artifacts-always-first.md` L3324, INDEX L50). Step 4 — an operator running `/smh-non-crit-pr-push` on a three-line `.agents/rules/` edit gets `TASK-LIGHT` and is sent to plan + self-audit + RED + mutant sweep + review, while the identical edit typed as `/smh-quick-dev` gets five steps; the row points at a licence that evaporated with the lane it belonged to.
  Reproduced or inferred: inferred from the diff.

- **severity: suggestion** · **confidence: 0.65** · `.agents/scripts/task_preflight.py` `_stale_against_sha` (patch L4636-4637) · In a repo that has product directories, the approval-staleness check is blind to post-approval commits on two of the surfaces the same lane declares critical — `.github/` and root `firebase.json`
  Evidence chain: Step 1 — the pathspec is `PRODUCT_DIRS` present in the repo (`backend/ frontend/ firebase/ functions/ mobile/`), and only falls back to the whole tree when none exist (L4636-4637). Step 2 — the operator approves a quick-lane walkthrough at sha X; the agent then commits `<fixture>/.github/workflows/pr-check.yml` or `firebase.json`. Step 3 — `git diff --name-only X..HEAD -- backend/ frontend/ …` lists neither, so `changed` is empty and no `STALE, re-approve` fires (L4664-4668), while the lane's own line lists both as critical (`GENERIC` L4367, L4379; the lobby map L3129). Step 4 — the walkthrough the operator saw did not contain a CI or deploy-topology change that lands under his approval. Engaging the stated rationale: the comment justifies `PRODUCT_DIRS` over `DEPLOY_DIRS` by SCC-118 (L4628-4635), but that incident was about routing an unshippable repo to the ship door; it says nothing about whether the operator saw a `.github/` edit, which is the only question this helper asks.
  Reproduced or inferred: inferred from the diff.

- **severity: nitpick** · **confidence: 0.7** · `.agents/commands/cicd-prune-worktree.md` hunk `@@ -328,12 +341,22 @@` (patch L711 vs L721-731) · The Step 5 fence comment still says a remote branch exists "i.e. it was PARKED", two paragraphs after the rewritten prose says a landed branch is normally on origin as the PR head
  Evidence chain: Step 1 — new prose: "A landed story branch NORMALLY exists on origin, and deleting it here is the point … the landing itself put it on origin" (L721-726). Step 2 — the unchanged fence comment beneath it: `# Remote FIRST: ONLY if the branch is actually on origin — i.e. it was PARKED.` (L711). Step 3 — the operative condition ("on origin") is still right, so no wrong action follows; the gloss is the retired model's. Cosmetic.
  Reproduced or inferred: inferred from the diff.

### Areas examined with nothing to report
- `epic_mode.py` — classification, `AMBIGUOUS`/`ERROR` exits, `EXIT[word.split(" ",1)[0]]`, origin-only ref read, the `.git`-as-file worktree case, the empty-`--repo` guard, and `uncommented()`'s escape/apostrophe handling all match their docstrings and the pinned cases in `test_epic_mode.py`.
- `scope_check.py` main paths — empty `--paths`, zero-file `--diff`, unparseable map, empty map fallback, absolute-path rebase, the `fragments` off-switch for repo maps, one-line-per-path `break`; `critical-surfaces.md` § The check's exit table and messages match the code.
- `$L` binding — every fence in the diff that uses `$L` binds `L=$(pwd)` in that fence and before any `cd` (all twelve Step 0 mode blocks, boot Step 2b, both quick-dev doors' Steps 0.5/1/5); `test_boot_epic_branch_read.py` A6 and `test_epic_mode.py` F pin it.
- The record-line contract — `_QUICK_LANE_RE` matches both doors' template verbatim and the lenient forms; one regex object is shared by both close-outs (`closeout_preflight` imports from `task_preflight`); `test_closeout_preflight.py` "row 14" binds writer to reader.
- Generated mirrors — all 25 `.opencode/commands/` hunks byte-identical to their `.agents/commands/` sources; `.roo/` rules differ only in hunk offsets; `.sync-manifest.json` and both skill trees add/remove the same two names.
- The `smh-quick-fix` → `smh-quick-dev` → `smh-dev-task-tests` re-pointing sweep across commands, rules, scripts, tests, SOP, quickref and changelog — no live reference left on the retired door, no rename to the wrong successor found.
- `cicd-close-story-merge-tree.md` Arm A/B, the walkthrough-before-PR ordering, the TRUNK merge-sha read, `cicd-push-e2e` AMBIGUOUS wording, `cicd-create-epic-sprint` post-cut assertion — the review rows the diff says it applied are applied and internally consistent.
- The `_bmad/custom/bmad-quick-dev.toml` clause (a) retirement and `000-PLAN-FIRST-GATE` carve-out list — consistent with each other and with `AGENTS.md` and `artifacts-always-first.md`.

**Count: 9 findings — 0 critical, 3 important, 5 suggestion, 1 nitpick.**

## Edge Case Hunter (isolated worktree)

Isolation: toplevel=/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/agent-aff4d76ed7e987b69 HEAD=ffca21c79248f2bd52ad163925562382bf09ac6e

### Findings

- **severity: important** · **confidence: 0.85** · `.agents/scripts/task_preflight.py:1426` · Absorbing `origin/main` after the walkthrough approval — a step this same preflight demands — flips the quick-lane approval STALE
  Evidence chain: Step 1: `/smh-quick-dev` Step 4 records `Review: none - quick lane; walkthrough approved by the operator @ X`; a sibling lane then lands `<fixture>/docs/sibling.md` on `main`. Step 2: `/smh-close-task-merge-tree` runs `task_preflight.py`, whose `check_base` errs `origin/main has 1 commit(s) NOT on chore/… - merge origin/main into this branch first`. Step 3: the agent merges `origin/main` (the preflight's own remedy) and re-runs; `check_gate` finds the record line and calls `_stale_against_sha(rep, repo, rel, X, "approved")`, which runs `git diff --name-only X..HEAD -- :(exclude)_artifacts/ :(exclude)_bmad-output/` — a two-endpoint tree diff, so main's absorbed file is in it. Step 4: `[ERROR] … 1 tracked file(s) … changed since the approved SHA - the approval is STALE, re-approve`, exit 2, while the lane's own merge-base diff vs `origin/main` is unchanged (`walkthrough.md`, `<fixture>/docs/x.md`). Every time `main` moves between approval and close-out the lobby demands a re-approval for work the operator already saw; the author's own `scope_check.py` docstring names the two-dot diff as "the expensive mistake" and uses the merge-base form there. Remedy: measure the lane's own post-approval commits (`git log --first-parent --no-merges --name-only X..HEAD`, or the merge-base diff vs the base taken at X and at HEAD) rather than the tree diff. The project door is not hit on its normal path (its preflight at Step 0.6 runs before Step 3's epic absorb) but a close-out re-run after that absorb takes the same branch (inferred).
  Reproduced: `python3 $TMPDIR/…/repro_stale.py <worktree>` → `F0 control before main moves: exit 0 | STALE? False` · `F1 main moved, NOT absorbed: exit 2 … [ERROR] base: origin/main has 1 commit(s) NOT on chore/SCC-11-thing - merge origin/main into this branch first` · after `git merge --no-edit origin/main` (rc 0): `F2 main ABSORBED after the approval: exit 2 … [INFO ] base: origin/main is fully absorbed … [ERROR] artifacts: …walkthrough.md: 1 tracked file(s) (no product dir here, so all of them) changed since the approved SHA - the approval is STALE, re-approve` · `lane's merge-base diff vs origin/main: ['_artifacts/_main/2026-08-08_scc-11-thing/walkthrough.md', 'docs/x.md']`

- **severity: important** · **confidence: 0.85** · `.agents/scripts/task_preflight.py:1542` · The record line's REQUIRED sha is not enforced in the lobby: an unfilled `@ <sha>` placeholder, or the line copied inside a code fence as the door displays it, reads as "no review Verdict line — the full gate runs" and the lane closes clear
  Evidence chain: Step 1: `smh-quick-dev.md` Step 4 shows the template inside a ``` fence with the literal `@ <sha>`; an agent copies it unfilled, or fenced. Step 2: `check_gate` runs `_QUICK_LANE_RE.search(strip_fenced(text))` — `<sha>` fails `[0-9a-f]{7,40}` and a fenced line is stripped before the search, so `quick` stays empty. Step 3: the `else:` branch prints `[INFO] gate: no review Verdict line in this task's own walkthrough - the full gate runs`; no staleness check, no error. Step 4: `VERDICT: clear to close out and merge`, exit 0, after a post-approval tracked-file commit — the exact case row 13 was written to close, reached by the likeliest copy mistake. The author says "The sha is REQUIRED: without it the line is a sentence, not a record", and pinned a `NEAR_MISS_LINE` guard for typo'd `Verdict:` stamps, but no near-miss guard exists for the record line. (`closeout_preflight.py:357` searches the raw, un-stripped text, so the two readers also disagree on a fenced line: the project accepts it, the lobby ignores it.)
  Reproduced: `repro_stale.py` → `G1 record line with literal `@ <sha>`: exit 0 … [INFO ] gate: no review Verdict line in this task's own walkthrough - the full gate runs … VERDICT: clear to close out and merge`; `repro_fenced.py` → `G2 fenced record line + a post-approval commit: exit 0 … [INFO ] gate: no review Verdict line … VERDICT: ['VERDICT: clear to close out and merge']`

- **severity: important** · **confidence: 0.85** · `.agents/scripts/scope_check.py:172` · The Step 5 tripwire reads the surfaces map from the LANE's own tree, so a lane that prunes the map's self-protecting rows reads CLEAR on the real diff — the "line that can widen itself" is enforced by a row the lane can delete
  Evidence chain: Step 1: both doors run the tripwire as `scope_check.py --repo "<the tree>" --diff <base>` (`cicd-quick-dev.md:405-406`, `smh-quick-dev.md:321`). Step 2: `main()` → `load_map(repo)` reads `<the tree>/.agents/critical-surfaces.json` at the lane's HEAD; with `rows` non-empty, `fragments=False` and only the lane's rows are consulted. Step 3: a lane commit that rewrites the map to drop `.agents/critical-surfaces.json`, `scope_check.py`, the rule and `gates/` (leaving one row, e.g. `.github/`) and edits `<fixture>/gates/x.sh` → `diff_paths` returns both files, `overlaps` matches neither. Step 4: prints `CLEAR` / `DIFF: 2 file(s) vs main`, exit 0; the same two paths against the base's map are `OVERLAP` under `ci`. `critical-surfaces.md` § The map claims the three self rows make this impossible; the GENERIC self-protection (row 21) is bypassed because a map with ≥1 row suppresses the generic set. Remedy: on `--diff`, read the map from the merge-base (`git show <fork>:.agents/critical-surfaces.json`) — or union base and HEAD maps.
  Reproduced: `repro_scope.py` → `C1 lane pruned the map's self rows + gates/ and edited gates/x.sh; --diff main -> (0, 'CLEAR\nDIFF: 2 file(s) vs main')` · `C2 control: --paths on the SAME two files against the base's map -> (3, 'OVERLAP\n.agents/critical-surfaces.json  ci: gates\ngates/x.sh  ci: gates')`

- **severity: important** · **confidence: 0.9** · `.agents/scripts/scope_check.py:146` · A directory entry without its trailing `/`, or an exact-file entry naming a file that does not exist, is a silently dead map row — the root-file guard covers only bare words
  Evidence chain: Step 1: a map author writes `"paths": ["backend/auth"]` (the rule says a directory needs `/`; forgetting it is the natural slip) or a typo'd exact path `<fixture>/backend/app/auth/tokens.py`. Step 2: `load_map` runs the existence check only when `"/" not in pat and "." not in pat`, so both entries skip it and are stored as exact-file patterns. Step 3: `pattern_hit("backend/auth/token.py", "backend/auth")` → not a prefix (no trailing `/`), not `*.`, fragments off → `path == pattern` False. Step 4: `CLEAR`, exit 0 for a file inside the declared auth directory — "a dead entry the author believes is protecting something", the class row 6 fixed for bare words, one level deeper. Remedy: for a slashed pattern with no trailing `/`, ERROR when `(repo / pat).is_dir()`, and when it names no tracked file.
  Reproduced: `repro_scope.py` → `A1 dir-without-slash + nonexistent exact file, --paths backend/auth/token.py -> (0, 'CLEAR')` · `A2 control: same map with trailing slash -> (3, 'OVERLAP\nbackend/auth/token.py  auth: auth')`

- **severity: important** · **confidence: 0.75** · `.agents/scripts/scope_check.py:230` · A lobby-relative path (`<fixture>/Projects/X/backend/auth.py`, the spelling a lobby session displays) or a `..`-relative path is compared as a string and answers CLEAR in a mapped repo; only absolute paths are rebased
  Evidence chain: Step 1: `cicd-quick-dev.md:238` runs Step 1 from the lobby (`cd "$L" && … --repo "$PROJECT_ROOT" --paths <the planned set>`); the agent standing in the lobby names the file as `<fixture>/Projects/X/backend/auth.py` (how `git status` in the lobby spells it). Step 2: `norm()` keeps it; `Path(p).is_absolute()` is False, so no `relative_to(repo)` rebase. Step 3: `overlaps` compares `<fixture>/Projects/X/backend/auth.py` to the map's `<fixture>/backend/auth.py` → no hit. Step 4: `CLEAR`, exit 0 exactly where the map is the authority — the sibling of row 3 (absolute paths), which the author fixed. Remedy: when `p` does not exist under `repo` but `(Path.cwd()/p).resolve()` lies inside `repo`, rebase it; a path outside stays ERROR.
  Reproduced: `repro_scope.py` (cwd = the lobby dir) → `B1 --paths Projects/X/backend/auth.py (lobby-relative) -> (0, 'CLEAR')` · `B2 control: repo-relative backend/auth.py -> (3, 'OVERLAP\nbackend/auth.py  auth: auth')` · `B3 control: absolute path -> (3, 'OVERLAP …')` · `B4 ..-relative path from inside a worktree dir -> (0, 'CLEAR')`

- **severity: suggestion** · **confidence: 0.7** · `.agents/scripts/scope_check.py:98` · A planned set declared at directory granularity (`backend/`, `.`) is CLEAR over a critical child, so Step 1 passes a plan that Step 5 will eject after the build
  Evidence chain: Step 1: the agent names `backend/` as the planned set. Step 2: `pattern_hit("backend/", "backend/auth/")` → `"backend/".startswith("backend/auth/")` False; `"." == pattern` False. Step 3: `CLEAR` at Step 1; the build touches `<fixture>/backend/auth/t.py`. Step 4: the Step 5 `--diff` ejects the lane to ①②③ after the work is done — the soft stop the lane exists for fires only post-build. Remedy: treat a planned path that is a directory as its own prefix (or ERROR "name files, not directories").
  Reproduced: `repro_scope.py` → `D1 --paths backend/ -> (0, 'CLEAR')` · `D2 --paths . -> (0, 'CLEAR')` · `D3 control --paths backend/auth/t.py -> (3, 'OVERLAP …')`

- **severity: suggestion** · **confidence: 0.7** · `.agents/commands/cicd-write-story-tests.md:27-28` (the same Step 0 fence in all twelve doors) · The fetch and the mode query are two independent lines, so a failed `git fetch origin --prune` leaves stale remote-tracking refs and `epic_mode.py` prints `FULL <epic that no longer exists on origin>` with exit 0
  Evidence chain: Step 1: the epic ships and `/cicd-push-e2e --after-merge` deletes it on origin (or another machine does). Step 2: on this machine the door's line 2 fetch fails (proxy, VPN, sandbox — all measured in this house) and prints `fatal:`; line 3 runs regardless because the lines are not chained. Step 3: `live_epics` reads `refs/remotes/origin/epic/*`, which still holds the cached ref; `classify` returns `FULL epic/…`. Step 4: `cicd-write-story-tests` Step 0.5 cuts a story worktree off a dead `origin/epic/…` and the close-out's `gh pr create --base epic/…` fails at GitHub; the door text names `AMBIGUOUS` and `ERROR` as stops but says nothing about a failed fetch. Remedy: chain them (`… git fetch origin --prune && cd "$L" && python3 … epic_mode.py …`) or add "a failed fetch is a STOP; the mode line is stale" beside the fence.
  Reproduced: `repro_git.py` → `I0 origin now has: ['main']` · `I1 fetch --prune rc 128 | fatal: '…/nowhere.git' does not appear to be a git repository` · `I2 epic_mode after the failed fetch: rc 0 | ['FULL epic/SCC-1-epic-2-x']` · `I3 control after a good fetch --prune: rc 0 | ['TRUNK']`

- **severity: nitpick** · **confidence: 0.9** · `.agents/commands/cicd-quick-dev.md:103` and `.agents/commands/smh-quick-dev.md:117` · `git branch --unset-upstream` right after `git worktree add --no-track …` always exits 128 `fatal: branch '…' has no upstream information` — a `fatal:` line inside the door's own fence
  Evidence chain: Step 1: the fence cuts the lane with `--no-track` (added by this diff) so no upstream is ever set. Step 2: the next line, kept from the pre-`--no-track` shape, runs `git branch --unset-upstream`. Step 3: git refuses with exit 128 because there is nothing to unset. Step 4: an agent reading exit codes (as `command-shape.md` tells it to) meets a `fatal:` on a line labelled "belt and braces"; no functional harm since each line is its own compound command. Remedy: drop the line, or make it `git branch --unset-upstream 2>/dev/null || true`.
  Reproduced: `repro_git.py` → `H1 worktree add --no-track rc 0` · `H2 git branch --unset-upstream rc 128 | fatal: branch 'chore/SCC-1-x' has no upstream information`

- **severity: nitpick** · **confidence: 0.7** · `.agents/commands/smh-quick-dev.md:160` · The Step 1 fence binds `$L` "in THIS fence: a fence is its own shell, nothing an earlier one set survives" and on the same line passes `--repo "$REPO"`, bound only in the Step 0 fence; run literally the fence gives `scope_check.py --repo ""` → `ERROR --repo was empty`
  Evidence chain: Step 1: Step 0's fence sets `REPO=$(cd … && git rev-parse --show-toplevel)`. Step 2: the Step 1 fence is a fresh shell; `$REPO` is empty. Step 3: `scope_check.py` refuses (`ERROR / --repo was empty - an unbound $REPO …`), so the failure is loud, not silent. Step 4: the house treats `$REPO` as a fill (32 cross-fence uses in 11 doors, measured with a fence audit), so this is a self-contradicting comment rather than a dead gate; the `$L` audit found 0 unbound uses.
  Inferred: fence audit script over `.agents/commands/*.md` → `unbound-in-fence counts: {'PROJECT_ROOT': 47, 'WORKTREE': 1, 'EPIC': 1, 'REPO': 32, 'TREE': 2}` (no `L` row); `scope_check.py --repo ""` refusal is pinned by `test_scope_check.py` block D and passed in my run (106/106).

### Areas examined with nothing to report
- `epic_mode.py` classification and `uncommented()` — walked TRUNK/FULL/LIGHT/AMBIGUOUS, empty/whitespace `--repo`, linked-worktree `.git` file, `-light-epic-` in the slug vs the key, `#` inside single/double quotes, backslash escape, unmatched apostrophe, `.yaml` spelling; `python3 .agents/scripts/tests/test_epic_mode.py` → 34/34.
- `scope_check.py` refusals — empty `--paths`, whitespace paths, unparsable/wrong-shape/`null`/all-empty maps, absolute path outside the repo, zero-file `--diff`, unresolvable base, unrelated histories (merge-base fails → ERROR), bypass flags refused by argparse; `test_scope_check.py` → 106/106.
- `_stale_against_sha` on the project arm — verdict WARN vs approval ERROR asymmetry, PRODUCT_DIRS derivation, `_bmad-output/` exclusion, uncommitted edits caught by the sync arm; `test_closeout_preflight.py` → 126/126, `test_task_preflight.py` → 124/124.
- Fence `$L` binding across every door — my own audit and `test_boot_epic_branch_read.py` A6 (51/51) agree: every fenced `$L` is bound in its fence; every `epic_mode.py` call is `cd "$L" && …` with `L=$(pwd)` earlier in the same fence.
- `.opencode/commands` mirrors — bodies after frontmatter byte-identical to `.agents/commands` for all 15 changed doors; no `smh-quick-fix` launcher left on any platform (`ech_mirrors.py`); `test_command_surfaces.py` 343/343, `test_twin_parity.py` 68/68.
- `cicd-close-story-merge-tree` Arm B — the `--after-merge` re-invocation it cites exists (`grep -n after-merge` → lines 226, 347, 417), so the TRUNK merge-sha read has a defined moment; `test_trunk_mode.py` 37/37.
- Circular import `closeout_preflight` ↔ `task_preflight` — one direction only (`grep` finds no import of closeout from task_preflight); both suites import cleanly.
- Record-line writer/reader parity — the doors' template line with a 40-hex sha is accepted by both readers (block "row 14"); `test_approved_word_is_the_operators.py` 122/122; `test_declared_change_set.py` 59/59; `test_doc_examples_parse.py` 22/22; `test_review_engine.py` 867/867.
- `docs/doc-graph.*` regeneration is not a hidden post-approval commit in the lobby: `refresh_maps.triggered()` regenerates the doc graph only for `.md` under `.agents`/`docs`, and `_artifacts` is in the repo-map's `DEFAULT_IGNORES`, so a walkthrough commit leaves both maps untouched.
- Records under `_artifacts/_main/2026-09-10_…` (plan, parts, tickets, review-lenses, receipts) and the SOP/quickref/changelog prose — read for machine-read contracts; the only executable content is three bash fences in the plan, none new in shape.

**Count: 9 findings — 0 critical, 5 important, 2 suggestion, 2 nitpick.**

Tree left clean: clean (only the six `?? .claude/*` sandbox bind-mount rows, which `git status --short | grep -v '^?? .claude/'` filters to nothing)

## Literal-Correctness Hunter (isolated worktree, 20-file cap, one top-up taken)

I received 20 of the diff's 152 files (the `.sync-manifest.json`, commands `INDEX.md`, and the 18 `cicd-*`/`smh-*` command documents listed in my brief); 132 files were withheld, including every script, rule, skill, generated door and artifact the slice's fences and prose lean on. I took the one top-up on `.agents/scripts/closeout_preflight.py`, to verify that the `Review: none - quick lane; …` record line `cicd-quick-dev.md` Step 4 tells the agent to write is what the close-out preflight actually reads (it is — quoted below). Every other withheld script was verified by executing it (`--help`, and real runs against a synthetic repo under the scratchpad), never by opening it.
Isolation: toplevel=/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/agent-a62ee26c2c510809b HEAD=ffca21c79248f2bd52ad163925562382bf09ac6e

### Findings
- **severity: important** · **confidence: 0.9** · `.agents/commands/cicd-quick-dev.md:103` · Step 0.5 fence keeps `git branch --unset-upstream` after every worktree add was switched to `--no-track`, so that line now dies `fatal:` on all three lane variants
  Assumption on the changed line: line 103 (`cd "$PROJECT_ROOT"/.claude/worktrees/<slug> && git branch --unset-upstream   # belt and braces: no upstream until the lane's own first push`) assumes the branch the preceding line created has an upstream to unset. · The definition I opened and what it actually says: `git worktree add -h` → `--[no-]track  set up tracking mode (see git-branch(1))`; with `--no-track` no upstream is written, and `git branch --unset-upstream` on such a branch exits 128 with `fatal: branch '<name>' has no upstream information`. The diff's own twin says the two are alternatives: `cicd-write-story-tests.md:62` (this diff) reads "spends a second line on `git branch --unset-upstream`; one flag here cannot be forgotten" — i.e. `--no-track` *replaces* the unset line, it does not precede it. · Evidence chain: Step 1: an agent runs the Step 0.5 fence and picks any of lines 98/100/102 (story FULL/LIGHT, story TRUNK, ad-hoc chore) — all three now carry `--no-track`. Step 2: the branch is created with no upstream (git prints only `Preparing worktree (new branch …)`, no `set up to track` line). Step 3: line 103 runs `git branch --unset-upstream` in that tree and git returns rc 128, `fatal: branch 'claude/…' has no upstream information`. Step 4: the fence reports a `fatal:` on every quick-lane open; an agent that treats a fence fatal as a STOP (house convention) halts before `link-worktree-assets.py` and the `Lane:` echo on line 104–106, and a `set -e` runner (the headless autopilot child on the quick-fix route this diff rewires, `cicd-autopilot-claude.md` stage 1) aborts the step. The author's stated rationale ("belt and braces") is rebutted by the reproduction: it is not a harmless double-check, it is a guaranteed non-zero exit. · Reproduced: in a scratch clone, `git worktree add --no-track .claude/worktrees/wt1 -b claude/AVCH-41-wt1 origin/epic/AVCH-40-epic-41-wt` → rc 0; then `git branch --unset-upstream` in that tree → `rc=128  err="fatal: branch 'claude/AVCH-41-wt1' has no upstream information"`. Control: the same add *without* `--no-track` prints `branch 'claude/AVCH-41-wt2' set up to track 'origin/epic/…'` and the subsequent `--unset-upstream` → rc 0. Fix is the one the twin already made: delete line 103 (or drop `--no-track` — not both).

- **severity: nitpick** · **confidence: 0.9** · `.agents/commands/smh-dev-task-tests.md:514` · "the `task.yaml` you wrote in Step 0" points at a step that writes no `task.yaml`
  Assumption on the changed line: Step 5's Dev Record note says the slug "is read from the `task.yaml` you wrote in Step 0". · The definition I opened and what it actually says: the same door's own sections — `task.yaml` appears at line 491 ("**The manifest** — `task.yaml` beside it", inside `## Step 5`, line 461) and nowhere in `## Step 0` (line 44) or `## Step 0.5` (line 95). `jira_feed.py devrecord --help`: `--story … defaults to the branch slug in this lane's task.yaml (SCC-174)`. · Evidence chain: Step 1: an agent reaches the Step 5 devrecord fence (line ~502) and reads line 514. Step 2: it goes looking for a Step-0 `task.yaml`; none was ever specified there. Step 3: the file it needs is the one written eleven lines earlier in the same step, so the outcome is a wrong cross-reference, not a runtime failure (`devrecord` still finds the manifest if Step 5's order was followed). Step 4: doc-only defect; "Step 0" should read "Step 5, above". · Inferred (from the door's own headings; no execution needed).

### Walked and clean
- `.agents/.sync-manifest.json` — `smh-dev-task-tests` added / `smh-quick-fix` removed in both lists matches disk: `.agents/commands|.opencode/commands|.roo/commands/smh-dev-task-tests.md` and `.agents/skills|.claude/skills/smh-dev-task-tests/SKILL.md` exist; all four `smh-quick-fix` doors that exist on `origin/main` (`.agents/commands`, `.agents/skills`, `.claude/skills`, `.opencode/commands`) are gone at HEAD and no `.roo` door ever existed; `workflow_lint.py --toolkit-only` on my copy → `0 error(s), 0 warning(s)`.
- `.agents/commands/INDEX.md` — `scope_check.py`, `.agents/critical-surfaces.json`, `.agents/rules/critical-surfaces.md`, `smh-dev-task-tests.md`, `smh-quick-dev.md` all exist; the `Review: none - quick lane; …` prefix matches the door text. Not verifiable inside the cap: "`lane_qualify.py` stays only for the standing-push doors" — `grep -l lane_qualify .agents/commands/*.md` also lists `smh-quick-dev.md` and `smh-llm-approvals.md`, both withheld, so I could not read whether those mentions are retirement notes or live calls.
- `cicd-autopilot-claude.md` — `Step 2.5` exists (`### Step 2.5 — What an escalation looks like`, line 210); the record line string is byte-identical to `cicd-quick-dev.md` Step 4's. The "batch approval scoped to this ticket, `000-PLAN-FIRST-GATE`" claim leans on a withheld rule and is unverified.
- `cicd-boot-sprint-memory.md` — both new fences: `L=$(pwd)` bound in-fence before use; `epic_mode.py --repo` is its only flag (`--help`); executed against a synthetic repo it prints exactly two lines — `TRUNK` / `FULL <branch>` / `LIGHT <branch>` then a cost line — and `AMBIGUOUS` (rc 2) with the candidate list when two `origin/epic/*` exist; a local-only `epic/*` branch is ignored ("reads origin only" holds); `git show origin/epic/…` on TRUNK is guarded by the following prose.
- `cicd-clean-code-audit.md` — `BASE=<…>` is a fill; `git diff --name-only "${BASE}...HEAD"` binds it in-fence.
- `cicd-close-story-merge-tree.md` — `--after-merge <JIRA-KEY>` re-entry for Arm B exists (line 347); Step 4 (Dev Record, line 390), Step 5 (prune, 519) and Step 1's `## Your Actions` row exist; `gh pr checks --watch` and `gh pr merge --merge` are real flags; `jira_feed.py devrecord` accepts `--key --story --project --outcome --decision --pitfall --followon --evidence --closing --apply`; `jira_feed.py finish` has `--landing-ref` (ancestry-computed, as the prose claims). The `⛔ NOT ARMED HERE` caveat is real: reproduced on a LIGHT branch in a repo with no `.github/workflows/` reading `-light-epic-`.
- `cicd-code-review.md` — `EPIC=main` in TRUNK makes `git fetch origin "$EPIC"` / `origin/$EPIC...HEAD` resolve to production as stated.
- `cicd-create-epic-sprint.md` — Step 3 is the sprint-board step (line 216); "unanchored substring" reproduced: `epic/AVCH-22-epic-23-fix-light-epic-banner` → `LIGHT`; the two fast check names `Backend (Python)`, `Frontend (Node.js)` match both `epic_mode.py`'s cost line and AviationChat's `pr-check.yml` job names (lines 74, 233).
- `cicd-dev-story-tests.md` — new Step 0 fence as above; `/smh-dev-task-tests` exists; Step 3.5 heading exists.
- `cicd-e2e.md` — Step 0/1/3 references resolve; no fence changes beyond the shared Step 0 block.
- `cicd-merge-epic-workingtrees.md` — Steps 4.5, 6, 7 exist (lines 228/350/364); fence flags real (`gh pr create --base/--head/--fill`, `gh pr checks --watch`, `gh pr merge --merge`).
- `cicd-prune-worktree.md` — Step 2 does `git push -u origin claude/…` (line 226) as the new Step 5 text claims; the `ls-remote` "above" is at line 363; Steps 1.6/1.7 exist; `merge-base --is-ancestor … origin/main` on TRUNK is a valid ref.
- `cicd-push-e2e.md` — Step 1.5 (line 102), Step 3 item 4 (line 137), Step 3.5 (line 144) exist; `AMBIGUOUS` output lists the candidates the new bullet says to show.
- `cicd-quick-dev.md` (everything except line 103) — Step 0.7 heading exists (line 201) and Steps 1–5/4.5 exist; `scope_check.py` has `--repo` + mutually exclusive `--paths|--diff` and, executed, prints `CLEAR`/`OVERLAP`/`ERROR` as line 1, `MAP: none for <repo> - generic surfaces only` when no map, `DIFF: <n> file(s) vs <base>` on `--diff`, overlap rows as `<path>  <surface>: <why>`, and `ERROR … no paths given` on an empty set; `story_status.py set <id> <status> --project` exists; `jira_feed.py check-actions --walkthrough` exists; `check_links.py --repo` exists; AviationChat's `_artifacts/AGENTS.md` exists and its `.agents/critical-surfaces.json` does not (matches "AVCH-152 lands AviationChat's"); the record line matches `task_preflight._QUICK_LANE_RE` (executed: `^[>\-*\s]*\**\s*Review:\**\s*none\s*[-—–]\s*quick lane;\s*walkthrough approved by the operator\s*@\s*`?([0-9a-f]{7,40})` captures a 7–40 hex sha), and `closeout_preflight.py:357-370` (top-up) does what Step 4 claims — no `Verdict:` + a matching line → `rep.info(… "no `Verdict:` line - quick lane, no review was asked for …")` plus a staleness check on the sha; neither line → `rep.err("… the review step has not run …")`; the regex is imported from `task_preflight`, so the chore-lane door shares the reader.
- `cicd-resume.md`, `cicd-write-story-tests.md` — shared Step 0 fence as above; `git worktree add --no-track` is a real flag and the write-story fences correctly carry no `--unset-upstream` line.
- `smh-close-task-merge-tree.md`, `smh-code-review.md`, `smh-designer.md` — every renamed reference (`/smh-dev-task-tests`, `/smh-quick-dev`) resolves to a door on disk; `smh-dev-task-tests.md` Step 1 does echo the list and Step 3 does stamp `gate_receipt.py run --task … --gate suite --root … --cwd …` (all real flags; `--task` is an alias of `--story`).
- `smh-dev-task-tests.md` (everything except line 514) — Step headings 0/0.5/1/1.5/1.6/2/3/3.5/4/5 all exist and every internal step pointer lands; `jira_feed.py start --key --apply`, `index-row`, `devrecord --stage/--verdict/--walkthrough/--apply`, `mutation_sweep.py --table`, `declared_change_set.py parse`, `link-worktree-assets.py <worktree>` all exist; the tracking `worktree add … origin/main` followed by `--unset-upstream` works (reproduced rc 0).
- `check_links.py --paths <all 19 .md in the slice>` → `142 path claim(s) checked … clean`.

**Count: 2 findings — 0 critical, 1 important, 0 suggestion, 1 nitpick.**
Tree left clean: `?? .claude/agents .claude/commands .claude/hooks .claude/launch.json .claude/loop.md .claude/routines .claude/scheduled_tasks.json .claude/workflows` (the sandbox bind-mount rows, present before my first command — no file of mine touched the copy; all scratch lives under the scratchpad)

## Acceptance Auditor (isolated worktree, review_mode: full)

Isolation: toplevel=/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/agent-a266bab402b1eb5e7 HEAD=ffca21c79248f2bd52ad163925562382bf09ac6e

### Coverage — every acceptance row
| Row (plan or part · letter) | State (satisfied / NOT satisfied / diverges / deferred-by-design) | Proving assertion or command + output |
|---|---|---|
| Plan · A (Part A's six rows green) | satisfied | see A·A–A·F below; `test_trunk_mode.py` 37/37 |
| Plan · B (Part B's six rows green) | satisfied | see B·A–B·F; `test_scope_check.py` 106/106 |
| Plan · C (Part C's eight rows green) | satisfied (one literal count diverges, C·C) | see C·A–C·H |
| Plan · D (Part D's six rows green) | satisfied in substance; three literal checks diverge (D·A, D·B, D·C) | see D·A–D·F |
| Plan · E (Part E's seven rows green) | satisfied (one literal count diverges, E·C) | see E·A–E·G |
| Plan · G (every commit leads with its part's key; each rider named) | satisfied | `git log --format=%s origin/main..HEAD` → 31 subjects, all begin `SCC-44x`; riders: SCC-442 ×1, SCC-443 ×1, SCC-444 ×3, SCC-445 ×1, SCC-446 ×1; `task.yaml` `riders: [SCC-442..446]`, `landing_mode: partial`; `task_preflight.py` RIDERS_RE reads that line (`:315`) |
| Plan · H (one gate at the tip; one review; riders flip, parent stays open) | deferred-by-design (close-out not run) — gate half holds, review half pending | `<fixture>/gates/suite.json`: `result: pass`, `sha: fb2639ac` = HEAD~1; HEAD `ffca21c7` touches only 4 artifact files (`git show --name-only`); `run_all.py` re-run in my copy → `87/87 files passed`, exit 0. The walkthrough's last `## Code Review` is `Verdict: FAIL @ dd5a5c42` with all 30 rows marked applied — the re-review stamp is this run's output. `preflight-receipt.json` still names `verdict_sha: 46bc4267` (the retracted stamp; review row 30, "done at the tip") |
| Plan · F (the closure lane after AVCH-152) | deferred-by-design | `declared_change_set.py diff` → `unimplemented: [.agents/commands/smh-new-project.md, docs/_scc_sops_prds/tea_testing_guide.md]` — exactly the two Part F bullets |
| A · A (FULL/LIGHT/TRUNK, both shapes, token in the switch fence, quickdev gone) | satisfied | `test_trunk_mode.py` block A 37/37; `grep -c quickdev .agents/rules/*.md` → every file 0; `grep -rn quickdev .agents/rules AGENTS.md` → empty |
| A · B (quick lane + rails once in git-policy; worktree rule points at them) | satisfied | `grep -n "Two toggles"` → `git-policy.md:167` (H2 with the five-step table and the six-rail table) and `worktree-per-story.md:73` (cites it) |
| A · C (constitution, AGENTS GATES, rules INDEX say full/light + PR; living-template-sync `.github` row, lists match) | satisfied | `constitution.md:23` "full `epic/<KEY>-epic-<N>-<slug>` or light `epic/<KEY>-light-epic-<N>-<slug>` … Landing on the epic branch, by pull request"; `AGENTS.md:151-154, 167-171` "full or light, read by the git query … by a pull request into it"; `rules/INDEX.md:50,51`; `living-template-sync.md:5,10` both lists carry `".github/**"`, row at `:36`; `test_rule_frontmatter.py` 30/30 |
| A · D (landing is the PR road; no `HEAD:epic/` fence in git-policy) | satisfied | `grep -n 'HEAD:epic/' .agents/rules/git-policy.md` → no output; landing fence `:430-436` is push-branch / `gh pr create --base epic/` / `gh pr checks` / `gh pr merge`; `test_trunk_mode` "no fence pushes HEAD:epic/" green |
| A · E (RED then GREEN; run_all, lint, maps clean) | satisfied | RED is the walkthrough's record (24/30 → 30/30; not re-seeable); at HEAD: `run_all.py` 87/87 exit 0; `workflow_lint.py --toolkit-only` `0 error(s), 0 warning(s), 8 info`; `check_maps.py --depth3-only --strict` no output, exit 0 |
| A · F (SOP block + changelog same commit; `.roo` constitution regenerated) | satisfied (mechanism note) | `git show --name-only 17546e8c` → 14 files incl. `workflows_testing_SOP.md` + `_changelog.md`; `.roo/rules/constitution.md` body == master body (my difflib compare: ok). Regenerated by a Python mimic, not `/smh-sync-agents` (walkthrough: "Not run") |
| B · A (rule lists five surfaces + map format; lobby map names gates, says which don't apply) | satisfied | `test_scope_check.py` block A green; `json.load('.agents/critical-surfaces.json')` → keys `['answers','auth','billing','ci','rules']`, four with `"paths": []` and a `why` |
| B · B (CLEAR/OVERLAP line 1, exits 0/3, empty → 2, merge-base diff, never prompts) | satisfied | `scope_check.py --repo <copy> --paths .agents/hooks/shape-guard.py docs/x.md` → `OVERLAP` + one `ci:` line, exit 3; `--paths` (empty) → `ERROR`, exit 2; `--diff origin/main` → `OVERLAP`, `DIFF: 152 file(s) vs origin/main`, exit 3; `grep -c "input(" scope_check.py` → 0; merge-base pinned by block E (`main` moved after the fork → still CLEAR) |
| B · C (repo map overrides generic; missing map is loud) | satisfied | block B "a repo map WINS" + "SAME path is OVERLAP in an unmapped repo"; block C `MAP: none` + `.github/` still overlaps — 106/106 |
| B · D (RED then GREEN; `run_all.py` 85/85) | diverges (count moved) | `run_all.py` → **87/87** at HEAD (85 was Part B's tip; `test_epic_mode.py` and `test_approved_word_is_the_operators.py` joined) |
| B · E (both INDEX rows; maps strict clean; rule frontmatter green) | satisfied | `.agents/scripts/INDEX.md:30` row + `:79` paragraph; `.agents/rules/INDEX.md:56` on-demand row; `check_maps` clean; `test_rule_frontmatter` 30/30; `test_scope_check` block H |
| B · F (SOP row + changelog same commit) | satisfied | `git show --name-only 2d57ba27` → 10 files incl. both SOP files |
| C · A (Steps 0, 0.5, 0.7, 1, 2, 3, 4, 4.5, 5; both `approved` stops; no review gate, no engine, no one-shot) | satisfied | headings at `cicd-quick-dev.md:44/64/201/230/263/297/324/360/398`; `grep -c code-review-engine` → 0; `grep -n bmad-quick-dev` → none; `test_review_engine.py` 867/867 (`CALLER_FILES = (CICD_CMD, SMH_CMD)`); `test_command_surfaces.py` 343/343 |
| C · B (Step 2 writes a plan with `## Declared Change Set`; door is an emitter) | satisfied | `cicd-quick-dev.md:283` heading in the Step 2 template; `test_declared_change_set.py` S7 59/59 (`"## Declared Change Set" in quick and "RE-ARMS the plan-first gate" in quick and "plan-exempt lane" not in quick`) |
| C · C (`scope_check.py` at Steps 1 and 5; only the operator's quoted words override; never proposes a light epic) | satisfied; literal diverges | `grep -c "scope_check.py" cicd-quick-dev.md` → **4** (plan said 2): `:13` prose, `:238` `--paths`, `:405/:406` two `--diff` arms; `grep -c light-epic` → **0**; `grep -rn -i 'cut a light\|switch to light' .agents/commands` → none; `:1028` "This step never proposes a lighter road" |
| C · D (Step 3 RED then GREEN; twin fence byte-identical; directive line) | satisfied | `cicd-quick-dev.md:297` "RED, then GREEN"; `test_twin_parity.py` 68/68; `test_directive_quote.py` 32/32 |
| C · E (walkthrough with the `Review: none …` line and no `Verdict:` passes; neither still errs) | satisfied | `closeout_preflight.py:357-366` reads `_QUICK_LANE_RE` → INFO + `_stale_against_sha`; `test_closeout_preflight.py` QL1 (no error), QL3 CONTROL (neither → error stands), QL4 (no sha → error) — 126/126 |
| C · F (guard toml no longer names the door; zoo-team and AGENTS.md:86-87 updated) | satisfied | `bmad-quick-dev.toml:35-46` "There is exactly ONE way … No house door launches this skill", `TOKEN-SIZE GATE RETIRED` kept (`:60`); `zoo-team.md:46-53` "a review runs only when the operator asks"; `AGENTS.md:86-89` skip list names `/smh-llm-approvals` only; `test_zoo_team.py` 33/33, `test_bmad_token_gate_retired.py` 16/16 |
| C · G (autopilot requests the review at stage 2; reads no door verdict) | satisfied | `grep -c "first-pass gate" cicd-autopilot-claude.md` → 0; `:83-89` "The quick lane produces no verdict; stage 2 does"; `test_approved_word_is_the_operators.py` 122/122 |
| C · H (SOP §8, lane table, stop-points, atlas, quickref, changelog same commit; gates clean) | satisfied | `git show --name-only 5aa18f0c` → 22 files incl. both SOP files, quickref, autopilot_SOP; SOP `§8` at `:1667` is the five-step table, lane table `:389-395`, stop-points `:3997`, atlas `:4034`; gates as A·E |
| D · A (`smh-dev-task-tests.md` is old `smh-quick-dev.md`; rename with ≤ 6 changed lines) | diverges | `git diff -M --stat origin/main...HEAD -- .agents/commands/smh-dev-task-tests.md` → `529 insertions(+)` (an add, no rename pairing); difflib vs `origin/main:smh-quick-dev.md` → **5 changed line pairs (10 unified lines)**: description, title, flow line, and TWO lines of the intro paragraph (`/cicd-quick-dev is the fast lane and is still story-shaped` → `/cicd-quick-dev and /smh-quick-dev are the quick lane…`) — a fourth change the plan did not name |
| D · B (five-step quick lane; quick-fix gone; INDEX pointer) | satisfied; literal diverges | `grep -c "scope_check.py" smh-quick-dev.md` → **3** (plan said 2): `:14` prose, `:160` `--paths`, `:321` `--diff origin/main`; `test ! -e .agents/commands/smh-quick-fix.md` → absent; `commands/INDEX.md:58` carries the retired pointer |
| D · C (no live `smh-quick-fix` reference outside history) | diverges | `grep -rn smh-quick-fix .agents AGENTS.md docs --include=*.md --include=*.py --include=*.sh` → 9 hits: 2 changelog rows + **7 retirement notices** (`commands/INDEX.md:58`, `smh-quick-dev.md:182`, `artifacts-always-first.md:323`, SOP `:2157`, `scripts/INDEX.md:75`, `test_lane_qualify.py:278`, `test_sops_prds_folder.py:166`). None invokes the door; the literal "only changelog rows" does not hold |
| D · D (launchers on every platform; quick-fix absent; manifest updated) | satisfied (mechanism note) | `ls` → `smh-dev-task-tests` present in `.agents/skills`, `.claude/skills`, `.roo/commands`, `.opencode/commands`; `smh-quick-fix` absent from all four; `.sync-manifest.json:62,123` added, quick-fix rows gone; `test_command_surfaces.py` 343/343; `test_settings_allowlist.py` 28/28; 24 changed `.opencode` mirrors body-identical to masters, 8 skill pairs identical (my script). Regenerated by a mimic, not the ps1 |
| D · E (the pinned tests move in the same commit; gates clean) | satisfied | `git show --name-only 49dc82ed` → 76 files incl. 16 test files (the plan's 15 + `test_sops_prds_folder.py`); `run_all.py` 87/87; `check_maps` clean; `check_links.py --base origin/main` → `clean`, exit 0 |
| D · F (SOP §9 + quick-lane section, quickref, § When to Skip, changelog same commit) | satisfied | 49dc82ed carries both SOP files; SOP `:2212` `### /smh-dev-task-tests`, `:2129` `### The quick lane — /smh-quick-dev` (five-step table); `artifacts-always-first.md:316-354`; changelog `:26` |
| E · A (`epic_mode.py` word + cost; AMBIGUOUS exit 2; local-only head not a mode) | satisfied | `test_epic_mode.py` 34/34 (A local-only head → still TRUNK; D AMBIGUOUS exit 2 with refs; C `light` in slug is FULL); live: `epic_mode.py --repo <copy>` → `TRUNK` / `lands on main by a PR the operator merges…`, exit 0. (`Projects/AGY_AVIATIONCHAT` is not checked out in a lens worktree → `ERROR … not a git repository`, the script's correct answer for a non-repo; the walkthrough's live TRUNK reading there could not be reproduced here) |
| E · B (kickoff asks FULL/LIGHT/TRUNK, cuts the right name, banner word; no `quickdev` in commands) | satisfied | `cicd-create-epic-sprint.md:103-107` the ask; `:123-126` FULL and LIGHT cut lines; `:148-149` post-cut assertion admits both shapes; `:114-115, :220-221` banner word; `grep -rc quickdev .agents/commands` → every file 0; `test_trunk_mode` rows 9/25/26 green |
| E · C (twelve doors print the mode line first; no door keeps its own `for-each-ref`) | satisfied; literal diverges | `grep -l "epic_mode.py" .agents/commands/cicd-*.md \| wc -l` → **13**, not 12 — the twelve callers plus `cicd-create-epic-sprint.md:138` (a prose mention, "`epic_mode.py` is an unanchored substring test"); `grep -l "for-each-ref.*epic" …` → 0; `test_epic_mode.py` F pins exactly 12 `epic_mode.py --repo` call lines, each `cd "$L" &&`-pinned with `L=$(pwd)` before it; `test_boot_epic_branch_read.py` A6 (no unbound `$L` in any door) 51/51 |
| E · D (two arms; no fence pushes `HEAD:epic/`; walkthrough rides the PR) | satisfied | `cicd-close-story-merge-tree.md:296-345` Arm A / Arm B keyed on the word; `grep -n 'HEAD:epic/'` → `:302`, `:377` prose only ("retired", "never"); `:356-377` walkthrough committed before the PR opens; `test_trunk_mode.py` block B 37/37 |
| E · E (push-e2e names LIGHT; e2e names the branch under test + on-demand) | satisfied | `grep -c LIGHT` → `cicd-push-e2e.md` 4, `cicd-e2e.md` 5; push-e2e `:137-139` "first and only E2E run for the whole epic"; e2e `:7-14` |
| E · F (both hand-authored launchers current in both copies; generated ones re-synced) | satisfied | `diff .agents/skills/cicd-create-epic-sprint/SKILL.md .claude/skills/…` → empty; same for `cicd-close-story-merge-tree`; `test_command_surfaces.py` 343/343 |
| E · G (SOP §7, close-out section, atlas, changelog same commit; gates clean) | satisfied | `git show --name-only 4d7b3a2e` → 42 files incl. both SOP files; SOP `:828-835` "There is no direct `HEAD:epic/` push any more"; kickoff block `:481-525`; atlas `:4161,:4166`; gates as A·E |

### Findings
- **severity: suggestion** · **confidence: 0.9** · `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/handoff.md:33,36,54,123` · The hand-off at HEAD describes a state four commits gone — violates Plan row H's record contract (the close-out reads the lane's record) and the file's own first line ("Every claim here is checkable against the tree") — evidence: it says `HEAD 18afe3f6`, `Verdict FAIL @ dd5a5c42`, a "What is broken" section naming rows 1/9/8 as open, and "It is not lifted now" about the rules freeze; the walkthrough's `## Changes applied` says all 30 rows were applied at `2cee8c5f`…`fb2639ac` after the freeze was lifted, and the records commit `ffca21c7` did not touch `handoff.md` (`git show --name-only ffca21c7` → suite.json, review-lenses.md, walkthrough.md, INDEX.md). A next agent following its "How to continue" re-does or refuses work that is done — reproduced: `grep -n 'HEAD |\|Verdict |\|It is not lifted now\|What is broken' handoff.md`
- **severity: suggestion** · **confidence: 0.9** · `_artifacts/…/preflight-receipt.json` · The lane's preflight receipt names a verdict that no longer exists — violates Plan row H ("one gate at the tip") — evidence: `verdict_sha: 46bc4267ffda…`, `when: 2026-09-10T23:04`, i.e. the retracted `PASS` stamp, eight commits behind HEAD; review row 30 already records this as "deferred — rewritten by `task_preflight` at the shipping tip after the re-review stamps". Still open at HEAD; noted so the assessor sees it is not yet closed — reproduced: `cat preflight-receipt.json`
- **severity: suggestion** · **confidence: 0.5** · `.agents/commands/smh-quick-dev.md:106-152` (Step 0.5) · The quick lane dropped the "reusing a tree `/smh-plan-task` cut? absorb `origin/main` FIRST" block the old Step 0.5 carried, while `/smh-plan-task` now sends its ⚡ `quick-dev` lanes to this door — engages Part D §Step 0.5 ("today's Step 0.5, carried over"; the plan enumerated key, worktree and `jira_feed.py start`, not the absorb block, so this is a divergence from the old body, not from the plan's list) — evidence: diff lines 2324-2332 delete the block from `smh-quick-dev.md`; `smh-dev-task-tests.md` keeps it; `smh-plan-task.md:120,2120` "⚡ marks the lanes small enough for one quick-lane `/smh-quick-dev` pass". Scenario: a ⚡ lane's tree was cut at planning time, siblings land, the operator runs `/smh-quick-dev` in it days later; nothing tells the agent to absorb first, so the conflicts the deleted text said are "cheap and yours" at the tree arrive at `/smh-close-task-merge-tree`'s "origin/main absorbed" check instead — inferred (not executed)
- **severity: nitpick** · `.agents/commands/cicd-label-tasks.md:44`, `.agents/commands/smh-label-tasks.md:226`, `.agents/commands/smh-close-task-merge-tree.md:331` · Three "light lane"/"lightweight lane" survivors — violates Part D's re-point-by-meaning sweep (it declared `smh-label-tasks` "light lane reworded", 2 sites, and missed `:226`; `cicd-label-tasks` and the close-out line are outside its declared set) — evidence: "a child the light lane fits | ships via `/cicd-quick-dev`", "⚡ quick-dev | small enough for one light lane", "(or a lightweight lane that recorded none)"; now that LIGHT is an epic mode the phrase is ambiguous — reproduced: `grep -n -i 'lightweight lane\|light lane' .agents/commands/*.md`
- **severity: nitpick** · `<fixture>/parts/SCC-446.md` § Acceptance row C · The row's literal check reads as a failure at HEAD and, unlike C·C and D·B, the walkthrough did not record the divergence — evidence: `grep -l "epic_mode.py" .agents/commands/cicd-*.md` lists 13 (the prose mention at `cicd-create-epic-sprint.md:138`, added by the review fix for row 25); substance holds (12 call lines, pinned) — reproduced
- **severity: nitpick** · `.agents/commands/smh-dev-task-tests.md:35-36` · The "rename, no behaviour change" carries a fourth content edit the plan did not enumerate — violates Part D §1 ("The only lines that change are the description, the title and the flow-position line") — evidence: difflib against `origin/main:smh-quick-dev.md` shows the two-line intro paragraph rewritten; prose only, but the walkthrough reported "5 changed lines" without naming it — reproduced
- **severity: nitpick** · `<fixture>/parts/SCC-446.md` §3 "Not touched" · The stated reason for leaving `cicd-park.md` out ("none of them cut, base, land or ship a branch") is false on its face — evidence: `cicd-park.md:79` `git push origin epic/<JIRA-KEY>-<slug>`, a direct epic push of the same class as the kickoff's `:197/:234/:268` (already routed to AVCH-152 in the walkthrough). Under the PR-only landing the local epic head never leads origin, so park's push is a no-op; no failure to state, hence nitpick — reproduced: `grep -n 'git push' .agents/commands/cicd-park.md`

Areas walked with nothing found: every spec constraint outside the tables — "no door prompts to cut a light epic" (grep over `.agents/commands`: none), "TDD stays in every lane" (Step 3 in both quick-lane doors), the rails table, `EPIC_REF_RE` (`task_preflight.py:123`, `.+` after the key admits `-light-epic-`), `ship_preflight.BRANCH_RE` (`:55`, same), `merge-target-guard.sh:159` `epic/*)`, no `-epic-(\d+)` parser anywhere in `.agents/scripts`, no `quickdev` reader outside a fixture string and retirement comments, `Projects/` untouched by the diff, the autopilot's "launch word is a batch approval" pre-dates this lane (`cicd-autopilot-claude.md:13,109`).

### Drift — in the diff, beyond the list
- `.agents/rules/reproduce-before-you-fix.md` — one phrase re-pointing at the rebuilt door's RED phase; consequence of Part C; undeclared, stays
- `.agents/scripts/tests/test_approved_word_is_the_operators.py` (NEW) — the pin for review row 8; undeclared, stays
- `.agents/scripts/tests/test_sops_prds_folder.py` — `DISCUSSED_AS_RETIRED` entry for the deleted door; consequence of Part D; undeclared, stays
- `.agents/scripts/tests/test_task_preflight.py` — review row 13 pins; undeclared, stays
- `.agents/scripts/wf_common.py` — `norm_path` hoist (review); undeclared, stays
- `.agents/skills/cicd-e2e/SKILL.md`, `.claude/skills/cicd-e2e/SKILL.md`, `.agents/skills/smh-self-audit/SKILL.md`, `.claude/skills/smh-self-audit/SKILL.md` — generated descriptions following their commands; undeclared, stays
- `.claude/rules/living-template-sync.md` — path-scoped mirror of the edited master; undeclared, stays
- `.agents/scripts/task_preflight.py` — declared by Part D as "comment" only; delivered `_QUICK_LANE_RE`, `_stale_against_sha` and the `check_gate` dereference (147 diff lines, review row 13) — declared path, beyond its declared scope; stays (pinned)
- `.agents/scripts/closeout_preflight.py` — declared by Part C; also imports the helper from `task_preflight` and replaces its inline staleness diff; declared, stays
- `.agents/commands/cicd-quick-dev.md` `--no-track` on the three worktree adds — beyond Part C's enumerated edits (SCC-444's second commit); consistent with `worktree-per-story` G3; declared path, stays
- `.agents/commands/smh-merge-multiple-workingtrees.md:255` artifact-path fix (`2026/08/`) — beyond the declared lane-name re-point; `check_links`-driven; stays
- `_artifacts/…/{gates/suite.json, handoff.md, preflight-receipt.json, review-lenses.md}` — lane records outside the declared block (the parser ignores `_artifacts/`); `handoff.md` and `preflight-receipt.json` are stale at HEAD (findings 1–2)
- Part D plan §Step 1 "`lane_qualify.py` is no longer called by any door" vs the build's "no dev door (the two standing-push doors still qualify `LIGHT` with it)" — `smh-non-crit-pr-push.md:30` and `cicd-non-crit-pr-push.md` still call it; the build's sentence is the true one, the plan's is not
- Unimplemented (declared, not touched): `.agents/commands/smh-new-project.md`, `docs/_scc_sops_prds/tea_testing_guide.md` — Part F, deferred by design (`declared_change_set.py diff` → exactly these two)

**Count: 7 findings — 0 critical, 0 important, 3 suggestion, 4 nitpick. Rows: 33 satisfied, 0 not satisfied, 6 diverge, 2 deferred.**

Tree left clean: `?? .claude/agents .claude/commands .claude/hooks .claude/launch.json .claude/loop.md .claude/routines .claude/scheduled_tasks.json .claude/workflows` (sandbox bind mounts, present before my first command; no tracked file modified, nothing written under the repo — scratch lived in `$TMPDIR`)

## Test-Adequacy Auditor (isolated worktree)

Isolation: toplevel=/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/agent-a070c52f4e3277d56 HEAD=ffca21c79248f2bd52ad163925562382bf09ac6e
Baseline: run_all.py 87/87 files passed

### Findings
- **severity: important** · `.agents/scripts/task_preflight.py:1545-1550` (`check_gate`, the `if foreign_stamped: … elif quick:` order) · A stamped sibling walkthrough that merely cites the key silences the quick lane's approval-sha dereference — tier missing: a unit case with BOTH this lane's record line AND a foreign stamped walkthrough present (row 13 has only the lane alone) — evidence: reproduced by execution: the row-13 fixture (record line at sha X, then a `<fixture>/docs/after.md` commit) exits 2 with `STALE, re-approve`; add one walkthrough in `_artifacts/_main/2026-01-01_other-lane/` (task.yaml `SCC-99`, prose "Follow-on: SCC-11 …", `Verdict: PASS @ …`) and the same run exits 0 with `[INFO] gate: verdict stamp(s) exist only in 1 walkthrough(s) … the full gate runs` and no STALE row. `check_artifacts` (line 1326) collects any walkthrough whose text mentions the key, so any lobby lane cited by a reviewed sibling loses the SCC-441 row-13 protection. Mutation M23 (precedence swapped to `if foreign_stamped and not quick:`) SURVIVED `test_task_preflight.py` 124/124 and the whole suite 87/87 — suggested test: extend row 13 with a foreign stamped walkthrough citing the key and assert `STALE, re-approve` + exit 2 (and pin whichever precedence the design intends).
- **severity: important** · `.agents/scripts/closeout_preflight.py:348` vs `.agents/scripts/task_preflight.py:1507` · The "one reader" is two readers: the project close-out feeds the regex UNSTRIPPED text, the lobby close-out feeds `strip_fenced` text, and both doors show the record line inside a ``` fence — tier missing: a contract case feeding a fenced record line to both readers (row 14 pins only `tp._QUICK_LANE_RE is cp._QUICK_LANE_RE`, regex identity, not reader agreement) — evidence: reproduced by execution with the line copied exactly as `cicd-quick-dev.md` Step 4 and `smh-quick-dev.md` Step 4 display it (inside a fence): lobby `task_preflight` → exit 0, `no review Verdict line in this task's own walkthrough - the full gate runs`, no dereference, a post-approval commit passes; project `closeout_preflight` on the same text → INFO "quick lane … approved by the operator", `1 code file(s) changed since the approved SHA`, rc 2. Per `wf_common.strip_fenced`'s own doctrine (SCC-154: a fenced stamp is a paste, not a record) the two disagree about whether the doors' own template shape is evidence — suggested test: one fenced record line + one post-approval commit, run through both readers, assert the same decision (and settle whether closeout should strip, or the doors should show the line unfenced).
- **severity: suggestion** · `.agents/scripts/epic_mode.py:59-60` (`live_epics`, `if r.returncode != 0`) · The script's own contract table lists `ERROR … not a git repo, or git failed` and the "git failed" half has no case — tier missing: a unit case where `.git` exists but git fails — evidence: mutation M4 (returncode branch removed) SURVIVED `test_epic_mode.py` 34/34 and the suite 87/87; direct probe at HEAD with a `.git` pointer file naming a missing gitdir (the shape `worktree prune` leaves) → `ERROR` / `fatal: not a git repository`, exit 2; under the mutant the same tree prints the empty-list answer, `TRUNK`, exit 0 — a broken linked worktree routed to the trunk arm, the direction the file's own `--repo ""` guard calls the worst kind of wrong — suggested test: block E gains a `.git` file `gitdir: /nonexistent` case asserting line 1 `ERROR`, exit 2.
- **severity: suggestion** · `.agents/scripts/scope_check.py` (`main`, `if not p: continue`) · The empty-string-path guard has no pin — tier missing: a unit case for `--paths ""` (what a quoted, unset shell variable becomes) — evidence: at HEAD `--paths ""` → `ERROR` exit 2 and `--paths "" backend/auth/x.py` → `OVERLAP`; mutation M7 (`continue` → `pass`) SURVIVED `test_scope_check.py` 106/106 and the suite 87/87 — under it `--paths "$PLANNED"` with `PLANNED` empty is a one-element list, the map matches nothing, and the pass word prints — suggested test: block D adds `run(repo, "--paths", "")` → `ERROR`, exit 2.
- **severity: suggestion** · `.agents/scripts/wf_common.py:norm_path` (new) · No direct unit test, and `scope_check`'s consumption of it is unpinned — tier missing: a `norm_path` unit block and one scope_check case with a `./` or backslash path — evidence: M12 (the `./` loop removed) SURVIVED `test_scope_check.py` 106/106 and was killed only at suite level by `test_refresh_maps.py` (86/87) — a different consumer; M13 (backslash normalisation removed) SURVIVED 106/106 and the suite 87/87. Under M13 the PC spelling `.github\workflows\x.yml` in a mapped repo never matches the `.github/` prefix and prints `CLEAR`; the docstring names the `lstrip("./")` trap it exists to avoid and no test holds it — suggested test: `norm_path("./.github/x.yml")`, `"././a"`, `".github\\x.yml"`, `".agents/x"` (dot kept), plus `--paths ./.github/workflows/x.yml` → `OVERLAP`.
- **severity: suggestion** · `.agents/scripts/tests/test_approved_word_is_the_operators.py:GRANT` · The grant scan fires only on a possessive of five nouns; the same grant re-worded passes — tier mis-applied: the control set proves the two shipped sentences and one reverse order, not the phrasing space — evidence: executed `grants()`: `both `approved` stops are the lead's` FIRES; `both `approved` stops are the Cheshire Cat's`, `the builder's `approved` is enough here`, `the lead supplies `approved` at both stops`, `the lead may write `approved` on the operator's behalf`, and ``approved` is supplied by the child` are all quiet. The author states the narrowness is deliberate to avoid firing on prose about the rule; none of the five quiet sentences is prose about the rule — each is the grant itself, and "the agent never supplies `approved`" (the negation control) stays distinguishable by its `never` — suggested test: extend WHO with the seat names and add a verb form (`(?:supplies|writes|gives|provides)\s+`approved``) with the existing negation control kept green.
- **severity: nitpick** · `.agents/scripts/epic_mode.py:106` (`uncommented`, the whitespace-before-`#` rule) · Branch dead to the suite — evidence: M2 (`elif ch == "#":`) SURVIVED 34/34 and 87/87; at HEAD `run: echo x#-light-epic-` keeps the token, under the mutant it is stripped → NOT ARMED. Fails toward the loud side the author names as safe, hence nitpick — suggested test: one `light_armed` line with an unspaced `#` before the token asserting ARMED.
- **severity: nitpick** · `.agents/scripts/epic_mode.py:76` (`_closing_quote`, the escape applies only inside `"`) · Branch dead to the suite — evidence: M3 (escape honoured inside `'` too) SURVIVED 34/34 and 87/87; the differing input is contrived (`'x\' # a' -light-epic-`) — suggested test: one single-quoted-scalar-with-backslash line, or drop the distinction and say so.
- **severity: nitpick** · `.agents/scripts/scope_check.py:overlaps` (`break`) · The documented "at most ONE line per path" contract is unpinned — evidence: M10 (`break` → `pass`) SURVIVED 106/106 and 87/87. The assessor dismissed this on the previous pass as "output shape, not a verdict"; that is correct for the word and the exit code, but the docstring calls the single line "the contract" and both doors tell the agent to print every overlap line, so a duplicate reads as two problems — suggested test: `<fixture>/backend/auth/session.py` in an unmapped repo → exactly one overlap line.
- **severity: nitpick** · `.agents/scripts/scope_check.py:load_map` (the `why` default) · No fixture declares a surface without `why` — evidence: M11 (default text removed) SURVIVED 106/106 and 87/87; under it the overlap line ends `auth: ` with an empty reason — suggested test: a map row with no `why` asserting the default reason on the overlap line.

### Examined and adequate
- `epic_mode.live_epics` origin/ prefix strip — M1 (append `ref` unstripped) KILLED: `test_epic_mode.py` 30/34, `[FAIL] line 1 is `FULL epic/SCC-1-epic-2-x` … ['FULL origin/epic/SCC-1-epic-2-x', …]` plus the LIGHT, light-in-slug and linked-worktree rows.
- `scope_check.load_map` bare-word rule — M17 (`is_file` → `exists`) KILLED: 105/106, `[FAIL] SCC-441 row 6 · a bare word naming a root DIRECTORY is the same ERROR … rc=0 ['CLEAR']`.
- `_QUICK_LANE_RE` sha length — M18 (`{6,40}`) KILLED: `test_closeout_preflight.py` 125/126, `[FAIL] QL16 CONTROL · a short sha is NOT the record line`.
- `_stale_against_sha` pathspec source — M19 (`DEPLOY_DIRS`) KILLED: 125/126, `[FAIL] SCC-441 row 19c · fallback arm with a `.github/` dir present`.
- `_stale_against_sha` warn/err asymmetry — M20 (`say = rep.err`) KILLED: 124/126, both row-19a checks red.
- `_stale_against_sha` fallback excludes — M21 (`_bmad-output/` dropped) KILLED: 125/126, `[FAIL] SCC-441 row 19b`.
- `task_preflight.check_gate` collects the record line — M22 (`quick.append` never reached) KILLED: `test_task_preflight.py` 120/124, all four row-13 checks red (`exit 0` where `STALE, re-approve` exit 2 was required).
- `closeout_preflight` dereferences the approval sha — M24 (`_stale_against_sha` call removed) KILLED: 117/126, QL8, QL9, QL14, QL17 red.
- `wf_common.norm_path` `./` stripping — M12 KILLED at suite level only (86/87, `FAILED: test_refresh_maps.py`); its own consumer's file (`test_scope_check.py`) stayed 106/106, which is the gap listed above.
- Door-reading tests read the doors' real text, not typed strings: `test_closeout_preflight.py` row 14 extracts the `Review: none … <sha>` template lines from both doors and feeds them to both readers; `test_scope_check.py` G greps both doors for `--paths`, `--diff` and a quoted `--repo`; `test_epic_mode.py` F counts the twelve `cicd-*` callers and pins `cd "$L" &&` on the call line with `L=$(pwd)` before it; `test_boot_epic_branch_read.py` A6 scans every door's fences for `$L` used before bound; `test_trunk_mode.py` reads `git-policy.md`, the kickoff and the close-out door by regex; `test_approved_word_is_the_operators.py` scans 60+ law files; `test_command_surfaces.py` CS-13 applies `gh pr merge --merge` to the real close-out door's step body, not only to its synthetic controls.
- Every gate the diff adds is pinned on both sides: `scope_check` prints and exits `CLEAR` / `OVERLAP` / `ERROR` (block B/C/D/E/F); `epic_mode` prints `TRUNK` / `FULL` / `LIGHT` / `AMBIGUOUS` / `ERROR` (blocks A–E2); `light_armed` is armed and not-armed across seven workflow shapes (E3); the quick-lane staleness check errs and passes on both arms (QL7–QL20c, row 19a–c, row 13); `unbound_L` catches the cross-fence and after-use shapes and passes the fixed shape; `GRANT` fires on both shipped lines and stays quiet on the record line and the negation.
- Direct probes at HEAD behave: `--paths ""` → `ERROR`; `--repo "  "` → `ERROR` (pinned); a `.git` pointer to a missing gitdir → `ERROR` exit 2; `norm_path("./.github/workflows/x.yml")` → `<fixture>/.github/workflows/x.yml`.
- Rubric questions 2 and 3: no script in this diff produces or parses LLM output, so there is nothing to assert softly; no judge-style behavioural test exists for the door prose — raised once by the previous lens as house architecture and ruled out of this lane's scope by the assessor, not re-raised.
- The lobby map's 32 declared paths: 31 resolve on disk; `.claude/settings.local.json` is the gitignored per-machine file, not a dead row — a "rows resolve" pin would need that one exemption; no finding.
- `.opencode/commands` twins: all 24 changed masters byte-identical; `smh-quick-fix.md` absent from `.agents` and `.opencode`.

**Count: 10 findings — 0 critical, 2 important, 4 suggestion, 4 nitpick. Mutations run: 17, killed: 9, survived: 8.**
Tree left clean: `?? .claude/agents` `?? .claude/commands` `?? .claude/hooks` `?? .claude/launch.json` `?? .claude/loop.md` `?? .claude/routines` `?? .claude/scheduled_tasks.json` `?? .claude/workflows` (the eight sandbox bind mounts present at session start, never written); `git diff --stat HEAD` is empty; every mutant restored with `restore_cmp=True` on all 17 file-level runs and all 9 suite-level runs.

## Evidence Verifier (step 2, one wave with Compound Synthesis) — dossier: built, 37 packages

Every result `verified: true`. Revised severity and confidence per finding, with the verification note condensed to what settled it:

| # | Finding (short) | revised | conf | What settled it |
|---|---|---|---|---|
| 1 | unset-upstream after --no-track (cicd-quick-dev:103) | suggestion | 0.95 | Re-ran: add --no-track rc 0; unset rc 128 with the fatal; the door's compound rc 128; control without --no-track rc 0. Tree usable afterwards; noisy and deterministic. |
| 2 | smh-dev-task-tests:514 "Step 0" | nitpick | 0.9 | task.yaml only at 491 (Step 5) and 514; the same sentence exists at origin/main's smh-quick-dev.md:514 — pre-existing, inherited by the rename. |
| 3 | git-policy row 5 puts the tripwire in the close-out | suggestion | 0.85 | Read both rule texts; grepped every door and script for scope_check: only the two quick-dev doors' Steps 1/5 call it. |
| 4 | smh-quick-dev Step 3 floor unpinned | important | 0.8 | Read the fence and the four scripts' cwd/__file__ derivations; nothing pins the tree; the close-out's receipt run is the backstop, so important not critical. |
| 5 | handoff.md stale | important | 0.75 | Read handoff, suite.json, walkthrough §Changes applied, git log -- handoff.md (last touched d77b8a4d). |
| 6 | (group of 1) | suggestion | 0.95 | expanded from 1 |
| 7 | dir without slash / leading slash dead row | suggestion | 0.9 | Reproduced: map ["backend/auth"] → CLEAR; ["/backend/"] → CLEAR; control ["backend/auth/"] → OVERLAP; is_dir() True so the remedy is one line. |
| 8 | record line written before the word | suggestion | 0.8 | Read both Step 4s and both readers; no door says which sha; the staleness check still catches post-sha code commits. |
| 9 | TASK-LIGHT row cites a deleted licence | suggestion | 0.8 | Grepped right-siz across SOP, both lobby dev doors, the standing-push door and lane_qualify.py (:20, :92); the diff deletes the SOP paragraphs. |
| 10 | staleness blind to .github/ and firebase.json with product dirs | suggestion | 0.7 | Reproduced on a deployable fixture; partly covered: the Step 5 tripwire reported OVERLAP on .github/ in the same fixture; residual is a commit after the tripwire or an overridden .github/ edit. |
| 11 | prune-worktree fence comment "PARKED" | nitpick | 0.9 | Read lines 345-380; cosmetic gloss from the retired model. |
| 12 | absorb main after approval → STALE | important | 0.85 | Reproduced with the suite's fixtures (F0/F1/F2). On the remedy: `git log --first-parent --no-merges` names NOTHING in a conflict-resolution scenario, so it would miss the edit that matters; a sound measure flags the resolved file and ignores the absorbed one. |
| 13 | placeholder / fenced record line → lobby gate benign | important | 0.85 | Reproduced G1 (literal <sha>: exit 0 clear) and G2 (fenced + post-approval commit: exit 0 clear); cp raw True vs tp stripped False; closeout on the same text → STALE ERROR. Both doors display the line inside a fence. |
| 14 | tripwire reads the map from the lane's tree | important | 0.9 | Reproduced C1/C2; stronger variant: in an UNMAPPED repo a lane that writes the repo's first one-row map reads CLEAR too. Remedy base sound on both lane shapes: `git show <merge-base>:map` on a chore lane; on a story lane whose epic carries no map it fails → None → generic set, whose ci rows name the map file itself. |
| 15 | dir-without-slash + nonexistent exact file | suggestion | 0.85 | Directory half as 7; exact-file half reproduced (map ["backend/auth/tokn.py"] → CLEAR). The assessor's caveat holds: .claude/settings.local.json is gitignored and absent in a fresh clone; block A runs the real lobby map, so a hard existence ERROR would red CI — a gitignore-aware check is the remedy. |
| 16 | lobby-relative path → CLEAR | important | 0.75 | Reproduced B1-B4 with cwd = a lobby dir; (cwd/p).resolve() lies inside the repo so rebase-when-it-exists-under-cwd is implementable; a NEW file typed lobby-relative remains the residual. |
| 17 | directory-granularity planned set | suggestion | 0.75 | Reproduced D1-D3; reachable only if the agent declares directories; cost is a late eject. |
| 18 | fetch and mode query not chained | suggestion | 0.75 | Reproduced I1-I3; the fatal is loud in the same output; a && chain or a named STOP fixes it. |
| 19 | (group of 1) | suggestion | 0.95 | expanded from 1; fires on every open of both doors. |
| 20 | :159 comment contradiction | nitpick | 0.85 | Read both fences and command-shape; self-contradicting comment, not a dead gate (empty --repo refusal pinned). |
| 21 | (group of 5) | important | 0.75 | expanded from 5 |
| 22 | preflight-receipt stale | suggestion | 0.85 | Read the receipt and git log; task_preflight rewrites it on every run — a stale artifact, not a gate defect. |
| 23 | absorb-first block dropped from smh-quick-dev Step 0.5 | suggestion | 0.7 | Grepped absorb/reusing a tree/smh-plan-task in origin/main's file, both HEAD doors and smh-plan-task; consequence is deferred to close-out where finding 12 then flips STALE. |
| 24 | "light lane" survivors (3) | nitpick | 0.9 | grep reproduces the three plus the two intentional retirement notices. |
| 25 | row C literal 13 vs 12 unrecorded | nitpick | 0.9 | Ran the grep (13); cicd-create-epic-sprint.md:138 prose mention added by the row-25 fix; test F pins 12 call lines. |
| 26 | fourth edit in the rename unenumerated | nitpick | 0.85 | `git diff --no-index` origin/main blob vs HEAD: 5 changed lines incl. the intro paragraph at 27-28 (the finding's 35-36 is off; the claim stands). |
| 27 | parts/SCC-446 §3 reason for cicd-park | nitpick | 0.6 | "False on its face" overstates it; a sync push is not cutting/basing/landing/shipping; no failure follows. |
| 28 | foreign_stamped precedence silences the quick dereference | important | 0.9 | Reproduced: a foreign stamped sibling mentioning the key → exit 0, no STALE; control without it → exit 2 STALE. check_artifacts collects by substring, so SCC-1's pool holds every SCC-1x walkthrough. |
| 29 | (group of 13) two readers | important | 0.85 | expanded from 13 |
| 30 | epic_mode git-failed branch unpinned | suggestion | 0.85 | Reproduced on copies: .git = gitdir: /nonexistent → HEAD (2, ERROR); M4 → (0, TRUNK). Code at HEAD correct; test gap. |
| 31 | --paths '' unpinned | suggestion | 0.85 | Reproduced: HEAD (2, ERROR); M7 (0, CLEAR); the test passes no empty string. |
| 32 | norm_path backslash unpinned | suggestion | 0.8 | Reproduced: `.github\workflows\x.yml` HEAD OVERLAP; M13 CLEAR; no backslash fixture in either test. |
| 33 | GRANT scan narrow | suggestion | 0.85 | Executed grants() on six sentences; only the shipped one fires; seat names, verb forms and non-backticked approved all miss. |
| 34 | whitespace-before-# dead | nitpick | 0.9 | Reproduced: HEAD ARMED; M2 NOT ARMED; fails toward the loud side. |
| 35 | _closing_quote escape in ' | nitpick | 0.8 | Read; contrived input; not executed. |
| 36 | overlaps break unpinned | nitpick | 0.85 | Read the tests end to end; output-shape contract, exit unchanged. |
| 37 | why default unpinned | nitpick | 0.85 | Read; cosmetic reason text only. |

## Compound Synthesis (step 2, one wave with the Verifier)

dossier: built, 37 packages

- **severity: important** · **confidence: 0.75** · In the lobby the critical-surfaces line has no enforcement point outside the agent's own hands, and the hub rule tells the reader a second one exists
  contributing_findings: "git-policy Two-toggles row 5 places the eject tripwire in the close-out door…"; "The Step 5 tripwire reads the surfaces map from the LANE's own tree…"; "A lobby-relative path … answers CLEAR in a mapped repo"; "A planned set declared at directory granularity … is CLEAR over a critical child"
  evidence: `task_preflight.py:1244-1261` `deploy_surface` returns `[]` for a repo with no PRODUCT_DIRS, and `check_scope` (`:1264-1290`) then returns `LOCAL, []` for any diff — so every row of the lobby map's `ci` surface passes the lobby close-out untouched, by SCC-118 design. Nothing else on the operator's side reads the map; the only call sites are the two quick-dev doors' Steps 1 and 5, run by the agent. `critical-surfaces.md:116-117` states the close-out doors do not call the script; `git-policy.md:190` row 5 states the close-out "re-runs the scope check on the real diff". Remedy proposed: have `task_preflight` run `scope_check --diff <base_ref>` itself with the map read from `base_ref`.

- **severity: important** · **confidence: 0.75** · The cicd door promises a refusal the ad-hoc lane never meets: "a walkthrough with neither line is still refused there" is closeout_preflight's branch, and the ad-hoc lane closes through task_preflight, which has no such branch
  contributing_findings: "The lobby gate ignores an unfilled '@ <sha>' placeholder or a fenced record line…"; "The 'one reader' is two readers…"; "The record line … is written by the agent BEFORE the stop that obtains the approval"
  evidence: `cicd-quick-dev.md:349` shows the record line inside a fence with a literal `<sha>`, written before the `approved` stop at `:357`, and `:355` assures the agent that `closeout_preflight.py` "still refuse[s]" a walkthrough with neither line. That refusal belongs to the story-lane reader; the cicd ad-hoc lane is routed at `:181` and `:423` to `/smh-close-task-merge-tree Projects/<name>`, which runs `task_preflight.py`, whose reader strips fences, has a NEAR_MISS guard for Verdict typos only, and falls into `rep.info("no review Verdict line ... the full gate runs")`. Remedy: extend `task_preflight`'s NEAR_MISS treatment to the record line, and correct `cicd-quick-dev.md:355` to name the reader the ad-hoc lane actually meets.

- **severity: important** · **confidence: 0.70** · The /smh-plan-task hand-off makes the false STALE certain: the quick door deleted the only instruction to absorb main BEFORE approval, so the absorb now happens at close-out, after approval, where it flips the approval STALE
  contributing_findings: "smh-quick-dev Step 0.5 dropped the 'reusing a tree /smh-plan-task cut? absorb origin/main FIRST' block…"; "Absorbing origin/main after the walkthrough approval … flips the quick-lane approval STALE"
  evidence: the deletion at diff 2324-2332 removes "Reusing a tree /smh-plan-task cut? Absorb main FIRST (SCC-155) …"; it survives only at `smh-dev-task-tests.md:111-119`. `smh-plan-task.md:252` marks its small lanes for one `/smh-quick-dev` pass; Step 0.5 has no merge before the `approved` stop; the first merge the lane is told to do is at close-out (`task_preflight.py:1235`), after which `_stale_against_sha` finds the absorbed files. Remedy: restore the six deleted lines in `smh-quick-dev.md` Step 0.5.

- **severity: important** · **confidence: 0.65** · The STALE remedy is agent self-service, and finding 11 makes it routine: nothing in the gate distinguishes a re-approval from the agent bumping the sha in a line it wrote itself
  contributing_findings: "The record line … is written by the agent BEFORE the stop…"; "Absorbing origin/main after the walkthrough approval … flips the quick-lane approval STALE"; "The GRANT scan … fires only on a possessive of five nouns"
  evidence: the staleness check's whole input is the record line, which the agent writes with a sha of its own choosing before the stop; its remedy text is "re-approve" and no close-out door says what re-approving means. The path of least resistance is editing the hex to HEAD in an `_artifacts/`-only commit, which the pathspec excludes. Note when fixing 11: counting only first-parent lane commits would hide a merge-resolution hunk, which the house treats as code; measure the lane's merge-base diff against base instead.

- **severity: important** · **confidence: 0.70** · Systemic: both new gate scripts resolve unrecognised input to the permissive word and have been patched one reproduced shape at a time; this wave found the next four shapes
  contributing_findings: "A directory entry without its trailing slash, or an exact-file entry naming a file that does not exist, is a silently dead map row"; "A lobby-relative path … answers CLEAR"; "A planned set declared at directory granularity … is CLEAR"; "The lobby gate ignores an unfilled '@ <sha>' placeholder or a fenced record line"; "check_gate's `if foreign_stamped: ... elif quick:` order…"
  evidence: `scope_check.py` carries six case-patches (non-string entry, bare word, empty `--repo`, zero diff, absolute path, empty map); the structural cause is that `--paths` never resolves a planned path against the repo and `load_map`'s existence check is gated on a heuristic. `task_preflight.check_gate` sends everything that is not a recognised stamp to `rep.info(... the full gate runs)`. The fix is one rule per script: in `--paths` mode a planned path must resolve under `repo` (an existing file, or a not-yet-existing file; a directory is judged as a prefix or refused; lobby-relative, `..`, or elsewhere is ERROR); in `load_map`, every non-prefix row must name a file that exists or is gitignored; in `check_gate`, a governing walkthrough carrying the record phrase that does not parse is an error.

- **severity: important** · **confidence: 0.60** · The unconditional `fatal` on every Step 0.5 open trains the reader to skip the one `fatal` in the previous fence that matters — a failed fetch — which is the only signal of finding 17's dead-epic base
  contributing_findings: "Step 0.5 fence runs git branch --unset-upstream after a --no-track worktree add…"; "In the Step 0 fence of all twelve doors the fetch and the mode query are independent lines…"
  evidence: in `cicd-quick-dev.md` the two fences run back to back; a failed fetch prints `fatal:` and the mode query still prints `FULL <shipped epic>` exit 0; the next fence's `--unset-upstream` prints `fatal:` on every open. No rule maps a `fatal` line in fence output to a STOP. Deleting `:103` (and `smh-quick-dev.md:117`) and chaining Step 0's fetch to the mode query with `&&` closes both.
