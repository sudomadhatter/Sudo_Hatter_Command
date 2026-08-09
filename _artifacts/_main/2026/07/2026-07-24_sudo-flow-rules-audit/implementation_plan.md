---
IsArtifact: true
ArtifactMetadata:
  title: Fix plan — sudo flow + rules audit findings (F1–F12) + quick-dev hardening
  type: implementation_plan
  date: 2026-07-24
---

# Implementation Plan — audit fixes + /sudo-quick-dev hardening

Source: [2026-07-24_sudo-flow-rules-audit.md](2026-07-24_sudo-flow-rules-audit.md). All edits are lobby **master** files (`.agents/commands/` + `.agents/rules/` + one `_my_resources` doc); mirrors follow via `/sync-agents`. No project-code changes. ② (`sudo-dev-story-tests.md`, 11,988/12,000 chars) is deliberately **untouched** — its contradiction is fixed from the constitution side.

## Edit 1 — [sudo-update-sprint-memory.md](../../../../../.agents/commands/sudo-update-sprint-memory.md) (F1 + F11 + F4b)

Now 12,420 chars — **over the 12,000 Antigravity workflow limit**. Target ≤ 11,950, verified by `wc -c` after the edit.

- **Rename Step 2 heading** → `## Step 2 — Verify the claimed work exists on disk (grep-check, NOT a code review)`.
- **Strip** `(G1 close-out)` from the H1 (orphaned guardrail numbering).
- **Trim without weakening any contract** — compress explanatory parentheticals only; every gate, the no-punt flip rules, fail-open verdict read, explicit-paths ban, and Step 7/8 sequence stay semantically identical. Targets: the `/autopilot` no-conflict parenthetical (Step 4), Step 7's bash-comment tails and intro sentence tail, the `~27k tokens` aside (Step 1), the "(MOST sessions …)" aside (Step 6), frontmatter description tail.

## Edit 2 — [constitution.md](../../../../../.agents/rules/constitution.md) (F2 + F12)

- **Gate-word carve-out** — append to the "Never treat 'ok', 'perfect', 'continue' …" hard stop: a reply word that a sudo command's own body explicitly defines as its gate trigger (②'s Step-2 `continue`, close-out's invocation-as-sign-off) **IS** the explicit approval for exactly the step it gates; the ban targets ad-hoc chat words, not command-defined gates.
- **Review-output homes** — extend the "Always save code-review output…" bullet: the ③ gate ALSO writes its machine-read verdict to `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md`; two homes by design (session detail vs the verdict close-out greps). Prevents a future "fix" that collapses one into the other.

## Edit 3 — [000-PLAN-FIRST-GATE.md](../../../../../.agents/rules/000-PLAN-FIRST-GATE.md) (F3)

- Exception paragraph: drop `task.md` from the artifact-directory list.
- "After Approval" step 1: replace `Create task.md artifact…` with the current contract — track via the live TodoWrite list; its end-state lands as `## Task Checklist` inside `walkthrough.md`(per `artifacts-always-first`). No other restructuring (surgical).

## Edit 4 — [sudo-boot-sprint-memory.md](../../../../../.agents/commands/sudo-boot-sprint-memory.md) (F4)

- Step 3: drop the orphaned **G2/G3/G5/G6/G8** numbers — same five checks, plainly named; the Firestore line generalized to "shared-resource singleton (one client per DB/auth/cache — per constitution)" so the shared command stays project-agnostic.
- Strip `(G1)` from the H1 and delete the "manual trigger for Guardrail G1" sentence.

## Edit 5 — [sudo-code-review.md](../../../../../.agents/commands/sudo-code-review.md) + [clean-code-audit.md](../../../../../.agents/commands/clean-code-audit.md) (F5)

