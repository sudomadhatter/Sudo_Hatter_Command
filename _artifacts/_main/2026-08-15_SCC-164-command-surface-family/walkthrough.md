# SCC-164 — Command-surface correctness family: walkthrough

**Lane:** `chore/SCC-164-command-surface-family` · worktree `.claude/worktrees/SCC-164-command-surface-family` ·
cut from `origin/main` @ `a0aceaf` · LANE: LOCAL (this repo has no deployable surface) ·
manifest [task.yaml](task.yaml) declares thirteen riders · plan [implementation_plan.md](implementation_plan.md).

**review-runtime: fan-out** — probed at Step 0, before any code (lane rule 3, Part I's law on day one).
The independent PRE-WORK self-audit ran as a clean-context subagent and returned in ~14 min; a second
re-audit turn resumed the same agent with its context intact. Subagent spawn is LIVE in this session, so
the review's blind lenses fan out and a dead lens is a finding, not a `recovered-inline`.

**Plan approval:** operator, 2026-08-15, verbatim — *"perfect. approved"* — following the plan's rev 2
(§ STOP named the two calls it covers knowingly: B3 scoped per-file, and the live acceptance scoped to
SCC-163). The arming ruling was closed separately, quoted in § ARMING.

## Task Checklist

- [x] **Step 0–1.5 · plan, audit, approval** — plan rev 1 written on the lane; independent
      `/smh-self-audit` (PRE-WORK, FULL) returned **NO-GO** with 25 findings; all 25 adopted into the
      plan text as rev 2 (`7ac8f35`); re-audit of the touched phases returned **GO** with 6 further
      findings (F26–F31), all baked in. Operator approval received.
  - Finding that fought back hardest: **F4** — E3 as first written ("PASS/CONCERNS + a `dead` lens is a
    contradiction") would have made the engine's own designed end state unclosable. `step-01-review.md:398`
    raises the floor to CONCERNS when a lens stays dead after the inline retry — that IS the escape hatch
    § ARMING promises, and blocking it would have left `--no-verify` or a forged roster as the only ways
    out. Corrected to: PASS + dead blocks; CONCERNS + dead passes.
- [ ] **Part 1 · SCC-170** — the consolidation rule becomes law, riders default, partial landing
- [ ] **Part 2 · J / SCC-178** — gate_receipt stops counting its own output as dirt
- [ ] **Part 3 · K / SCC-179** — mutation sweep gets a mechanical restore check
- [ ] **Part 4 · A / SCC-165** — a bare `main` is a stale ref (20 operands)
- [ ] **Part 5 · B / SCC-166** — cicd-code-review gains its twin's two steps, ADAPTED
- [ ] **Part 6 · H / SCC-176** — the plan-time port checklist
- [ ] **Part 7 · F / SCC-174** — jira_feed check stops blessing a forked Dev Record ⛔ CUT LINE
- [ ] **Part 8 · C / SCC-171** — the token path as git gives it
- [ ] **Part 9 · G / SCC-175 + Part 12 · L / SCC-180** — no post-merge write to main; the `--hard` remedy
- [ ] **Part 10 · D / SCC-172** — three fail-opens in the main-write gate
- [ ] **Part 11 · E / SCC-173 + I / SCC-177** — the blind review recorded, enforced, sequenced

## Evidence

_Each acceptance item → the assertion that proves it, RED output then GREEN output. Filled in per part._

## Your Actions

_Filled in at the end of the lane._
