---
IsArtifact: true
ArtifactMetadata:
  title: Artifacts rule hardening — read the local law, fix the dead lobby pointer, record the verdict home
  type: walkthrough
  date: 2026-07-26
---

# Walkthrough — Artifacts rule hardening

## What this was

A verification pass, asked for after a stretch of hand-cleaning and re-indexing misplaced artifacts.
The question was whether the artifacts rule actually tells an agent to read a project folder's own
instructions before placing a file there.

**It did not.** The placement for story 21.3 was correct — that part of the read was right — but the
rule that produced it was correct by luck, not by instruction.

## What I checked first

21.3's artifacts sit at `Projects/AGY_AVIATIONCHAT/_artifacts/epic_21/story-21-3-student-archive-never-delete/`
with `implementation_plan.md` + `self-audit-stress-test.md` + `walkthrough.md`. Same shape as its four
siblings. `git ls-tree main_debug` confirms they landed at those paths, nothing sits loose at the
`_artifacts/` root, and nothing leaked into the lobby bucket. Placement: clean.

Then three defects underneath it.

### D1 — the rule never said to read the local law

`§2`'s project-local branch named `active-context.md`/`INDEX.md` and said "follow its rules" — but never
said to **open** `<project>/_artifacts/AGENTS.md`, which is the file that actually is the local law. That
file carries buckets the global rule does not contain at all:

| Work type | project local law | global rule alone |
|---|---|---|
| debugging / ad-hoc | `debugging/<YYYY-MM-DD>_<slug>/` | `_main/<YYYY-MM-DD>_<slug>/` ❌ |
| TEA / non-numeric story id | `tea/<story>/` | `<YYYY-MM-DD>_<slug>/` ❌ |
| structured debug epic | `epic_debug_<N>/<story>/` | not mentioned ❌ |

Story work survived only because `epic_<E>/<story>/` happens to appear in both lists. Every debugging and
TEA session written by a rule-only agent lands in the wrong bucket. That is the recurring cleanup, and it
was structural.

### D2 — the code-review verdict had two competing homes

`§6` and a Hard Stop demanded `code-review.md` in the session folder. `sudo-code-review.md:87` writes
`_bmad-output/implementation-artifacts/sudo-code-review-<story>.md`. Epics 11–12 followed the rule;
epic 15 onward follows the command. Both readable, but a reader trusting the rule looks in the wrong place.

### D3 — a dead pointer in three live files

`_artifacts/AGENTS.md:24`, `README.md:1,10`, `INDEX.md:5` all sent the reader to `_artifacts/aviationChat-AGY/`
in the lobby. That path does not exist — the Claude bucket is `_artifacts/AGY_AVIATIONCHAT/`.
`aviationChat-AGY` survives only as opencode's namespace, under a pre-rename folder name. An agent trusting
the pointer creates a second bucket.

## What fought back

Nothing technical. The one thing that changed mid-flight was scope: the first draft proposed making
"append a row to `INDEX.md`" a per-session obligation, on the evidence that **`epic_21` appeared nowhere
in the ledger** — not one of its five stories.

That was the wrong conclusion from a correct observation. The ledger already has machinery: the
SessionStart hook chain runs `check_maps.py --depth3-only` ("Checking depth-3 _artifacts INDEX...") and
`record_map_changes.py --nag`, and `/update-maps-indexes` does the real reconcile — deliberately, on
cheaper agents. Baking a hand-append into every session would have duplicated all of that and burned
expensive context on mechanical work. **Withdrawn on the operator's call**, and the rule now says so
explicitly so the next agent does not re-propose it.

The five missing `epic_21` rows were still backfilled by hand — kept in scope for the opposite reason:
the "What" column needs story knowledge (why 21.2 was descoped, what R1 actually was, which of 21.12's
findings stayed latent) that a mechanical reconciler cannot recover.

## What changed, file by file

**`.agents/rules/artifacts-always-first.md`** — four edits:

1. The **top blockquote's** project-local sentence now says read `Projects/<name>/_artifacts/AGENTS.md`
   **first**, and that it wins.
2. **§2's project-local bullet** carries the ⛔ mandate plus the worked example — AGY's three extra
   buckets, named — so the failure mode is concrete rather than abstract. Also states that the local law
   **overrides the task-type list below it**, which is the part that was ambiguous.
