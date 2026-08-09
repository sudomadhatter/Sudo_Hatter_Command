---
IsArtifact: true
ArtifactMetadata:
  title: Sudo flow + rules audit — occasional quality pass
  type: code_review
  date: 2026-07-24
---

# Sudo Flow + Rules Audit — 2026-07-24

Scope: the full story loop (①②③ + close-out + satellites), `sudo_workflows_testing.md`, and all 19
rules in `.agents/rules/`. Question that triggered it: "is there a code review inside
`/sudo-update-sprint-memory` Step 2?" Focus: cut repetition/token waste without lowering the
quality/check/test bar.

## The direct answer — close-out Step 2 is NOT a code review

`/sudo-update-sprint-memory` Step 2 ("Code-verify") is a **grep-level existence check**: confirm the
story's claimed fix/feature is actually present in the files it says it touched, mark
`✅ / ❌ / ⚠️`. It exists because close-out often runs in a fresh chat after an autopilot run, and a
polished walkthrough can claim work the tree doesn't hold (the 2026-06 autopilot-takeover incident —
artifact-vs-tree mismatch). It explicitly does **not** re-run suites or re-review; the real review is
③, whose verdict close-out reads in Step 4. **Verdict: keep it — it's cheap and load-bearing. Rename
the heading** so it stops reading as a review (see F11).

## Healthy — verified, no action

- `commands/` vs `workflows/` mirrors are **byte-identical** for the whole sudo set (sync manifest works).
- `rules/INDEX.md` covers all 19 rules; the floor/protocol/on-demand tiering is coherent; no dead rules.
- The gates **layer rather than repeat**: pre-dev plan audit ≠ post-dev adversarial review ≠ clean-code
  floor ≠ e2e gate. Only one true overlap found (F5).
- Close-out's scoped reads (grep the story id, never the 27k-token sprint file) and "don't re-run
  suites after autopilot" are already token-optimized.
- The no-punt close-out contract, fail-open verdict read, and worktree landing sequence are consistent
  across `git-policy`, `worktree-per-story`, and the close-out body.

## Findings

### P0 — broken now

**F1 · `/sudo-update-sprint-memory` is over the Antigravity 12k workflow limit.**
`sudo-update-sprint-memory.md` = **12,420 chars** (limit 12,000; ② was deliberately held at 11,988).
The AG mirror is at risk of truncation/rejection. Fix: trim ≥450 chars — compress Step 7's bash
comments and Step 4's parentheticals; fold the F11 rename into the same pass.

### P1 — contradictions that will bite an agent

**F2 · Constitution bans `continue` as authorization; ②'s gate is literally triggered by `continue`.**
`constitution.md` hard stop: *"Never treat 'ok', 'perfect', 'continue', or 'ready-for-dev' as
authorization."* ② Step 2: *"`continue` always means: run the remainder without further stops"* —
i.e. it authorizes implement. A literal-minded agent must refuse; a loose one proceeds. Fix: one
carve-out clause in the constitution — a gate word **defined by an invoked sudo command's own body**
(②'s `continue`, close-out's invocation-as-sign-off) IS explicit approval; the ban targets ad-hoc
chat words only.

**F3 · `000-PLAN-FIRST-GATE` still mandates `task.md` — retired by `artifacts-always-first`.**
000's "After Approval" step 1 says *"Create task.md artifact"* and its exception paragraph names
`task.md`; `artifacts-always-first` explicitly bans a hand-maintained `task.md` (TodoWrite +
walkthrough sections). Two Always-On rules disagree, and the `_bmad/custom/` guard tomls inject 000
into every dev run — so autopilot devs can re-mint the retired file. Fix: update 000's two mentions;
slim its duplicated "Sequence" to a pointer at `artifacts-always-first` (kill the drift surface, keep
the kill-chain).

**F4 · Boot's guardrail numbering (G2/G3/G5/G6/G8) is defined nowhere.**
`sudo-boot-sprint-memory` Step 3 recites G-numbers whose home no longer exists; the only other
G-numbering in the ruleset (`worktree-per-story` G1–G4) means **different things** — a numbering
collision. G6 "Firestore singleton" is also project bleed in a shared command (constitution already
generalizes it). Fix: drop the G-numbers, state the five checks plainly and generically.

