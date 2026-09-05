---
IsArtifact: true
ArtifactMetadata:
  title: "SCC-416 — Decide the epic's mode at kickoff; freeze main for a live epic's scope"
  type: implementation_plan
  date: 2026-09-05
---

# Implementation Plan — SCC-416

**Ticket:** [SCC-416](https://sudo-command.atlassian.net/browse/SCC-416) · **Lane:** `chore/SCC-416-in-flight-epic-freezes-main` off `origin/main` @ `f0dcb423`, worktree `.claude/worktrees/scc-416-epic-freeze` · **Door:** `/smh-close-task-merge-tree`

**Operator design (2026-09-05):** *"When we branch the epic, that is when we decide if we are testing it like an extension of main, or a branch to quick-dev on and not waste money and time on E2E. We do both. Critical that this is set up at the beginning. Not the case for all epics — don't over-design the fix. Keep what is actually real to our development system, not extra noise."*

**Approval:** design confirmed by the operator ("Yes") 2026-09-05 with the trim instruction above; v3 is the trimmed plan. v1 (guard only) and v2 (guard + modes + five door nudges + a constitution clause) are in this lane's history.

---

## 1. The reproduction

AVCH-80 was cut as `chore/AVCH-80-rolling-bugs` **off `main`**; its riders were Epic 24 findings routed out of story 24.4. Its diff shared three runtime files with the live `epic/AVCH-100-epic-24-agent-quality` (`backend/agents/specialist/agent.py`, `backend/agents/admin/agent.py`, `backend/tools/librarian.py`). `ship_preflight` said *chore touching backend → light gate → clear to ship*; PR #72 merged at `4afaa667`; Cloud Run revision `00076-boh` took traffic mid-epic. The operator's 2026-09-03 ruling forbidding it sits in the Epic 24 banner of `sprint-status.yaml` **on the epic branch** — a main-bound lane never reads it. Neither preflight lists `origin/epic/*`; "deployable → product change" promotes epic work to prod.

**Second measured fact:** `cicd-close-story-merge-tree.md` Step 3 lands a story by `git push origin HEAD:epic/<KEY>-<slug>`. AVCH-119 (armed 2026-09-04) requires four checks on every push to `epic/**`, so that push is **refused on Epic 24 today** (story 24.3 already had to go by PR #63). The door and the ruleset disagree, and nothing records which epics should get which treatment.

## 2. The change

### 2.1 The decision at kickoff — `cicd-create-epic-sprint.md`, at the cut

One question, answered by the operator, never defaulted by an agent:

> **Is this epic an EXTENSION OF MAIN or a QUICK-DEV branch?**
> *extension of main* — every story lands by PR into the epic under the full four-check gate (E2E on every landing); the epic is kept current with `main`. *quick-dev* — stories land by direct push after the local light gate (suite + build); no CI per story; E2E once, at `/cicd-push-e2e`.

The answer is in the branch name and nowhere else — the one place GitHub's ruleset and every local door read without opening a file:

```text
epic/AVCH-100-epic-24-agent-quality          extension of main   (the existing shape)
epic/AVCH-131-epic-25-tool-menu-quickdev     quick-dev           (the -quickdev suffix is the switch)
```

`epic/` prefix unchanged, so the existing `epic/*` globs keep working. Server side (AviationChat, one-time, after recovery): the AVCH-119 ruleset gains `exclude: refs/heads/epic/*-quickdev`. `pr-check.yml` is untouched — a quick-dev epic lands by push, and pushes fire no CI here.

### 2.2 The story door reads the mode — `cicd-close-story-merge-tree.md` Step 3

The one landing line becomes a two-arm `case` on the epic branch name already in hand:

- `*-quickdev` → **unchanged:** `git push origin HEAD:epic/<KEY>-<slug>` after the merge gate.
- otherwise → push the story branch, `gh pr create --base epic/<KEY>-<slug> --head claude/<KEY>-<slug>`, `gh pr checks --watch`, then `gh pr merge --merge` (the door's invocation is the sign-off; the ruleset's bypass list governs rules, not who merges a green PR). Red → STOP and report, as the door already says for a conflict.

This is what makes Epic 24's landings work again and quick-dev epics cheap. One `case`, two arms, no new script. The "do not push `claude/*` to origin" rule gets its one exception spelled out: the extension-of-main arm pushes it because a PR needs a head; Step 5 prunes it.

### 2.3 The floor — the overlap guard, both preflights, both modes

One shared function in `task_preflight.py`:

```python
EPIC_REF_RE = re.compile(r"^refs/(?:heads|remotes/origin)/(epic/[A-Z][A-Z0-9]*-\d+-.+)$")

def live_epic_branches(repo: Path) -> dict[str, str]:
    """name -> ref. origin/ wins when both exist; a local-only epic still counts."""

def epic_overlap(repo: Path, changed: list[str], base: str) -> list[tuple[str, list[str]]]:
    """(epic name, PRODUCT files both change), per live epic. The epic's diff is base...ref,
    so a fully merged unpruned epic diffs to nothing. Only PRODUCT_DIRS paths count -
    shared bookkeeping is touched by every lane by design and must never refuse one."""
```

Called from `task_preflight.check_scope` and `ship_preflight.check_lane` **before** the deployable-surface decision:

```python
hits = epic_overlap(repo, changed, base)
if hits:
    for name, files in hits:
        rep.err("lane", f"EPIC WORK: {len(files)} file(s) this lane changes are ALSO changed on the "
                        f"live epic {name}: {', '.join(files[:6])}{' ...' if len(files) > 6 else ''}. "
                        f"While that epic is in flight, main is FROZEN for its scope. STOP. Cut "
                        f"claude/<KEY>-<slug> off origin/{name} and land it with "
                        f"/cicd-close-story-merge-tree - never /cicd-push-e2e, never this door.")
    return "handoff"
rep.info("lane", f"{n} live epic branch(es) checked, no product-file overlap")
```

One `git diff --name-only` per live epic. No flag overrides it. Both modes, because a half-built quick-dev epic reaching prod through a side lane is the same incident. Not caught: a brand-new file in the epic's subsystem the epic has not touched — named and accepted.

### 2.4 The law — `git-policy.md` §Branch model, one short subsection

> ### The epic's mode is decided at kickoff, and a live epic freezes `main` for its scope (SCC-416)
>
> When the epic branch is cut, the operator decides once: **extension of main** (stories land by PR into the epic under the full gate, E2E on every landing, epic kept current with `main`) or **quick-dev** (stories land by direct push after the local light gate, no CI per story, E2E once at `/cicd-push-e2e`). The answer is the `-quickdev` suffix on the branch name, or its absence; every door reads it from there. An agent never chooses or changes it.
>
> In both modes, while the epic is live, **`main` is frozen for everything the epic changes.** Scope is the epic's diff. A main-bound lane sharing a product file with it is epic work and lands on the epic via `claude/<KEY>-<slug>` and the story door. Both preflights refuse it; no flag overrides. `main` is reached once, at the end, through `/cicd-push-e2e`, on the operator's decision.
>
> *Measured 2026-09-05: AVCH-80 → PR #72 → Cloud Run 00076, three Epic 24 runtime files shipped mid-epic by a preflight that never looked at the live epic.*

### 2.5 One sentence in `cicd-push-e2e.md` Step 1

The chore paragraph currently reads *"admits it under the light gate only when it touches a deployable path."* It gains: *"— and Step 1.5's preflight refuses it outright when that diff shares a product file with a live `epic/*`: that is epic work, and for a chore lane this check IS the 'every story done' sanity check."*

### 2.6 SOP §7 + changelog row — same commit (sop-currency gate)

## 3. Acceptance

| Row | Check | Proof |
|---|---|---|
| **A** | `ship_preflight` on a `chore/*` sharing a product file with a live epic → exit 2, `VERDICT: BLOCKED`, names the epic, the files, the story door | `test_ship_preflight.py` SP-Q.1 |
| **B** | `task_preflight` same lane → exit 2 `HANDOFF` naming the story door — never `/cicd-push-e2e` | `test_task_preflight.py` new block |
| **C1** | chore lane, live epic, no overlap → unchanged; says `1 live epic branch(es) checked, no product-file overlap` | SP-Q.2 + twin |
| **C2** | no live epic → unchanged, `0 … checked` | SP-Q.3 |
| **C3** | the epic branch itself → full gate, untouched | SP-Q.3 with a sibling epic live |
| **D** | remote-only epic counts | SP-Q.4 |
| **E** | overlap only in a non-product path → not refused | SP-Q.5 |
| **G** | fully merged, unpruned epic → no false hit | SP-Q.6 |
| **H** | **Replay, read-only, real repo:** `ship_preflight.py --repo Projects/AGY_AVIATIONCHAT --branch chore/AVCH-80-rolling-bugs --expect-key AVCH-80` → BLOCKED naming `epic/AVCH-100-epic-24-agent-quality` and the three runtime files | walkthrough |
| **I** | Revert-proof: call removed from `check_lane` → SP-Q.1 red; restored → green | Suite Ledger |
| **J** | `run_all.py` green; sop-currency gate passes | the commit lands without `[sop-ok]` |
| **K** | `cicd-create-epic-sprint.md` asks the question and produces the suffix; `cicd-close-story-merge-tree.md` Step 3 has exactly two arms keyed on `*-quickdev` | read in review |

## 4. Out of scope

AviationChat, after recovery, on the operator's call: the ruleset `exclude` (one call); the revert of `4afaa667` and re-landing AVCH-80's fixes on the epic as a story; `pr-check-skip.yml` to `main`; the enforce-on-create probe. Not built: a `hotfix:` carve-out, a push-time hook — not needed to stop today's incident recurring.

## 5. Sequence

RED tests → GREEN code → revert-proof → replay on the real repo → law, doors, SOP → walkthrough → `/smh-close-task-merge-tree` → PR → the operator's click.

## 6. Risk

A prod hotfix overlapping a live epic's file is refused — accepted; that overlap is a conflict the epic must absorb either way. Rollback is reverting the PR; the check is additive.

## Declared Change Set

- EDIT `.agents/scripts/task_preflight.py` — `EPIC_REF_RE`, `live_epic_branches()`, `epic_overlap()`; `check_scope` calls it before the surface decision → B, C1, C2, E, G
- EDIT `.agents/scripts/ship_preflight.py` — `check_lane` calls `tp.epic_overlap` before the light-gate return → A, C1, C2, C3, D, H, I
- EDIT `.agents/scripts/tests/test_ship_preflight.py` — `SP-Q · a live epic freezes main` block → A, C1, C2, C3, D, E, G, I
- EDIT `.agents/scripts/tests/test_task_preflight.py` — the Task-door twin → B, C1
- EDIT `.agents/rules/git-policy.md` — §2.4 subsection → law
- EDIT `.agents/commands/cicd-create-epic-sprint.md` — the kickoff question + the `-quickdev` name → K
- EDIT `.agents/commands/cicd-close-story-merge-tree.md` — Step 3 two-arm landing → K
- EDIT `.agents/commands/cicd-push-e2e.md` — one sentence in Step 1 → §2.5
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — §7: the two modes, the switch, the freeze → §2.6
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one row → §2.6
- NEW `_artifacts/_main/2026-09-05_scc-416-in-flight-epic-freezes-main/walkthrough.md` — the record → record
