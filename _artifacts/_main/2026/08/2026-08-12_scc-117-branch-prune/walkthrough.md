# Walkthrough — SCC-117 prune git branches (2026-08-12)

**Ticket:** SCC-117 (Task) · **Branch:** `chore/SCC-117-branch-prune`
**Plan:** none — the plan is skippable on this lane; this walkthrough is the record.

## What shipped

Ref surgery on `origin`, not a code change. The remote went from **6 branches to 2**: four
`claude/*` branches deleted, three annotated `archive/*` tags pushed first so nothing was
destroyed. `origin/main` and `origin/chore/SCC-124-baseline-trial` (a sibling lane, live at the
time) are what remain.

⛔ **This task produced no source diff.** The commit on this lane carries only these artifacts. The
lane was opened *after* the ref work, because the work needed no branch — that is stated here rather
than smoothed over, since the preflight's `base` check exists precisely to stop a close-out with
nothing to merge.

## What was deleted, and the evidence for each

| Branch | Mobile? | Verdict |
|---|---|---|
| `claude/fit-repo-workflow-integration-xzvg6q` | yes | `merge-base --is-ancestor origin/<b> origin/main` → **true**. Fully merged; nothing to preserve. |
| `claude/port-aviationchat-updates-dxpryk` | yes | 1 commit, **578 behind**. Its `require-push-approval.py` is on `main` **+133 lines richer**, and SCC-77 shipped `.githooks/pre-push` as the real gate. |
| `claude/gitnexus-metadata-sync` | **no** | 1 commit, **551 behind**. Rewrites the generated GitNexus block *backwards*: symbols 1481 → 1244, and deletes two `pdg_query` doc lines. Merging it would have **regressed** `main`. |
| `claude/teaching-edition` | **no** | 15 commits, **~3,375 insertions**, none of it on `main` and nothing on `main` superseding it. Archived, not discarded. |

## ⭐ The finding that reshaped the task: `claude/` is a prefix, not an authorship claim

The ticket said *"remove all the branches created by Claude mobile"*, and all four candidates sat
under `claude/`. Two of them were not written by Claude mobile at all.

The discriminator is **committer identity**, not the branch name:

- `fit-repo-workflow-integration-xzvg6q` and `port-aviationchat-updates-dxpryk` — author **and**
  committer `Claude <noreply@anthropic.com>`, and both carry the sandbox's random name suffix.
- `gitnexus-metadata-sync` and `teaching-edition` — author and committer `sudomadhatter`,
  hand-named, no suffix.

`teaching-edition` is 15 operator-authored commits over two days: an export engine with an
unskippable leak scan, lobby + skeleton manifests, `/sudo-tour`, a training-mode rule and toggle,
`.env.example`, and a rule-provenance test. Deleting on the prefix alone would have destroyed it.
Checked and confirmed absent from `main`: `export-teaching-edition.ps1`, `training-mode.md`,
`sudo-tour.md`, `training.md`, `test_rule_provenance.py`, `.env.example`. The only `main` hit for
"teaching" is `2026-08-11_scc-90-sop-teaching-restructure/`, which restructures the SOP doc — a
different concern, not a successor.

## The ordering that made the deletions safe

Tags were created, pushed, and **verified on the remote before a single branch was deleted**, then
re-verified after:

```
git ls-remote --tags origin 'archive/*'    # peeled ^{} SHAs equal the branch tips exactly
archive/teaching-edition^{}          3cdb130bec7b4b93b4fb83590544530fcc9d12c8
archive/gitnexus-metadata-sync^{}    5b1ec085fde7a916c812c35bf89c9710a11062a5
archive/port-aviationchat-updates^{} a045cdb710a7405dd9cbfa2003b749c87c4cbbfe
```

Post-delete spot-check: `archive/teaching-edition^{commit}:.agents/scripts/export-teaching-edition.ps1`
and `archive/port-aviationchat-updates^{commit}:.agents/commands/merge_main_debug.md` both still
resolve. `fit-repo` got no tag and needs none — an ancestor of `main` is reachable forever.

Each tag's message carries the evidence for its own deletion, so the reason survives with the object
rather than only in this file.

**This repo had zero tags before today**, so `archive/<name>` is a new convention established here,
not an existing one followed. Flagged as such because it was a judgement call, not a precedent.

## Decisions

- **Tag-then-delete over leave-in-place** (operator's call, offered with three alternatives). Keeps
  the branch list honest while making the work permanently recoverable.
- **`gitnexus-metadata-sync` archived rather than landed.** It is strictly older than `main` on the
  only file it touches, so "merge it first" would be a regression dressed as thoroughness.
- **`INDEX.md` deliberately not touched.** The SCC-119 lane holds an **uncommitted 10-row INDEX
  reconcile** in the shared checkout; adding an eleventh row here would collide with their dirty
  tree at merge time. The row for this folder is owed, not forgotten — see below.

## Pitfalls

- **A branch prefix is not provenance.** `claude/*` held two operator branches. Read
  `%an/%cn` before treating any branch as machine-generated.
- **"Already on main" needs a per-branch answer.** It was true for both mobile branches, but only
  one was an actual ancestor; the other was true only in the sense that `main` had evolved past it.
  `merge-base --is-ancestor` and a content check answer different questions.
- **Diffing `main → branch` to ask "what does main lack" is misleading** when the branch is
  hundreds of commits behind — the output is dominated by `main`'s own additions shown as
  deletions. Targeted `cat-file -e` checks on the specific paths are what actually answered it.

## Still owed

1. **`claude/teaching-edition` land-or-kill.** ~3,375 lines now reachable only via
   `archive/teaching-edition`. No ticket yet.
2. **`merge_main_debug` orphan.** 31 lines mirrored across three command surfaces, never on `main`,
   and it predates the one-door-per-platform rule that retired `.claude/commands` — so it cannot be
   revived as written. Preserved in `archive/port-aviationchat-updates`.
3. **`_artifacts/_main/INDEX.md` row for this folder**, held back for the SCC-119 collision above.
