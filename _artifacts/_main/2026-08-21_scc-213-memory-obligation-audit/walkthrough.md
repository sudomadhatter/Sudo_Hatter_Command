---
type: walkthrough
task: SCC-213
date: 2026-08-21
lane: smh-quick-fix
---

# SCC-213 — the memory store carries obligations that no rule enforces

**The audit in one line:** all 132 memories were read and classified; **11 carry an obligation that
nothing else in the system carries**, and each is now filed as missing-rule work. Two memories were
found actively wrong and fixed here. No memory was deleted.

The law audited against is **`.agents/rules/artifacts-always-first.md` lines 355–381** — *"The memory
store — what it is for, and what it must never carry"* — which the SCC-212 twin-parity lane landed
before this lane started. It is live on `main`.

---

## The numbers

| | Before | After |
|---|---|---|
| Memories in `_artifacts/_memory/` | 132 (+ `README.md` scaffolding + `MEMORY.md` index) | 132 |
| `MEMORY.md` index size | 18,361 / 25,600 bytes (**71.7%**) | 18,361 / 25,600 bytes (**71.7%**) |

The index does not move because this lane retired nothing — deliberately. See *"What was NOT done,
and why"*.

⚠️ The ticket's measured starting point (2026-08-17) was **127 memories / 17,302 bytes (68%)**. The
store grew 5 entries and 1,059 bytes in four days. The audit trigger is 90%; at this rate that is
roughly six weeks out.

---

## The classification — every entry, three buckets

The test, per the ticket: *if this memory disappeared tomorrow, would something BREAK, or would
someone merely have to look it up again?*

| Bucket | Count | Meaning |
|---|---:|---|
| **Recall** | 70 | context, a gotcha, a pointer. Correct as a memory. Left alone. |
| **CASE A** | 51 | carries an obligation, **and a rule / gate / command already carries the law**. |
| **CASE B** | 11 | carries an obligation, and **nothing else does**. The finding. |

⛔ **One method note, because it decides the count.** A "carrier" here means a file that is READ at
the moment the obligation binds — a `.agents/rules/` entry, an armed gate, an enforced test, or a
command body the agent must follow to do the work. A law stated only inside a memory has no carrier.
Being stricter than that (rules-only) would have pushed roughly twenty command-carried obligations
into CASE B and manufactured findings the system does not actually have — the failure
`audit-findings-need-a-file-anchor` names. Being looser would have hidden real gaps.

---

## ⛔ CASE B — 11 memories, 7 missing rules, all filed

Each row was verified absent on 2026-08-21 by grep across `.agents/rules/`, `.agents/commands/`,
`.agents/skills/`, `.agents/scripts/` and `.githooks/`. **None was deleted.**