3. A new blockquote after the task-type list: **the ledger is reconciled in batch, do NOT hand-append a
   row every session**, naming the hook scripts and `/update-maps-indexes`, with the one carve-out (append
   by hand only when you are the only one who can write the row).
4. **§6** gains the sudo-lane exception recording `_bmad-output/implementation-artifacts/` as the verdict's
   home, with the note that epics 11–12 predate it and both are valid history — so a future reader checks
   both places before concluding a review was never persisted.
5. Two **Hard Stops** updated: a new one for the local law, and the code-review one now names both
   locations.

The two vendored copies (`Projects/AGY_AVIATIONCHAT/`, `Projects/Fresh_Workspace_BMAD/`) were byte-identical
to the master beforehand and were re-copied verbatim. `/sync-agents` copies commands and skills but **never
rules** — these are hand-vendored, which is why the copy is a step and not a sync.

**`Projects/AGY_AVIATIONCHAT/_artifacts/{AGENTS.md, README.md, INDEX.md}`** — the three dead pointers now
name `_artifacts/AGY_AVIATIONCHAT/`. `AGENTS.md` additionally records opencode's `aviationChat-AGY`
namespace as a third place to *read*, never a place to write from — otherwise the next person to notice the
folder re-introduces the same confusion. Historical hits under `_archived/` and inside old walkthroughs are
immutable history and were left alone.

**`Projects/AGY_AVIATIONCHAT/_artifacts/INDEX.md`** — five backfilled rows (21.3, 21.12, 21.1, 21.6, 21.2),
newest-first in the existing order.

## Verification — actual output

```
=== live aviationChat-AGY pointers remaining ===
Projects/AGY_AVIATIONCHAT/_artifacts/AGENTS.md:25:  reconstruct full history. (opencode's home-base namespace is `_artifacts/opencode/aviationChat-AGY/`,

=== epic_21 rows now in the ledger ===
5

=== rule copies still identical ===
OK  Projects/AGY_AVIATIONCHAT
OK  Projects/Fresh_Workspace_BMAD
```

The single remaining hit is the deliberate opencode-namespace note, not a live pointer.

Scoping check before commit — only this session's files dirty in each repo:

```
##### .                              main_debug
 M .agents/rules/artifacts-always-first.md
?? _artifacts/_main/2026-07-26_artifacts-rule-hardening/
##### Projects/AGY_AVIATIONCHAT      main_debug
 M .agents/rules/artifacts-always-first.md
 M _artifacts/AGENTS.md
 M _artifacts/INDEX.md
 M _artifacts/README.md
##### Projects/Fresh_Workspace_BMAD  main
 M .agents/rules/artifacts-always-first.md
```

---

# Round 2 — auditing `/update-maps-indexes`, and the law consolidation

The follow-on question was whether `/update-maps-indexes` is detailed enough that a weaker model would
update every INDEX, AGENTS and README correctly — plus a direct question: do we actually need both a
README and an AGENTS.md per folder?

## What the linter proved

Running it rather than reading it was the whole value:

```
[INDEX.md paths]            [ok] clean
[depth-3 _artifacts INDEX]  [x] _artifacts/epic_21/INDEX.md: missing row for `story-21-3-...`
[level-2 INDEX presence]    [x] .ruff_cache/0.15.21/INDEX.md: missing
[tier-2 local law]          [ok] guarded dirs carry AGENTS.md + adapters (redirects verified)
```

- **The root ledger has no row-completeness check at all.** Depth-3 caught the missing 21.3 row instantly,
  while the *root* `_artifacts/INDEX.md` was missing all five `epic_21` stories and every check said
  `[ok] clean`. `[INDEX.md paths]` only verifies that paths a row *mentions* resolve — never that a session
  folder *got* a row. That asymmetry is the entire reason epic 21 went unindexed.
- **Step 3 contradicted the fan-out.** Its opening line read "for **every home-base** `INDEX.md`
  (`Projects/` are skipped)" while Step 0.5 says run it per workspace. A weak model follows the literal
  line and never audits a project's INDEXes.
- **`.ruff_cache` was a permanent FATAL false positive.** `check_level2_indexes` skipped `SCAN_IGNORES` and
  `.git` at level 1 but not dot-dirs generally, so it descended into a build cache and demanded an
  `INDEX.md` in it — while the level-2 loop one line below already skipped dot-dirs. A fatal check that
  cries wolf every run is how a real check gets trained into background noise.

