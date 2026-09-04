---
IsArtifact: true
ArtifactMetadata:
  title: SCC-74 consolidate procedural docs into docs/_scc_sops_prds + arm drift monitoring
  type: implementation_plan
  date: 2026-08-10
---

# SCC-74 — consolidate the SOPs + PRDs into `docs/_scc_sops_prds/`

## Goal

Every procedural document — the pages that tell the operator *what to do* and *what to type* — moves
into one monitored folder, `docs/_scc_sops_prds/`, and the drift monitoring that today protects
exactly one of them is extended to cover all of them. Then the accumulated staleness in those docs
gets fixed.

## The finding that drives the whole plan

The docs did not go stale from neglect. They went stale because **they live inside the one folder
every drift-checker in this system is explicitly forbidden to look at.**

`_my_resources/` is named in `SCAN_IGNORES` (`.agents/scripts/check_maps.py:60`), in
`DEFAULT_REGEN_IGNORE` for the repo-map (`check_maps.py:66`), in the GitNexus ignore list, and its own
`_my_resources/AGENTS.md:23-24` says *"excluded from repo-map regen + linter scans … do not 'fix'
that."* Ten of the thirteen procedural docs sit inside it. No automation can reach them. That is the
root cause, and moving them is the fix — the monitoring rule is only the second half.

**Operator rulings, 2026-08-10 (this session), which settle the shape:**

1. Target is **`docs/_scc_sops_prds/`**, not a new top-level folder — everything documentation-shaped
   stays under `docs/`.
2. The SOP PRD **moves and is renamed** to drop the retired `sudo-` prefix. (This reverses the
   "brand names keep sudo" line in the SCC-63 plan, which had exempted this filename.)
3. **`_my_resources/` is Daniel's human thinking + brainstorming space. Agents ignore it entirely
   unless he links a specific document.** Staleness there is acceptable by design — it is a
   scratchpad, not a contract.
4. **`docs/` must always be kept from going stale.** That is the maintained surface.

(3) and (4) together are the real thesis: the two folders get *opposite* treatment, so a procedural
doc sitting in the wrong one is a defect by definition. That is why this move is not cosmetic.

`docs/` is already inside scanner scope (absent from `SCAN_IGNORES` and `DEFAULT_REGEN_IGNORE`), and
`docs/_scc_sops_prds/` is a **level-2 folder**, which means `check_maps.py` check 2.5
(`check_maps.py:389-410`) will *require* it to carry an `INDEX.md` and fail if it drifts. The chosen
location buys enforcement for free.

## Evidence of current rot (measured this session)

| Defect | Count | Where |
|---|---|---|
| INDEX lists files that do not exist | 2 | `diagrams_guides/INDEX.md` → `gitnexus-usage-guide.md`, `updated_folder_file_structure_diagram.md` |
| Files on disk absent from the INDEX | 4 | sentry, file_folder_structure, md_feedback, adviser-board |
| Dead relative links | 5 | incl. both autopilot copies → `../../.claude/commands/` (a door **retired by SCC-66**) |
| Unresolved command references | **3** | `/sudo-update-scrum-board` (retired SCC-13), `/new-project` + `/sync-agents` (renamed by SCC-63 to `smh-*`) |
| References to a deleted directory | 9 | `_bmad-output/sudo-tests…` — **that path does not exist** |

> **Correction to an earlier figure in this plan's own research.** A first pass reported "26 retired
> `sudo-` hits across 8 docs." That was a crude grep and it was wrong in both directions. Ground-truthed:
> **3** are genuinely unresolved command references; **9** point at a deleted `_bmad-output/sudo-tests…`
> directory (real staleness, but a dead *path*, not a retired command); and **3** are
> `sudo-command.atlassian.net` — the **real Jira site slug**, which must not be touched. The remainder
> were substring noise. This is precisely the "wrong in ways a regex cannot see" trap the plan warned
> about, caught by the TDD detector-validation step rather than by a find-and-replace in Phase 6.
| Duplicate doc, diverged | 508 differing lines | `autopilot_bmad_dev_loop.md` exists in `.agents/reference/` (38,770 B) **and** `_my_resources/diagrams_guides/system/` (36,354 B) |

