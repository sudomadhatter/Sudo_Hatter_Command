# SCC-430 — Autopilot v3, the Claude half

**Ticket:** SCC-430 (Subtask of SCC-429)
**Lane:** `chore/SCC-430-autopilot-claude`, cut from `origin/main` at `d70347ba`
**Plan:** [implementation_plan.md](implementation_plan.md) — approved 2026-09-07, recorded at `dbb9c4b0`, stamped `c88f4f60`
**Spike:** [spike.md](spike.md)
**Date:** 2026-09-07

## What this closes, in one paragraph

The autopilot's lead session can now launch one headless `claude -p` child per workflow step, and
the child runs the **existing** door by name rather than a copy of it. Two acceptance rows are
closed: **A**, the S0 spike, which measured six tables against the real CLI and falsified three of
the design's assumptions before a line of the runner was written; and **B**, `autopilot_run.py`
and its negative control, which holds the five rules an LLM cannot keep about itself — a missing
door costs nothing, a reply without a `status` is a failure, a reviewer cannot inherit the
author's session, the door travels as a name and never as text, and the only budget ceiling that
can actually be enforced is the runner's own.

## Task Checklist

- [x] **Row A — the S0 spike.** Six tables measured on CLI 2.1.263, ~$2.06 spent, posted to SCC-430.
- [x] **Row A — the CLI upgrade** (2.1.258 → 2.1.263) on the operator's word; `--append-system-prompt-file` re-probed and found present, `--max-turns` confirmed absent and dropped.
- [x] **Row B — `autopilot_run.py`**, stdlib only, verb `run`, plus the seat renderer's pointer half.
- [x] **Row B — `test_autopilot_run.py`**, 35 cases across 8 blocks, every one seen RED first.
- [x] **Row B — the sandbox question closed** (spike Table 6): `CLAUDE_CONFIG_DIR` relocates the transcript store into a sandbox-writable path, so a sandboxed fork works and costs 92% less than its parent. No settings change, no escalation, no unsandboxed fallback.
- [x] **Row C — the seat renderer.** `render_seat()` builds the `--agents` JSON in memory from the master's frontmatter; the six masters carry `claude-model`, `claude-effort` and `claude-tools`; no `.claude/agents/` file is written.
- [x] **Row D — `jira_feed.py step`.** One comment per child, read back by session id, `needs_human` leading with the `Needs Mr. Hatter` line; self-contained, so `test_jira_start_hook.py`'s fixture still works.
- [x] **Row E — the lead's door.** Charter ruled 2026-09-07 (as proposed) and pasted into the door as its own table; `/cicd-autopilot-claude` rewritten from the v2 four-stage engine to the v3 lead session.
- [x] **Row E — the Autopilot SOP.** `docs/_scc_sops_prds/autopilot_SOP.md` with three validated `flowchart` diagrams; SOP §15 links to it, both atlas entries describe v3, one changelog line.
- [x] **Row F — one real AGY ticket.** Operator chose **AVCH-138** (the 3MB pre-hydration splash) 2026-09-07. Three defects found and fixed before the first child launched, a fourth found BY the run. The work shipped: branch `chore/AVCH-138-splash-image-weight` @ `ee9442ae`, pushed.
- [x] **Difficulty tiers.** `--tier easy|medium|hard`, ruled 2026-09-07 and amended twice by the operator (the Gnat exempt; Sonnet 5 at medium, not Haiku at low). The invariant the table is an instance of — *the reviewer never runs the model that wrote the code* — is asserted for every tier.
- [x] **AVCH-138 closed out** — verified by hand, the 3MB PNG deleted, [PR #96](https://github.com/sudomadhatter/AGY_AVIATIONCHAT/pull/96) **merged 2026-09-07** (112/112 journeys green on CI; the quick fix renumbered 1.6 → 1.8 after a parallel lane claimed 1.6) and the ticket **Done**, dev record on the ticket.
- [x] **Row G — the v2 lane retired.** Ruled 2026-09-07. Five doors, two launchers and the v2 reference page deleted; nineteen referencing files closed out; five things harvested first.
- [x] Row G — the five old doors deleted. Ruling 3 given 2026-09-07 ("delete, but harvest first"); this line duplicates the Row G entry directly above it, written before the ruling landed.
- [x] **Close-out — the Autopilot SOP** (operator direction, 2026-09-07): its own document with its own diagrams, linked from the main SOP, and the upkeep home for the autopilot workflows from then on. Delivered as [`autopilot_SOP.md`](../../../docs/_scc_sops_prds/autopilot_SOP.md) — the same work the Row E entry above records. See *What close-out owes* below.

## Evidence

### The RED run — every case failed against a naive stub first

The plan requires each row-B test to be seen red against "a stub that launches anyway". A naive
`autopilot_run.py` was written first, doing the plausible thing at every decision: launch the
child and let it sort itself out, trust the reply, resume whatever session is handy, paste the law
in so the child cannot miss it, and pass `--bare --permission-mode bypassPermissions`.

```
-- 11/35 passed --
FAILED: D1 a missing door exits 2, D2 ...and claude was NEVER launched, D4 anti-vacuity - a door
that EXISTS does launch claude, S1 a result with no status exits non-zero, S2 ...and the runner
reports it as failed, S3 stdout that is not JSON is failed, not a traceback, R1 a review on a
session id in the ledger exits 2, R2 ...before launching anything, R3 a review that forks another
session exits 2, R4 ...before launching anything, R5 a review wearing a seat exits 2, R6
anti-vacuity - an unseen, unforked, seatless review DOES launch, N1 no door or rule sentence
appears in the runner, N2 the runner never reads a door's body, F1 --bare is never passed, F2
bypassPermissions is never passed, F3 --permission-mode is auto, F8 stdin is closed at the launch
site, B2 ...and so is the seat JSON, across two renders, K2 ...and STILL carries --agents, or the
seat is silently dropped, C1 a run already over its ceiling exits 2, C2 ...before launching
anything (the CLI cap is soft - spike finding 2), C3 ...and the refusal prints what has been
spent, C4 anti-vacuity - under the ceiling it launches
```

Twenty-four failures, one per defect the suite exists to catch. `N1` fired on a single sentence of
`constitution.md` pasted into the stub, which is exactly the drift the rule forbids.

### The GREEN run — the real runner

```
-- 35/35 passed --
```

### Test Suite Ledger

| Suite | Scope | Result |
|---|---|---|
| `tests/test_autopilot_run.py` | the new file, alone | **35/35 passed** |
| `tests/test_autopilot_run.py` | after row C's seat cases | **87/87 passed** |
| `tests/test_autopilot_run.py` | after row D's handoff cases | **106/106 passed** |
| `tests/test_jira_feed.py --case "SCC-430 step"` | the new verb | **17/17 passed** |
| `tests/run_all.py` | the whole workflow-script suite | **82/82 files passed** |
| `mutation_sweep.py` | 9 mutants (rows B–D) | **9/9 killed**, restore verified |
| `mutation_sweep.py` | 5 mutants (row E's charter) | **5/5 killed**, restore verified |
| `mutation_sweep.py` | 2 mutants (row F's routes) | **2/2 killed**, restore verified — after the first pass caught AP6 being vacuous |
| `workflow_lint.py --toolkit-only` | the door's rule pointers | **0 errors** |
| `sync-agents.ps1 -Status` | is any launcher stale? | clean - every invocable file matches |
| `check_maps.py` | drift | all maps & INDEXes agree with disk |

### Anti-vacuity, deliberately

Four cases exist only to stop their neighbours passing for the wrong reason: `D4` (a door that
exists really does launch), `R6` (a clean review really does run), `C4` (under the ceiling it
launches) and `N0` (the drift corpus really holds 12,413 fragments to check against). Without them,
a runner that launched nothing at all would score green on the DOOR, REVIEW and CAP blocks.

### The mutation sweep — nine mutants, all code-derived

A test that has never failed is a claim. The row-B cases were seen red against the naive stub; the
row-C cases were not, so they were swept. Every mutant is drawn from a decision in
`autopilot_run.py`, never from reading the cases and asking what would break them.

| # | mutant | must kill | outcome |
|---|---|---|---|
| M1 | the seat's tools are never emitted | `T4 gnat: tools are the master's claude-tools` | KILLED |
| M2 | the prompt stops naming the master file | `T5 gnat: the prompt names the master file` | KILLED |
| M3 | every seat renders under one constant name | `T1 gnat: rendered under its own name` | KILLED |
| M4 | the seat's model is not carried | `T3 gnat: model is the master's claude-model` | KILLED |
| M5 | a missing door no longer stops the launch | `D2 ...and claude was NEVER launched` | KILLED |
| M6 | the reviewer may fork the author's session | `R3 a review that forks another session exits 2` | KILLED |
| M7 | the run-level ceiling never trips | `C2 ...before launching anything` | KILLED |
| M8 | a reply with no status defaults to done | `S1 a result with no status exits non-zero` | KILLED |
| M9 | a fork stops re-passing the seat | `K2 ...and STILL carries --agents` | KILLED |

`-- restore verified: bytes match, nothing was committed -- ` and the closing unfiltered run of the
whole file exited 0.

**The first pass was 8 killed and one SWEEP ERROR, and the error was the finding.** M3 makes
`render_seat` return `{"seat": ...}`; the parity cases indexed `rendered[seat_name]`, raised
`KeyError`, and the test **file** died mid-run — so the harness printed no `FAILED:` line, the kill
could not be attributed, and every case after that point went unscored. Reading it as a survivor
would have bought a test for a hole that did not exist; reading it as a kill would have certified a
file that silently stops scoring. Fixed at `c1610941` (`.get`, not `[]`), then re-swept 9/9.

### Two defects the row-D cases found, both invisible to every other test

**The failure message named the wrong thing.** `post_step` used `key` as a for-loop variable while
folding the child's artifacts and denials into the comment body, which shadowed the ticket key the
function had been handed. Everything worked — except the one path that matters when something is
wrong, where the runner announced it could not record a step "on denials" instead of naming the
ticket nobody could reach. Caught by `H10`, which asserts the ticket is named.

**A check that could never run.** `cmd_step` carried its own `--status` guard that argparse's
`choices` had already made unreachable. It is now gone: a check that cannot fire is worse than no
check at all, because the next reader trusts it and never tests it. Caught by `R3`, whose evidence
turned out to be argparse's usage line rather than the message the guard was written to print.

Both sit in the HANDOFF block, which exists because neither file's own suite covered the seam:
`test_autopilot_run` stubbed the ticket verb away with `--no-post`, `test_jira_feed` called `step`
directly, and a signature drift between them would have left both suites green while every
autopilot step went unrecorded on the board.

## Decisions taken in this step

**The runner seeds its own Claude config directory, and that is what makes forking possible.**
`~/.claude/projects` is deny-listed by the sandbox, so a sandboxed child answers perfectly and
persists no transcript — and without a transcript there is nothing to fork, which costs the whole
layered saving. `CLAUDE_CONFIG_DIR` moves the store to `~/.local/share/autopilot-claude-home`,
which the sandbox already permits. Two seeds are required there: the OAuth credential, **symlinked
and never copied**, and the workspace trust flag. The trust flag turned out to be load-bearing for
cost rather than for warnings — untrusted, every fork read **zero** cached tokens while still
succeeding, so the bill was the only symptom. What it grants is the repository's own tracked
`.claude/settings.json` allow rows; it widens nothing beyond them, and it is written into the
autopilot's own directory, never into `~/.claude/settings.json` or the repo's.

**The reviewing and default models are pinned in the runner, not passed by the caller.** An
unpinned child inherits `claude-opus-5[1m]` and costs six to twenty times more for the least
valuable calls in a run (spike finding 4). Pinning them in the file means "the reviewer ran on the
author's model" is not something a caller can cause by forgetting a flag.

**`--run-cap-usd` exists because `--max-budget-usd` cannot be trusted.** The CLI's cap stops the
next turn, not the current one: probes capped at $0.05 spent $0.496 and $0.296. The runner sums its
ledger before launching and refuses over the ceiling, which is the only ceiling that holds.

### Row E — what the charter case is actually for

The plan asks for the charter to be pinned by a test rather than by review, and the reason is worth
stating because it is not obvious: **the lead reads the door and nothing else.** Not the SOP page,
not the design record — the door is its whole context at launch. A charter that lived only on the SOP
would be a charter the robot never sees; it would improvise a scope, every step would look entirely
normal, and the first sign of trouble would be an unattended overnight run doing something that was
never approved.

Five mutants, each drawn from a row of the charter, all killed by their declared case:

| # | mutant | must kill | outcome |
|---|---|---|---|
| E1 | the file-deletion escalation row is dropped | `AP1 …names deleting a file` | KILLED |
| E2 | landing becomes something the lead may do | `AP3 landing is marked NEVER` | KILLED |
| E3 | the `code-standards.md` citation is removed | `AP4 the door cites code-standards.md` | KILLED |
| E4 | the door stops pointing at its own manual | `AP5 the door points at the Autopilot SOP` | KILLED |
| E5 | the second-non-PASS row loses its limit | `AP1 …a second non-PASS review` | KILLED |

Restore verified byte-identical against the pre-sweep sha; the closing unfiltered run of the whole
file exited 0.

### Two gates that caught real gaps in row E

**The reverse door check refused the commit**, and it was right to. Rewriting §15 dropped the rows
for `/cicd-autopilot-opencode` and `/cicd-autopilot-deepseek4` — but those files still exist, so the
operator would have had two commands he could type and no page describing either. They keep their
rows until row G actually deletes them.

**`check_maps.py` and `refresh_maps.py` appeared to disagree**, each making the other stale. They do
not: `check_maps` counts `.md` files from disk, `refresh_maps` counts them from git's index, and the
new SOP page was still untracked — a one-line difference in a folder's file count. Staging it settled
both. Worth writing down because the symptom (two repair commands undoing each other) points nowhere
near the cause.

### Row F — three defects found by aiming the door at a real ticket

The plan asks row F to run the door on one real story, and the value showed up before a single child
launched. **All three defects live in the gap between what the runner CHECKS and what the child
EXPERIENCES**, which is exactly the gap no unit test can see, because every test in this lane
launches a stub rather than a child.

| # | What was wrong | Why no test could see it | Fixed by |
|---|---|---|---|
| F-a | The door knew only the ①②③ story route. AVCH-138 is a project **Task** — no story file, no sprint row, no epic branch | The suite checks the charter's rows, not whether a real ticket fits one | The quick-fix route, `AP6` |
| F-b | The CLI floor's stated reason was **false**, and the flag it existed for was never passed | The floor is prose in a door; nothing executed it | `--permission-prompts none`, `F3b` |
| F-c | `resolve_door` fell back to the RUNNER's repo, green-lighting a door the **child** cannot load | Every test passes a cwd that owns its door, so the fallback never fired | cwd-only resolution, `D5`/`D6` |

**F-b is the one worth reading twice.** The door refuses below CLI 2.1.259 and told you the reason
was that `--agents` and `--json-schema` are absent below it. Measured on this box: both are present
on 2.1.258. A floor whose stated reason is false is a floor the first inconvenienced reader correctly
talks themselves past — and the real constraint goes with it. The genuine reason is
`--permission-prompts none`, whose default is `host` ("the SDK host or `--permission-prompt-tool`
answers"). A child launched by this runner has **neither**, so an unattended child that hit a
permission prompt had nobody to answer it. The runner never passed the flag, so the floor was buying
nothing at all.

**F-c is SCC-70 reappearing inside the function written to prevent it.** Rule 1 of the runner says a
door is a file, resolve it and refuse before spending anything. Its implementation then fell back to
the runner's own repo root — so pointing a child at a thin project PASSED (the runner could see the
door in its own tree) and launched a child with no such slash command at all: nothing above it,
improvising a workflow, reporting success. Measured: `Projects/AGY_AVIATIONCHAT` carries tier-2 law,
no `cicd-*` door and **0** skills, and `~/.claude/skills` is empty, so nothing would have loaded.
The centre is now a diagnostic only, and the refusal distinguishes *"no such door"* from *"that door
exists, but not where you pointed the child"* — completely different fixes.

### The sweep caught one of my own tests being vacuous

`AP6` first read `"/cicd-quick-dev" in body`. Mutant F1 deleted the route's dispatch row and the case
stayed **green**, because the paragraph two lines below the table still names the door. A route is a
ROW — a door and the seat that wears it — so that is what it counts now. Worth recording because it
is the failure `tests-must-gate-for-real` names: a check that passes for a reason unrelated to the
behaviour it claims to protect, and only a declared mutant found it.

| # | mutant | must kill | outcome |
|---|---|---|---|
| F1 | the quick-fix route's dispatch row is dropped | `AP6 …dispatchable quick-fix route row` | KILLED (after AP6 was tightened) |
| F2 | the door stops explaining why a seated child's review is a first pass | `AP7 …cannot fan out review lenses` | KILLED |

### One environment fact the operator needs

`~/.local/bin/claude` still points at **2.1.258** — below this lane's own floor — while **2.1.263**
is installed beside it and is what the interactive session runs. The symlink never moved after the
upgrade. Row F's first child is pinned with `--claude` by hand; the standing fix is `claude update`
or repointing that symlink, after which the pin comes out of the call.

### Row F — the real run, and the fourth defect it found

One child, one door, one ticket.

| | |
|---|---|
| door · seat · stage | `/cicd-quick-dev` · `cheshire-cat` · 1 |
| session | `fe0d0248-58fc-409a-8786-a404068b24f0` |
| wall clock | 22m 40s (`duration_api_ms: 1359765`) |
| cost | **$5.82** against a $6 soft cap — it stopped itself rather than overrun |
| result | `chore/AVCH-138-splash-image-weight` @ `ee9442ae`, committed **and pushed**, 16 files, +234/-29 |
| ticket | comment **10477** — stage, door, seat, status and session id, posted by the runner |

**What the child actually did.** `Dark Mode Earth.png` 3,169,191 bytes → WebP **150,356** bytes (95%
smaller, under the ticket's own 200KB bar), applied across all nine consumers; the favicon split into
its own 6.7KB file so `AviationChat.png` is fetched once rather than twice; two new tests written
(W7 byte budget, W8 the favicon no longer shares a URL) and `investor-weight.spec.ts` run **9/9
green**; a walkthrough and an acceptance-criteria file written.

⭐ **The charter fired, unprompted and correctly.** The old 3MB PNG was left unreferenced by its own
change, and the child **refused to delete it** — *"the constitution requires asking before any
delete, so I left it and named the one-line fix"*. Nobody reminded it. That row of the charter was
the one the operator was most entitled to be nervous about, and it held on the first real run.

### The fourth defect — and it is the v2 war story happening to v3

The step was recorded **`failed`**, and the ticket comment read:

```
no usable status in the reply: {'duration_api_ms': 1359765, 'stop_reason': 'end_turn', ...}
```

The child answered in prose rather than the JSON shape. `--json-schema` **shapes** a reply and does
not guarantee one — design rule 3 already said so, which is why the status is correctly `failed`:
nothing may guess a status, or a silent no-op is recorded as work.

⛔ **But the runner then threw away the child's own words.** The prose arrives in `result` as a
non-JSON string, so `inner` became `None` and the code fell back to the envelope — printing a
duration in milliseconds as the sole record of a $5.82 run that had answered every question an
operator would ask. **UNREADABLE and UNVERIFIED are different problems, and only the second was ever
intended.** A failure now carries the child's report verbatim, and the door's exit-1 row says to read
it and the worktree *before* retrying, because `failed` here meant *done but unverified* and a blind
retry pays twice.

This is precisely what the retired lane had already learned — *"a stage that did everything right but
phrased its verdict in natural language got stamped CRASHED… trust the artifacts, not a token"* —
harvested into §7.5 of the SOP about an hour before the run reproduced it live.

**What row F could NOT prove:** an escalation reaching the phone as a `needs_human` ticket comment.
The child *did* escalate, correctly, but in prose — so it never became a structured `needs_human`
step. That path stays unproven until a child returns the schema with `status: needs_human`.

### Closing AVCH-138 — verifying a robot's work when the operator cannot see it

The operator's instruction was the interesting part: *"if its fixed delete the huge file just verify
this its work is good. I am blind of this one."* That is the real question this lane will keep
facing — **how do you check an unattended agent's work in a domain the operator cannot inspect?**

What a code review would have caught anyway: no surviving references (three hits, all comments
recording the before-measurement), all nine consumers switched, `tsc` and `eslint` clean across the
changed set while the repo's pre-existing errors sit in files this diff never touched.

⭐ **What it would NOT have caught, and this is the one worth keeping.** The WebP **dropped the PNG's
alpha channel**. Nothing in the diff says so, no test measures it, and the pixel difference was
0.30% — everything looked fine. Had that channel carried real transparency, those pixels would have
flattened to black on the splash of **every route in the product**, and the first person to know
would have been a user. So it was checked rather than inferred: the original is **fully opaque** —
minimum alpha 255, zero transparent and zero partially-transparent pixels across all 2,073,600. The
channel carried no information and dropping it is pure saving.

**The lesson for this lane:** when the operator cannot see the output, "the tests are green" is not
verification — the tests only cover what someone thought to measure, and a re-encode's *shape* and
*transparency* were not among them. Reach for the property the change could silently break and
measure it directly.

| | |
|---|---|
| ticket | AVCH-138, `chore/AVCH-138-splash-image-weight` @ `e804c03e` |
| PR | [#96](https://github.com/sudomadhatter/AGY_AVIATIONCHAT/pull/96) |
| shipped | 3,169,191 B → **150,356 B** (95%), favicon split out, 3MB PNG deleted |
| board | no `In Review` state exists on this project — the ticket stays **In Progress** until the operator merges |

## What close-out owes

**A dedicated Autopilot SOP, with diagrams** — the operator's direction on 2026-09-07, in his words:
a new SOP document *"for the Auto Pilot SOP with its own mermaid diagrams and stuff so I can
visualize this"*, linked from the main SOP, and *"the one we use to upkeep the AutoPilot
workflows"* from then on.

`docs/_scc_sops_prds/autopilot_SOP.md`, and the main
[`workflows_testing_SOP.md`](../../../docs/_scc_sops_prds/workflows_testing_SOP.md) links to it from
§15 rather than growing a second copy of the same prose — the same retire-don't-accrete habit the
`sop-currency` rule already demands of that page. What it has to carry: the three layers and who
launches whom; the charter as a table (what the lead passes, what escalates, what is impossible);
the escalation round trip from a child's `needs_human` to the phone and back; the per-seat model and
tool pins with the cost reasoning behind them; and the failure modes the spike measured, because
every one of them is silent and none is guessable from the code.

⛔ **`flowchart TD` / `LR`, never `sequenceDiagram`** — a standing preference
(`mermaid-diagram-preferences`, ruled 2026-06-21): the participant-lane layout reads as noise to him,
which defeats the entire purpose of a document he asked for in order to *see* this.

**Sequencing, and why it is not simply "at close-out".** Row E has to edit the main SOP in its own
commit regardless — the armed `sop_currency.py` gate refuses a `.agents/commands/*.md` change
without it, and the rule's stated reason is that the context making the edit correct exists only
while the change is being made. So row E creates `autopilot_SOP.md` and links it, carrying the
charter and the door's flow; close-out then adds the diagrams and whatever row F's real story taught,
which is exactly the half that cannot honestly be drawn before the thing has run once.

## Deferred, and where it goes

**`claude-skills` is read but written on no master, deliberately.** Three keys is the whole
budget — `sync-agents.ps1` reads the header with `Get-Content -TotalCount 12` and a fourth and fifth
key push the closing `---` out of the window, at which point the seat vanishes from `.roomodes` with
no error anywhere. Skills lost the tie-break because the spike measured `skills:` having no effect
on a child's prefix (11,466 against 11,467 tokens) while accepting a made-up skill name in silence:
a populated list buys nothing measurable and could, if the key ever does restrict, cut a seat off
from the very door it was launched to run. The renderer still reads the key, so a master that grows
one needs no code change.

**The per-seat tool lists are the one thing row F will confirm or amend.** They mirror the Zoo
seat's `mode-groups` — read maps to Read/Grep/Glob plus the web pair, edit to Edit/Write/
NotebookEdit, command to Bash/TodoWrite — and `Task` is on no seat, because a headless child that
can spawn its own subagents is an unbounded bill with no ledger row. If a real door needs a tool no
seat carries, it will show up as a child that cannot finish, and the fix is a key on the master.

Whether a leading `/door-name` in a `-p` prompt expands to the door's launcher skill is proved by
row F's real story, where the plan places it.
