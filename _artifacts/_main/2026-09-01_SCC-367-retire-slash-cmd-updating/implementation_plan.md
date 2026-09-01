# SCC-367 — Retire `/smh-slash-command-updating` into `/smh-sync-agents`

**Lane:** `chore/SCC-367-retire-slash-cmd-updating` · **Base:** `origin/main` @ `1adaffae`
**Ticket:** [SCC-367](https://sudo-command.atlassian.net/browse/SCC-367)
review-runtime: fan-out

## Why

`/smh-slash-command-updating` is a **self-described thin alias**. Its entire body is
`sync-agents.ps1 -GlobalsOnly`, and its own closing bullet tells the operator to prefer plain
`/smh-sync-agents`, which does the globals pass *and* the local doors. A command whose
documentation ends by recommending a different command is a menu row that costs six generated
door files, three INDEX rows, an SOP row, a `NOT_PAIRED` decision row and a comment in the sync
engine — and buys nothing a flag does not.

The one thing it holds that is **not** redundant is the SCC-332 explanation: the two machine-global
caches have **different sources**, because Antigravity truncates any workflow over 12,000 chars
instead of rejecting it, so it must receive the thin launchers from `.agents/workflows/` while
opencode receives the full bodies from `.agents/commands/`. That law is load-bearing and moves
into `/smh-sync-agents` rather than dying with the alias.

## Acceptance — every row is checkable

| # | Statement | How it is checked |
|---|---|---|
| **A** | The name `smh-slash-command-updating` appears on **zero live surfaces** — the six door files are gone, and no live command / rule / INDEX / SOP doc names it | new `CS-22` assertion in `test_command_surfaces.py` over a `RETIRED` registry (name -> retiring ticket) |
| **B** | `/smh-sync-agents` carries a `-GlobalsOnly` section stating **both** per-cache sources and the 12,000-char Antigravity truncation reason | same assertion pins both source paths + the cap number in `smh-sync-agents.md` |
| **C** | `NOT_PAIRED` in `test_twin_parity.py` holds no key whose command master is gone | new assertion: every `NOT_PAIRED` key resolves to a file in `.agents/commands/` |
| **D** | The enforcement suite passes, CS-18 included (its SCC-332 ordering checks named the retired command) | `python3 .agents/scripts/tests/run_all.py` exits 0 |
| **E** | The SOP §3 menu no longer lists the retired command, staged in the same commit | `sop_currency.py` exits 0 at commit; grep of §3 returns nothing |
| **F** | The lane's artifact set is complete — plan, ticket outline, closing walkthrough — per `artifacts-always-first` | the three files exist in `_artifacts/_main/2026-09-01_SCC-367-retire-slash-cmd-updating/`; `walkthrough_roster.py` parses the walkthrough at close-out |

## Steps

1. **Assertions first (RED).** Add `CS-22` to `test_command_surfaces.py` (rows A + B), then the
   `NOT_PAIRED`-keys-exist check `A0c` to `test_twin_parity.py` (row C).
   ⚠️ **AUDIT FINDING — CS-22 scans all six door surfaces plus the live doc set, never the master
   alone**, and keys on the current `smh-slash-command-updating` spelling only (the
   `slash_command_updating` history passages must survive). A master-only scan goes green while the
   generated mirrors stay dirty. CS-22 is **red on arrival** — the master and every reference still
   exist. `A0c` is **green on arrival** (measured: 35 keys, 0 missing) and turns red the instant
   step 2 lands, which is what proves it has teeth.
2. **Delete the six doors.** The master plus its five generated launchers. Steps 3–7 turn CS-22 green.
3. **Port the law into `/smh-sync-agents`** — a `-GlobalsOnly` section carrying the per-cache
   sources and the SCC-332 truncation reason (row B).
4. **Clean the engine + registries** — `sync-agents.ps1:60`, `test_twin_parity.py` NOT_PAIRED row,
   `test_command_surfaces.py:2728` comment and the `RULE_SITES` entry at `:2748`.
5. **Clean the menus** — `.agents/commands/INDEX.md` (3 sites), `.agents/workflows/INDEX.md` (row 23),
   SOP §3 (row 4302).
6. **Regenerate and sync.** Run the sync (`-WhatIf` first) so the manifest and the five generated
   door surfaces agree with the master set, ⚠️ **including the two `smh-sync-agents` full-body
   mirrors the audit found**; regenerate `docs/doc-graph.json`; then the full suite.

## Declared Change Set

- DELETE `.agents/commands/smh-slash-command-updating.md` — the master; the alias itself → A
- DELETE `.agents/workflows/smh-slash-command-updating.md` — generated Antigravity door → A
- DELETE `.agents/skills/smh-slash-command-updating/SKILL.md` — generated Claude/Codex launcher → A
- DELETE `.claude/skills/smh-slash-command-updating/SKILL.md` — generated Claude menu door → A
- DELETE `.opencode/commands/smh-slash-command-updating.md` — generated opencode mirror → A
- DELETE `.roo/commands/smh-slash-command-updating.md` — generated Zoo Code door → A
- EDIT `.agents/commands/smh-sync-agents.md` — receives the `-GlobalsOnly` section and the SCC-332 law → B
- EDIT `.agents/scripts/sync-agents.ps1` — the line-60 comment stops naming a command that is gone → A
- EDIT `.agents/scripts/tests/test_command_surfaces.py` — new CS-22; stale comment and RULE_SITES entry removed → A
- EDIT `.agents/scripts/tests/test_twin_parity.py` — NOT_PAIRED row removed; keys-exist assertion added → C
- EDIT `.agents/scripts/tests/test_sops_prds_folder.py` — added during REVIEW: the SOP edit tripped its T4 (`every command reference resolves`), so the retired name joins `DISCUSSED_AS_RETIRED` with its reason → E
- EDIT `.agents/commands/INDEX.md` — three references to the retired command removed → A
- EDIT `.agents/workflows/INDEX.md` — the alias's router row removed → A
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — §3 menu row removed → E
- EDIT `.agents/workflows/smh-sync-agents.md` — generated full-body mirror; carries the retired name at :85 → A
- EDIT `.opencode/commands/smh-sync-agents.md` — generated full-body mirror; carries the retired name at :85 → A
- EDIT `docs/doc-graph.json` — generated doc index; 25+ entries name the retired files, regenerated in step 6 → A
- EDIT `.agents/.sync-manifest.json` — regenerated by the sync in step 6 → A
- EDIT `docs/doc-graph.md` — the Markdown twin of the graph; the generator writes both → A
- EDIT `_artifacts/_main/INDEX.md` — this lane's session row (required by `check_maps` F2), plus a pre-existing orphaned merge-conflict marker found on `origin/main` at line 8 → F
- NEW `_artifacts/_main/2026-09-01_SCC-367-retire-slash-cmd-updating/implementation_plan.md` — this plan → D
- NEW `_artifacts/_main/2026-09-01_SCC-367-retire-slash-cmd-updating/tickets/SCC-367.md` — the ticket fast-read outline → D

## Out of scope — named, not silently dropped

- **`Projects/sudo-command-center`** carries its own copy of every one of these files. It is a
  **separate GitHub repo** (`sudomadhatter/sudo-command-center`), so per the cross-repo rule it needs
  its own ticket in its own key space. Not touched here.
- **Eight pre-existing dangling `/cicd-*` and `/smh-*` doc references** turned up while probing for a
  blanket guard (mostly `_AP`-suffix and example-text artifacts). A general dangling-reference guard
  would drag that cleanup into this lane and manufacture findings with no anchor in this diff, so
  CS-22 is scoped to an explicit `RETIRED` registry (name -> retiring ticket) instead.

---

## Self-Audit (2026-09-01)

**Level: LEDGER+BLAST** — the Declared Change Set carries six `DELETE` ops, a script, a
command/door surface across four platforms, and files that exist in more than one repo. Any one of
those forces the heavier level. **Mode:** PRE-WORK. **Lenses ran inline, not fanned out** — a
16-file doc/test lane does not earn three subagents, and with three findings on two anchors
corroboration sorting is moot.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every DELETE path exists on disk (6/6 OK)
             every EDIT path exists on disk (8/8 OK)
             Declared Change Set parses: 16 entries, incomplete: 0
             both-machine commands exist (run_all.py, sop_currency.py, declared_change_set.py, sync-agents.ps1)
             lane fit: zero deployable paths in the set -> /smh-close-task-merge-tree is the right door
             Scope Ledger precondition: ticket acceptance rows >= 2, each with a concrete observable
read:        .agents/commands/*, .agents/workflows/*, .agents/skills/*, .claude/skills/*,
             .opencode/commands/*, .roo/commands/*, .agents/scripts/sync-agents.ps1,
             declared_change_set.py parse output, acli jira workitem view SCC-367
verdict:     findings below (1 of them closed during the audit)
```

```
lens:        2 Parity + Blast
checks_run:  command file changed -> all four platform doors + commands/INDEX.md enumerated
             command NAME retired -> every live reference across .agents/, docs/, AGENTS.md
                                     (AGENTS.md: clean; _artifacts/ excluded as read-only history)
             script changed -> .githooks callers (none), its test, scripts/INDEX.md (clean)
             path DELETE -> every tracked mirror of the edited command enumerated
             file exists in >1 repo -> port-checklist.md fired; answered with the diff (below)
             sibling worktrees -> git worktree list: none besides this lane; no landing-order dependency
             risk_seam -> unclassified, correctly and permanently (SCC-289: the centre has no code graph)
read:        git ls-files | grep smh-sync-agents (6 mirrors, 3 carry the retired name),
             git diff --no-index across both repos, .agents/scripts/sync-agents.ps1:60 and :496
verdict:     findings below
```

```
lens:        3 Pre-Mortem
checks_run:  attached one failure narrative to finding 1 (below); originated nothing
read:        .agents/scripts/tests/test_command_surfaces.py CS-18 L/M commentary
verdict:     attached to finding 1
```

### The port section — `port-checklist.md` fired, and this is its answer

`Projects/sudo-command-center` carries a copy of **seven** of this lane's files, so the checklist
fires mechanically. Answered with the diff, not memory:

| Measured | Result |
|---|---|
| `git diff --no-index` on all 7 shared files | **all 7 already differ** |
| divergence size | `sync-agents.ps1` **326 lines**, `workflows_testing_SOP.md` **730 lines**, `test_twin_parity.py` 42, `smh-sync-agents.md` 12 |
| shared history | **none** — `git cat-file -e 1adaffae` fails in that repo; 5 total commits, unrelated histories |
| last touched | 2026-08-24 |
| `maintained-projects.txt` | not listed |

**Conclusion: it is not a mirror, it is a separate published skeleton product** with its own GitHub
remote (`sudomadhatter/sudo-command-center`) and its own key space. The six checks are **N/A — no
code is being ported in either direction.** Per the cross-repo rule, aligning it is its own ticket
in its own key space, and doing it from this lane would be a cross-repo commit with the wrong key.

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/workflows/smh-sync-agents.md:85` (and `.opencode/commands/smh-sync-agents.md:85`) | "skills mirror, plus the one-time Codex prompts retirement purge — what `/smh-slash-command-updating` delegates to) ·" | **Two generated full-body mirrors of the command being edited carry the retired name and are absent from the Declared Change Set.** They land in the real diff, so `/smh-code-review` Step 2 flags undeclared drift; and until a sync runs they keep acceptance row A literally false. | **HIGH** |
| `docs/doc-graph.json:550` | `"path": ".agents/commands/smh-slash-command-updating.md",` | The generated doc-graph carries 25+ entries naming the retired files, is undeclared, and leaves row A false on a literal read of "zero live surfaces". Needs a regen in the lane. | **MEDIUM** |
| SCC-367 description, as first read | `Placeholder - the fast-read outline is written by jira_ticket.py describe once the lane's artifact folder exists.` | **Scope Ledger precondition failed** — the ticket carried no acceptance rows, which is a NO-GO ground. | **CLOSED during the audit** — six rows with concrete observables now on the ticket via `jira_ticket.py describe`; re-read and confirmed. |

**⚠️ AUDIT FINDING — baked into the Declared Change Set above.** Findings 1 and 2 add three `EDIT`
rows (`.agents/workflows/smh-sync-agents.md`, `.opencode/commands/smh-sync-agents.md`,
`docs/doc-graph.json`) and amend step 6.

### Pre-Mortem — attached to finding 1

The lane ships, and the operator's next Antigravity session still shows the ghost. Mechanism, and
it is already written down in this repo: `test_command_surfaces.py` CS-18 L/M says *"`$IsLobby` is
false in a worktree — so this lane's own sync wrote 4 local twins and left the cache in its
23-over-cap defect state while every source-side check stayed green."* The identical shape applies
here. A CS-22 that scans only `.agents/commands/` goes green the moment the master is deleted,
while two generated mirrors on disk still name the retired command and the machine caches are
untouched.

**Fix, baked into step 1:** CS-22 scans **all six door surfaces plus the live doc set**, never the
master alone — so the assertion cannot go green until every surface is actually clean.

### Observations (uncounted, no severity)

- `.agents/scripts/sync-agents.ps1:496` and `.agents/commands/INDEX.md:71` name the **old
  snake_case** `slash_command_updating` inside passages documenting *retired* behaviour — the SCC-56
  name filter that was removed, and the SCC-63 rename. **Leave them.** Scrubbing them erases the
  record of why the filter and the rename happened, and CS-22 must therefore key on the current
  `smh-slash-command-updating` spelling, not a loose `slash.command.updating` match.
- `_artifacts/` carries roughly thirty historical references. Read-only history, out of scope by
  convention.

```
Audit verdict: GO
```
