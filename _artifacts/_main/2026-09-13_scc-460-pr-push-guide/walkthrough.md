# SCC-460 — A user's guide to the PR push system

**Lane:** `chore/SCC-460-pr-push-guide`, cut from `origin/main` @ `0070d8d3`.
**Lane type:** quick lane. Plan approved, scope override given, no self-audit, no code review.

---

## What shipped

One page — [`docs/_scc_sops_prds/pr_push_system_guide.md`](../../../docs/_scc_sops_prds/pr_push_system_guide.md)
— plus its INDEX row and the one manifest string the folder's contract requires.

**The gap it closes.** Every rule in the PR push system was already written down, and none of them
were written down *together*. `lane_qualify.py` holds the lane decision and explains itself to an
agent reading its docstring. Ten git hooks hold the refusals, each with a header explaining the
incident that produced it. `main_write_gate.py` holds the server half. `ceremony_tier()` holds the
blast radius. Every one of those is an excellent explanation aimed at whoever opens that file next —
and the operator, who types the commands, opens none of them.

So the page is organised around what an operator actually does, in order: *which door do I type* →
*what will refuse me* → *how do I override it when it is wrong*.

### The nine sections

| § | What it answers |
|---|---|
| 1 | Which `/` command — the `lane_qualify.py` decision as a flowchart, its six verdicts, and the two traps (silence is not smallness; a self-contradiction is never read permissively) |
| 2 | The two toggles — the lane you call vs. the epic you are on, and that they never depend on each other |
| 3 | What refuses you and where it lives — all ten hooks in the order they run, the three preflights, the server gate |
| 4 | The road to `main` — the permission table, and why the click is a stronger constraint than a sentence in a file |
| 5 | Blast radius — `code-review-graph`, the reach score, `ceremony_tier`'s four design properties |
| 6 | Overrides — every escape hatch in one table with what each one costs |
| 7 | One worked example — a docs change, every command pasted |
| 8 | Three refusals people try to route around, and why each is right |

Six diagrams, all `flowchart TD` or `LR`. Zero `sequenceDiagram` — `mermaid-diagram-preferences`.

### Four things the guide says that are easy to get wrong

These are the places where the honest answer is not the intuitive one, and each is stated in the
page with the measurement behind it:

**`main-write-gate` is not a port of the local hook.** The local token enforces *authorisation* and
by design never leaves the machine; the server check enforces *fitness*. They guard different
ground and neither covers the other's. The page says so in a two-row table rather than letting a
reader assume the server "took over".

**There is no *who* to restrict on GitHub.** The agent merges as the operator — same identity, not a
bot account — so no identity rule can separate them. A required status check was the only
server-side discriminator left. This is the reason the whole gate is shaped the way it is, and it
had never been said on an operator-facing page.

**The cap of 10 on reach was measured, not chosen.** The page carries the distribution table for
both repos, because "10" with no provenance reads as arbitrary and invites someone to change it.

**A hook can be silently OFF five different ways**, and `core.hooksPath` is local config git never
carries in a clone. A fresh clone has every gate switched off and says nothing. The page names
`hooks_armed.py` as the thing to run before trusting any green.

## Gates

```
run_all.py                            94/95   (this workstation)
run_all.py  GITHUB_ACTIONS=true       95/95   (the runner's view - what CI sees)
workflow_lint.py --toolkit-only       0 errors, 0 warnings, 8 info
check_maps.py --depth3-only --strict  clean (no output)
test_sops_prds_folder.py              60/61 - T1, T2, T3, T4, T10 all PASS
sequenceDiagram count                 0    (6 mermaid blocks, all flowchart)
```

⭐ **The one workstation red is `test_sops_prds_folder.py` T9, and it is not this lane's.** Its two
findings are `workflows_testing_SOP.md` and its changelog referencing `.agents/workflows/` — a
surface SCC-394 retired — inside accurate *historical* narration. Byte-identical in the clean lobby,
and inconclusive on a runner by `t9_inconclusive`'s ruling, which is why the runner column is 95/95.
Nothing was rewritten to silence it.

