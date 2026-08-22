---
IsArtifact: true
ArtifactMetadata:
  title: SCC-244 — the rolling bug list run as one consolidated lane (cycle 4)
  type: walkthrough
  date: 2026-08-21
---

review-runtime: fan-out

# SCC-244 — Seven riders, one lane, and the regression the lane found in itself

**Lane:** `chore/SCC-244-bugs-updates-cycle-4` · **Ticket:** SCC-244 (Task, rolling "Bugs and Updates", cycle 4)
**Riders:** SCC-254 Part A · SCC-255 B · SCC-256 C · SCC-257 D · SCC-258 E · SCC-259 F · SCC-260 G
**Plan:** [implementation_plan.md](implementation_plan.md) (with its Self-Audit, `Audit verdict: GO`)
**Base:** `origin/main@038c0f1`, unmoved for the whole lane — no absorb was needed.

---

## What this changed, and the one thing that changed the shape of it

Seven riders were developed in **one** worktree instead of seven, on the operator's instruction, because six of them are single-file fixes whose only shared surface is the test harness. That decision is what made the lane's own worst defect findable: **the code review found a regression this lane introduced in rider C** — a story worktree cut off `origin/epic/…` inherits the **epic** as its upstream, so every `0 0` check in the house measures the wrong remote and a bare `git push` fatals with git's own suggested remedy being the mid-story epic push `worktree-per-story.md` G3 bans. Seven separate lanes would each have gated green on their own file.

Two riders were re-scoped on ground truth rather than built as written:

- **G dropped both `_bmad/custom/*.toml` override halves** on the operator's ruling — *"we cant change bmad stuff … if there is something we created that contradicts bmad we need to look at that or just drop this fix plan all together."* Not editing BMAD and not overriding it are the same instruction, so the halves are **withdrawn, not deferred**: there is no defect left to anchor, and filing them would mint two tickets nobody may close. What remained was real and landed — the live defect was `/sm`, which invoked `bmad-create-story` naming no output path.
- **C grew a second half** when recon showed `worktree-per-story.md` itself carries the HEAD precondition the command was following. Fixing only the command would have left it silently contradicting its own rule.

Three riders are guarded by pattern scans over the whole `.agents/commands/` + `.agents/rules/` glob with a file-count floor — never a pinned line number — and every requirement in every scan has a mutant that kills it.

## Task Checklist

- [x] Open ONE worktree off `origin/main`; fold in the two memory files sitting uncommitted on `main`
- [x] Plan + `/smh-self-audit` → `Audit verdict: GO`, four anchored findings baked into the plan
- [x] Riders B, D, E, F — script changes, each RED-first against a test that names the assertion
- [x] Riders A, C, G1 — prose changes, each guarded by a whole-glob pattern scan with a `MIN_FILES` floor
- [x] Rider G2 — **NOT RUN, deliberately**, and the acceptance row records the withdrawal rather than asserting a thing that was never going to happen
- [x] Mutation sweep declared as JSON, drawn from decisions in the code — **14 mutants at review time**
- [x] `/smh-code-review` — 5 lenses, fan-out, 21 findings confirmed and **all 21 applied**
- [x] Sweep re-declared for the guards the review fixes added — **27/27 killed**
- [x] Doors regenerated; SOP spine + sibling changelog current
- [x] Suite receipt PASS at the shipping sha, clean tree
- [x] Walkthrough + roster gate (exit 0), INDEX row, Dev Record — one record, slug from `task.yaml`
- [x] **Rider SCC-253, picked up at close-out** — the parent carried an eighth open subtask this lane never scoped, and a parent does not close over an open child

## Evidence

### RED → GREEN

The lane's strongest RED is the one the review produced, because it is a live reproduction of shipped behaviour rather than a fixture. **A1, on git 2.50.1 (Apple Git-155), in a sandbox repo:**

