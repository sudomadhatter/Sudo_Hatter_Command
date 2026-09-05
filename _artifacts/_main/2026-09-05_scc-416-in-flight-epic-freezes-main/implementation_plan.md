---
IsArtifact: true
ArtifactMetadata:
  title: "SCC-416 — An in-flight epic freezes main: the guard on main-bound lanes"
  type: implementation_plan
  date: 2026-09-05
---

# Implementation Plan — SCC-416 — An in-flight epic freezes `main`

**Ticket:** [SCC-416](https://sudo-command.atlassian.net/browse/SCC-416) · **Lane:** `chore/SCC-416-in-flight-epic-freezes-main` off `origin/main` @ `f0dcb423`, worktree `.claude/worktrees/scc-416-epic-freeze` · **Door:** `/smh-close-task-merge-tree` (lobby, no deploy surface — a PR into `main` that Mr. Hatter merges)

**Operator ask (2026-09-05, verbatim intent):** *solve this issue with the branches; make it clear — even for an agent — that we are working to finish the epic on the branch while keeping it updated with main and implementing the E2E tests for the branch; THEN AND ONLY THEN we test it and decide if we can merge it to main.*

---

## 1. What happened, measured — the reproduction

**The incident.** AVCH-80 (rolling bug ticket) was cut as `chore/AVCH-80-rolling-bugs` **off `main`**. Its riders AVCH-120/121/122 were "found while pinning the bandit wire in AVCH-104 (story 24.4)" — Epic 24's subject — and routed out of the story to the rolling ticket. The lane's diff intersected the live `epic/AVCH-100-epic-24-agent-quality` in **six files** (`comm -12` of the two `git diff --name-only` lists):

```
_bmad-output/active-context/active-context.md
_bmad-output/component-specs/socratic-teaching.md
_bmad-output/sudo-tests.yaml
backend/agents/admin/agent.py          ← runtime
backend/agents/specialist/agent.py     ← runtime
backend/tools/librarian.py             ← runtime
```

`ship_preflight.py` said `chore branch touching backend/ -> the light gate … VERDICT: clear to gate and ship`. `/cicd-push-e2e` opened PR #72 into `main`; five CI checks went green; the operator merged at `4afaa667` (19:02:56 UTC); `deploy-backend.yml` put revision `aviationchat-backend-00076-boh` on 100% traffic at 19:13:59 UTC. **No Epic 24 story had been merged to `main`, by design.**

**The ruling that forbade it** — operator, 2026-09-03, the Epic 24 banner of `_bmad-output/implementation-artifacts/sprint-status.yaml`, **on the epic branch**:

> ⛔ DO NOT MERGE THIS EPIC TO main UNTIL EVERY STORY IS done AND THE OPERATOR'S FULL TEST PASS IS GREEN. Epic 24 integrates on epic/AVCH-100-epic-24-agent-quality — every story lands THERE, never on main. main is reached ONCE, at the end… ⚠️ KEEP THE EPIC BRANCH CURRENT WITH main.

The same day's plan (`_artifacts/epic_24/epic-sync-and-merge-guard/implementation_plan.md`, epic branch) wrote: *"Gap A — nothing written down stops a premature merge to main… the ruleset does NOT know whether the epic is finished."* Its Lane 2 — the lobby-side guard — was recorded **"not started"**. The story-door half (Step 0.6 "is the epic behind main? STOP") *was* built into `cicd-dev-story-tests.md`. The main-bound-lane half never was.

**Why no machine caught it — five mechanisms, each with a fix below:**

| # | Mechanism | Where | Fixed by |
|---|---|---|---|
| 1 | The stop is written on the branch it protects; a lane cut from `main` never reads that file | `sprint-status.yaml` on the epic | §2.1 — read the **live branch list**, not a file |
| 2 | `check_lane` / `check_scope` judge a `chore/*` by its own diff against `PRODUCT_DIRS` and never list `origin/epic/*` | `ship_preflight.py:276-334`, `task_preflight.py:1199-1233` | §2.1 |
| 3 | "Deployable → product change → ship" *promotes* epic work to prod; and `check_scope`'s handoff sends it to `/cicd-push-e2e` — the door that shipped it | same | §2.1 — the overlap check runs **before** the surface decision |
| 4 | The door's "every story on this epic must be done" check is switched off for the chore substitution | `cicd-push-e2e.md` Step 1 | §2.3 — the text says the preflight's overlap check IS that check for a chore lane |
| 5 | Nothing in the law says an in-flight epic freezes `main` for its scope; `git-policy.md` describes the chore road as "the DIFF selects the door" with no mention of live epics | `git-policy.md` §Branch model | §2.2 |

## 2. The change

### 2.1 The mechanical guard — one function, called from both preflights

**New in `task_preflight.py`** (shared, because `ship_preflight.py` already imports it as `tp` and both read `PRODUCT_DIRS` from here — "the two agree by construction"):

```python
EPIC_REF_RE = re.compile(r"^refs/(?:heads|remotes/origin)/(epic/[A-Z][A-Z0-9]*-\d+-.+)$")

def live_epic_branches(repo: Path) -> dict[str, str]:
    """name -> ref to diff against. origin/ wins when both exist (the machine-independent
    truth); a local-only epic still counts (it is live on THIS machine)."""

def epic_overlap(repo: Path, changed: list[str], base: str) -> list[tuple[str, list[str], list[str]]]:
    """For each live epic: (name, product files BOTH change, product dirs both touch at depth 3).
    The epic's diff is `base...<ref>` (merge-base to tip), so a fully-merged, unpruned epic
    diffs to nothing and cannot false-fire. Only PRODUCT_DIRS paths count: bookkeeping
    surfaces (`_bmad-output/active-context.md`, `sprint-status.yaml`) are shared by every
    lane by design, and refusing on them would refuse every lane."""
```

**In `task_preflight.check_scope`** — inserted after `changed` is read and **before** the `surface`/`touched` decision:

```python
hits = epic_overlap(repo, changed, base)
if any(files for _, files, _ in hits):
    for name, files, _ in hits:
        if files:
            rep.err("scope", f"EPIC WORK: {len(files)} file(s) this lane changes are ALSO changed on "
                             f"the live epic branch {name}: {', '.join(files[:6])}"
                             f"{' …' if len(files) > 6 else ''}. While that epic is in flight, "
                             f"main is FROZEN for its scope. STOP. This lands on the epic: cut "
                             f"claude/<KEY>-<slug> off origin/{name} and close it out with "
                             f"/cicd-close-story-merge-tree - never /cicd-push-e2e, never this door.")
    return "HANDOFF", [f for _, fs, _ in hits for f in fs]
for name, _, dirs in hits:
    if dirs:
        rep.warn("scope", f"no file overlap, but this lane and the live epic {name} both touch "
                          f"{', '.join(dirs)} - same subsystem. Confirm this is not epic work "
                          f"before landing it on main.")
rep.info("scope", f"{len(hits)} live epic branch(es) checked, no product-file overlap")
```

**In `ship_preflight.check_lane`** — same shape, same place (after `changed`, before `touched`), `rep.err("lane", …)` and `return "handoff"`. The door's exit-2 text already says *BLOCKED - nothing may be gated, merged or pushed*.

**Order is the point.** Today `check_scope` reaches `touched` → *"deployable path(s) changed… ship it with /cicd-push-e2e"*, and `check_lane` reaches `touched` → *"light gate"*. The overlap check sits **above** both, so a lane that is epic work is named epic work before either door can call it a product change.

**What it does NOT catch, said plainly:** a change in the epic's subsystem that touches a file the epic has not touched (a brand-new file in `backend/agents/specialist/`). File-level overlap catches the AVCH-80 shape exactly and produces no false refusals on shared bookkeeping; the depth-3 directory WARN covers the subsystem case as a nudge, not a block. The full answer to that case is the creation-time landing decision (§4, Phase 2).

### 2.2 The law — `git-policy.md` §Branch model, new subsection after the branch table

> ### ⛔ An in-flight epic freezes `main` for its scope (SCC-416, 2026-09-05)
>
> While any `epic/*` branch is live on origin, **`main` is frozen for everything that epic is changing.** The epic's scope is its diff — `git diff --name-only origin/main...origin/epic/<KEY>-<slug>` — not its ticket tree and not its title. A main-bound lane (`chore/*`, or anything aimed at `main`) whose diff intersects it **is epic work**: it lands on the epic, via a `claude/<KEY>-<slug>` branch off the epic and `/cicd-close-story-merge-tree`. Never `main`. Both preflights measure this and refuse on it; the refusal is not overridable by a flag.
>
> **The three things that are true for the whole life of the epic:**
> 1. **Every story lands on the epic.** `main` is reached **once**, at the end, through `/cicd-push-e2e` — after every story is done, the epic has been driven by the operator, and he decides. That decision is his; it is never a next step an agent schedules.
> 2. **The epic stays current with `main`.** `cicd-dev-story-tests.md` Step 0.6 STOPs a story when the epic is behind. The sync itself is an epic-branch write and, under a ruleset that requires checks on `epic/**` (AviationChat's AVCH-119), it is a **pull request into the epic**, not a direct push — see SCC-416 Phase 2 for the door.
> 3. **The E2E gate runs on the epic.** A ruleset requiring the four `pr-check.yml` jobs on `epic/**` (AVCH-119) means every story PR into the epic runs Playwright and the emulator E2E. Green there is the branch being tested as it grows; it is **not** the epic being finished.
>
> **Why the ruleset alone cannot do this:** `main write gate` knows a PR's checks, not whether an epic is finished. A green mid-epic PR satisfies it. The stop has to be measured from the live branch list, which is what the preflights now read.
>
> **What "tested" means here.** Five green CI checks on a half-built epic are five green checks on a half-built epic. **CI green is not "tested."** Tested is: the epic's stories are done, the operator has driven the full pass, and he has said so. Then `/cicd-push-e2e`.
>
> *Measured 2026-09-05 (AVCH-80 → PR #72 → Cloud Run 00076): a chore lane off `main` carrying three Epic 24 runtime files was classed "product change → light gate → ship" by a preflight that never looked at the live epic, and deployed. The ruling forbidding it was on the epic branch, unreadable from a main-bound lane. This section and the overlap check are the two halves of the fix.*

Plus one clause in `constitution.md`'s git bullet after *"`main` is never an agent's"*: *"— and while an epic is in flight, its scope never reaches `main` outside the epic (`git-policy.md` §in-flight epic)."*

### 2.3 The door texts

- **`cicd-push-e2e.md` Step 1**, the chore paragraph: *"the diff decides the GATE, not the DESTINATION. Step 1.5's preflight refuses a chore lane whose diff overlaps a live `epic/*` — that lane is epic work and lands on the epic. For a chore lane, that overlap check IS the 'every story done' sanity check; it is not switched off by the substitution."*
- **`smh-close-task-merge-tree.md` Step 1** preflight row: add the new exit-2 reason and its remedy (cut `claude/` off the epic; story door).
- **`cicd-quick-dev.md` / `smh-quick-fix.md` / `smh-plan-task.md`**, the branch-cut arm: one line before the cut — `git for-each-ref refs/remotes/origin/epic/` — *"a live epic is listed → if this work touches what that epic touches, the lane is `claude/<KEY>-<slug>` off the epic, not `chore/` off `main`. When in doubt, cut off the epic: a story lane can always be re-pointed, a chore lane that reaches `main` cannot be un-deployed."*
- **SOP §7** (the `/cicd-push-e2e` chore-admission paragraph, ~line 862) and the lane table: the same rule in the operator's voice; **changelog row** `2026-09-05 · SCC-416 · …`, same commit (sop-currency gate).

## 3. Acceptance — every row is a test or a command

| Row | Check | How it is proven |
|---|---|---|
| **A** | `ship_preflight` on a `chore/*` whose diff shares a product file with a live epic → exit 2, `VERDICT: BLOCKED`, message names the epic, the files, the road | `test_ship_preflight.py` SP-Q.1 |
| **B** | `task_preflight` same lane → exit 2, `HANDOFF`, and the message says the STORY door — never `/cicd-push-e2e` | `test_task_preflight.py` new block |
| **C1** | chore lane, live epic, **no** overlap → behaviour unchanged (ship: light gate; task: LOCAL/HANDOFF by surface as today), and the output SAYS `1 live epic branch(es) checked, no product-file overlap` | SP-Q.2 + task twin |
| **C2** | no live epic → unchanged, says `0 live epic branch(es) checked` | SP-Q.3 |
| **C3** | the epic branch itself → full gate, untouched by this check | SP-A already pins it; SP-Q asserts it still holds with a sibling epic live |
| **D** | a **remote-only** epic (`refs/remotes/origin/epic/…`, no local ref) counts | SP-Q.4 — fixture pushes the epic to the bare origin and deletes the local ref |
| **E** | overlap only in a non-product path (`_bmad-output/x.yaml` on both) → **not** refused | SP-Q.5 |
| **F** | same depth-3 dir, no file overlap → exit 1 WARN naming the dir, not a block | SP-Q.6 |
| **G** | a fully merged, unpruned epic → no false hit (its `base...ref` diff is empty) | SP-Q.7 |
| **H** | **The incident replayed against the fixed gate, on the real repo, read-only:** `ship_preflight.py --repo Projects/AGY_AVIATIONCHAT --branch chore/AVCH-80-rolling-bugs --expect-key AVCH-80` → BLOCKED naming `epic/AVCH-100-epic-24-agent-quality` and the three runtime files | pasted in the walkthrough |
| **I** | Revert-proof: the call removed from `check_lane` → SP-Q.1 red; restored → green | walkthrough Suite Ledger |
| **J** | `run_all.py` green; sop-currency gate passes on the commit (SOP + changelog staged) | commit succeeds without `[sop-ok]` |

## 4. Out of scope here — named so it is not lost

- **Phase 2 (next SCC lane):** the creation-time landing decision — `close_command` mandatory at lane open, no `TBD`; the push-time hook (`require-push-approval.py`) echoing it plus `N behind main` on every push; the **epic sync door** (`chore/<EPIC-KEY>-absorb-main` off the epic → PR into the epic, because AVCH-119 makes a direct sync push impossible — measured: `required_status_checks` on `epic/**`, `do_not_enforce_on_create: false`).
- **AviationChat (AVCH, its own tickets, after recovery):** the revert of `4afaa667` and re-landing the AVCH-80 fixes on the epic as a story; `pr-check-skip.yml` to `main` (today only on the epic branch, so a fresh epic's docs-only PR is unmergeable); the enforce-on-create probe (the only live epic predates the ruleset; `git push -u origin epic/NEW` may be refused).
- **Not changed:** the ruleset, CI, anything in `Projects/`.

## 5. Sequence

1. RED — write SP-Q and the task twin; run both files; paste the red totals.
2. GREEN — `task_preflight.py` (functions + `check_scope`), `ship_preflight.py` (`check_lane`); run both files + `run_all.py`.
3. Revert-proof (row I).
4. Row H against the real AviationChat repo, read-only.
5. Law + doors + SOP + changelog, one commit each or one commit — the sop-currency gate decides the grouping.
6. Walkthrough; `/smh-close-task-merge-tree` → PR → Mr. Hatter's click.

## 6. Risk

**False refusal on a genuine prod hotfix that overlaps a live epic's file.** Accepted for Phase 1: that overlap is a real conflict the epic must absorb either way, and the operator has said main rarely moves during an epic. If it ever bites, Phase 2 adds a declared, tracked `hotfix:` carve-out in `task.yaml` — never a flag.
**Runtime cost:** one `git diff --name-only` per live epic. Negligible.
**Rollback:** revert the PR. The check is additive; nothing else moves.

## Declared Change Set

- EDIT `.agents/scripts/task_preflight.py` — `EPIC_REF_RE`, `live_epic_branches()`, `epic_overlap()`; `check_scope` calls it before the surface decision → B, C1, C2, E, F, G
- EDIT `.agents/scripts/ship_preflight.py` — `check_lane` calls `tp.epic_overlap` before the light-gate return → A, C1, C2, C3, D, H, I
- EDIT `.agents/scripts/tests/test_ship_preflight.py` — new `SP-Q · a live epic freezes main` block → A, C1, C2, C3, D, E, F, G, I
- EDIT `.agents/scripts/tests/test_task_preflight.py` — new block, the Task-door twin → B, C1
- EDIT `.agents/rules/git-policy.md` — §2.2 subsection → law
- EDIT `.agents/rules/constitution.md` — one clause in the git hard stop → law
- EDIT `.agents/commands/cicd-push-e2e.md` — Step 1 chore paragraph → §2.3
- EDIT `.agents/commands/smh-close-task-merge-tree.md` — Step 1 preflight row → §2.3
- EDIT `.agents/commands/cicd-quick-dev.md` — branch-cut arm → §2.3
- EDIT `.agents/commands/smh-quick-fix.md` — branch-cut arm → §2.3
- EDIT `.agents/commands/smh-plan-task.md` — branch-cut arms (two) → §2.3
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — §7 chore admission + lane table → §2.3
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one row → §2.3
- NEW `_artifacts/_main/2026-09-05_scc-416-in-flight-epic-freezes-main/walkthrough.md` — the record → record
