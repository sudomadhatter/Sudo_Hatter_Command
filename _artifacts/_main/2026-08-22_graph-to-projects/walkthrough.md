---
IsArtifact: true
ArtifactMetadata:
  title: "SCC-288 — graph to projects · maps self-refresh · fast-read tickets"
  type: walkthrough
  date: 2026-08-22
  ticket: SCC-288
  riders: [SCC-289, SCC-290, SCC-291]
  lane: chore/SCC-288-graph-to-projects
---

review-runtime: fan-out

# SCC-288 — walkthrough

**One consolidated lane, ONE commit, on the operator's word (2026-08-22): *"we will do all subtasks
in one shot on this working tree, one commit at the end."*** Shipping sha `52edbb2` for A/B/C; `14ed813`, `1624a5d` and `4aa9ef2` add the three
close-out fixes in Findings 4–6.

---

## Task Checklist

- [x] **A (SCC-289) — the centre drops its own code graph, and `risk_seam` reads the PROJECT's.**
  - A1 `code-review-graph` removed from `.mcp.json`, `.claude/mcp.json`, `.antigravity/mcp.json`
    (`.opencode` was already clean); all four now declare the same server set.
  - A2 `.code-review-graphignore` DELETED; the two live references fixed.
  - A3/A4 `AGENTS.md`, `docs/code-review-graph.md`, `docs/repo-map.md` rescoped to projects-only.
  - A5 `risk_seam.py classify --repo <root>`; the JSON echoes `root`.
  - A6 all four review/audit doors pass it; the dead `test_links` passage trimmed from both `smh-`
    doors (1823 → 776 chars, 722 → 436).
  - A7 **verify-only, and it stayed a no-op** — neither `.agents/skills/INDEX.md` nor
    `workspace-structure/SKILL.md` claimed a lobby index. No edit.
  - A8 the sentry door states that its enrichment reads AGY's graph, with `--repo`.
- [x] **B (SCC-290) — the doc graph grows a second root; the maps refresh themselves.**
  - B1 `generate_doc_graph.py`: repeatable `--root`, `--lobby`, lobby-relative ids, relative roots.
  - B2 **the SOP's dangling list, worked** — see Evidence.
  - B3 `docs/doc-graph.*` regenerated from the lobby; CURATED block rewritten.
  - B4/B5 NEW `refresh_maps.py`; B6/B7 the hook delegates; B8 `check_maps` check 10.
  - B9 `/smh-update-maps-indexes` states the generated-vs-curated split.
  - B10 ASCII-only output, asserted (RM-H).
  - B11 **no-op, and the plan's finding was stale** — see Deferred / Corrections.
  - B12 SOP §"Maps refresh" + changelog.
  - ⚠ **Three defects found while building, each pinned by a named case** — see Findings.
- [x] **C (SCC-291) — tickets are fast reads.**
  - C1 NEW `jira_ticket.py` — `outline` / `describe` / `attach` / `done`.
  - C2 `.agents/rules/jira.md` §"The description is the FAST READ".
  - C3 both Task doors wired (`smh-plan-task`, `smh-close-task-merge-tree --after-merge`).
  - C4 `jira_integration_guide.md` §12.5, `jira_manual.md` step 5, SOP §12.
  - C5 **deferred with a structural reason** — see Deferred.
- [x] **D (SCC-290 follow-on) — `--repair`, found by this lane's gate at its own close-out.**
  - The merge that absorbed `origin/main` left the maps stale behind a clean tree, and the remedy
    `--verify` printed could not fix it. See Finding 4.
- [x] **E (SCC-288) — a green mutation sweep was leaving the mutant running.** See Finding 5.
- [x] **F (SCC-288) — the link checker read the doc graph's report as its own findings.** Finding 6.
- [x] **G (SCC-288) — the adversarial review, and the three `important` findings it left open.**
  - Five lenses at `27870ba`; eight patches at `7a311c6`; verdict **`CONCERNS @ a722228`**.
  - R1 a map may only name what git HAS — `--verify` was refusing pushes over untracked scratch
    files and `--repair` was writing them into the committed map. `2982b7a`.
  - R2 `-Uninstall` deleted the tracked `.githooks/pre-commit` dispatcher. `2982b7a`.
  - R3 the three maps delegates had zero executable coverage — four mutants survived at 58/58.
    NEW `test_maps_hooks.py`, driving real `git commit` / `git push` / `git merge`. `2982b7a`.
  - R4–R7 carried, reproduced and tabled — see the last section.
- [x] The merge itself — lands via this branch's PR

---

## Evidence

### A5 · `risk_seam.py --repo` — RED then GREEN

RED, before the flag existed (`test_risk_seam.py --case "N · SCC-289 …"`):

```
[PASS] N exit 0: rc=0
[FAIL] N the JSON ECHOES the root it classified against: root=None want=/tmp/…/lobby
[FAIL] N status is classified — the FIXTURE's graph was read, not cwd's absent one:
       {'status': 'unclassified', 'tiers': {}}
[FAIL] N the tier belongs to the FIXTURE's path: {}
[FAIL] N control · and it echoes the cwd repo as its root, not the fixture: root=None
-- 2/6 passed --
```

and case O, `0/2 passed`. GREEN after: **`test_risk_seam.py` 36/36**.

⭐ **The bug this pins is a silent wrong answer, not a crash.** `_repo_root(None)` fell back to
`git rev-parse --show-toplevel` **of CWD**, and the four doors run from the command centre while
reviewing a project worktree. Every project review therefore classified the centre — which has no
graph — so it answered `unclassified`, indistinguishable from "this project's index was never
built."

### A1/A2/A6 · the surfaces — RED then GREEN

`test_command_surfaces.py --case "CS-15 …"`, RED **2/7**:

