# SCC-62 — Trigger worktree isolation on CONCURRENCY, not on work type

**Ticket:** SCC-62 (Task) · **Lane:** `chore/SCC-62-worktree-on-concurrency` off `main`, in a worktree
**Date:** 2026-08-09 · **Status:** PLAN — awaiting operator approval, no files touched yet
**Unblocked:** SCC-61 merged (`eaec85d`), so all six target files are free.

---

## The problem in one paragraph

`worktree-per-story.md` decides who gets an isolated tree by asking **what kind of work this is** — a
sudo story lane gets one, ad-hoc work is explicitly forbidden one ("Ad-hoc non-story work NEVER opens a
worktree"). The real hazard is **who else is in the repo**. A chore lane beside a story lane collides
exactly as hard as two story lanes, and today it is the one told to sit in the shared checkout. The
rule's stated reason for the ban is *"an orphan tree that no close-out will ever prune"* — which is not
a principle, it's a workaround for a missing prune step in `close-task-merge-tree`.

**Evidence, twice in one day (2026-08-09):** SCC-61 exists because a close-out preflight resolved
another lane's branch and printed `VERDICT: clear to close out and merge` about it. SCC-58 then opened
onto a shared checkout standing on SCC-61's branch with 11 dirty files.

## Acceptance criteria

| # | AC |
|---|---|
| AC1 | A commit-producing lane opens a worktree **without** first classifying itself as story-vs-chore. The "unsure? you're not in a lane" fallthrough is gone. |
| AC2 | Base branch is unchanged: `claude/<KEY>-<slug>` off the **epic branch**, `chore/<KEY>-<slug>` off **main**. |
| AC3 | `close-task-merge-tree` prunes its own worktree, so a chore tree is never an orphan. |
| AC4 | Sibling detection is **mechanical** (command output), not "assume you are not alone." |
| AC5 | A lane is told, as a hard stop, not to touch/report/fix another lane's files. |
| AC6 | Gitignored assets are linked into a new tree by one command, so isolation costs seconds, not a setup project. |
| AC7 | `run_all` and `sop_currency` stay green; all command mirrors stay consistent. |

## Steps (each traced to an AC)

**S1 — `worktree-per-story.md`: flip the trigger.** (AC1, AC2, AC4, AC5)
Rewrite the `Trigger` section and the frontmatter `description`. New rule: *any lane that will produce
commits works in a worktree.* Keep the branch/base table intact (AC2) — this changes **who gets a tree**,
not **what they branch from**. Add the mechanical sibling check (AC4) and a `⛔ Your tree is your world`
hard stop (AC5) next to SCC-61's existing `⛔ cwd is not intent`. Exemptions stay explicit: read-only
sessions, and a single trivial edit the operator is watching.

**S2 — `close-task-merge-tree.md` Step 5: prune the tree, not just the branch.** (AC3)
Step 5 is "Prune the branch"; it becomes branch **+ worktree**, mirroring `/sudo-close-workingtree`
Step 8, including the Windows pruned-shell-dir workaround. This is the unblocker for S1 — land it first.

**S3 — `link-worktree-assets`: make isolation cheap.** (AC6)
New script under `.agents/scripts/`. Links a repo's gitignored runtime assets into a fresh tree:

| Asset | Mac | PC | Why |
|---|---|---|---|
| `node_modules/` | symlink | **junction** | directory; junction needs no admin on Windows |
| `auth_keys/` | symlink | junction | directory, read-only in practice |
| `.env` | symlink | **copy** | Windows file-symlinks need admin/Dev Mode — the reason today's rule says "copy" |

Carries two warnings in its own output: a symlinked `.env` is **shared state** across lanes (good for
rotation, one collision surface re-introduced), and shared `node_modules` is fine for dev but the E2E
tier keeps its own `npm ci`.

**S4 — Mirrors + SOP.** (AC7)
Republish `.agents/commands/` → `.opencode/commands/` (byte-identical) and `.agents/workflows/`.
Update `_my_resources/_quick_reference/sudo_workflows_testing.md` — the `sop_currency` gate rejects the
commit otherwise.

## Verification
- `run_all` exit 0 (bare, never piped — a pipe returns `tail`'s code).
- `sop_currency` exit 0.
- Mirrors byte-identical where they are meant to be.
- Behavioral check: open a chore lane, run `close-task-merge-tree`, confirm the tree is gone afterward.

## Explicitly out of scope
- Renaming `.claude/worktrees/` — measured and parked by operator ruling (~91 files, three repos, the
  load-bearing `claude/` branch prefix).
- Any change to story lanes' epic-branch base (AC2 guards this).

---

# Self-Audit (2026-08-09)

**Right-size: LIGHT-plus.** No code, no state machine, no contract. But it rewrites a **protocol-four
rule** that every lane binds and that is inlined into project `AGENTS.md` files, so Phase 1 and Phase 3
are warranted; Phase 2 is cheap here.

**Method note (honest scoping):** `list_repos` shows `Sudo_Hatter_Command` indexed at 18 files / 86
nodes and **stale** (`3424306`, now several commits behind `main` at `eb4df48`). Per the freshness guard
this repo's own SCC-58 fix just added, that index is a **lead, not authority** — and at 18 files it does
not cover `.agents/` markdown at all. Blast radius below is grep-derived, correctly. This is the guard
working as intended, not a gap.

**Phase 0 — AC ↔ step traceability.** All seven ACs map to a step; no step lacks an AC. Clean.

**Phase 1 — Blast radius.**

| Change | Readers that break if wrong | Verified |
|---|---|---|
| `worktree-per-story.md` Trigger | It is one of the **protocol four**. Its law is **inlined** into project `AGENTS.md` §8 WORKTREE GATE (skeleton, AGY) — those inline copies say "any story/dev work… opens its own worktree". Flipping the center rule without them **splits the law**. | ⚠️ **FINDING 1** |
| `close-task-merge-tree.md` Step 5 | File is **13,166 B**, over Antigravity's 12k cap; its workflow mirror is already a **1,171 B thin launcher**. Adding to it keeps it a launcher — a grep against the mirror returns 0 and **looks like a failed sync**. | ⚠️ **FINDING 2** |
| Sibling detection | `git worktree list` is **per-repo and machine-local**. It shows nothing about another *session* on the same branch, and nothing on a fresh machine. | ⚠️ **FINDING 3** |

**Phase 2 — Over-engineering gate.** One tripwire fires and is answered:
`link-worktree-assets` (S3) is new tooling. Justified by AC6 — without it "always isolate" imposes a
per-tree setup tax in AGY, which is exactly the excuse that keeps lanes in the shared checkout. It stays
a flat per-repo script; **no plugin/registry/config layer** for one behavior. If S3 slipped, S1/S2 still
deliver AC1–AC5 — so it is genuinely severable, not load-bearing complexity.

**Phase 3 — Pre-mortem.** *"It shipped and silently corrupted state — how?"*
A lane reads the **stale inlined §8** in a project `AGENTS.md`, follows the old story-only rule, works in
the shared checkout beside a lane that followed the new one, and both edit `sprint-status.yaml` — the #1
conflict surface. **Split law is the failure mode**, and it is Finding 1.

### Findings

| # | Where | Severity | Failure scenario | Disposition |
|---|---|---|---|---|
| 1 | project `AGENTS.md` §8 inline copies (AGY, skeleton) | **HIGH** | Center rule flipped, inline copies still say story-only ⇒ two lanes obey different laws in one repo. | **Add step S1b**: update every inlined §8 WORKTREE GATE in the same change. Note: skeleton is a **separate repo ⇒ its own commit** (ticket-per-repo). |
| 2 | `.agents/workflows/close-task-merge-tree.md` | MED | Mirror stays a thin launcher; a future grep reads as a broken sync. | **Accept + document** — state it in the walkthrough so it is not re-diagnosed. Do **not** byte-golf the body. |
| 3 | S1 sibling check | MED | `git worktree list` cannot see a second *session*, and sees nothing on a fresh machine. | **Soften the claim**: the check catches the common case (another tree/branch on this machine). Isolation must not *depend* on detection — which is why AC1 makes the worktree the default rather than the detected exception. |

**Audit verdict: GO** — with S1b added (Finding 1) before implementation.
