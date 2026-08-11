---
IsArtifact: true
ArtifactMetadata:
  title: SCC-90 — restructure the workflows SOP as a teaching document
  type: walkthrough
  date: 2026-08-11
---

# Walkthrough — SCC-90 / SCC-91

**Branch:** `chore/SCC-90-sop-teaching-restructure` (cut from `main` @ `50e357b`)
**Scope:** the SOP restructure **only** — see the scope cut below.

> ⚠ **This lane is RETROACTIVE and the record says so rather than pretending otherwise.**
> The rewrite was written on operator instruction during a session that ended at "stop before
> commit"; the ticket was minted afterwards. **No plan was written first, no `approved` gate ran, and
> no pre-work `/smh-self-audit` ran.** SCC-90's ACCEPTANCE block was authored after the fact and is
> what the evidence below audits against. A record that reads as though a gate ran in time when it
> did not is the failure this note exists to prevent.

## ⛔ The scope cut — the most useful thing in this document

This branch was briefly staged with **27 files**. Only 4 were its own.

**Cause:** the lane ran in the **shared checkout** on operator instruction, and a sibling lane
(`chore/SCC-89-migrations-to-docs`) had ~23 uncommitted files sitting in the same working tree. To
`git add`, they are indistinguishable from this lane's own work. That is precisely the SCC-58 /
SCC-61 failure the SOP documents in §7 — and it reproduced here, in the document *about* it, within
an hour of it being written.

**Caught by:** the operator, before the commit. Not by a gate. There is no gate for this; the only
mechanical defence is a worktree, which this lane did not have.

**Corrected by:** `git restore --staged .` then re-adding four explicit paths. `--staged` never
touches working-tree content, so the sibling lane's ~23 files are intact and still unstaged —
verified after the fact, not assumed.

**Second correction, same cause.** A sub-task (SCC-92) was minted for the migrations relocation
before discovering **SCC-89 already existed** and specified that work far better — measured blast
radius, an operator ruling on standing-vs-disposable, per-repo out-of-scope notes, and a three-way
secrets verification. SCC-92 was **deleted** and SCC-89 **linked** to SCC-90 instead. *A twin ticket
nothing will ever move again is worse than none.*

**Consequence for this commit:** SCC-89's blast-radius list already claims this file's two dead
migrations links as its own. So this branch **leaves both links on `_my_resources/migrations/`** —
the path that still resolves on `main` — and SCC-89 repoints them when it lands the move. This
commit therefore stands alone and cannot red `main` on its own, in either landing order.

## Task Checklist

- [x] **SCC-91** — restructure the SOP as a teaching document
  - Six parts replacing 13 flat sections; **two reading levels** — a spine anyone can read start to
    finish, plus skippable `ⓘ Why it works this way` asides holding the incident history, so the
    review surface survives without blocking a first read.
  - 8 diagrams → **23**. A new internals diagram for every command that *contains* another: ①, ②,
    ③, the four close-outs, `/cicd-push-e2e`, `/cicd-quick-dev`, `/smh-quick-dev`, `/smh-code-review`.
  - New §5 lane chooser and §7 close-out decision tree. The §7 tree is the reason the ticket exists:
    the page described the close-out family as four interchangeable commands when they are four
    **altitudes**, and `/cicd-close-workingtree` is not a close-out at all — it is a janitor both
    story close-outs call automatically.
  - **Nothing cut.** Every fact from the prior version survives; history relocated into asides.
- [x] ⛔ **Two defects found only by RENDERING, not by linting**
  - **mermaid parses `<KEY>` as an HTML tag even inside a quoted label.** Bare `<id>` / `<KEY>-<slug>`
    in new diagrams were rejected outright by the renderer. Escaped to `&lt;`/`&gt;` — the shape the
    original file had already solved in its shipping diagram. A house-style lint passed this; only
    rendering caught it.
  - **`①②③` in a heading breaks its own anchor** — GitHub strips the glyphs when slugifying. This
    would have shipped silently: pure-anchor links are invisible to `test_sops_prds_folder.py` T3,
    whose regex stops at `#`.

## Evidence

Measured in a **clean worktree** on this branch — not in the shared checkout, whose sibling-lane
contamination would have made every number unreadable.

| Acceptance item (SCC-90) | Evidence |
|---|---|
| 1 — teaches a new reader | §1 four un-fakeable claims · §2 nine-word glossary · §5 lane chooser · §7 close-out tree · 23 diagrams |
| 2 — no fact lost | history relocated into `ⓘ` asides; +1294/−695 with no section dropped |
| 3 — every diagram renders | 23/23; two validated through the Mermaid renderer (`valid: true`), covering the `&lt;`-escape and `##`-in-label patterns |
| 4 — anchors + links resolve | scripted sweep: 19 anchor links vs 63 headings → 0 broken; 0 broken relative links |
| 5, 6 — migrations relocation | **not this lane** → SCC-89 |
| 7 — gates green | below |

### Gate results

Run **bare** (unpiped — a piped gate returns the pipe's exit code), in the clean worktree.

```
Measured in .claude/worktrees/scc-90-verify (detached at ba9aa91, clean tree,
only this commit on top of main).

python3 .agents/scripts/tests/run_all.py                -> exit 0   12/12 files passed
python3 .agents/scripts/workflow_lint.py --toolkit-only -> exit 0   0 errors, 0 warnings, 8 info
python3 .agents/scripts/tests/test_sops_prds_folder.py  -> exit 0   16/16 passed

content sweep, same tree:
  anchors     19 links vs 63 headings -> 0 broken
  file links  20 unique               -> 0 broken
  mermaid     23 blocks               -> 0 bare angle brackets in labels
  size        1632 lines, 108 KB

check_maps.py is NOT cited here on purpose: its AUTO-block staleness check labels
the tree by the CWD basename, so it reports a FALSE stale inside any worktree.
This commit touches no INDEX path and adds no folder, so it cannot move that gate;
it was green in the shared checkout before the scope cut and is unaffected.
```

**No `gate_receipt.py` on this lane, and that is a stated limit, not an oversight.** It resolves a
BMAD project root and exits in the command centre. The evidence contract here is pasted real output
plus the commit it was measured on. Any change after that commit voids this verdict.

## Your Actions

- **Read the diff, then run `/smh-close-task-merge-tree`** — typing it is the merge sign-off, and it
  authorises exactly this one merge.
- The branch stops here **pushed, gated and merge-ready**. It is deliberately not merged.
- **Landing order matters and is written up separately.** This branch is independent of SCC-89 in
  either direction, but SCC-89 expects to rebase onto it and fix the two links there.
- **Left untouched in the shared checkout:** SCC-89's ~23 files, `_artifacts/_memory/` (another
  session), and the Antigravity guide + its artifacts folder (SCC-93, which lands inside the folder
  SCC-89 creates).
- **The shared checkout was returned to `chore/SCC-89-migrations-to-docs`** after this commit, which
  is where the sibling lane expects to find it.
