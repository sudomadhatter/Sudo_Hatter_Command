---
IsArtifact: true
ArtifactMetadata:
  title: SCC-447 — Review disposition doctrine: reproduce or drop, then fix, one review per lane
  type: implementation_plan
  date: 2026-09-11
  version: 3
  supersedes: v2 @ 114deb3a · v1 @ 47b3c4aa
---

# SCC-447 — implementation plan (v3)

**Ticket:** [SCC-447](https://sudo-command.atlassian.net/browse/SCC-447) · **Decisions of record:** ticket comment 10508 (2026-09-11), which governs over the description where they differ
**Lane:** `chore/SCC-447-review-disposition` · worktree `.claude/worktrees/scc-447-review-disposition` · cut from `origin/main` @ `03778605` · draft PR #210
**Door:** `/smh-dev-task-tests` (the full lane — the work touches gate scripts and the tests directory, which the quick lane may not)
**Sibling lanes:** none live (`git worktree list` → the lobby on `main` @ `03778605` and this lane only; the two stale stubs v1 named have since been pruned)
**State at v3:** Part 1 landed at `9b127e09` under v2's policy and is corrected to this version in the commit that carries v3; Parts 2–6 are not built.

## Why a v2, and why it is a full rewrite

Two things happened after v1 was approved, and each one changed the design rather than a paragraph of it.

**The operator asked who reproduces.** v1 had the *assessor* running a finding's reproduction command. His question — *"we are also making the agents who are claiming they found it recreate, correct? This way they will discover if it's real or not"* — is the stronger design, and checking it against the tool grants turned it into a three-layer contract (D1) that runs through every part: the lens proves it, the engine cannot execute and only checks the claim is there, the door re-proves it on the real tree. That is not an amendment to the assessor's table; it is what the table sits on.

**The self-audit of v1 was too narrow.** It verified the paths v1 declared and stopped. Grepping the repo for the machinery this lane retires found six undeclared files that go red or go stale the moment Part 1 lands, one latent gate defect that the retirement would turn into a false refusal on every spec-less review, and one sizing fact v1 glossed (half of `test_review_engine.py` retires). All ten findings of the v2 audit are baked in below; none is carried as an open item.

## v3 — the operator struck `escalate` and `defer` (2026-09-11)

Part 1 landed at `9b127e09` under v2's action policy and was rejected twice on the same day, once per bucket. On `escalate`: *"There is no reason for an important coming to me? ... what am I going to do? Go read the code and test it again? ... I don't want to review anything. That was the reason I asked you to have the sub agents prove the findings so I don't have to go read files and code for every important."* On `defer`: *"Why would we defer? That is giving up ... The agents now fix critical and important. What else is there? What would be fair grounds based off previous evidence to flag the CONCERNS, instead of PASS ... we have to define that now for this to work."*

Both buckets had the same defect: each put a reproduced defect in front of him to read, and the lenses were made to reproduce precisely so that nobody has to. v3 removes both, makes "reproduced" mean "fixed", and defines the CONCERNS grounds from the evidence on disk — exactly two, both things the review cannot settle by itself. D2, D3 and D5 below are rewritten; Parts 3, 4 and 6 are re-aimed where they named the struck buckets. The correction to Part 1's files is one RED→GREEN commit on top of `9b127e09`.

## The problem, in one paragraph

The review engine has no stop condition an agent can reach on its own. Its lenses are told to be exhaustive and are measured by what they return; the assessor was told to fix everything that survived triage; the verdict floor was computed *before* the fixes and never moved with them; and the preflight's remedy for FAIL said "re-run the review". Measured over every review on disk (138 with a verdict, 88 with per-lens ledgers): 17.9 fixes per review, 52% of them on severities that can never block, re-review converting a non-PASS to PASS 1 time in 7, the verify wave refuting 2 findings in 18 reviews. SCC-441 ran that machine three times over a 155-file, 1.46 MB diff (48 files were byte-copy mirrors, 26 the lane's own records) and consumed a week of credit without closing. Underneath all of it is one price: a finding costs the lens a paragraph, so thirty come back.

## The fix, in four sentences

