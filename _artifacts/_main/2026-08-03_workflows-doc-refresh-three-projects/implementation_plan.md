---
IsArtifact: true
ArtifactMetadata:
  title: Rebuild sudo_workflows_testing.md across lobby + AGY + Fresh (mermaid-led)
  type: implementation_plan
  date: 2026-08-03
---

# Plan — `sudo_workflows_testing.md` × 3, mermaid-led

Ad-hoc infra: `main_debug` in each repo, no worktree, no story key, explicit paths only.

## What's actually stale

Five waves of workflow upgrade landed today **after** the AGY doc was last written (20:58), plus my
boot/resume fix. The lobby's copy predates all of it by ten days.

| Doc | Age | State |
|---|---|---|
| [lobby](../../_my_resources/_quick_reference/sudo_workflows_testing.md) | **2026-07-24**, 19,573 B | The ancestor. Pre-08-02 restructure, still carries the §6.1–6.6 curriculum that duplicates the lobby's own `tea_deep_reference.md`. 1 diagram. |
| [AGY](../../Projects/AGY_AVIATIONCHAT/_my_resources/_quick_reference/sudo_workflows_testing.md) | today 20:58, 20,582 B | Structurally current, but written **before Waves 3/4/5**. 1 diagram. |
| [Fresh](../../Projects/Fresh_Workspace_BMAD/_my_resources/_quick_reference/) | — | Folder exists, holds only a `sprint_scrum_board_map.md` stub. **No workflows doc at all.** |

**Missing from every copy** (all landed 21:49–23:36 today):

1. **The six workflow-enforcement scripts** — `wf_common` · `workflow_lint` · `story_status` ·
   `gate_receipt` · `closeout_preflight` · `split_sprint_status`. They are now *wired into* the commands:
   ③ runs every gate through `gate_receipt.py run`, close-out runs `closeout_preflight.py` and flips via
   `story_status.py set`, `/sudo-close-workingtree` pre-flights. None of this is documented anywhere a
   human reads.
2. **The Wave 4 sprint-status split** — AGY's board went **363,334 → 62,040 B**. Row narrative moved to
   `_bmad-output/history/<epic>/<key>.md` + `CHANGELOG.md`; the board now carries bare `key: status` plus
   a **≤120-char note on live rows only** (a note on a terminal row is a `workflow_lint` ERROR). §9 of the
   current doc still describes the old single-file board.
3. **The Wave 5 pre-commit encoding gate** — `workflow_lint.py --staged [--fix]`, installed by
   `git-hooks/install-encoding-hook.ps1`, resolving **`core.hooksPath`** (3 of 4 repos set `.githooks`,
   so `.git/hooks` installs a file git never reads), `scripts/git-hooks/DISABLE` kill switch, and the
   `wf-lint: allow-encoding-literals` opt-out for files that legitimately carry those bytes.
4. **`/sudo-resume`'s new hard gate** — on a fresh machine HEAD is `main`, so `git pull --ff-only origin
   main_debug` from there fast-forwards **`main` itself**: a silent unreviewed promote of every unshipped
   commit (AGY carries 160+). This is the most dangerous thing added today and appears in no reference doc.
5. **`/sudo-boot-sprint-memory`'s verdict resolution** — today's fix; the doc still describes boot as
   just "tells you the next story."
6. `gate_receipt.py` has **no `--result` flag by design** — it executes the gate and writes the receipt
   from the real exit code, and staleness compares **trees, not SHAs** (a merge commit with identical
   content is not stale). Both are the kind of thing that gets "helpfully" broken later.
7. Test suite is now **94 cases across 5 files** (`python .agents/scripts/tests/run_all.py`).

## Voice — who this is written for

**Audience of one: Sudo Hatter.** Big-picture operator, not a hardcore dev. He holds the whole system in
his head and makes the calls; he does *not* hold flag syntax, git plumbing, or test-tier jargon. The doc
must respect both halves of that — never dumb down the *system*, always explain the *machinery*.

Concretely, binding on every section:

- **Consequence before mechanism.** Lead with what it means for him, then how it works. Not *"`--ff-only`
  fails on divergence"* but *"this refuses to merge anything it can't do cleanly — if it errors, someone
  else's work is sitting there and you'd be papering over it."*
- **Every technical term earns its keep on first use** — SHA, worktree, fast-forward, ATDD, red test,
  emulator, receipt. One clause, inline, no glossary to bounce to.
- **Stakes in outcome terms.** The `/sudo-resume` hazard is not "HEAD defaults to main" — it is *"one
  wrong pull ships 160 unreviewed commits to your live users, and git reports success."*
- **Diagrams carry the structure, prose carries the why.** He reads shape first; that is why this is
  mermaid-led. Every diagram gets a one-line "what you're looking at" above it.
- **No unexplained flag soup.** A command in a table is followed by what it does *for him*, not its
  signature. Full invocations live in §5 where they're being explained, not scattered as decoration.
- **Keep every hard rule and number exactly as they are.** Plain language is the delivery, never a
  softening — a wrong number is worse than a hard one.

## Structure — one body, three copies

The current AGY doc's shape is good and stays. The only per-project variation is a **6-line
"In this workspace" block** directly under the header; everything below it is byte-identical across all
three. That is the whole anti-drift mechanism, and verification #4 enforces it mechanically.

Sections: `## Start here` (situational lookup + index) · 1 map · 2 the two rules · 3 commands by lane ·
4 the loop · **5 the enforcement layer (NEW)** · 6 shipping · 7 machine handoff · 8 how we test ·
9 TEA tools · 10 autopilot · 11 the board · 12 incidents · 13 depth.

