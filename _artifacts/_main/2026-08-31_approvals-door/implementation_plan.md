# SCC-354 — the `/smh-llm-approvals` door (Part A) — **Zoo only**

**Lane:** `chore/SCC-354-approvals-door`, cut from `origin/main` at `8af1f134`
**Parent:** SCC-352 (stays open until this lands) · **Sibling:** SCC-355, Part B, landed in PR #107

**Scope, re-cut 2026-08-31 on the operator's ruling.** v1 of this plan planned four platforms — Zoo,
Claude across six divergent settings stores, opencode and Codex — for nineteen declared paths. The
audit below returned **NO-GO** with thirteen findings, and most of them were consequences of that
surface area rather than of the feature. The operator's call: *"that is fine I just have another
agent edit claude since it cant edit its own files."*

**So this lane is Zoo only, and the asymmetry is the reason.** Claude Code offers "don't ask again"
in its own approval prompt, so its allow list grows as you work. Zoo has no such affordance — its
decisions live in VS Code `globalState`, the tracked settings file seeds **once** and denies never
seed at all ([[zoo-approvals-decision-store]]). Zoo is the platform that cannot help itself, and it
is the one this door serves.

**Claude gets a hand-off, not a writer** (operator, this session: *"for clause just have it give me a
copy and paste command to give an agent to update the allow list"*). Claude Code cannot edit its own
settings, so the door reads Claude's blocked commands the same way it reads Zoo's and then **prints a
paste-ready block** naming ONE target — the `.claude/settings.json` of the repo you are standing in —
and the rules to add. It never writes it. That is what replaces v1's six-store enumerator, and it is
why findings F7 and F11's store-targeting complexity dissolve rather than needing to be worked.
opencode and Codex stay out; their rows get a recorded reason, which the ticket already permits.

**Why this is not the batch-approved plan.** The consolidated plan carries a batch-approval line
recorded at `237cf3fc`, but that file's last commit is `df8f1c9d` — it was amended during the Part B
lane, so condition 3 fails and the gate re-armed. Verified by Lens 1.

---

## Acceptance — the checkable list

| # | Statement | Proved by |
|---|---|---|
| A1 | The matcher mirror is ONE module imported by both the test battery and the proposer — no second copy, and no verdict moves | `grep -c "def decide" .agents/scripts/tests/test_zoo_permissions.py` → 0, and the full existing battery passes **unchanged** |
| A2 | The reader extracts every approval-blocked command from a Zoo thread | test over a committed redacted fixture extracting a known command list, plus a declared mutant that must kill it |
| A3 | Every proposed row (a) allows its own command, (b) leaks no deny-battery row, **and (c) clears a breadth floor** | three assertions, not two — (c) is a named test that the letter `n` is refused as a proposal |
| A4 | The door PRINTS and writes nothing, and says what it scanned even when it finds nothing | `test_command_surfaces.py` (the gate that sees a missing launcher) + a fixture run leaving every store byte-identical + a zero-result run that still names the root and the counts |
| A6 | For Claude, the door prints a **copy-paste hand-off block** — the target `.claude/settings.json` and the exact rules to add — and writes nothing itself | a test that the block names a resolved store path and contains valid `Bash(...)` rules, plus a fixture run leaving that file byte-identical |
| A5 | SOP, changelog, guide §6/§11 and both INDEX files name the new door; opencode and Codex carry a recorded reason | `sop_currency.py` passes without `[sop-ok]`; `grep "to be pinned" docs/migrations/terminal-global-permission.md` goes 2 → 0; `check_links` clean |

---

## The structural finding that shapes step 1

The matcher lives **inside the test file**, `.agents/scripts/tests/test_zoo_permissions.py`. A
production path cannot import from a test without making the test a library, and copying it creates
a second copy of the one thing that exists to be the single mirror of Zoo's real matcher.

**⚠️ AUDIT FINDING F2 (pass 1) + F14/F15 (pass 2) — the extraction is five functions, TWO
constants and ONE module-level binding, and `ROOT` is DUPLICATED rather than moved.** `decide` binds its lists as default arguments evaluated at def time
(`test_zoo_permissions.py:111`, `ALLOW, DENY = load_lists()` at `:36`), so moving
`decide`/`pieces`/`_longest`/`_mask_quotes` alone raises `NameError` on import. `load_lists` and `SETTINGS` move too, **and so does the
`ALLOW, DENY = load_lists()` statement itself** — pass 2 traced it: that binding is not a name in
the declared set, so moving only the declared names still raises `NameError: name 'ALLOW' is not
defined` at import, which is the very failure F2 exists to prevent, restated one line short.

**`ROOT` cannot be moved at all — it is duplicated at two different depths.**
`test_zoo_permissions.py` still needs `ROOT` at `:26` (`GUIDE`), `:27` (`APPLY`) and `:330`/`:340`
(the `git -C` door scan), so a literal move kills the whole 78-row battery at import, before a
single case runs, and step 1's GREEN becomes structurally unreachable. So: `ROOT` stays
`parents[3]` in the test **and** is re-derived as `parents[2]` in the mirror (verified: from a module directly under `.agents/scripts/`, that is the same repo root). The test then imports `ALLOW` and `DENY` back —
it consumes them at seven sites (`:262`, `:263`, `:289`, `:290`, `:296`, `:302`, `:305`).

**⚠️ AUDIT FINDING F9 (Lens 2) — name the import mechanism.** `grep -c "sys.path\|_harness"` on the
battery file returns **0**, and `run_all.py:77` launches each test bare, so `.agents/scripts/` is not
importable from it today. Step 1 adds an explicit `sys.path.insert` — not `_harness`, which drags in
`wf_common` and `tree_guard` the file never currently runs.

## What Part B already paid for

`zoo_notify.py` is on `main` with `store_roots()` and `read_thread()`, which solve Zoo store
discovery including `zoo-code.customStoragePath` and named VS Code profiles. The reader imports them.

**⚠️ AUDIT FINDING F10 (assessor, verified) — no Linux branch.** `zoo_notify.py:56-61` falls through
to the macOS path for every non-Windows platform. CI Linux is the third machine and it is what gates
`main`. One `elif` for `~/.config/Code/User` plus a `linux` case in `test_zoo_notify.py`.

## Measured, not assumed

```
grep -l "doesn't want to proceed with this tool use" ~/.claude/projects/*/*.jsonl  ->  34 files
zoo_permissions_apply.py exposes candidate_dbs() and load_memento()               ->  importable
zoo_permissions_apply.py --status  ->  112 allow / 105 deny, tracked and live IN SYNC
.agents/commands/smh-llm-approvals.md  ->  does not exist
grep -c "to be pinned" docs/migrations/terminal-global-permission.md  ->  2
test_twin_parity.py today  ->  67/67 PASS
```

**No `--suggest` mode is added to `zoo_permissions_apply.py`.** v1 declared one; `candidate_dbs()`
and `load_memento()` are already importable, so the new script reads the live store directly and the
apply script is not touched. One fewer edited surface, and the proposer computes against the lists
Zoo is **actually** enforcing rather than the tracked file that seeds once.

---

## Steps — each names the assertion that proves it

1. **A1 — extract the matcher.** Move `decide`/`pieces`/`_longest`/`_mask_quotes`/`load_lists` and
   the `ROOT`/`SETTINGS` constants into .agents/scripts/zoo_matcher.py with `parents[2]`;
   `test_zoo_permissions.py` gains a `sys.path.insert` and imports them.
   *RED:* a new case importing `zoo_matcher` fails with `ModuleNotFoundError`.
   *GREEN:* that case passes and the whole existing battery passes **unchanged** — a verdict that
   moves is a failed extraction, not a new decision.
2. **A2 — the Zoo reader.** `zoo_threads()` over `tasks/*/ui_messages.json`, reusing
   `zoo_notify.store_roots()`, extracting every command that stopped for approval.
   *RED:* a test over the **existing** fixture `.agents/scripts/tests/fixtures/zoo_ui_messages_ask.json`
   asserting an exact command list, failing because the reader does not exist.

   **⚠️ AUDIT FINDING F21 (Lens 2 observation, verified) — no second fixture.** That file already
   carries two `ask`/`command` messages (`ls -la` and `acli jira workitem view SCC-352`), which is
   exactly what this reader must extract. v1 declared a `zoo_thread_sample.json` alongside it; a
   second redaction of the same shape is the "two copies of the one mirror" problem step 1 exists to
   kill. Dropped from the change set.
3. **A3 — the proposer, with a breadth floor.** Replay each command through `zoo_matcher.decide()`
   against the **live** memento lists and emit the shortest prefix that flips it to `auto_approve`
   **subject to the floor**.

   **⚠️ AUDIT FINDING F6 (assessor, verified by command) — this is the one that would have shipped a
   hole.** Executed against the real matcher: the shortest prefix flipping `npx create-next-app
   my-app` to `auto_approve` is the single character `'n'`; it leaks **0** of the 78 battery rows, so
   both of v1's assertions passed. That row then auto-approves `npm publish`, `node evil.js`,
   `nc -l 4444` and `netsh advfirewall set allprofiles state off`. The floor: a proposal must be at
   least the full first token of the command, and must not be a strict prefix of a token it does not
   complete.
   *RED:* three assertions — each row allows its own command; the deny battery stays all-deny with
   the row added; and `'n'` is **refused** for `npx create-next-app`.
4. **A4 — the door.** .agents/commands/smh-llm-approvals.md plus its generated launchers, printing
   grouped rows and writing nothing.

   **⚠️ AUDIT FINDING F11 (Lens 1) — name the right prover.** `workflow_lint.py:247` scans authored
   masters only and cannot see a missing launcher; A4 is proved by `test_command_surfaces.py:20`
   ("a door in the wrong place is exactly as wrong as a missing one"). `workflow_lint --toolkit-only`
   still runs — it is what proves the two INDEX rows.

   **⚠️ AUDIT FINDING F3 (Lens 2) — the suite goes red the moment the door lands.**
   smh-llm-approvals.md is an `smh-*` door with no `cicd-*` twin, so `test_twin_parity.py` block A1
   (67/67 PASS today) fails until the door has a `NOT_PAIRED` row **with its reason**. That file is
   now in the change set.

   **⚠️ AUDIT FINDING F12 (Lens 2) — author the door `cd <abs> && git`.** Both new files land inside
   `test_doors_carry_no_git_dash_c`'s scan roots; a single `git -C` fails the battery step 1 must
   keep verdict-identical.

   **⚠️ Discarded-narrative remedy folded in here:** the door prints the store root it scanned, the
   thread count read and the commands-extracted count **even when all three are zero** — the sibling
   `zoo_notify.py` already does this, and without it "nothing found" reads identically to "broken".
5. **A6 — the Claude hand-off block.** The same reader over `~/.claude/projects/*/*.jsonl`
   (verified: 34 files carry `doesn't want to proceed with this tool use`), then a printed block
   naming the resolved `.claude/settings.json` of the repo the door was run in and the `Bash(...)`
   rules to add — ready to paste to another agent. **One store, resolved from where you stand**, not
   six enumerated. The door writes nothing.
   *RED:* a test over a committed redacted Claude fixture asserting the block names a resolved store
   path and carries well-formed `Bash(...)` rules, and that the target file is byte-identical after.
6. **A5 — docs and indexes.** Guide §6/§11, both INDEX rows, the opencode and Codex reason in
   `terminal-global-permission.md`, SOP + changelog.
   *Assertion:* `sop_currency.py` passes without `[sop-ok]`; `grep "to be pinned"` goes 2 → 0.

### ⚠️ AUDIT FINDINGS F4 + F5 (Lens 2) — the commit shape, or nothing commits

Two **armed** `commit-msg` gates make the build order load-bearing (`core.hooksPath` = `.githooks`,
confirmed):

- `refresh_maps.py:47` — "every house door in `.agents/commands/` must be named as `/<name>` in the
  SOP". The commit creating the door is **rejected** unless the SOP names it in that same commit.
- `sop_currency.py:71-77` — `.agents/commands/` and `.agents/scripts/` are usage surfaces; only
  `.agents/scripts/tests/` is exempt.

**⚠️ AUDIT FINDING F16 (Lens 1 + Lens 2, `x2`) — this bound was stale v1 numbering.** The docs are
**step 6**, and step 5 stages the new llm_approvals.py, which
`sop_currency.classify()` returns as "the safety-net scripts" (executed). So the correct bound is:
**steps 1 through 5 each commit their code plus their own SOP line**, because A5 asserts
`sop_currency.py` passes *without* `[sop-ok]` and only `.agents/scripts/tests/` is exempt.

### ⚠️ AUDIT FINDING F8 (Lens 1) — the mutant table, declared before step 2

`tests-must-gate-for-real.md:70` — "proving a new test non-vacuous is a mutation". A reader returning
`[]` and a proposer emitting no rows both pass their assertions vacuously. Before step 2 is written,
_artifacts/_main/2026-08-31_approvals-door/sweep.json declares the mutants, drawn **from the code**,
each naming the case that must kill it, run via `mutation_sweep.py`.

**⚠️ AUDIT FINDING F17 (Lens 1) — one table per step, not one before step 2.** A table "drawn from
the code" cannot be written before the code exists, so A3's proposer (step 3) and A6's hand-off
block (step 5) each declare their own mutants when their code lands. The table must also cover A4's
zero-result assertion and A6's three, which pass 1's single table never mapped.

**⚠️ AUDIT FINDING F18 (Lens 1) — the two amendments were mutually incompatible, executed live.**
`mutation_sweep.judge` reads `failed = [ln for ln in out.splitlines() if ln.startswith("FAILED:")]`,
but the harness shape F13 pins prints `FAILED:` **mid-line**. Run against it,
`judge(1, '-- 11/12 passed --  FAILED: test_reader_extracts', ...)` returns
`SWEEP ERROR - ... the kill cannot be attributed to a named case` — so every mutant would have
produced no evidence at all. `test_llm_approvals.py` prints `FAILED:` at **line start**, and the
table carries `"unfiltered": true`, which `mutation_sweep.py:38-40` names as the only honest answer
for a file declaring no `c.block()`.

### ⚠️ AUDIT FINDING F13 (Lens 2) — the new test file needs a `__main__` harness

`run_all.py:93-101` counts `exit 0 with NO OUTPUT` as a **failure**. `test_llm_approvals.py` carries
the harness shape at `test_zoo_permissions.py:408-421`.

**Build order:** 1 → 2 → 3 → 4 → 5 → 6, each of steps 1-5 carrying its own SOP line.

**⚠️ AUDIT FINDING F22 (Lens 2 observation) — the door's prose is gated too.** The door body becomes
a doc-graph node the moment it lands, and `refresh_maps.py`'s RATCHET refuses any commit that raises
`broken_paths` above HEAD's count — **70 today**. Every path the door's prose names must resolve, or
the commit is refused with `[maps-ok]` as the only recorded way through.

---

## Port section (MANDATORY RULE 5)

**Trigger — TWO of them, and v1 answered only the first.**

1. *OS portability:* this lane writes `.agents/scripts/*.py` that resolve OS-dependent store roots.
2. **⚠️ AUDIT FINDING F1 (Lens 2) — the NO-GO ground: files that exist in more than one repo.**
   `Projects/sudo-command-center` is a **separate git repo** at HEAD `8fe19ad` (2026-08-24) carrying
   its own divergent copies of three paths this lane edits. Measured:

```
.agents/commands/INDEX.md                     lobby=108  child=104  differ=YES
.agents/scripts/INDEX.md                      lobby= 77  child= 79  differ=YES
docs/_scc_sops_prds/workflows_testing_SOP.md  lobby=4344 child=4228 differ=YES
```

**Ruling:** `Projects/sudo-command-center` is a **frozen snapshot, not a port target.** It is a
separate repository with its own key space; propagating a lobby door row into it would be a
cross-repo change needing that repo's own ticket ([[cross-repo-work-needs-a-ticket-per-repo]]), and
the toolkit sync deliberately covers `.agents/`, not `docs/` ([[toolkit-sync-covers-agents-not-docs]]).
Nothing in this change set is written to it. The divergence is recorded here so the next lane does
not re-discover it.

| # | Check | Answer |
|---|---|---|
| 1 | A path git gave you is used exactly as git gave it | Store paths come from `Path.home()` absolutes, never git-relative, and are printed verbatim |
| 2 | Operator-facing text goes through `printf`, never `echo` | Python `print()` throughout, **ASCII-only in the proposal rows** — `run_all.py:74` records 22 files going red on the PC when cp1252 met a decorative glyph, and the door's output is exactly what gets redirected to a file |
| 3 | On a write, verify the FILE — not `$?` | The door writes nothing; A4's byte-identical assertion is the proof |
| 4 | No path the target repo does not carry | See the ruling above: nothing is written to any project repo |
| 5 | It runs on ALL THREE machines | Mac, PC **and CI Linux** — F10 adds the missing Linux branch, and every new store-discovery case injects `platform=`/`home=` explicitly rather than inheriting `sys.platform` |
| 6 | Hooks stay repo-local; a port needs the target's OWN key | No hook is installed anywhere; no project repo is touched |

**⚠️ AUDIT FINDING F7 (Lens 1 + Lens 3, `x2`) — folded into check 5.** Store enumeration must print
its **resolved anchor root** alongside the count. Measured: from the lobby the Claude-store count is
6; from this worktree the identical command returns **1**, because `Projects/*` are mode-160000
gitlink stubs. Zoo-only scope removes the six-store enumeration entirely, but the anchor-root lesson
stands for the Zoo store: the door prints the root it scanned so "1" is legible as an environment
fact, not a bug.

---

## Declared Change Set

- NEW .agents/scripts/zoo_matcher.py — the matcher mirror: 5 names + 2 constants, extracted → A1
- EDIT `.agents/scripts/tests/test_zoo_permissions.py` — `sys.path.insert` and import the mirror → A1
- NEW .agents/scripts/llm_approvals.py — the Zoo + Claude readers, the row proposer, the Claude hand-off block → A2, A3, A6
- NEW .agents/scripts/tests/test_llm_approvals.py — reader, proposer, breadth-floor and hand-off-block tests → A2, A3, A6
- NEW .agents/scripts/tests/fixtures/claude_session_sample.jsonl — redacted Claude session → A6
- NEW _artifacts/_main/2026-08-31_approvals-door/sweep.json — the declared mutant tables → A2, A3, A4, A6
- EDIT `.agents/scripts/zoo_notify.py` — the missing Linux branch in `user_dir()` → A2
- EDIT `.agents/scripts/tests/test_zoo_notify.py` — a linux store-root case → A2
- EDIT `.agents/scripts/tests/test_twin_parity.py` — the door's `NOT_PAIRED` row and reason → A4
- NEW .agents/commands/smh-llm-approvals.md — the door brain → A4
- NEW .claude/skills/smh-llm-approvals/SKILL.md — generated Claude launcher → A4
- NEW .opencode/commands/smh-llm-approvals.md — generated opencode launcher → A4
- NEW .roo/commands/smh-llm-approvals.md — generated Zoo launcher → A4
- NEW .agents/workflows/smh-llm-approvals.md — generated Antigravity launcher → A4
- NEW .agents/skills/smh-llm-approvals/SKILL.md — generated skills-surface launcher → A4
- EDIT `.agents/commands/INDEX.md` — the new door's row → A5
- EDIT `.agents/scripts/INDEX.md` — rows for the two new scripts → A5
- EDIT `docs/migrations/terminal-global-permission.md` — the opencode and Codex recorded reason → A5
- EDIT `docs/migrations/zoo-code-permissions-guide.md` — sections 6 and 11 → A5
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the new door's usage → A5
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — the changelog row → A5
- EDIT `docs/repo-map.md` — regenerated and auto-staged by `pre-commit-maps` → A4
- EDIT `docs/doc-graph.md` — regenerated and auto-staged by `pre-commit-maps` → A4
- EDIT `docs/doc-graph.json` — regenerated and auto-staged by `pre-commit-maps` → A4
- EDIT `.agents/.sync-manifest.json` — rewritten by the launcher generator → A4

**⚠️ AUDIT FINDING F19 + F20 (Lens 2) — those last four are declared because a HOOK stages them, not
because anyone edits them.** The doc graph's roots are `['.agents','docs']` and it indexes
`.agents/commands/*.md` by row, so adding the door moves all three generated maps and `pre-commit`
stages them with the commit; `sync-agents.ps1` rewrites `.sync-manifest.json` when it emits the five
launchers (measured precedent: `c13e3976` staged the manifest beside six new commands and their
launchers). Undeclared, `/smh-code-review`'s drift check reports four-file drift on files no human
chose to touch — and a manifest left unwritten is how a later sync purges a launcher it no longer
believes it owns.

**Bare paths are deliberate:** `check_links.py:60-61` reads a backticked path with a known extension
as a claim the file exists, so files this lane has not built yet are declared bare and gain
backticks as they land.

**Cut from v1, and why:** `.agents/scripts/zoo_permissions_apply.py --suggest` (its readers are
already importable), the **six-store enumerator and every Claude write path** — replaced by the A6
hand-off block against one store — and the opencode/Codex propose paths. Claude Code grows its own allow list from its approval prompt; Zoo
cannot. The five launchers stay because `/smh-sync-agents` generates them — SCC-300 denies writes
under `.claude/skills/`, so that one mirror is hand-written byte-matching the generator, as SCC-351
did.

**Not in the set, deliberately:** no file under `Projects/*/` is written. No deployable path
(`backend/`, `frontend/`, `firebase/`, `functions/`, `mobile/`, `.github/`) is touched — MANDATORY
RULE 4 checked and clear (Lens 1 verified all entries), so this stays Task work and closes via
`/smh-close-task-merge-tree`.

---

## Self-Audit (2026-08-31)

**Level:** LEDGER+BLAST (the change set touches scripts, a door surface and five platform
launchers) · **Mode:** PRE-WORK · **review-runtime:** fan-out, three lenses run blind to each other.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  existence of all 15 named-as-existing paths + the 4 declared-NEW confirmed absent;
             plan step numbers 1-7 exist; declared_change_set.py parse -> present true, 19 entries,
             incomplete []; both-machines command audit; lane fit vs the six deployable prefixes;
             test strategy vs tests-must-gate-for-real.md; re-measurement of every "Measured, not
             assumed" number; Part B inheritance claims; git provenance of 8af1f134 / 237cf3fc /
             df8f1c9d; launcher-surface parity; Scope Ledger precondition + 11 NEW x 7 rows
read:        the plan; test_zoo_permissions.py; zoo_notify.py; zoo_permissions_apply.py;
             workflow_lint.py; sop_currency.py; check_links.py; declared_change_set.py;
             test_command_surfaces.py; test_zoo_notify.py; tests-must-gate-for-real.md;
             code-standards.md; command-shape.md; git-policy.md; terminal-global-permission.md
verdict:     findings below (3)

lens:        2 Parity + Blast
checks_run:  env -u GITHUB_TOKEN git fetch origin main FIRST; git worktree list -> 2 trees, both at
             8af1f134; traced every caller of decide/pieces/_longest/_mask_quotes repo-wide;
             traced zoo_* callers incl. .githooks/ -> empty; confirmed Part B on origin/main;
             five platform surfaces enumerated vs ALL=(claude,opencode,antigravity,codex,zoo);
             twin check -> no cicd twin, test_twin_parity.py currently 67/67 PASS; gate arming
             (commit-msg 4 gates, pre-commit 2 delegates, core.hooksPath=.githooks); _RULE_POINTERS;
             A6 assertion live (to be pinned -> 2); guide sections 6 and 11 exist; memory keys
             resolve; multi-repo sweep of every declared path across Projects/*;
             risk_seam.py classify -> unclassified (SCC-289, expected, informs nothing)
read:        the plan; test_zoo_permissions.py; test_twin_parity.py; test_command_surfaces.py;
             run_all.py; _harness.py; sop_currency.py; refresh_maps.py; workflow_lint.py;
             .githooks/commit-msg; .githooks/pre-commit; sop-currency.sh; commit-msg-maps.sh;
             smh-sync-agents.md; terminal-global-permission.md;
             Projects/sudo-command-center/.agents/commands/INDEX.md
verdict:     findings below (8)

lens:        3 Pre-Mortem
checks_run:  read the plan in full; zoo_notify.py; zoo_permissions_apply.py;
             test_zoo_permissions.py; run_all.py encoding scar; workflow_lint --toolkit-only
             branch; re-ran the plan's measured numbers inside THIS worktree; git ls-files -s
             Projects/ -> mode 160000 gitlinks; sibling-lands-first sweep across four origin/chore
             branches -> no overlap; Linux branch presence in both zoo scripts
read:        the plan; zoo_notify.py; zoo_permissions_apply.py; test_zoo_permissions.py;
             run_all.py; workflow_lint.py; .gitignore
verdict:     narratives below (8 raised, 3 attached to anchored findings, 5 discarded per the bound)
```

### Findings

| # | anchor | literal text read | consequence | severity |
|---|---|---|---|---|
| F1 | plan Port row 4 + `Projects/sudo-command-center/` (separate repo, HEAD `8fe19ad`) | Port row 4: "No `.agents/rules/` path the target repo does not carry — Nothing ships into a project repo". Measured: `.agents/commands/INDEX.md` lobby 108 / child 104 **differ**; `.agents/scripts/INDEX.md` 77 / 79 **differ**; `docs/_scc_sops_prds/workflows_testing_SOP.md` 4344 / 4228 **differ** | **NO-GO ground.** Three declared paths have live, divergent copies in a separate git repo a week old. The port section's six rows are answered in prose with no command output, and its stated trigger is OS portability — so the SCC-176 question ("which copy diverges, is that deliberate?") is never asked. `port-checklist.md` makes a plan that skips the differing-copies section a NO-GO, not a note | **NO-GO** |
| F2 `x2` | `.agents/scripts/tests/test_zoo_permissions.py:24-37` and `:111` | `ROOT = Path(__file__).resolve().parents[3]` · `SETTINGS = ROOT / ".vscode" / "settings.json"` · `ALLOW, DENY = load_lists()` · `def decide(cmd: str, allow: list[str] = ALLOW, deny: list[str] = DENY) -> str:` | The declared extraction is four functions. `decide` binds `ALLOW`/`DENY` as **default arguments evaluated at def time**, so moving four names alone gives `zoo_matcher.py` a `NameError` on import. The mirror is **five names plus two path constants**, and `parents[3]` (depth from `tests/`) becomes `parents[2]` from `.agents/scripts/`. Left uncorrected the module reads the wrong tree's settings or none, and step 1's "verdict-identical" proof compares against an empty allowlist — a green that proves nothing | high |
| F3 | `.agents/scripts/tests/test_twin_parity.py:112` and `:283` | `NOT_PAIRED = {` … `return sorted(fam - pinned - set(NOT_PAIRED))`, with `fam` built from `cicd-*.md` \| `smh-*.md` | `smh-llm-approvals.md` is an `smh-*` door with no `cicd-*` counterpart. Ran the file: **67/67 PASS today**. The moment step 5 lands the door, block A1 goes RED and stays RED, so `run_all.py` — the gate both `/smh-code-review` and `/smh-close-task-merge-tree` run — fails on a file the change set never names | high |
| F4 | `.agents/scripts/refresh_maps.py:47` + `.githooks/commit-msg` (`core.hooksPath` = `.githooks`, confirmed) | "REVERSE DOOR   every house door in `.agents/commands/` must be named as `/<name>` in the SOP." | Build order creates the door at step 5 and edits the SOP at step 7. The commit that creates the door file smh-llm-approvals.md is **rejected at commit-msg** unless the SOP names `/smh-llm-approvals` in that same commit or the message carries `[maps-ok]` — and A7 asserts `sop_currency.py` passes *without* an escape token | high |
| F5 | `.agents/scripts/sop_currency.py:71-77` | `_SURFACES: … [(".agents/commands/", (".md",), "the / command menu"), … (".agents/scripts/", (".py", ".ps1"), "the safety-net scripts")]` with `_EXEMPT_PREFIXES = (".agents/scripts/tests/",)` | Steps 1, 3, 5 and 6 each stage a usage surface. Every one of those commits must move the SOP quick-reference or carry `[sop-ok]`; only the test files are exempt. The plan never states the commit shape, so a RED/GREEN-per-step cadence stalls at the first commit | high |
| F6 | `.agents/scripts/tests/test_zoo_permissions.py:106` — **assessor finding, verified by command** | `if (s == "*" or p.startswith(s)) and (best is None or len(s) > len(best)):` | **A3 is not a floor on breadth.** Executed against the real matcher: the shortest prefix that flips `npx create-next-app my-app` to `auto_approve` is the single character `'n'`; it leaks **0** of the 78 battery rows, so **both halves of A3 pass green**. That row then auto-approves `npm publish`, `node evil.js`, `nc -l 4444` and `netsh advfirewall set allprofiles state off`. A3 forbids unlocking the 105 denies someone already thought of; it says nothing about breadth | high |
| F7 `x2` | plan `step 4` + the §correction block | "Enumerate the six stores excluding `.claude/worktrees/`" · "The six distinct stores are the lobby plus five `Projects/*/`" | Step 4 names the exclusion as the assertion but never names the **anchor root**. Measured: from the lobby root the count is **6**; from this lane's own worktree the identical command returns **1**, because `Projects/*` are mode-160000 gitlink stubs here. An enumerator anchored on `Path.cwd()` or `git rev-parse --show-toplevel` returns 1 in every worktree — including the one the door is built and demoed in — while A4's fixture-tree test still passes. Exclusion and anchor are two assertions; only one is in the plan | medium |
| F8 | `.agents/rules/tests-must-gate-for-real.md:70` and `:93` vs plan steps 2, 3, 4 | "Proving a new test non-vacuous is a mutation — the procedure is § Mutation Testing below" · "Declare the table BEFORE you mutate… A surviving mutant is a finding." | The plan creates one wholly new test file and names no way to prove any of its checks can fail for the right reason. The strings "mutation", "mutant" and "sweep" appear nowhere in it. A reader returning `[]` and a proposer emitting no rows both satisfy "no row is emitted store-less" vacuously. Step 1 is the exception and is genuinely covered | medium |
| F9 | `.agents/scripts/tests/test_zoo_permissions.py:15-22` + `.agents/scripts/tests/run_all.py:77` | `grep -c "sys.path\|_harness"` on the battery file → **0**; `run_all.py:77` launches each file bare via `subprocess.Popen([sys.executable, str(HERE / name)])` | `.agents/scripts/` is not importable from that test. Step 1's GREEN has no named mechanism, and both options change the file beyond "imports the extracted mirror": an explicit `sys.path.insert`, or `from _harness import …` which drags in `wf_common` + `tree_guard` the file never currently runs | medium |
| F10 | `.agents/scripts/zoo_notify.py:56-61` — **assessor finding, verified by reading** | `if platform == "win32": … else: base = home / "Library" / "Application Support"` | **The third machine.** `user_dir()` has no Linux branch; the `else` falls through to the macOS path. Port row 5's "unit-tested under simulated darwin/win32" is true and incomplete — CI Linux is what gates `main`, and it went red on exactly this class of assumption last lane. Any new store-discovery case that omits `platform=`/`home=` returns `[]` on CI and passes green having read nothing | medium |
| F11 | `_artifacts/_main/2026-08-31_approvals-door/implementation_plan.md` row A5 + `.agents/scripts/workflow_lint.py:247` | "⛔ Scans the AUTHORED masters only. Generated mirrors (`.claude/skills`, `.opencode`, `.agents/workflows`) are byte copies…" | A5's named prover cannot see a missing launcher, so A5 goes green with 3, 4 or 5 of 5 present — the exact failure the plan's own closing paragraph predicts. The gate that sees it is `test_command_surfaces.py:20` ("a door in the wrong place is exactly as wrong as a missing one") | medium |
| F12 | `.agents/scripts/tests/test_zoo_permissions.py:324-341` | `dirs = (ROOT / ".agents" / "commands", ROOT / ".agents" / "rules", ROOT / ".agents" / "skills")` … `assert not offenders, f"doors still spell git -C (Zoo auto-denies it)"` | Two of step 5's new files land inside this scan's roots. A single `git -C` spelling in the door body fails the battery step 1 must keep verdict-identical, surfacing as a step-1 regression rather than a step-5 authoring bug | low |
| F13 | `.agents/scripts/tests/run_all.py:93-101` | `return name, 1, (f"{name}: exit 0 with NO OUTPUT - this file executed nothing (missing __main__ harness?)\n")` | `FILES` auto-arms `test_llm_approvals.py` by glob, so no arming marker is needed — but the bare runner means the new file needs a `__main__` harness or it is counted a failure. Steps 2-4 never mention it | low |

### Sibling landing-order dependency

**None.** `git worktree list` returns exactly two trees, the lobby and this lane, both at `8af1f134`,
which is `origin/main` after an explicit fetch. The lobby's tracked tree is clean. Lens 3 separately
swept four `origin/chore/*` branches for overlap with this change set and found none.

### Observations (uncounted, no check gating them)

- **The Zoo memento is currently IN SYNC**, so the "proposals computed against the wrong list" risk
  is a design constraint, not a live defect: `--status` reports 112 allow / 105 deny on both the
  tracked file and `state.vscdb`. It still shapes the build — `--suggest` should replay through the
  live store's lists and print which store each proposal was computed against, because the two
  drifting apart is the reason `zoo_permissions_apply.py` exists at all.
- `destructiveCommandGuardEnabled: False` on this machine, so the lists are the only fence.
- Declaring five launcher files commits the door to a universal `platforms:` list. `smh-quick-fix.md`
  declares four platforms and correctly has no `.roo/commands/` file; if this door is not meant for
  Zoo, one of the five declared paths becomes a ghost the surfaces test flags.
- Every measured claim in the plan re-measured true (Lens 1): `to be pinned` → 2, `--status`/`--apply`
  and no `--suggest`, 34 session files, the door absent, 6 stores from the lobby and 35 including
  worktrees. The batch-approval re-arm reasoning verified correct — `237cf3fc` is the approval
  commit, `df8f1c9d` is the plan's last commit, so condition 3 genuinely fails.
- The plan's matcher line range ("41–137") is two lines long; the block runs 41–135. Nothing turns on it.

### Pre-Mortem bound applied

Lens 3 raised 8 narratives and **cannot originate a finding**. Three attached to anchored findings
(F2, F7, and the store-drift observation). Two more were promoted only because the assessor
**verified them with a command** and they now stand on that output, not on the narrative — F6 and
F10, both labelled above. The remaining three — an absent-store early exit, silent-empty output, and
a cp1252 encoding truncation — had no originating anchored finding and were **discarded, not
demoted**, per the bound. The absent-store and empty-output concerns are answered anyway by F11's
remedy, which requires the door to print the root it scanned and the counts it read.

**This is the frozen pass-1 record. It was superseded by pass 2 below, whose verdict is the
live one.**

Audit verdict: NO-GO

---

## Self-Audit (2026-08-31, pass 2 — re-audit after the NO-GO)

**Level:** LEDGER+BLAST · **Mode:** PRE-WORK, re-audit of the re-cut plan · **Lenses:** 1 and 2 only.
Lens 3 was not re-run: it is bounded and cannot originate a finding, and its pass-1 narratives were
already harvested into F6, F7 and F10.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every NEW factual claim the re-cut introduces, each verified by command — candidate_dbs
             and load_memento importable (True/True); zoo_notify has no Linux branch (grep -> 0);
             test_twin_parity 67/67; run_all counts exit-0-no-output as failure; check_links path
             claim semantics; sudo-command-center separate repo, 3 paths differ; the F6 breadth hole
             re-executed against the live matcher; the F2 extraction shape; every F4/F5/F9/F11/F12/
             F13 anchor; the whole Measured block re-measured; git provenance of 8af1f134 /
             237cf3fc / df8f1c9d; existence sweep 22 present + 12 NEW absent; step numbering;
             declared_change_set parse; both-machines; lane fit; test strategy vs
             tests-must-gate-for-real.md incl. a LIVE mutation_sweep.judge() call; Scope Ledger
verdict:     findings below (5)

lens:        2 Parity + Blast
checks_run:  fetch origin/main FIRST -> 8af1f134; 2 worktrees, lane diff EMPTY; NO-GO ground tested
             against the MACHINERY — sync-agents.ps1 target guard read in full, maintained-projects,
             check_maps fan_out_targets, grep -rn "sudo-command-center" across .agents/ docs/
             _artifacts/_memory/ -> ZERO; AST-traced the module-level free names of all five
             extracted functions; NOT_PAIRED mechanism + ran the file; sop_currency _SURFACES /
             _EXEMPT_PREFIXES / main() + refresh_maps reverse_door_check + the 4-gate commit-msg
             chain + SOP-ENFORCE marker; every user_dir() caller repo-wide; five platform doors vs
             ALL=(claude,opencode,antigravity,codex,zoo); doc-graph roots and index rows;
             git show --stat c13e3976 for real blast precedent; declared_change_set diff semantics
verdict:     findings below (5)
```

### The pass-1 NO-GO ground: CLEARED

Not by prose but by machinery. `Projects/sudo-command-center` is
`https://github.com/sudomadhatter/sudo-command-center.git` with its own toplevel, held here as a
`160000` gitlink — a stub, not tracked content. No propagation path reaches it:
`sync-agents.ps1:117-124` refuses any non-lobby target outright and `:102-107` refuses
`-Maintained`; `.agents/maintained-projects.txt` names only `AGY_AVIATIONCHAT` and
`NEXgen-VR-Director`; and `grep -rn "sudo-command-center"` across `.agents/`, `docs/` and
`_artifacts/_memory/` returns **zero hits**. The frozen-snapshot ruling holds.

### Findings — all baked into the plan body above

| # | anchor | consequence | severity |
|---|---|---|---|
| F14 | `test_zoo_permissions.py:36` | `ALLOW, DENY = load_lists()` is a module-level *statement*, not a name in the declared set — moving only the declared names still raises `NameError` at import, the exact failure F2 exists to prevent | high |
| F15 | `test_zoo_permissions.py:26-27`, `:330`, `:340` | `ROOT` cannot be *moved*: the test needs it at four sites, so a literal move kills the 78-row battery at import and makes step 1's GREEN structurally unreachable. It is duplicated at two depths | high |
| F16 `x2` | plan commit-shape block | the bound was stale v1 numbering — "Steps 1–4" is one short after the renumber, and step 5 stages a `_SURFACES` script, so its commit is rejected by an armed gate | high |
| F17 | plan mutant-table block | a table "drawn from the code" cannot be declared before the code exists; A6's three assertions and A4's fourth were unmapped | medium |
| F18 | `mutation_sweep.py:186-189` vs `test_zoo_permissions.py:421-422` | **executed live:** the pinned harness prints `FAILED:` mid-line, `judge()` requires line-start — every declared mutant would have returned `SWEEP ERROR`, producing no evidence at all | high |
| F19 | `pre-commit-maps.sh:2`, `doc-graph.md:235` | three generated map files are staged by a hook on the door's commit; undeclared, the review's drift check reports them | medium |
| F20 | `sync-agents.ps1:222`, `c13e3976` | `.sync-manifest.json` is rewritten when the launchers are emitted; left unwritten, a later sync purges a launcher it no longer believes it owns | medium |
| F21 | `fixtures/zoo_ui_messages_ask.json` | the fixture already carries two `ask`/`command` rows; the declared second one was a redundant redaction — dropped | low |
| F22 | `refresh_maps.py` RATCHET | the door body becomes a doc-graph node; any path its prose names must resolve or the commit is refused. `broken_paths` = 70 today | low |

**Verified correct and unchanged:** `test_twin_parity.py` is the right file and `NOT_PAIRED` the
right mechanism (67/67 today, and `smh-sync-agents.md` is the row shape to copy); the Linux branch is
safe, with `zoo_permissions_apply.py:49` already spelling `~/.config/Code/User` as the house
precedent; no `cicd-*` twin exists or should. Scope Ledger precondition **MET**, all 12 `NEW` rows
have a populated acceptance cell, **zero ledger findings**. Lane fit clean — no deployable path, no
`Projects/*` write. Both machines clear.

### Gates re-run after the amendments

```
declared_change_set.py parse   ->  present: true, 25 entries, incomplete: []
check_links.py --paths         ->  clean
```

### Sibling landing-order dependency

**None.** Two worktrees, both at `8af1f134` = `origin/main` after an explicit fetch; the lane has no
commits yet and nine other `origin/chore/*` branches have no live worktree here.

Audit verdict: GO