**Two reds during the build, both real, both caught by a gate rather than by reading:**

1. `check_maps.py` F2 — the lane's own `_artifacts/` folder had no row in `_artifacts/_main/INDEX.md`.
   Added.
2. `test_command_surfaces.py` CS-26 J — `Projects/sudo-project-skeleton` was uninitialised in this
   worktree, because **a worktree never inherits its parent's submodule checkouts**. The check named
   its own remedy and, on this machine, that remedy is actionable — so it is a real red, not an
   environmental one. `git submodule update --init Projects/sudo-project-skeleton` cleared it. This
   is the check SCC-459 built, working exactly as designed one day later.

**No `Verdict:` stamp**, and none is invented. No `/smh-code-review` ran on this lane, so there is
no review record to cite; a stamp would pull in the roster gate for lenses that never launched. The
quick lane's record line instead:

Review: none - quick lane; walkthrough approved by the operator @ e7faa2215b4167f924380efbd4377d3ab393e7e5

## Decisions

**No RED/GREEN staging.** An earlier draft withheld the `EXPECTED` manifest row to stage a
deliberate red. Operator correction, verbatim: *"You are writing a guide, there is no RED/GREEN."*
Correct — there is no behaviour to assert on a document, and a red that proves a manifest is a
manifest is theatre. The three edits landed together and the suite ran once. What the suite checks
about the page *unprompted* is the real protection: T2/T3 resolve every link, T4 resolves every
`/command` to a real master, `check_maps` resolves every backticked path in a table row.

**The guide lives in `docs/_scc_sops_prds/` precisely because that folder has a gate.** Loose in
`docs/` it would rot silently. Here, a renamed command or a moved script turns the suite red. That
gate is also what made this a three-file commit rather than one, and the cost is worth naming: the
folder's manifest is *"a contract, not an inventory"*, so a new doc is a conscious edit in three
places or the PR cannot merge.

**The scope stop was honoured, not reasoned past.** `scope_check.py` returned `OVERLAP` on
`test_sops_prds_folder.py` — a gate test is a critical surface. The quick lane is not for those
surfaces, so the lane stopped and asked. The operator's word is recorded verbatim in the plan
(`"Approved"`, then `"Yes both approved"`). No agent override exists and none was manufactured.

## Your Actions

1. **Nine dead branches are yours to delete.** The branch-delete guard refuses bare names by design
   — only `chore/`, `claude/`, `epic/` — and these are review-lens scratch branches from SCC-441 and
   SCC-447, all **0 commits ahead of `origin/main`**:

   ```
   git branch -d worktree-agent-a070c52f4e3277d56 worktree-agent-a0969d2636c00e2c4 \
     worktree-agent-a33b26aa304ac08ed worktree-agent-a4b4a4fe780509304 \
     worktree-agent-a62ee26c2c510809b worktree-agent-a634a20752bdb4c8a \
     worktree-agent-a636af52d3860745e worktree-agent-a86a39192c1850a39 \
     worktree-agent-aff4d76ed7e987b69
   ```

2. **`chore/SCC-431-zoo-remote` carries 2 unlanded commits.** Land it or let it go — it is the only
   branch in this checkout holding work that is not on `main`.

3. **Five submodule gitlinks in the lobby are behind their checkouts** — `AGY_AVIATIONCHAT` by 464
   commits, `NEXGen-Films` by 20, `B-L-WorldWide` by 11, `NEXgen-VR-Director` by 9, `BRKN_Tattoos` by
   1. `ignore = all` in `.gitmodules` means this never appears in `git status`, which is how it
   accumulated. It does not block a machine switch — a fresh clone takes the recorded pointers — but
   the lobby is describing project states that are months old. Bumping them is a decision about what
   the lobby records, not cleanup, so it is yours.