### P2 — efficiency (cut repetition, keep the bar)

**F5 · ③ hunts AI drift twice on the same diff.**
Step 1 (`bmad-code-review`: Blind Hunter + drift/bloat hunt) and Step 3.5 (`clean-code-audit`
judgment pass §B: the same §2 drift bans) both read the same hunks for the same patterns, in the same
command run. Fix: when invoked as Step 3.5, `clean-code-audit` runs the **machine floor + comment
contract only** and imports Step 1's drift findings into its table; the full two-half pass stays for
standalone runs. Zero coverage loss, one full diff re-read saved per story.

**F6 · ③ re-audits the CI pipeline every story.**
Step 3.1 guard (a) (open the workflow YAML, verify the real entrypoint) and Step 3.4's soft-step scan
(`continue-on-error`, `|| true`, `.skip`) run per story though the pipeline rarely changes. Fix:
change-triggered — run them only when the story's diff touches `.github/workflows/**` or test
configs, else reuse the last audit (record `ci_audited_sha` in `sudo-tests.yaml`). The
`tests-must-gate-for-real` guarantee is preserved: re-audit fires exactly when the pipeline can have
drifted.

**F7 · `/sudo-quick-dev` Step 3 uses the wrong auditor.**
It runs `/sudo-self-audit` post-dev — a tool whose own text says it audits *plans, never a code
diff*. `clean-code-audit` (added after quick-dev was written) is the purpose-built post-dev check:
diff-scoped machine floor + drift bans. Fix: swap Step 3 to `/clean-code-audit` plus a one-line
AC-trace check. Better fit **and** fewer tokens (no Phase 0–4 plan walk against already-built code).

**F8 · ③ runs both stacks' full suites regardless of what the diff touched.** *(Judgment call —
recommend, Daniel decides.)* Recommendation: full suite of the **touched** stack always; the other
stack only when shared contract surfaces changed (API/SSE schemas, shared types) — PR CI and
`/sudo-e2e` still cover both stacks before anything ships. Tradeoff: saves the biggest per-story cost
block, at the price of catching a cross-stack break at PR-CI time instead of review time.

### P3 — doc accuracy + small tidies

**F9 · Quick-ref names the wrong kickoff command.** `sudo_workflows_testing.md` (map, §3 table, §4
step 1, §7 row) says `/bmad-create-epics-and-stories`; the real command is **`/sudo-create-epic-sprint`**,
which wraps it and adds the sprint board + the P0–P3 risk-scoring hard stop + the 2-checkpoint FLOW
CONTRACT from the 2026-07-19 retro. As written, the doc routes you around your own retro fix.

**F10 · Quick-ref ③ order is wrong.** §3/§4 say review → clean-code (3.5) → suites; the command runs
suites (Step 3) **before** clean-code (Step 3.5). Align the doc — or, nicer, renumber ③'s steps
1–6 honestly while trimming.

**F11 · Rename close-out Step 2's heading** to e.g. *"Verify the claimed work exists on disk
(grep-check — NOT a code review)"*. Kills the exact confusion that triggered this audit; fold into
the F1 trim pass.

**F12 · Two homes for review output, undocumented split.** Constitution says code review output →
`code-review.md` in the session folder; ③ Step 4 writes the verdict to
`_bmad-output/implementation-artifacts/sudo-code-review-<story>.md`. Both are correct (human-readable
detail vs machine-read gate verdict) but no rule says so — one clarifying clause in the constitution
prevents a future agent "fixing" one to match the other.

## Suggested order of fixes

1. F1 + F11 together (one edit pass on close-out; must land before AG next syncs).
2. F2, F3, F4 (rule-file edits — small, high blast-radius; remember `living-template-sync` → mirror
   into Fresh, then `/sync-agents`).
3. F9 + F10 (quick-ref edits — 10 minutes).
4. F5, F6, F7 (command-body efficiency edits; F6 adds one key to `sudo-tests.yaml`).
5. F8 — decide, then edit ③ (or explicitly note "both stacks always" as a deliberate cost).

After the batch: run `/update-maps-indexes` for the mechanical reference sweep, and `/sync-agents`
to propagate.