## The proposal I withdrew

I had ranked a new "check 10 — local-law pointer lint" highly: run the existing `dead_paths()` over the
tier-2 law files with its table-rows-only restriction lifted, to catch stale prose pointers like the
`aviationChat-AGY` one from round 1.

Two things killed it.

First, the operator's objection: a grep-based sweep can't see into `Projects/` at all, because those are
gitignored from the lobby root — it would have returned clean for every project and *looked* like a
passing check. (Moving it into the linter answers that; `check_maps.py` walks with `os.walk` under
`--root` and never reads gitignore.)

Second, and decisive: **testing it against reality.** The line I had written into `_artifacts/AGENTS.md`
two hours earlier references `_artifacts/opencode/aviationChat-AGY/` — a *lobby* path, cited from inside
AGY. First segment `_artifacts` is a real top-level folder there, and `AGY/_artifacts/opencode/` doesn't
exist, so check 10 would have flagged my own correct line on day one. Adding a noisy hint while removing a
noisy fatal (the `.ruff_cache` fix) is incoherent — noise is what trained agents to ignore these checks in
the first place. The bug it targets has fired **once**, on a two-month-old folder rename.

Deferred, with the trigger stated: a second rename-strands-prose incident, or the consolidation below
failing to shrink the path count.

## Do we need both a README and an AGENTS.md?

`docs/workspace-standard.md` already answers it, and the answer indicted what was on disk.

- Tier 2 (`_artifacts/`, `_my_resources/`, `docs/`) **must** carry a local-law `AGENTS.md` + adapters —
  it's on the format checklist and in the PATH CONTRACT.
- `README.md` is **not** required: `check_maps.py` never mentions it, and no adapter loads it.
- The reading-order rule: *"`AGENTS.md` = behavior, `INDEX.md` = contents. Complements, not substitutes."*
- And the binding constraint: *"a Tier-2 `AGENTS.md` is a **digest that points at canon** — never a second
  canonical copy."*

That last line was being violated in every `_artifacts/` folder in the system. The placement law existed
**four** times per folder — the global rule, `AGENTS.md`, `README.md`, and `INDEX.md`'s header — and they
had drifted in the worst possible direction:

| File | Routing branches it listed |
|---|---|
| `AGENTS.md` (**auto-loaded**) | 3 — no `debugging/` |
| `README.md` (never loaded) | 5 |
| `INDEX.md` header (never loaded) | 5 |

The file agents actually load was the *least* complete one. AGY's `AGENTS.md` even contradicted itself
inside eight lines: no `debugging/` in its WRITE list, then `debugging/` named as a valid bucket parent in
its NEVER line. Fresh carried the identical defect, which makes it template-inherited, not a one-off.

## What changed

**`.agents/scripts/check_maps.py`** — one condition, plus a comment saying why: dot-dirs are tool caches,
never content, so they never owe an `INDEX.md`.

**`.agents/workflows/update-maps-indexes.md`** — Step 3 rewritten at the top: the scope line now reads
"every `INDEX.md` in the workspace you are currently reconciling," with a note explaining that the
`Projects/` skip applies only to a bare lobby lint. Added a ⚠️ block stating outright that **a clean lint
proves nothing about root-ledger row completeness**, citing this exact incident. Added the row schema —
the two-table shape (session table first, bucket summary lower down), "copy the columns already in use,
never invent or reorder," and what belongs in a "What" cell, with the note that a row reading
"Story 21.3 work" is *worse* than no row because it looks reconciled.

**Nine files consolidated** — `_artifacts/{AGENTS.md, README.md, INDEX.md}` × lobby, AGY, Fresh:

- `AGENTS.md` is now the single placement authority in each, with the **complete** branch list — AGY gains
  `debugging/`, `tea/`, `epic_debug_<N>/` and `_archived/`; Fresh gains `debugging/`; the lobby's
  cwd-decides-first rule is now explicit (*if cwd is a project, stop — you do not write here*).
- `README.md` keeps what a digest can't carry — the file-shape table, the bucket inventory, the archive
  rationale, continuity — and states plainly that placement is deliberately not restated, with a line
  telling the next author to put new rules in `AGENTS.md` instead.
- `INDEX.md` headers became pointers.
- All three also stopped instructing "append a row to `INDEX.md`", which had directly contradicted the
  batch-reconcile note added in round 1.