## Target state

```text
docs/
  AGENTS.md                     <- local law; gains a section for the new folder
  repo-map.md                   <- AUTO body regenerated (new folder appears)
  workspace-standard.md         <- STAYS (agent-facing law, already in scope)
  system-builder.md             <- STAYS
  gitnexus.md                   <- STAYS
  _scc_sops_prds/               <- NEW. Flat. 13 docs + INDEX.md
    INDEX.md                    <- required by check_maps check 2.5
    workflows_testing_SOP.md    <- was _my_resources/_quick_reference/sudo_workflows_testing.md
    jira_manual.md
    jira_integration_guide.md
    git_walkthrough_settings.md
    autopilot_bmad_dev_loop.md  <- ONE copy; the 508-line divergence resolved
    sentry_error_response_team.md
    file_folder_structure+maintaining.md
    complete-system-overview.md
    md_feedback_setup_guide.md
    tea_testing_guide.md
    tea_deep_reference.md
    tdad_stack_install_guide.md
    smh-adviser-board-REFERENCE.md

_my_resources/                  <- human space. Agents IGNORE unless Daniel links a doc.
  board_sessions/ migrations/ open_tasks/ research_docs/ youtube_transcripts/
  _quick_reference/             <- becomes EMPTY -> removed
  diagrams_guides/              <- becomes EMPTY -> removed
```

**Assumption stated for reversal:** `workspace-standard.md`, `system-builder.md`, and `gitnexus.md`
stay at `docs/` root. They are agent-facing law that `AGENTS.md` routes to in six places, they are
already inside scanner scope, and `workspace-standard.md` alone carries 18 live inbound references
plus a vendored copy in every project. Moving them buys nothing and costs a wide rewrite. One line to
reverse if you disagree.

**Assumption:** flat, no subfolders. Thirteen docs do not need `system/` `security/`
`workflows_tea_testing/` partitions, and a flat level-2 folder is exactly what the INDEX rule
enforces cleanly.

## Blast radius — measured, not estimated

