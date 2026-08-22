# Twin-parity content ports — the filtered backlog

Full detail for the ports ticket. Produced 2026-08-17 by two adversarial sweeps (24 agents,
every claim re-measured against `fd22097`, each followed by a skeptic tasked to REFUTE),
then filtered through the three-question disposition test — REAL? · changes BEHAVIOUR? · in SCOPE?

**172 confirmed → 126 FIX / 45 DROP / 1 DEFER.** The 84 below are the survivors that are command
CONTENT. `_AP` removal, the close-out rebalance and the production door carry their own tickets.

⛔ Runs AFTER SCC-205 Part B (the rules-in-force vehicle) and Part E (the hoists) — a hoisted rule
plus a pointer replaces N copies, so items here shrink or vanish once Part E lands.

## SAFETY

### `DEV-01` · dev-cycle · The backtick-in-`-m` execution hazard is carried by three smh commands and by ZERO cicd commands and by no rule, so the story lane's two commit instructions (cicd-dev-story-tests.md:133, :181) are unguarded against a commit message that runs shell.

**Failure:** An agent commits `git commit -m "SCC-21.8 wire `gate_receipt.py` into Step 4.5"` — a story subject quoting a command name, which is routine — and the backticked text executes as a subshell before the commit is made. Pure shell hazard, identical on a project repo and the lobby; recorded house incident.

**Edit:** .agents/commands/cicd-dev-story-tests.md:133 — append to the Commit bullet, verbatim from smh-quick-dev.md:307-308: "⛔ **Backticks in `-m \"…\"` EXECUTE.** A message quoting a shell command runs it. Use `git commit -F <file>` whenever the message contains a backtick." Durable half (whole-family gap): add the same clause to `.agents/rules/git-policy.md`, which cicd-dev-story-tests.md:9 already cites — rule + pointer + restatement, never pointer alone (smh-clean-code-audit.md:149).

### `MERGE-01` · multi-lane · Every literal `git` call in cicd-merge's Step 4 landing loop is bare, so a cwd reset to the shared checkout (which the file itself says stands on `main`) merges the epic branch into local `main` and pushes `main`'s tip onto the shared epic branch — the exact pattern the file's own cited rule bans.

**Failure:** Bash cwd resets to the main checkout between tool calls; line 113 states that checkout stands on `main`; so line 80 `git merge origin/epic/<KEY>-<slug>` merges the epic into `main` and line 108 `git push origin HEAD:epic/<KEY>-<slug>` pushes `main`'s tip onto the shared epic branch every sibling then absorbs at 4.1 — reporting success either way.

**Edit:** .agents/commands/cicd-merge-epic-workingtrees.md:80, :106, :108 — add `-C "$TREE"` to each literal git call in Step 4 (merge, commit, push), and insert immediately before the 4.4 push: `test "$(git -C "$TREE" rev-parse --abbrev-ref HEAD)" = "claude/<JIRA-KEY>-<slug>" || { echo 'WRONG TREE — STOP'; exit 1; }`, citing `git-policy.md` §'Pin the merge TARGET' rather than restating it.

### `QD-C1` · quick-dev · cicd-quick-dev.md:36-38 authorises a chore branch to be 'merged back to main in the same session with Daniel's sign-off' while naming NO door, contradicting the same file's Done section ('never touch main') and the standing law that no agent merges to main.

**Failure:** An agent reads :37 as in-session authority, treats a spoken 'looks good' as the sign-off, and merges a chore branch straight to main with no PR, no preflight and no gate — the one write the permission layer and git-policy.md:123 exist to make impossible.

**Edit:** At .../.agents/commands/cicd-quick-dev.md:36-38 delete the clause 'merged back to `main` in the same session with Daniel's sign-off' and end the ad-hoc case at a named door: cut the branch, do the work, STOP — then `/cicd-push-e2e` (diff touches backend/ frontend/ firebase/ functions/ mobile/ .github/) or `/smh-close-task-merge-tree` (it touches none of those), invoking it IS the sign-off.

## HIGH

### `QD-C5` · clean-code · DIFFERENT DEFECT FROM THE OTHER QD-C5 ENTRIES (which are line-count recounts): cicd-clean-code-audit resolves its changed-file set from committed + staged only, while smh also reads unstaged, so uncommitted work is invisible to the cicd audit.

**Failure:** A dev runs /cicd-clean-code-audit standalone mid-story with edits saved but not staged. Step 0.5 runs exactly two commands - `git diff --name-only "${BASE}...HEAD"` (:54) and `git diff --name-only --cached` (:55) - so every unstaged changed file is absent from what :44 calls "the audit's entire universe", and the gate returns PASS on code it never read. This is a vacuous green, the exact failure the same file cites `tests-must-gate-for-real` §2 against at :58-60, and the file explicitly admits mid-work runs (":55 # plus staged, if mid-work"). Verified: `grep -nE '^git diff --name-only *(#.*)?$'` in cicd-clean-code-audit.md returns nothing; smh-clean-code-audit.md:61-63 runs all three forms.

**Edit:** .agents/commands/cicd-clean-code-audit.md - insert one line into the Step 0.5 bash block between :54 and :55: `git diff --name-only                            # plus uncommitted`, so the set matches smh:61-63.

### `DEV-02` · dev-cycle · The story lane's ONE certification run is unstamped: Step 4.5 item 3 runs the suite bare and item 4 has the agent HAND-WRITE the totals into certification-<story>.json — the exact fabricable shape gate_receipt.py exists to close — and ③ then re-runs the same suite through the writer, so the story pays for the full suite twice.

**Failure:** At Step 4.5 the agent types `{"passed":412,"failed":0}` into certification-<story>.json with nothing linking those numbers to an execution; then cicd-code-review.md:217 runs the same full suite through `gate_receipt.py run --story <id> --gate suite`. One 70s+ suite paid for twice, and only the second run is evidence.

**Edit:** .agents/commands/cicd-dev-story-tests.md:134-137 — route the one full-suite run through the writer: `python3 .agents/scripts/gate_receipt.py run --story <id> --gate suite --cwd <worktree> -- <the canonical runner>`, keep "paste the actual output" as the reading requirement, and add the STAMP-FIRST sentence from smh-quick-dev.md:318-320 (do not run the runner bare 'to check' and then re-run it through the writer). Leave item 4's certification-<story>.json in place as the DERIVED handoff — cicd-code-review.md:235 and :247 read it — but state that its totals come from the receipt, not from typing.

### `DEV-03` · dev-cycle · cicd-dev-story-tests.md:121-124 owes behavioral coverage but names ONE mutation technique (RELOCATE) and points at `tests-must-gate-for-real` Rule 4 — the superseded pointer; the rule itself says at :57-58 that the procedure is § Mutation Testing, and the whole cicd family carries zero mutation doctrine.

**Failure:** An agent at Step 4 writes a behavioral test for a gate or a hook — where there is nothing to relocate — follows the only technique the command names, cannot apply it, and improvises. That is the shape the rule at :79-82 says the relocate advice does not transfer to. And with no declared table, mutants get drawn from the agent's own cases: SCC-144 measured 14 case-derived mutants all killed vs 24 of 25 surviving from code-derived ones.

**Edit:** .agents/commands/cicd-dev-story-tests.md:121-124 — replace the single-technique sentence with the mutation obligation: declare the table BEFORE mutating (mutant · file · the NAMED case it must kill), run it as ONE sweep, draw every mutant from a decision in the source under test and never from your own cases, restore in a `finally` and re-check `git status`, run the file unfiltered once at the end, record the finished table in the walkthrough, a survivor is a finding — and repoint at `tests-must-gate-for-real` **§ Mutation Testing**, not Rule 4. Do NOT mandate `mutation_sweep.py`: it is coupled to the lobby harness (`--case`, `_harness.NO_MATCH` exit 3, `FAILED:` lines) and does not run against pytest/vitest.

### `DEV-04` · dev-cycle · The story lane records `review-runtime:` at exactly one point — inside the review step it describes — which is the circularity the SCC-203 ruling bans; cicd-code-review.md:103-105 names this gap against itself in its own body.

**Failure:** ③ is the only recording point, so the header is written from the roster it is supposed to independently check: `walkthrough_roster.py`'s contradiction test (`inline` header + a lens reporting `ok`) can never fire, because the header is derived from those very states. If ③ skips the step the story walkthrough gets no header at all.

**Edit:** .agents/commands/cicd-dev-story-tests.md — add Step 0.8 mirroring smh-quick-dev.md:65-88: probe whether a subagent tool exists in this runtime, restate the SCC-203 capability-not-policy ruling and "subagents are the DEFAULT, invoking a review IS that request", and write `review-runtime: fan-out|inline` as the first line of the walkthrough header (add it to the Step 5 checklist at :157-164), noting `walkthrough_roster.py` blocks close-out when the roster disagrees.

### `DEV-05` · dev-cycle · Neither ① nor ② requires the RED output to be pasted or diagnosed — ①'s Done asks only for "confirmation they fail as expected" and ②'s `## Evidence` is GREEN certification totals plus a SHA — so a red that died in setup is indistinguishable from one that failed its assertion.

**Failure:** ① writes a red whose fixture raises (a missing conftest env var, a bad import); it reports "fails as expected"; ② drives it green by fixing the fixture, and a test that never asserted anything ships as an acceptance proof. The house has this recorded (memory: red-test-can-die-before-its-assertion) and neither command carries it.

