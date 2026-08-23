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
in one shot on this working tree, one commit at the end."*** Shipping sha `52edbb2` for A/B/C; `14ed813` and `1624a5d` add the two close-out fixes in
Findings 4 and 5.

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

**Re-run at the close-out tip `1624a5d`**, after `origin/main` was absorbed and Finding 4 was
fixed: `run_all.py` **58/58 files**, `refresh_maps.py --verify` **exit 0**, `mutation_sweep.py`
**34/34 killed** (M28–M32 for `--repair`, M33–M34 for the bytecode purge), with
`test_jira_ticket.py` at **41/41** because the sweep was run outside the sandbox. `check_maps --all` still exits 1 on the same
two pre-existing rows below and nothing else.

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

## Mutation sweep — 34/34 killed

`python3 .agents/scripts/mutation_sweep.py --table _artifacts/_main/2026-08-22_graph-to-projects/sweep.json`

```
-- sweep clean: 34/34 killed by their declared case --
```

Every mutant is drawn from a **decision in the source**, not from the cases. Coverage: `risk_seam`
(M1–M3), the triggers (M4–M5), the ratchet and door check (M6–M8, M26–M27), the kill switch (M9),
`--verify` read-only (M10), ordering and self-inclusion (M11–M12), the mermaid strip in both
directions (M13–M14), lobby-relative ids and relative roots (M15–M16), the label (M17), check 10's
project skip (M18), the PS installer (M19), and `jira_ticket` (M20–M25).

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
| The 75 broken doc references repo-wide | The ratchet's whole design (Decision 5): it forbids an INCREASE, it does not demand zero on day one. Most are stale references inside old migration guides |
| AGY's vendored `scripts/check_maps.py`, `generate_repo_map.py` | All three already differ from the masters, and check 10 is lobby-only by construction (F1), so porting would add a check that never fires. Cross-repo work needs an **AVCH** key (plan §7, F8) |
| The PC half — `commit-msg-maps.sh`, `pre-commit-maps.sh`, `pre-push-maps-verify.sh` and the F2 installer fix | Written for both machines (`python3 → python → py`, ASCII output, `printf` only) and **verified on the Mac only**. The PowerShell installer case DID run here on `pwsh`. Re-verify on the next PC session |

---

## Your Actions

**What landed:** `52edbb2` (all three riders' scope) and `14ed813` and `1624a5d` (Findings 4 and 5,
both found while closing the lane out — the second by the first one's symptom), on `chore/SCC-288-graph-to-projects`. Gates green at the tip,
34/34 mutants killed.

⛔ **No adversarial review verdict on this lane.** `/smh-code-review` was the next door and it was
not run — the close-out was invoked straight after the build. Nothing was waved through: with no
verdict the preflight grants **no SKIP**, so the full mechanical gate ran at the landing sha rather
than being cited from a review. Stated here because the walkthrough carries no `Verdict:` line and
that absence should be a fact on the record, not something a later reader has to notice.

**What I decided, and why, without asking:**
- Moved the two truth checks from `pre-commit` to a new `commit-msg` delegate. The ratchet could not
  otherwise be satisfied by the commit that introduces it, and every future root addition would hit
  the same wall. It mirrors `sop-currency.sh` exactly.
- Used `[maps-ok]` on this commit as a **recorded re-baseline**, with the reason written into the
  commit message. It is in the log forever, which is the design.
- Fixed the repo-map's root label at the source rather than exempting worktrees from `--verify`.
  It was required for B to work at all, and it retires a long-standing false positive.
- Left the two `auth_keys` dead-path rows alone; they are pre-existing and outside this diff.

- [ ] **Create an Atlassian API token on this Mac and store it as `sudo-jira`** (plan step C0 — the
      one item in this lane an agent cannot do). Until then `jira_ticket.py attach` exits 5 and
      prints the setup; `describe` and `done` work now, so the fast-read shape lands either way.
      Guide: `docs/migrations/install_guides/jira-api-token-setup.md`.
- [ ] **Decide whether `jira_feed.py mint` should adopt the fast-read shape** on a BMAD-lane ticket
      (deferred C5 above). It is a scope call, not a defect.
