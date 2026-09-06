---
IsArtifact: true
ArtifactMetadata:
  title: "SCC-417 — the banned-row gate: both orders, the plural, and another board's tickets"
  type: implementation_plan
  date: 2026-09-05
---

# Implementation Plan — SCC-417

**Ticket:** [SCC-417](https://sudo-command.atlassian.net/browse/SCC-417) (Subtask of SCC-411, the September rolling ticket) · **Lane:** `chore/SCC-417-banned-row-plural-order` off `origin/main` @ `b029aeff` · **Lane class:** TASK (`lane_qualify.py`: two toolkit paths, "this changes the development system, so it takes the full lane") · **Doors:** `/smh-quick-dev` → `/smh-code-review` → `/smh-close-task-merge-tree`

## 1. The reproduction

On 2026-09-05 SCC-416's walkthrough carried this `## Your Actions` row, verbatim:

> `- [ ] **AviationChat, after recovery, on your call — its own AVCH tickets, none of it touched here:** (1) the decision on 4afaa667 …`

`jira_feed.py finish` held the ticket at `Review Required` on it, and `jira_feed.py check-actions --walkthrough <the SCC-416 walkthrough at 604a12b0>` printed `no banned action rows, no ceremony steps`. The row hands over work for another repo and another board, which is the class `_BANNED_PATTERNS` exists to refuse.

Measured against the verbatim row (`python3 -c`, 2026-09-05):

| Pattern | Matches the row? |
|---|---|
| the current entry `\bticket\b[^\n]{0,40}?\byour\s+call\b` | False |
| order-reversed, singular: `\byour\s+call\b[^\n]{0,40}?\bticket\b` | False |
| order-reversed, plural: `\byour\s+call\b[^\n]{0,40}?\btickets?\b` | True |

Two defects in one entry: it requires "ticket" BEFORE "your call", and `\bticket\b` cannot see "tickets". The order swap alone, as the hand-over note proposed, would still have missed the row. Underneath both: no entry knows the shape "its own AVCH tickets" at all, which is a row that files work as another board's without any verb.

Corpus baseline (`corpus_sweep.py` over every tracked `walkthrough*.md`, 2026-09-05): 194 walkthroughs carry the section; the current list flags 3 rows, all three the legacy true positives already named in `test_jira_feed.py` (2026-08-12, -13, -14).

## 2. The change

### 2.1 `jira_feed.py` — the ticket × your-call entry, both orders and the plural

Replace the last `_BANNED_PATTERNS` entry with one entry carrying both orders, plural-aware, same 40-character window on each arm:

```
\b(?:tickets?\b[^\n]{0,40}?\byour\s+call|your\s+call\b[^\n]{0,40}?\btickets?)\b
```

The reason string is unchanged ("hands a ticket decision to the operator"). A short comment names the SCC-416 row and the two defects.

### 2.2 `jira_feed.py` — a seventh entry: another board's tickets named as the home

```
\b(?:its|their)\s+own\s+(?-i:[A-Z]{2,10})\s+tickets?\b
```

Reason: "files this work as another board's tickets". The project token is case-sensitive by a scoped flag group, because the list compiles under `re.I` and `[A-Z]{2,10}` would otherwise match "its own two tickets". This is the widening the code's own note calls "a decision, not a tidy-up"; this plan is that decision, and the operator's `approved` on this file is what makes it one.

**Measured before any edit** (`probe_patterns.py`, the two candidates swapped in over the live list): 6 must-flag rows flagged, 14 must-not-flag rows clean (the six new near-misses plus every existing B5 and B10 negative control), and **0 new hits across the 194-walkthrough corpus**.

### 2.3 `test_jira_feed.py` — the pins, written RED first

Inside the existing SCC-163 Part B block, using its own `flagged()` and `one_row()` helpers:

- `REAL_BANNED` gains the verbatim SCC-416 row (it runs as B5.4x).
- `SHAPES` gains three rows, each matching exactly one entry on its own: `tickets (plural) + your call` ("Whether the residue gets its own tickets is your call"), `your call + ticket (reversed)` ("Your call whether the residue becomes a ticket"), and `another board's tickets as the home` ("That work is AviationChat's, on its own AVCH tickets").
- A new list `WIDENED_PROBE` (cases B12.n): six honest rows the widened entries must NOT flag, exactly the six measured in §2.2, including the case-sensitivity near-miss ("its own two tickets") and the window near-miss (a landing-order row where "your call" and "ticket" sit 80 characters apart).

### 2.4 The revert-proof

Five code-derived mutants declared in `mutants.json` and run as one sweep by `mutation_sweep.py`, each named to the case that must kill it:

| Mutant | Decision mutated | Named case |
|---|---|---|
| M1 | NARROW: drop the reversed arm (forward order only, plural kept) | B11 `your call + ticket (reversed)` |
| M2 | NARROW: drop the plural (`ticket\b` in both arms) | B11 `tickets (plural) + your call` |
| M3 | DELETE the cross-repo entry | B11 `another board's tickets as the home` |
| M4 | WIDEN: drop the scoped `(?-i:…)` so the token is case-insensitive | B12 "its own two tickets" |
| M5 | WIDEN: the reversed arm's window 40 → 400 | B12 the 80-character landing-order row |

Then the closing full run of `test_jira_feed.py`, unfiltered, and `run_all.py`.

## 3. Acceptance

| Row | Observable | Proof |
|---|---|---|
| A | the verbatim SCC-416 row is flagged by `check-actions` | B5.4x RED on the unfixed tree, GREEN after §2.1 |
| B | "ticket"/"tickets" and "your call" are flagged in either order | B11 rows for the plural-forward and singular-reversed shapes, RED then GREEN |
| C | a row naming another board's tickets as the home is flagged | B11 `another board's tickets as the home`, RED then GREEN |
| D | no honest row is newly flagged | B12 six rows GREEN; B5 (7 allowed) and B10 (4) unchanged; `probe_patterns.py` corpus sweep: 0 new hits over 194 walkthroughs |
| E | each widening is revert-proved | five mutants killed by their named case; restore verified by the sweep |
| F | the enforcement suite is green at the shipping sha | `run_all.py` N/N files passed, `workflow_lint.py --toolkit-only` 0 errors |

## 4. Out of scope, said plainly

- The STATUS-NOTE class (a row that is a note, not an imperative) stays undetected, per the code's own B5 scoping note. Not touched.
- The creation entry's project token `(?:[A-Z]{2,10}\s+)?` runs under `re.I` while its comment says "all-caps only". Pre-existing, one line of observation here, no edit: it is not this lane's diff.
- The `jira_feed.py` copy in `Projects/sudo-command-center` (§7).
- ⚠️ AUDIT FINDING (Lens 2, F1) — this bullet used to read "no SOP edit, `[sop-ok]`". Wrong: the SOP's `## Your Actions` passage ([workflows_testing_SOP.md:1036-1043](../../../docs/_scc_sops_prds/workflows_testing_SOP.md)) names the three row classes the gate refuses, and §2.2 adds a fourth. So the SOP moves in the SAME commit: one clause in that sentence naming *work that belongs to another board* ("its own AVCH tickets"), plus one changelog row. No `[sop-ok]` on the code commit.

## 5. Sequence

1. RED: §2.3 edits; `python3 .agents/scripts/tests/test_jira_feed.py --case "legacy B"` (the Part B cases live inside the block `jira_feed · legacy B: finish - Done held back by the operator's own actions (SCC-155)`, [test_jira_feed.py:1697](../../../.agents/scripts/tests/test_jira_feed.py#L1697)); paste the red and which lines raised.
2. GREEN: §2.1 and §2.2; the same filtered run green; then the full file unfiltered.
3. `mutants.json`; `mutation_sweep.py --table … --repo <tree>`; closing full file green.
4. `run_all.py`, `workflow_lint.py --toolkit-only`, `check_links.py --base origin/main`, `probe_patterns.py` re-run on the edited tree (the corpus half now measures the shipped code).
5. `/smh-code-review` → `Verdict:` in the walkthrough.
6. Walkthrough, Dev Record, hand back for `/smh-close-task-merge-tree`.

## 6. Risk

The reversed arm shares the forward arm's exposure: a landing-order row that says "your call" and then "ticket" within 40 characters would be refused. That exposure already exists in the forward direction and measured 0 hits in 145 walkthroughs at arming (2026-08-16) and 0 new hits in 194 today. B12 pins two near-misses on each side of the window. If a live false-red ever appears, the remedy is the one `finish` already prescribes (edit the row, commit, re-run), not a wider carve-out.

## 7. Port checklist

`jira_feed.py` exists in one other repo: `Projects/sudo-command-center/.agents/scripts/jira_feed.py` (a submodule with its own GitHub origin, `main` @ `10ba6ea`). `git diff --no-index --stat` between the two copies: `167 insertions(+), 167 deletions(-)` — the copies had already diverged before this lane, and that copy carries the same defective entry at its line 2149 (`grep -n "your\\s+call"`). This lane is **not a port**: it edits the lobby copy only, and nothing in it writes to that repo. The six checks, each answered (port-checklist.md: "A check answered n/a needs the reason"):

| # | Check | Answer, from the commands run |
|---|---|---|
| 1 | a git-given path used as given | n/a — the diff is a Python regex list; `grep -n 'git-common-dir\|--git-path' .agents/scripts/jira_feed.py` has no hit in the edited region |
| 2 | `printf`, not `echo` | n/a — no shell; the script prints through `say()` |
| 3 | verify the FILE on a write | n/a — the edit writes no file; `finish`'s board writes read back already (unchanged) |
| 4 | no `.agents/rules/` path the target lacks | the edit names no rules path; the sibling carries a full `.agents/rules/` (28 files, `ls`) anyway |
| 5 | both sides | `python3` 3.11.15 here, `python` on the PC; stdlib only; the scoped-flag group needs Python ≥ 3.6 and the file already uses `str \| None` (≥ 3.10) |
| 6 | repo-local hooks + the target's OWN key | the sibling has `core.hooksPath=.githooks` but an EMPTY `.githooks/` (`ls`: nothing) and **no `.agents/jira.conf`** — no key to file a port under, and its gates are disarmed on this machine. If the operator wants the fix there, it is a ticket in that repo's own key once it has one |

## Declared Change Set

- EDIT `.agents/scripts/jira_feed.py` — the your-call entry rewritten for both orders and the plural; one new cross-repo entry → A, B, C
- EDIT `.agents/scripts/tests/test_jira_feed.py` — B5.4x, three B11 shapes, the B12 `WIDENED_PROBE` list → A, B, C, D
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — one clause in the `## Your Actions` passage: a fourth refused class, work that belongs to another board → C
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one row, newest first → C
- EDIT `.agents/scripts/INDEX.md` — the `jira_feed.py` row still says `--strict-actions` "ships disarmed (SCC-163)"; armed since SCC-164 (2026-08-16) → record
- NEW `_artifacts/_main/2026-09-05_scc-417-banned-row-plural-order/mutants.json` — the declared mutant table → E
- NEW `_artifacts/_main/2026-09-05_scc-417-banned-row-plural-order/walkthrough.md` — the record → record

## Approval

Pending. The operator's `approved` of 2026-09-05 was given in chat against the inline key points (both orders, the plural, the pinned SCC-416 row, home SCC-411) before this file existed, and it did not name §2.2 or the SOP edit. This plan needs its own `approved`.

**Approved.** Operator, 2026-09-05, in chat, on this file as pushed: "merged, and approved. do this quick though you are blocking." — recorded at `567d3040` (the plan commit; §2.2 and the same-commit SOP edit were named in the hand-back he answered).

## Self-Audit (2026-09-05)

**Level:** LEDGER+BLAST (a script others import, a gate, and a file that exists in more than one repo) · **Mode:** PRE-WORK · **Repo:** `Sudo_Hatter_Command` worktree `scc-417-banned-row-plural-order` · **Branch:** `chore/SCC-417-banned-row-plural-order` (from `git rev-parse`) · **Plan:** this file · **Ticket:** SCC-417

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every path the plan names exists (ls: 11 paths, all present)
             the helpers and lists the plan edits exist at the lines named: flagged() :2211, one_row() :2227,
               REAL_ALLOWED :2244, REAL_BANNED :2266, SHAPES :2284, FALSE_POSITIVE_PROBE :2306,
               _BANNED_PATTERNS :2130, the DELIBERATELY-NOT-DETECTED note :2152, the block label :1697
             Declared Change Set parses: present, 0 incomplete (4 entries before the audit; 7 after its findings were baked in)
             both sides: python3 3.11.15 here; PC python; stdlib only; the scoped flag group needs >= 3.6
               and the file already needs >= 3.10 (`str | None`)
             lane fit: no deployable path; the door is /smh-close-task-merge-tree
             Scope Ledger precondition: SCC-417 carries 6 Plan rows, each with an observable (acli view, quoted in §1/§3);
               plan §3 rows A-F each name a proof
             Scope Ledger: NEW mutants.json -> E; NEW walkthrough.md -> record. Caller count for mutants.json: one
               (the sweep this plan runs), countable by grep, and it is the declared shape of every revert-proof here
             tests-must-gate-for-real: RED first (§5.1), five code-derived mutants named to cases (§2.4),
               closing full file + run_all (§5.3-5.4)
read:        .agents/scripts/jira_feed.py (:2093-2160, :3591-3660), .agents/scripts/tests/test_jira_feed.py (:1697, :2180-2345),
             declared_change_set.py parse output, acli view SCC-417, lane_qualify.py (TASK), python3 --version
verdict:     clean
```

```
lens:        2 Parity + Blast
checks_run:  a script: callers - .agents/scripts/git-hooks/post-commit-jira-start.sh:119 calls `jira_feed.py start`
               (signature untouched); its test is test_jira_feed.py (edited in the same lane); scripts/INDEX.md row :23 exists
             a gate: `--strict-actions` default True (jira_feed.py:3611-3620) - ships ARMED, no arming marker to move
             the SOP: workflows_testing_SOP.md:1036-1043 names the refused classes -> FINDING F1
             a file in >1 repo: Projects/sudo-command-center (submodule, own origin) - §7 answered collectively -> FINDING F2
             sibling worktrees (after `env -u GITHUB_TOKEN git fetch origin main`): the lobby on main @ b029aeff and this tree only
             sibling branches: claude/teaching-edition (pushed @ 8b42390f, 37 ahead of origin/main) touches
               workflows_testing_SOP.md (+16) and the changelog (+1), both now in this plan's set -> FINDING F3
             twins: jira_feed.py has no cicd-/smh- twin script; the command bodies cite the gate generically (no shape list)
             risk_seam classify --repo <this tree>: status unclassified, root = this tree (the centre carries no code graph)
read:        docs/_scc_sops_prds/workflows_testing_SOP.md (:1030-1066, grep jira_feed), workflows_testing_SOP_changelog.md (:1-12, :106),
             .agents/scripts/INDEX.md:23, .agents/scripts/git-hooks/post-commit-jira-start.sh, git worktree list, git branch --list,
             git diff --stat origin/main...claude/teaching-edition, Projects/sudo-command-center (.agents/rules ls, .githooks ls, jira.conf ls, grep)
verdict:     findings below
```

```
lens:        3 Pre-Mortem
checks_run:  attached to F1 and F3 only (bounded: it originates nothing)
read:        the two findings above
verdict:     findings below (narratives attached, no new anchors)
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `docs/_scc_sops_prds/workflows_testing_SOP.md:1039-1040` | "and *mint / file / rule on where a ticket goes* (an open box there holds the ticket on the review ladder forever)" | F1 · the plan declared `[sop-ok]` while §2.2 adds a refused class this passage does not name. The armed sop-currency gate would accept the opt-out, and the manual would describe three classes while the gate refuses four. Pre-mortem: a future agent writes a fourth-class row believing it legal, the close-out refuses with a banner naming a class the manual never mentioned, and it reads as a gate bug. **Baked in:** §4 rewritten, Declared Change Set +2 rows (SOP, changelog) | medium |
| `claude/teaching-edition` @ `8b42390f` | `git diff --stat origin/main...claude/teaching-edition -- docs/_scc_sops_prds/` → "workflows_testing_SOP.md \| 16 +", "changelog \| 1 +" | F3 · landing-order dependency on the two SOP files this plan now edits. Pre-mortem: that branch lands first and the close-out absorb conflicts on the changelog's newest-first row. **Recorded:** this lane lands first (small, in flight); if it does not, the absorb keeps BOTH changelog rows and re-reads the SOP passage before resolving | low |
| this plan, §7 (pre-amendment) | "the six checks are therefore n/a here" | F2 · port-checklist.md: "A check answered n/a needs the reason", and Lens 2's row demands all six with command output. Answered collectively, not one by one. **Baked in:** §7 now carries the six rows with the commands' output | low |

### Observations

- `.agents/scripts/INDEX.md:23` says `--strict-actions` "ships disarmed (SCC-163)"; it has been armed since SCC-164 (2026-08-16). Stale before this lane; one-phrase fix added to the change set because the row describes this exact gate.
- `test_jira_feed.py:2283` "Each row below matches exactly ONE pattern": the existing SHAPES row "Mint its own AVCH ticket for the remainder" will match both the creation entry and the new cross-repo entry. First match wins, so its reason stays "CREATE", and B4 ("Mint a ticket for the N deferred items") still pins the creation entry alone. The new entry goes LAST in the list for that reason.
- `jira_feed.py:2136` says the creation entry's project token is "All-caps only", while the list compiles under `re.I`, so it is not. Pre-existing, untouched (surgical); the new entry uses a scoped flag group instead, and M4 proves that group carries weight.
- `Projects/sudo-command-center`: `core.hooksPath=.githooks` with an empty `.githooks/` directory, so its gates are disarmed on this machine. Another repo's state, not this lane's; the remedy is the migrations kit's hook arming in that repo.

**Sibling landing-order dependency:** `claude/teaching-edition` on the two SOP files (F3). This lane first.

Audit verdict: GO