```
DEFECT (the form this lane shipped):
    git worktree add -q wt-bad -b claude/K-story origin/epic/K-thing
    $ git -C wt-bad status -sb | head -1
    ## claude/K-story...origin/epic/K-thing
    $ git push                       # bare, from inside the tree
    fatal: The upstream branch of your current branch does not match
    the name of your current branch.  To push to the upstream branch
    on the remote, use
        git push origin HEAD:epic/K-thing
    exit=128
  ...and push.autoSetupRemote=true does NOT rescue it (same fatal, exit=128).

FIXED (--no-track):
    git worktree add -q --no-track wt-good -b claude/K-story2 origin/epic/K-thing
    $ git -C wt-good status -sb | head -1
    ## claude/K-story2
    $ git push                       # bare, push.autoSetupRemote=true
     * [new branch]      claude/K-story2 -> claude/K-story2
    exit=0
    $ git rev-list --left-right --count @{u}...HEAD
    0	0
```

⛔ **The test that should have caught it was PINNING the defective form.** `test_shared_checkout_stays_on_main.py` asserted the base-as-operand shape and said nothing about tracking. It now scans every command and rule for an epic-based `worktree add` left tracking the epic, and accepts **either** house cure — the `--no-track` flag, or a `git branch --unset-upstream` within four logical lines, which is what `smh-plan-task.md` and `cicd-quick-dev.md` already ship.

**A2, reproduced in the operator's own shell:**

```
$ git for-each-ref --format='%(refname:short)' refs/remotes/origin/epic/*
zsh: no matches found: refs/remotes/origin/epic/*
exit=1, zero output          # and the next line reads an empty variable
$ git for-each-ref --format='%(refname:short)' 'refs/remotes/origin/epic/*'
exit=0
```

**Test-file growth, which is where the review's work is durable.** Every one of these counts is checks added to close a finding, not cases restated:

| File | Before review | After |
|---|---|---|
| `test_link_worktree_assets.py` | 24 | **42** |
| `test_jira_feed.py` | 385 | **402** |
| `test_label_tasks.py` | 120 | **129** |
| `test_shared_checkout_stays_on_main.py` | 14 | **22** |
| `test_boot_epic_branch_read.py` | 18 | **27** |
| `test_story_path_is_pinned.py` | 10 | 10 (a dead conjunct repaired, not a count) |

**GREEN at the shipping sha** — the sweep's own closing unfiltered runs, which are the runs that would have caught a mutant left in the tree: `10/10 · 402/402 · 22/22 · 27/27 · 129/129 · 42/42`, every file exit 0.

### Mutation sweep — 14 → 27, and two rows that had gone stale

The table carried **14** mutants written before the review. Every guard the review's fixes added was proven by hand at the time and nowhere durable, so the next person to touch these files would have had 14 mutants standing over 27 guards. Thirteen new rows now cover, one per defect: the story door dropping `--no-track` (A1) and `cicd-quick-dev` losing the **other** accepted cure — which is what proves the scan reads both idioms rather than one; the refspec losing its quotes (A2); the disagreement claim naming one copy (B1); the DIFFERENT-repo refusal (B6); the verified flag, the unplaceable count and the A9 refusal (A3/A9); the sub-heading label (A4); `check` deciding by length (A5); `rfind`→`find` (A8); a door dropping its `git show` line (A7); the Locked row back to one blocker (C6).

⭐ **Two existing rows had gone stale against the fixes and would have failed the sweep at load rather than reporting anything about the code** — which is the sweep working as designed, and worth recording because a stale table is the failure mode nobody looks for:

- **M6**'s `note = current.strip()` became `note = preserved_note(current)` when A8 landed.
- **M2**'s `if probe.returncode != 0 or not top:` stopped being **unique** when A3 added the `--repo` working-tree probe, which repeats that line verbatim. Widened by one line.

```
-- restore verified: bytes match, nothing was committed, and `git diff --quiet 2be3fb66` is clean --
-- sweep clean: 27/27 killed by their declared case --
```

