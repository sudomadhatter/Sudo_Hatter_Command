---
IsArtifact: true
ArtifactMetadata:
  title: SCC-113 — the In Progress seam
  type: walkthrough
  date: 2026-08-11
---

# SCC-113 — Nothing moved a ticket to `In Progress`

**Branch** `chore/SCC-113-jira-in-progress-seam` · **Lane** LOCAL · **HEAD** `f4ae128`
**Plan** [implementation_plan.md](implementation_plan.md) · **Ticket** SCC-113 under SCC-12

---

## Task Checklist

- [x] **Diagnose.** Five transition seams: four wrote `Done`, exactly one wrote `In Progress`
      (the BMAD story lane). Every non-epic SCC ticket is a `Task`, so nothing here was ever
      visible in flight.
- [x] **`jira_feed.py start`** — the verb, with the read-back contract its four siblings have.
- [x] **`post-commit-jira-start.sh`** — fires on the first commit of `chore/ · claude/ · epic/`.
- [x] **`/smh-quick-dev` Step 0.5** — the visible move at worktree-open.
- [x] **`--yes` on all three `Done` call sites**, plus a regression guard.
      - ⚠ The guard was wrong twice before it was right. See Review, findings 1 and 1′.
- [x] **`jira.md` guardrail 4** rewritten; `INDEX.md` and the SOP updated in the same commits.
- [x] **Prep commit `ea8fe97`** — regenerated the platform doors SCC-77 left stale (found by
      re-deriving the blast radius before starting; **not** part of this ticket's scope).
- [x] Review gate — **two** clean-room passes, both CONCERNS, all 19 findings closed.

---

## Evidence

**Every gate below was run bare (no pipe) at `f4ae128`, the sha that ships.**

| # | Acceptance item | Assertion | RED → GREEN |
|---|---|---|---|
| 1 | `start` moves a ticket, `--yes`, reads back, exits 2 if it did not land | `test_jira_feed.py` "start: To Do → In Progress", "passes --yes", "a transition that silently no-ops is reported" | RED `invalid choice: 'start'` → GREEN |
| 2 | Idempotent | "already In Progress is a no-op", "the no-op makes NO transition call at all" | RED → GREEN |
| 3 | Refuses `Done` and Subtask; allows `Epic` | "a Done ticket is REFUSED", "a Subtask is refused", "an Epic IS allowed" | RED → GREEN |
| 4 | First commit on a keyed branch moves it | `test_jira_start_hook.py` "first commit on chore/TEST-1-* moves it to In Progress" | RED "the recorder script exists" 0/1 → GREEN |
| 5 | One transition per branch; failure retries | "exactly ONE transition per branch", "later commits cost NO further transition", "a FAILED move writes NO marker" | RED → GREEN |
| 6 | Can never block a commit | "the commit itself always succeeds", "a commit succeeds with NO board reachable at all" | RED → GREEN |
| 7 | `/smh-quick-dev` calls it at worktree-open | present in the command brain; `workflow_lint --toolkit-only` exit 0 | GREEN |
| 8 | All three `Done` sites carry `--yes` | "yes-guard: every `workitem transition` under `.agents/` passes --yes" | **RED, 4 offenders** → GREEN |
| 9 | `jira.md` guardrail 4 enumerates what ships | link + anchor sweep, 17 md files / 0 dead links | GREEN |
| 10 | Suite green, doors present | `run_all.py`, `workflow_lint --toolkit-only` | GREEN |

### The RED, as captured

```
[FAIL] start: To Do -> In Progress: usage: jira_feed.py [-h] {outline,mint,devrecord,audit,trace,flag,check} ...
jira_feed.py: error: argument verb: invalid choice: 'start'          (× 11 start cases)
[FAIL] yes-guard: every `workitem transition` under .agents/ passes --yes:
       .agents/commands/cicd-push-e2e.md:134, .agents/commands/smh-close-task-merge-tree.md:244,
       .agents/commands/smh-merge-multiple-workingtrees.md:225, .agents/workflows/cicd-push-e2e.md:134
-- 105/117 passed --
[FAIL] hook: the recorder script exists          -- 0/1 passed --
```

### The GREEN, at `f4ae128`

```
run_all.py                        15/15 files passed          exit 0
  ├─ jira_feed                    134/134 passed
  └─ jira_start_hook               30/30 passed
workflow_lint.py --toolkit-only   0 error(s), 0 warning(s)    exit 0
sop_currency.py                                               exit 0
py_compile (3 files)                                          exit 0
sh -n (both hooks)                                            exit 0
link + anchor                     17 md files, 0 dead links
```

### ⭐ Live end-to-end, on the real board

The hook fired on **its own first commit**, which is the strongest evidence available:

```
$ git commit -F …
jira-feed: SCC-113 To Do -> In Progress
[chore/SCC-113-jira-in-progress-seam a944b44] SCC-113 feat(jira): the In Progress seam

$ acli jira workitem view SCC-113 --fields "key,status"
Key: SCC-113
Status: In Progress

$ ls "$(git rev-parse --absolute-git-dir)" | grep jira-started
jira-started-chore-SCC-113-jira-in-progress-seam
```

The next two commits printed **nothing** — the marker short-circuited them, which is the
once-per-branch property observed rather than asserted.

---

## Code Review (2026-08-11)

```
Verdict: PASS @ f4ae128
```

**Two independent clean-room passes ran** (`bmad-review-adversarial-general` in a subagent with no
conversation context, Opus, hunting the diff before reading the plan). Both returned **CONCERNS**.
All **19** findings are closed at `f4ae128`. Neither pass found a defect in the shipped *behaviour* —
the second explicitly verified the feature works end to end in both a worktree and a plain checkout.
**Every finding was in the guards or the claims around it**, which is the failure mode this repo
cares most about.

### Pass 1 @ `a944b44` — 8 findings, all closed in `882cc27`

| # | Sev | Finding | Closed by |
|---|---|---|---|
| 1 | **HIGH** | The `--yes` guard used a 3-line window, so prose on the line excused a deleted flag — at `smh-merge-multiple-workingtrees.md`, **a site this ticket was fixing**. Verified by mutation: 4 caught, **2 missed** | anchored to the command span |
| 2 | MED | Hook was **not** silent on failure — `jira_feed` prints via `say()` to **stdout**, and only stderr was redirected. A `Done`-key branch printed a 5-line refusal on *every* commit. Falsified 3 shipped claims | `>/dev/null 2>&1` |
| 3 | MED | A permanently-failing state re-paid the round-trip every commit, inline, with `acli`'s 90s ceiling — measured 5.5s with a sleeping stub; up to 90s per commit on a dead uplink | `--timeout` threaded through, hook passes 10 |
| 4 | MED | **A non-startable status wrote the marker**, silencing the branch forever. `Blocking` at open → marker → blocker clears → ticket sits in `To Do` for the whole build. *The very defect SCC-113 exists to close, reintroduced by SCC-113* | exit 3 = "left alone, ask again"; marker only on 0 |
| 5 | LOW | "one acli call per branch" was a 3× understatement (`view` → `transition` → read-back) in 4 operator-facing places | corrected everywhere |
| 6 | LOW | The "board unreachable" test drove the silent-no-op path, not a transport failure | renamed; real unreachable case added |
| 7 | LOW | Three source-greps in a file advertising "the REAL hook against a REAL git repo" | DISABLE + `jira.conf` now runtime |
| 8 | LOW | Plan audit F-3 promised a worktree assertion; none existed | added — and it caught a fixture bug immediately |

### Pass 2 @ `882cc27` — 11 findings, all closed in `f4ae128`

| # | Sev | Finding | Closed by |
|---|---|---|---|
| 1′ | **HIGH** | **The fix re-opened its own hole.** Joined lines were appended **raw**, so a comment naming `--yes` *below* a wrapped call excused the deleted flag — and `jira_feed.py:1049` is the repo's only **executable** call site and is exactly that shape | strip every joined line; real continuations only |
| 2′ | MED | **The silence fix had zero effective coverage** — `">/dev/null 2>&1" in text` is satisfied by the interpreter probe's own line. Suite went **29/29 green against the unfixed hook** | runtime `Done`-key case |
| 3′ | MED | **Four** exit codes, not three: a hung uplink and a missing binary escaped as an uncaught traceback (exit 1), and transport failure shared exit 2 with "wrong key" — whose documented instruction is *"mint a new ticket"*. A dead uplink instructed a **duplicate** | `acli()` catches; new exit 4 = transport |
| 4′ | MED | False positives on 4-line continuations (the repo's own style) and on a line mentioning `acli` before the call | same rewrite; now positive controls |
| 5′–11′ | LOW | Value-blind `--timeout` grep · 2 surviving "one call" claims · "capped at 10 seconds" sold as a total (it is per-call, ×3) · "one exchange per branch, ever" untrue for exit-3 branches by design · worktree rationale comment wrong · ① not updated for exits 3/4 | all corrected |

### Mutation proof — the guards fail on the defect

A guard nobody has seen fail is decoration. Both were mutation-tested against **real** files:

```
--yes guard, mutating .agents/scripts/jira_feed.py itself:
                 clean  <- baseline (untouched, compliant)
      CAUGHT at [1049]  <- --yes deleted
      CAUGHT at [1049]  <- --yes deleted + inline comment naming --yes
      CAUGHT at [1049]  <- --yes deleted + comment line BELOW naming --yes

silence guard, reverting the hook to the old 2>/dev/null:
  as shipped   -- 30/30 passed --
  mutated      -- 28/30 passed --   leaked: '[ERR] TEST-9 is Done - that is not your key…'
```

Controls now stand at **8 negative / 6 positive** for the `--yes` guard.

### Step 0.7 — blast radius re-derived against current `main`

- **Nothing landed** on `main` since the base (`4c8cf7f`); no reference in this diff moved.
- **True overlap: none.** `merge-tree` produced a clean tree, no conflicts.
- **Sibling lane:** `chore/SCC-110-hooks-armed` is live with **uncommitted** work overlapping
  `.agents/scripts/INDEX.md`. Both edits are additive to different sections. **Landing order does
  not matter**; whichever lands second re-checks that file. SCC-110's subject ("nothing asserts
  `core.hooksPath` at runtime") *strengthens* this design — it is why Layer C is not optional.

### Gate table

| Gate | Result |
|---|---|
| Enforcement suite | **15/15 files, exit 0** |
| Toolkit lint | **0 errors, 0 warnings, exit 0** |
| Assertion evidence | RED captured → GREEN at `f4ae128` |
| SOP currency | exit 0 — the SOP moved in the same commits |
| Link + anchor | 17 md files, **0 dead links** |
| Door parity | 4 doors regenerated per touched brain via `/smh-sync-agents` |
| Clean-code floor | `py_compile` 0 · `sh -n` 0 (both hooks) · no `git add -A` · explicit paths only |

### Stated limits — not oversights

- **AGY is not covered.** `.githooks/` and `.agents/scripts/git-hooks/` are repo-local enforcement
  that never centralize, and AGY has **no `jira_feed.py`**. Owed its own **AVCH ticket** (plan F-1).
- **`docs/_scc_sops_prds/jira_manual.md:198`** still shows the un-flagged form. Deliberate: it is
  the *by hand at a terminal* row, where a human can answer the prompt. Recorded in `jira.md`.
- **The guard skips `>` blockquote lines.** `jira.md` teaches the trap by quoting the bad form in a
  callout; a positive control pins that this stays true. Real call sites live in fenced blocks.
- **A third blind pass was not run** on `f4ae128`. Pass 2's findings were all guard/doc-level and
  each fix is pinned by a control or a mutation proof above.

---

## Your Actions

1. **Review and close out** — `/smh-close-task-merge-tree` (invoking it is your merge sign-off).
   Preflight will want `--expect-key SCC-113`.
2. **Restart opencode and start a new Codex chat** — the sync refreshed the machine-global caches.
3. **On the PC**, once this lands: `git config core.hooksPath .githooks` or the hook is silently OFF.
4. **Decide on the AVCH ticket** for AGY coverage (plan F-1 + F-6).
5. **Decide on the `workflow_lint` door-content gap** — it checks door *presence*, not *content*,
   which is why SCC-77's stale doors passed its close-out. Separate defect, deserves its own ticket.
