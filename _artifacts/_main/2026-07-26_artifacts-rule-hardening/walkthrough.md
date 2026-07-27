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