1. **Reproduce or drop.** A `critical` or `important` that no one can make fail does not exist — the lens runs its own command before it reports, and the door runs it again on the real tree before anyone acts.
2. **Fix what reproduced.** A reproduced `critical` or `important` is fixed in the lane with a pin — nothing is escalated, nothing is deferred. The one thing the operator sees is a fix the agent may not apply alone (the constitution's Ask First list, or a spec conflict), and it reaches him written, as a patch, with the verdict.
3. **The floor is computed at the stamp, on rows still open.** A row closed by a fix and a green pin no longer gates. CONCERNS has exactly two grounds — coverage (a dead lens) and authority (a held fix) — and ships on the operator's word; FAIL is the only blocker.
4. **One review per lane.** The retest is the pins plus the suite through the receipt writer — never a second fan-out.

## Acceptance — checkable, in the ticket's revised order

| Row | Statement | Proved by |
|---|---|---|
| **A** | `code-standards.md` §6.5 and §7 (and the byte twin `.claude/rules/code-standards.md`) carry Gate 0 (reproduce or drop, receipt on disk, no `--result` flag), the action policy (reproduced → fixed; `held` and `out-of-lane` the caller's only other dispositions), the two CONCERNS grounds, "CONCERNS ships on the operator's word", "one review per lane", and "the floor is computed at the stamp on what is still OPEN". `artifacts-always-first.md` §6's findings-table vocabulary and its "invalidates the verdict" sentence, and `jira.md`'s review-findings paragraph, say the same thing in the same words | `test_review_disposition.py` block A: relationship regexes with in-memory counter-examples; twin byte-equality |
| **B** | Engine: step-01's lens table has exactly three rows and no levels; the hunter contract and the auditor rubric require `reproduce:` + `expected_wrong_output:` on every critical/important **and require the lens to run it in its own copy** before reporting; step-02 is a pass-through; step-03 carries the presence gate (the engine cannot execute), the two buckets `fix`/`drop`, and the floor on open rows; step-04's record vocabulary matches; SKILL.md states the floor is provisional and names the two evidence-backed ways down; the `.claude/skills/code-review-engine/` cache is byte-identical; the negative-control fixture attributes its seeds to surviving lenses | `test_review_disposition.py` block B; `test_review_engine.py`, `test_lens_roster_contract.py`, `test_finding_record.py`, `test_review_fixture.py` updated and green |
| **C** | Both review doors and their `.opencode/` byte mirrors: Step 1 runs `review_scope.py` and passes its output as `DIFF`; a `## Reproduce` step re-runs every surviving critical/important through `repro_receipt.py` on the real tree; the fix paragraph is the action policy; Step 3.5 nested runs the machine floor only; Step 4 resolves the provisional floor on open rows, carries the re-stamp block and the end-of-review message; NO door instructs a full re-review on a fix batch; no level derivation, no `lens_budget` row | `test_review_disposition.py` block C; `test_command_surfaces.py` green; `test_twin_parity.py` green |
| **D** | Scripts, each seen red first: `review_scope.py` strips mirrors/records/generated launchers, groups commits by key, refuses a range spanning two keys, and `--audit` keeps every mirror; `repro_receipt.py` records command, exit and output per finding id; `walkthrough_roster.py` refuses a second full roster without the operator's line, a fixed suggestion/nitpick, a fixed row without a pin, a fixed/held critical/important without a receipt on disk, a held row without its patch on disk, a PASS with an open critical, a PASS or CONCERNS with a reproduced important that is neither fixed nor held, **and no longer refuses a mode-skipped lens under `fan-out`**; `task_preflight.py`'s FAIL message says "re-run the pins and the suite, re-stamp" | `test_review_scope.py`, `test_repro_receipt.py`, `test_walkthrough_roster_dispositions.py`, `test_walkthrough_roster.py` (one new NA case), `test_task_preflight.py` (one new case) — all with a mutation sweep |
| **E** | `cicd-autopilot-claude.md`, `autopilot_SOP.md`, and the SOP §15 table row: a non-PASS verdict escalates; no fix child, no fresh reviewer; "never ships by itself" gone | `test_review_disposition.py` block E |
| **F** | `work-consolidation.md` Rule 2 and `smh-plan-task.md` (+ mirror): parts are built AND reviewed in sequence, each review on its own commits; parts without rider keys are selected by `--range`; the enforcement suite is the integration check; a plan-time size warning when a part's declared set exceeds 40 master files | `test_review_disposition.py` block F |
| **G** | `workflows_testing_SOP.md` (§③, §`/smh-code-review`, §10, §11, §15, **and the command-atlas appendix rows**), the `operator_workflows_quickref.md` diagrams, and the changelog updated in the same commits as the surfaces they describe; `workflow_lint.py --toolkit-only` 0 errors; `run_all.py` N/N through the receipt writer on a clean tree | pasted output + `gates/suite.json` |
| **H** | Both self-audit twins: POST-DEV mode resolves its change set through `review_scope.py --audit`, and Lens 2 states the scope asymmetry — the parity lens reads the mirrors a review strips. The twin-law fences stay byte-identical | `test_review_disposition.py` block H; `test_review_scope.py` audit-mode case; `test_twin_parity.py` green |

## Design — the mechanisms, stated once

### D1. WHO reproduces — the three-layer contract (the spine of this lane)

**Verified, not assumed (2026-09-11).** `code-review-engine/SKILL.md:4` grants `allowed-tools: Read, Write, Glob, Grep, Task` — **no Bash**. The engine cannot execute anything, and that is deliberate: a reviewer that can execute is one edit from being an editor, and SCC-295 measured three of five lenses writing to the builder's tree with one reporting a RED that no version of the real code could produce. Every lens skill (`bmad-review-edge-case-hunter`, the auditor rubrics) carries **no** `allowed-tools` line, so a lens subagent inherits full tools and holds its own worktree copy. The doors (`/smh-code-review`, `/cicd-code-review`) carry no grant line either — they have everything, on the real tree. So the reproduction splits by what each layer can do:

| Layer | Can execute | What it does with a `critical`/`important` |
|---|---|---|
| **the lens** — Edge Case · Acceptance · Test-Adequacy | yes, in its own disposable copy | writes `reproduce: <command>` and `expected_wrong_output: <text>`, **runs the command itself**, and **deletes the finding** if it does not fail the way it predicted. Reports `reproduced: yes` + the output it saw. A finding without all three is not sent |
| **the engine** — step-01 → step-04 | **no** (no Bash, by design) | checks the three fields are THERE. Missing any → `drop`, counted, unread. Buckets on the lens's claim, returns a **provisional** floor and never runs a command |
| **the door** — `/smh-code-review`, `/cicd-code-review` | yes, on the REAL tree | re-runs each surviving command through `repro_receipt.py`; **that receipt is what binds**. Drops what does not reproduce, fixes every reproduced critical and important with a pin (holds a written patch only where Ask First or the spec forbids applying it alone), resolves the floor at the stamp |

**Why the lens's own run is the filter that matters.** A finding today costs the lens one paragraph, which is why thirty come back. A `critical` now costs a working command — and an agent forced to write the exact command usually discovers, part-way through writing it, that it has nothing. That discovery costs one command while the lens already has the file open and the reasoning in context; the assessor making the same discovery costs a read, a trace and a judgment call. The tax is **severity-gated**: a `suggestion` needs no reproduction and never blocks, so the one move that becomes uneconomical is inflating a nitpick to be heard — the exact behaviour that broke SCC-441. That is a better fix than telling agents to be less enthusiastic, because it does not depend on them obeying it.

**Why the door's run is not optional.** A lens proves the bug exists *in the lens's copy* — which it may have edited (SCC-295). Only the door's run on the real tree proves it exists in the code that ships. Two runs, two different questions.

**What "cannot reproduce" means, so nobody argues it later.** One of three things: the finding was imagined (a pattern that looks like a bug class, never traced); it is real but unreachable (an upstream guard, a type, a config we do not ship — true and inert, and fixing it is how working code gets changed to chase a state that cannot occur); or it is real, reachable, and the lens could not be bothered to prove it. The rule treats all three identically **on purpose**: telling them apart is the expensive judgment call that has been going wrong, and the measured price of having that debate was 17.9 fixes per review. A command that fails, or does not, is not a debate. The third case is the honest cost of the rule and is stated under Risks.

### D2. The action policy — reproduced means fixed (code-standards §6.5 + §7, engine step-03, both doors)

**Ruled 2026-09-11, replacing v2's table.** v2 kept two buckets beside `fix` — `escalate` for a reproduced `important` (handed to the operator with a recommendation, "ships as recorded") and `defer` for a fix "this lane structurally cannot hold". The operator struck both (quoted in the v3 note above). Each bucket put a reproduced defect in front of him to read, which is the review the lenses were made to reproduce so that nobody has to.

| The door's receipt says | The assessor does | Disposition written |
|---|---|---|
| reproduced `critical` or `important` | fixes it, in this lane, with a pin, through `reproduce-before-you-fix` G1–G5 | `fixed @<sha> · pin <test>[:<case>] · repro <id>` |
| reproduced, and the fix needs the operator's permission — the constitution's Ask First list, or it contradicts the spec | writes the fix and its pin as a patch at `<artifacts>/gates/repro/<id>.patch` (beside the receipt), verifies `git apply --check` on the lane tip, does NOT apply it, stamps | `held — ask-first: <row> \| spec-conflict · repro <id> · patch <path>` |
| reproduced, in a file this lane did not touch (another repo · a file another LIVE lane owns) | not this lane's work: the `work-consolidation` ladder, receipt attached | `out-of-lane — <where it went>` |
| `critical`/`important` that did not reproduce on the real tree, or arrived without its three fields | dropped, counted, never written up individually | `dropped — no reproduction` (one count line) |
| `suggestion` / `nitpick` | nothing; a count | `recorded` (one count line) |

**The operator's two words on a `held` row:** `apply <id>` — the door applies the patch, runs the pin red then green, re-stamps (D4); `approved` — the lane ships without it and the row closes as `ruled — <his word>`. A held `critical` is FAIL until one of those; a held `important` is CONCERNS. `held` is never a question and never carries a recommendation to weigh: the fix is written, and the only thing missing is permission the constitution says the agent may not grant itself.

**`decision_needed`, `escalate` and `defer` are all retired**, and the deferred-work ledger and the `DEFERRED_WORK` input with them. An open decision row holds the ticket forever at `jira_feed.py finish` (`:1774`, `:2452`); an escalated row and a deferred row are the same thing with the operator as the queue. What used to be a decision either reproduces — fixed, or held as a written patch — or it is dropped.

### D3. The floor — provisional at the engine, resolved at the stamp; exactly two ways down

The engine returns `severity_floor` computed on the lens's claims: it is **provisional**. The door resolves it at the stamp on what is still **open**: an open reproduced `critical` (unfixed or held) → FAIL; a `held` reproduced `important` → CONCERNS (authority); a still-dead lens → CONCERNS (coverage); a reproduced `important` neither fixed nor held → no verdict at all — `walkthrough_roster.py` refuses the stamp (Part 3) and the caller finishes; everything else → none. **A row closed by a fix and a green pin does not appear.** **Those are the only two CONCERNS grounds** (ruled 2026-09-11): taste — §1 comment-contract gaps, §2 judgment calls — is a count in the record and never a verdict, because a CONCERNS made of taste is a file the operator has to open.

**This is the stop condition the ticket exists to create.** The loop existed because the floor had no legal way DOWN: it was computed from what the lenses returned, fixing never lowered it, so the only road from CONCERNS to PASS was another full fan-out. Now there are exactly two ways down, both machine-checkable and neither a judgment call: a receipt showing the command does **not** fail on the real tree (the row is dropped), or a fix with a test seen red and then green (the row is closed). Any other downgrade is the caller overruling the review, which it may not do. More severe needs no permission — the door's own gates add their own reasons. `SKILL.md`'s severity-axis paragraph says this, and block B pins it.

### D4. One review per lane, and the re-stamp

The engine runs once. After the door's fix batch (reproduced criticals only) the retest is: the pins named in the `fixed` rows, plus the enforcement suite once through the receipt writer. Then a new section:

```
## Code Review (<date>, re-stamp after fixes)

Verdict: PASS|CONCERNS @ <sha>
retest: scoped — pins: <test:case>, … · suite: run_all N/N @ <sha> (gates/suite.json)
review: carried from the one review @ <sha1> — no lens re-run
```

No second `lenses_run:` roster. `walkthrough_roster.py` counts roster headers in the stripped text; a second one refuses the close-out unless a line `re-review: approved by the operator — "<his words>"` is present. The last `Verdict:` still governs (unchanged reader).

### D5. The end-of-review message (the review never pauses)

The door runs lenses → engine → reproduce on the real tree → fix reproduced criticals → gates → stamp → **ends the turn** with one screen: the verdict and sha; the fixed rows (id, pin); the held rows (id, reason, one-line evidence from the receipt, a link to the patch); the out-of-lane rows (id, where they went); the counts of dropped and recorded; and the two words that move it: `approved` (the operator runs the close-out door; held rows close as `ruled`) or `apply <ids>` (the door applies those patches, runs their pins red then green, re-stamps, in one turn). Nothing is a question, and nothing is a recommendation to weigh. Nothing is written under `## Your Actions` for a finding (D2, the `finish` hold).

### D6. `review_scope.py` — what a lens reads, with no cap

```
python3 .agents/scripts/review_scope.py --repo <worktree> --base origin/main \
        [--key <PART-KEY> | --range <sha>..<sha>] [--audit] --out <artifacts>/review/diff.patch
```

Reads `base..HEAD` commits, extracts every `[A-Z]+-\d+` in each subject, and groups commits by part key — a key other than the lane key in the subject is the part (Rule 2's rider convention, `SCC-<parent> rider SCC-<child>: …`); otherwise the lane key. With more than one part in the range and no selector: **exit 2, naming the keys**. A lane whose parts carry no rider keys (this one) selects by `--range`. Writes the diff restricted to the selected commits' files, minus the withheld classes: mirrors (`.opencode/`, `.roo/`, `.claude/`, `.agent/`), generated launchers (text carries `GENERATED by sync-agents`), and records (`_artifacts/`, `_bmad-output/`, `docs/_scc_sops_prds/`). Prints every withheld path with its class, the kept count and bytes. **No byte cap exists; the size of a review is the size of a part.** Measured on the SCC-441 diff by running the built script over `03778605^1..03778605` (2026-09-11): 155 files / 1.46 MB in, **82 files / 618 KB out** — v2 sized this at 81 / 658 KB from a hand count, and the built script is the number that stands. `--audit` applies the commit selection and the record stripping but **keeps every mirror** (D9).

### D7. `repro_receipt.py` — the DOOR's tool; the engine never calls it

```
python3 .agents/scripts/repro_receipt.py run --root <artifacts> --id <finding-id> --cwd <worktree> -- <command…>
```

Writes `<root>/gates/repro/<id>.json`: `{id, result, command, cwd, exit_code, output_tail, sha, dirty_tree, recorded_at}`. There is no `--result` flag; a receipt implies execution. An existing id refuses (exit 2) unless `--replace`. **As built (Part 3):** `result` is one of three words and the script exits with it so a door can branch — `reproduced` (the command failed, exit 0), `not-reproduced` (exit 0 from the command, script exit 1, the finding is dropped), `unrunnable` (a missing executable, exit 127/9009, or `gate_receipt.py`'s unrunnable signatures in the tail — script exit 2). The third result exists because a typo'd command exits non-zero, and a naive "non-zero means reproduced" would stamp every finding whose command is broken. `--cwd` is required, for the SCC-154 reason. The roster gate refuses a `fixed`/`held` row whose receipt does not say `reproduced`. The findings row cites `repro <id>`; `walkthrough_roster.py` resolves the file beside the walkthrough and refuses when it is absent. Same shape as `gate_receipt.py`, kept separate because a gate receipt is one per gate name and a reproduction is one per finding. The lens's own run leaves no receipt — its evidence is the `reproduced: yes` line and the output it pasted, which the engine reads as text.

### D8. The roster (engine step-01)

| Lens | Gets | Tree | Runs | How | Reproduction |
|---|---|---|---|---|---|
| Edge Case Hunter | `DIFF` + `REPO` | own worktree copy | always | the `bmad-review-edge-case-hunter` skill + the hunter contract | required on every critical/important, **run by the lens** |
| Acceptance Auditor | `DIFF` + `STORY_FILE` + context docs | own worktree copy | `review_mode: full` | the auditor rubric | required — a command or grep that shows the specified behaviour absent, run by the lens |
| Test-Adequacy Auditor | `DIFF` + `REPO` | own worktree copy | always | the auditor rubric | required — the mutant or the input under which the test still passes, run by the lens |

Blind Hunter, Literal-Correctness, the two levels, `lens_budget`, `EVIDENCE_PACK` priming, the verify wave and the compound role are retired with one paragraph naming SCC-447 and the measurement (7 historical criticals: this roster retains 5; Blind was sole source of 1, Literal of 1; Literal cost 1,082 s / 147,814 tokens per run and set the wall clock). `lenses_counted: 3/3`. The `dispositions:` line keeps its three-count shape, relabelled `<lens>=<reproduced>/<dropped>/<recorded>` (`_DISPO_RE` checks presence only, so the parser is untouched).

### D9. The self-audit — what shares, what must NOT (unchanged from v1)

Neither self-audit twin fans out (no subagent, launch, parallel or isolation instruction in either); its three lenses are sections one reader works through, so the fork saving has nothing to share and pre-work has no diff. It already holds the stop condition the review lacked: anchor-or-delete, a roster fixed at three, caps rejected by name, a Lens 3 that cannot originate. Two shares land: POST-DEV mode resolves its change set through `review_scope.py --audit`, and Lens 2 states the scope asymmetry — a review strips byte-copy mirrors because a defect in a copy is a defect in its master; a **parity** audit's whole question is whether the copies agree, so `--audit` keeps every mirror. Both edits sit outside every `twin-law` fence (verified: fences end at smh:115 / cicd:108; the post-dev sections start at smh:220 / cicd:207).

### D10. Parts in sequence — and why THIS lane is reviewed at the tip

Rule 2 already sequences the BUILD by the overlap map. The added law: **each part is reviewed on its own commits before the next part starts**, the scope script selects the part (`--key` for rider parts, `--range` otherwise), and the enforcement suite at each part's close and at the tip is the integration check across parts — no lens is. `/smh-plan-task` Step 2.5 and `/smh-dev-task-tests` Step 1.5 warn when a part's declared set exceeds 40 master files: split it at plan time, when splitting is free.

**This lane is the one exception, and the plan says so rather than pretending.** The doors that would review each part are the lane's subject: until Part 4 lands, `/smh-code-review` passes `lens_budget`, expects `findings: <d> decision · <p> patch`, runs the judgment half of the clean-code audit inside the review, computes a floor that binds, and has no `## Reproduce` step. Reviewing Part 1 under that door reviews to the old law. So this lane is reviewed **at the tip, under the finished doors, as two scoped reviews by `--range`** — one over Parts 1–3's commits (doctrine, scope script, gates), one over Parts 4–6's (doors, lanes, records). The declared set holds 60 paths, of which 42 are masters after the nine `.opencode/` mirrors, six `.claude/` copies and three `docs/_scc_sops_prds/` records are stripped — two over the size-warning threshold, which is why it is two reviews and not one. Per-part review binds from the next lane.

## Step 1.6 — subtasks

None. Every piece is the same lane class in the same repo and shares files (the SOP, the engine, the doors); by Rule 2 they are parts of one lane. Commit subjects carry `SCC-447 <part-word>:` — `doctrine`, `scope`, `gates`, `doors`, `lanes`, `records` — so the tip's two `--range` selections fall on part boundaries.

## Parts, in order — each: RED first, then the edit, then GREEN, then one commit

⛔ **A part's test runs need the operator's word, and his `approved` on the part IS that word** (standing instruction 2026-09-11, corrected the same day: *"I just said approved? What is the issue?"*). Each part's RED and GREEN run are named below with what they should print; the agent runs them on the approval and never asks a second time. Part 6's full suite is asked for separately.

### Part 1 — the doctrine (rows A, B) — `SCC-447 doctrine: …`

**Landed at `9b127e09` under v2's policy; corrected to D2/D3 as ruled in the commit that carries v3** — the §6.5 table, §7's two grounds, step-03's two buckets, step-04's single box, SKILL's return block and `DEFERRED_WORK` row, the jira.md and artifacts-always-first vocabulary, SOP §③ + the close-task line + the changelog row, with 20 rewritten content checks and 4 new identifier bans RED first (`test_review_disposition.py` 261/322 → 322/322; `test_finding_record.py` 8/10 → 10/10; `test_review_engine.py` 414/423 → 423/423). The bullets below are v2's as built and are annotated where v3 changed them.

**RED:** `test_review_disposition.py` blocks A and B (72 content checks, every one with a counter-example the harness applies in memory and must reject; 5 identifier bans over the five engine files with anti-vacuity; twin and cache byte-equality). Expected: all 72 content checks red, the byte-identity rows green. **In the same commit**, the sibling pins that go red on the edit — and the number is the honest size of this part: `test_review_engine.py` has 264 CHECKS rows, of which all 78 targeting step-02, ~36 step-01 rows naming the Blind Hunter / Literal lens / pack / levels, ~10 step-03 bucket rows and ~4 step-04 record rows retire or are rewritten (~130 rows, half the file), plus its §2a SCC-203 byte-comparison block (names the Blind Hunter) and the SKILL `lens_budget` input row; `test_lens_roster_contract.py`'s SCC-147, SCC-203, SCC-230, SCC-232 and SCC-301-B2b checks (`QUICK_TOKEN = "≤3 source files"`, the `| **Blind Hunter**` row read at :209); `test_finding_record.py`'s five pins on `[Review][Decision]`, `[Review][Patch]`, `blind+edge` and the `<survived>/<dismissed>/<relevance-killed>` line (**AUDIT FINDING 3** — undeclared in v1); `test_review_fixture.py:550`'s `| lens_budget | standard | standard |` pin (**AUDIT FINDING 6**). Their old pins going red on the edit is the proof they were live.

**Edits:**
- `.agents/rules/code-standards.md` §6.5: the three questions gain **Gate 0** above them — *"A `critical` or `important` that did not reproduce does not exist"*, the receipt command, "no `--result` flag — a receipt implies execution", the measurement — and "Fix what passes all three" becomes the D2 table and *"A reproduced finding is fixed. There is no third bucket."* (v3) §7: FAIL = an open reproduced `critical` at the stamp, whatever the reason; CONCERNS = coverage or authority, nothing else (v3); PASS = every lens ran and no open reproduced finding; three paragraphs — the floor at the stamp on open rows, CONCERNS ships on the operator's word (no command, door or agent may treat it as a blocker on its own authority), one review per lane (a second roster needs the operator's written word and `walkthrough_roster.py` refuses one without it). Twin: byte copy to `.claude/rules/`.
- `.agents/rules/artifacts-always-first.md:277–281` (**AUDIT FINDING 4** — undeclared in v1): the findings-table vocabulary becomes `fixed @sha · pin / held — reason · repro · patch / out-of-lane — where / dropped — no reproduction (count) / recorded (count)` (v3), and "any code/test diff between that SHA and HEAD invalidates the verdict" becomes "invalidates the **suite evidence** — re-run the pins and the suite and re-stamp; the lenses are not re-run". No twin exists.
- `.agents/rules/jira.md:562–566` (**AUDIT FINDING 5** — undeclared in v1): "the relevance gate" → "the reproduction gate"; "Every survivor is fixed in the same lane" → "a reproduced `critical` or `important` is fixed in the same lane; a fix the agent may not apply alone is held as a written patch" (v3). No twin exists.
- `.agents/skills/code-review-engine/steps/step-01-review.md`: the assessor section keeps its ruling and adds Gate 0 with the three-layer split; the lens table becomes D8 (the `How` column stays — it is the wiring; the `EVIDENCE_PACK` column goes); the hunter contract gains three blockquoted bullets — the two required fields, **"RUN IT YOURSELF, in your own copy, before you report it"** with "if it does not fail the way you predicted, you have not found a defect — delete the finding", and the `reproduced: yes` + output line; the auditor rubric gains the same requirement adapted to an absence; the retirement paragraph names every retired piece and the measurement; `## The two levels`, `### lens_budget`, the Literal-Correctness section, the SCC-203 Blind Hunter drop rule and the evidence-pack section are removed; the lens-roster contract keeps its invariant, the dead-lens ladder, `review_runtime`, and skipped-by-mode (Acceptance under `no-spec`); every paste-ready `lenses_run:` example is rewritten with the three lenses, **unfenced** (`test_doc_examples_parse.py` extracts them and runs the real parser).
- `steps/step-02-verify.md`: a pass-through — *"This step runs nothing."* The wave is retired (2 refutations in 18 reviews; step 3's reproduction gate replaces it); findings travel unchanged with `verification: none`; `notes` records `verify wave: retired (SCC-447)`.
- `steps/step-03-triage.md`: §1 gains `reproduce`, `expected_wrong_output`, `reproduced` fields and the three surviving `source` values; §2 loses the revised-severity paragraphs; §4 becomes *"The reproduction gate, then the bucket"* — the presence gate (missing any field → drop; a lens that did not run its own command has not met the contract → drop), then **"This engine cannot run it, by design"** (no Bash), **"The CALLER runs the command again, on the REAL tree, through `repro_receipt.py`"** with SCC-295 as the named reason; the two buckets `fix` / `drop` (v3 — `held` and `out-of-lane` are the CALLER's dispositions and are named as such); `decision_needed`, `escalate` and `defer` retired with their reasons; "fixed in this thread, never a ticket"; §5 becomes *"on the rows that are still OPEN at the stamp"* with the D3 table (held critical → FAIL; held important → CONCERNS; neither fixed nor held → the stamp is refused), "A row closed by a fix and a green pin does not appear here", and **"CONCERNS is not a stop"** pointing at §7.
- `steps/step-04-record.md`: one record box `[Review][Fix] … · repro <id>` (v3 — the Escalate and Defer boxes are retired, and the retirement is stated with its ruling); `src=` short names `edge`, `acceptance`, `test-adequacy` (a joined src is `edge+test-adequacy`); summary line `findings: <f> fix (<d> dropped — no reproduction · <r> recorded)` (v3); `dispositions: per-lens: <lens>=<reproduced>/<dropped>/<recorded> · …`; the boundary keeps "never applies fixes" and gains "never runs a command".
- `SKILL.md`: description — the lenses **reproduce** what they find; the input table drops `lens_budget`, `EVIDENCE_PACK` and (v3) `DEFERRED_WORK`, `ARTIFACT_DIR` stays optional (the engine writes no receipts); the flow lists step 2 as *pass-through (the verify wave is retired, SCC-447)*; the return block matches step-04; the severity-axis paragraph becomes D3 — *"The floor this engine returns is **provisional**, and the caller resolves it at the stamp"*, exactly two ways down, both evidence; "What the engine does NOT do" loses `decision_needed` and gains "run a command".
- `.claude/skills/code-review-engine/` — byte copy of the five files.
- `.agents/skills/INDEX.md:29` engine cell: `lens fan-out → verify → triage → record … returning a severity floor` → `three lenses that reproduce what they find → triage → record, returning a provisional floor the caller resolves at the stamp`.
- The negative-control fixture (**AUDIT FINDING 6**): `fixtures/nc_review_engine/README.md` rows 29/31 re-attribute `NC_BLIND` and `NC_LITERAL` to the Edge Case Hunter (it reads the diff and has uncapped repo access — the file cap that made `NC_LITERAL` Literal-only was the retired lens's), row 51's `lens_budget` row deleted, the top-up paragraph at :112 rewritten; `manifest.json` `"lens": "blind"` / `"literal"` → `"edge"`; `test_review_fixture.py:550` pin retired.
- `test_review_engine.py`, `test_lens_roster_contract.py`, `test_finding_record.py`, `test_review_fixture.py`: as sized under RED.
- DELETE `evidence_extract.py` + `test_evidence_extract.py` (the approval covers both DELETE rows; `test_command_surfaces.py:3932` keeps its comment, `run_all.py` discovers tests by glob so nothing is unwired); `.agents/scripts/INDEX.md` rows 33 and 47.
- SOP §③ (:636–730) in present tense — the level paragraph, the relevance-gate aside, the dispositions sentence at :698, the verdict table; changelog row.

**GREEN:** `test_review_disposition.py --case "A ·"`, `--case "B ·"`; `test_review_engine.py`; `test_lens_roster_contract.py`; `test_finding_record.py`; `test_review_fixture.py`; `test_doc_examples_parse.py`. Paste the totals.

### Part 2 — the scope script (row D) — `SCC-447 scope: …`

**RED:** `test_review_scope.py` against a temp git repo built in the test: (1) mirrors, generated launchers and records withheld, masters kept, bytes reported; (2) commits grouped by key, rider key wins over lane key; (3) a two-key range with no selector exits 2 naming both keys; (4) `--key` selects one part's files only; (5) `--range` selects explicit commits; (6) `--out` writes the patch and prints kept/withheld counts; (7) an empty selection exits 2, never a clean patch; (8) `--audit` keeps every mirror and still strips records — proved by the same fixture returning a mirror path under `--audit` and not without it.

**Edits:** `.agents/scripts/review_scope.py` (new, stdlib; the docstring carries the SCC-441 measurement, the rider-key convention, and the D9 asymmetry paragraph); `.agents/scripts/INDEX.md` row; SOP §11 paragraph + changelog row.

**GREEN:** `test_review_scope.py` bare.

### Part 3 — receipts and the roster gate (row D) — `SCC-447 gates: …`

**RED:** `test_repro_receipt.py`: writes the json with the true exit code and output tail; an existing id refuses without `--replace`; a dirty tree is recorded; no `--result` flag exists (argparse rejects it). `test_walkthrough_roster_dispositions.py` on synthetic walkthroughs dated after `DISPOSITION_CUTOFF = "2026-09-12"` (a **literal** — E4c: a computed cutoff exempts its own lane): a fixed `nitpick` row refuses; a `fixed` row without `pin` refuses; a `fixed`/`held` critical/important whose `repro <id>` file is absent refuses and names the path; a `held` row whose `patch <path>` is absent refuses; present → passes; PASS with an open critical refuses (a held critical is open); PASS or CONCERNS with a reproduced `important` that is neither `fixed` nor `held` refuses and says "finish the fix"; a held important under CONCERNS passes; two roster headers without the operator line refuse; with the line, pass; a re-stamp section with no roster reads the earlier roster and passes; a pre-cutoff walkthrough (SCC-441's own) is untouched. `test_walkthrough_roster.py` gains **NA4** (**AUDIT FINDING 7**): a `fan-out` lane whose only `n/a` row reads `acceptance · n/a — skipped-by-mode (no-spec)` PASSES; NA2 (a contaminated drop under fan-out BLOCKS) unchanged. `test_task_preflight.py` gains one case: the FAIL refusal names "pins and the suite" and never "re-run the review".

**Edits:** `.agents/scripts/repro_receipt.py` (new); `.agents/scripts/walkthrough_roster.py` — a findings-table parser (header row must carry a `sev`/`severity` and a `disposition` column; other columns free), the refusals above inside `judge()` after the `DISPO_CUTOFF` block, the second-roster count in `parse()`, the `:373–384` fan-out refusal exempting rows whose reason carries `skipped-by-mode` (today it refuses ANY `n/a` under fan-out, and once the Blind Hunter is gone the mode-skip is the only `n/a` left — every spec-less fan-out review would be refused at close-out), the `:443` message relabelled to the D8 shape; `.agents/scripts/task_preflight.py:1618` one string; `.agents/scripts/workflow_lint.py:114–122` (**AUDIT FINDING 2**): the `("code-standards", "producing findings", …)` trigger gains a fourth alternation `fixed\s*/\s*held\s*/\s*dropped` so a door written only in the new words still owes the §6.5 pointer (one case in the lint's test); `.agents/scripts/INDEX.md` row; SOP §10/§11 paragraphs + changelog row.

**Mutation sweep** over `review_scope.py`, `repro_receipt.py`, `walkthrough_roster.py`: the table declared in `sweep.json` (the `mutation_sweep.py` schema — `test`, `mutants[]` of `id/file/original/mutated/case/block`) before mutating; mutants drawn from the code, never from the cases: drop a withheld prefix; invert the two-key refusal; make `--audit` strip mirrors; write the receipt before running the command; drop the `pin` requirement; drop the open-critical floor; drop the neither-fixed-nor-held refusal; drop the patch-presence check on a `held` row; count rosters from the raw text instead of the stripped text; drop the `skipped-by-mode` exemption. Each names the case that must kill it; run through `mutation_sweep.py`, which restores and runs the closing full green itself.

**GREEN:** the three new test files bare, `test_walkthrough_roster.py`, `test_task_preflight.py`, `test_workflow_lint.py`, then the sweep.

**As built (2026-09-11), where the plan's names were off:** the plan's `NA4` label already existed in
`test_walkthrough_roster.py` (`NA4 · (control) lenses_na: none`), so the mode-skip case is **NA7**, with **NA8**
as its control (a mode-skip beside a contaminated drop still blocks — the exemption is per row). The
rule-pointer check is exercised in `test_command_surfaces.py` (block CS-12, which calls the real
`check_rule_pointers`), not `test_workflow_lint.py`, so the fifth-arm case lives there. The rule's own
command line in §6.5 lacked the `--cwd` the script requires; corrected, twin byte-copied. The sweep table
declares **19** mutants rather than the ten named above: the ten, plus width mutants over the new code
(the receipt-result check narrowed, the second-roster threshold moved, the quoted-words requirement
dropped, the fixed-nitpick refusal, PASS over a held important, the receipt writer's three arms, the
lint's fifth arm). RED first: `test_walkthrough_roster_dispositions.py` 14/48 → 48/48; `test_repro_receipt.py`
2/19 → 19/19; `test_walkthrough_roster.py` NA block 7/8 → 85/85 bare; `test_task_preflight.py` new block 0/2 →
141/141 bare; `test_command_surfaces.py` CS-12 28/29 → 345/345 bare; `workflow_lint --toolkit-only` 0 errors.

### Part 4 — the doors (row C) — `SCC-447 doors: …`

**RED:** `test_review_disposition.py` block C: both doors carry the `review_scope.py` call in Step 1 with `DIFF` as its output; a `## Reproduce` step naming `repro_receipt.py` and "on the real tree"; the D2 policy in the fix paragraph; "machine floor only" in the nested Step 3.5; Step 4 resolves the provisional floor on open rows; the D4 re-stamp block; the D5 message contract; no `lens_budget` row; no `twin-law: review-level` fence; no sentence matching `re-run the review|fresh review|fresh lens|invalidates the verdict`; the `.opencode/` copies byte-equal. `test_review_engine.py`'s 14 caller rows (SMH_CMD/CICD_CMD) that pin `lens_budget: standard` are retired in the same commit.

**Edits:** `.agents/commands/smh-code-review.md` and `cicd-code-review.md`: Step 0.7 loses the level-derivation fence (the blast-radius section and its `origin/main` / `origin/$EPIC` pins stay — `test_command_surfaces.py:953–1001` reads them and is untouched); Step 1's input table drops `lens_budget`, `DIFF` becomes the `review_scope.py` output with the command shown; a **`## Reproduce`** step follows the engine's return — every surviving critical/important's command through `repro_receipt.py run` on this tree; not reproduced → `dropped`; the "Then fix in thread" paragraph becomes D2 (reproduced critical or important → fix with pin; Ask First or spec conflict → a held patch; an untouched file → out-of-lane; nothing under `## Your Actions`); "The engine returns a `severity_floor`, and it BINDS Step 4" becomes D3 (provisional; resolved on open rows; two ways down); Step 3.5 nested: "run the machine floor (Step 1 of the audit door) only — the judgment pass is not run inside a review"; Step 4: the findings table header fixed to `| # | file:line | sev | lens | failure scenario | repro | disposition |`, the verdict rules (FAIL = an open reproduced critical, held or not, or a red machine floor; CONCERNS = a held important or a dead lens, nothing else; PASS = nothing open), the re-stamp block, the end-of-review message, and "any code/test diff between that sha and HEAD invalidates the **suite evidence** — re-run the pins and the suite and re-stamp; never the lenses". `smh-clean-code-audit.md` and `cicd-clean-code-audit.md`: one line under Step 2 — "nested inside a review, this pass does not run (SCC-447)" — and the judgment pass's "caps at CONCERNS" (description, Step 2 heading, gate legend) becomes "recorded, never a verdict", because §7 as ruled 2026-09-11 has exactly two CONCERNS grounds and taste is not one of them. `smh-close-task-merge-tree.md:301`: the severity-triage sentence narrowed to D2. All five `.opencode/` mirrors byte-copied. SOP §③ and §`/smh-code-review` (:2339) in present tense; changelog row.

**GREEN:** `test_review_disposition.py --case "C ·"`, `test_review_engine.py`, `test_command_surfaces.py`, `test_twin_parity.py`, `workflow_lint.py --toolkit-only`.

**As built (2026-09-11), with the deviations and one defect this part found in the lane's own work.**

The new law is carried in NINE `twin-law:` fences rather than ported prose, so `test_twin_parity.py` holds it byte-identical between the two doors and a half-port cannot ship: `review-scope`, `reproduce-gate`, `disposition-policy`, `floor-at-the-stamp`, `nested-machine-floor`, `findings-table`, `verdict-rules`, `one-review-per-lane`, `end-of-review` — parity went 68 → 76 checks on them, and the retired `review-level` fence left with the axis. The reproduce step is numbered **Step 1.4** in both doors, which is the only number free on both (the Task door's next step is 2, the story door's is 1.5). The end-of-review screen is its own **Step 6**, after the walkthrough refresh, because the message has to describe a record that already exists. Three sentences outside the plan's list were corrected because the new fences contradicted them where they stood: the Task door's acceptance-audit "CONCERNS floor" for an unevidenced item (now: run the assertion, or the item is undelivered and that is this lane's own FAIL reason), the story door's "`unrunnable` receipt caps the verdict at CONCERNS" (now: the floor is unrunnable, report it and name the fix), and the story door's Step 4 "any code/test diff invalidates the verdict" (now: the suite evidence).

⛔ **Both doors were still instructing agents to run a lens this lane retired in Part 1.** Six sites each: the Step 0.9 tail ("the engine **drops** the Blind Hunter rather than faking it"), the Task door's Step 1 heading and its "evidence-verification pass" (the verify wave, also retired), the ordering paragraph's "that lens is starved of context on purpose", the example roster's `- blind-hunter · ok` row, and the `twin-law: roster` fence, whose whole justification was the contaminated-Blind-Hunter drop. `test_review_engine.py` was *pinning* the drop clause as shared law, so it protected the stale sentence in both doors. Fixed here because the doors are Part 4's subject: the inline obligation that survives is the one the roster can still break — under `inline` every lens comes back `recovered-inline` and the roster may not read as a more independent review than the one that ran — and the example roster is now a spec-less review (`2/2`, with `acceptance-auditor · n/a — skipped-by-mode (no-spec)`, which is the one legal `n/a` and the row Part 3's exemption reads).

`test_review_engine.py`'s `lens_budget` rows were retired and **inverted** rather than deleted: the two caller-row checks are gone with their reason recorded, and the pair of loops that counted one row per interactive caller and required every discovered caller to name a budget is now one loop, over **every** discovered caller, asserting the row count is ZERO with an anti-vacuity body row. The failure mode flipped with the axis — from "a caller names none" to "a caller still passes one" — and counting is still what reads it. 417/417.

⛔ **The lane's own enforcement floor was RED and had been since Part 1.** `test_suite_runner.py`'s ORPHAN walker reads the AST and recognises exactly one guard idiom, a `c.check` inside the BODY of an `if c.block(...)`; `test_review_disposition.py` shipped its three `c.check` calls inside a module-level `run_checks(c, checks)` helper, which is outside every block however it is called — those three rows ran under EVERY `--case` filter and counted toward every filtered tally, so a mutant they killed was attributed to whichever case happened to be named. `run_all.py` auto-discovers, so the floor was red at `3964e196`, `27aa4248` and `3233f2e8` and every filtered count in Parts 1 and 3 was three rows high. Fixed here: the helper is `check_rows(checks)` and RETURNS its rows, each block calls `c.check` under its own guard. `test_suite_runner.py` 182/182, exit 0.

RED→GREEN: `test_review_disposition --case "C ·"` 28/209 → 209/209 (531/531 whole file) · `test_review_engine` 413/423 → 417/417 · `test_command_surfaces` 343/345 → 345/345 (the `smh-clean-code-audit` launcher and its `.claude/` cache carry the description, so both were re-emitted by hand) · `test_twin_parity` 68/68 → 76/76 · `test_suite_runner` 181/182 → 182/182 · `workflow_lint --toolkit-only` 0 errors · `check_links --base origin/main` clean · `test_sops_prds_folder` 61/61 · `test_lens_roster_contract` 39/39 · `test_review_fixture` 69/69 · `test_walkthrough_roster` 85/85 · `test_finding_record` 10/10 · `test_task_preflight` 141/141 · `test_closeout_preflight` 136/136 · `test_workflow_lint` 59/59.

### Part 5 — consolidation, planner, autopilot, self-audit (rows E, F, H) — `SCC-447 lanes: …`

**RED:** `test_review_disposition.py` blocks E, F and H: the autopilot's step-3 row for CONCERNS/FAIL contains `escalate` and neither `fix child` nor `fresh`; `never ships by itself` absent from the door, `autopilot_SOP.md:192` and the SOP §15 row; Rule 2 carries "reviewed on its own commits", "`--range` for parts without rider keys" and "the enforcement suite is the integration check"; `smh-plan-task.md` Step 2.5 and `smh-dev-task-tests.md` Step 1.5 carry the 40-master warning; both self-audit twins' post-dev section names `review_scope.py … --audit` and Lens 2 carries the asymmetry sentence, byte-identical across the twins (a drift check of its own — the sentence sits outside the fences `test_twin_parity` compares).

**Edits:** `.agents/commands/cicd-autopilot-claude.md:122` → "**escalate** — post the D5 message on the ticket via `needs_human`; no fix child, no second reviewer; the operator's word moves it" (**AUDIT FINDING 1**: `platforms: [claude]` — no `.opencode/` mirror exists); `docs/_scc_sops_prds/autopilot_SOP.md:192` and the SOP §15 row; `.agents/rules/work-consolidation.md` Rule 2 (D10 sentences; no twin exists); `.agents/commands/smh-plan-task.md` Step 2.5 and `smh-dev-task-tests.md` Step 1.5 (the size warning, after the mode table / after item 1); their `.opencode/` mirrors; both self-audit twins + mirrors (D9); changelog row.

**GREEN:** `test_review_disposition.py --case "E ·"`, `"F ·"`, `"H ·"`; `test_twin_parity.py`; `test_command_surfaces.py`.

**As built (2026-09-11), and the scope this part had to widen to stay honest.**

**The autopilot edit is not one row — it is a stage each route loses.** The plan declared
`cicd-autopilot-claude.md:122` and "the matching row" in `autopilot_SOP.md`. Editing only those two
would have left the manual contradicting itself in six other places: the story route's §4 table and
mermaid still ran child 5 (the fix) and child 6 (the fresh reviewer), the quick-fix route's §5 table
and mermaid ran the same pair as children 3 and 4, both section headings counted children that no
longer exist, and the lane SOP's §18 command atlas carried the whole `R → C5 → C6 → R2` chain. A
charter row saying "escalate" beside a table saying "one fix cycle" is not a fixed lane; it is a lane
that reads whichever half the agent reaches first. So **the story run is four children and the
quick-fix run is two**, in the command, in both of the manual's routes, in both mermaids, in §15's
short version and in §18's atlas — and the retirement paragraph is the same text in the command and
the manual, pinned as one law in both by block E. The seat pins, the dial, the budgets and the
escalation protocol are untouched; only the stages after the verdict are gone.

**Why that is a consequence and not a policy change.** The door now reproduces and fixes before it
stamps, so a non-PASS verdict is one of exactly two things (§7's two grounds): a fix the agent may
not apply alone, already written as a patch, or a lens that never ran. A fix child cannot apply a
patch whose whole problem is missing permission, and a second reviewer is the fan-out D4 forbids.
The stage had nothing left to do.

**One in-lane defect, fixed here.** `test_command_surfaces.py`'s AP1 loop pinned the literal
`second non-PASS` as a charter row the door must name — so the enforcement suite was holding the
retired escalate-on-the-second-verdict shape in place, exactly the way `test_review_engine.py` was
found holding the Blind Hunter's drop clause in Part 4. The needle is now
`no fix child, no second reviewer`, which is the half a re-added loop would have to delete.

**Three sentences rather than one in Rule 2.** The plan's D10 asked for "reviewed on its own
commits", "`--range` for parts without rider keys" and "the enforcement suite is the integration
check". Written as one paragraph that reads as a list of assertions; split into two, the second of
which says *why* no lens is the integration check — a scoped review sees one part by construction,
so the cross-part question belongs to something that reads the whole tree.

**The size warning is the same paragraph in both planners,** by design: `smh-plan-task` Step 2.5
after the mode table, `smh-dev-task-tests` Step 1.5 inside item 1 where the Declared Change Set is
written. Block F asserts the same text in both with the same counter-example, so a warning added to
one door and forgotten on the other fails.

**A new test helper, `one_line()`.** Part 4 hit three line-wrap mismatches — a regex or a
counter-example needing a literal the prose had broken across lines — and each cost a re-wrap. Prose
checks in this part compile through `one_line()`, which matches the words across whatever wrapping
the file uses. The words are the law; where the line ends is not, and binding both together is what
tempts an agent to loosen a check it did not mean to change.

**Beyond the declared set, deliberately:** `autopilot_run.py:615`'s budget comment said "xhigh across
six children" — a comment this change makes wrong, so it says "across every child in a run" (a count
in a comment is the thing that drifts). The lane SOP gained two paragraphs the currency rule owes —
per-part review with the 40-master warning in §11, and the POST-DEV `--audit` resolution beside the
port section — plus the §15 and §18 corrections. And `_artifacts/_main/INDEX.md` gained this lane's
depth-3 row, which `test_check_maps.py` had been refusing since Part 1 (36/37); the row links the
plan and `task.yaml` only, because the walkthrough is Part 6's.

**Evidence, RED first.** `test_review_disposition` block E 15/54 → 54/54 · block F 4/25 → 25/25 ·
block H 4/24 → 24/24 (634/634 whole file) · `test_command_surfaces` 344/345 → 345/345 ·
`test_check_maps` 36/37 → 37/37. Then, all green: `test_twin_parity` 76/76 · `test_suite_runner`
182/182 · `test_autopilot_run` 136/136 · `test_self_audit_contract` 44/44 · `test_review_engine`
417/417 · `test_walkthrough_roster` 85/85 · `test_task_preflight` 141/141 · `test_closeout_preflight`
136/136 · `test_workflow_lint` 59/59 · `test_sops_prds_folder` 61/61 · `test_scope_check` 141/141 ·
`test_lane_qualify` 46/46 · `test_declared_change_set` 59/59 · `test_doc_examples_parse` 22/22 ·
`test_approved_word_is_the_operators` 130/130 · `workflow_lint --toolkit-only` 0 errors ·
`check_links --base origin/main` clean.

### Part 6 — the gate at the tip (row G) — `SCC-447 records: …`

`operator_workflows_quickref.md` (**AUDIT FINDING 8** — v1 declared it conditionally): the three Mermaid diagrams at :717–763 and :958 redrawn — three lenses, no verify wave, `## Reproduce`, two buckets, no `lens_budget`; the SOP's hand-written appendix twins of those diagrams (:3441–3483, :3668–3669 — no generator exists, so both are edits); `workflow_lint.py --toolkit-only` (0 errors); `check_links.py --base origin/main`; `check_maps.py --depth3-only --strict`; `sop_currency.py` on the changed set; then — **on the operator's word, asked separately** — **one** full `run_all.py` through `gate_receipt.py run --task SCC-447 --gate suite`, on a clean tree; the walkthrough with RED→GREEN evidence per row, the sweep record, `## Your Actions`; the Dev Record via `jira_feed.py devrecord`. Then STOP: the two `--range` reviews of D10 run when the operator asks, under the doors this lane just changed.

**As built (2026-09-11), and what the tip's first full suite found.**

**One data table draws both sides.** The quickref's three review diagrams (the story door, the engine, the
task door) and their hand-drawn SOP appendix twins were rendered from one node list — a Python renderer
emitted the mermaid block and the `| ID | label | next |` table from the same labels — so the two cannot
disagree, and block I of `test_review_disposition.py` now holds them there: every node the quickref draws
must be a row in the SOP twin, label for label (the `\n` fold IS the generator, done by hand until now).
That check PASSED on the old tables before any edit, which proved the twins were exact folds, and it is what
fails the next hand that moves one side without the other. Block I also bans every retired token where the
operator reads (Blind Hunter, Literal-Correctness, verify wave, Evidence Verifier, Compound Synthesis,
`lens_budget`, `decision_needed`, a five-lens roster, the fix cycle / new sha / second verdict), pins the
engine blurb as the SAME paragraph in both records, and counts four paired sentences that must appear in
BOTH door diagrams. RED 27/69 → GREEN 69/69; 703/703 whole file. All four diagrams valid under the Mermaid
validator.

**Beyond the plan's three diagrams, in the declared files:** the atlas node (`CRE`) said "5 lenses · verify
wave"; the quickref's autopilot picture still ran the fix child and the fresh reviewer Part 5 retired (the
plan named the three engine diagrams only — a quickref that stops the robot on one page and loops it on
another is the failure mode this ticket exists to kill); and the SOP's gates-table engine row still
described, in present tense, a Blind Hunter DROPPED under a contaminated inline context (SCC-203) and "the
other four" lenses — rewritten to what runs (the only `n/a` left is the Acceptance Auditor's mode-skip; the
ORDER both doors impose is what now protects the review from the builder's framing). Changelog row six.

**The absorb.** `origin/main` had moved (SCC-186's records: a plan, a walkthrough, an INDEX row,
`.maps-state.json`); `git merge-tree --write-tree` dry-ran clean and the merge landed at `8bf95733` before the
certifying run, so the receipt describes the tree that ships.

⛔ **The first full `run_all.py` at the tip was 88/90, and both reds were this lane's own — neither visible to
any per-part targeted run, which is D10's claim made on the lane that wrote it.** (1) `test_boot_epic_branch_read`
A6: the two fences Part 4 added to `cicd-code-review.md` (Step 1's `review_scope.py`, Step 1.4's
`repro_receipt.py`) used `$L` without binding it in that fence — a fence is its own shell, SCC-441's exact
shape; earlier fences have cd'd the shell into the project, so the fix is the door's own line-401 idiom (the
lobby path re-typed), two lines, mirror byte-copied. (2) `test_jira_feed` SCC-335 E1: `review_scope.py`'s two
`subprocess.run` seams decoded with the machine locale; pinned `encoding="utf-8", errors="replace"`, the idiom
`repro_receipt.py` already used. Fixed at `c34edf5f` (`[sop-ok]` — no usage change): 50/51 → 51/51, 20/21 →
21/21; the sweep re-ran over the changed script (19/19); the suite re-stamped **PASS 90/90 @ `c34edf5f`**, 30.8s,
clean tree — `gates/suite.json`.

**The walkthrough** is [walkthrough.md](walkthrough.md): outline, the acceptance→evidence matrix per row A–H,
both suite runs pasted (the red one too — a red receipt is the mechanism working), the ledger, and one open row
under `## Your Actions` (the merge, via the PR the reviews will carry). The Dev Record is filed at stage
`records`; the close-out updates it.

**Then STOP, as the plan says.** The two `--range` reviews of D10 — Parts 1–3 `114deb3a..3233f2e8`, Parts 4–6
`3233f2e8..c34edf5f` — run on the operator's word, under the doors this lane changed.

### The review at the tip — as run (2026-09-12)

**The two `--range` reviews D10 owes ran under the finished doors, and the doors reviewed the doors.** Parts
1–3 (`114deb3a..3233f2e8`) and Parts 4–6 (`3233f2e8..3f482b30`), three lenses each in an isolated worktree,
every `critical`/`important` re-run on this tree through `repro_receipt.py`, every reproduced row fixed here
with a pin seen red, both verdicts **PASS @ `63399ba3`** — 24 reproduced findings fixed, 0 dropped, 0 held, 26
suggestions and nitpicks recorded as counts. The record is the two `## Code Review` sections in
[walkthrough.md](walkthrough.md); the receipts are `gates/repro/*.json`; the certifying run is
`gates/suite.json` (90/90 @ `63399ba3`, clean tree); the sweep is 34/34 with fifteen new mutants (M20–M34).

**What the doors found in their own author, in the order the doors found it.** Before any lens ran, the Step 1
scope cut printed `review_scope.py` withholding ITSELF (`s1`): the "generated" class was a bare substring, and
every master that talks about launchers carries the phrase. Then the lenses: the auditor rubric named "a suite
that comes back green" as a reproduction — exit 0, which the receipt writer reads as NOT reproduced, so no
auditor finding could ever have survived to a fix (`x1`); the receipt writer certified a typo'd `--case` label
(`NO CASES RAN`, exit 3) as reproduced (`e2`) and split a piped command before it ever ran (`x3`);
`KEY_RE` made `UTF-8` and `H-1` in real subjects into phantom parts (`x4`); a prefix was a mirror, so
`.claude/settings.json` shipped unread (`x5`); a keyless tree guessed one part (`a1`); the roster gate refused
the second part's first review as a re-review — the flow Rule 2 mandates (`x6`); `closeout_preflight.py` read
the FIRST stamp while the doors say the LAST governs (`e3`); `<first>..<HEAD>` excluded the part's first commit
(`e4`); the story door's two new fences used variables no fence binds (`e1`); both doors minted CONCERNS on
grounds §7 does not have (`b1`, `b2`); "blind lens first" survived the six-site fix (`b3`); the story self-audit's
fence ran the lobby's script from inside the project (`b4`); and eleven law sentences could be inverted with
every pin green (`t1`–`t3`, `b5`–`b10`, `b7`, `b8`). Every one is fixed at `3f482b30` / `bcd1ba09`.

**Three things the record should carry forward.** (1) The auditor-rubric polarity (`x1`) is the finding that
matters most: the two auditor lenses in this very review only produced usable reproductions because they chose
mutation commands ending in `test $rc -ne 0`; a lens following the rubric as written would have been neutered.
(2) Rosters are now counted PER PART (`x6`): `code-standards` §7 and both doors say one review per part, and a
consolidated lane's walkthrough carries one roster per part under a heading that names it. (3) Two receipts
were taken with the pin as the command and came back `unrunnable` because the pinning test's own output quotes an
unrunnable signature (`No module named`) — the tail-signature heuristic in `classify()` reads a test's printed
detail as its own failure; retaken with the lens's direct command (`e2`). Recorded, not fixed: a suggestion.

**Beyond the declared set:** `.agents/scripts/closeout_preflight.py` and `test_closeout_preflight.py` (row 13
of the Parts 4–6 review) — declared below.

## Declared Change Set

- NEW `.agents/scripts/review_scope.py` — the diff a lens reads: one part, masters only, no cap; `--audit` keeps mirrors → D
- NEW `.agents/scripts/repro_receipt.py` — the door's receipt writer; a reproduction is a receipt → D
- NEW `.agents/scripts/tests/test_review_disposition.py` — the prose pins with counter-examples (blocks A–I; I pins the records) → A
- NEW `.agents/scripts/tests/test_review_scope.py` — the scope script seen red → D
- NEW `.agents/scripts/tests/test_repro_receipt.py` — the receipt writer seen red → D
- NEW `.agents/scripts/tests/test_walkthrough_roster_dispositions.py` — the new refusals seen red → D
- EDIT `.agents/rules/code-standards.md` — §6.5 Gate 0 + the action policy; §7 open rows at the stamp, CONCERNS ships, one review → A
- EDIT `.claude/rules/code-standards.md` — byte twin → A
- EDIT `.agents/rules/artifacts-always-first.md` — §6 findings-table vocabulary; "invalidates the suite evidence", never the verdict (AUDIT FINDING 4) → A
- EDIT `.agents/rules/jira.md` — the review-findings paragraph: reproduction gate, reproduced means fixed, `held` / `out-of-lane` (AUDIT FINDING 5) → A
- EDIT `.agents/skills/code-review-engine/SKILL.md` — inputs, flow, return block, the provisional floor and its two ways down → B
- EDIT `.agents/skills/code-review-engine/steps/step-01-review.md` — three lenses, the lens runs its own command, retirements → B
- EDIT `.agents/skills/code-review-engine/steps/step-02-verify.md` — pass-through → B
- EDIT `.agents/skills/code-review-engine/steps/step-03-triage.md` — presence gate, the engine cannot execute, two buckets, floor on open rows → B
- EDIT `.agents/skills/code-review-engine/steps/step-04-record.md` — record vocabulary, one Fix box → B
- EDIT `.claude/skills/code-review-engine/SKILL.md` — cache copy → B
- EDIT `.claude/skills/code-review-engine/steps/step-01-review.md` — cache copy → B
- EDIT `.claude/skills/code-review-engine/steps/step-02-verify.md` — cache copy → B
- EDIT `.claude/skills/code-review-engine/steps/step-03-triage.md` — cache copy → B
- EDIT `.claude/skills/code-review-engine/steps/step-04-record.md` — cache copy → B
- EDIT `.agents/skills/INDEX.md` — engine row description → B
- EDIT `.claude/skills/INDEX.md` — byte mirror of the skills INDEX → B
- EDIT `.agents/scripts/tests/test_review_engine.py` — ~130 of 264 rows retire or are rewritten (all step-02, the Blind/Literal/pack/level step-01 rows, old buckets and record, the SKILL and caller `lens_budget` rows) → B
- EDIT `.agents/scripts/tests/test_lens_roster_contract.py` — SCC-147/203/230/232/301-B2b pins retired, roster pins → B
- EDIT `.agents/scripts/tests/test_finding_record.py` — the record-box and dispositions pins follow step-04 (AUDIT FINDING 3) → B
- EDIT `.agents/scripts/tests/fixtures/nc_review_engine/README.md` — seeds re-attributed to the Edge Case Hunter; `lens_budget` row and top-up paragraph gone (AUDIT FINDING 6) → B
- EDIT `.agents/scripts/tests/fixtures/nc_review_engine/manifest.json` — `lens` fields follow the README (AUDIT FINDING 6) → B
- EDIT `.agents/scripts/tests/test_review_fixture.py` — the `lens_budget` README pin retired (AUDIT FINDING 6) → B
- DELETE `.agents/scripts/evidence_extract.py` — served only the retired wave (approved with the plan) → B
- DELETE `.agents/scripts/tests/test_evidence_extract.py` — its test (approved with the plan) → B
- EDIT `.agents/commands/smh-code-review.md` — scope, reproduce on the real tree, policy, provisional floor, re-stamp, message, verdict rules → C
- EDIT `.opencode/commands/smh-code-review.md` — byte mirror → C
- EDIT `.agents/commands/cicd-code-review.md` — the same, story-lane twin → C
- EDIT `.opencode/commands/cicd-code-review.md` — byte mirror → C
- EDIT `.agents/commands/smh-clean-code-audit.md` — nested: machine floor only → C
- EDIT `.opencode/commands/smh-clean-code-audit.md` — byte mirror → C
- EDIT `.agents/skills/smh-clean-code-audit/SKILL.md` — generated launcher, re-emitted by hand because Part 4 changed the command's description → C
- EDIT `.claude/skills/smh-clean-code-audit/SKILL.md` — that launcher's `.claude/` cache → C
- EDIT `docs/doc-graph.json` — regenerated by the pre-commit maps refresh on every commit that moves a mapped doc; output, not authorship → G
- EDIT `docs/doc-graph.md` — the same generator's Markdown twin → G
- EDIT `.agents/commands/cicd-clean-code-audit.md` — nested: machine floor only → C
- EDIT `.opencode/commands/cicd-clean-code-audit.md` — byte mirror → C
- EDIT `.agents/commands/smh-close-task-merge-tree.md` — §2 tail narrowed to the policy → C
- EDIT `.opencode/commands/smh-close-task-merge-tree.md` — byte mirror → C
- EDIT `.agents/scripts/walkthrough_roster.py` — findings-table parser, the five refusals, the second-roster count, the mode-skip exemption under fan-out (AUDIT FINDING 7), the relabelled message → D
- EDIT `.agents/scripts/tests/test_walkthrough_roster.py` — NA4: a mode-skip under fan-out passes (AUDIT FINDING 7) → D
- EDIT `.agents/scripts/closeout_preflight.py` — the LAST `Verdict:` stamp governs, as in `task_preflight` (review row e3) → E
- EDIT `.agents/scripts/tests/test_closeout_preflight.py` — block RS: a FAIL then a re-stamp PASS reads PASS; a later FAIL still blocks (review row e3) → E
- EDIT `.agents/scripts/task_preflight.py` — the FAIL message string → D
- EDIT `.agents/scripts/tests/test_task_preflight.py` — one case for the message → D
- EDIT `.agents/scripts/workflow_lint.py` — the finding-producer trigger learns `fixed / held / dropped` (AUDIT FINDING 2) → C
- EDIT `.agents/scripts/tests/test_doc_examples_parse.py` — the `lenses_run:` examples it extracts follow the three-lens roster (declared at review; Part 1 edited it, the plan's GREEN list named it, this block did not) → B
- EDIT `.agents/scripts/INDEX.md` — two new script rows; the two extractor rows removed → D
- EDIT `.agents/commands/cicd-autopilot-claude.md` — step-3 row: escalate (AUDIT FINDING 1: `platforms: [claude]`, no `.opencode/` mirror exists — none declared) → E
- EDIT `docs/_scc_sops_prds/autopilot_SOP.md` — the matching row, and the stage each route loses with it: §4's table + mermaid + heading, §5's table + mermaid + heading, §6's charter row → E
- EDIT `.agents/scripts/autopilot_run.py` — one budget comment this change makes wrong ("six children" → "every child in a run"); no behaviour, `--stage` was never a fixed count → E
- EDIT `.agents/scripts/tests/test_command_surfaces.py` — AP1's charter needle pinned the retired `second non-PASS` row, so the suite was holding the loop in place → E
- EDIT `_artifacts/_main/INDEX.md` — this lane's depth-3 row, red since Part 1 (`test_check_maps` 36/37) → G
- EDIT `.agents/commands/smh-self-audit.md` — post-dev resolves through `review_scope.py --audit`; Lens 2 states the scope asymmetry → H
- EDIT `.opencode/commands/smh-self-audit.md` — byte mirror → H
- EDIT `.agents/commands/cicd-self-audit.md` — the same, story-lane twin (outside every `twin-law` fence — verified) → H
- EDIT `.opencode/commands/cicd-self-audit.md` — byte mirror → H
- EDIT `.agents/rules/work-consolidation.md` — Rule 2: review per part, `--range` for parts without rider keys, suite is the integration check → F
- EDIT `.agents/commands/smh-plan-task.md` — plan-time size warning → F
- EDIT `.opencode/commands/smh-plan-task.md` — byte mirror → F
- EDIT `.agents/commands/smh-dev-task-tests.md` — Step 1.5 size warning → F
- EDIT `.opencode/commands/smh-dev-task-tests.md` — byte mirror → F
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — §③, §`/smh-code-review`, §10, §11, §15 and the command-atlas appendix rows, in present tense → G
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one row per part → G
- EDIT `docs/_scc_sops_prds/operator_workflows_quickref.md` — the three engine diagrams redrawn (AUDIT FINDING 8) → G

Launcher skills (`.agents/skills/<cmd>/SKILL.md`, `.roo/commands/`) carry only each command's description, which this lane does not change, so they are not regenerated — with ONE exception declared above: `smh-clean-code-audit`'s description changed in Part 4, so its launcher and `.claude/` cache were re-emitted by hand (`test_command_surfaces` 343/345 → 345/345 was that). Comments that credit a retired lens by name in unrelated files (`_harness.py:156`, `wf_common.py:282`, `task_preflight.py:944`, `jira_feed.py:2229`, `test_command_surfaces.py:2552/2665/3932`, and eight sibling tests) are history and are not touched.

## Risks, named

- **A new gate refuses once before it settles.** Every roster-parser tier in this house produced one false refusal on its first lane (SCC-210: two round trips). The disposition vocabulary is five words, pinned by tests, and every refusal names the row and the fix. Expect one bump on the first review under it.
- **The lens's self-run is not free.** Each critical/important costs the lens one command in its own copy. On a part-sized diff that is a handful, and it replaces a whole verifier wave. It is the slowest step on a bad diff, and it is the step that should be.
- **Coverage lost, stated.** One of seven historical criticals was Blind-only, one Literal-only; the fence checker SCC-441 added covers the Literal class. And the third "cannot reproduce" case — real, reachable, unproven — is dropped by design. That is the price of ending the debate.
- **Half a test file retires in one commit.** ~130 of `test_review_engine.py`'s 264 rows go with the machinery they pinned. The rows that stay are the ones about the surviving contract (the assessor ruling, the tree half of isolation, the ladder, the roster block). The counter-example discipline is unchanged, so what stays is still self-proving.
- **This lane reviews at the tip, not per part.** D10 says why and what replaces it (two `--range` reviews; 42 masters, two over the threshold). The next lane gets per-part review under the finished doors.
- **The prose pins are one test file.** `test_review_disposition.py` guards the doctrine; the roster parser guards the behaviour. Both, deliberately.

## Not in this lane

The phase-2 fork (lenses forked from a review parent that loaded only the diff — measured 92% saving in the SCC-430 spike; own ticket, measured first on the `nc_review_engine` fixture, which this lane keeps intact for exactly that reason). The three SCC-441 findings escalated in that lane's pass-3 note (own ticket). The labeller's SOP shared-ground rule (untouched).

## Self-Audit (2026-09-11, v2)

**Level:** LEDGER+BLAST — the declared set touches rules, gate scripts, doors on every platform, the tests directory, and carries two `DELETE` rows. **Mode:** PRE-WORK (nothing built; one RED file on disk, unrun). **Runtime:** the three lenses were run inline by the assessor with real commands (outputs quoted); they were not fanned out. **What v1's audit did not do and this one does:** grep the repo for every piece of machinery the lane retires, and classify each hit as law, test, fixture or history.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  declared block parses · NEW judged against origin/main, EDIT/DELETE against the tree AND origin/main · every section/line anchor the plan names re-read · twins and mirrors exist where declared · lane fit · Scope Ledger (NEW × acceptance row)
read:        declared_change_set.py parse → entries=60 incomplete=[] ops={NEW:6, EDIT:52, DELETE:2} (the first draft of this block said 58 — the parser corrected the author's tally, which is what the check is for)
             audit_paths2.py (NEW vs `git ls-tree origin/main`, EDIT/DELETE vs disk + base) → mismatches: none
             SKILL.md:4 → `allowed-tools: Read, Write, Glob, Grep, Task` (no Bash) · step-02-verify.md:241 → "you have no Bash" · bmad-review-edge-case-hunter/SKILL.md, smh-code-review/SKILL.md, cicd-code-review/SKILL.md → no allowed-tools line (inherit)
             task_preflight.py:1618 → `"the review verdict is FAIL - fix on the branch and re-run the "` · workflow_lint.py:114-122 → the `code-standards` trigger with `applied/deferred/dismissed`, `- **FAIL**`, `patch/defer/reject`, `NO-GO` arms · cicd-autopilot-claude.md:122 + autopilot_SOP.md:192 → "One fix child … fresh review child … never ships by itself"
             SOP → `### ③` :636 · `≤3 source files` :662 · `### /smh-code-review` :2339 · `## 10.` :2391 · `## 11.` :2608 · `## 15.` :2924 · appendix rows :3441-3483, :3668-3669 · smh-plan-task.md → `## Step 2.5` :117 · smh-dev-task-tests.md → `## Step 1.5` :178
             twin-law fences → smh-code-review.md:120, cicd-code-review.md:181 (`review-level`) · .claude/rules/ holds ONLY code-standards.md of the four rules edited (artifacts-always-first, jira, work-consolidation: no twin) · .opencode/commands/ holds all nine mirrors declared
             jira_feed.py:1774 `open_actions` + :2452 → `finish` decides Done from the open `- [ ]` rows under `## Your Actions` (the D2 reason `decision_needed` retires)
             Scope Ledger — NEW × row: review_scope.py→D · repro_receipt.py→D · test_review_disposition.py→A(+B,C,E,F,H) · test_review_scope.py→D · test_repro_receipt.py→D · test_walkthrough_roster_dispositions.py→D — no empty cell. Callers: review_scope.py 0 existing, 4 planned (both review doors, both self-audit twins); repro_receipt.py 0 existing, 2 doors + walkthrough_roster reads its files
verdict:     findings below (F3, F4, F5, F6, F8)
```

```
lens:        2 Parity + Blast
checks_run:  repo-wide grep for every retired token (decision_needed · [Review][Patch] · relevance gate · verify wave · Evidence Verifier · Compound Synthesis · lens_budget · review_level · Blind Hunter · Literal-Correctness · EVIDENCE_PACK · evidence_extract · noise-dismissed · relevance kill) over rules, commands, engine, scripts, tests, SOP docs — 41 files, each hit classified · scripts that READ the review section · roster gate refusals vs the surviving roster · test_review_engine.py sized by target · twins · generators · sibling worktrees
read:        41 files carry a retired token. LAW (undeclared in v1): artifacts-always-first.md:277-281 (`applied @ sha / deferred … / dismissed — a relevance kill`; "invalidates the verdict"), jira.md:563-565 ("the relevance gate"; "Every survivor is fixed"). TESTS that go red (undeclared in v1): test_finding_record.py:33-54 pins `[Review][Decision]`, `[Review][Patch]`, `blind+edge`, `<survived>/<dismissed>/<relevance-killed>`; test_review_fixture.py:550 pins `| lens_budget | standard | standard |` in the fixture README. FIXTURE: nc_review_engine/README.md:29,31,51,112 + manifest.json:19,40 attribute seeds to `blind`/`literal`. DOCS: quickref :247,397,717-763,958 (three Mermaid diagrams); SOP appendix :3441-3483, :3668-3669 (hand-written twins; `grep -rln "quickref|mermaid|appendix" .agents/scripts/*.py` → none). HISTORY (kept): 15 comment credits across _harness.py, wf_common.py, task_preflight.py:944, jira_feed.py:2229/2237, run_all.py:63, test_command_surfaces.py:2552/2665/3932, six sibling tests; changelog rows.
             test_review_engine.py → 264 CHECKS rows: STEPS[0]=111, STEPS[1]=78, STEPS[2]=29, STEPS[3]=12, SKILL=18, SMH_CMD=7, CICD_CMD=7, DEV_STORY_CMD=2; rows naming retired machinery by keyword: 90 (STEPS[1] 37 by keyword, ALL 78 by subject)
             test_lens_roster_contract.py → SCC-147 :45-56, SCC-203 :74-78, SCC-230 :91, SCC-232 :139-161 (`QUICK_TOKEN`), SCC-301-B2b :209-211 (reads the `| **Blind Hunter**` row)
             walkthrough_roster.py judge() :373-384 → `if na and data["runtime"] == "fan-out": … return False` — refuses ANY `lenses_na` row under fan-out; parse() :209-235 builds `na` without distinguishing a mode-skip from a drop; test_walkthrough_roster.py:103 NA2 pins "a fan-out lane that drops a lens BLOCKS". Under the surviving roster the ONLY possible `n/a` is `acceptance · skipped-by-mode (no-spec)`.
             walkthrough_roster.py → `_DISPO_RE` :111 checks presence only; :443 message text carries the old three labels. No script parses the `findings:` line or a bucket word (flight_recorder, closeout_preflight, task_preflight, jira_feed grepped).
             test_command_surfaces.py → :953-1001 pins both doors' blast-radius sections (`origin/main` / `origin/$EPIC`), :2177 pins the empty-diff STOP — none touched by Part 4 · test_doc_examples_parse.py → extracts `lenses_run:` examples from the docs and runs the real parser; lens names are not validated (:268-269 are in-test controls)
             test_twin_parity.py:185-189 → FENCED_TODAY comment names `review-level` (a comment; the check compares law maps, so removing the fence from BOTH doors keeps parity)
             git worktree list → the lobby @ 03778605 [main] and this lane only · risk_seam classify → unclassified (markdown repo, SCC-289 — correct)
verdict:     findings below (F2, F7, F9, F10)
```

```
lens:        3 Pre-Mortem (attached to anchored findings only)
checks_run:  the silent one · the fresh-clone one · the own-lane-exempt one · the half-migrated one
read:        F7 shipped without → the first `review_mode: no-spec` review after Part 1 records `acceptance · n/a — skipped-by-mode` under `fan-out` and the close-out refuses it as an SCC-203 drop; the agent's cheapest exit is to declare `inline` falsely or omit the row — both of which the roster gate exists to catch, now defeated by the gate itself.
             F10 shipped as v1 wrote it → Part 1's per-part review runs under the OLD door: `lens_budget` passed to an engine that no longer lists it, `findings: <d> decision · <p> patch` expected from a step-04 that no longer emits it, the judgment audit run inside the review, a binding floor, no `## Reproduce` — a review of the new law under the old law, with every check green.
             F3/F6 shipped without → Part 1's GREEN is red on two files the plan never named; the agent "fixes" them under time pressure at the end of the part, which is the unreviewed-edit shape this lane exists to end.
             cutoff (design) → `DISPOSITION_CUTOFF = "2026-09-12"` literal; the test asserts the literal (E4c).
             fresh clone → the two new scripts are stdlib; the new refusals ride a script the close-out already runs; nothing needs arming.
verdict:     clean — nothing to originate; three narratives attached above
```

| # | anchor | literal text read | consequence | severity | baked in as |
|---|---|---|---|---|---|
| F1 | `.agents/commands/cicd-autopilot-claude.md:3` | `platforms: [claude]` | a declared `.opencode/` mirror cannot exist | medium | no mirror declared (Part 5) |
| F2 | `.agents/scripts/workflow_lint.py:114-122` | `r"`?applied`?\s*/\s*`?deferred`?\s*/\s*`?dismissed`?" … r"\|patch\s*/\s*defer\s*/\s*reject"` | a door carrying only the new words loses the §6.5 pointer requirement silently | medium | Part 3: fourth alternation + one lint case |
| F3 | `.agents/scripts/tests/test_finding_record.py:33-54` | `"- [ ] [Review][Patch] <title> [<file>:<line>] src=<lens>" in t` … `"<lens>=<survived>/<dismissed>/<relevance-killed> · …"` | five of nine checks go red on Part 1's step-04 edit; file undeclared | high | Part 1: EDIT declared, pins follow step-04 |
| F4 | `.agents/rules/artifacts-always-first.md:277,280-281` | `any code/test diff between that SHA and HEAD invalidates the verdict` · `disposition (applied @ sha / deferred — … / dismissed — a relevance kill` | the rule the doors quote keeps the old vocabulary and the re-review sentence; `workflow_lint`'s trigger keys on exactly this text | high | Part 1: EDIT declared |
| F5 | `.agents/rules/jira.md:563-565` | `(`code-review-engine` step-03, the relevance gate)` · `Every survivor is fixed in the same lane` | law pointing at a retired gate and the retired fix-everything rule | medium | Part 1: EDIT declared |
| F6 | `fixtures/nc_review_engine/README.md:29,31,51` · `manifest.json:19,40` · `test_review_fixture.py:550` | `NC_BLIND \| Blind Hunter` · `NC_LITERAL \| Literal-Correctness` · `\| lens_budget \| standard \| standard \|` · `"lens": "blind"` | the negative-control fixture attributes two seeds to retired lenses and its test pins a retired row | medium | Part 1: three EDITs declared; seeds re-attributed to Edge Case |
| F7 | `.agents/scripts/walkthrough_roster.py:373-384` · `test_walkthrough_roster.py:103` | `if na and data["runtime"] == "fan-out":` … `return False, reasons` · `NA2 · a fan-out lane that drops a lens BLOCKS` | after the Blind Hunter retires, the only `n/a` is the Acceptance mode-skip; every spec-less fan-out review is refused at close-out | high | Part 3: exemption for `skipped-by-mode` + NA4 |
| F8 | `docs/_scc_sops_prds/operator_workflows_quickref.md:717-763,958` · SOP `:3441-3483,3668-3669` | `L1["Blind Hunter …"]` · `V["Step 02 — the verify wave …"]` · `T["… decision_needed · patch · defer · dismiss"]` · `lens_budget: standard` | three operator-facing diagrams and their hand-written SOP twins draw the retired engine; v1 declared the quickref only "if the deletion is approved" | medium | Part 6: unconditional EDIT, both surfaces |
| F9 | `.agents/scripts/tests/test_review_engine.py` (ast count) | `STEPS[1]: 78` rows · `STEPS[0]: 111` rows | "step-02 checks updated" under-states a rewrite of ~130 of 264 rows | low (sizing) | Part 1 sized honestly; Risks |
| F10 | plan v1 D7 · `smh-code-review.md:213,229,241` | `\| lens_budget \| standard` · `Every \`patch\` the engine hands back` · `it BINDS Step 4` | per-part review of THIS lane runs the new engine under the old door | high | D10: reviewed at the tip, two `--range` reviews |

### Observations (uncounted)

- `test_twin_parity.py:185-189`'s FENCED_TODAY comment names `review-level`; update the comment when the fence goes (a comment is not law).
- `test_walkthrough_roster.py` uses `blind-hunter`/`blind`/`edge` as synthetic names in pre-cutoff fixtures; the parser never validates names and `DISPOSITION_CUTOFF` exempts them, so they keep passing untouched.
- `Projects/sudo-command-center/` is the published teaching edition (export, never edited in place); it picks these files up on its next export, not by port.

**Sibling landing-order dependency:** none.

Audit verdict: GO