⛔ **One mutant SURVIVED on its first attempt, and it was a real defect in my own fix.** `unplaceable += 1 → pass` stayed green because the report read `len(assets)` instead of the count it had just measured — dead state dressed as a counter. The count is load-bearing now and B2e asserts the **number** (`1 asset(s) FOUND in this repo`), not the phrase. A second mutant **crashed** instead of failing: `.index()` on a missing label raises, and a crashed run prints no `FAILED:` line, which is the only thing the sweep scores — so it would have been recorded as SURVIVED. Those two order checks compute positions first and assert second.

### Gates, run bare, at the shipping sha `ead8c831`

| Gate | Result |
|---|---|
| Enforcement suite (through `gate_receipt.py`) | `[PASS] suite exit=0 67.3s @ ead8c831` — `gates/suite.json`: `"result": "pass"`, `47/47 files passed`, `"dirty_tree": false` |
| `workflow_lint.py --toolkit-only` | exit 0 — `-- 0 error(s), 0 warning(s), 8 info --` (the 8 are a pre-existing UTF-8 BOM on `testarch-*.md`, untouched here) |
| `sop_currency.py --paths <40> --message …` | exit 0 |
| `check_maps.py --depth3-only --strict` | exit 0 |
| Declared-set drift | `{"present": true, "incomplete": [], "undeclared": [], "unimplemented": []}` — 41 declared entries against the 40-file shipping diff |
| `py_compile` (12 changed `.py`) | exit 0 — ⚠️ run **per file**; zsh does not word-split an unquoted `$PYS` |
| Link + anchor sweep (24 changed `.md`) | **0** dead relative links, **0** out-of-range `#L` anchors |
| Mutation sweep | **27/27 killed by their declared case**, restore verified against `2be3fb66` |
| Door parity | every command is a MODIFY — no add, rename or delete; `platforms:` lines untouched. The final `sync-agents -NoGlobals` moved **only** the manifest timestamp, which is the check that the per-batch syncs were complete |

### Acceptance matrix