## Diagrams — the ask is "mermaid-led", so 8, not 1

Per [mermaid-diagram-standards](../../.claude/skills/mermaid-diagram-standards/SKILL.md): **no
`sequenceDiagram`**, no unescaped `&` (write "and"), no `A --> B & C` multi-edge, every complex label and
subgraph title double-quoted, `\n` for line breaks, never `<br/>`.

| # | § | Diagram | Why it earns its place |
|---|---|---|---|
| 1 | 1 | The whole system | keep (refresh edges for the new commands) |
| 2 | 4 | ①②③ loop with **what each stage writes** | the artifact contract is invisible in prose |
| 3 | 5 | **Enforcement layer** — which script fires inside which command | entirely new; the point of Wave 1–5 |
| 4 | 5 | **Verdict resolution decision tree** — verdict → SHA vs HEAD → next command | today's fix; a decision tree beats three paragraphs |
| 5 | 6 | Shipping A/B/C + the branch model | the e2e gate is conditional; branching reads badly as a table |
| 6 | 7 | **park → resume**, with the `main`-promote hazard on the failure edge | the new hard gate |
| 7 | 10 | Autopilot 4 stages + resume-by-section | shows why it's resumable |
| 8 | 12 | Incident response, 3 layers | keep |

## Workstreams

- **WS-1 — write the canonical body** (lobby copy first; it is the master).
- **WS-2 — AGY copy** = canonical body + AGY's "In this workspace" block (its `sudo_artifacts_and_gates.md`
  and `sprint_scrum_board_map.md` siblings, the 278 s suite, Cloud Run/Sentry pointers). AGY's
  **`sudo_artifacts_and_gates.md` also needs §6 refreshed** for the Wave 4 board split and the receipt
  contract — it is the contracts doc and would otherwise contradict the how-to.
- **WS-3 — Fresh copy** = canonical body + a Fresh block saying it is the template and has no live sprint.
  Lands in the existing `_my_resources/_quick_reference/`.
- **WS-4 — register + land.** Add the doc to Fresh's `_my_resources/AGENTS.md` standing-exception list
  (AGY already lists it). Commit + push all three repos, explicit paths.

## Not in scope — decided, not skipped

- **No `/sync-agents` involvement.** These are `_my_resources/` docs; the sync covers `.agents/` only.
  Three hand-maintained copies is the cost of the ask, which is why the body is identical by construction.
- **The lobby's `diagrams_guides/INDEX.md:13`** still points at a `workflows_tea_testing/sudo_workflows_testing.md`
  that does not exist. `/update-maps-indexes` owns that; flagging, not fixing.
- **No size gate.** Per [artifact-budgets-are-scoped], the 8/10 KB caps bind story artifacts, not
  reference docs. I will report the final sizes rather than compress against an invented target.

## Verification

| # | Check | How |
|---|---|---|
| 1 | Every `/command` named resolves to a real file in `.agents/commands/` | scripted |
| 2 | Every markdown link resolves **from its own directory** (paths differ per project) | scripted, per copy |
| 3 | All 8 mermaid blocks parse and obey the standards (no `sequenceDiagram`, no bare `&`, quoted labels) | scripted lint + eyeball |
| 4 | The three copies are byte-identical **below** the "In this workspace" block | `diff` on the tail |
| 5 | All 7 new facts present in each copy (scripts, split, hook gate, resume gate, boot verdict, receipt design, 94 tests) | grep per fact |
| 6 | **Voice**: every diagram has a one-line "what you're looking at"; no jargon term appears before its inline explanation; every hazard states its outcome | read-through pass against the Voice list |
| 7 | Three repos commit + push clean, `0 0` vs origin | `git status` + `rev-list` |

No code changes → no test suite in scope.

## Risk

Low, with one real hazard: **three hand-maintained copies drift.** Mitigated by making the bodies
identical by construction and checking it (verification #4) rather than trusting it.