```
[FAIL] CS-15 B ⛔ no platform starts a code-review-graph server in the CENTRE:
       .mcp.json=['code-review-graph','md-feedback']; .claude/…; .antigravity/…
[FAIL] CS-15 C the four configs declare the SAME server set
[FAIL] CS-15 E ⛔ every `risk_seam.py classify` call passes --repo: naked calls:
       ['cicd-code-review.md:118','cicd-self-audit.md:166','smh-code-review.md:88','smh-self-audit.md:179']
[FAIL] CS-15 F .code-review-graphignore is DELETED
[FAIL] CS-15 G no live surface still names the deleted ignore file: ['test_sops_prds_folder.py',
       'file_folder_structure+maintaining.md', 'docs/repo-map.md']
```

G named exactly the three sites the plan's audit predicted (F5, F6). GREEN: **7/7**.

### B1/B3 · the doc graph — RED then GREEN

RED: the generator did not know the flag — `error: unrecognized arguments: --lobby`, and every
downstream case failed with `nodes=[]`. GREEN: **`test_doc_graph.py` 24/24**, live regen **0.14 s**.

**B2 — the SOP's dangling list, measured before and after.** The plan predicted 38 flagged refs,
"17 resolver false positives, 21 bare basenames". After B1 the SOP's real count is:

| | before (single root) | after |
|---|---|---|
| SOP broken-path refs | 38 flagged | **1** |
| SOP bare-name refs | — | 9 |

The one remaining broken-path ref is `docs/notes.md` at `workflows_testing_SOP.md:1754` — a **prose
example** inside a `--paths backend/api.py and --paths docs/notes.md` illustration, not a link. The
nine bare names (`walkthrough.md`, `implementation_plan.md`, `epics.md`, …) are generated-artifact
names workflows mention. **The SOP has zero real broken links.** Worked, not accepted blind.

Repo-wide the graph went 329 → **362** nodes (32 of them `docs/`, including the SOP, in-degree 21),
and broken paths **80 → 75** after the mermaid fix below.

### B4–B8 · the hook — GREEN, and the hook fired live on this commit

**`test_refresh_maps.py` 48/48.** The commit that landed this lane printed:

```
  refresh-maps: [maps-ok] - the truth checks are re-baselined by this commit, on the record.
[chore/SCC-288-graph-to-projects] 60 files changed, 10301 insertions(+), 4156 deletions(-)
```

⛔ **HONESTY NOTE ON RED-FIRST FOR `refresh_maps.py`.** Its cases were written against a first draft
of the script, not before it — the script and its shape were settled together, so they are
characterization checks by construction and carry no "seen red" warrant. **The mutation sweep is
what certifies them**, and it is recorded in full below. The test file says this in its own
docstring rather than leaving a reader to assume otherwise.

### C1 · `jira_ticket.py` — GREEN

**`test_jira_ticket.py` 39/39 outside the sandbox**, 32/32 inside it (see the Findings note). The
`outline` verb on the house shape produces exactly:

```
['paragraph', 'heading', 'taskList', 'heading', 'paragraph', 'heading', 'bulletList']   # fresh
['paragraph', 'heading', 'taskList', 'heading', 'bulletList', 'heading', 'bulletList']  # filled
```

`attach` was driven against a real local `http.server`, which received a real multipart body with
`filename="plan.md"`, the bytes, and `X-Atlassian-Token: no-check`.

### Gates at the tip — `52edbb2`

| Gate | Result |
|---|---|
| `run_all.py` (through `gate_receipt.py`) | **`[PASS] suite exit=0 114.7s @ 52edbb2f`** → `gates/suite.json` |
| `run_all.py` bare | **58/58 files passed** |
| `workflow_lint.py --toolkit-only` | **0 errors, 0 warnings**, 8 info (pre-existing BOMs) |
| `refresh_maps.py --verify` | **exit 0** |
| `check_maps.py --all` | exit 1 — **two pre-existing dead-path reports, not this lane** (below) |
| `mutation_sweep.py` (27 mutants) | **27/27 killed by their declared case** |

**Re-run at the close-out tip `4aa9ef2`**, after `origin/main` was absorbed and Finding 4 was
fixed: `run_all.py` **58/58 files**, `refresh_maps.py --verify` **exit 0**, `mutation_sweep.py`
**36/36 killed** (M28–M32 for `--repair`, M33–M34 for the bytecode purge, M35–M36 for the
AUTO-block strip), with
`test_jira_ticket.py` at **41/41** because the sweep was run outside the sandbox. `check_maps --all` still exits 1 on the same
two pre-existing rows below and nothing else.

`check_links.py --base origin/main` exits 1 with **26** unresolved paths: 15 pre-existing on
`origin/main`, 11 example fixture paths in this lane's own artifacts. Finding 6 has the breakdown.

⚠ **`check_maps --all` exits 1 on two rows and both are pre-existing.** Both name
`docs/migrations/auth_keys/_secrets/master.env`, a hand-carried secrets file that is gitignored
(`.gitignore:52 **/auth_keys/`) and therefore absent from every clone. The same row is on
`origin/main`. Untouched by this lane; not this task's work (`code-standards` §6.5, question 3).

⭐ **What this lane REMOVED from that same run:** the three worktree false positives —
`AUTO block is STALE`, `on disk but not in map: <lane>/`, `in map but not on disk: <repo>/` — are
gone. See finding 1.

---

## Findings — three defects found while building, each pinned

### 1. The repo-map's root label was the WORKTREE directory basename

`build_auto_body` wrote `Path(root).name + "/"` as the tree's first line. Every lane here lives in
`.claude/worktrees/<slug>/`, so the map said `SCC-288-graph-to-projects/` from a lane and
`Sudo_Hatter_Command/` from main — **the artifact changed identity depending on who regenerated
it.**

⛔ **This is the long-recorded "check 1 always reports STALE in a worktree" false positive**, whose
printed remedy would have shipped the lane name into the map bound for `main`, and it is why
`/smh-close-task-merge-tree` runs `check_maps --depth3-only` instead of the full lint.

**SCC-290 could not ship around it.** `refresh_maps.py --verify` runs at **push**, and every push in
this system comes from a worktree — a per-tree label would have refused every push. Fixed at the
source: `generate_repo_map.repo_label()` reads `--git-common-dir`'s parent, which is the repo from
a checkout and from a worktree alike, with a fallback to the old behaviour. Pinned by `CM-LABEL`;
mutant **M17** kills it.

