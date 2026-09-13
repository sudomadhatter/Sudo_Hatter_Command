# SCC-460 — A user's guide to the PR push system

**Lane:** `chore/SCC-460-pr-push-guide` in `.claude/worktrees/SCC-460-guide`, cut from `origin/main` @ `0070d8d3`.
**Ticket:** SCC-460 *Diagram for PRs* — "I need a PRP user guide for the way we built the PR push
rules. include the hooks and the rules … make sure to explain how the different / command we have
work and how they trigger different things, how they are over ridden if they are wrong … Explain the
code graph and the blast radius."
**Lane type:** quick lane (`artifacts-always-first` § When to Skip names *"Writing a document or a
guide"* explicitly). Plan + the literal `approved`; no self-audit, no code review unless asked.

---

## Goal

One page an operator can open cold and answer four questions from:

1. **Which `/` command do I type for this change?** — and what decides that, mechanically.
2. **What refuses me, and where does the refusal come from?** — the five local git hooks, the
   server-side gate, and the preflights, each named with the file it lives in.
3. **How do I override a gate that is wrong?** — every kill switch and escape hatch in one table,
   with what each one costs.
4. **What are the code graph and the blast radius?** — the operator's own note: *"I forget the
   correct name."* The name is **reach score**, the thing that produces it is `code-review-graph`,
   and the tier it feeds is `ceremony_tier`.

Written for the operator, not for an agent: consequence first, mechanism second, one worked example
end to end. Mermaid throughout as `flowchart TD`/`LR` — **never** `sequenceDiagram`
(`mermaid-diagram-preferences`).

## Why this file cannot be a three-file-free drop

`test_sops_prds_folder.py` pins an **explicit manifest** of the docs in this folder — its own header
calls it *"a contract, not an inventory … a 14th doc must be a conscious edit here."* `EXPECTED` is
compared to the directory **both ways**, so a new doc with no `EXPECTED` row turns `run_all.py` red,
and `main-write-gate` runs `run_all.py`. The three edits below land in one commit or the PR cannot
merge. That is the manifest doing its job, not an obstacle to route around.

## ⛔ Scope check — OVERLAP, and the override it needs

```
python3 .agents/scripts/scope_check.py --repo <lobby> --paths \
    docs/_scc_sops_prds/pr_push_system_guide.md \
    docs/_scc_sops_prds/INDEX.md \
    .agents/scripts/tests/test_sops_prds_folder.py

OVERLAP
.agents/scripts/tests/test_sops_prds_folder.py  ci: the gates: … a gate test … changes what green
means for every lane in every repo
```

`test_sops_prds_folder.py` is a **gate test**, and gate tests are on the critical-surfaces list. The
quick lane is not for surfaces on that list, so this is a soft stop: it moves only on Mr. Hatter's
word, quoted here as `Scope override (2026-09-13): "…"`. No agent override exists.

**What the edit actually is:** one string added to a `set` literal, so the manifest names the file
this ticket creates. No assertion changes, no logic, no threshold. The contract is *designed* to
require this edit in the same commit.

**Scope override (2026-09-13):** "Approved" — then, on being told this was being read as covering
both the plan and the overlap: **"Yes both approved"**

Both given verbatim. The first came in reply to a message whose headline was this scope stop and
which stated exactly what the edit is (one filename added to a `set` literal); the second confirms
the override explicitly rather than by inference. The operator's word is the only thing that moves a
critical-surface overlap, and this is that word, twice, with the overlap in front of him.

## What proves it

⛔ **Operator correction (2026-09-13): *"You are writing a guide, there is no RED/GREEN."*** An
earlier draft of this section staged a deliberate red by withholding the `EXPECTED` row. That is
theatre on a document — there is no behaviour to assert and nothing to falsify, so the red proves
only that a manifest is a manifest. Dropped. The three edits land together and the suite is run once.

What the suite genuinely checks about this document, unprompted, is worth more than a staged red:

| check | what it catches in the guide |
|---|---|
| T1 / T6 manifest | the folder and `EXPECTED` agree in both directions |
| T2 / T3 | every markdown link in the guide resolves to a real file |
| T4 | every `/command` the guide names resolves to a real master under `.agents/commands/` |
| `check_maps.py` | every backticked multi-segment path in a table row is real |
| T10 | the whole page survives a Windows cp1252 console |

The guide names ~20 commands and links ~12 files. **That is the reason this doc belongs in this
folder rather than loose in `docs/`** — the folder comes with an accuracy gate, so a renamed command
or a moved script turns the suite red instead of quietly rotting the page.

## Declared Change Set

- NEW `docs/_scc_sops_prds/pr_push_system_guide.md` - the guide: the lane decision, every hook, the server gate, the override table, the code graph and reach score → A, B, C, D
- EDIT `docs/_scc_sops_prds/INDEX.md` - one row in the operator's-PRD table → A, C
- EDIT `.agents/scripts/tests/test_sops_prds_folder.py` - one string in `EXPECTED` → A, E, F
- EDIT `_artifacts/_main/INDEX.md` - the session row this lane's own artifacts need → E
- NEW `_artifacts/_main/2026-09-13_scc-460-pr-push-guide/` - plan, walkthrough, task.yaml → E

**Three files. No script behaviour changes, no gate thresholds move, no command body is touched.**
`ceremony_tier` returns `full` on this set (the gate test vetoes), which is why the scope override is
asked for rather than assumed.

## What the guide will contain (the outline being approved)

| § | Content | Diagram |
|---|---|---|
| 1 | **Start here** — the one-question decision: which door do I type? | `flowchart TD` from "I changed some files" to a named `/` command |
| 2 | **The five verdicts** — `lane_qualify.py`'s word, what each means, why silence means TASK | table |
| 3 | **The two toggles** — the lane you call vs the epic you are on (`epic_mode.py`: FULL/LIGHT/TRUNK) | `flowchart LR` |
| 4 | **What refuses you, and where it lives** — commit-msg (Jira key, SOP currency, merge target), pre-push (maps, merge backstop, main token), server-side `main-write-gate` | `flowchart TD` of a commit's journey through the gates |
| 5 | **The road to `main`** — PR, the gate, the operator's click, `--after-merge`; why there is no token on that road and why that is not a bypass | `flowchart LR` |
| 6 | **Blast radius** — `code-review-graph`, `reach_score`, `ceremony_tier`'s tiny/quick/full, the measured knee at 10, why entry points are excluded by name | `flowchart TD` |
| 7 | **Overrides — every one, and what it costs** | table: `[sop-ok]`, `--no-verify`, `DISABLE`, the `*-ENFORCE` markers, ruleset break-glass, scope override, `--accept-*` flags |
| 8 | **One worked example** — a docs change, start to merge, every command pasted | — |
| 9 | **When it refuses and it is right** — the three refusals people try to route around | — |

## Acceptance

| # | Statement | Check |
|---|---|---|
| A | The manifest contract is satisfied | `test_sops_prds_folder.py` seen RED without the `EXPECTED` row, GREEN with it |
| B | Every `/command` the guide names resolves to a real master | T4, in the same suite |
| C | Every markdown link resolves | T2/T3, same suite |
| D | No diagram is a `sequenceDiagram` | grep the file; `mermaid-diagram-preferences` |
| E | The floor holds | `python3 .agents/scripts/tests/run_all.py` at the lane tip |
| F | Nothing else moved | `declared_change_set.py parse`, 3 rows, 1 NEW |

## Your Actions

Three, and the first two are the gate:

1. **The literal `approved`** on this plan.
2. **The scope override** for `test_sops_prds_folder.py` — one sentence in your words, quoted into
   this file.
3. **Nine dead branches are yours to delete.** The branch-delete guard refuses bare names by design
   (only `chore/`, `claude/`, `epic/`), and these are review-lens scratch branches, all **0 commits
   ahead of `origin/main`**:

   ```
   git branch -d worktree-agent-a070c52f4e3277d56 worktree-agent-a0969d2636c00e2c4 \
     worktree-agent-a33b26aa304ac08ed worktree-agent-a4b4a4fe780509304 \
     worktree-agent-a62ee26c2c510809b worktree-agent-a634a20752bdb4c8a \
     worktree-agent-a636af52d3860745e worktree-agent-a86a39192c1850a39 \
     worktree-agent-aff4d76ed7e987b69
   ```