| Ticket | The missing law | Memories it holds up | Cost already paid |
|---|---|---|---|
| **SCC-247** | A new blocking gate needs its own plan heading + the operator's quoted words; a settled decision is never written up as a gap; a concern ships with its fix after grepping for the existing mechanism | `blocking-gates-need-a-quoted-ruling` · `settled-decisions-are-not-gaps` · `propose-a-fix-only-after-grepping-for-the-existing-one` | SCC-119 shipped a derived exit-2 gate under a laundered "Operator ruling" header; it later walled the SCC-156 close-out. SCC-240 rebuilt a guard that already existed. |
| **SCC-248** | Naming a ticket key while saying "fix it now" points at existing coverage — it is not a mint order | `naming-a-ticket-is-not-a-mint-order` | SCC-225 lane, 2026-08-20: SCC-239 was minted and deleted the same minute. *"i can do this forever running of new tasks"* |
| **SCC-249** | A command body restates the Always-On obligations it depends on; a lens is never handed a bare suite run; nested wrapper menus auto-continue | `restate-alwayson-obligations-in-command-bodies` · `review-lenses-die-on-suite-output` · `wrapper-flows-collapse-nested-menus` | SCC-201: a five-lens fan-out was launched twice and **every lens died** on `run_all.py` output. A `/sudo-dev-story-tests` run shipped with no walkthrough at all. |
| **SCC-250** | The memory→rule **pointer** has no convention and no checker | *(blocks this ticket's own AC 3 — see below)* | This lane could not honestly satisfy AC 3 without it. |
| **SCC-251** | A GitNexus verdict is evidence only after checking freshness (`indexed_commit == HEAD`) and grep-verifying a bare LOW/0 `impact()` on attribute dispatch | `gitnexus-verify-index-fresh-after-pull` · `gitnexus-impact-misses-attribute-dispatch` | TEA-6: `impact("evaluate")` returned 0 callers / LOW while grep found 4 real call sites. |
| **SCC-252** | The secrets bundle **layout** is operator-owned; autopilot takeover checks orchestrator liveness | `secrets-bundle-layout-is-operator-owned` · `autopilot-manual-takeover-check-liveness` | *"leave the secrets alone they are organized the way I want."* The 8.22.2 takeover: the crashed autopilot came back twice and overwrote the run folder. |
| **AVCH-65** | AGY production `users/` is real NDA-signed data — never bulk-wipe | `agy-has-real-nda-users` | 2026-07-20: the operator asked for a full `users/` + Auth wipe believing it was test data. A read-only audit disproved it **before** anything was deleted. |

**Why AVCH-65 is not an SCC subtask.** The rule edit lands in AGY's own `.agents/rules/`, and each
repo's armed `commit-msg` gate answers only to its own Jira project — an `SCC` subject is rejected
inside AGY. Cross-repo work needs a ticket per repo, so it was minted in `AVCH`.

**The sharpest one.** `AVCH-65` is the clearest instance of the failure SCC-213 exists to prevent.
AGY's `constitution.project.md` **does** carry the sibling ruling (archive, never delete). It does
**not** carry "these users are real." So one half is enforced law and the other half is a prunable,
unenforced memory — and the only thing that stopped a real wipe was an agent that happened to check.

---

## CASE A — 51 memories, and the rule that carries each

This table is the deliverable that makes **SCC-250** mechanical. Line numbers are pinned where a grep
resolved one; otherwise the file and section are named.

### The git / landing family
| Memory | Carrier |
|---|---|
| `git-branch-model-standard` | `git-policy.md:3,17` + the armed pre-push hook |
| `nothing-guards-the-merge-target` | `git-policy.md:118,328` |
| `revert-target-must-be-a-ref` | `git-policy.md:381-389` |
| `one-shot-permission-persists-in-context` | `constitution.md:18` · `git-policy.md:74` |
| `main-merge-needs-operator-verbatim-approval` | `git-policy.md:139,147` + `mint-push-token.sh` |
| `close-out-command-is-daniels-signoff` | `git-policy.md:33,70` · `000-PLAN-FIRST-GATE.md:94` |
| `commit-and-push-are-one-action` | `git-policy.md:8` + `task_preflight.py` sync check (`0/0`) |
| `landing-is-not-closeout` | `/smh-close-task-merge-tree --after-merge` (verifies with plain git) |
| `lane-collision-is-gates-not-files` | `work-consolidation.md:159` · `cicd-merge-epic-workingtrees.md:115` |
| `landing-ceremony-is-the-block-not-the-gates` | recorded history; the PR door is the fix and it shipped |

### The worktree / artifact family
| Memory | Carrier |
|---|---|
| `worktrees-do-not-inherit-gitignored-assets` | `worktree-per-story.md:80,86` (⛔ `--unlink` before removal) |
| `story-artifacts-live-in-the-tree` | `worktree-per-story.md:197` · `smh-clean-code-audit.md:167` |
| `story-artifacts-two-doc-close` | `artifacts-always-first.md:24` |
| `limits-relocate-content-never-truncate` | `artifacts-always-first.md:39` (*"there is NO byte cap"*) + 2 guard tests |
| `active-context-pointer-budget` | `cicd-prune-context.md:2,19` (≤20 KB, runs unconditionally) |
| `lightweight-lane-for-specific-no-break-work` | `artifacts-always-first.md` §"When to Skip" (cited by `smh-quick-fix.md`) |
| `memory-store-is-read-by-every-platform` | `AGENTS.md` §7 + `artifacts-always-first.md:355-381` + the 25 KB cap in `run_all` |
| `plan-reviews-ride-md-feedback-memos` | `artifacts-always-first.md:303,391` |

### The board / ticket family
| Memory | Carrier |
|---|---|
| `to-do-next-is-the-queue` | `jira.md:55,73` |
| `review-status-means-needs-operator` | `jira.md:57` — **the follow-on it named has landed; fixed here** |
| `review-findings-are-not-a-work-queue` | `jira.md:509-521` |
| `a-defer-needs-a-structural-blocker` | `jira.md:514-515` — **its anchor was wrong; fixed here** |
| `discovered-work-becomes-a-lettered-part` | `work-consolidation.md:29-54` (Rule 1) |
| `followon-fixes-are-not-a-new-story` | `work-consolidation.md` Rule 1 rung 1 |
| `story-status-flip-contract` | `jira.md` §Statuses + `git-policy.md` sign-off ladder |
| `devrecord-story-slug-forks-the-record` | `smh-quick-fix.md` Step 4 (⛔ no `--story`, SCC-174) |
| `closeout-target-is-a-machine-contract` | `task_preflight.py --expect-key` (required) |
| `preflight-resolves-repo-from-cwd` | same — the prose guard became an exit code |

### The port / two-machine family — all six checks live in `port-checklist.md:3`
| Memory | Carrier |
|---|---|
| `echo-truncates-at-backslash-c` | `port-checklist.md` item 2 (`printf`, not `echo`) |
| `piping-a-gate-hides-its-exit-code` | `port-checklist.md` item 3 (verify the FILE, not `$?`) |
| `zsh-does-not-word-split-gate-args` | `port-checklist.md` item 3 |
| `two-machines-mac-and-pc` | `port-checklist.md:84` item 5 |
| `windows-authored-code-hides-posix-bugs` | `port-checklist.md` item 5 |
| `cross-repo-work-needs-a-ticket-per-repo` | `port-checklist.md:97` item 6 + the armed `commit-msg` gate |
| `powershell-console-fakes-mojibake` | `powershell-encoding-safety.md` |

### The test family — all in `tests-must-gate-for-real.md`
`comment-literals-invert-source-grep-tests` · `source-grep-guards-cannot-see-order` ·
`prose-pinning-guards-are-vacuous` (§ Mutation, lines 59, 81-82) · `stubbed-children-make-green-vacuous` ·
`red-test-can-die-before-its-assertion` · `atdd-mock-shape-must-match-backend-contract` ·
`e2e-gate-fiction-test-guardrails` (this memory **created** the rule) ·
`test-certification-at-shipping-sha` (Rule 4, named explicitly in the memory).

### The toolkit / platform family
| Memory | Carrier |
|---|---|
| `thin-projects-center-owns-workflow-law` | `project-law.md:3,15` §BIND |
| `repo-local-enforcement-never-centralizes` | `project-law.md:21,28` (the carve-out) |
| `one-door-per-platform-per-command` | `smh-sync-agents.md:13-14` |
| `sudo-commands-have-ap-twins-that-drift` | the `UNMAINTAINED` markers at `cicd-*-AP.md:4` + the twin-parity test |
| `sop-doc-currency-gate` | `sop-currency.md:3,8` + the armed `commit-msg` gate |
| `maintained-projects-allowlist` | `living-template-sync.md:13` + the commands that read the file |
| `grep-skips-gitignored-projects` | `lobby-search.md` |
| `no-personal-name-in-directives` | **enforced test** `test_command_surfaces.py:1074` + `smh-clean-code-audit.md:169` |

### The conversation / operator family
| Memory | Carrier |
|---|---|
| `close-the-loop-dont-hand-back-decisions` | `operator-profile.md:64` — speaking obligation #9 |
| `own-it-plainly-dont-make-excuses` | `operator-profile.md` speaking obligations |
| `writes-for-big-picture-operator` | `operator-profile.md` |
| `operator-chairs-the-board` | `smh-adviser-board.md:2` |
| `adviser-board-caucus-card-contract` | `smh-adviser-board.md:22,36` |
| `dev-flow-model-switch-stops` | `cicd-dev-story-tests.md:128` — *"never offer to"* |
| `dev-story-gate-is-conditional` | `cicd-dev-story-tests.md` Step 2.5 |
| `audit-findings-need-a-file-anchor` | `smh-self-audit.md:76` — *"No anchor, no finding"* |
| `agy-archive-never-delete-ruling` | AGY's own `constitution.project.md` |
| `board-narrative-lives-in-history` | AGY's board lint (a note on a done row is an ERROR) |

---

## What changed

| File | Why |
|---|---|
| `_artifacts/_memory/a-defer-needs-a-structural-blocker.md` | **Wrong anchor.** It opened *"**The rule:** `deferred-work.md` defines exactly three blockers"*. `deferred-work.md` is not a rule — it is the `_artifacts/_main/` **ledger** a legal defer is written into. The rule is `.agents/rules/jira.md:514-515`. Corrected, and the ledger's real role stated so the mistake is not repeatable. |
| `_artifacts/_memory/review-status-means-needs-operator.md` | **Stale open gap.** It said the SCC definition *"needs to be written into jira.md (pending fix, SCC-156 follow-on)"*. That follow-on **landed**: the misleading *"In Review is finished work waiting on a human"* line is gone and `jira.md:57` now carries the ruling. Updated, plus the fact the table records — `In Review` exists on **AVCH only**, not on SCC. |
| `_artifacts/_main/2026-08-21_scc-213-memory-obligation-audit/` | This walkthrough + `task.yaml`. |

Both edits are the ticket's own **false-coverage** class, one in each direction: the first pointed at
the wrong authority, the second advertised a gap that was already closed.

---

## What was NOT done, and why

**ACCEPTANCE 3 — *"Every CASE A is retired or reduced to a pointer"* — is not satisfied by this lane,
and that is a decision, not an omission.**

There is no pointer convention in the store. Measured: zero of 132 memories carry a structured
reference to the rule holding their law, there is no frontmatter field for one, and nothing checks
one. Inventing a body convention across 51 files with no checker would produce precisely the failure
SCC-213 was written to stop — *a thing that looks handled and is not*, one compaction from gone.

So the anchors were **recorded** (the CASE A table above, which is the whole job minus the stamping)
and the convention was **filed as SCC-250**, which also carries the mechanical stamping of all 51
once a checker exists. The ticket's own DO NOT — *"DO NOT edit `.agents/rules/` in this lane… File
it"* — is the instruction being followed.

**Also not done, on the ticket's instruction:** no general compaction pass. The store is at 71.7% of
a 90% trigger; volume is not the problem being solved here.

---

## Evidence

```
lane_qualify.py --paths <5 planned>          -> LIGHT (none deployable, none in the toolkit)
lane_qualify.py --paths <real diff>          -> LIGHT   [Step 3.5 EJECT re-check]
store read                                    132/132 memories, 392,251 bytes total
carrier search                                .agents/rules/ .agents/commands/ .agents/skills/
                                              .agents/scripts/ .githooks/  — per candidate
MEMORY.md index                               18,361 / 25,600 bytes (71.7%) — unchanged
```

**Gate output, run bare (never piped — a pipe reports its own exit code):**

```
python3 .agents/scripts/tests/run_all.py              exit 0   -- 41/41 files passed --
python3 .agents/scripts/workflow_lint.py --toolkit-only
                                                      exit 0   0 error(s), 0 warning(s), 8 info
python3 .agents/scripts/check_maps.py --depth3-only --strict
                                                      exit 0
python3 .agents/scripts/sop_currency.py --repo . --paths <staged>
                                                      exit 0   no usage surface in the diff
link + anchor over the 4 changed docs                 exit 0   all relative links resolve
lane_qualify.py --paths $(git diff --name-only origin/main...HEAD)
                                                      LIGHT    [Step 3.5 EJECT — lane holds]

git rev-parse HEAD   4d84e2506fb04799f655bde570ec347d7f4608ff
branch               chore/SCC-213-memory-obligation-audit, clean, 0/0 with origin
```

⚠️ **The suite caught a real miss on its first run** and is the reason there was a second: F2 failed
with *"missing row for `2026-08-21_scc-213-memory-obligation-audit/`"* — the `_artifacts/_main/INDEX.md`
row for this session's own folder. Added, then green. Worth recording because the gate that caught it
is the one an artifacts-only lane is most tempted to assume it does not need.

The 11 `[FAIL]` lines visible inside the green run are expected-fail probes on synthetic fixtures
(the `SCC-9` / `SCC-6` receipt lanes and `BETA · one: on purpose`), not lane failures — the run exits
0 with 41/41 files passed.

---

## Your Actions

- [x] CASE B filed — SCC-247, SCC-248, SCC-249, SCC-250, SCC-251, SCC-252 (subtasks of SCC-213) and
      AVCH-65 (cross-repo). Index rows appended to SCC-213's description.
- [x] Two defective memories corrected. No memory deleted.

Nothing is owed by the operator — the audit is complete and its findings are on the board.

Context for whoever picks the parts up: **SCC-250 is the one to read first.** It is why ACCEPTANCE 3
is open, and until a pointer convention exists with a checker behind it, every future memory can
re-create this same gap. The other six are ordinary rule work; that one is the mechanism.