### 2. The graph read its own output, and the two maps never converged

Two ordering defects, one symptom — `--verify` refusing a tree the hook had just written.

- `docs/doc-graph.md` lands **inside a scanned root**, so run 2 parsed run 1's tables and produced a
  different graph. Measured on the fixture: 1153 bytes, then 1795. Fixed twice over — generated
  `AUTO` blocks are no longer parsed as link sources (they are machine inventories, not authored
  wiring), and the generator's own output is excluded from its own scan.
- `docs/doc-graph.*` land inside `docs/`, **which the repo-map walks** — so a repo-map built from
  the pre-write tree was stale the instant they landed. `run_staged` now writes the doc graph first
  and always re-derives the repo-map after.

⭐ **The test fixture had the same bug**, and it was building its own baseline the wrong way round
(`2 files` where the converged tree has `4`) — so every case was measuring a broken fixture. The
seed now converges through `run_staged` itself. Mutants **M12** and **M11** kill both halves, and
M11 only dies in a fixture that stages under `.agents/` — see the sweep note.

### 3. `install-encoding-hook.ps1` would have silently disarmed the maps hook on the PC

Confirmed live on `pwsh`, exactly as the plan's audit F2 predicted. The installer's ownership test
was `-match $MARKER`, and `.githooks/pre-commit` — now a dispatcher chaining two delegates —
necessarily contains the string `pre-commit-encoding`. So the installer called the file its own and
overwrote it with its three-line body, dropping the maps delegate. `git status` would show a
modified `.githooks/pre-commit`, which reads as "the installer touched its own file."

Ownership is now **byte equality**, with three distinct outcomes asserted against the real
PowerShell: foreign → REFUSED, ours-but-extended → REFUSED, ours-and-identical → installed.
Mutant **M19** kills it.

### 4. `--verify` printed a remedy that could not fix the tree it fires on

**Found at this lane's own close-out, by this lane's own gate — the fourth time that has happened
here.** Merging `origin/main` in at Step 1 brought a new file under `docs/`. `git merge` runs
`pre-merge-commit`, never `pre-commit`, so `pre-commit-maps.sh` did not fire and the generated maps
went stale **behind a clean tree**. `--verify` caught it at the push. That part worked exactly as
designed — it is reason #1 in `pre-push-maps-verify.sh`'s own header.

What did not work was the next line. `--verify` printed:

```
regenerate: python3 .agents/scripts/refresh_maps.py --staged
```

and `--staged` is gated on the **staged set**. After a merge nothing is staged, so it exits 0 having
written nothing. Run it, run `--verify` again, get the same refusal, forever. **All three trees
`--verify` exists to catch have an empty index** — a merge commit, a `--no-verify` commit, and a
clone whose `core.hooksPath` was never armed — so on every one of them the printed remedy was a
no-op and `--no-verify` was the only way past. ⛔ **A gate whose only escape is the bypass is a gate
everybody bypasses**, which would have quietly retired the whole of Part B within a month.

**Fixed:** `run_staged` split into the trigger gate plus a reusable `converge()`; new `run_repair`
/ `--repair` runs the same convergent write with no trigger gate. Every message that names a remedy
now names it — `refresh_maps --verify`, `check_maps` check 10, `pre-push-maps-verify.sh`, SOP §8.

**RED first.** `RM-D2` builds the merge shape (stale tree, empty index), asserts the fixture really
is stale and the index really is empty, then that `--staged` **cannot** fix it — that assertion is
the defect, kept as a case so the trigger gate cannot be deleted to "simplify" it — then that one
`--repair` converges, stages all three files, and a second run is a silent no-op. `RM-D` now pins
the printed remedy **both ways** (`--repair` present, `--staged` absent); `CM10 C` pins check 10's;
`RM-I` covers the new mode collision. Mutants **M28–M32** kill all five.

### 5. ⛔ A green 32/32 sweep left M16 still executing — the sweep produced a green that lies

**Found minutes after Finding 4, by its own symptom.** `refresh_maps --repair` wrote an **absolute**
`root` into `docs/doc-graph.json` — the precise output of **M16**, *"the artifact carries an
ABSOLUTE root again"*, a mutant the sweep had reported **KILLED and restored**. Source clean,
`git status` clean, sweep green, tracked artifact corrupt. Deleting `.agents/scripts/__pycache__`
made the generator correct again, and the tree returned to HEAD's bytes with no other change.

**The mechanism, and why no case covered it.** `restore()` rewrote the source **text** and stopped.
Python had already compiled the mutant to `__pycache__/<mod>.cpython-XY.pyc`, and it decides that
cache is current by comparing the source's **timestamp and size** against the pair recorded inside
the `.pyc` — never the contents. M16 is `"root": rel_roots,` → `"root": str(root),`: **26
characters each**. Same size, same wall-clock second, so the pair matched and the import machinery
served bytecode compiled from code that no longer existed on disk.

This is the one failure the sweep exists to make impossible. It also means a stale mutant can be
live while the *next* mutant is judged — kills attributable to the wrong code.

**Fixed:** `restore()` deletes the `__pycache__` beside every table file. One recompile, class
closed.

**RED first.** `K7` sweeps a module the stand-in test **imports** — the existing stand-in only read
the source as text, so it never compiled anything, which is exactly why no case reached this.
`K7d`: after the sweep a fresh interpreter importing restored source returns the **mutant's**
answer without the fix (`0`), the original's with it (`1`). `K7c`: no `.pyc` may predate the source
it caches. Mutants **M33** and **M34** kill against them.

⛔ **`K7c`'s first draft was vacuous, and vacuous for the same reason the bug exists.** It compared
the `(mtime, size)` pair recorded in the `.pyc` header against the source — and passed **with the
fix and without it**, because that pair matching *is* the defect. Kept in the case comment rather
than quietly replaced.

### 6. `check_links` reported the doc graph's findings as its own — 40 of them