| # | Rider | Acceptance statement | Result |
|---|---|---|---|
| A1 | SCC-254 | Boot Step 2b names the epic-branch read **and** the disagreement report | **PASS** — `test_boot_epic_branch_read.py` 27/27 |
| A2 | SCC-254 | SOP page updated | **PASS** — `sop_currency.py` exit 0 |
| B1 | SCC-255 | Without `--repo`, inside a **submodule** checkout, the script links the same assets `--repo` links | **PASS** — `test_link_worktree_assets.py` 42/42 (block B1, gitdir-file fixture) |
| B2 | SCC-255 | An **unverified resolution** exits non-zero with the resolved path; a *verified* repo with zero assets exits 0 and says so (amended from SCC-255's literal wording — Audit Finding 2) | **PASS** — `--case unverified-resolution-refuses` 5/5 |
| B3 | SCC-255 | `tests/` covers the submodule case | **PASS** — the file runs in `run_all.py` (47/47) |
| C1 | SCC-256 | Step 0.5 item 2 no longer requires HEAD on the epic branch; no command contradicts `worktree-per-story.md` | **PASS** — `test_shared_checkout_stays_on_main.py` 22/22, whole-glob scan |
| C2 | SCC-256 | SOP page updated | **PASS** — `sop_currency.py` exit 0 |
| D1 | SCC-257 | `outline` on `## Acceptance Criteria` → `### Theme` → `- **AC-n**` renders every AC | **PASS** — `--case ac-theme-subheadings` 15/15 |
| D2 | SCC-257 | A story with flat `1.` ACs still renders as before | **PASS** — same block, regression case; `story_statement` and `scrape_bucket` byte-identical across 123 AGY story files |
| E1 | SCC-258 | `mint` on a hand-note ticket replaces it with the outline and preserves the note under `PREVIOUS NOTE` | **PASS** — `--case mint-reuse-stale-description` 18/18 |
| E2 | SCC-258 | `outline` and `mint` accept the same flags | **PASS** — same block (⛔ `--case` selects a **block**; the plan's original filter named the case and returned exit 3, NO_MATCH) |
| F1 | SCC-259 | `plan` lists a `story` source for a child whose story file exists **only on the lane branch**; a tests-only branch-diff carries `tests_only: true` and ranks **after** `story` | **PASS** — `test_label_tasks.py` whole file 129/129 (it declares no `c.block()`, so every `--case` against it is NO_MATCH) |
| F2 | SCC-259 | `resolve`'s lock `detail` names **every** declared blocker — in the legend and the chat report as well as the engine | **PASS** — same file; the two door bodies fixed as review finding C6 |
| G1 | SCC-260 | The story path is named at our own call site | **PASS** — `test_story_path_is_pinned.py` 10/10 |
| G2 | SCC-260 | ~~The two out-of-repo halves are filed~~ | ⛔ **WITHDRAWN under the operator's BMAD ruling, not deferred.** Both halves were `_bmad/custom/bmad-create-story.toml` overrides; BMAD is neither edited nor overridden, so the accepted fix may not be applied and there is no defect left to anchor. Step 7 is NOT RUN, deliberately |
| H1 | SCC-253 | The `test_jira_feed.py` sentence in `.agents/scripts/INDEX.md` is replaced with the measured position: no single file is the next lever, the suite is work-bound, packing limit ~39 s | **PASS** — the clause is rewritten; `test_jira_feed.py` is third by wall clock behind `test_task_preflight.py` (~49.5 s) and `test_task_preflight_contract.py` (~46.1 s), so it cannot move the floor |
| H2 | SCC-253 | The number is cited with **how it was obtained**, so the next reader can re-run it rather than trust it | **PASS** — "the same pool run with that file excluded entirely … 59.5 s wall against 61.7 s", plus the instruction to re-run it that way before believing any successor sentence |
| H3 | SCC-253 | Enforcement suite green | **PASS** — see Z1; the receipt was re-stamped after this edit, because `.agents/scripts/INDEX.md` is not `_artifacts/` and the freshness rule correctly went stale |
| Z1 | all | Enforcement suite green at the shipping sha, through the receipt writer | **PASS** — `gates/suite.json`, 47/47, exit 0, 67.3 s @ `ead8c831` |
| Z2 | riders | The two memory files ride **this** PR, and `main` is clean | **PARTIAL, and reported rather than swept** — both memory files are in this branch's diff (`_artifacts/_memory/MEMORY.md`, `exercise-the-real-cicd-doors.md`). `main`'s working tree is **not** empty: it carries `M .claude/settings.json` and `?? .claude/hooks/allow-scratchpad.py`, written today by a **concurrent session**, unrelated to this lane and deliberately untouched. Neither path is in this diff, so the merge does not contend with them. See § Your Actions |

## Code Review (2026-08-21)

Verdict: PASS @ ead8c831

Reviewed at `c492d76`; all 21 findings applied across five commits and re-gated at `ead8c831`. **One code change landed after that stamp and is named rather than hidden:** rider SCC-253's one-paragraph correction to `.agents/scripts/INDEX.md`, picked up at close-out when the board showed an eighth open subtask. It is a doc sentence in a file no lens finding touched, it changes no behaviour, and the suite receipt was **re-stamped after it** — so the freshness rule correctly withholds the preflight's suite SKIP and the full gate runs at the landing sha. The verdict stands for the code the lenses read.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok — truncated pass, 20/36 files, withheld list named in its own output; no top-up used
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

dispositions:    per-lens: blind-hunter=2/2/0 · edge-case-hunter=3/0/0 · literal-correctness-hunter=3/1/0 · acceptance-auditor=4/5/0 · test-adequacy-auditor=5/6/0 (a multi-lens finding counts once per contributing lens). Nine further confirmed findings — A2, A3, A5, A6, A7 and C1–C4 — were surfaced during triage verification rather than credited to a single lens in the engine's return, and are counted in the 21 below but not in the per-lens tally, which would otherwise assert an attribution the record does not carry.
drift:           undeclared=0 · unimplemented=0 · incomplete=0

**Scope:** the committed `origin/main...HEAD` diff at `c492d76` — 36 files, code only. **Method:** `review_level: standard` derived at Step 0.7 (gate, rule and contract surfaces in the radius; 36 files ≫ 3), `lens_budget: standard`, `review_runtime: fan-out`. Five lenses in parallel, each in its own clean context; all five returned usable output first time, no retry, no inline rerun, no dead lens.

**The tail, in one line.** 34 findings came back across five lenses. **21 were confirmed and all 21 are fixed in this lane** — no residue ticket, no defer. 13 were dismissed: verified-wrong claims, pre-existing template behaviour, missing tests for arms that are correct today, and observations without a concrete failure. One dismissal was **promoted instead**: `repo_root()`'s `check=True` was pre-existing debt until edge-case-hunter noticed that **the SOP hunk in this very diff makes the promise the code does not keep**, which moves it into the lane. That is A9.

### Findings

| file:line | severity | failure scenario | disposition |
|---|---|---|---|
| `cicd-write-story-tests.md:32` + `worktree-per-story.md` | **critical** (A1) | A story worktree cut off `origin/epic/…` inherits the **epic** as upstream: `status -sb` reads `## claude/…...origin/epic/…` so every `0 0` check measures the wrong remote, and a bare `git push` fatals — offering the mid-story epic push G3 bans. `push.autoSetupRemote=true` does not rescue it. **A regression this lane introduced in Part C** | applied @ d077113 — `--no-track` in the fence, the rule, the SOP; the test that PINNED the defective form now scans the whole surface and accepts either house cure |
| `cicd-boot-sprint-memory.md:71` | important (A2) | `for-each-ref … refs/remotes/origin/epic/*` unquoted: zsh — the operator's shell — answers `no matches found`, exit 1, zero output, so the next line reads an empty variable and the whole SCC-254 read dies | applied @ d077113 — quoted at **three** sites; the other two (`cicd-prune-worktree`, `cicd-clean-code-audit`) were pre-existing and break identically |
| `link-worktree-assets.py:183-222` | important (A3) | `resolution verified: <repo> — this repo genuinely has none.` printed over two states it had verified nothing about: `--repo` skips `repo_root()` entirely, and a repo whose assets are **found but unplaceable** `continue`s past without incrementing either counter | applied @ 46e84fd — three kinds of zero, each named; `--repo` warns (never refuses, or the hatch closes) |
| `jira_feed.py:288-306` | important (A4) | `include_subheadings=True` swallows every `###` child of Acceptance Criteria and drops the heading text, so an `### Out of scope` bullet reaches a live board as a criterion with the one word that said otherwise deleted. Latent — 0 of 123 AGY story files carry such a child today | applied @ 8391d65 — the sub-heading renders as a `[label]` row above the bullets it introduces, emitted lazily so an empty sub-section leaves no orphan |
| `jira_feed.py:2853` | important (A5) | `check` still decided with `len(desc) < MIN_DESCRIPTION` — the exact predicate `OUTLINE_TRAILER` exists to replace — and reported `outline present (213 chars)` over somebody's hand note, **at close-out, in both doors** | applied @ 8391d65 — reads the trailer. ⛔ The severity boundary is deliberately **unmoved**: a hand note passed before and passes now, because `wf.Report.warn` returns exit 1 and would fail close-outs on every ticket nobody has minted. That is a gate change, not a review fix |
| `jira_feed.py:944` | important (A6) | The `PREVIOUS NOTE` rewrite used `Path.write_text`, which defaults to `newline=None` and translates to `os.linesep`, while the sibling `write_temp` pins `newline="\n"` on purpose — PC-only divergence in a documented two-machine system | applied @ 8391d65 — pinned. Its test **cannot go red on POSIX and says so** rather than implying coverage it does not have |
| `label_tasks.py:589` + both door bodies | important (A7) | The packet emits `{"kind","path","ref"}` and marks it grounded; both doors said "read them" and neither said how, so the agent opens `<path>` in a checkout that does not have it — ENOENT on the rung the packet just called authoritative, read as "no source" | applied @ 20e1f18 — both doors carry the two-line fence: `git show "<ref>:<path>"` when a ref is present, `cat` when it is null |
| `jira_feed.py:928-945` | important (A8) | Repeated `mint --apply` **nested** a fresh `PREVIOUS NOTE` block every run — 502 → 986 → 1498 → 2038 chars over four runs, the operator's note a level deeper each time. A retry is the normal path here: the read-back guard exits 2 on a lossy writer, which is exactly the state somebody re-runs from | applied @ 8391d65 — `preserved_note()` takes the **last** header, not the first, so it also converges a ticket this bug has already nested. Four retries now leave exactly one block, identical length each time |
| `link-worktree-assets.py:89` | important (A9) | `check=True` raises `CalledProcessError`, which `main()` does not catch, so the operator gets a raw traceback instead of the refusal **this diff's SOP hunk advertises**. Pre-existing code; the promise is not | applied @ 46e84fd — raises `ResolutionError` like every other failure here |
| `test_boot_epic_branch_read.py` | important (B1) | The scan's disagreement requirements were satisfied by the **board** sentence they were built to exclude, and then by the no-epic fallback line. Only a 10-line window separated them and nothing tested that | applied @ d077113 — the claim is measured on the sentence carrying `report both`, and must name **both** copies |
| `test_boot_epic_branch_read.py` | important (B2) | The `ANCHOR` regex accepted `git show <ref>/<path>` — git answers `fatal: ambiguous argument` — and a refspec degraded to `…/epic/` | applied @ d077113 — objectspec colon required, star and quotes required, three more mutants |
| `test_story_path_is_pinned.py` (G2 block) | important (B3) | Dead conjunct: `offenders(plant)[2] >= 0 and len(one(...)) == 1`. A count is never negative, so the left half was unconditionally true — and being on the left it ran **before** `one()` wrote the body, counting callers in whatever the previous check left behind | applied @ 20e1f18 — write first, assert second, assert the count that was meant |
| `test_link_worktree_assets.py` (B1 fixture) | important (B4) | `seed()` configures the source repo; `git submodule add` **clones** it, and local config does not travel with a clone. On a machine with no ambient identity the fixture commit failed silently and surfaced four assertions later, pointing at the script | applied @ 46e84fd — identity set on the submodule, and the commit is checked |
| `test_shared_checkout_stays_on_main.py` (C1) | important (B5) | The exemption assertion only restated the check above it, and would have gone red the day the surface stopped needing the exemption — a gate that fails on a strictly better surface | applied @ d077113 — re-derives both halves from each ruled paragraph, and passes on a surface carrying none |
| `link-worktree-assets.py:120` | important (B6) | The "is inside a DIFFERENT repo" refusal was unguarded: `if False:` in its place kept all 24 checks green, because B2a only asserts the message is **absent** | applied @ 46e84fd — B2c reaches it with a submodule gitdir whose `core.worktree` names a superproject subdirectory |
| `implementation_plan.md:172-216` | important (C1) | The `## Declared Change Set` block was unreadable to its own parser — 13 bullets `incomplete`, 15 declared files read as `undeclared` drift. Three grammar breaks: `**+**` before the op, several paths per bullet, `~~struck~~` rows | applied @ 2be3fb6 — one path per bullet, unforeseen marker after the em-dash, dropped scope as prose. Now `{"present": true, "incomplete": [], "undeclared": [], "unimplemented": []}` |
| `implementation_plan.md` (E2, F1, F2) | important (C2) | Three acceptance rows named a `--case` filter that selects **nothing**. `--case` matches a BLOCK label and exit 3 is NO_MATCH — a run that reports green having chosen zero checks | applied @ 2be3fb6 — all three corrected to runnable forms, each verified by running it |
| `implementation_plan.md` (G2 row) | important (C3) | G2 stood in the acceptance table as a **live contract row** while Step 7 says NOT RUN | applied @ 2be3fb6 — the row records the operator's BMAD ruling as a withdrawal rather than asserting a thing that was never going to happen |
| `implementation_plan.md` (Self-Audit) | suggestion (C4) | The cited tool result — "32 entries / 0 incomplete" — was true at PRE-WORK and **false at the shipping sha**, where it read 14 / 13 | applied @ 2be3fb6 — the real number, what happened in between, and the general point that a parse result is only true of the sha it was taken at |
| `label_tasks.py:381, 589` | suggestion (C5) | Two comments and a docstring described the opposite of the code: `:589` said branch-first when the code is checkout-first (and the **code** is what acceptance row F1 asks for); `:381` claimed the matching "mirrors `wf.find_story_files` exactly" when the slug rule does and the traversal does not | applied @ 20e1f18 — both corrected, with the direction of the difference stated |
| `cicd-label-tasks.md` + `smh-label-tasks.md` (legend + report rows) | important (C6) | F2's behaviour change never reached either door body: the engine emits `after A-1, A-2, A-3, A-4` while the legend still read `🔒 after <ticket>` and the report template `Locked: <key> after <key>`. The chat report is the operator-facing surface, so the shape the ticket calls the defect was still the shape being described | applied @ 20e1f18 — both rows in both doors show more than one blocker |
| `mutation_sweep.py` `startswith("KILLED")` | critical (lens) | Claimed the kill test is vacuous | **dismissed** — verified wrong: a kill line does start with `KILLED` |
| three thin launchers lost `$ARGUMENTS` | important (lens) | Claimed this diff dropped the token | **dismissed** — verified pre-existing: **zero** thin launchers carry it, and `.agents/workflows/cicd-label-tasks.md` was already a launcher on `origin/main`. Template behaviour |
| six missing-test findings (exact-match arm · `_TEST_PATH_RE` alternatives · multi-blocker `evidence` · checkout-vs-branch precedence · `_bmad/custom` ban · `U4` naming) | suggestion (lens) | Untested arms that are **correct today** | **dismissed** — missing coverage for behaviour with no defect is new scope, not a review finding |
| receipt sha ≠ HEAD | important (lens) | Claimed the receipt was stale | **dismissed** — freshness is a **tree** comparison, and only `_artifacts/` had moved |
| `story_branch()` reads local refs only · G1 glob scope · two story readers not true mirrors · `OUTLINE_TRAILER` literal duplicated | suggestion (lens) | Four claims of latent breadth | **dismissed** — pre-existing since SCC-155, or correct today with no such caller of ours; the doc half of the mirrors claim **was** fixed as C5 |

⭐ **One decision inside A4 where two lenses disagreed, and both were right.** Acceptance-auditor reproduced the defect on a synthetic doc; edge-case ran the live `acceptance_criteria` over all **123** AGY story files with only the flag varied and measured **6 files change, every one `0 → N` ACs, zero lose an AC, zero gain a non-AC**. So the defect is real but **latent — 0/123 in today's corpus**. Fixed anyway, because story files are written going forward and a false AC lands on a live board. Default chosen rather than handed back: keep the sub-heading as a **visible boundary label** instead of guessing which `###` children are AC-bearing.

⭐ **My own first A1 scan produced two false positives, and the mechanisms are worth keeping.** `cicd-quick-dev.md:74` already cures the bug with `branch --unset-upstream` three lines below — a second valid idiom my scan demanded away; and `cicd-resume.md` uses `--track` correctly while my paragraph-based regex spanned into an unrelated prose mention of `origin/epic/` four lines down. The scan was rewritten onto **logical lines** (backslash continuations joined, paragraphs abandoned) and accepts either cure within four of them. Four controls now prove both mechanisms.

### Step 0.7 — re-derivation

1. **Did anything this diff references move on `main`?** No. `origin/main` is still `038c0f1`, identical to the merge base; `git diff --name-only <base>..origin/main` returned **zero** files. No reference this diff names was moved, renamed or deleted by a landed lane, for the whole life of the lane.
2. **True overlap and `merge-tree`.** Empty. `merge-tree --write-tree` returned a clean tree oid with no conflict messages, and `merge-base --is-ancestor origin/main HEAD` is true — a pure fast-forward. No absorb was needed, so HEAD stayed at the reviewed sha and the suite receipt stayed valid.
3. **Sibling landing order.** No live sibling lane. Two worktrees only — the main checkout on `main`, and this lane. Three unmerged remote refs exist and none is a dependency: `chore/SCC-187-caller-ranking` (no file overlap), `claude/sop-document-cleanup-qk778r` (**zero tree diff vs `main`** — SCC-186's dev branch, already landed via PR #45, unpruned), and `claude/teaching-edition` (2026-08-05, 16 days stale, no worktree; it would overlap `.sync-manifest.json` and `worktree-per-story.md` only if revived, and it rebases on this, not the reverse).

### Clean-Code Gate — PASS

The machine floor is imported from the gate table above (suite receipt, `workflow_lint` exit 0, `sop_currency` exit 0, `check_maps` exit 0, link/anchor 0/0) and the ban-hunt is imported from the lens findings. Run here: `py_compile`, the comment contract, the convention table.

| Check | Result |
|---|---|
| `py_compile` (12 changed `.py`) | exit 0 |
| Committed secret / token | none |
| Debug output | none added — every `print(` in the changed scripts is operator-facing report text, which is what these scripts are for |
| Commented-out code | none |
| Broad `except` | none added |
| Hardcoded absolute / `C:/` paths | none |
| A gate that cannot fail | **this was the review's second theme, and it is closed** — B1, B3, B5, B6 were each a check that could not fail, and every guard added since has a mutant that kills it (27/27) |
| Both machines | A6 pins LF where `Path.write_text` would have written CRLF on the PC half; A2's quoting is the zsh half. No bare `python`, no `;` PATH join, no `robocopy` |
| Comment provenance | `SCC-244` plus the reason on every non-obvious block; the two **inverted** comments in `label_tasks.py` were the C5 finding and are corrected rather than deleted |
| Generated surfaces | `.agents/workflows/`, `.opencode/commands/` and the skills were regenerated by `sync-agents.ps1`, never hand-edited. The final run moved only the manifest timestamp |
| Naming law / door parity | n/a — every command is a MODIFY; nothing added, renamed or deleted |
| No personal name in `.agents/` | 0 |
| Artifacts live in the tree | plan, walkthrough, manifest, sweep table and receipt all ride this branch |

## Your Actions

**Nothing is owed.** All 21 review findings are fixed in-lane, no residue ticket was minted, nothing was deferred, and SCC-244's successor was cloned when this one went In Progress.

- [x] The merge itself — lands via this branch's PR

⚠️ **One thing to know, and it is not a task.** Two files are sitting uncommitted on the `main` checkout and are not this lane's: `M .claude/settings.json` and `?? .claude/hooks/allow-scratchpad.py`, both written today (00:06 and 04:18) by a **concurrent session** building a PreToolUse scratchpad-allow hook. This lane touches neither path, so the merge does not contend with them, and they are deliberately not swept — another session's uncommitted work is never committed under this ticket. They need a home before they are lost, and that belongs to the session that wrote them.