**Edit:** .agents/commands/cicd-dev-story-tests.md Step 3 (before :99's drive-to-green) — add: "Run the ① reds and paste the actual RED output. Then read WHICH LINE RAISED — a red that dies in setup looks identical to one that fails its assertion, and only one of those is a real red." And extend the `## Evidence` clause at :160 so each AC carries RED output then GREEN output, not GREEN totals alone (mirrors smh-quick-dev.md:281-282 and :414).

### `DEV-06` · dev-cycle · Step 2 invokes `/cicd-self-audit`, requires persisting its `Audit verdict:` line, and then says "go straight on … no second gate" — the verdict's VALUE is never read, so a mechanically produced NO-GO is written into the plan and stepped over.

**Failure:** `/cicd-self-audit` emits `Audit verdict: GO | NO-GO` (cicd-self-audit.md:173, defaulting to NO-GO at :15/:121). The agent appends `Audit verdict: NO-GO` into the plan, reads :73-74's "Then go straight on (Step 2.5 → 3 → 4 → 5) — no second gate", and implements against a plan its own audit refused. `grep -c NO-GO` on the command = 0.

**Edit:** .agents/commands/cicd-dev-story-tests.md:70-74 — after the persist instruction add: "⛔ Read the `Audit verdict:` line. **A NO-GO stops the lane** — fix the plan and re-audit; do not proceed on a NO-GO and do not re-run it hoping for a different answer." And narrow :86-87 so "without further stops" is explicitly conditional on a GO verdict. (smh-quick-dev.md:184-186.)

### `MERGE-02` · multi-lane · cicd Step 3's overlap map has no modify/delete class, so when a landed sibling's deletion meets this lane's edit at the 4.1 absorb, the plan the command tells the agent to follow has no row for it.

**Failure:** Lane A deletes a file Lane B edited; at Step 4.1 git raises modify/delete; line 82 says 'resolve per the Step 3 plan' and the only nearby bullet is 'Code overlaps — read both hunks, pick an owner', which cannot apply because one side has no hunks; the agent accepts the deletion and the surviving content is proven to exist nowhere.

**Edit:** .agents/commands/cicd-merge-epic-workingtrees.md:61-76 — add a **modify / delete** class (one lane deletes a file another lane edited): ordering does not rescue it, both orders end with the file deleted; rule which side wins and prove the surviving content exists at its destination (`git show <branch>:<path>`, or a named replacement) BEFORE accepting the deletion. Land it in the SAME table edit as MERGE-07, not a second pass.

### `MERGE-03` · multi-lane · The multi-lane door — the one running with the most trees open — is the only door that never runs the mechanical preflight; its Step 2 is two prose bullets while the equivalent script exists and the single-lane door runs it as an AUTOMATIC step.

**Failure:** A lane whose verdict is stale against its own tip, whose worktree is a HUSK, or whose two status surfaces disagree passes cicd Step 2's eyeball read (`git status` clean + a verdict lookup) and enters the landing order; `closeout_preflight.py` would have exited 2 on every one of those and never runs, because Step 4.3 delegates only '/cicd-update-sprint-memory Steps 1–4 + 6' and the preflight is that command's Step 0.6.

**Edit:** .agents/commands/cicd-merge-epic-workingtrees.md:52-59 — replace the prose bullets with a per-lane `python3 .agents/scripts/closeout_preflight.py --story <id> --project <PROJECT> --fetch --branch claude/<JIRA-KEY>-<slug> --worktree <tree>`, state exit 2 = BLOCKED (that lane leaves the landing order) and exit 1 = warnings that are read not ignored, and require the echoed target line to be checked against the lane you meant. Keep the existing eligibility sentences below it.

### `MERGE-07` · multi-lane · cicd's overlap map is three prose bullets and omits three classes with distinct resolution laws — rewrite-vs-edit (re-author; both automatic resolutions are wrong), generated (regenerate, never hand-merge), and gate-or-script (rule which version wins BEFORE merging).

**Failure:** A lane that rewrote a doc another lane edited a paragraph of falls to 'Code overlaps — read both hunks, pick an owner', and the paragraph the edit changed no longer exists, so both resolutions lose content; a generated manifest hand-merged produces a file no regeneration would ever produce; and a shared gate file gets 'note which suites re-run' when what is needed is a ruling on which VERSION of the gate wins.

**Edit:** .agents/commands/cicd-merge-epic-workingtrees.md:61-76 — convert the three bullets into a class table in ONE edit shared with MERGE-02: keep Code overlaps · Board files (= smh's ledger, already correct) · Test surfaces; add **rewrite vs edit**, **generated**, **modify / delete** (MERGE-02); and promote the gate half out of Test surfaces into **gate or script** — state which version must win before merging and re-run the gate that file feeds after each landing that touches it.

### `MERGE-08` · multi-lane · cicd Step 4.3 delegates '/cicd-update-sprint-memory Steps 1–4 + 6', and the Jira transition plus Dev Record live in that command's Step 4.5 — so no lane landed through the multi-lane door ever moves its ticket or files a Dev Record, while the command's preamble promises nothing is left owed.

**Failure:** Four lanes land through this door: each story flips to `done` in the frontmatter and `sprint-status.yaml`, the code reaches the epic branch, the tree is pruned — and every one of the four Jira tickets is still sitting in In Review with no Dev Record, with the tree that held the evidence already deleted at Step 6.

**Edit:** .agents/commands/cicd-merge-epic-workingtrees.md:100 — change 'Steps 1–4 + 6' to 'Steps 1–4, **4.5** + 6' and state 4.5 runs per lane at ITS landing, never batched: `acli jira workitem transition --key <KEY> --status "Done" --yes`, `jira_feed.py devrecord --key <KEY> --story <id> --project <PROJECT> --closing --apply`, then `jira_feed.py check --key <KEY> --story <id>` exit 0. Add ticket state to the Done report at :140. Do NOT import smh's `check-actions`/`finish` contract — cicd transitions via acli and cicd-code-review.md already governs `## Your Actions`.

### `PAIR-01-PLAN-FIRST-GATE-UNCITED` · planning · cicd-create-epic-sprint.md writes two files the plan-first gate names as project files (epics.md content and `_bmad-output/implementation-artifacts/sprint-status.yaml`) while citing no rule pointer to `000-PLAN-FIRST-GATE.md`, and its one pre-Step-3 checkpoint never says STOP — it says "then proceed to Step 2" — so nothing holds the agent before the board is written.

**Failure:** Failure: an agent runs the command, prints the epic + story digest at line 36 as the FLOW CONTRACT's "no further menus" instructs, and continues in the same turn to Step 2 which writes sprint-status.yaml — a named project file — with no operator word between them. The same file proves the omission is a defect rather than a style: Step 3 at :100 says "**STOP and wait** for the decisions. This is the hard stop", checkpoint 1 says nothing of the kind.

**Edit:** .agents/commands/cicd-create-epic-sprint.md — (a) insert a `> **Rules in force for this command:**` block after the H1 at :6 citing `000-PLAN-FIRST-GATE.md`, `artifacts-always-first.md`, `git-policy.md`, `jira.md`, `worktree-per-story.md`, `work-consolidation.md` and the already-used `smh-target-resolution.md` (shape at smh-plan-task.md:8-20); (b) rewrite the checkpoint at :36-37 to present the digest and then **STOP and wait**, naming the operator's word as what opens Step 2.

### `PAIR-05-NOTHING-IT-PRODUCES-IS-COMMITTED-OR-PUSHED` · planning · epics.md, sprint-status.yaml and the test-design artifact are written and never committed or pushed — only the bare epic branch is pushed — so the epic branch tip that every story worktree is cut from contains none of the kickoff's output. (Story files are NOT written here; drop them from the list.)

**Failure:** Failure: kickoff ends, the operator runs `/cicd-write-story-tests 17.1`, whose Step 0.5 opens `.claude/worktrees/story-17-1-…` off `epic/<KEY>-<slug>` — a branch whose tip is bare origin/main — so `bmad-create-story` reads an epics.md with no Epic 17 section and sprint-status.yaml with no epic rows, and the kickoff's work exists only as dirty files in the shared checkout of one machine. git-policy.md:240-248 requires `git status --short` empty + `0 0` per repo to call work finished, and its single exception at :250-252 (a story branch mid-flight) does not cover kickoff.

**Edit:** .agents/commands/cicd-create-epic-sprint.md — after Step 2 and again after Step 3 records the P-levels: `git -C "$PROJECT_ROOT" add <epics.md> <sprint-status.yaml> <test-design file>` (explicit paths; ⛔ never `git add -A`, git-policy.md:293-296), `git -C "$PROJECT_ROOT" commit -F <message-file>` with the epic's Jira key leading the subject, `git -C "$PROJECT_ROOT" push origin HEAD:epic/<JIRA-KEY>-<slug>`; close the Done section with the git-policy.md:243-244 check (status empty + `0 0`).

### `PAIR-07-GIT-CALLS-NOT-BOUND-TO-THE-RESOLVED-REPO` · planning · All three git calls (lines 48-50) are bare — none binds `-C` to the `PROJECT_ROOT` Step 0 resolved — so they act on whatever tree the shell is standing in, which is the lobby checkout.

**Failure:** Failure: with cwd in the command centre (the documented default — `bash cwd resets to the MAIN checkout`), `git checkout -b epic/AVCH-13-… origin/main` cuts and CHECKS OUT an AVCH-named branch inside Sudo_Hatter_Command, moves the lobby's HEAD off main under whoever is standing there, and `git push -u origin epic/…` publishes it to the wrong remote — while the target project gets no epic branch, so cicd-write-story-tests Step 0.5 later reports the epic branch missing. Step 0's binding at :19-21 is to PATHS only and a bare `git checkout -b` contains no path, so that sentence cannot reach it.

**Edit:** .agents/commands/cicd-create-epic-sprint.md:47-51 — `git -C "$PROJECT_ROOT" fetch origin` / `git -C "$PROJECT_ROOT" checkout -b epic/<JIRA-KEY>-<slug> origin/main` / `git -C "$PROJECT_ROOT" push -u origin epic/<JIRA-KEY>-<slug>`, plus `BRANCH=$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD); echo "Epic branch: $BRANCH"` so the cut is proved from output.

### `PAIR-05-NOTHING-IT-PRODUCES-IS-COMMITTED-OR-PUSHED` · planning · Same defect, re-filed after verification: nothing the kickoff produces is committed or pushed, and story files correctly drop out of the list because cicd-write-story-tests owns them.

**Failure:** Identical defect and identical location to the earlier entry carrying this id — ONE edit closes both. Kept as FIX rather than dropped because its correction (story files are not written here) and its grounding (git-policy.md:240-252 is cicd-side law, not imported smh law) are the versions that should be applied.

**Edit:** As the earlier PAIR-05 entry — no second edit; fold this entry's correction into that one.

### `PAIR-07-GIT-CALLS-NOT-BOUND-TO-THE-RESOLVED-REPO` · planning · Same defect, re-filed after verification: lines 48-50 are bare git calls with no `-C "$PROJECT_ROOT"`.

**Failure:** Identical defect and identical location to the earlier entry carrying this id — ONE edit closes both. It adds the cicd-side grounding (cicd-code-review.md:63's `git -C ""` note, and the 11-vs-0 per-file count) that makes the fix behaviour-identical when cwd is already correct.

**Edit:** As the earlier PAIR-07 entry — no second edit.

### `QD-C2` · quick-dev · cicd-quick-dev.md:37 tells the ad-hoc lane to work with `no worktree`, contradicting worktree-per-story.md (every commit-producing lane isolates, SCC-62) and the same file's own :20-21 and :38-39.

**Failure:** An agent takes the ad-hoc branch in the shared checkout, commits there beside three live story lanes, and either sweeps a sibling's dirty file into its commit or has its own work swept into theirs — the exact SCC-58/SCC-61 pair the rule was written for.

**Edit:** At /Users/sudohatter/Sudo_Hatter_Command/.claude/worktrees/SCC-197-wave2-twin-parity/.agents/commands/cicd-quick-dev.md:37 delete the words `no worktree,` and give the ad-hoc case the same tree the story case gets: `git worktree add .claude/worktrees/<slug> -b chore/<KEY>-<slug> origin/main`, `branch --unset-upstream`, and echo BRANCH from `rev-parse`.

### `QD-C3` · quick-dev · cicd-quick-dev never states that a fired EJECT re-arms the plan-first gate and never binds 000-PLAN-FIRST-GATE.md, though two rules say the gate re-arms on eject.

**Failure:** Step 1.5 fires, the agent hands off to the full lane still holding the plan exemption its invocation granted, and writes code in ① with no `implementation_plan.md` and no literal `approved` — the gate is bypassed exactly where it was supposed to come back on.

**Edit:** Add `.agents/rules/000-PLAN-FIRST-GATE.md` to the rules-in-force block at .../.agents/commands/cicd-quick-dev.md:8-14, and append one line after :63: 'A fired tripwire re-arms the plan-first gate — from here the work needs an approved `implementation_plan.md` like any other lane.'

### `QD-C5` · quick-dev · cicd-quick-dev is the only review-running lane in either family that bypasses the house review engine — it calls `bmad-review-adversarial-general` directly, so its `Verdict:` line rests on one unverified subagent with no lens roster and no triage.

**Failure:** A /cicd-quick-dev run writes `Verdict: PASS @ <sha>` into the story walkthrough from a single hand-rolled reviewer — no verification pass, no four-bucket triage, no `lenses_run:` roster — and /cicd-update-sprint-memory reads that line as the review of record before flipping the story to `done`.

**Edit:** At .../.agents/commands/cicd-quick-dev.md:75-77 replace the `bmad-review-adversarial-general` bullet with an invocation of the `code-review-engine` skill, passing REPO/WORKTREE/DIFF/HEAD_SHA, `review_mode: full` on the story lane and `no-spec` on the ad-hoc lane, `lens_budget: standard`, and `review_runtime` from QD-C4's probe. ⛔ Do NOT take the finding's proposed action of delegating to `/cicd-code-review`: that command is `platforms: [opencode, antigravity]` and its AP twin `[claude, opencode]`, while cicd-quick-dev is all four — the skill is platform-neutral, the command is not.

### `QD-C2` · quick-dev · Same defect as the earlier QD-C2 entry — cicd-quick-dev.md:37's `no worktree` contradicts worktree-per-story.md — with the extra, verified point that artifacts-always-first.md makes this command's plan-skip carve-out CONDITIONAL on the worktree existing.

**Failure:** Two lens copies of one defect; one edit satisfies both. The extra half is real and raises the stakes: with no worktree the plan-skip exemption at artifacts-always-first.md:337-339 has lost one of its four named guards, so the lane is running unplanned AND unisolated.

**Edit:** Same single edit as QD-C2 above (delete `no worktree,` at :37 and add the worktree mechanics to Step 0.5). Do not apply twice.

## MEDIUM

### `QD-C1` · clean-code · cicd-clean-code-audit has no soft-gate awareness anywhere in its scan list or its verdict ladder, while smh-clean-code-audit scans for it (:153) and makes a new gate that cannot fail a FAIL trigger (:188-189).

**Failure:** A story diff adds `continue-on-error: true` to a workflow test job, or a helper script whose check is piped to `tail` so the pipe's exit code is returned. Run standalone, /cicd-clean-code-audit's Step-1 scan list (:82-87 = bare except, `any`, secret, debug prints, commented-out code) has no soft-gate row and its FAIL rule (:135 = machine check errors on a changed line, a §2 banned pattern, a secret) cannot reach it - the audit returns PASS on a gate that can never go red. Verified absent: grep for `continue-on-error`, `Run gates bare` and `cannot fail` (as a gate) in cicd-clean-code-audit.md all return 0.

**Edit:** .agents/commands/cicd-clean-code-audit.md:87 - append one scan row after the commented-out-code bullet: "- a gate that cannot fail: `continue-on-error`, `|| true`, blanket `.skip`/`xfail`, a warn-only hook, or a check whose empty input, missing tool, or piped exit code reads as PASS - run gates bare (`tests-must-gate-for-real` §3)". And :135 - extend the FAIL bullet to "... or a secret, or a NEW gate the diff adds that cannot fail". Keep it scoped to gates the diff ADDS: a pre-existing soft step carrying a named owner + a tracked expiry stays legitimate at the CONCERNS floor per tests-must-gate-for-real §3, and /cicd-code-review.md:268-272 already owns that change-triggered scan.

### `QD-C2` · clean-code · cicd-clean-code-audit never scans the diff for a hardcoded absolute / drive-letter path or for bare `python`, though code-standards §5 states the Paths rule and §3/§6 state the interpreter rule - smh-clean-code-audit scans for both (:113-114).

**Failure:** A story commits `open('C:/Users/.../config.json')` in backend code, or a README/shell step spelled `python scripts/seed.py`. ruff and pyrefly flag neither; cicd's Step-1 scan list (:82-87) is explicitly scoped to the §2 banned patterns and Step 2's judgment lists (:93-110) have no path or interpreter question, so the audit reports PASS against a standard its own :15 says it must not audit from memory. Verified: `grep -c 'Path(__file__)'` = 0 and `grep -c 'C:/'` = 0 in cicd-clean-code-audit.md; its only `python` mentions (:66-67, :71) instruct the AUDITOR which interpreter to run, never scan the diff.

**Edit:** .agents/commands/cicd-clean-code-audit.md:87 - append two scan rows: "- a hardcoded absolute path or a drive-letter (`C:/`) path where `Path(__file__).parent` belongs (`code-standards` §5)" and "- bare `python` in a committed script or a documented command - the house interpreter is the venv (`code-standards` §3, §6)". Do NOT copy smh's `robocopy` / `chmod` / `|`-PATH-join row or its "the Mac has only python3" wording; those are lobby-shaped.

### `QD-C3` · clean-code · cicd-clean-code-audit has no "never sweep another session's memory into this diff" guard; smh-clean-code-audit carries it at :71-73, and since SCC-73 the project subject has its own tracked `_artifacts/_memory/` store too.

**Failure:** A story worktree has a dirty `_artifacts/_memory/<file>.md` written by a parallel session. cicd Step 0.5's `git diff --name-only --cached` (:55) pulls it into what :44 calls "the audit's entire universe"; Step 2 audits it; Step 3's "Apply the fixes you can make safely" plus "Commit fixes inside the story worktree with explicit paths" (:139, :146) then commits another session's memory under this story. Verified live in the subject: `git -C Projects/AGY_AVIATIONCHAT ls-files _artifacts/_memory` lists MEMORY.md and per-fact files as TRACKED; cicd-boot-sprint-memory.md:39-43 reads that store ("Step 1.5 - Read THIS project's memory store (SCC-73)") and cicd-update-sprint-memory writes it. `grep -c '_artifacts/_memory'` in cicd-clean-code-audit.md = 0.

**Edit:** .agents/commands/cicd-clean-code-audit.md - insert immediately after the empty-set STOP at :60: "⛔ **Never sweep another session's memory into this diff.** Dirty files under `PROJECT_ROOT/_artifacts/_memory/` belong to whatever wrote them (SCC-73 - the store is two-tier and this project has its own); report them as present and out of scope. They are parked or left, never committed under this story." Keep it inline in the step list, not hoisted to a rule pointer.

### `QD-C1` · clean-code · Same defect as the earlier QD-C1 entry: no soft-gate row in cicd's Step-1 scan list and no gate clause in its FAIL ladder.

**Failure:** Same failure sentence as the first QD-C1 entry; one edit satisfies both. This entry's evidence is the stronger of the two (it checks smh:190-191 for internal tension in the verdict ladder and finds none) - use its quotes, apply the single edit once.

**Edit:** Identical to the first QD-C1 entry - .agents/commands/cicd-clean-code-audit.md:87 (scan row) and :135 (FAIL trigger, scoped to gates the diff ADDS). Do not apply twice.

### `QD-C2` · clean-code · Same defect as the earlier QD-C2 entry: no hardcoded-path scan and no bare-`python` scan in cicd's diff scan list.

**Failure:** Same failure sentence; one edit satisfies both. This entry is the more honest of the two - it says out loud that only the hardcoded-path half is backed by code-standards §5, which is what I verified.

**Edit:** Identical to the first QD-C2 entry - two rows appended at .agents/commands/cicd-clean-code-audit.md:87. Do not apply twice.

### `QD-C3` · clean-code · Same defect as the earlier QD-C3 entry: cicd-clean-code-audit is missing the "never sweep another session's memory into this diff" guard.

**Failure:** Same failure sentence; one edit satisfies both. This entry carries the better proof that the hazard is live in the project subject (cicd-boot-sprint-memory reads the store, cicd-update-sprint-memory writes it), so its evidence is the one to cite.

**Edit:** Identical to the first QD-C3 entry - insert the guard after the Step 0.5 empty-set STOP at .agents/commands/cicd-clean-code-audit.md:60. Do not apply twice.

### `D7` · close-out · git-policy.md's write-gate row at :70 answers `main` in a project repo with '/cicd-push-e2e' and gives no chore carve-out, contradicting :36-40, which hands the non-deployable chore lane in a DEPLOYING repo to /smh-close-task-merge-tree.

**Failure:** An agent routing off the write-gate table sends a docs-only `chore/AVCH-x` branch to /cicd-push-e2e; an agent routing off :36-40 sends the same branch to /smh-close-task-merge-tree - one branch, two doors, two different ceremonies, and D4's fix cannot quote the rule to settle it.

**Edit:** .agents/rules/git-policy.md:70 - carve the chore lane out of the `main` row so it matches :36-40: chore with nothing deployable in the diff -> /smh-close-task-merge-tree; chore with a deployable path -> /cicd-push-e2e; epics -> /cicd-push-e2e in project repos, a PR in this repo. Drop the finding's action (b): what a PR against a project repo with no `main-write-gate` means is already assigned elsewhere by :84-86 ('each project's own ticket, in its own tracker') - do not decide it in this lane.

### `QD-C2` · code-review · cicd-code-review.md:369-370 asserts that `jira_feed.py` mechanically refuses a close-out on a ceremony action row "at check-actions and again at finish" — on the story lane no command ever invokes either verb, and closeout_preflight.py has no ceremony detector, so the reviewer is told a machine will catch what only they can catch.

**Failure:** A reviewer leaves a ceremony row ("click Merge", "re-invoke the door") in a story walkthrough's `## Your Actions` believing a script will refuse the close-out; /cicd-update-sprint-memory calls only `jira_feed.py devrecord` (:169) and `jira_feed.py check` (:191), neither of which reads ceremony_rows, so the row lands and the operator is handed the ceremony's own steps.

**Edit:** .agents/commands/cicd-code-review.md:369-370 — replace "`jira_feed.py` **refuses** a close-out on such a row, at `check-actions` and again at `finish`" with the story-lane truth (the rule is the reviewer's to hold here; the mechanical refusal lives on the Task lane's door). Do NOT wire `check-actions` into cicd-update-sprint-memory — that rewrites another command's close-out sequence and is outside this lane.

### `QD-C3` · code-review · cicd-code-review resolves no diff as a first-class step — no `git status --short`, no "committed work only" rule, no echoed file count — and its only empty-diff STOP sits at :293 inside Step 3.5, after the engine fan-out, the acceptance audit and the whole test gate have run.

**Failure:** A story worktree with uncommitted work gets reviewed and PASSes at a HEAD_SHA that does not contain it (the twin explicitly scopes the review to committed work, smh-code-review.md:58-60), and a resume that binds the wrong tree runs Steps 1, 1.5 and 3 on an empty diff before :293 finally stops it.

**Edit:** Add a `## Step 0.6 — Resolve the diff` between Step 0.5 (:37) and Step 0.7 (:45) in .agents/commands/cicd-code-review.md, porting smh-code-review.md:55-63 with the story lane's ref: `git -C "$WORKTREE" diff --name-only "origin/$EPIC"...HEAD` + `git -C "$WORKTREE" status --short   # anything uncommitted (report it; it is not reviewed)`, echo the file count, "An empty set is a STOP, not a pass." Keep :293 as the gate-local restatement. NEVER substitute origin/main for the epic ref (SCC-165).

### `QD-C5` · code-review · cicd-code-review carries no "a check that cannot fail is a finding" guard anywhere — and, unlike the twin, no `Rules in force` block that would load `tests-must-gate-for-real` § Mutation Testing — so a story that ships a one-sided gate passes. (The "run gates bare" half of the finding is NOT a defect on this lane.)

**Failure:** A story adds a CI guard or shell check; the reviewer confirms it allows the good case, never proves it rejects the bad one, and cicd's Step 3 guard list (:255-264 — CI-entrypoint audit and grandfathering only) gives no reason to look, so a gate that can never fail ships under a PASS verdict.

**Edit:** Add one bullet to .agents/commands/cicd-code-review.md Step 3's guard list (:255-264): "**A check that cannot fail is a finding.** If the diff adds a gate, a guard or a CI step, prove it **rejects** the case it must reject *and* **allows** the case it must allow — `tests-must-gate-for-real` § Mutation Testing (INVERT the decision). One half is not a gate." Do NOT add a "run gates bare" line.

### `QD-C6` · code-review · cicd's engine-input `DIFF` row (:149) carries no re-take instruction and no "committed work only", so the diff computed in Step 0.7 before the absorb is what reaches the engine — even though the same step orders the GATE re-run after absorbing.

**Failure:** Step 0.7 absorbs `origin/$EPIC` at :95-97; the reviewer passes the `/tmp/mine.txt` diff taken at :72 (pre-absorb), so the engine reviews a tree that no longer exists and every conflict resolution the absorb produced goes unreviewed while the verdict cites the post-absorb sha.

**Edit:** .agents/commands/cicd-code-review.md:149 — "| `DIFF` | the story's diff, **re-taken in that worktree after Step 0.7 absorbed `origin/$EPIC`** — committed work only |", plus the ⚠ note after the table mirroring smh-code-review.md:176-178 with `origin/$EPIC` substituted for `main`.

### `QD-C1` · code-review · cicd-code-review.md:366-372 is the Task lane's ceremony paragraph byte-for-byte: it names `/smh-close-task-merge-tree --after-merge <KEY>` and blesses `- [x] The merge itself — lands via this branch's PR` as the one legitimate merge-shaped row, on a lane that has no PR and lands by pushing to `epic/<KEY>-<slug>`.

**Failure:** A story reviewer follows :371-372 and writes (or preserves) a PR ledger row in the story walkthrough describing a landing mechanism the lane does not have, while the paragraph points the operator at a Task-lane door the story flow never invokes — contradicting the file's own "Stay in lane" (:382-384).

**Edit:** In .agents/commands/cicd-code-review.md:366-372 keep the subject-neutral principle (the operator's decision to proceed is the sign-off; never hand them the ceremony's own steps) and swap the three Task-lane instances for the story lane's real ones ("land the branch on the epic", "re-invoke /cicd-update-sprint-memory", "run the merge gate"); delete the `this branch's PR` ledger-row sentence entirely.

### `QD-C2` · code-review · Same defect: the false mechanical-backing sentence at cicd-code-review.md:369-370.

**Failure:** Same failure as the earlier QD-C2 entry; one edit covers both. Its option (b) — adding `jira_feed.py check-actions` to /cicd-update-sprint-memory's pre-flip sequence and gating Step 7's push on it — is rejected: that rewrites a different command's close-out contract and is outside this parity lane.

**Edit:** None beyond the earlier QD-C2 edit at .agents/commands/cicd-code-review.md:369-370.

### `QD-C3` · code-review · Same defect: no early diff resolution, no uncommitted sweep, empty-diff STOP arriving only at Step 3.5.

**Failure:** Same failure as the earlier QD-C3 entry; one Step 0.6 edit covers both. Its "no diff-resolution step at all" wording overstates — the diff IS computed at :72 for the overlap sweep — but the underlying defect (no count, no emptiness check, no committed-only scoping, no status sweep) is real.

**Edit:** None beyond the earlier QD-C3 edit (new Step 0.6 in .agents/commands/cicd-code-review.md).

### `QD-C4` · code-review · cicd's Step 4 verdict list (:299-349) has no bullet for Step 1.5's acceptance matrix, and none for Step 0.7's three written answers, so both die in chat — the twin records both (smh-code-review.md:357 and :359-361).

**Failure:** Step 1.5 orders "every item paired with the assertion that proves it" (:195-198) and Step 0.7 orders three answers "in writing" (:90-94), but neither names a destination; /cicd-update-sprint-memory then reads a walkthrough that carries a Verdict with no acceptance evidence and no record of whether an epic-mate moved a file this story depends on.

**Edit:** Add two bullets to .agents/commands/cicd-code-review.md's Step 4 list, after the findings-table bullet (~:338): "- the acceptance matrix from Step 1.5 — every acceptance item → its proving assertion;" and "- **Step 0.7's re-derivation**, in three lines — what the epic branch moved under this diff, the true overlap + `merge-tree` result, and any sibling-lane landing-order dependency. 'Nothing moved' is a reportable result; silence is not."

### `QD-C5` · code-review · Same defect: the missing "a check that cannot fail is a finding" guard in cicd.

**Failure:** Same failure as the earlier QD-C5 entry; one bullet covers both. Its second half (add a pipe/exit-code clause) is rejected on the same measurement: gate_receipt.py runs shell=False (:201-202) and cicd routes every gate through it (:214), so the pipe hazard does not exist on this lane.

**Edit:** None beyond the earlier QD-C5 edit (one guard bullet in Step 3 of .agents/commands/cicd-code-review.md).

### `DEV-09` · dev-cycle · cicd-dev-story-tests.md carries no EJECT tripwire and names no door to hand work to — `grep -ci 'eject|tripwire|correct-course'` = 0 — while both sibling dev commands have one (cicd-quick-dev.md:54-60, smh-quick-dev.md:383-396).

**Failure:** Mid-Step-3 the agent finds the story's ACs no longer describe what can be built, or a Step 4 finding is bigger than a trivial patch. Step 2.5's question gate is closed (it fires only before code) and no door is named, so the agent silently re-scopes inside the story instead of routing to `bmad-correct-course`. The lane has no defined way to stop after implementation starts.

**Edit:** .agents/commands/cicd-dev-story-tests.md — add Step 3.5 modelled on smh-quick-dev.md:383-396 with the story-lane conditions: the work is Task-shaped (no story id, no board row) → `/smh-quick-dev`; the audit returned NO-GO and the plan cannot be fixed without re-scoping → `bmad-correct-course`; the built scope has diverged from the story's ACs; a finding is bigger than a trivial patch. Close with "Report the one-line reason; keep the worktree and everything written. Discard nothing." Land this in the same edit as DEV-06 — the NO-GO condition is shared.

### `DEV-10` · dev-cycle · The story lane reads sibling lanes only at REVIEW time (cicd-code-review.md:92-93), never before the first edit — cicd-dev-story-tests.md:33-38 runs `git worktree list` for the single purpose of re-entering THIS story's own tree.

**Failure:** Two `claude/*` lanes in the same epic both edit `backend/app/routes/chat.py`; each lane's uncommitted work is invisible to the other's `grep`; the collision surfaces at ③'s absorb or at the epic merge, after both stories are fully built. The house recorded this (memory: lane-collision-is-gates-not-files). The timing is the defect, not the question — smh asks it at Step 0.5, before the first edit.

**Edit:** .agents/commands/cicd-dev-story-tests.md Step 0.6 (:33-38) — extend with the sibling-lane read, mirroring smh-quick-dev.md:139-149: enumerate the other `claude/*` trees under `PROJECT_ROOT`, run `git -C <each-other-tree> diff --name-only <epic-branch>...HEAD` and `git -C <each-other-tree> status --short`, and name any overlapping file as a landing-order dependency carried into the plan — "say which lane should land first and what happens to your work if it does not."

### `DEV-11` · dev-cycle · cicd-dev-story-tests.md contains no fetch, no merge and no absorb anywhere, so a story tree re-entered on a fresh chat is planned and built against whatever base it was cut from; the cicd family's only absorb is at review time (cicd-code-review.md:95-97).

**Failure:** A `claude/*` tree cut at epic kickoff and picked up days later is branched from an epic branch its sibling lanes have since moved. The agent plans against stale files and builds; the conflicts land at ③'s absorb, after the work exists — the exact late position cicd-code-review.md:96-97 says a verdict must not be measured before.

**Edit:** .agents/commands/cicd-dev-story-tests.md Step 0.6, on the reuse path (:35-37): "Reusing a tree cut earlier? Absorb the EPIC branch FIRST, before the first edit — `git -C <tree> fetch origin && git -C <tree> merge --no-edit <epic-branch>`. Conflicts here are cheap and yours; the same conflicts at ③ are on the epic branch's doorstep." (smh-quick-dev.md:105-113; only the branch to absorb differs, which is subject-forced.)

### `DEV-12` · dev-cycle · No cicd command LINKS a worktree's gitignored assets — `link-worktree-assets.py` appears exactly once in the family, at cicd-close-workingtree.md:228 calling `--unlink` — so the project lane unlinks assets it was never told to link.

**Failure:** A story worktree opens with no `.env`, no `backend/.venv`, no `auth_keys/`, no `node_modules`. Step 3's scoped suite and Step 4.5's certification run cannot execute in that tree; the agent either fails outright or falls back to running the suite in the main checkout, which certifies the wrong tree. The script's own docstring names this: pytest, uvicorn, `next dev` and the Firebase emulators resolve these RELATIVE TO CWD.

**Edit:** .agents/commands/cicd-dev-story-tests.md Step 0.6 — after the tree is resolved (reused or newly opened at first edit) add: `python3 .agents/scripts/link-worktree-assets.py <PROJECT_ROOT>/.claude/worktrees/<slug>` (PC: `python`); it is idempotent, so a resumed lane re-runs it safely. Mirrors smh-quick-dev.md:100 and pairs with the `--unlink` already at cicd-close-workingtree.md:228. Sibling edit outside this group: the same line belongs at cicd-write-story-tests.md Step 0.5, which opens the tree explicitly.

### `DEV-14` · dev-cycle · `.agents/rules/reproduce-before-you-fix.md` is on-demand tier and is named by cicd-mobile-error-team, cicd-quick-dev and smh-quick-dev — but NOT by cicd-dev-story-tests.md, whose rules block carries git-policy alone, so the story lane's dev command never loads it.

**Failure:** The rule is on-demand (rules/INDEX.md:40), so a rule a command does not name is a rule the agent does not read. A bug-fix story runs through ② as the default lane; the agent gets no reproduce → minimize → pin-a-test-seen-red → falsify-one-hypothesis → minimal-fix → prove-by-reverting chain, and patches at the symptom.

**Edit:** .agents/commands/cicd-dev-story-tests.md:8-9 — add one line to the rules-in-force block, conditioned exactly as smh-quick-dev.md:17-18: "`.agents/rules/reproduce-before-you-fix.md` — **when the story is a BUG fix**: reproduce → minimize → pin a test seen red → falsify one hypothesis at a time → minimal fix → prove by reverting." This is one line of the DEV-16 block; land them together.

### `DEV-15` · dev-cycle · `.agents/rules/work-consolidation.md` is on-demand, fires "the moment work is DISCOVERED mid-lane", and is named by four smh commands and zero cicd commands — so the story lane's dev command never loads the look-for-a-home-before-you-mint ladder.

**Failure:** A defect met while building at Step 3 becomes a new ticket by default, because the rule that says to check this lane's own ticket → an open thematic parent → the open rolling `Bugs and Updates` ticket first is never read. That is the operator's named failure: "we are not developing 3 task for every 1 we try to fix" (2026-08-15). The rule is written subject-neutrally — "one SCC or AVCH tag", and rung 3 says to find the rolling ticket by its LABEL, never by remembering a key.

**Edit:** .agents/commands/cicd-dev-story-tests.md — add `work-consolidation.md` to the rules-in-force block at :8-9, and put the rung ladder as a short box in Step 3 (where a defect is met while building), phrased with the project's own Jira project and the rolling ticket found by label (`bugs-and-updates`) rather than by a hardcoded key, requiring the one-line statement of what was looked at. ⚠️ Adapt rung 2: `jira.md` §Subtasks scopes the mint-a-Subtask answer to Tasks — for a Story the home is a checklist line or the rolling ticket, never a Subtask under the story.

### `DEV-16` · dev-cycle · The rules-in-force block at cicd-dev-story-tests.md:8-9 declares ONE rule (git-policy) where the smh twin declares six, so the three on-demand rules this command acts on — reproduce-before-you-fix, work-consolidation, code-standards — are never loaded at all.

**Failure:** Tier decides this. On-demand rules load only when a command names them, so an agent running ② never reads the bug-fix loop, the discovered-work ladder, or the surgical-change / no-scope-creep law (code-standards.md:78) — the last reaching the story lane only at ③, after the drift is written. This is Part B of the SCC-197 plan: the block is the structural mechanism by which a rule reaches a command.

**Edit:** .agents/commands/cicd-dev-story-tests.md:8-9 — expand the block, each entry with its one-line reason: git-policy (already, plus the DEV-01 backtick clause) · worktree-per-story · tests-must-gate-for-real (loaded HERE because this is where the assertions and mutants are designed — SCC-145) · artifacts-always-first · 000-PLAN-FIRST-GATE · reproduce-before-you-fix (bug stories) · work-consolidation · code-standards (surgical changes / no scope creep). ⛔ The pointers do not replace the inline obligations DEV-01/03/05/06/15 add — rule + pointer + restatement (smh-clean-code-audit.md:149).

### `MERGE-04` · multi-lane · Narrower than reported: cicd DOES re-gate the post-absorb tree at 4.2, but nothing states that a non-`_artifacts/` change during the 4.1 absorb voids the lane's `Verdict:`, and nothing records the re-measurement — so 4.3 flips the story to done leaving a verdict line pinned to a pre-absorb sha.

**Failure:** Lane B absorbs the epic branch at 4.1, resolves a code conflict, goes green at 4.2, and is flipped `done` at 4.3 with its walkthrough still reading `Verdict: PASS @ <pre-absorb sha>` — a sha whose tree no longer exists; `closeout_preflight.py:239-247` will later call that verdict STALE, and with no append rule an agent 'fixing' it overwrites a FAIL record that was worth keeping.

**Edit:** .agents/commands/cicd-merge-epic-workingtrees.md:92-98 — add two sentences to Step 4.2: a non-`_artifacts/` change during the 4.1 absorb VOIDS this lane's `Verdict:`; append a `## Post-absorb re-measurement` block to the lane's walkthrough carrying `Verdict: <PASS|CONCERNS> @ <post-absorb sha>`, the absorbed epic-branch sha and one bullet per conflicted file, leaving the pre-absorb verdict standing. Point Step 4.3's done-flip at the re-measured verdict. Do NOT add a second gate run — 4.2 already is it.

### `MERGE-05` · multi-lane · cicd's stated ordering — dependency edges, then fewest-overlaps-first — actively schedules a machinery lane FIRST, because a lane editing CI config, a hook or a test runner typically has zero import edges and few overlaps.

**Failure:** A lane changing `.githooks/` or the project's test-runner entry point lands first; every subsequent lane's Step 4.2 gate runs under 'the project's canonical runners' that lane just redefined, and every subsequent 4.4 push runs under a pre-push hook no lane's review measured — so the rest of the sequence is a different procedure than the one reviewed.

**Edit:** .agents/commands/cicd-merge-epic-workingtrees.md:75-76 — after the fewest-overlaps-first sentence add: a lane touching commit or push machinery (`.github/workflows/`, `.githooks/`, hook config, the project's test-runner or gate scripts) lands LAST regardless of overlap count, and the gate it feeds re-runs after it lands.

### `MERGE-06` · multi-lane · cicd's closing report asserts landed SHA range, done-flip and pruned ✓ per story with no command that measures any of it — the set-level landing is never verified with plain git before the set is declared closed.

**Failure:** A `/cicd-close-workingtree` call that leaves a worktree shell behind, or a lane branch that survives the prune, is printed as 'pruned ✓' because nothing lists trees or branches after Step 6; the surviving shell then blocks a future `worktree add` and fakes a live lane in the next inventory.

**Edit:** .agents/commands/cicd-merge-epic-workingtrees.md:139 — retitle the closing section `## Step 7 — Verify, THEN report` and put four literal commands ahead of the narration: `git -C <project> rev-list --left-right --count epic/<KEY>-<slug>...origin/epic/<KEY>-<slug>` (expect `0 0`), `git -C <project> status --short` (empty), `git -C <project> worktree list` (only expected trees), `git -C <project> branch -a --list 'claude/*'` (only deliberately-retained lanes).

### `MERGE-11` · multi-lane · cicd's combined gate is a green/red judgement with no arithmetic — nothing reconciles per-lane test-case totals against the combined total, so a merge that ate one lane's cases reports green.

**Failure:** Two lanes each add cases to one shared test file; the 4.1 conflict is resolved under 'Code overlaps — pick an owner', which drops one side's cases; Step 4.2's 'already-landed siblings' red files stay green' then runs a file that no longer contains the missing cases and passes; Step 5.1 runs the union and is green with fewer cases than the set contributed, and nothing asks the count.

**Edit:** .agents/commands/cicd-merge-epic-workingtrees.md:115-119 — add to Step 5.1: record the case/test totals from each lane's Step 4.2 gate and from the combined run, and assert they are additive against the epic branch's pre-set total — or name which lane displaced which and why that was correct.

### `MERGE-12` · multi-lane · cicd names long scoped runners at 4.2 and 5.1 but never says to run them bare — piping a gate to `tail`/`head` returns the pipe's exit code, so a red suite reads as green.

**Failure:** The agent runs `npx vitest run <paths> | tail -40` at Step 4.2 because the scoped run is long, the pipe exits 0, the lane reads green, Step 4.3 flips the story to done and 4.4 lands it — with a red suite on the epic branch.

**Edit:** .agents/commands/cicd-merge-epic-workingtrees.md:94-96 and :115-119 — one sentence in each: run every gate BARE and read its exit code; piping to `tail`/`head` returns the pipe's status, so a red suite reads as green.

### `MERGE-14` · multi-lane · cicd Step 4.1 says to resolve conflicts per the Step 3 plan and pre-declares the one conflict it expects, but never says what a conflict the plan does not cover MEANS — so an unforeseen conflict is resolved in flight and the map that produced the remaining lanes' landing order stays wrong.

**Failure:** A lane committed an untracked artifact folder after the Step 3 `git diff --name-only` pass, so it never entered the map; it collides at 4.1 in a file the map does not classify; the agent resolves it in flight and continues, and the landing order for every remaining lane is still derived from a map now known to undercount.

**Edit:** .agents/commands/cicd-merge-epic-workingtrees.md:82 — one sentence in Step 4.1: a conflict in a file the Step 3 map did not classify is a finding — stop, re-derive the map for the remaining lanes, and only then continue.

### `MERGE-15` · multi-lane · cicd never counts commits-ahead per lane, so a lane reported finished with ZERO commits and its work sitting uncommitted is indistinguishable from a built lane with trailing artifacts — and Step 2 commits it and lands it unreviewed.

**Failure:** A lane at 0 commits ahead with a dirty tree arrives in the set; Step 2's 'uncommitted work gets committed HERE first' commits it, line 59's 'missing verdict → proceeds' backward-compat allowance lets it through, and Step 4 lands content that has never been reviewed by anything onto the epic branch.

**Edit:** .agents/commands/cicd-merge-epic-workingtrees.md:42-46 — add a commits-ahead column to Step 1.2's lane map (`git -C <project> rev-list --count origin/epic/<KEY>-<slug>..claude/<KEY>-<slug>`), and one sentence in Step 2: a lane at 0 commits ahead was never built — it needs commit, artifacts and `/cicd-code-review` before it is in the set. ⛔ Leave lines 54-55 ('uncommitted work gets committed HERE first') exactly as they stand; they are correct for trailing artifacts, and the finding's proposed rewording would break them.

### `MERGE-16` · multi-lane · cicd's landing order is derived from pairwise file overlap and in-repo import edges only — a lane whose content's destination is an unmerged branch in ANOTHER repo can land first, leaving the content on no merged branch in either repo.

**Failure:** Lane A deletes a file because its content moved to a sibling repo's branch; Lane A lands on the epic branch and its tree is pruned at Step 6; the sibling repo's branch is never merged; the content now exists on no merged branch in either repo and nothing in the report says so.

**Edit:** .agents/commands/cicd-merge-epic-workingtrees.md:75-76 — add to Step 3's ordering paragraph: a lane whose content's destination is an unmerged branch in another repo lands AFTER that branch merges there; name the other repo's branch and its state in the landing table.

### `PAIR-02-NOT-APPROVAL-LIST-MISSING-AND-CORRECTION-CLAUSE-INVERTED` · planning · The Step 1 checkpoint carries no inline restatement of what is NOT approval, so any reply — including a correction — reads as permission to write the board; the claim that it "states the opposite of the gate's correction clause" is overstated (it names no token at all rather than inverting one).

**Failure:** Failure: the operator replies "looks good, but drop story 4" at the checkpoint; the command's literal text ("correction loops happen here, then proceed to Step 2") gives the agent no instruction to re-present and stop again, so it edits and proceeds — while 000-PLAN-FIRST-GATE.md:51-53 rules a correction restarts the wait. Same checkpoint, same edit as PAIR-01, but the inline list is a separate line of text and the repo's own law (smh-clean-code-audit.md:149) is that a pointer never replaces the inline obligation.

**Edit:** .agents/commands/cicd-create-epic-sprint.md:36-37 — append the NOT-approval sentence from smh-plan-task.md:227-229 with `plan` swapped for `epic + story set`, and change "(correction loops happen here), then proceed to Step 2" to "a correction re-presents the set and stops again".

### `PAIR-06-PROJECT-FILES-WRITTEN-BEFORE-THE-BRANCH-IS-CUT` · planning · Step 1 (line 23) writes the epic into the project before Step 1.5 (line 42) cuts the epic branch, against artifacts-always-first.md's hard stop that no project file is edited for a commit-producing lane before its lane is opened.

**Failure:** Failure: Step 1 writes epics.md against whatever ref the checkout is parked on; Step 1.5 then runs `git checkout -b epic/<KEY>-<slug> origin/main`, which aborts with "Your local changes to the following files would be overwritten" whenever origin/main has advanced on epics.md — the kickoff wedges mid-run with authored work in a checkout it cannot move. When it does not abort, the work rides along uncommitted, which is the same state PAIR-05 fixes. The ordering law is subject-independent and already written: artifacts-always-first.md § Hard Stops, "NEVER edit a project file for a commit-producing lane before opening its worktree"; smh-plan-task.md:125-134 and :166 cut first and write inside.

**Edit:** .agents/commands/cicd-create-epic-sprint.md — move the Step 1.5 block (:42-72) ahead of Step 1 (:23-40) and renumber, so the branch exists before `bmad-create-epics-and-stories` writes anything; add one line stating that every artifact from that point is authored on that branch in `$PROJECT_ROOT`.

### `PAIR-08-NO-LOOK-BEFORE-YOU-MINT` · planning · The Epic mint at :58-62 is a raw `acli jira workitem create` with no dedupe search, while the sibling story mint in the same flow does the search mechanically for exactly this reason — the corrected framing is the missing dedupe, not "work-consolidation.md is uncited".

**Failure:** Failure: the command re-runs (it has two human stops, so a stall and restart is the normal case) or the board was backfilled, and Step 1.5 mints a SECOND Epic ticket for the same BMAD epic; story tickets then parent to whichever key that run read, leaving an Epic row nothing will ever move again. jira_feed.py cmd_mint's own docstring rules this the worse outcome — "a second ticket for the same story is worse than no ticket - two rows, one of which nothing will ever move again" — and cicd-write-story-tests.md:66-79 carries that discipline for stories. `mint` takes `--story` only, so the Epic mint cannot inherit it and needs the look written into the prose.

**Edit:** .agents/commands/cicd-create-epic-sprint.md, immediately before the `acli jira workitem create` at :60 — add `acli jira workitem search --jql "project = <PROJ> AND type = Epic AND statusCategory != Done" --fields key,summary --limit 50`, and require ONE line naming what was looked at and why nothing covers this epic (work-consolidation.md:53-54: "Say in ONE line what you looked at. That sentence is the whole enforcement mechanism"). Add `.agents/rules/work-consolidation.md` to PAIR-01's rules block rather than a second pointer here.

### `QD-C8` · quick-dev · cicd-quick-dev has no sibling-lane read; its only `git worktree list` is a tree-reuse lookup, so a collision with another live lane's uncommitted work is discovered at merge time.

**Failure:** Two lanes edit the same shared handler; the quick-dev lane never reads the sibling tree's uncommitted diff (invisible to grep and to any branch diff), builds on a signature the sibling is changing, and the collision surfaces as a conflict or a regression on the epic branch at close-out.

**Edit:** Add to Step 0.5 at .../.agents/commands/cicd-quick-dev.md:34: `git worktree list` → `git -C <each-other-tree> diff --name-only origin/main...HEAD` → `git -C <each-other-tree> status --short`, then 'any file in both sets is a landing-order dependency — name which lane lands first and what happens to this work if it does not.'

### `QD-C12` · quick-dev · cicd-quick-dev.md:124 passes `--story <id-or-slug>` on both lanes, but the ad-hoc lane has no slug source and writes no task.yaml, so jira_feed.py's SCC-174 disagreement guard cannot fire and the Dev Record forks.

**Failure:** On the ad-hoc chore lane the agent invents a free-text slug for `--story`; the later close-out files under the branch slug `<KEY>-<slug>`, the script creates a SECOND record instead of updating, and `check` blesses one ticket's two records as two lanes — the AVCH-59 shape, in a project repo.

**Edit:** Split .../.agents/commands/cicd-quick-dev.md:124 by lane: story lane keeps `--story <story-id>`; ad-hoc chore lane passes the BRANCH slug `<KEY>-<slug>` and says so in the surrounding prose (matching what /smh-close-task-merge-tree passes), or writes a `task.yaml` at Step 0.5 so jira_feed.py can default it. Leave the story half alone.

### `QD-C14` · quick-dev · cicd-quick-dev's Done section (:141) sends the operator to /cicd-update-sprint-memory, a door its own :117-118 says the ad-hoc lane never reaches and whose precondition rejects a chore branch outright.

**Failure:** An ad-hoc quick fix finishes; the agent tells the operator to run /cicd-update-sprint-memory; that command's Step precondition requires HEAD on a `claude/*` branch and STOPs on anything else, so the branch is left with no named door and never lands.

**Edit:** Make the Done section at .../.agents/commands/cicd-quick-dev.md:138-141 lane-aware: story lane → invite `/cicd-update-sprint-memory`; ad-hoc chore lane → `/cicd-push-e2e` when the diff touches `backend/ frontend/ firebase/ functions/ mobile/ .github/`, else `/smh-close-task-merge-tree`. Land it with QD-C1 so both ends of the file name the same door.

### `QD-C4` · quick-dev · cicd-quick-dev claims its reviewer runs 'in a subagent with NO conversation context' but never probes the review runtime, so an inline runtime silently reviews inside the builder's own context and the flow records it as independent.

**Failure:** In a headless pipeline or a platform with no subagent tool, the Step 3 fan-out fails to launch; the lane runs the adversarial review in the builder's own context, writes the same `Verdict:` line, and the walkthrough asserts an independence that never existed — the SCC-203 incident exactly.

**Edit:** Add a Step 0.9 review-runtime probe to .../.agents/commands/cicd-quick-dev.md carrying the SCC-203 capability-not-policy wording (a subagent tool exists = fan-out; permission is a different question), and require the `review-runtime:` line in the Step 4 walkthrough header at :108-114. Pair with QD-C5 — the engine takes `review_runtime` as an input.

### `QD-C6` · quick-dev · cicd-quick-dev never binds `tests-must-gate-for-real.md` anywhere, so the pinning regression test its Step 3 demands carries no obligation to have been seen red for the right reason.

**Failure:** A bug fix on this lane adds a regression test that was never run before the fix; it passes with and without the change, and the lane ships a vacuous pin as its Step 3 evidence — the `red-test-can-die-before-its-assertion` / `prose-pinning-guards-are-vacuous` failure.

**Edit:** Add `.agents/rules/tests-must-gate-for-real.md` to the rules-in-force block at .../.agents/commands/cicd-quick-dev.md:8-14 (and `.agents/rules/worktree-per-story.md` alongside it, riding with QD-C2's fix). 000-PLAN-FIRST-GATE is QD-C3's.

### `QD-C7` · quick-dev · cicd-quick-dev cuts its branch from a bare local `main` / epic ref with no fetch — the file never mentions `origin` at all — where the twin pins the base to `origin/main` after fetching.

**Failure:** The lane opens its tree from a stale cached local ref, builds on a base a sibling has already moved, and the divergence surfaces as a conflict or a silent revert of the sibling's landed work at close-out.

**Edit:** In Step 0.5 at .../.agents/commands/cicd-quick-dev.md:34-37 add `git -C "$PROJECT_ROOT" fetch origin`, pin the base to `origin/epic/<KEY>-<slug>` (story lane) / `origin/main` (ad-hoc lane), and add `git -C "<the new tree>" branch --unset-upstream` that the origin start-point makes necessary.

### `QD-C9` · quick-dev · cicd-quick-dev's Step 0.5 mints `chore/<JIRA-KEY>-<slug>` from a key no step has established, and the lane never moves the ticket to In Progress — Step 4.5 simply asserts the key is 'already in hand'.

**Failure:** On the ad-hoc lane there is no story frontmatter to read, so the agent invents or guesses the key when naming the branch; the armed commit-msg hook then refuses every commit (or a wrong-project key is rejected), and the ticket sits in To Do for the whole lane because nothing but the per-machine post-commit hook ever moves it.

**Edit:** In Step 0.5 at .../.agents/commands/cicd-quick-dev.md:33-39, before the branch is named: pin `EXPECTED_KEY`, `acli jira workitem view "$EXPECTED_KEY"` to read its ACCEPTANCE block (Step 1's first AC source on the ad-hoc lane), 'no ticket → STOP and ask, never invent a key', then `python3 .agents/scripts/jira_feed.py start --key <KEY> --apply` with the 0/2/3/4 exit-code table.

### `QD-C11` · quick-dev · cicd-quick-dev never runs `link-worktree-assets.py`, so its worktree lacks `.env`, `auth_keys/` and `node_modules` — which a project repo needs and the command centre does not.

**Failure:** The lane opens its tree, reaches Step 3's scoped tests, and pytest/uvicorn/`next dev`/the emulators fail on missing `.env` or `node_modules` because they resolve relative to cwd — the agent then either runs the gate in the wrong checkout or reports a red that is environmental, not real.

**Edit:** Add `python3 .agents/scripts/link-worktree-assets.py .claude/worktrees/<slug>` to Step 0.5 at .../.agents/commands/cicd-quick-dev.md:34, with the `--copy-env` note for a lane that will change `.env` and a pointer that `--unlink` runs before any prune.

### `QD-C12` · quick-dev · Same defect as the earlier QD-C12 entry — the unconditional `--story` at cicd-quick-dev.md:124 has no slug source on the ad-hoc lane.

**Failure:** Two lens copies of one defect; one lane-split edit satisfies both. Do not apply twice. This copy adds one worthwhile rider: the 'found by SLUG, not by --key' note belongs beside the existing 'exactly one Dev Record' paragraph at :131-133, which currently half-carries it.

**Edit:** Same lane-split at :124, plus fold 'the script finds the record by the SLUG, never by --key (SCC-174)' into the paragraph at :131-133.

### `QD-C1` · self-audit · cicd-self-audit.md's Phase 2 tripwire list omits the subject-neutral "a gate that cannot fail" tripwire, and the file never cites `.agents/rules/tests-must-gate-for-real.md`; the twin carries both (smh-self-audit.md:20-23 and :159-160).

**Failure:** A plan proposing a CI job with `continue-on-error: true`, a test script ending `|| true`, or a check whose empty file set reads as a pass walks all nine cicd Phase 2 tripwires (:130-139) without firing one, so the vacuous gate is approved GO at the cheapest moment to cut it and only surfaces, if at all, downstream at /cicd-code-review.

**Edit:** Append one bullet to .agents/commands/cicd-self-audit.md after line 139: "- [ ] A **gate that cannot fail** - report-only, `|| true`, `continue-on-error`, or a check whose empty input or missing tool reads as a pass. A vacuous green is worse than no gate at all (`.agents/rules/tests-must-gate-for-real.md` Rules 1 + 3)". The inline restatement carrying the rule stem IS the fix; the separate `> **Rules in force**` block the finding also proposes is optional and not required by workflow_lint - do not let it grow the edit.

### `QD-C2` · self-audit · cicd-self-audit.md Phase 1 has no sibling-lane read, so the plan-time blast radius is traced blind to other live story worktrees on the same epic branch; the twin has one at smh-self-audit.md:123-135.

**Failure:** Two story lanes off one epic branch both plan edits to the same file; lane B's Phase 1 greps only its own tree, cannot see lane A's uncommitted work at all, reports the radius clean, and the landing-order dependency is first discovered at /cicd-code-review Step 0.7 or at merge - after the code is written.

**Edit:** Insert a "⭐ Check the sibling lanes" block into .agents/commands/cicd-self-audit.md between line 119 and the Phase 2 heading at line 121, modelled on smh-self-audit.md:123-135 but with the story's EPIC BRANCH as the comparison ref, never origin/main: `git -C "$PROJECT_ROOT" worktree list`; `git -C <each-tree> status --short`; `git -C <each-tree> diff --name-only <epic-branch>...HEAD`; plus the ruling that a file in both change sets is a landing-order dependency to name in the Phase 4 verdict with which lane lands first. ⛔ The same block MUST cite `.agents/rules/worktree-per-story.md`.

### `QD-C3a` · self-audit · cicd-self-audit.md has no "no plan file and no story file, so STOP" branch; Step 0 (:22-28) resolves only the project, while :13 and :34 assume the artifact already exists. The twin has the branch at smh-self-audit.md:55-59.

**Failure:** Invoked standalone (the frontmatter and the skill listing both advertise it as standalone) in a project where neither an implementation_plan.md nor a story file exists, the agent hits no step telling it to stop, so it reconstructs a plan from the chat and audits its own invention - a GO verdict on a plan nobody wrote.

**Edit:** Add one sentence to .agents/commands/cicd-self-audit.md Step 0, after line 28 and before the `---` at line 30: "**No plan file AND no story file under `PROJECT_ROOT`? STOP and say so.** This command audits a written plan or story; reconstructing one from the chat and auditing that is the exact failure it exists to catch." Naming the story-file fallback is what keeps it a cicd sentence rather than a copy of the Task-lane one.

### `QD-C4` · self-audit · cicd-self-audit.md's right-size ladder contradicts itself: :38 puts Phase 3 inside every Light pass ("Phases 1-3") while :146 admits Phase 3 for Light "only when state is involved" and :14 says a Light plan does not get the Full pass.

**Failure:** On a Light plan with no state involved - a prompt-string tweak - an agent walking the literal step list from Phase 0 runs the whole seven-row pre-mortem table, which is precisely the brute-forcing :10-11 exists to prevent, while an agent reading the Phase 3 heading skips it: same plan, two different audits and two different costs.

**Edit:** Edit .agents/commands/cicd-self-audit.md:38 only, from "Phases 1-3." to "Phases 1-2 (add Phase 3 only when state is involved)." Leave line 146 and its "state" trigger word alone - the subject legitimately owns that word; only the ladder arithmetic is wrong. One line, nothing else moves.

### `QD-C5` · self-audit · smh-self-audit.md points at `.agents/rules/constitution.md` at :15 but no phase ever performs the constitution + assumptions scan its twin restates inline at cicd-self-audit.md:100-103 - a pointer that replaced the obligation, the shape smh-clean-code-audit.md:149 names as a finding.

**Failure:** A Task plan that proposes rewriting a whole command file where a surgical edit would do, hardcodes a secret, or rests on an untested assumption about external state (a file existing, a hook being armed, an env var set) walks every row of Phase 1's table and every Phase 2 tripwire without one of them asking the question, and gets GO.

**Edit:** Add one bullet to .agents/commands/smh-self-audit.md Phase 1, after the sibling-lane ruling ending at line 135: a restated constitution + assumptions scan (one line each, if relevant) carrying only the subject-neutral half - does the plan propose a full-file rewrite where a surgical edit would do? does it hardcode a secret? does it rest on an untested assumption about external state (a file's existence, whether a hook ships armed, an env var, the other machine's interpreter)? ⛔ Drop cicd's `get_db()` shared-singleton clause (project-specific) AND drop the contract-two-sidedness clause - Phase 1's table already covers it at :107 (command → four doors) and :110 (script → hook callers), so restating it would be duplication, not parity.

### `QD-C1` · self-audit · Second copy of QD-C1 in the source file (same defect, same file, same lines): cicd-self-audit.md lacks the "gate that cannot fail" tripwire and any citation of `.agents/rules/tests-must-gate-for-real.md`.

**Failure:** Same failure as the first QD-C1 entry: a plan proposing a report-only or `continue-on-error` gate clears all nine Phase 2 tripwires at :130-139 and is approved GO. Apply the fix once.

**Edit:** Same single edit as QD-C1 - one tripwire bullet after cicd-self-audit.md:139 carrying the `tests-must-gate-for-real` stem inline. Do not apply twice.

### `QD-C2` · self-audit · Second copy of QD-C2 in the source file (same defect): cicd-self-audit.md Phase 1 has no sibling-lane / landing-order read.

**Failure:** Same failure as the first QD-C2 entry: lane B's plan-time radius cannot see lane A's live worktree, so a shared file is not named as a landing-order dependency until review or merge. Apply the fix once.

**Edit:** Same single insertion between cicd-self-audit.md:119 and :121, epic-branch-scoped, and it must cite `.agents/rules/worktree-per-story.md` or workflow_lint.py's `_RULE_POINTERS` warns on the literal `git worktree`. Do not apply twice.

### `QD-C3a` · self-audit · Second copy of QD-C3a in the source file (same defect): cicd-self-audit.md has no plan-absence STOP.

**Failure:** Same failure as the first QD-C3a entry: with no plan and no story file, the agent invents a plan and audits it. Apply the fix once.

**Edit:** Same one sentence in cicd-self-audit.md Step 0 after line 28. Do not apply twice.

### `QD-C4` · self-audit · Second copy of QD-C4 in the source file (same defect): cicd-self-audit.md:38 admits Phase 3 into every Light pass while :146 makes it conditional.

**Failure:** Same failure as the first QD-C4 entry: a Light, stateless plan gets either the full pre-mortem or none depending on which line the agent reads. Apply the fix once.

**Edit:** Same one-line edit at cicd-self-audit.md:38 - "Phases 1-2 (add Phase 3 only when state is involved)." This copy's proposed wording is the one to use; leave :146 as written. Do not apply twice.

## LOW

### `QD-C4b` · clean-code · Narrowed: cicd-clean-code-audit's Step 0 omits §BIND's "a needed path missing under `PROJECT_ROOT` → STOP, never fall back to the lobby" clause that three sibling cicd commands restate literally, and never names the variant it binds.

**Failure:** Bound to `PROJECT_ROOT = Projects/<name>` from the lobby, Step 1 runs `backend/.venv/Scripts/python.exe -m ruff` and the path does not exist under PROJECT_ROOT. cicd-clean-code-audit.md:35-36 says only "Every bare path and every command below resolves under `PROJECT_ROOT`" with no STOP on a missing path, so the agent resolves it against the lobby cwd and a `cicd-*` command audits the lobby - the exact break its own header rule at :10 forbids and smh's convention row (smh-clean-code-audit.md:146) names as a finding. Verified: `grep -c '§STD'`, `'§BIND'`, `'never fall back'` in cicd-clean-code-audit.md all = 0; cicd-code-review.md:17-21 and cicd-self-audit.md:22-26 both carry the clause verbatim.

**Edit:** .agents/commands/cicd-clean-code-audit.md:35-36 - append to the binding sentence: "(per `.agents/rules/smh-target-resolution.md` §STD + §BIND); a needed path missing under `PROJECT_ROOT` → STOP, never fall back to the lobby." That is the whole edit.

### `QD-C4b` · clean-code · Same underlying defect as the earlier QD-C4b entry, narrowed identically: cicd-clean-code-audit's Step 0 drops §BIND's "STOP, never fall back to the lobby" clause and never names the variant it binds.

**Failure:** Same one-sentence edit satisfies both. Its added half - "compress Step 0 to the sibling one-liner shape" - is DROPPED on question 2: reshaping four numbered cases into one sentence changes no obligation an agent acts on, and this entry's own §STD pointer-write half fails question 3 for the reason recorded on the earlier QD-C4b entry.

**Edit:** Identical to the earlier QD-C4b entry - one clause appended at .agents/commands/cicd-clean-code-audit.md:35-36. Do not compress or renumber Step 0, and do not apply twice.

### `QD-C7` · code-review · cicd carries no rule protecting another session's dirty `_artifacts/_memory/` files, and project memory stores are git-TRACKED, so they materialise in every story worktree.

**Failure:** Once the Step 0.6 sweep lands (QD-C3), an AGY story reviewer sees dirty tracked files under `Projects/AGY_AVIATIONCHAT/_artifacts/_memory/` left by another session and sweeps, reverts or commits them under this story — destroying memory the store's own law says is never deleted.

**Edit:** Land in the SAME edit as QD-C3, as the closing lines of the new Step 0.6 in .agents/commands/cicd-code-review.md, ported from smh-code-review.md:65-66 with "task" → "story": "Dirty files under `_artifacts/_memory/` are named separately and left alone — another session's memory store is never swept, deleted, or committed under this story." Do not land it as a floating bullet: without the `git status --short` line it has no trigger.

### `QD-C9` · code-review · smh-code-review's engine-input table omits `DEFERRED_WORK` although :198 names `_artifacts/_main/deferred-work.md` as the only legal sink for a `defer`, and no step tells the reviewer to transcribe the engine's bullets there by hand.

**Failure:** A lens finding is deferred on a real structural blocker; because the optional input is unset the engine returns the bullets in its summary instead of writing them (step-04-record.md:23-25), the reviewer files nothing, and the ledger the command declares mandatory never receives the item — deferred to nowhere.

**Edit:** Add one row to the engine input table in .agents/commands/smh-code-review.md after `ARTIFACT_DIR` (:172): "| `DEFERRED_WORK` | `_artifacts/_main/deferred-work.md` — the same file Step 1 names as the only legal sink for a `defer` |".

### `QD-C7` · code-review · Same defect: the missing dirty-`_artifacts/_memory` rule in cicd.

**Failure:** Same failure as the earlier QD-C7 entry; it lands as the closing lines of QD-C3's new Step 0.6, not as a separate edit.

**Edit:** None beyond the earlier QD-C7 edit.

### `QD-C9` · code-review · Same defect: `DEFERRED_WORK` missing from smh's engine-input table.

**Failure:** Same failure as the earlier QD-C9 entry; one row covers both.

**Edit:** None beyond the earlier QD-C9 edit (one table row in .agents/commands/smh-code-review.md after :172).

### `DEV-17` · dev-cycle · Step 4 adds tests after the code is written and demands non-vacuity proof, but nothing bans presenting a post-hoc green as a red or requires a characterization check to be labelled as one.

**Failure:** Once DEV-05 installs RED-then-GREEN per acceptance item in `## Evidence`, a Step-4 test written after the code exists has a slot it can be written into as a RED→GREEN pair it never was. The honesty clause is the guard on the evidence contract DEV-05 creates, and ③ and the close-out read that section as proof.

**Edit:** .agents/commands/cicd-dev-story-tests.md Step 4 (after :124) — one line from smh-quick-dev.md:295-297: "⛔ Never write an assertion after the edit and present it as a red. A characterization check written green is honest — label it that way in the walkthrough; a green check presented as a red is not." Land in the same edit as DEV-05.

### `MERGE-09` · multi-lane · An empty eligible set is never named as a STOP, so a run where every lane is BLOCKED still walks into Step 5 and prints the literal words 'Set closed.'

**Failure:** All lanes come back FAIL at Step 2; Step 3 produces an empty table, Step 4 loops zero times, Step 5.1's combined gate is trivially green, Step 5.2 runs `/cicd-prune-context` and asks 'Set closed. Any manual learnings…', and the preamble's 'NOTHING left owed on the set' is satisfied vacuously — after zero merges.

**Edit:** .agents/commands/cicd-merge-epic-workingtrees.md:59 — one sentence at the end of Step 2: if the eligible set is empty, STOP — print that zero lanes landed and why per lane, and never report the set as closed. Do NOT add a per-lane reason requirement; line 142 already carries it.

### `QD-C10` · quick-dev · The `git commit -m` backtick-execution hazard is in smh-quick-dev's commit step and absent from cicd-quick-dev's.

**Failure:** The agent writes a commit subject quoting a shell command in backticks; the shell executes it before git ever sees it, and the commit lands with a mangled subject (or runs the quoted command) — the incident the `commit-message-backticks-execute` law exists for.

**Edit:** Add one line after .../.agents/commands/cicd-quick-dev.md:69: '⛔ Backticks in `-m "…"` EXECUTE. Use `git commit -F <file>` whenever the message contains a backtick.' Scope the fix to this file; the family-wide absence across the other cicd commands is a separate ticket, not this lane's.

### `QD-C10` · quick-dev · Same defect as the earlier QD-C10 entry — the backtick `-m` execution hazard is absent from cicd-quick-dev's commit step.

**Failure:** Two lens copies of one defect; one added line satisfies both. Do not apply twice.

**Edit:** Same single line after .../.agents/commands/cicd-quick-dev.md:69.