`docs/doc-graph.md`'s AUTO block is a **report** whose job is to LIST the dangling references the
graph found, and every entry is a backticked path `check_links`'s pattern matches. So the graph's
findings came back as the checker's findings, in a file no human wrote a link into. **This lane
widened the graph onto `docs/`, which took the run from ~24 hits to 64** — and SCC-285 built this
script with the lesson written into it: *a gate that cries wolf thirty times teaches the reader to
skip the one real hit.* The lane that made the noise fixes it.

`generate_doc_graph.strip_auto()` already refuses to parse AUTO blocks as link **sources** for the
same reason. This is the same rule applied by the other reader of the same files — both sentinels,
line numbers preserved.

**Measured on this diff: 64 → 26.** Of the 26, **fifteen are pre-existing on `origin/main`**
(`PROJECT_ROOT/` placeholders in the sentry doors, two older pointers) and **eleven are example
fixture paths quoted in this lane's own plan and walkthrough** — prose about tests, in a historical
record. **No new dead link in authored prose.** The two illustrative node ids in `doc-graph.md`'s
curated header were also changed to real paths, so the example is true as well as quiet.

**RED first**, case `H`. `H1` a dead path inside the block is not the checker's finding; `H2`/`H3`
an authored dead link on **either side** still reports, so the strip cannot swallow the file — the
failure mode the mermaid strip had; `H4` the checked count; `H5` the repo-map sentinel.

⛔ **`H`'s first fixture used a plain table cell and passed WITHOUT the fix.** The real block
backticks its paths and only a backticked path matches. Corrected, and noted in the case — this is
the second vacuous first draft on this lane, both caught by running RED before GREEN.

---

## Corrections to the plan, made on measured evidence

| Plan said | What was true | What shipped |
|---|---|---|
| **B4** trigger: "under `.agents/` or `docs/`, or a top-level entry added/removed" | `.agents` is **in** the repo-map's own ignore set, and this map declares `mode=content` (signatures), so an edit to any walked `.py` changes it with nothing added or deleted | Two **disjoint** triggers: repo-map on anything it walks, doc graph on `.md` under either root. Caught by RM-B (the first draft made a staged `.agents/rules/x.md` trigger *nothing at all* — the exact commit the hook exists for) |
| **B4/B5** put the truth checks in `pre-commit` | The ratchet **refused the very commit that introduced it** (52 → 77), because that commit widens the graph's scope — the two numbers are not the same measurement. And the fix needs a recorded opt-out, which `pre-commit` cannot read | Truth checks moved to a **`commit-msg`** delegate with `[maps-ok]`, the same shape and the same reason `sop-currency.sh` gives in its own header. Regeneration stays at `pre-commit`, because it stages files |
| **B11** memory + `active-context.md` still name the old SOP path | **Already correct** — fixed by a sibling lane in the 63 commits absorbed at the start. The memory's two remaining hits are a past-tense history note and AGY's copy, which genuinely still lives there | No edit. Recorded rather than performed cosmetically |
| **A7** may need wording changes | Verified: neither skills file claimed a lobby index | No edit, as the plan allowed |
| **A10** interim `doc-graph.md` CURATED line | Superseded by B3 in the same commit | B3 only |

---

## Mutation sweep — 46/46 killed

`python3 .agents/scripts/mutation_sweep.py --table _artifacts/_main/2026-08-22_graph-to-projects/sweep.json`

```
-- sweep clean: 46/46 killed by their declared case --
```

Every mutant is drawn from a **decision in the source**, not from the cases. Coverage: `risk_seam`
(M1–M3), the triggers (M4–M5), the ratchet and door check (M6–M8, M26–M27), the kill switch (M9),
`--verify` read-only (M10), ordering and self-inclusion (M11–M12), the mermaid strip in both
directions (M13–M14), lobby-relative ids and relative roots (M15–M16), the label (M17), check 10's
project skip (M18), the PS installer (M19), and `jira_ticket` (M20–M25). The close-out findings
added M28–M36 (`--repair`, the bytecode purge, the AUTO-block strip), and the code review's three
`important` findings added ten more: **M37–M41** for the index filter that closes R1 (no filtering ·
files-only ancestry · directories unfiltered · the doc graph unfiltered · the doc graph staged last),
**M42** for the `-Uninstall` ownership test that closes R2, and **S1–S4** for the hook delegates that
close R3 (the dispatcher never calling the delegate · the delegate exiting 0 · the push remedy
reverting to `--staged` · the `MERGE_HEAD` carve-out deleted). All four of S1–S4 survived the suite
at **58/58** before `test_maps_hooks.py` existed; all four die now.

**Five survived the first run, and every one was a real gap or a defective mutant:**

| Mutant | Why it survived | What it bought |
|---|---|---|
| **M2** bare `--repo` falls through | `classify --repo` alone leaves **no paths either**, so the no-paths error produced the same exit 2. The case passed against code with the value check deleted | The path now comes FIRST (`classify .agents --repo`), so a fall-through would be a valid command classified against CWD. Plus an `--repo=` empty case — what an unset shell variable expands to |
| **M5** repo-map trigger dropped | RM-B2 stages a `docs/*.md`, which fires the **doc-graph** trigger, and a doc-graph write forces a repo-map rebuild anyway | NEW **RM-B3**: a `docs/*.txt` — walked by the repo-map, invisible to the doc graph — isolates the trigger |
| **M11** the `or wrote` rule dropped | Once the graph files exist only their CONTENT changes, and `docs/` collapses to a COUNT — the ordering is invisible in a settled tree | NEW **RM-B4**: the FIRST refresh, staging under `.agents/` so only the doc graph triggers and its two new files move the repo-map's count |
| **M12** self-inclusion restored | Same fixture problem as M11 | Same case |
| **M25** the token scrub deleted | JT-T drove a **refused connection**, whose OS message never contained the token. The assertion passed against code with the scrub gone | JT-T now also drives a **401 whose body echoes the secret** — the path that actually needs scrubbing |

