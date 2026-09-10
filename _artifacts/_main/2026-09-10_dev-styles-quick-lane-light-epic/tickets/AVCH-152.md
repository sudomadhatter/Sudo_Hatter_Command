Why: The epic ruleset (22247932) requires all four PR Quality Gate checks on every `epic/**` push, so a light epic today would still pay Playwright on every frontend landing, and a direct push would be refused outright. The server must read the same token the doors read (`-light-epic-`, from `epic/<KEY>-light-epic-<N>-<slug>`). And the skeleton every new project is cloned from (`sudomadhatter/sudo-project-skeleton`) still ships the pre-AVCH-149 `pr-check.yml` with no classifier, so a new project would start with neither the per-stack routing nor the light toggle. Lands last, after SCC-441's rules and doors.

## Plan
- [ ] `pr-check.yml`: the two E2E jobs add `!contains(github.event.pull_request.base.ref, '-light-epic-')` to their `if:`, fail-toward-running preserved; the classifier and the two unit jobs untouched
- [ ] Ruleset split, each GitHub write stopping for the operator first: `epic/**` minus the light pattern keeps four required checks; a new ruleset on `refs/heads/epic/*-light-epic-*` requires `Backend (Python)` and `Frontend (Node.js)` only; both carry a `pull_request` rule, strict, zero bypass actors
- [ ] `test_story_24_12_gate_recovery.py` pins the `if:`; a ruleset-shape test reads both rulesets through `gh api` and pins the required contexts and the patterns
- [ ] AviationChat `.agents/INDEX.md` and the TEA testing guide §6.0 mode table updated in the same commit; one worked light-epic example
- [ ] Skeleton (`Projects/sudo-project-skeleton`, committed under the SCC-441 key that repo accepts): `pr-check.yml` with the classifier and the light `if:`, `.github/scripts/classify_changes.py`, the ruleset recipe as a checked-in script the new-project door runs, an `AGENTS.md` GATES row naming both toggles, so every future project clones both on day one

## Done
(filled at close-out)

## Files
- Parent plan: `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/implementation_plan.md` (lobby)
- https://github.com/sudomadhatter/Sudo_Hatter_Command/blob/main/_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/implementation_plan.md
- https://github.com/sudomadhatter/AGY_AVIATIONCHAT/blob/main/.github/workflows/pr-check.yml