- ③ Step 3.5: when running **inside ③** (Step 1's adversarial review already walked the hunks), clean-code-audit runs the **machine floor + comment contract (§2A)** only and **imports Step 1's drift findings** into its findings table (source-labelled `review`); it does not re-hunt §2B.
- clean-code-audit Step 2: matching scoping note — Part B runs only on **standalone** invocations.
- Result: identical coverage (same checklist, run once), one full diff re-read saved per story.

## Edit 6 — [sudo-code-review.md](../../../../../.agents/commands/sudo-code-review.md) (F6)

Make the per-story CI-pipeline audit **change-triggered**. Step 3.1 guard (a) + Step 3.4's soft-step scan run only when:

1. the story's diff touches `.github/workflows/**` or a test-runner config (playwright/vitest/pytest), or
2. `sudo-tests.yaml` has no `ci_audit:` record, or
3. `git log -1 --format=%H -- .github/workflows/` differs from the recorded `ci_audit.sha`.

After a run, write `ci_audit: {sha, date}` back into `sudo-tests.yaml`; otherwise the verdict states "CI audit current as of `<sha>`". Exact drift detection, zero repeated audits.

## Edit 7 — [sudo-quick-dev.md](../../../../../.agents/commands/sudo-quick-dev.md) (F7 + Daniel's ask: fast AND safe)

The fast lane keeps its speed (no ATDD, no planning stop, no adversarial review) and gains four cheap guards — each targets a real risk the lane currently leaves open:

1. **Step 0.5 NEW — worktree.** Reuse/open `claude/<slug>` per `worktree-per-story` before the first edit. Costs seconds; keeps quick fixes tangle-free, rollbackable, and landable through the normal close-out path. (Today quick-dev says nothing about git — edits land in the shared checkout.)
2. **Step 2 — root-cause line + the EJECT TRIPWIRE.** One line: find root cause before fixing, no symptom patches. And a hard scope guard — if the emerging change exceeds **\~3 files / \~150 changed lines**, or touches a **protected surface** (auth/tenancy walls, payments, PII handling, DB schema/security rules, a cross-boundary API/SSE contract), **STOP and eject to the full ①②③ lane** with a one-line reason. The fast lane self-ejects the moment the change turns out not to be small — that is the "still safe" core.
3. **Step 2b NEW — scoped verification.** Run the test file(s)/suite covering the touched module — the whole endpoint suite when a shared handler changed (the sibling-regression lesson) — and paste actual output. **Bug fixes add ONE pinning regression test** (a fix without a test regresses silently); config/copy tweaks need none. Never the full suite — that's ③'s job in the full lane.
4. **Step 3 — swap the misfit auditor** (F7): `/sudo-self-audit` (pre-dev tool, audits plans) → `/clean-code-audit` (purpose-built diff audit: machine floor + drift bans, full two-half pass since no adversarial review ran here), plus a one-line AC-trace confirmation in the report.
5. **Done — unchanged** (stop; the human reviews and runs close-out), plus one explicit line: commit inside the worktree with explicit paths; never land on `main_debug`.

Size: \~3.3k → \~5.5k chars, far under the 12k limit.

## Edit 8 — [sudo_workflows_testing.md](../../../../../_my_resources/_quick_reference/sudo_workflows_testing.md) (F9 + F10)

- Swap `/bmad-create-epics-and-stories` → `/sudo-create-epic-sprint` in all four places (map node, §3 table, §4 step 1, §7 trigger column), noting it wraps the BMAD skill + sprint board + risk-scoring with the two-checkpoint flow contract.
- Fix ③'s order in §3/§4: review → test gate (suite + trace + NFR + test-review + automate evidence) → clean-code audit (Step 3.5) → verdict. Reflect Edit 5/6 (drift findings imported; CI audit change-triggered) in the two lines that describe them.

## Execution order & verification

1. Edits 1–8 (any order; Edit 1 first — it's the over-limit file).
2. `wc -c` on every touched command: **all ≤ 12,000** (close-out ≤ 11,950; ③ currently 10,849 + Edits 5/6 must stay under — compress ③'s Step 0 to the compact close-out style if needed).
3. `/sync-agents` with `-Maintained` (lobby 4-platform + AGY + Fresh); rules ride automatically, Fresh drift-check expected clean.
4. Walkthrough with per-file diffs summary + **explicit-path commit command** (lobby `main_debug`, Daniel's git lane — matches the 2026-07-20 step2-gate-rework precedent).

**Not in scope:** ② (at char ceiling — untouched), `_AP` twins (headless lane has no Step-2 gate / quick-dev; no behavior change applies), F8 unless answered below.

## Open questions (answer with your approval)

1. **F8 — ③'s suites:** (a) keep both stacks always \[status quo — default if unanswered\] or (b) full suite of the touched stack, other stack only when a shared contract changed \[my recommendation; PR CI + /sudo-e2e still cover both pre-ship\].

2. **F6 write-back:** OK for ③ to write the `ci_audit: {sha, date}` record into `sudo-tests.yaml`? (It's the gate's own config; the alternative — recording only in verdict files — makes staleness detection grep-y and weaker.)
3. **Quick-dev tripwire thresholds:** \~3 files / \~150 lines + the protected-surface list — confirm or adjust.
