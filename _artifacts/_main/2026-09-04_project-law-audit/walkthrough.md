# Project & seed law audit — 2026-09-04

Ticket: [SCC-388](https://sudo-command.atlassian.net/browse/SCC-388) · Branch: `chore/SCC-388-project-law-audit` · Date: 2026-09-04

## Task Checklist

- [x] Project and seed law audit completed across Tier 1 and Tier 2 repositories
- [x] Minted Jira subtasks: SCC-389 (seed thin-conversion), SCC-390 (projects thin-conversion), SCC-391 (rule frontmatter gate)
- [x] The merge itself — lands via this branch's PR

Raised during `/cicd-code-review AVCH-119`, when the operator asked whether the rule set was "set up
correctly". Read-only measurement across tier 1 (the lobby) and tier 2 (every project under
`Projects/`). No project files were changed by this audit; the AviationChat fixes it produced ride
the AVCH-119 review lane.

## What was measured, and with what

The lobby's own gate (`.agents/scripts/tests/test_rule_frontmatter.py --on-main`) for tier 1, and the
same contract re-applied to each project's `.agents/rules/` + `.agents/INDEX.md`. Two of this audit's
own first-pass results were **false positives and are recorded as such** — a path normaliser that
stripped the leading dot off `.agents/` reported 14 non-existent citations, and a link checker that
matched `[label](relative/path)` written inside backticks as an *example* reported 2 dangling links.
Corrected, tier 1 has **zero** of either.

## Tier 1 — the command center's 27 rules: healthy

- `test_rule_frontmatter.py --on-main` → **18/18 passed**.
- Every `.agents/scripts/`, `.agents/hooks/` and `.agents/rules/` path cited by a rule **exists**.
- No dangling relative link in any master or in the generated `.claude/rules/` mirrors.
- **One real defect.** `AGENTS.md` §3 states the four protocol rules are "Together ~44 KB — which is
  why they are conditional rather than floor." Measured: **94.4 KB** (`git-policy` 34.2 · 
  `artifacts-always-first` 31.4 · `worktree-per-story` 18.6 · `000-PLAN-FIRST-GATE` 10.2). The figure
  is 2.1× understated and it is load-bearing — it is the stated justification for the load class.
  Floor is 17.1 KB and correct.

## Tier 2 — what actually routes a project rule

There is no automatic loading of project rules. `.agents/hooks/rule-trigger.py` resolves
`.agents/rules/` from the **session root** (the lobby), so it never scans a project's rules; projects
carry no generated `.claude/rules/` mirror. The **only** path by which tier-2 law reaches an agent is
`project-law.md` §"Binding a project MEANS loading its law" — read `PROJECT_ROOT/.agents/INDEX.md`
and honour its `Load` column. **The INDEX is the whole mechanism.** A project rule's frontmatter is
close to decorative.

| Project | Rule files on disk | Rows in its INDEX | Copies of lobby tier-1 |
|---|---|---|---|
| `sudo-command-center` (seed) | 26 | **0** | 24 |
| `BRKN_Tattoos` | 25 | **0** | 15 |
| `B-L-WorldWide` | 17 | **0** | 15 |
| `AGY_AVIATIONCHAT` | 8 | 8 | 0 |
| `NEXgen-VR-Director` | 3 | 3 | 0 |
| `RAG_Pipeline_AC` | 2 | 2 | 0 |
| `sudo-project-skeleton` | 0 | 1 (intentional — "Create this first") | 0 |

⛔ **A present-but-empty INDEX is invisible to every existing check.** `project-law` STOPs on a
*missing* INDEX and `check_maps.py` lints for one; both pass on an INDEX that routes nothing. An
agent binding those three projects follows the rule correctly, opens the INDEX, and loads no law.

`Fresh_Workspace_BMAD` is **retired** (operator, 2026-09-04) and is excluded.

## The seed is the one that reproduces itself

`sudo-command-center` is the clone source for new projects. Of the 24 shared rules it seeds, **3 are
current and 21 have drifted**:

| Rule | In the seed | Live |
|---|---|---|
| `jira.md` | 4.1 KB | **48.6 KB** |
| `operator-profile.md` | 1.9 KB | **7.7 KB** |
| `git-policy.md` | 31.6 KB | 35.0 KB |
| `000-PLAN-FIRST-GATE.md` | 9.3 KB | 10.5 KB |
| `karpathy-guidelines.md` | 3.8 KB | 4.7 KB |
| `code-standards.md` | 11.5 KB | 12.1 KB |

It also ships two rules that no longer exist live (`prose-formatting.md`, retired into the operator
profile under SCC-333; `training-mode.md`) and is **missing two that do** (`command-shape.md`,
`zoo-team.md`).

**Severity is bounded by the empty INDEX**, and that is worth stating plainly rather than
overselling: because the seed routes zero rules, a cloned project loads none of them and falls back
to the lobby's live tier-1. The drift is **dormant, not active** — dead weight a future agent may
read directly (a grep finds them), not law currently being applied. That is exactly the
"dead weight that drifts" `project-law.md` forbids.

`sudo-project-skeleton` is **correct as-is** and needs no work: its `rules/` holds only `.gitkeep`,
and its INDEX row for `constitution.project.md` marked "**Create this first**" is template guidance,
not a dangling pointer.

## Related

`SCC-379` (To Do Next) already targets the same shells to propagate the SCC-376 fence shape, and
names a third shell — `teaching-edition` — that does not exist under `Projects/`. Whoever takes
either ticket should check that shell too.

## Evidence

Read-only audit measurements; zero code or configuration changes made in this lane.

## Your Actions

No operator action required. This lane records the audit findings; implementation will proceed under follow-on subtasks SCC-389, SCC-390, and SCC-391.
