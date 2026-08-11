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
  - 9 diagrams → **23**. A new internals diagram for every command that *contains* another: ①, ②,
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
  size        1636 lines (at review-fix sha), 108 KB

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

## Code Review (2026-08-11)

Verdict: PASS @ 577239e
Suite evidence measured at 577239e (run bare in this worktree, after the review fixes).

**Scope:** the full `main...HEAD` diff — the SOP rewrite plus 3 artifact files.
**Method:** clean-room adversarial subagent (no conversation context) on the diff first, artifacts
after; scripted mermaid-conformance and link/anchor sweeps; five command masters spot-checked
line-by-line against the SOP's internals diagrams; machine gates bare.

**Layer degradation, recorded:** the first clean-room subagent died on a session-limit API error
before producing anything. Retried once per the subagent-failure contract; the retry ran end to end
— all layers ran, no coverage lost.

### Findings (the only copy — the plan links here)

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| R1 | SOP :724 vs :783 | MED | §7 restated the command's push-approval-prompt claim as fact; the SOP's own aside proves no pre-push hook exists → an operator waits for a prompt that never fires | **applied** — §7 now says no prompt fires until SCC-77 lands the hook |
| R2 | SOP :1080 | MED | "202 checks across 7 files" — measured reality 408/12; a reader audits gate coverage at half its size | **applied** — corrected, dated, and subordinated to the suite's live output |
| R3 | SOP :678 | LOW | janitor diagram's Step 5 gate referenced "Step 1.7" with no such node — dangling for a diagram-only reader | **applied** — gate label now self-describing |
| R4 | SOP :553 | LOW | `ME --> E2E` drawn unconditional; the command runs e2e only when promoting | **applied** — edge now dotted + labeled |
| R5 | SOP :1018 | LOW | "two armed git hooks" undercounted the commit-time checks | **applied** — three hooks named with their checks |
| R6 | walkthrough :55/:101 | INFO | "8 diagrams" (main has 9) · "1632 lines" (1631 pre-fix) | **applied** — 9→23; 1636 at fix sha, measured |
| R7 | walkthrough :90 | LOW | evidence sha `ba9aa91` ≠ shipped `323cc32` (delta: walkthrough only — doc-only, so valid by the letter) | **superseded** — this section's evidence is at 577239e |

Bloat/duplication: none found. Unsupported walkthrough claims: none found (Jira-side claims
verified live where checkable). Both edited diagrams re-validated by the renderer: `valid: true`.

### Gates (bare, at 577239e)

| Gate | Result |
|---|---|
| `run_all.py` | **12/12 files passed**, exit 0 (per-file 26/26 · 13/13 · 21/21 · 103/103 · 39/39 · 46/46 · 26/26 · 16/16 · 19/19 · 14/14 · 48/48 · 37/37 = 408 checks) |
| `workflow_lint.py --toolkit-only` | **0 errors, 0 warnings**, 8 info (BOM notes), exit 0 |
| SOP currency | the SOP IS this diff; no usage surface staged without it — armed hook accepted every commit |
| Link + anchor | 20 relative links, 19 anchor links — 0 broken (scripted sweep + reviewer sweep) |
| Door parity | N/A — no command added, renamed or deleted |
| `check_maps.py` | deliberately NOT run here — AUTO-STALE is always false in a worktree (label = CWD basename); runs on `main` in the combined gate after landing |

### Acceptance matrix (parent SCC-90 ACCEPTANCE; items 5–6 are SCC-89's half)

| # | Item | Evidence |
|---|---|---|
| 1 | teaches a never-seen-it reader: lane chooser, close-out tree, internals diagram per containing command | §5 chooser · §7 decision tree + altitude table · internals diagrams for ①②③, all four close-outs, push-e2e, both quick-devs — reviewer spot-checked 5 masters line-by-line: faithful |
| 2 | no fact lost; incident history relocated to asides, never deleted | reviewer hunted the full diff for dropped facts: none found; two contradictions found were *pre-existing text carried over*, now fixed (R1, R2) |
| 3 | every mermaid diagram renders, validated | 23/23 conformant (scripted sweep); the 2 edited in review re-validated `valid: true` |
| 4 | every internal anchor + relative link resolves | 0 broken of 39 (sweep above) |
| 7 | run_all exit 0 · workflow_lint exit 0 · check_maps exit 0 | first two at 577239e above; check_maps owed on `main` post-merge (worktree false-STALE, see gates) |

### Step 0.7 re-derivation

Nothing moved on `main` under this diff (branch 0 behind at review time; merge-tree clean).
True overlap with live siblings: `_artifacts/_main/INDEX.md` — SCC-83/88/94 (and SCC-89 once it
commits its untracked artifact folder) each append one row at the table head; ledger law: keep all
rows, later-landing lane on top. Landing order: **SCC-90 lands FIRST** — SCC-94 and SCC-95 both
edit paragraphs of the file this lane rewrites and must re-place their edits against the new
structure at their own absorb step.

Changes applied: R1–R6 above, on this branch, before this verdict.