Two more were **sweep errors, not results**, and both were fixed rather than believed: **M21** made
`JT-A` *crash* (it indexed `[...][0]` into the very shape the mutation removes) — a case that dies on
the mutation it exists to detect proves nothing, so it now reports cleanly; and **M17/M18/M19**
returned exit 3 (`NO_MATCH`) because they target block-free test files, so they run `unfiltered`.

⭐ **And the sweep found a hole in the test *harness* usage too.** `test_check_maps.py`,
`test_hooks_armed.py` and `test_install_git_hooks.py` carry **no `c.block(`** by convention.
Introducing the first one into each made every pre-existing bare `c.check` an ORPHAN and failed
`test_suite_runner.py`. The new cases were rewritten in each file's own style.

⛔ **THAT CONVENTION IS A TRAP, and R2's fix walked into it.** A file with no `c.block(` is not
"wired", so `test_suite_runner.py`'s ORPHAN check exempts it entirely - and the sweep's `--case`
filter cannot reach anything inside it either, which is why M17/M18/M19 had to run `unfiltered`.
Adding one block to `test_install_git_hooks.py` for case F3 flipped the file to wired and made
every one of its pre-existing bare checks an orphan at once. Rewriting the new case "in the file's
own style" was the wrong answer the first time: it keeps the file unselectable. So the whole file
was wired instead (`da04d0f`) - five named blocks for the SCC-115 sections, F2 and F3 as SIBLING
top-level blocks, never nested, because a block inside another block's body is only ever reached
when the outer label matches and a mutant aimed at it returns exit 3 forever.

⛔ **THE SANDBOX MADE A GREEN LIE, and it is worth writing down.** `test_jira_ticket.py` reports
**32/32 inside the sandbox and 39/39 outside it**: `PermissionError` on binding `127.0.0.1:0` makes
JT-F, JT-G and JT-T skip, and a skip is counted as a PASS. Seven assertions — the multipart body,
the XSRF header, the 200-with-empty-array refusal, the token scrub — were silently unrun, and the
total read as coverage. Mutants M22/M23/M25 survived for exactly that reason on the sandboxed run.
The skip labels now say **`SKIPPED (UNVERIFIED HERE)`** and name what was not checked, and the
certifying sweep was run outside the sandbox.

---

## Deferred

| Item | Structural reason |
|---|---|
| `jira_feed.py mint` still renders a Story description from the story file, in the old shape | It is the **BMAD story lane's** seam and this is the Task lane. Adopting the fast-read shape there needs the story-lane doors in the same change (plan C5) |
| The two `check_maps` dead-path rows for `docs/migrations/auth_keys/_secrets/master.env` | Pre-existing on `origin/main`; the target is a gitignored, hand-carried secrets file that is absent from every clone by design. Not in this lane's diff |
| The 77 broken doc references repo-wide | The ratchet's whole design (Decision 5): it forbids an INCREASE, it does not demand zero on day one. Most are stale references inside old migration guides |
| AGY's vendored `scripts/check_maps.py`, `generate_repo_map.py` | All three already differ from the masters, and check 10 is lobby-only by construction (F1), so porting would add a check that never fires. Cross-repo work needs an **AVCH** key (plan §7, F8) |
| The PC half — `commit-msg-maps.sh`, `pre-commit-maps.sh`, `pre-push-maps-verify.sh` and the F2 installer fix | Written for both machines (`python3 → python → py`, ASCII output, `printf` only) and **verified on the Mac only**. The PowerShell installer case DID run here on `pwsh`. Re-verify on the next PC session |

---

## Your Actions

