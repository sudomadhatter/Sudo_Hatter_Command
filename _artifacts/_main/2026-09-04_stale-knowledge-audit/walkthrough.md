# SCC-399 — the rule audit was auditing the published teaching edition as if it were a thin project

**Lane:** `chore/SCC-399-frontmatter-allowlist` · **Ticket:** SCC-399 (subtask of SCC-398) · **Date:** 2026-09-04
**Base:** `main` @ `0010b09b`
**Also closes:** SCC-397 (Bug — "main is red: sudo-command-center ships 28 unindexed rules and tier-1 copies")

## The consequence first

`main` was red at 72/73 for every lane in the workspace, and the one red file could not be fixed
without deleting 27 files out of a shipped product. It is now 73/73, and the check that was failing
is stronger than it was, not weaker.

## The defect

`test_rule_frontmatter.py` walked **every** directory under `Projects/` that carried an `.agents/`
folder, skipping exactly one hardcoded name:

```python
for p in sorted(projects_dir.iterdir()):
    if not p.is_dir() or p.name == "Fresh_Workspace_BMAD":
        continue
```

Ten of those directories are git submodules. The lobby drives **two** of them. The one the walk
hurt was `Projects/sudo-command-center` — the **published teaching edition of this lobby**, the
artifact `export-teaching-edition.ps1` builds from the `claude/teaching-edition` branch and pushes
to GitHub for other people to read. It ships 28 rule files, sanitized, **on purpose**.

Three assertions fired on it:

| Assertion | What it said | What was actually true |
|---|---|---|
| every project rule has a Load row | 28 rules unrouted | the teaching edition's INDEX is a teaching document, not a loader manifest |
| ⛔ no project carries a tier-1 lobby rule | 27 forbidden copies | shipping the lobby's rules **is the product** |
| no project has zero rule rows | 28 on disk, 0 indexed | same |

## Why the obvious fixes were both wrong

SCC-397 raised this on 2026-09-04 and named two readings — *(a) the export is wrong*, or *(b) the
INDEX is stale* — and judged (a) the likelier because `project-law.md` forbids tier-1 copies.

Both would have damaged the product. (a) means stripping the constitution, `jira.md` and
`operator-profile.md` out of a teaching edition whose entire purpose is to show someone what a
command centre's rules look like. (b) means generating loader rows into a document nothing loads.
The tier-1 rule they were being measured against **does not apply**: `project-law.md` governs *thin
projects the lobby drives*, and a published mirror is not one.

The third reading is the right one, and it was already written down. `.agents/maintained-projects.txt`
answers "which projects does this lobby drive" — its own header has said
*"Never hand-loop over `Projects/*` — that touches repos we deliberately do not keep current"*
since 2026-08-07, and `check_maps.fan_out_targets` already obeys it. **This was the one fan-out
that did not.**

## The fix

`.agents/scripts/tests/test_rule_frontmatter.py` · `.agents/maintained-projects.txt`

1. **The scan reads the allowlist.** `check_maps.maintained_projects()` — the same parser
   `check_maps` and `test_memory_store` already use, not a fifth copy. The hardcoded
   `Fresh_Workspace_BMAD` skip is gone; the allowlist already excludes it.
2. **A missing allowlist file is a LOUD failure**, never a fall back to walking every folder. That
   fallback would silently restore the old behaviour in the one situation nobody is looking.
3. **The scan is extracted** to `_scan_project_rules(projects_dir, allowed, tier1_stems)`, a pure
   function.

## Three things that make the narrowing honest

A narrowing looks exactly like a disarming. Each of these exists to tell them apart.

**`[COVERAGE]`, because all four assertions are satisfied by scanning nothing.** `Projects/*` are
submodule gitlinks — empty in a fresh clone, empty in every `git worktree`, and not checked out by
the `main-write-gate` CI job at all. "0 findings" and "0 projects looked at" printed identically, so
the tier-1 check had been **passing vacuously in CI for its whole life** (a gap SCC-396's walkthrough
had already spotted and left open). The run now prints which rule sets it audited, and a `[SKIP]`
row naming any maintained project it could not, with the reason.

```
[COVERAGE] project rule sets audited: AGY_AVIATIONCHAT, NEXgen-VR-Director
```

**A fixture control, because the real tree cannot prove the rule.** Two temp projects, identical
down to the file, differing only in whether they are on the allowlist. The listed one must still
fire all four findings; the unlisted one must fire none. That is what makes excluding
`sudo-command-center` a stated rule rather than an accident that happens to be quiet today.

**A mutation, run and recorded.** Restoring the old walk-everything loop:

```
-- 22/27 passed --
FAILED: ...unrouted..., ...tier-1 copies..., ...zero rule rows...,
        control: a project ON the allowlist still fires all four findings,
        ⛔ control: an identical project OFF the allowlist fires NOTHING and is not scanned
[COVERAGE] project rule sets audited: AGY_AVIATIONCHAT, B-L-WorldWide, BRKN_Tattoos,
           NEXgen-VR-Director, RAG_Pipeline_AC, sudo-command-center, sudo-project-skeleton
```

Both controls die, all three original failures return, and the coverage line names the five repos
that were being audited by mistake. The file was restored byte-for-byte afterwards.

## Evidence

| Gate | Before | After |
|---|---|---|
| `test_rule_frontmatter.py` | 20/23 | **27/27** |
| `run_all.py` | 72/73 files | **73/73 files** |
| SCC-397 acceptance, verbatim | red | exit 0 |

⚠️ SCC-397's acceptance names `test_rule_frontmatter.py --on-main`. **That flag does not exist** —
the file ignores `argv`. It exits 0 either way, so the row is met, but the flag was never real and
nothing should be written against it.

## What this does NOT do

- It does not touch the teaching edition, its export script, or its manifest. Whether that export
  should ship an `INDEX.md` with loader rows is a `claude/teaching-edition` question (SCC-280), and
  nothing is red while it stays unanswered.
- It does not remove `Fresh_Workspace_BMAD` from git. That is a submodule gitlink and takes four
  steps — SCC-403.
- It does not change what `maintained-projects.txt` contains. Two names in, two names out.

## Your Actions

- [ ] **Merge the PR** when checks are green. This lane does not merge.
- [ ] **SCC-397 can close with this merge.** Both its acceptance rows are met, by a third reading it
      did not list. It is typed `Bug`, so it clears through `jira_feed.py devrecord --closing` at
      close-out rather than by hand.