Two depth-3 rows added — `epic_21/INDEX.md` for 21.3 and `_main/INDEX.md` for this session — under the
rule's own carve-out (append by hand only when you're the only one who can write the row).

## Verification — actual output

```
######## AGY ########                    ######## LOBBY ########
[level-2 INDEX presence]  [ok] clean     [level-2 INDEX presence]  [ok] clean
[depth-3 _artifacts INDEX] [ok] clean    [tier-2 local law]        [ok] (redirects verified)
[tier-2 local law] [ok] (redirects verified)
```

The `.ruff_cache` fatal is gone from both. Tier-2 still verifies clean after nine files were rewritten,
so no adapter or law file was broken in the process.

**Not fixed, deliberately:** six `_main/INDEX.md` rows in the lobby (`2026-07-23_code-standards-gate`,
`2026-07-23_reindex-gitnexus`, `2026-07-24_sudo-close-workingtree`, `2026-07-24_sudo-flow-rules-audit`,
`2026-07-24_update-sudo-close-workingtree`, `2026-07-25_sudo-command-optimization`). Those are earlier
sessions; writing their "What" cells would mean inventing summaries for work I wasn't in, which is exactly
the worse-than-nothing row the new guidance warns about. They belong to a `/update-maps-indexes` run.

## Task Checklist

- [x] Verify 21.3's artifact placement against disk **and** against `main_debug`
- [x] Audit `artifacts-always-first.md` for the read-the-local-law instruction — absent, confirmed
- [x] Diff the global rule's buckets against AGY's local law — 3 buckets missing from the global rule
- [x] Locate every vendored copy of the rule (6 on disk; AGY + Fresh are the maintained two)
- [x] D1 — read-the-local-law mandate (blockquote + §2 + Hard Stop)
- [x] D2 — §6 sudo-lane verdict exception + Hard Stop rewording
- [x] Ledger note: batch reconcile, no per-session append (scope change, operator's call)
- [x] Vendor to AGY + Fresh, verified byte-identical
- [x] D3 — three dead `aviationChat-AGY` pointers repaired
- [x] Backfill the 5 `epic_21` INDEX rows
- [x] Verify + commit one commit per repo
- [x] **Round 2** — audit `/update-maps-indexes` by running its linter, not reading it
- [x] Workflow Step 3: scope contradiction, "a clean lint proves nothing here" warning, row schema
- [x] `check_maps.py`: dot-dir skip at level 1 (`.ruff_cache` fatal false positive)
- [x] Answer the README/AGENTS question against `workspace-standard.md` rather than by preference
- [x] Consolidate the placement law 4 copies → 1 across 9 files (lobby, AGY, Fresh)
- [x] Backfill the two depth-3 rows that are mine to write
- [x] Re-run the linter: dot-dir FP gone, tier-2 still clean after the rewrites
- [x] Withdraw the check-10 proposal on evidence; record the trigger that would revive it
- [ ] **Deferred:** check 10 (local-law pointer lint) — would false-positive on day one; revisit on a
      second incident
- [ ] **Not done:** six `_main/INDEX.md` rows for earlier sessions — batch work for `/update-maps-indexes`
- [ ] **Not done:** `Fresh_Workspace_BMAD` is on `main` — committed locally, not pushed (owner-only branch)

## Your Actions

Ad-hoc toolkit maintenance, so no story worktree — committed directly on each repo's own branch per
`worktree-per-story`'s Trigger exemption. One commit per repo, never cross-committed:

| Repo | Branch | Commit |
|---|---|---|
| lobby `Sudo_Hatter_Command` | `main_debug` | rule hardening + this artifact folder |
| `Projects/AGY_AVIATIONCHAT` | `main_debug` | vendored rule + 3 pointer repairs + 5 INDEX rows |
| `Projects/Fresh_Workspace_BMAD` | `main` | vendored rule only |

**Left for you:**

1. **Nothing is pushed.** All three commits are local. AGY's would go to `main_debug` normally; say the word
   and I'll push it.
2. **`Fresh_Workspace_BMAD` sits on `main`**, which is yours alone — so its commit stays local regardless.
   Its earlier commit `803fbf1` is also still unpushed from the previous session.
3. **Optional:** run `/update-maps-indexes` on cheaper agents to confirm the ledger and pointer repairs
   agree with what its own linter sees. It would have caught D3 on its own — the pointers had simply not
   been reconciled since the project folder was renamed.