Hand-edited files: **~32**. The 132-file raw grep is misleading; it double-counts a stale
`.claude/worktrees/` checkout (another lane's tree — **do not touch**, per the worktree gate) and
`_artifacts/` history.

| Surface | Files | Note |
|---|---|---|
| `.agents/commands/` | 6 | INDEX, cicd-autopilot-deepseek4, cicd-quick-dev, smh-adviser-board, smh-close-task-merge-tree, smh-sync-agents |
| `.agents/rules/` | 2 | INDEX, **sop-currency.md** |
| `.agents/scripts/` | 4 | INDEX, sop-currency.sh, **sop_currency.py**, workflow_lint.py |
| `.agents/scripts/tests/` | 1 | test_sop_currency.py |
| `.agents/reference/` | 1 | INDEX (folder empties — see Phase 3) |
| root `AGENTS.md` | 1 | SOP path ×2 + the `_my_resources` posture |
| `docs/AGENTS.md` | 1 | new folder's local law |
| `_my_resources/AGENTS.md` + `README.md` | 2 | exceptions collapse; new ignore posture |
| `_bmad/custom/.../bmad-quick-dev.toml` | 1 | SOP path |
| the 13 docs themselves | 13 | internal cross-links |

**Regenerated, never hand-edited:** `.agents/workflows/`, `.opencode/commands/`, `.claude/skills/`
and the machine caches — `/smh-sync-agents` rewrites them after the masters change.

**Deliberately NOT rewritten:** `_artifacts/` walkthroughs and plans. They are the historical record
of what was true when written; rewriting history to match the present is how an audit trail stops
being one.

## Development method — TDD (operator ruling, 2026-08-10)

**Ruling: this Task is developed test-first.** Every item in the Definition of Done is written as an
executable assertion **before** the work that satisfies it, and every one of them **fails today** —
so the red phase is real, not manufactured.

New test file: `.agents/scripts/tests/test_sops_prds_folder.py`, registered in `run_all.py`.

| # | Assertion | Red today because | Goes green in |
|---|---|---|---|
| T1 | `docs/_scc_sops_prds/` exists and holds the 13 expected docs | folder does not exist | Phase 1–2 |
| T2 | its `INDEX.md` matches the directory exactly — every row resolves, every file has a row | folder does not exist; the INDEX it replaces has **2 phantom rows + 4 omissions** | Phase 1 |
| T3 | 0 dead relative links across the folder | **5 dead links** today, incl. both autopilot copies → the retired `.claude/commands/` door | Phase 6 |
| T4 | 0 references to retired `/sudo-*` command names | **26 hits across 8 docs** | Phase 6 |
| T5 | `sop_currency.py`'s `SOP_DOC` resolves to a file that exists | will break the instant the doc moves | Phase 4 |
| T6 | `_my_resources/` holds no procedural docs | 13 live there | Phase 2 |
| T7 | exactly one copy of `autopilot_bmad_dev_loop.md` in the repo | two copies, 508 differing lines | Phase 3 |

**This is what "monitored so they never go stale" actually means.** T2–T4 are the drift monitoring the
ticket asks for, and as `run_all.py` members they are *enforced on every run* — a stronger guarantee
than a commit-time co-occurrence gate, which only proves the author looked. The gate and the tests are
complements: `sop_currency.py` asks "did you update the PRD," the suite asks "is the folder still
correct."

> ⚠️ This **supersedes** the audit's F2 verification bullet. F2 said "prove `check_maps.py` catches a
> broken INDEX row." T2 does that as a permanent test rather than a one-off manual check. Keep the
> `check_maps.py` coverage — it is free and it guards the whole repo — but T2 is the regression that
> stays.

**Order per phase: red → implement → green.** No phase closes with its assertion still red, and no
assertion is written after the code that satisfies it.

**Honest limit:** T1/T6 encode a fixed 13-doc manifest, which is a snapshot, not a law — adding a
14th doc must be a deliberate edit to the test. That is the intent: the manifest is the contract, and
a doc appearing or vanishing without a test change is exactly the drift being guarded against.

## Phases

### Phase 0 — lane setup
Worktree gate: this Task produces commits, so it gets its own tree before the first file is edited.
- `chore/SCC-74-consolidate-sops-prds` off **`main`** (Task lane, not a story lane).
- `.agents/scripts/link-worktree-assets.py` for the gitignored assets.
- Remove the stray empty top-level `_scc_sops_prds/` (untracked, 0 files — created before the
  location was settled).

> ⚠️ **AUDIT FINDING F4 — a concurrent lane overlaps this one.** `git worktree list` shows
> **SCC-77 live** at `.claude/worktrees/scc-77-main-write-gate` (`chore/SCC-77-main-write-gate`,
> at `8e2ee83`): *"Enforce the main-branch write gate: cross-platform pre-push hook + single-use
> merge token."*
>
> SCC-77 is building **git hooks**. SCC-74 edits `sop_currency.py` and its `sop-currency.sh` hook
> shim and touches `.agents/scripts/git-hooks/`. That is a genuine overlap on the hook installer and
> the hooks directory — the SET rule binds on **file overlap**, so these two are not safely parallel
> in that area.
>
> **Before Phase 4 touches anything under `.agents/scripts/git-hooks/`:** diff that path against
> SCC-77's branch and confirm the two lanes do not both edit it. If they do, sequence them — land one,
> rebase the other. ⛔ Never sweep, revert, or file findings against SCC-77's in-flight work; its
> checkout is its world, and its 104 grep hits in the earlier sweep were its own tree, correctly
> excluded from this plan's blast radius.

### Phase 1 — create the folder + its INDEX
- `docs/_scc_sops_prds/INDEX.md` — one row per doc: what it is, when to reach for it. This is the
  file `check_maps.py` check 2.5 requires; writing it first means the folder is never non-compliant.

### Phase 2 — move with history intact
- `git mv` every doc (preserves `git log --follow`; a delete+add loses the provenance that tells us
  when a line went stale).
- `sudo_workflows_testing.md` → `workflows_testing_SOP.md` in the same `git mv`.

### Phase 3 — resolve the autopilot duplicate
Two copies, 508 differing lines. Diff them, determine which lines are *newer* rather than merely
different, merge into one doc at `docs/_scc_sops_prds/autopilot_bmad_dev_loop.md`. Then
`.agents/reference/` holds only its INDEX — retire the folder and fold its "why this is off-surface"
rationale into the new INDEX. **This one needs your eyes on the merged result before it lands**;
I will surface the diff rather than silently pick a winner.

### Phase 4 — the monitoring (the ticket's actual ask) — **REWRITTEN BY AUDIT**

> ⚠️ **AUDIT FINDING F2 (reinvention) + F1 (invented scope).** The original Phase 4 proposed making
> `sop_currency.py` "folder-aware" and encoding a **usage-surface → doc mapping**. Both were wrong.
> `check_maps.py` *already* enforces the bulk of what this ticket asks for, on `docs/`, today — and
> the mapping was unimplementable without inventing requirements. Phase 4 shrinks accordingly.

**What the move alone buys — zero new code.** `check_maps.py` walks every `INDEX.md` outside
`SCAN_IGNORES` (`docs/` is in scope; `_my_resources/` is not) and already reports:

| Existing check | What it catches once the docs are in `docs/_scc_sops_prds/` |
|---|---|
| `INDEX.md paths` (`check_maps.py:638-643`) | every phantom row — the exact defect rotting `diagrams_guides/INDEX.md` today (2 dead rows) |
| `level-2 INDEX presence` (`:389-410`) | the folder losing or never having its `INDEX.md` |
| `folder coverage` + `repo-map paths` | the new folder going missing from the repo-map, and dead paths in its CURATED header |
| `AUTO block freshness` | the repo-map tree drifting from disk after any add/remove |

That is the "drift monitoring" the ticket asks for, and **relocation is the entire implementation.**
Phase 4 must *verify* this rather than assume it — run `check_maps.py` against a deliberately broken
INDEX row and confirm it fails.

**What actually needs new work — one string, not a subsystem:**
- `sop_currency.py:60` `SOP_DOC` → the new path. Behavior unchanged: still one specific document,
  still co-occurrence, still armed by `SOP-ENFORCE`, `[sop-ok]` still the logged opt-out.
- `test_sop_currency.py` updated. Regression cases A–D and X (the `lstrip` bug) must keep passing.

**Explicitly CUT (finding F1):** any surface → doc mapping table. Nobody can answer "which command
change obliges `tea_deep_reference.md` to be updated," so the mapping would be invented, and a gate
satisfied by *any* file in the folder is weaker than the one we already have. The SOP PRD keeps its
single-path contract; the other 12 docs are covered by `check_maps.py` structural checks plus the
Phase 6 content sweep.

**Ownership, stated so a fifth checker never gets built:** `sop_currency.py` = "did the author update
the PRD in the same commit" (co-occurrence). `check_maps.py` = "does the INDEX match disk, does the
folder exist in the map" (structure). `generate_doc_graph.py` = dangling-link reporting (report-only).
`workflow_lint.py` = command-surface INDEX links. No overlap, no new mechanism.

**Trap to verify, not assume:** the commit that moves the SOP doc must itself pass the gate. The hook
runs the working-tree copy of `sop_currency.py`, so the new path is what gets checked and it *is*
staged — but `git diff --cached --name-only` reports renames differently depending on rename
detection. I will test this against a real staged rename before relying on it.

### Phase 5 — rewrite the ~32 live references
Mechanical, but two need care: `AGENTS.md` (the front door) and `sop-currency.md` (the rule that
describes the gate) both narrate the old path in prose, not just links.

### Phase 6 — fix the stale content (the ticket's second half)
Per doc: 26 retired-`sudo-` hits, 5 dead links, both autopilot copies pointing at the retired
`.claude/commands/` door, and `git_walkthrough_settings.md` — the example you named. Each doc gets
read and corrected, not find-and-replaced; a prefix rename can be wrong in ways a regex cannot see
(the `sudo-project-skeleton` repo name and the `Sudo_Hatter_Command` brand legitimately keep it).

> ⚠️ **AUDIT FINDING F3 — two docs describe the very structure this ticket changes.** The plan
> treated all 13 as cargo to be moved and spell-checked. These two are different: their *subject* is
> the folder layout, so the move makes their content wrong, not merely stale.
>
> - **`file_folder_structure+maintaining.md`** — the files-and-folders guide. Must gain
>   `docs/_scc_sops_prds/`, drop `_my_resources/_quick_reference/` + `diagrams_guides/`, and state the
>   new **`_my_resources/` = human space, ignored unless linked** posture.
> - **`complete-system-overview.md`** — describes the system layout; same treatment. Also the
>   staleness outlier at last-substantive-commit **2026-06-26**, and it still points at a
>   `_docs/master-implementation-plan.md` whose folder no longer exists.
>
> Without this, the consolidation ships a folder whose own structure guide describes the *previous*
> structure — the exact failure mode SCC-74 exists to end.

### Phase 7 — the `_my_resources/` posture change
Your ruling (3) is a law change, and it belongs in this ticket because it is the flip side of the move:
- `_my_resources/AGENTS.md` — the `_quick_reference/` standing exception is **deleted** (the folder
  is gone). New posture: ignore entirely unless Daniel links a specific document. `migrations/` keeps
  its run-when-pointed-at exception; being pointed at *is* the link.
- `_my_resources/README.md` and root `AGENTS.md` §4 — restate it.
- Remove the now-empty `_quick_reference/` and `diagrams_guides/`.

> ⚠️ **AUDIT FINDING F5 — do not trust the INDEX as the inventory before deleting.**
> `diagrams_guides/INDEX.md` is *measurably* unreliable: 2 rows point at files that do not exist and
> 4 files on disk are absent from it. Confirm both folders are empty with `find`, against the disk,
> immediately before removal — never against the INDEX, and never from the move manifest alone. A
> deletion justified by a stale inventory is how a doc nobody listed disappears silently.

### Phase 8 — regenerate + gate
- `/smh-sync-agents` (mirrors), `generate_repo_map.py` (AUTO body), `generate_doc_graph.py`.
- `python3 .agents/scripts/tests/run_all.py` — expect 11/11.
- `workflow_lint.py --toolkit-only`, `check_maps.py`, dead-link re-check → 0.
- `closeout_preflight.py --repo … --branch … --expect-key SCC-74` (pass both flags explicitly; it
  resolves the repo from CWD and has reported on the wrong lane's branch before).

## Open item needing your word (not blocking Phases 0–3)

`_artifacts/_memory/` holds facts that name the old path — `sop-doc-currency-gate.md` and
`relocated-doc-links-are-mispathed-not-dead.md` at minimum. After the move they are wrong. But the
memory store is **read-only outside the sanctioned write flows**, so I will not edit them as part of
the mechanical sweep. I will surface the exact list at close-out for your call.

## Self-Audit (2026-08-10)

Run via `/cicd-self-audit`. **Step 0 deviation:** that command binds a child project under
`Projects/` and explicitly refuses the lobby (`cicd-self-audit.md:22-28`). Invoked on the operator's
instruction against `Target: Sudo_Hatter_Command (LOBBY, adapted)`. There is no story file, no ACs and
no sprint board, so AC-traceability was run against the **SCC-74 ticket text + the operator rulings**
as the requirement source. That mismatch is the gap **SCC-78** was minted to close.

**Right-size: FULL.** It modifies a commit gate, a constant consumed by seven files, and the front
door — not a contained change.

| Phase | Walked | Result |
|---|---|---|
| 0 · Scope + AC coverage | 9 proposed changes mapped to the 4 ticket asks + 2 operator rulings | 1 gap → **F3** |
| 1 · Blast radius | `SOP_DOC` consumers traced (7); folder-existence contracts; concurrent lanes | 1 collision → **F4** |
| 2 · Over-engineering | 9 tripwires; 2 fired (invented mapping, reinvention) | **F1**, **F2** |
| 3 · Pre-mortem | 8 failure paths; 5 already covered by the plan | 1 gap → **F5** |

**Graph-first note:** GitNexus was *not* used for the blast radius, deliberately. This change moves
**path strings**, and an AST code-graph has no edges for those; grep is the authoritative tool here,
not a fallback. The lobby index is routing-surface only. Stated so the omission reads as a decision.

| # | Finding | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| **F1** | Phase 4 proposed encoding a *usage-surface → doc mapping* | HIGH | Unimplementable without inventing requirements — nobody can say which command change obliges `tea_deep_reference.md`. A gate satisfied by *any* file in the folder is **weaker than the one we already have**. | **CUT.** Phase 4 rewritten |
| **F2** | Reinvention — `check_maps.py` already enforces INDEX-path validity + level-2 INDEX presence across `docs/` (`:638-643`, `:389-410`) | HIGH | Building a fifth overlapping checker; and the plan overstated the work — most of the requested monitoring arrives **free from the move**. | **REVISED.** Phase 4 shrinks to one string + a verification; ownership boundaries stated |
| **F3** | `file_folder_structure+maintaining.md` and `complete-system-overview.md` *describe the structure this ticket changes*; plan treated them as cargo | MED | Ships a folder whose own structure guide documents the previous structure — precisely the failure SCC-74 exists to end. | **ADDED** to Phase 6 |
| **F4** | SCC-77 (`chore/SCC-77-main-write-gate`, live worktree) is building **git hooks**; SCC-74 edits `sop-currency.sh` + `.agents/scripts/git-hooks/` | MED | Two lanes editing the hooks dir; the SET rule binds on file overlap, so these are not safely parallel there. | **ADDED** to Phase 0 as a pre-check + sequencing rule |
| **F5** | Deletion of the emptied folders was justified against the INDEX | LOW | That INDEX is *measurably* unreliable (2 phantom rows, 4 omissions) — a doc nobody listed disappears silently. | **ADDED** to Phase 7: confirm with `find` against disk |

**Four gates**
- **Verification strategy?** Present and now stronger — F2 converts an assumption into an executable
  check (break an INDEX row, confirm `check_maps.py` fails).
- **Irreversible / destructive?** Yes — two folder deletions and 13 moves. Gated: `git mv` preserves
  history, deletions are `find`-verified (F5), and every step is revertable on a `chore/*` branch.
- **Any step vague enough the dev will guess?** One remains by design: the 508-line autopilot merge.
  Not tightened — it is routed to the operator rather than resolved by rule, because "which lines are
  newer" is a judgment call, and a plan that pretends otherwise invites a confident wrong merge.
- **Quality fit?** Anchored — `git mv` over delete+add, stdlib-only, existing gate idioms
  (`SOP-ENFORCE`, `[sop-ok]`) preserved rather than reinvented.

**Decomposition:** considered and rejected *after* F2. The gate work looked like a second kind of
work worth splitting out; once F2 reduced it to a one-string change, the split stopped paying.

**Audit verdict: GO** — as revised. NO-GO as originally written; F1–F5 are baked into the phases
above, and the net effect is a **smaller** plan than the one audited.

## Definition of done

- 13 docs in `docs/_scc_sops_prds/`, one copy each, `git log --follow` intact.
- `INDEX.md` matches the directory exactly — 0 phantom rows, 0 missing files.
- 0 dead links across the folder; 0 retired-`sudo-` command references.
- `sop_currency.py` points at the new SOP path, stays armed, and its A–D/X regressions pass.
- **Monitoring proven, not assumed (F2):** a deliberately broken INDEX row makes `check_maps.py`
  fail. If it does not, the monitoring claim is false and the ticket is not done.
- **The two structure-describing docs describe the NEW structure (F3).**
- **No hook-directory collision with SCC-77 (F4)** — verified before Phase 4, sequenced if present.
- `_my_resources/` contains no procedural docs, both emptied folders `find`-verified before removal
  (F5), and its law states the ignore posture.
- run_all 11/11, lint 0 errors, check_maps clean, preflight green on `SCC-74`.