**What landed:** `52edbb2` (all three riders' scope) and `14ed813`, `1624a5d` and `4aa9ef2`
(Findings 4, 5 and 6 — all three found while closing the lane out, the second by the first one's
symptom), then `7a311c6` (the eight patches the five review lenses earned) and `2982b7a` /
`c733b3f` / `da04d0f` (R1, R2 and R3 — the three `important` findings the review left open), on
`chore/SCC-288-graph-to-projects`. Gates green at the shipping sha, **46/46** mutants killed.

⭐ **The adversarial review DID run, and its verdict is `CONCERNS @ a722228`.** Five lenses, fifteen
real findings, eleven fixed in-lane and four carried with reasons — the full record is in the Code
Review section above. It was run because `flight_recorder record` refuses a lane whose walkthrough
carries no canonical `Verdict:` line (`main_write_gate.py:368`, and `:411` is the refusal), which
is the machinery working exactly as designed.

**What I decided, and why, without asking:**
- Moved the two truth checks from `pre-commit` to a new `commit-msg` delegate. The ratchet could not
  otherwise be satisfied by the commit that introduces it, and every future root addition would hit
  the same wall. It mirrors `sop-currency.sh` exactly.
- Used `[maps-ok]` on this commit as a **recorded re-baseline**, with the reason written into the
  commit message. It is in the log forever, which is the design.
- Fixed the repo-map's root label at the source rather than exempting worktrees from `--verify`.
  It was required for B to work at all, and it retires a long-standing false positive.
- Left the two `auth_keys` dead-path rows alone; they are pre-existing and outside this diff.

- [x] **Create an Atlassian API token on this Mac and store it as `sudo-jira`** (plan step C0 — the
      one item in this lane an agent cannot do). Guide:
      `docs/migrations/install_guides/jira-api-token-setup.md`.
      **Done by the operator 2026-08-23. Verified by measurement, not by their word:**
      `security find-generic-password -s sudo-jira` returns an item created `20260823002015Z`;
      the value reads back at **192 chars** (the guide's floor is ~190, and both silent-corruption
      routes land at 128 or at the command text); and a live `GET /rest/api/3/issue/SCC-288`
      authenticated with it returns **200** and lists `implementation_plan.md` already attached.
      The token is labelled `acli-mac-files-upload` on Atlassian's own site — that label is
      cosmetic and need not match; the **credential-store item name** is the contract, and it is
      `sudo-jira` as specified.
*(No second box. `jira_feed.py mint` adopting the fast-read shape was posed here as a decision for
the operator, and that was the wrong section: it is already the first row of `## Deferred`, carrying
its structural reason — it is the BMAD **story** lane's seam and this is the Task lane, so the change
needs the story-lane doors with it. Deferred work is recorded, not handed over; `finish` refused the
row and was right to.)*

---

## Code Review (2026-08-22)

Verdict: CONCERNS @ a722228

review-runtime:  fan-out
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none
findings:        15 real · 8 patched at review · 3 patched after (R1-R3) · 4 open (R4-R7)   (2 dismissed under code-standards §6.5)
dispositions:    5 lenses, 17 findings assessed: 15 survived, 2 dismissed, 0 relevance-killed. ⛔ Per-lens attribution is NOT reconstructed here: this review ran fan-out with no `FINDINGS_SINK`, so the engine's per-lens counts were never written to a file and the orchestrator's context was compacted before the section was authored. Inventing the split would be worse than saying so. Two attributions ARE on the record because they were written down at the time: R2 was raised independently by two lenses, and R3 came from the test-adequacy auditor.
drift:           undeclared=17 · unimplemented=0 · incomplete=0
severity_floor:  CONCERNS
notes:           No optional `FINDINGS_SINK` or `EVIDENCE_PACK` was supplied, so findings live in this section and nowhere else. The 17 undeclared changes are a BOOKKEEPING defect, not scope creep - the acceptance auditor ruled all three close-out findings (the unusable `--verify` remedy, the poisoned bytecode, the `check_links` noise) legitimately in scope; what was never done is amending the Declared Change Set block as they landed.

### The verdict, and why it is not PASS

Three `important` findings came back that this lane had to own, and all three are now FIXED with
RED-first cases and declared mutants (`2982b7a`, `c733b3f`, `da04d0f`). What keeps the verdict off
PASS is the four that are **recorded and not fixed** - R4 through R7 below. None of them is a gate
that fails open, which is what would force FAIL under `tests-must-gate-for-real` §5; R7 is the
closest, and it is an UNCOVERED behaviour rather than an uncoverable one.

⛔ It is not WAIVED either. A waiver says the finding does not need fixing. These do; they are
carried, named, and reproduced, so the next commit on this surface picks them up from a table
rather than rediscovering them.

### Findings

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | The changelog claimed "every message that names a remedy now names `--repair`" - four sites in `/smh-update-maps-indexes` still said `--staged`, the exact door an operator lands on after check 10 fires | important | FIXED @ `7a311c6`, pinned by `RM-D4` (anti-vacuity: `seen > 20`) |
| 2 | `check_links.strip_auto` went SILENT on a torn file - an unpaired `AUTO-START` blanked to EOF. Measured on the real tree: path claims 887 -> 541; `workspace-standard.md` alone lost 408 of 467, because line 390 mentions the sentinel in prose | important | FIXED @ `7a311c6`, cases `H1`-`H6`, mutants `M35`/`M36` |
| 3 | `jira_ticket` crashed on Windows - `$TMPDIR` is POSIX-only, the PC resolved `C:\tmp`, uncaught, and in `done` it lands AFTER the outline file was rewritten | important | FIXED @ `7a311c6` (`tempfile.gettempdir()`) |
| 4 | `risk_seam` swallowed a typo'd `--flag` as a path, answering about the wrong tree in silence | medium | FIXED @ `7a311c6`, case `O` |
| 5 | `reverse_door_check` was satisfied by a FILE PATH - `.agents/commands/x.md` matched at the `/` and `.` passed the lookahead | medium | FIXED @ `7a311c6`, case `RM-G4` |
| 6 | `converge` walked the whole tree to build a repo-map it could not use | low | FIXED @ `7a311c6` |
| 7 | `.gitignore:17` still named the deleted `.code-review-graphignore` | suggestion | FIXED @ `7a311c6` |
| 8 | The PowerShell installer's refusal claimed a hook "CHAINS more than the encoding gate" about one that may merely be ours-but-older | suggestion | FIXED @ `7a311c6` |
| R1 | `--verify` measured the WORKING TREE, so an untracked scratch `.md` refused the push of unrelated committed work - and the `--repair` it prints as the remedy then STAGED the phantom into a tracked artifact bound for main | important | **FIXED @ `2982b7a`** - `refresh_maps.in_index` passes an index predicate into both generators; cases `RM-J`/`RM-J2`, mutants `M37`-`M41` |
| R2 | `install-encoding-hook.ps1 -Uninstall` kept the marker-only ownership test and DELETED the tracked `.githooks/pre-commit` dispatcher; this lane made it worse by chaining the maps refresh into that same file | important | **FIXED @ `2982b7a`** - one byte-equality test serves both directions; case `F3`, mutant `M42` |
| R3 | The three maps delegates had ZERO executable coverage - 146 lines of shell pinned only by source greps, with four mutants surviving at 58/58 | important | **FIXED @ `2982b7a`** - `test_maps_hooks.py` drives real `git commit` / `git push` / `git merge`; mutants `S1`-`S4` all killed |
| R4 | `check_maps` check 10 is fatal on `docs/repo-map.md` but reports under the doc-graph heading, and `check_doc_graph_fresh(root)` silently discards the operator's `--ignore` | medium | **OPEN** - see the table below |
| R5 | `attach()` raises `AttributeError` on a 2xx body that is not a JSON array; `except ValueError` does not catch it | low | **OPEN** |
| R6 | `triggered()` reads git's quoted path form literally, so a non-ASCII staged filename regenerates the wrong artifact | suggestion | **OPEN** |
| R7 | `generate_doc_graph.strip_auto` has no named case and no mutant | medium | **OPEN** |

**Dismissed under `code-standards` §6.5** (the assessor decides, not the lens): the repo-map's
hard-coded `threshold=8` - no door passes `--threshold`, so no operator can reach the divergence,
which makes it unreachable rather than latent · `_land`'s read-back - correct that it has no
observable, but it is the Port Check 3 idiom this house mandates and it costs one read.

### Gate results at the shipping SHA

| Gate | Result |
|---|---|
| `run_all.py` | **59/59 files** (`test_maps_hooks.py` joins by auto-discovery) |
| `mutation_sweep.py --table sweep.json` | **46/46 killed**, restore verified byte-identical, closing full-file green on every affected suite |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info |
| `refresh_maps.py --verify` | exit 0 - and with ZERO map churn: the R1 fix removes nothing the repository actually has |
| `check_maps.py --depth3-only --strict` | exit 0 |
| `check_links.py` | 26 unresolved (from 64): 15 pre-existing, 11 fixture examples in this lane's own artifacts. Zero new dead links in authored prose |
| doc graph | 362 nodes · 77 broken paths (the ratchet's baseline, unchanged) |

⛔ **Three mutants needed an unsandboxed run** (`M22`, `M23`, `M25` - the Jira upload path). Under
the sandbox `test_jira_ticket.py` cannot bind a local listener, prints `SKIPPED (UNVERIFIED HERE)`,
and those three SURVIVE for the environment's reason rather than the code's. The 46/46 above is the
unsandboxed run. A sweep read from a sandboxed shell would have reported three false holes.

### Acceptance matrix

| Part | Ticket | Items | Result |
|---|---|---|---|
| A - centre drops its own code graph; `risk_seam` reads the PROJECT's | SCC-289 | A1-A10 | **10/10** |
| B - the SOP and the docs folder cannot go stale | SCC-290 | B1-B12 | **12/12** |
| C - Jira descriptions are fast reads, the plan rides as an artifact | SCC-291 | C0-C5 | **5/5** (C0 is the operator's token step, in `## Your Actions`) |

The auditor re-checked all 27 items against the SHIPPED CODE, not against this walkthrough's
claims. B9 was `partial` at review time on the door remedy alone; that is finding 1 above and it
is fixed.

### Step 0.7 - re-derivation of the review radius

1. **Nothing this diff references has moved.** `origin/main` has landed **0 commits** since the
   merge-base `7c8105a3`, so no reference can have been moved out from under this branch.
2. **True overlap with `main` is zero files.** `git diff --name-only <merge-base>..HEAD` and the
   same against `origin/main` share no path; `merge-tree --write-tree` is clean with no conflict
   messages.
3. **One sibling lane is live** - `SCC-280-teaching-edition` on `claude/teaching-edition`, a story
   lane with no landing-order dependency on this diff.

Level was `standard` rather than `quick` because the radius covers gate, hook, rule and contract
surfaces across 72 files.

### Clean-Code Gate (Step 3.5)

⛔ **`/smh-clean-code-audit` was NOT run as a separate step, and this is the record of what was
done instead.** The `code-standards` §6 machine floor is a FastAPI + Next.js contract - `ruff`,
`pyrefly`, `npm run lint`, `tsc` - and this repository has no `backend/`, no `frontend/` and no
venv, so all four commands are **N/A here**, not skipped. Under the audit's own rule a missing
tool is a finding rather than a skip, so it is named: the objective half of the gate has no
runnable check in the command centre, which is itself worth a ticket one day.

The judgment half was performed against §1 and §2 over this lane's diff:

- **Comment contract (§1)** - every non-obvious block added here carries its `SCC-<n>` provenance
  and the trap it closes. No `TODO`/`FIXME` was added.
- **No new abstraction with a single caller (§2)** - `stage()` has two call sites by construction
  (that is the R1 ordering fix); `in_index()` has two (both generators); `run_installer()` in the
  installer test has two blocks calling it.
- **No re-implementing what exists** - `in_index` is passed INTO the two existing generators
  rather than a third walker being written beside them.
- **Both machines (§5)** - the one finding of this class in the whole lane was `jira_ticket`'s
  `$TMPDIR`, fixed at `7a311c6`. Every hook added here probes `python3 -> python -> py`, and
  `test_maps_hooks.py` asserts nothing but ASCII reaches the console.

## Review findings STILL OPEN at this commit - not fixed, deliberately recorded

Five lenses ran at `27870ba`. R1, R2 and R3 were the three `important` ones and are now **CLOSED**
at `2982b7a` with RED-first cases and declared mutants - see the Code Review section above. What
follows is what remains: none of it is a gate that fails open, and all of it is reproduced, so the
next commit on these surfaces picks it up from a table rather than rediscovering it.

| # | Finding | Severity | Why it is real |
|---|---|---|---|
| R4 | **`check_maps` check 10 is fatal on `docs/repo-map.md`, not just the doc graph, and it silently discards the operator's `--ignore`.** Reproduced both. | medium | `refresh_maps.verify()` regenerates BOTH artifacts, but the guard tests only for `docs/doc-graph.md` and the heading says doc-graph - so a repo-map failure prints under the wrong name. And `check_doc_graph_fresh(root)` takes no ignore argument, so `--ignore` is honoured by check 1 and dropped by check 10; the documented escape hatch cannot suppress the drift it exists for, and `--repair` would write the excluded entry into the committed map. |
| R5 | **`attach()` crashes with a traceback on a 2xx body that is not a JSON array.** `except ValueError` does not catch the `AttributeError` a JSON object produces. | low | The function's own docstring says success is the filename in the response, never HTTP 200 - it is written to survive a well-formed-but-wrong 2xx and return `TRANSPORT`. An error envelope makes the comprehension iterate dict keys and die instead. |
| R6 | **`triggered()` reads git's quoted path form literally**, so a non-ASCII staged filename regenerates the wrong artifact and leaves the doc graph stale. | suggestion | `git diff --cached --name-only` emits `".agents/rules/caf\303\251.md"` under default `core.quotepath`; the leading quote breaks both the top-segment split and the `.md` suffix test. Fix is `-z` + NUL split. ASCII-strict repo, so unlikely - but it is the exact failure the function was widened to avoid. |
| R7 | **`generate_doc_graph.strip_auto` has no named case and no mutant.** Removing it from the pipeline leaves `test_doc_graph.py` at 24/24 and `test_check_maps.py` at 35/35; `test_refresh_maps.py` exits 1 but with **zero `[FAIL]` lines** - it dies in `seed_repo`'s assert, the "red test dies before its assertion" shape. | medium | The file that owns the behaviour cannot see it. |

**Dismissed, with reasons:** the repo-map's hard-coded `threshold=8` (no door passes `--threshold`,
so no operator can reach the divergence - unreachable, not latent) · `_land`'s read-back (correct
that it has no observable, but it is the Port Check 3 idiom this house mandates, and it costs one
read).

---

## Follow-on — 2026-08-23 · the `attach` door could not run at all (R8)

Found while verifying C0 before ticking its box. **The operator's token step was done and correct;
the door it exists to unlock was broken**, so the box could not have been honestly ticked without
this fix. Landed on `chore/SCC-288-attach-site-parse`.

| # | Finding | Severity | Why it is real |
|---|---|---|---|
| R8 | **`auth_identity` could never parse a real `acli jira auth status`, so `attach` died at "could not determine the Jira site" while holding a valid token.** | **high** — it is the whole of C0's payoff | The read was `re.search(r"https://[\w.-]+\.atlassian\.net", text)`. `acli` 1.x prints four labelled lines and the site line carries **no scheme**: `  Site: sudo-command.atlassian.net`. A scheme-anchored pattern can never match it. Measured on the real binary, this machine, 2026-08-23. |

⛔ **Why the suite was green over it.** `test_jira_ticket.py`'s `acli_stub` printed an **invented**
one-line shape — `https://sudo-command.atlassian.net  account: t@example.com` — that nothing in the
world produces, and it happened to satisfy the very regex under test. Every upload case (JT-F, JT-G,
JT-T) passes `--site/--email` explicitly, so `auth_identity` had **no** coverage against reality at
all. A fixture that does not match the contract is not coverage; it is the bug, written twice.

**The fix, RED first.**

1. The stub now prints what the binary actually prints (four lines, bare host), measured with
   `acli jira auth status | od -c`. That alone turned **JT-I** red: `site == ''`.
2. `parse_site()` replaces the regex — it reads the `Site:` **label** first (what acli prints),
   falls back to a loose URL then `*.atlassian.net`, strips ANSI, and always returns a
   scheme-qualified URL. `auth_identity` also strips ANSI before the email read.
3. **JT-I** pins both halves: a bare host comes back as `https://sudo-command.atlassian.net`, **and**
   `attach` completes with **no** `--site/--email` against a real local listener. It owns its own
   listener because `srv` is already shut down by JT-T — pointing at the dead one hangs to the
   socket timeout instead of failing honestly.

**Evidence.** `python3 .agents/scripts/tests/test_jira_ticket.py` → **44/44 passed** (was 42/44 with
the corrected fixture and the old regex — the two new assertions failing for exactly the right
reason). Against the real binary: `jt.auth_identity()` → `('https://sudo-command.atlassian.net',
'sudomadhatter@gmail.com')`.

**Not fixed here:** R5 above (`attach()` on a non-array 2xx) is the same function and still open. It
is a different failure mode, it is already recorded with a reproduction, and widening this follow-on
to chase it would be the scope creep the lane rules exist to stop.

---

## Follow-on — 2026-08-23 · the maps ratchet refused every worktree commit (R9)

Found by this lane's own commit being refused. **Not worked around** — the operator's ruling when
shown the `[maps-ok]` escape hatch: *"dont work around it lets fix it."*

| # | Finding | Severity | Why it is real |
|---|---|---|---|
| R9 | **`generate_doc_graph` counted references into an uninitialized submodule as broken links, so the doc-reference ratchet was tree-dependent and refused every commit made in a worktree.** | **high** — every lane in this system works in a worktree | `git worktree add` does not initialize submodules. `Projects/*` is ten empty directories in a worktree and ten populated repos in the main checkout. `resolve()` probed those targets with a plain `is_file()`, got False, and recorded them dangling. The same tree, the same commit: **74** broken refs from the main checkout, **77** from a worktree. `commit-msg-maps.sh` reads that as a rise and refuses. |

⛔ **This is what `[maps-ok]` was hiding.** The previous lane recorded using it as a *"recorded
re-baseline"*; it was in fact banking a number that only one checkout could ever reproduce. A gate
whose escape hatch is needed on every commit is not a gate.

**The fix, and the second thing it exposed.** The first cut excused only the submodules this tree
cannot see. That cleared the refusal — and left the count still tree-dependent, **measured on the
live repo as main `74` / worktree `71`**: three of the six refs into `Projects/*` are real files the
main checkout can stat and a worktree cannot. A commit from a worktree would bank `71`, and the
next regeneration from the main checkout would read as a rise to `74` and be refused — the same bug
pointing the other way.

⭐ So the rule is **every declared submodule, in every checkout state: the lobby graph does not
adjudicate links into another repo.** That is the existing design rather than a new carve-out —
each project is an independent repo with its own map artifacts and its own `check_maps` run, and
lobby checks are lobby-only by construction. A broken link inside a project is that project's gate
to catch, and it is the only gate that can catch it reliably.

**Shape of the change** — `blind_submodules()` parses `.gitmodules` textually (no subprocess: the
module's cwd-independence and "git may not be on PATH" contracts), a fourth `resolve()` status
`unresolvable` is returned **before** the `is_file()` probe rather than after, and the count is
reported in the header line so the blind spot is visible instead of being an invisible subtraction.

**Evidence.**

| | `broken_paths` | `unresolvable` |
|---|---|---|
| Main checkout, before | 74 | — |
| Worktree, before | **77** (the refusal) | — |
| Worktree, first cut | 71 | 6 |
| **Main checkout, fixed** | **71** | **6** |
| **Worktree, fixed** | **71** | **6** |

`test_doc_graph.py` **32/32**, up from 30 — DG-S drives the same fixture twice, checked out and
blind, and pins that `broken_paths` **and** `unresolvable` match across both, with a negative
control (`Projects/NotASub/...`, a directory no `.gitmodules` declares) that must still be broken so
the fix cannot degrade into "excuse everything under `Projects/`".
